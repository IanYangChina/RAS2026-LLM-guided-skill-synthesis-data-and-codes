## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3307 | 0.46 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3411 | 0.65 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1002 | 0.12 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3662 | 0.39 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3571 | 0.68 | ✅ accepted |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.331) — your mutation base

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

- **Composite score**: 0.331
- **task_score** (E): 0.458
- **fitness_score**: 0.441  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1013 |
| contact_peg | 1.00 | 1.00 | 0.0278 |
| push_channel | 1.00 | 1.00 | 0.1685 |
| retract | 1.00 | 1.00 | 0.0906 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.502, 0.151, 0.184)→(0.497, 0.121, 0.088) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.550 | 2.127 |
| contact_peg | contact | 1.00 / force_exceeded | (0.497, 0.121, 0.088)→(0.495, 0.119, 0.060) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 18.491 | 18.491 |
| push_channel | push | 1.00 / step_budget | (0.495, 0.119, 0.060)→(0.491, -0.049, 0.062) | (0.501, 0.099, 0.034)→(0.498, 0.023, 0.024) | 0.180→0.104 | 1.00 / 1.000 | 0.610 | 43.808 |
| retract | retract | 1.00 / step_budget | (0.491, -0.049, 0.062)→(0.488, -0.049, 0.152) | (0.498, 0.023, 0.024)→(0.501, 0.021, 0.024) | 0.104→0.103 | 1.00 / 1.000 | 0.662 | 6.153 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.504
- alignment_error: None
- force_efficiency: 0.116
- terminal_score: 0.504
- phase_score: 0.558
- phase_breakdown.pre_push_score: 0.414
- phase_breakdown.push_goal_score: 0.620

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.537
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.504
- **Median Q (composite search score)**: 0.321
- **K-run variance**: 0.0056
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.185


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94361,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.0655,"approach_behind.lateral_offset_x":0.00048,"contact_peg.contact_force_threshold":14.41511,"contact_peg.contact_speed":0.01729,"push_channel.push_speed":0.02414,"retract.retract_speed":0.05885},"optimized_scores":{"best_composite_score":0.42662,"best_fitness_score":0.53662,"best_task_score":0.50389},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50204,0.01816,0.00918],"force_p95":40.02274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.19411,"mean_force":19.9395,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49624,0.00626,0.06085]},{"body_a":"attachment","body_b":"peg","contact_count":623.0,"contact_point_centroid":[0.50658,0.04207,0.05964],"force_p95":40.66683,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.77453,"mean_force":31.00609,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49773,0.03748,0.0605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":141.0,"contact_point_centroid":[0.50278,0.06728,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.76515,"mean_force":0.68295,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50143,0.08855,0.07218]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51114,0.08359,0.05871],"force_p95":19.21509,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.21509,"mean_force":19.21509,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50012,0.088,0.06042]},{"body_a":"peg","body_b":"channel_base_body","contact_count":869.0,"contact_point_centroid":[0.49637,-0.01112,0.00809],"force_p95":0.73078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.8629,"mean_force":0.7782,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48984,-0.07596,0.10763]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":43.0,"contact_point_centroid":[0.475,-0.03478,0.02448],"force_p95":7.98644,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.37457,"mean_force":3.91496,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48968,-0.07594,0.08914]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,-0.03263,0.02416],"force_p95":7.24557,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.00266,"mean_force":2.93813,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49306,-0.07438,0.06247]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1344.0,"contact_point_centroid":[0.50307,0.06747,0.00937],"force_p95":0.5512,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55305,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49929,0.1397,0.18325]}],"total_contact_groups":8},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50166,-0.01316,0.0241],"final_tcp_position":[0.48998,-0.07594,0.15307],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":44.19411,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54546,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1344.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push","tcp_end":[0.50398,0.08935,0.08402],"tcp_start":[0.49954,0.11122,0.13097],"tcp_to_object_dist_end":0.0548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06752,0.0338],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.14768,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":19.76515,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":142.0,"raw_peak_contact_force":19.76515,"tcp_end":[0.50013,0.08799,0.06027],"tcp_start":[0.50398,0.08935,0.08402],"tcp_to_object_dist_end":0.03359,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49454,-0.00893,0.02432],"object_pos_start":[0.50307,0.06752,0.0338],"object_to_goal_dist_end":0.07299,"object_to_goal_dist_start":0.14768,"object_z_max":0.04072,"peak_contact_force":0.54184,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1620.0,"raw_peak_contact_force":44.19411,"subtask_id":"push_goal","tcp_end":[0.49302,-0.07637,0.06255],"tcp_start":[0.50013,0.08799,0.06027],"tcp_to_object_dist_end":0.07754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":869.0,"n_steps_budget":1000.0,"object_pos_end":[0.50166,-0.01316,0.0241],"object_pos_start":[0.49454,-0.00893,0.02432],"object_to_goal_dist_end":0.06873,"object_to_goal_dist_start":0.07299,"object_z_max":0.02501,"peak_contact_force":0.63682,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":912.0,"raw_peak_contact_force":8.8629,"tcp_end":[0.48998,-0.07594,0.15307],"tcp_start":[0.49302,-0.07637,0.06255],"tcp_to_object_dist_end":0.14392,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84015,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.03556,"approach_behind.lateral_offset_x":0.00031,"contact_peg.contact_force_threshold":14.37609,"contact_peg.contact_speed":0.01916,"push_channel.push_speed":0.05027,"retract.retract_speed":0.05324},"optimized_scores":{"best_composite_score":0.32104,"best_fitness_score":0.43104,"best_task_score":0.48033},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50195,0.06148,0.00914],"force_p95":41.72478,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.41845,"mean_force":20.28145,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.497,0.04685,0.06039]},{"body_a":"attachment","body_b":"peg","contact_count":606.0,"contact_point_centroid":[0.5073,0.08583,0.05952],"force_p95":41.55854,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.00474,"mean_force":32.43325,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49856,0.081,0.06034]},{"body_a":"peg","body_b":"channel_base_body","contact_count":149.0,"contact_point_centroid":[0.50384,0.11159,0.00942],"force_p95":0.60422,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.80907,"mean_force":0.66544,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50214,0.13204,0.07319]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51205,0.12769,0.05886],"force_p95":18.32157,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.32157,"mean_force":18.32157,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50083,0.13154,0.06064]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,0.01206,0.0242],"force_p95":6.80656,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.93339,"mean_force":2.27988,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49439,-0.01012,0.06046]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1184.0,"contact_point_centroid":[0.50365,0.11165,0.0094],"force_p95":0.59987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55041,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50215,0.16448,0.18837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":864.0,"contact_point_centroid":[0.50098,0.03519,0.00804],"force_p95":0.6834,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6835,"mean_force":0.60589,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49062,-0.03967,0.10655]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49967,0.19945,0.29938]}],"total_contact_groups":8},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50525,0.03493,0.02413],"final_tcp_position":[0.49075,-0.03964,0.15196],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":44.41845,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1206.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11174,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55894,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1200.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push","tcp_end":[0.5048,0.13293,0.08605],"tcp_start":[0.50525,0.1425,0.12094],"tcp_to_object_dist_end":0.05639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11172,0.03386],"object_pos_start":[0.5037,0.11173,0.03383],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19186,"object_z_max":0.03391,"peak_contact_force":18.80907,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":150.0,"raw_peak_contact_force":18.80907,"tcp_end":[0.50083,0.13155,0.06049],"tcp_start":[0.5048,0.13293,0.08605],"tcp_to_object_dist_end":0.03332,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49642,0.03555,0.02413],"object_pos_start":[0.50373,0.11172,0.03386],"object_to_goal_dist_end":0.11669,"object_to_goal_dist_start":0.19185,"object_z_max":0.04069,"peak_contact_force":0.68338,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1604.0,"raw_peak_contact_force":44.41845,"subtask_id":"push_goal","tcp_end":[0.49381,-0.03986,0.0614],"tcp_start":[0.50083,0.13155,0.06049],"tcp_to_object_dist_end":0.08416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.50525,0.03493,0.02413],"object_pos_start":[0.49642,0.03555,0.02413],"object_to_goal_dist_end":0.11613,"object_to_goal_dist_start":0.11669,"object_z_max":0.02413,"peak_contact_force":0.6834,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":864.0,"raw_peak_contact_force":0.6835,"tcp_end":[0.49075,-0.03964,0.15196],"tcp_start":[0.49381,-0.03986,0.0614],"tcp_to_object_dist_end":0.14869,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05242,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07208,"approach_behind.lateral_offset_x":-0.00122,"contact_peg.contact_force_threshold":13.55398,"contact_peg.contact_speed":0.0194,"push_channel.push_speed":0.03352,"retract.retract_speed":0.05197},"optimized_scores":{"best_composite_score":0.24444,"best_fitness_score":0.35444,"best_task_score":0.3891},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.49693,0.06843,0.00915],"force_p95":41.67942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.80994,"mean_force":19.93332,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48469,0.05508,0.06025]},{"body_a":"attachment","body_b":"peg","contact_count":599.0,"contact_point_centroid":[0.49423,0.09379,0.05938],"force_p95":41.43516,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.38521,"mean_force":32.24246,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48487,0.08942,0.06019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.49602,0.11903,0.0094],"force_p95":0.60163,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.89901,"mean_force":0.60491,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48261,0.13929,0.07555]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49694,0.13701,0.05882],"force_p95":16.36808,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.36808,"mean_force":16.36808,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4852,0.13877,0.06052]},{"body_a":"peg","body_b":"channel_base_body","contact_count":831.0,"contact_point_centroid":[0.49923,0.04255,0.00804],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.91371,"mean_force":0.63383,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48185,-0.03049,0.10634]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.475,0.0187,0.02422],"force_p95":8.35149,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.48344,"mean_force":3.04898,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48179,-0.03045,0.13276]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52502,0.06622,0.02425],"force_p95":6.6575,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.20932,"mean_force":1.94225,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4824,-0.03066,0.06756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.49617,0.11923,0.00942],"force_p95":0.60198,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5492,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49,0.16908,0.19243]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49951,0.19925,0.29844]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.04981,0.0583],"force_p95":0.25494,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2573,"mean_force":0.23363,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48417,0.03598,0.05976]}],"total_contact_groups":10},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49528,0.04249,0.02414],"final_tcp_position":[0.48195,-0.03045,0.15173],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":42.80994,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.49611,0.11899,0.03389],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54513,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_push","tcp_end":[0.48215,0.14046,0.09374],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11903,0.03387],"object_pos_start":[0.49611,0.11899,0.03389],"object_to_goal_dist_end":0.19916,"object_to_goal_dist_start":0.19912,"object_z_max":0.03392,"peak_contact_force":16.89901,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":273.0,"raw_peak_contact_force":16.89901,"tcp_end":[0.48523,0.13877,0.06043],"tcp_start":[0.48215,0.14046,0.09374],"tcp_to_object_dist_end":0.03483,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5041,0.04228,0.02417],"object_pos_start":[0.49608,0.11903,0.03387],"object_to_goal_dist_end":0.12337,"object_to_goal_dist_start":0.19916,"object_z_max":0.04072,"peak_contact_force":0.60595,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1595.0,"raw_peak_contact_force":42.80994,"subtask_id":"push_goal","tcp_end":[0.48497,-0.03063,0.06126],"tcp_start":[0.48523,0.13877,0.06043],"tcp_to_object_dist_end":0.08402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.49528,0.04249,0.02414],"object_pos_start":[0.5041,0.04228,0.02417],"object_to_goal_dist_end":0.12361,"object_to_goal_dist_start":0.12337,"object_z_max":0.02452,"peak_contact_force":0.6672,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":842.0,"raw_peak_contact_force":8.91371,"tcp_end":[0.48195,-0.03045,0.15173],"tcp_start":[0.48497,-0.03063,0.06126],"tcp_to_object_dist_end":0.14757,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```