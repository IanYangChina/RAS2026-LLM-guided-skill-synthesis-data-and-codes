## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3571 | 0.68 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0108 | 0.00 | ✅ accepted |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0107 | 0.00 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0828 | 0.00 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.357) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.3
- id: push_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_behind
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
    - 0.02
    - 0.0
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
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
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
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
  - guards:
    - id=check_approach, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=ensure_contact, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.01
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

- **Composite score**: 0.357
- **task_score** (E): 0.682
- **fitness_score**: 0.606  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 0.33 | 1.00 | 0.0743 |
| contact_peg | 0.33 | 1.00 | 0.0211 |
| push_channel | 0.00 | 1.00 | 0.1059 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 0.33 / step_budget | (0.495, 0.142, 0.105)→(0.501, 0.121, 0.035) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.667 | 1.116 | 58.576 |
| contact_peg | contact | 0.33 / step_budget | (0.501, 0.121, 0.035)→(0.497, 0.101, 0.031) | (0.502, 0.091, 0.036)→(0.500, 0.072, 0.035) | 0.171→0.152 | 1.00 / 2.333 | 5.085 | 4.069 |
| push_channel | push | 0.00 / guard_failure | (0.497, 0.101, 0.031)→(0.495, -0.005, 0.030) | (0.500, 0.072, 0.035)→(0.504, -0.031, 0.036) | 0.152→0.058 | 1.00 / 3.000 | 2099.490 | 45.393 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.964
- alignment_error: None
- force_efficiency: 0.051
- terminal_score: 0.921
- phase_score: 0.698
- phase_breakdown.pre_push_score: 0.877
- phase_breakdown.push_goal_score: 0.621

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.818
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.458
- **K-run variance**: 0.1424
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84932,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.04274,"approach_behind.lateral_offset_x":0.00296,"contact_peg.contact_force_threshold":12.43912,"contact_peg.contact_speed":0.00985,"push_channel.push_speed":0.03531,"retract.retract_speed":0.07202},"optimized_scores":{"best_composite_score":0.76052,"best_fitness_score":0.78719,"best_task_score":0.92121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":63.0,"contact_point_centroid":[0.4975,-0.10132,0.03359],"force_p95":38.64072,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.47246,"mean_force":25.04597,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50225,-0.05556,0.03099]},{"body_a":"attachment","body_b":"peg","contact_count":688.0,"contact_point_centroid":[0.49797,-0.01008,0.02888],"force_p95":24.24941,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.00169,"mean_force":2.98028,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49901,0.0018,0.02857]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1537.0,"contact_point_centroid":[0.50285,0.0662,0.00939],"force_p95":0.6436,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.98188,"mean_force":0.74088,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5004,0.14254,0.16311]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.5041,0.08138,0.04426],"force_p95":14.52789,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.6996,"mean_force":5.11325,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50562,0.09322,0.0441]},{"body_a":"peg","body_b":"channel_base_body","contact_count":667.0,"contact_point_centroid":[0.49593,-0.02856,0.00992],"force_p95":2.04334,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.58176,"mean_force":1.07895,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49877,0.00729,0.02842]},{"body_a":"peg","body_b":"channel_base_body","contact_count":630.0,"contact_point_centroid":[0.49266,0.04368,0.00967],"force_p95":1.15141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.43073,"mean_force":0.68719,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50038,0.07869,0.03014]},{"body_a":"attachment","body_b":"peg","contact_count":423.0,"contact_point_centroid":[0.49783,0.06693,0.03044],"force_p95":0.84758,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.73085,"mean_force":0.43822,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50033,0.07864,0.03009]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":101.0,"contact_point_centroid":[0.47491,0.03198,0.03667],"force_p95":1.73914,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.37474,"mean_force":0.51232,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49693,0.06169,0.0274]}],"total_contact_groups":8},"final_pose_error":0.04928,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49715,-0.08676,0.03526],"final_tcp_position":[0.50263,-0.05803,0.03118],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":47.47246,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1561.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.72211,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1597.0,"raw_peak_contact_force":15.98188,"subtask_id":"pre_push","tcp_end":[0.50649,0.08925,0.0347],"tcp_start":[0.50058,0.12666,0.12787],"tcp_to_object_dist_end":0.02211,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.49301,0.04365,0.03431],"object_pos_start":[0.49943,0.06023,0.03424],"object_to_goal_dist_end":0.12398,"object_to_goal_dist_start":0.14035,"object_z_max":0.035,"peak_contact_force":13.07999,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1053.0,"raw_peak_contact_force":3.43073,"tcp_end":[0.49872,0.07308,0.02974],"tcp_start":[0.50649,0.08925,0.0347],"tcp_to_object_dist_end":0.03033,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.49715,-0.08676,0.03526],"object_pos_start":[0.49301,0.04365,0.03431],"object_to_goal_dist_end":0.00873,"object_to_goal_dist_start":0.12398,"object_z_max":0.03536,"peak_contact_force":47.47246,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1519.0,"raw_peak_contact_force":47.47246,"subtask_id":"push_goal","tcp_end":[0.50263,-0.05803,0.03118],"tcp_start":[0.49872,0.07308,0.02974],"tcp_to_object_dist_end":0.02953,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99048,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.0634,"approach_behind.lateral_offset_x":0.00164,"contact_peg.contact_force_threshold":11.93351,"contact_peg.contact_speed":0.01404,"push_channel.push_speed":0.04354,"retract.retract_speed":0.06524},"optimized_scores":{"best_composite_score":0.45795,"best_fitness_score":0.81795,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1440.0,"contact_point_centroid":[0.50509,0.11183,0.0093],"force_p95":103.68293,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.66365,"mean_force":11.49912,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50317,0.1632,0.15678]},{"body_a":"attachment","body_b":"peg","contact_count":165.0,"contact_point_centroid":[0.51489,0.12868,0.05508],"force_p95":141.09412,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.31434,"mean_force":95.6492,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5093,0.13874,0.054]},{"body_a":"attachment","body_b":"peg","contact_count":832.0,"contact_point_centroid":[0.50194,0.00762,0.04173],"force_p95":10.14791,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.13214,"mean_force":3.86721,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49712,0.01912,0.03155]},{"body_a":"peg","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.50702,-0.10045,0.06007],"force_p95":37.96147,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.81631,"mean_force":29.01244,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49612,-0.05423,0.03357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.50539,-0.017,0.00994],"force_p95":7.74915,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.11159,"mean_force":4.06454,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49732,0.02703,0.03143]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":557.0,"contact_point_centroid":[0.52505,-0.0176,0.02451],"force_p95":3.25753,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.68345,"mean_force":1.10348,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49687,0.0102,0.03165]},{"body_a":"peg","body_b":"channel_base_body","contact_count":938.0,"contact_point_centroid":[0.5023,0.071,0.00996],"force_p95":1.62286,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.97103,"mean_force":1.24349,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5029,0.11713,0.0331]},{"body_a":"attachment","body_b":"peg","contact_count":937.0,"contact_point_centroid":[0.50321,0.10487,0.03716],"force_p95":1.30455,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.39561,"mean_force":0.93192,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50285,0.11686,0.03309]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":39.0,"contact_point_centroid":[0.52545,0.11124,0.04626],"force_p95":2.76643,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.77936,"mean_force":1.24337,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50713,0.16365,0.15203]}],"total_contact_groups":9},"final_pose_error":0.02002,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50719,-0.08239,0.03574],"final_tcp_position":[0.49599,-0.05533,0.03348],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":142.66365,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1462.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11176,0.03379],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.43538,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":142.66365,"subtask_id":"pre_push","tcp_end":[0.50825,0.13388,0.03763],"tcp_start":[0.50506,0.14942,0.10626],"tcp_to_object_dist_end":0.02291,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50151,0.07573,0.03499],"object_pos_start":[0.50511,0.10155,0.03803],"object_to_goal_dist_end":0.15582,"object_to_goal_dist_start":0.18163,"object_z_max":0.03803,"peak_contact_force":1.47092,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1875.0,"raw_peak_contact_force":3.97103,"tcp_end":[0.50164,0.1057,0.03313],"tcp_start":[0.50825,0.13388,0.03763],"tcp_to_object_dist_end":0.03003,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.50719,-0.08239,0.03574],"object_pos_start":[0.50151,0.07573,0.03499],"object_to_goal_dist_end":0.00869,"object_to_goal_dist_start":0.15582,"object_z_max":0.03625,"peak_contact_force":45.13214,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1944.0,"raw_peak_contact_force":45.13214,"subtask_id":"push_goal","tcp_end":[0.49599,-0.05533,0.03348],"tcp_start":[0.50164,0.1057,0.03313],"tcp_to_object_dist_end":0.02937,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8156,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.09456,"approach_behind.lateral_offset_x":-0.00781,"contact_peg.contact_force_threshold":9.08995,"contact_peg.contact_speed":0.00724,"push_channel.push_speed":0.02825,"retract.retract_speed":0.08906},"optimized_scores":{"best_composite_score":-0.14729,"best_fitness_score":0.21271,"best_task_score":0.12557},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.09928,0.02823],"force_p95":43.04302,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.57405,"mean_force":35.96236,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48683,0.09928,0.02627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":138.0,"contact_point_centroid":[0.50885,0.07105,0.00984],"force_p95":21.50635,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.93844,"mean_force":16.85531,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4878,0.11046,0.02662]},{"body_a":"peg","body_b":"link7","contact_count":118.0,"contact_point_centroid":[0.52006,0.09427,0.06203],"force_p95":16.40771,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.73665,"mean_force":13.56142,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48748,0.10842,0.02637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1455.0,"contact_point_centroid":[0.49817,0.11479,0.00955],"force_p95":3.8309,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.08156,"mean_force":0.92455,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48656,0.16324,0.14192]},{"body_a":"attachment","body_b":"peg","contact_count":175.0,"contact_point_centroid":[0.49227,0.12976,0.05414],"force_p95":6.30173,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.6485,"mean_force":3.41188,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48577,0.1408,0.04169]},{"body_a":"attachment","body_b":"peg","contact_count":138.0,"contact_point_centroid":[0.49723,0.10046,0.04508],"force_p95":14.21027,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.83973,"mean_force":11.04273,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48778,0.11035,0.0266]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":46.0,"contact_point_centroid":[0.52504,0.08304,0.05475],"force_p95":8.55019,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.09317,"mean_force":6.40479,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48762,0.10892,0.02653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":976.0,"contact_point_centroid":[0.50693,0.08703,0.00998],"force_p95":2.67465,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.8056,"mean_force":1.09969,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48842,0.12956,0.02836]},{"body_a":"attachment","body_b":"peg","contact_count":976.0,"contact_point_centroid":[0.49536,0.11862,0.03926],"force_p95":2.31281,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.47915,"mean_force":0.78053,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48842,0.12945,0.02833]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49948,0.19925,0.2982]}],"total_contact_groups":10},"final_pose_error":0.15514,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50654,0.07562,0.03639],"final_tcp_position":[0.48685,0.09901,0.02629],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":6205.86669,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1490.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11919,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19932,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":2.19104,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1654.0,"raw_peak_contact_force":17.08156,"subtask_id":"pre_push","tcp_end":[0.48867,0.13881,0.03159],"tcp_start":[0.47882,0.14877,0.08166],"tcp_to_object_dist_end":0.02109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50564,0.09727,0.03623],"object_pos_start":[0.50023,0.11074,0.03575],"object_to_goal_dist_end":0.1774,"object_to_goal_dist_start":0.19078,"object_z_max":0.03624,"peak_contact_force":0.70423,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1952.0,"raw_peak_contact_force":4.8056,"tcp_end":[0.49053,0.12389,0.02893],"tcp_start":[0.48867,0.13881,0.03159],"tcp_to_object_dist_end":0.03146,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.50654,0.07562,0.03639],"object_pos_start":[0.50564,0.09727,0.03623],"object_to_goal_dist_end":0.1558,"object_to_goal_dist_start":0.1774,"object_z_max":0.03657,"peak_contact_force":6205.86669,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":443.0,"raw_peak_contact_force":43.57405,"subtask_id":"push_goal","tcp_end":[0.48685,0.09901,0.02629],"tcp_start":[0.49053,0.12389,0.02893],"tcp_to_object_dist_end":0.0322,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```