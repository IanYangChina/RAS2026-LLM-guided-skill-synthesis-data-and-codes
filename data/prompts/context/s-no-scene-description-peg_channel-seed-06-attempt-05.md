## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3662 | 0.39 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3571 | 0.68 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0108 | 0.00 | ✅ accepted |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0107 | 0.00 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0828 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.366) — your mutation base

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

- **Composite score**: 0.366
- **task_score** (E): 0.390
- **fitness_score**: 0.526  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 0.67 | 1.00 | 0.1012 |
| contact_peg | 1.00 | 1.00 | 0.0297 |
| push_channel | 1.00 | 1.00 | 0.1691 |
| retract | 1.00 | 1.00 | 0.0906 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 0.67 / step_budget | (0.503, 0.152, 0.184)→(0.499, 0.121, 0.088) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.518 | 2.127 |
| contact_peg | contact | 1.00 / force_exceeded | (0.499, 0.121, 0.088)→(0.497, 0.111, 0.060) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 23.304 | 23.304 |
| push_channel | push | 1.00 / step_budget | (0.497, 0.111, 0.060)→(0.492, -0.058, 0.062) | (0.501, 0.099, 0.034)→(0.499, 0.033, 0.024) | 0.180→0.115 | 1.00 / 1.000 | 0.576 | 44.709 |
| retract | retract | 1.00 / step_budget | (0.492, -0.058, 0.062)→(0.489, -0.058, 0.152) | (0.499, 0.033, 0.024)→(0.501, 0.034, 0.024) | 0.115→0.115 | 1.00 / 1.000 | 0.630 | 5.985 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.427
- alignment_error: None
- force_efficiency: 0.149
- terminal_score: 0.427
- phase_score: 0.696
- phase_breakdown.pre_push_score: 0.886
- phase_breakdown.push_goal_score: 0.615

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.589
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.427
- **Median Q (composite search score)**: 0.362
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86691,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.0577,"approach_above.lateral_offset_x":-0.00017,"contact_peg.contact_force_threshold":9.09094,"contact_peg.contact_speed":0.01732,"push_channel.force_limit_threshold":59.07796,"push_channel.push_speed":0.02526,"retract.retract_speed":0.05209},"optimized_scores":{"best_composite_score":0.42858,"best_fitness_score":0.58858,"best_task_score":0.42712},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50068,0.0208,0.00906],"force_p95":40.95779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.5722,"mean_force":16.78423,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49559,-0.00235,0.06092]},{"body_a":"attachment","body_b":"peg","contact_count":513.0,"contact_point_centroid":[0.50601,0.04402,0.05977],"force_p95":40.70539,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.15861,"mean_force":31.37314,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49758,0.03831,0.06053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":158.0,"contact_point_centroid":[0.50273,0.06739,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.12205,"mean_force":0.64522,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50082,0.08521,0.07215]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51153,0.08011,0.05878],"force_p95":15.60585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.60585,"mean_force":15.60585,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49969,0.08059,0.06066]},{"body_a":"peg","body_b":"channel_base_body","contact_count":881.0,"contact_point_centroid":[0.50146,-0.00145,0.00807],"force_p95":0.68343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.26237,"mean_force":0.63757,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48941,-0.08359,0.10795]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52501,0.02188,0.02434],"force_p95":7.90372,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.92409,"mean_force":3.60627,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48932,-0.08354,0.12314]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.475,-0.02343,0.02438],"force_p95":7.76298,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.85147,"mean_force":3.72294,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49312,-0.05806,0.06177]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1363.0,"contact_point_centroid":[0.50307,0.06746,0.00937],"force_p95":0.55118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55296,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49895,0.14104,0.18571]}],"total_contact_groups":8},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50273,-0.00088,0.02417],"final_tcp_position":[0.48955,-0.08358,0.15335],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":42.5722,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1379.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54774,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1363.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push","tcp_end":[0.50342,0.08952,0.08434],"tcp_start":[0.49896,0.11482,0.13776],"tcp_to_object_dist_end":0.05516,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06751,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14767,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":16.12205,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":159.0,"raw_peak_contact_force":16.12205,"tcp_end":[0.49969,0.08053,0.06053],"tcp_start":[0.50342,0.08952,0.08434],"tcp_to_object_dist_end":0.02993,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4958,-0.00117,0.02443],"object_pos_start":[0.50307,0.06751,0.0338],"object_to_goal_dist_end":0.08046,"object_to_goal_dist_start":0.14767,"object_z_max":0.04072,"peak_contact_force":0.56299,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1530.0,"raw_peak_contact_force":42.5722,"subtask_id":"push_goal","tcp_end":[0.49259,-0.08404,0.06282],"tcp_start":[0.49969,0.08053,0.06053],"tcp_to_object_dist_end":0.09138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.50273,-0.00088,0.02417],"object_pos_start":[0.4958,-0.00117,0.02443],"object_to_goal_dist_end":0.08074,"object_to_goal_dist_start":0.08046,"object_z_max":0.02462,"peak_contact_force":0.60596,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":890.0,"raw_peak_contact_force":8.26237,"tcp_end":[0.48955,-0.08358,0.15335],"tcp_start":[0.49259,-0.08404,0.06282],"tcp_to_object_dist_end":0.15395,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77863,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.06468,"approach_above.lateral_offset_x":0.00574,"contact_peg.contact_force_threshold":19.7166,"contact_peg.contact_speed":0.01591,"push_channel.force_limit_threshold":49.79734,"push_channel.push_speed":0.0595,"retract.retract_speed":0.02708},"optimized_scores":{"best_composite_score":0.36179,"best_fitness_score":0.52179,"best_task_score":0.40101},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.50189,0.06609,0.00897],"force_p95":44.77482,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.96604,"mean_force":17.54137,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49996,0.03727,0.05994]},{"body_a":"attachment","body_b":"peg","contact_count":487.0,"contact_point_centroid":[0.50986,0.08861,0.05947],"force_p95":44.79259,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.53992,"mean_force":34.56514,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50216,0.0821,0.06005]},{"body_a":"peg","body_b":"channel_base_body","contact_count":152.0,"contact_point_centroid":[0.50359,0.11168,0.00941],"force_p95":0.60598,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.63371,"mean_force":0.88072,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50636,0.1284,0.07296]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51581,0.12337,0.05869],"force_p95":22.48654,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.17032,"mean_force":17.18566,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50396,0.12361,0.06047]},{"body_a":"peg","body_b":"channel_base_body","contact_count":976.0,"contact_point_centroid":[0.5033,0.04738,0.00806],"force_p95":0.69709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.95989,"mean_force":0.62258,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49368,-0.04829,0.10605]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52501,0.07165,0.02423],"force_p95":8.53871,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.55696,"mean_force":3.10038,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49362,-0.04825,0.12216]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1145.0,"contact_point_centroid":[0.50362,0.11165,0.00939],"force_p95":0.59907,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5509,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50501,0.16415,0.18739]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49972,0.19943,0.29931]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.0234,0.02427],"force_p95":0.40038,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40478,"mean_force":0.36189,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4979,0.00206,0.05949]}],"total_contact_groups":9},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50505,0.04761,0.02414],"final_tcp_position":[0.49382,-0.04827,0.15168],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":45.96604,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1167.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11176,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.49524,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1161.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push","tcp_end":[0.51,0.13283,0.08579],"tcp_start":[0.51019,0.14022,0.11383],"tcp_to_object_dist_end":0.05642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.1117,0.03378],"object_pos_start":[0.50373,0.11171,0.03389],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19184,"object_z_max":0.03396,"peak_contact_force":23.63371,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":155.0,"raw_peak_contact_force":23.63371,"tcp_end":[0.50395,0.1235,0.06018],"tcp_start":[0.51,0.13283,0.08579],"tcp_to_object_dist_end":0.02892,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.49831,0.04757,0.02414],"object_pos_start":[0.5037,0.1117,0.03378],"object_to_goal_dist_end":0.12856,"object_to_goal_dist_start":0.19184,"object_z_max":0.04067,"peak_contact_force":0.66719,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1479.0,"raw_peak_contact_force":45.96604,"subtask_id":"push_goal","tcp_end":[0.49692,-0.04854,0.06112],"tcp_start":[0.50395,0.1235,0.06018],"tcp_to_object_dist_end":0.10299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.50505,0.04761,0.02414],"object_pos_start":[0.49831,0.04757,0.02414],"object_to_goal_dist_end":0.1287,"object_to_goal_dist_start":0.12856,"object_z_max":0.02434,"peak_contact_force":0.66721,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":982.0,"raw_peak_contact_force":8.95989,"tcp_end":[0.49382,-0.04827,0.15168],"tcp_start":[0.49692,-0.04854,0.06112],"tcp_to_object_dist_end":0.15996,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1453,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.07359,"approach_above.lateral_offset_x":0.00159,"contact_peg.contact_force_threshold":13.20632,"contact_peg.contact_speed":0.02503,"push_channel.force_limit_threshold":62.11575,"push_channel.push_speed":0.03681,"retract.retract_speed":0.04901},"optimized_scores":{"best_composite_score":0.30824,"best_fitness_score":0.46824,"best_task_score":0.34078},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.49889,0.07228,0.00894],"force_p95":44.83541,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.58778,"mean_force":16.76285,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48596,0.04386,0.05993]},{"body_a":"attachment","body_b":"peg","contact_count":472.0,"contact_point_centroid":[0.49498,0.09536,0.05937],"force_p95":44.68652,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.10765,"mean_force":34.19659,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48634,0.08971,0.06]},{"body_a":"peg","body_b":"channel_base_body","contact_count":246.0,"contact_point_centroid":[0.49591,0.11931,0.00947],"force_p95":0.5972,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.15575,"mean_force":0.7077,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48466,0.13467,0.07588]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49845,0.12854,0.05878],"force_p95":28.70315,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.58738,"mean_force":20.74507,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4866,0.12929,0.06045]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.49614,0.11911,0.00944],"force_p95":0.61754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54732,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49137,0.16906,0.19235]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49953,0.19925,0.29842]},{"body_a":"peg","body_b":"channel_base_body","contact_count":842.0,"contact_point_centroid":[0.49916,0.05426,0.00802],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73332,"mean_force":0.60581,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48327,-0.04095,0.10614]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.07832,0.02416],"force_p95":0.42259,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42757,"mean_force":0.37931,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.486,-0.02079,0.06048]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,0.03029,0.0242],"force_p95":0.40558,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40818,"mean_force":0.3822,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48335,-0.04092,0.14868]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.05985,0.05769],"force_p95":0.27272,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27556,"mean_force":0.24714,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48521,0.04569,0.05899]}],"total_contact_groups":10},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49449,0.05457,0.02424],"final_tcp_position":[0.48338,-0.04092,0.15158],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":45.58778,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.1191,0.03401],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50975,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_push","tcp_end":[0.48484,0.14048,0.09375],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":246.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11911,0.03392],"object_pos_start":[0.49603,0.1191,0.03401],"object_to_goal_dist_end":0.19924,"object_to_goal_dist_start":0.19923,"object_z_max":0.03416,"peak_contact_force":30.15575,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":248.0,"raw_peak_contact_force":30.15575,"tcp_end":[0.48664,0.12925,0.06031],"tcp_start":[0.48484,0.14048,0.09375],"tcp_to_object_dist_end":0.02979,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50437,0.05407,0.02409],"object_pos_start":[0.49606,0.11911,0.03392],"object_to_goal_dist_end":0.13508,"object_to_goal_dist_start":0.19924,"object_z_max":0.04071,"peak_contact_force":0.49884,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1471.0,"raw_peak_contact_force":45.58778,"subtask_id":"push_goal","tcp_end":[0.4864,-0.04116,0.06108],"tcp_start":[0.48664,0.12925,0.06031],"tcp_to_object_dist_end":0.10373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":842.0,"n_steps_budget":1000.0,"object_pos_end":[0.49449,0.05457,0.02424],"object_pos_start":[0.50437,0.05407,0.02409],"object_to_goal_dist_end":0.1356,"object_to_goal_dist_start":0.13508,"object_z_max":0.02426,"peak_contact_force":0.61809,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":844.0,"raw_peak_contact_force":0.73332,"tcp_end":[0.48338,-0.04092,0.15158],"tcp_start":[0.4864,-0.04116,0.06108],"tcp_to_object_dist_end":0.15955,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```