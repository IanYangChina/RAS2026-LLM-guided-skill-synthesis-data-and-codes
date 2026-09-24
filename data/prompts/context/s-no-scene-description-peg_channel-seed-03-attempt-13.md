## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4964 | 0.10 | ✅ accepted |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4934 | 0.09 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | -0.1396 | 0.00 | ❌ rejected |
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0766 | 0.00 | ❌ rejected |
| 9 | approach → push → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | -0.1164 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.10 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.496) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_above_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: contact_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.5
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_peg
- id: descend_contact
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
    tolerance: 0.02
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
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_below_contact
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: contact_peg
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    max_push_time:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_below_contact, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]

## Design Metrics

- **Composite score**: 0.496
- **task_score** (E): 0.103
- **fitness_score**: 0.326  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1457 |
| descend_contact | 1.00 | 1.00 | 0.1424 |
| push_channel | 1.00 | 1.00 | 0.1702 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.097, 0.200) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.546 | 3.954 |
| descend_contact | descend | 1.00 / force_exceeded | (0.505, 0.097, 0.200)→(0.499, 0.082, 0.060) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 26.996 | 26.996 |
| push_channel | push | 1.00 / time_limit | (0.499, 0.082, 0.060)→(0.507, -0.086, 0.040) | (0.502, 0.082, 0.034)→(0.500, 0.030, 0.024) | 0.162→0.111 | 1.00 / 2.333 | 226.933 | 359.179 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.317
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.096
- phase_score: 0.506
- phase_breakdown.contact_peg_score: 0.646
- phase_breakdown.push_to_goal_score: 0.357
- phase_breakdown.reach_above_peg_score: 0.671

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.342
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.130
- **Median Q (composite search score)**: 0.503
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.288


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.81333,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.20359,"descend_contact.contact_force_threshold":9.39071,"descend_contact.descend_speed":0.16128,"push_channel.max_push_time":1.70646,"push_channel.push_distance":0.19411,"push_channel.push_speed":0.16289},"optimized_scores":{"best_composite_score":0.51203,"best_fitness_score":0.34203,"best_task_score":0.09578},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.52519,-0.08806,0.05996],"force_p95":527.92939,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":533.78931,"mean_force":415.28333,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50867,-0.08579,0.03806]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":387.0,"contact_point_centroid":[0.50331,-0.10017,0.06499],"force_p95":417.59921,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":530.82003,"mean_force":236.56125,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49929,-0.08719,0.04212]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.49924,0.01811,0.00856],"force_p95":68.9923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.8037,"mean_force":14.62476,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49341,-0.04087,0.04901]},{"body_a":"attachment","body_b":"peg","contact_count":294.0,"contact_point_centroid":[0.49655,0.03721,0.05787],"force_p95":71.49869,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.28241,"mean_force":47.58935,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4898,0.02959,0.05791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.49426,0.05886,0.00939],"force_p95":0.55036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.28127,"mean_force":0.59477,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.4775,0.06815,0.1308]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50048,0.05876,0.05885],"force_p95":26.80114,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.80114,"mean_force":26.80114,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48865,0.05977,0.06055]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52503,-0.01619,0.02434],"force_p95":6.36854,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.89088,"mean_force":1.57934,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49007,-0.08799,0.0467]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.49454,0.05907,0.00932],"force_p95":0.65931,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60076,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48294,0.1333,0.24426]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49806,0.1943,0.29475]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.0127,0.05842],"force_p95":0.70543,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71347,"mean_force":0.63311,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48941,-0.00377,0.05428]}],"total_contact_groups":10},"final_pose_error":0.18887,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49581,0.00817,0.02413],"final_tcp_position":[0.50793,-0.08541,0.03825],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":533.78931,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":297.0,"n_steps_budget":600.0,"object_pos_end":[0.49407,0.05888,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5481,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":303.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_above_peg","tcp_end":[0.46914,0.07635,0.19952],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":550.0,"n_steps_budget":600.0,"object_pos_end":[0.4942,0.05911,0.0339],"object_pos_start":[0.49407,0.05888,0.03384],"object_to_goal_dist_end":0.13937,"object_to_goal_dist_start":0.13914,"object_z_max":0.0339,"peak_contact_force":27.28127,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":551.0,"raw_peak_contact_force":27.28127,"subtask_id":"contact_peg","tcp_end":[0.48869,0.05974,0.06034],"tcp_start":[0.46914,0.07635,0.19952],"tcp_to_object_dist_end":0.02701,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49581,0.00817,0.02413],"object_pos_start":[0.4942,0.05911,0.0339],"object_to_goal_dist_end":0.08968,"object_to_goal_dist_start":0.13937,"object_z_max":0.0403,"peak_contact_force":250.97153,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1719.0,"raw_peak_contact_force":533.78931,"subtask_id":"push_to_goal","tcp_end":[0.50793,-0.08541,0.03825],"tcp_start":[0.48869,0.05974,0.06034],"tcp_to_object_dist_end":0.09541,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.5443,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.21335,"descend_contact.contact_force_threshold":8.33679,"descend_contact.descend_speed":0.13232,"push_channel.max_push_time":1.39083,"push_channel.push_distance":0.17715,"push_channel.push_speed":0.15287},"optimized_scores":{"best_composite_score":0.47446,"best_fitness_score":0.30446,"best_task_score":0.08315},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":275.0,"contact_point_centroid":[0.50628,-0.10018,0.065],"force_p95":238.72259,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.7344,"mean_force":210.08846,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50264,-0.08768,0.04282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.50188,0.04008,0.00858],"force_p95":66.90686,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.45077,"mean_force":15.03419,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50159,-0.02418,0.04988]},{"body_a":"attachment","body_b":"peg","contact_count":315.0,"contact_point_centroid":[0.51019,0.05831,0.05777],"force_p95":68.82375,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.93436,"mean_force":45.70199,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5037,0.05049,0.05781]},{"body_a":"peg","body_b":"channel_base_body","contact_count":587.0,"contact_point_centroid":[0.50601,0.08089,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.1837,"mean_force":0.58533,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51529,0.08888,0.12889]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51598,0.0811,0.05877],"force_p95":22.71598,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.71598,"mean_force":22.71598,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50412,0.08154,0.06053]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47497,0.00602,0.02435],"force_p95":8.26347,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.43705,"mean_force":2.32909,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49897,-0.0359,0.04862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.50538,0.08082,0.00933],"force_p95":0.62698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.6078,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51481,0.14412,0.24437]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50097,0.19502,0.29473]}],"total_contact_groups":8},"final_pose_error":0.17084,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50334,0.02931,0.02412],"final_tcp_position":[0.50953,-0.08657,0.03991],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":278.7344,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":279.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54666,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":286.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_above_peg","tcp_end":[0.52837,0.09661,0.19962],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":587.0,"n_steps_budget":720.0,"object_pos_end":[0.50596,0.08086,0.03377],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":23.1837,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":588.0,"raw_peak_contact_force":23.1837,"subtask_id":"contact_peg","tcp_end":[0.50409,0.08152,0.06031],"tcp_start":[0.52837,0.09661,0.19962],"tcp_to_object_dist_end":0.02661,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50334,0.02931,0.02412],"object_pos_start":[0.50596,0.08086,0.03377],"object_to_goal_dist_end":0.11051,"object_to_goal_dist_start":0.16109,"object_z_max":0.04028,"peak_contact_force":215.69376,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1593.0,"raw_peak_contact_force":278.7344,"subtask_id":"push_to_goal","tcp_end":[0.50953,-0.08657,0.03991],"tcp_start":[0.50409,0.08152,0.06031],"tcp_to_object_dist_end":0.11712,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.78947,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.42244,"descend_contact.contact_force_threshold":18.32129,"descend_contact.descend_speed":0.15595,"push_channel.max_push_time":2.18891,"push_channel.push_distance":0.22489,"push_channel.push_speed":0.15252},"optimized_scores":{"best_composite_score":0.50284,"best_fitness_score":0.33284,"best_task_score":0.13024},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":192.0,"contact_point_centroid":[0.50371,-0.1002,0.065],"force_p95":233.69779,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.01428,"mean_force":204.18344,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50035,-0.08797,0.04444]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50105,0.06364,0.00858],"force_p95":64.92308,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.43985,"mean_force":14.37629,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50031,-0.00701,0.05106]},{"body_a":"attachment","body_b":"peg","contact_count":311.0,"contact_point_centroid":[0.50936,0.0819,0.05794],"force_p95":66.53075,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.92363,"mean_force":44.23513,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50283,0.07403,0.05802]},{"body_a":"peg","body_b":"channel_base_body","contact_count":565.0,"contact_point_centroid":[0.506,0.10472,0.00939],"force_p95":0.57562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.52186,"mean_force":0.59936,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50988,0.11195,0.13051]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51513,0.10475,0.0588],"force_p95":30.03216,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.03216,"mean_force":30.03216,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50326,0.10511,0.06053]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47499,0.0295,0.02433],"force_p95":8.41341,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.57379,"mean_force":2.6584,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49832,-0.04941,0.04797]},{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.50506,0.10457,0.00935],"force_p95":0.67266,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.59899,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50948,0.15631,0.24591]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50053,0.19622,0.29519]}],"total_contact_groups":8},"final_pose_error":0.21778,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50128,0.05306,0.02406],"final_tcp_position":[0.50425,-0.08716,0.04244],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":265.01428,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.50589,0.10473,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18493,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54214,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":247.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_above_peg","tcp_end":[0.51843,0.11922,0.20229],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":565.0,"n_steps_budget":630.0,"object_pos_end":[0.50597,0.10457,0.03384],"object_pos_start":[0.50589,0.10473,0.03383],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18493,"object_z_max":0.03384,"peak_contact_force":30.52186,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":566.0,"raw_peak_contact_force":30.52186,"subtask_id":"contact_peg","tcp_end":[0.50324,0.10509,0.06031],"tcp_start":[0.51843,0.11922,0.20229],"tcp_to_object_dist_end":0.02662,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50128,0.05306,0.02406],"object_pos_start":[0.50597,0.10457,0.03384],"object_to_goal_dist_end":0.13402,"object_to_goal_dist_start":0.18477,"object_z_max":0.04031,"peak_contact_force":214.13298,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1506.0,"raw_peak_contact_force":265.01428,"subtask_id":"push_to_goal","tcp_end":[0.50425,-0.08716,0.04244],"tcp_start":[0.50324,0.10509,0.06031],"tcp_to_object_dist_end":0.14146,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```