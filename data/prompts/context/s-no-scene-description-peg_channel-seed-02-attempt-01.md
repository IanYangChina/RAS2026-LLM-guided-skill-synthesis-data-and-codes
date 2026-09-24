## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=0.197) — your mutation base

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

- **Composite score**: 0.197
- **task_score** (E): 0.134
- **fitness_score**: 0.157  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1780 |
| descend_to_peg | 1.00 | 1.00 | 0.0858 |
| push_through_channel | 0.67 | 1.00 | 0.0955 |
| retract_up | 1.00 | 1.00 | 0.0891 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.076, 0.181) | (0.494, 0.068, 0.040)→(0.499, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.548 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.076, 0.181)→(0.492, 0.070, 0.097) | (0.499, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 45.327 | 45.327 |
| push_through_channel | push | 0.67 / step_budget | (0.492, 0.070, 0.097)→(0.498, -0.021, 0.096) | (0.498, 0.068, 0.034)→(0.502, 0.027, 0.028) | 0.148→0.108 | 1.00 / 2.667 | 2106.948 | 357.142 |
| retract_up | retract | 1.00 / step_budget | (0.498, -0.021, 0.096)→(0.495, -0.021, 0.185) | (0.502, 0.027, 0.028)→(0.498, 0.027, 0.027) | 0.108→0.108 | 1.00 / 1.000 | 0.444 | 108.427 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.402
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.268
- phase_score: 0.246
- phase_breakdown.approach_peg_score: 0.189
- phase_breakdown.push_channel_score: 0.260

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.255
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.268
- **Median Q (composite search score)**: 0.229
- **K-run variance**: 0.0092
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.268


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96429,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.1073,"descend_to_peg.descend_force":8.54702,"push_through_channel.push_distance":0.17391},"optimized_scores":{"best_composite_score":0.29468,"best_fitness_score":0.25468,"best_task_score":0.26829},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":596.0,"contact_point_centroid":[0.47498,0.10546,0.05997],"force_p95":283.2235,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":330.974,"mean_force":241.12757,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49142,0.04631,0.10061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":690.0,"contact_point_centroid":[0.49688,0.05231,0.00926],"force_p95":125.17047,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.24554,"mean_force":11.73707,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49215,0.03824,0.10006]},{"body_a":"peg","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.49431,0.05898,0.06176],"force_p95":170.97204,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.93132,"mean_force":121.07066,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50036,0.00342,0.09179]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47499,-0.00597,0.05999],"force_p95":106.3983,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.96408,"mean_force":72.67476,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48952,-0.07769,0.10661]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.06],"force_p95":62.46942,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.46942,"mean_force":62.46942,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48376,0.0673,0.10712]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":33.0,"contact_point_centroid":[0.52524,-0.00388,0.02549],"force_p95":13.53576,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.49403,"mean_force":3.1988,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49024,-0.05762,0.1053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49519,-0.00024,0.00814],"force_p95":0.92827,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.30955,"mean_force":1.00155,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48745,-0.07775,0.15083]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":54.0,"contact_point_centroid":[0.47498,-0.00319,0.02454],"force_p95":9.44912,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.89033,"mean_force":4.2984,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48725,-0.07764,0.15026]},{"body_a":"peg","body_b":"channel_base_body","contact_count":662.0,"contact_point_centroid":[0.49537,0.06379,0.00937],"force_p95":0.5665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55842,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48668,0.14338,0.22102]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47473,0.00248,0.05392],"force_p95":2.3074,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4179,"mean_force":1.51304,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49436,-0.02707,0.09897]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50406,0.21534,0.293]},{"body_a":"peg","body_b":"channel_base_body","contact_count":239.0,"contact_point_centroid":[0.4951,0.06441,0.0094],"force_p95":0.55032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55213,"mean_force":0.54534,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48105,0.06916,0.12948]}],"total_contact_groups":12},"final_pose_error":0.01092,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.494,-0.00038,0.02414],"final_tcp_position":[0.48753,-0.07759,0.19585],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":330.974,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.49532,0.06394,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14414,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54852,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":690.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.47998,0.07179,0.15301],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":239.0,"n_steps_budget":660.0,"object_pos_end":[0.49483,0.06387,0.034],"object_pos_start":[0.49532,0.06394,0.03397],"object_to_goal_dist_end":0.14409,"object_to_goal_dist_start":0.14414,"object_z_max":0.034,"peak_contact_force":62.46942,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":240.0,"raw_peak_contact_force":62.46942,"subtask_id":"approach_peg","tcp_end":[0.4838,0.0673,0.10694],"tcp_start":[0.47998,0.07179,0.15301],"tcp_to_object_dist_end":0.07385,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":704.0,"n_steps_budget":1000.0,"object_pos_end":[0.5051,-0.00033,0.02491],"object_pos_start":[0.49483,0.06387,0.034],"object_to_goal_dist_end":0.08125,"object_to_goal_dist_start":0.14409,"object_z_max":0.0391,"peak_contact_force":1.418,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1388.0,"raw_peak_contact_force":330.974,"subtask_id":"push_channel","tcp_end":[0.4896,-0.07733,0.10656],"tcp_start":[0.4838,0.0673,0.10694],"tcp_to_object_dist_end":0.1133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.494,-0.00038,0.02414],"object_pos_start":[0.5051,-0.00033,0.02491],"object_to_goal_dist_end":0.08141,"object_to_goal_dist_start":0.08125,"object_z_max":0.02529,"peak_contact_force":0.6672,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":600.0,"raw_peak_contact_force":108.96408,"tcp_end":[0.48753,-0.07759,0.19585],"tcp_start":[0.4896,-0.07733,0.10656],"tcp_to_object_dist_end":0.18838,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96552,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.19935,"descend_to_peg.descend_force":11.13461,"push_through_channel.push_distance":0.16071},"optimized_scores":{"best_composite_score":0.22901,"best_fitness_score":0.18901,"best_task_score":0.13471},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":79.0,"contact_point_centroid":[0.47499,0.07208,0.05998],"force_p95":159.8656,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.278,"mean_force":124.6683,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48417,0.00761,0.1116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":235.0,"contact_point_centroid":[0.49554,0.03468,0.00901],"force_p95":110.01723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.56589,"mean_force":35.98517,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48449,0.00193,0.11182]},{"body_a":"peg","body_b":"link7","contact_count":94.0,"contact_point_centroid":[0.48782,0.05033,0.06253],"force_p95":114.62683,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.20417,"mean_force":88.57645,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48483,-0.00633,0.11212]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.47499,-0.004,0.05999],"force_p95":61.4834,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.51304,"mean_force":52.21662,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48499,-0.07011,0.11109]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47497,0.11999,0.05996],"force_p95":52.21874,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.21874,"mean_force":52.21874,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48264,0.06114,0.11214]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.4932,-0.00313,0.00807],"force_p95":0.64948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.16964,"mean_force":0.64018,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48289,-0.07036,0.15539]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47497,-0.02818,0.02417],"force_p95":9.62868,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.76998,"mean_force":2.67312,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48353,-0.07096,0.11629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":593.0,"contact_point_centroid":[0.49442,0.05891,0.00936],"force_p95":0.56457,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57088,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48059,0.14244,0.26024]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50213,0.22043,0.28757]},{"body_a":"peg","body_b":"channel_base_body","contact_count":667.0,"contact_point_centroid":[0.49416,0.05898,0.00939],"force_p95":0.55019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54583,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47444,0.06457,0.17487]}],"total_contact_groups":10},"final_pose_error":0.01085,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49308,-0.00337,0.02415],"final_tcp_position":[0.48298,-0.07021,0.20042],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":200.278,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":622.0,"n_steps_budget":990.0,"object_pos_end":[0.4942,0.05907,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":628.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46783,0.06869,0.23967],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.49416,0.05919,0.03397],"object_pos_start":[0.4942,0.05907,0.03388],"object_to_goal_dist_end":0.13945,"object_to_goal_dist_start":0.13933,"object_z_max":0.03397,"peak_contact_force":52.21874,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":668.0,"raw_peak_contact_force":52.21874,"subtask_id":"approach_peg","tcp_end":[0.48267,0.06113,0.11199],"tcp_start":[0.46783,0.06869,0.23967],"tcp_to_object_dist_end":0.07888,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.49506,-0.00304,0.02399],"object_pos_start":[0.49416,0.05919,0.03397],"object_to_goal_dist_end":0.07877,"object_to_goal_dist_start":0.13945,"object_z_max":0.03895,"peak_contact_force":104.82434,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":408.0,"raw_peak_contact_force":200.278,"subtask_id":"push_channel","tcp_end":[0.485,-0.06992,0.11108],"tcp_start":[0.48267,0.06113,0.11199],"tcp_to_object_dist_end":0.11027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49308,-0.00337,0.02415],"object_pos_start":[0.49506,-0.00304,0.02399],"object_to_goal_dist_end":0.07856,"object_to_goal_dist_start":0.07877,"object_z_max":0.02465,"peak_contact_force":0.64358,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":553.0,"raw_peak_contact_force":62.51304,"tcp_end":[0.48298,-0.07021,0.20042],"tcp_start":[0.485,-0.06992,0.11108],"tcp_to_object_dist_end":0.18879,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96396,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.10455,"descend_to_peg.descend_force":16.76734,"push_through_channel.push_distance":0.14174},"optimized_scores":{"best_composite_score":0.06666,"best_fitness_score":0.02666,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":623.0,"contact_point_centroid":[0.47495,0.1199,0.05998],"force_p95":373.40192,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":540.175,"mean_force":250.47537,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51464,0.0816,0.06812]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":173.0,"contact_point_centroid":[0.525,0.08622,0.06],"force_p95":305.19428,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.83643,"mean_force":124.75774,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51697,0.0837,0.0685]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":92.0,"contact_point_centroid":[0.52501,0.11975,0.05809],"force_p95":197.83984,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.47467,"mean_force":135.7342,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50911,0.07863,0.06897]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.47497,0.11991,0.05997],"force_p95":150.4247,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.80414,"mean_force":98.81609,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51813,0.08574,0.06956]},{"body_a":"peg","body_b":"channel_base_body","contact_count":697.0,"contact_point_centroid":[0.51414,0.08379,0.00902],"force_p95":60.92525,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.02893,"mean_force":48.32898,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51402,0.08131,0.06824]},{"body_a":"attachment","body_b":"peg","contact_count":697.0,"contact_point_centroid":[0.51389,0.08249,0.05716],"force_p95":60.03677,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.87081,"mean_force":47.592,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51402,0.08131,0.06824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50579,0.08493,0.00942],"force_p95":0.59709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.96141,"mean_force":0.67534,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51581,0.08469,0.11317]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.51776,0.08684,0.05851],"force_p95":24.21984,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.56542,"mean_force":5.61734,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51801,0.08599,0.07006]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.50607,0.08088,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.29208,"mean_force":0.60814,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5192,0.084,0.11018]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5086,0.09864,0.05878],"force_p95":20.871,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.871,"mean_force":20.871,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50862,0.08105,0.07094]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":532.0,"contact_point_centroid":[0.52515,0.0822,0.04698],"force_p95":9.99867,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.92499,"mean_force":3.23482,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51536,0.08208,0.06809]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":206.0,"contact_point_centroid":[0.52501,0.08473,0.04595],"force_p95":0.25873,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.74123,"mean_force":0.12289,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51607,0.0849,0.10346]},{"body_a":"peg","body_b":"channel_base_body","contact_count":654.0,"contact_point_centroid":[0.50573,0.08089,0.00936],"force_p95":0.55553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5701,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51014,0.15062,0.21943]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50284,0.22152,0.28711]}],"total_contact_groups":14},"final_pose_error":0.01165,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50697,0.08471,0.03378],"final_tcp_position":[0.51585,0.08464,0.15813],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":6214.60112,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55006,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":690.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.5306,0.08771,0.14964],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":338.0,"n_steps_budget":630.0,"object_pos_end":[0.50598,0.08085,0.03377],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16108,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":21.29208,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":339.0,"raw_peak_contact_force":21.29208,"subtask_id":"approach_peg","tcp_end":[0.50856,0.08104,0.0707],"tcp_start":[0.5306,0.08771,0.14964],"tcp_to_object_dist_end":0.03702,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":697.0,"n_steps_budget":900.0,"object_pos_end":[0.50728,0.08461,0.03376],"object_pos_start":[0.50598,0.08085,0.03377],"object_to_goal_dist_end":0.16489,"object_to_goal_dist_start":0.16108,"object_z_max":0.03404,"peak_contact_force":6214.60112,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2814.0,"raw_peak_contact_force":540.175,"subtask_id":"push_channel","tcp_end":[0.51816,0.08568,0.06951],"tcp_start":[0.50856,0.08104,0.0707],"tcp_to_object_dist_end":0.03738,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50697,0.08471,0.03378],"object_pos_start":[0.50728,0.08461,0.03376],"object_to_goal_dist_end":0.16498,"object_to_goal_dist_start":0.16489,"object_z_max":0.03425,"peak_contact_force":0.02211,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":766.0,"raw_peak_contact_force":153.80414,"tcp_end":[0.51585,0.08464,0.15813],"tcp_start":[0.51816,0.08568,0.06951],"tcp_to_object_dist_end":0.12467,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```