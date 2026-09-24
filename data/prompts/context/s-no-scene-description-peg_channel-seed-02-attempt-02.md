## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1931 | 0.13 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1968 | 0.13 | ✅ accepted |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.1029 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.193) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: push_channel
  weight: 0.8
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.2
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_force:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_confirm
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: approach_peg
- id: push_through_channel
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: push_channel
- id: retract_up
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
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.2
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_confirm, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_up** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.193
- **task_score** (E): 0.126
- **fitness_score**: 0.153  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1794 |
| descend_to_peg | 1.00 | 1.00 | 0.0839 |
| push_through_channel | 0.67 | 1.00 | 0.0937 |
| retract_up | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.076, 0.179) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.545 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.076, 0.179)→(0.492, 0.070, 0.096) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 41.824 | 41.824 |
| push_through_channel | push | 0.67 / step_budget | (0.492, 0.070, 0.096)→(0.498, -0.019, 0.095) | (0.498, 0.068, 0.034)→(0.501, 0.028, 0.027) | 0.148→0.110 | 1.00 / 2.333 | 2071.109 | 355.468 |
| retract_up | retract | 1.00 / step_budget | (0.498, -0.019, 0.095)→(0.496, -0.019, 0.184) | (0.501, 0.028, 0.027)→(0.499, 0.029, 0.028) | 0.110→0.110 | 1.00 / 1.000 | 0.585 | 103.325 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.401
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.265
- phase_score: 0.242
- phase_breakdown.approach_peg_score: 0.189
- phase_breakdown.push_channel_score: 0.255

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.251
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.265
- **Median Q (composite search score)**: 0.222
- **K-run variance**: 0.0088
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.347


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96296,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.10591,"descend_to_peg.descend_force":19.99697,"push_through_channel.push_distance":0.15603},"optimized_scores":{"best_composite_score":0.29113,"best_fitness_score":0.25113,"best_task_score":0.26514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":625.0,"contact_point_centroid":[0.47498,0.11253,0.05996],"force_p95":286.8201,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.00196,"mean_force":251.51156,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49165,0.05408,0.09989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":711.0,"contact_point_centroid":[0.49497,0.05719,0.00935],"force_p95":134.37278,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.39455,"mean_force":12.0698,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49256,0.04698,0.09909]},{"body_a":"peg","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.49254,0.04922,0.05924],"force_p95":186.01124,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.29324,"mean_force":109.94857,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49996,-0.00767,0.09232]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.0134,0.06],"force_p95":85.88353,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.21403,"mean_force":82.909,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49073,-0.05983,0.10458]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.11997,0.05998],"force_p95":50.02388,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.02388,"mean_force":50.02388,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48359,0.06738,0.10695]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47482,0.00111,0.05317],"force_p95":45.70961,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.79505,"mean_force":36.59369,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49585,-0.03056,0.09779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49994,6e-05,0.00809],"force_p95":0.70949,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.7264,"mean_force":0.68949,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48858,-0.06014,0.14879]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47499,-0.02395,0.0244],"force_p95":8.27162,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.32737,"mean_force":3.52415,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48862,-0.06,0.19016]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52506,0.0237,0.02458],"force_p95":8.03838,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.24201,"mean_force":1.90472,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48842,-0.06016,0.12363]},{"body_a":"peg","body_b":"channel_base_body","contact_count":664.0,"contact_point_centroid":[0.49542,0.06381,0.00937],"force_p95":0.56648,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55838,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48669,0.14337,0.22043]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50406,0.21534,0.293]},{"body_a":"peg","body_b":"channel_base_body","contact_count":232.0,"contact_point_centroid":[0.49521,0.0641,0.0094],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55213,"mean_force":0.54537,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48101,0.06923,0.12875]}],"total_contact_groups":12},"final_pose_error":0.01095,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49421,-0.0003,0.0248],"final_tcp_position":[0.48866,-0.05999,0.19382],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":334.00196,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":691.0,"n_steps_budget":1000.0,"object_pos_end":[0.49525,0.06405,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14425,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54338,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.47998,0.07182,0.15176],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":232.0,"n_steps_budget":630.0,"object_pos_end":[0.49504,0.06414,0.034],"object_pos_start":[0.49525,0.06405,0.03397],"object_to_goal_dist_end":0.14434,"object_to_goal_dist_start":0.14425,"object_z_max":0.034,"peak_contact_force":50.02388,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":233.0,"raw_peak_contact_force":50.02388,"subtask_id":"approach_peg","tcp_end":[0.48362,0.06737,0.1068],"tcp_start":[0.47998,0.07182,0.15176],"tcp_to_object_dist_end":0.07376,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":717.0,"n_steps_budget":990.0,"object_pos_end":[0.49684,-4e-05,0.02361],"object_pos_start":[0.49504,0.06414,0.034],"object_to_goal_dist_end":0.08169,"object_to_goal_dist_start":0.14434,"object_z_max":0.03891,"peak_contact_force":1.41258,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1422.0,"raw_peak_contact_force":334.00196,"subtask_id":"push_channel","tcp_end":[0.49076,-0.05965,0.10456],"tcp_start":[0.48362,0.06737,0.1068],"tcp_to_object_dist_end":0.10072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49421,-0.0003,0.0248],"object_pos_start":[0.49684,-4e-05,0.02361],"object_to_goal_dist_end":0.08134,"object_to_goal_dist_start":0.08169,"object_z_max":0.02487,"peak_contact_force":0.52216,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":565.0,"raw_peak_contact_force":86.21403,"tcp_end":[0.48866,-0.05999,0.19382],"tcp_start":[0.49076,-0.05965,0.10456],"tcp_to_object_dist_end":0.17933,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9661,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.19786,"descend_to_peg.descend_force":13.57353,"push_through_channel.push_distance":0.17309},"optimized_scores":{"best_composite_score":0.22153,"best_fitness_score":0.18153,"best_task_score":0.11213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":88.0,"contact_point_centroid":[0.47499,0.0639,0.05998],"force_p95":160.63434,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":202.23479,"mean_force":122.92746,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48419,-0.00065,0.11161]},{"body_a":"peg","body_b":"channel_base_body","contact_count":267.0,"contact_point_centroid":[0.49816,0.03695,0.00924],"force_p95":106.36588,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.44919,"mean_force":34.48793,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48439,-0.00611,0.11181]},{"body_a":"peg","body_b":"link7","contact_count":115.0,"contact_point_centroid":[0.48784,0.04317,0.0626],"force_p95":112.8956,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":118.10083,"mean_force":78.89031,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48454,-0.01371,0.11208]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,-0.01691,0.05999],"force_p95":70.27241,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.27241,"mean_force":70.27241,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.485,-0.08298,0.11111]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47497,0.11999,0.05996],"force_p95":55.03355,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.03355,"mean_force":55.03355,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48258,0.06117,0.1122]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49471,0.0007,0.00803],"force_p95":0.72801,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.76634,"mean_force":0.68206,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.483,-0.08272,0.15539]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.4749,0.02485,0.02445],"force_p95":8.95047,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.40247,"mean_force":2.94492,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48336,-0.08311,0.11906]},{"body_a":"peg","body_b":"channel_base_body","contact_count":593.0,"contact_point_centroid":[0.49442,0.05891,0.00936],"force_p95":0.56457,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57088,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48058,0.14241,0.25959]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50213,0.22043,0.28757]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52509,-0.00814,0.04776],"force_p95":1.18366,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2374,"mean_force":0.78446,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48448,-0.05399,0.11159]},{"body_a":"peg","body_b":"channel_base_body","contact_count":660.0,"contact_point_centroid":[0.49401,0.05893,0.00939],"force_p95":0.55018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54583,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47439,0.06457,0.17419]}],"total_contact_groups":11},"final_pose_error":0.01084,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49521,0.00125,0.0241],"final_tcp_position":[0.48309,-0.08257,0.20043],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":202.23479,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":622.0,"n_steps_budget":990.0,"object_pos_end":[0.4942,0.05907,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":628.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46782,0.06867,0.23829],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":660.0,"n_steps_budget":1000.0,"object_pos_end":[0.49433,0.05884,0.03397],"object_pos_start":[0.4942,0.05907,0.03388],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.13933,"object_z_max":0.03397,"peak_contact_force":55.03355,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":661.0,"raw_peak_contact_force":55.03355,"subtask_id":"approach_peg","tcp_end":[0.48261,0.06116,0.11205],"tcp_start":[0.46782,0.06867,0.23829],"tcp_to_object_dist_end":0.07899,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.49913,0.00098,0.02361],"object_pos_start":[0.49433,0.05884,0.03397],"object_to_goal_dist_end":0.08262,"object_to_goal_dist_start":0.13908,"object_z_max":0.03902,"peak_contact_force":0.4566,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":476.0,"raw_peak_contact_force":202.23479,"subtask_id":"push_channel","tcp_end":[0.48511,-0.08234,0.11108],"tcp_start":[0.48261,0.06116,0.11205],"tcp_to_object_dist_end":0.12161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49521,0.00125,0.0241],"object_pos_start":[0.49913,0.00098,0.02361],"object_to_goal_dist_end":0.08293,"object_to_goal_dist_start":0.08262,"object_z_max":0.02519,"peak_contact_force":0.63682,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":560.0,"raw_peak_contact_force":70.27241,"tcp_end":[0.48309,-0.08257,0.20043],"tcp_start":[0.48511,-0.08234,0.11108],"tcp_to_object_dist_end":0.19562,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9646,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.10087,"descend_to_peg.descend_force":9.30352,"push_through_channel.push_distance":0.14007},"optimized_scores":{"best_composite_score":0.06669,"best_fitness_score":0.02669,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":619.0,"contact_point_centroid":[0.47495,0.1199,0.05998],"force_p95":362.58599,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":530.16812,"mean_force":247.13336,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51462,0.08154,0.06822]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":166.0,"contact_point_centroid":[0.525,0.08627,0.06],"force_p95":273.08383,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.36185,"mean_force":118.74608,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51705,0.08377,0.06859]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":94.0,"contact_point_centroid":[0.52501,0.11975,0.05761],"force_p95":195.47842,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.14392,"mean_force":142.20995,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50914,0.07864,0.06914]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.47496,0.11989,0.05997],"force_p95":152.25208,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.48775,"mean_force":99.53094,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51805,0.08559,0.06951]},{"body_a":"peg","body_b":"channel_base_body","contact_count":697.0,"contact_point_centroid":[0.51415,0.08375,0.00905],"force_p95":59.43641,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.25659,"mean_force":47.12606,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51397,0.08124,0.06835]},{"body_a":"attachment","body_b":"peg","contact_count":697.0,"contact_point_centroid":[0.51385,0.08242,0.05724],"force_p95":58.25875,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.11163,"mean_force":46.38335,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51397,0.08124,0.06835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.50601,0.08485,0.00941],"force_p95":0.61743,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.04134,"mean_force":0.71345,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5157,0.08451,0.11317]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.51768,0.08667,0.0585],"force_p95":28.19522,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.65855,"mean_force":7.09994,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51792,0.08583,0.07006]},{"body_a":"peg","body_b":"channel_base_body","contact_count":325.0,"contact_point_centroid":[0.50598,0.08082,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.41346,"mean_force":0.6079,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5193,0.08402,0.10846]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50876,0.09858,0.05871],"force_p95":20.02411,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.02411,"mean_force":20.02411,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50878,0.08108,0.0708]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":517.0,"contact_point_centroid":[0.52517,0.08223,0.04647],"force_p95":9.09848,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.14672,"mean_force":3.22291,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51541,0.08207,0.06817]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":269.0,"contact_point_centroid":[0.52503,0.08464,0.04789],"force_p95":0.256,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.10011,"mean_force":0.09615,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51587,0.08464,0.10591]},{"body_a":"peg","body_b":"channel_base_body","contact_count":662.0,"contact_point_centroid":[0.50578,0.08089,0.00936],"force_p95":0.55542,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56981,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51019,0.15053,0.21789]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50285,0.22153,0.28712]}],"total_contact_groups":14},"final_pose_error":0.01136,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,0.08468,0.03378],"final_tcp_position":[0.51577,0.08448,0.15838],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":6211.45805,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":691.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54612,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":698.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.53057,0.0877,0.14621],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":325.0,"n_steps_budget":630.0,"object_pos_end":[0.50595,0.08086,0.03377],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":20.41346,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":326.0,"raw_peak_contact_force":20.41346,"subtask_id":"approach_peg","tcp_end":[0.50872,0.08107,0.07057],"tcp_start":[0.53057,0.0877,0.14621],"tcp_to_object_dist_end":0.0369,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":697.0,"n_steps_budget":900.0,"object_pos_end":[0.50729,0.08451,0.03373],"object_pos_start":[0.50595,0.08086,0.03377],"object_to_goal_dist_end":0.16479,"object_to_goal_dist_start":0.16109,"object_z_max":0.03407,"peak_contact_force":6211.45805,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2790.0,"raw_peak_contact_force":530.16812,"subtask_id":"push_channel","tcp_end":[0.51808,0.08553,0.06945],"tcp_start":[0.50872,0.08107,0.07057],"tcp_to_object_dist_end":0.03733,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50696,0.08468,0.03378],"object_pos_start":[0.50729,0.08451,0.03373],"object_to_goal_dist_end":0.16495,"object_to_goal_dist_start":0.16479,"object_z_max":0.03426,"peak_contact_force":0.59524,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":860.0,"raw_peak_contact_force":153.48775,"tcp_end":[0.51577,0.08448,0.15838],"tcp_start":[0.51808,0.08553,0.06945],"tcp_to_object_dist_end":0.12492,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```