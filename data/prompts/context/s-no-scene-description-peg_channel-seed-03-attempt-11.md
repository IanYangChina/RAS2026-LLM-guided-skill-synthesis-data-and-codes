## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | -0.1396 | 0.00 | ❌ rejected |
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0766 | 0.00 | ❌ rejected |
| 9 | approach → push → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | -0.1164 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4935 | 0.09 | ❌ rejected |
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0765 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.140) — your mutation base

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

- **Composite score**: -0.140
- **task_score** (E): 0.000
- **fitness_score**: 0.190  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1150 |
| descend_contact | 0.00 | 1.00 | 0.1475 |
| push_channel | 1.00 | 1.00 | 0.2299 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.143, 0.204) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 3.954 |
| descend_contact | descend | 0.00 / step_budget | (0.505, 0.143, 0.204)→(0.499, 0.131, 0.059) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.543 | 0.563 |
| push_channel | push | 1.00 / time_limit | (0.499, 0.131, 0.059)→(0.411, -0.012, 0.212) | (0.502, 0.081, 0.034)→(0.507, 0.086, 0.034) | 0.162→0.166 | 1.00 / 2.667 | 204.274 | 1597.541 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.331
- phase_breakdown.contact_peg_score: 0.651
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_pre_contact_score: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.198
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.134
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.3
- **Final σ (mean)**: 0.301


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32051,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.13997,"descend_contact.contact_force_threshold":28.65371,"descend_contact.descend_speed":0.15331,"push_channel.max_push_time":2.75725,"push_channel.push_distance":0.21946,"push_channel.push_speed":0.11199},"optimized_scores":{"best_composite_score":-0.13356,"best_fitness_score":0.19644,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":348.0,"contact_point_centroid":[0.53181,0.06385,0.05964],"force_p95":557.28472,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1624.53816,"mean_force":374.34779,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50149,0.12093,0.13629]},{"body_a":"channel_base_body","body_b":"link6","contact_count":679.0,"contact_point_centroid":[0.53319,-0.11028,0.06486],"force_p95":373.38341,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":474.79634,"mean_force":293.77551,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.45894,0.05488,0.17594]},{"body_a":"peg","body_b":"link7","contact_count":262.0,"contact_point_centroid":[0.50932,0.05752,0.05646],"force_p95":160.31822,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":236.27138,"mean_force":63.17943,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4798,0.09695,0.14758]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50427,0.06174,0.00925],"force_p95":98.68964,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":236.24664,"mean_force":17.19357,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.47336,0.0774,0.16023]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":196.0,"contact_point_centroid":[0.52513,0.06421,0.05047],"force_p95":11.12726,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.68631,"mean_force":3.32224,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.46779,0.07313,0.16588]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":37.0,"contact_point_centroid":[0.47489,0.06043,0.0594],"force_p95":8.42757,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.08161,"mean_force":1.47223,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50516,0.15033,0.09419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.49497,0.05901,0.0093],"force_p95":0.72903,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.61577,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48353,0.15805,0.24597]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49806,0.19576,0.29442]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.49397,0.05891,0.00939],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54618,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.47841,0.11602,0.13124]}],"total_contact_groups":9},"final_pose_error":0.33278,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50694,0.06398,0.03383],"final_tcp_position":[0.4166,-0.02583,0.21004],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":1624.53816,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":660.0,"object_pos_end":[0.49408,0.05903,0.03383],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5489,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":245.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.47039,0.12309,0.20326],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":583.0,"n_steps_budget":630.0,"object_pos_end":[0.49419,0.05882,0.0339],"object_pos_start":[0.49408,0.05903,0.03383],"object_to_goal_dist_end":0.13907,"object_to_goal_dist_start":0.13929,"object_z_max":0.0339,"peak_contact_force":0.54114,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":583.0,"raw_peak_contact_force":0.55382,"subtask_id":"contact_peg","tcp_end":[0.48898,0.10913,0.05866],"tcp_start":[0.47039,0.12309,0.20326],"tcp_to_object_dist_end":0.05631,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50694,0.06398,0.03383],"object_pos_start":[0.49419,0.05882,0.0339],"object_to_goal_dist_end":0.14428,"object_to_goal_dist_start":0.13907,"object_z_max":0.03564,"peak_contact_force":0.93265,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2522.0,"raw_peak_contact_force":1624.53816,"subtask_id":"push_to_goal","tcp_end":[0.4166,-0.02583,0.21004],"tcp_start":[0.48898,0.10913,0.05866],"tcp_to_object_dist_end":0.21743,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37333,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.2882,"descend_contact.contact_force_threshold":19.48292,"descend_contact.descend_speed":0.16565,"push_channel.max_push_time":1.45941,"push_channel.push_distance":0.20418,"push_channel.push_speed":0.08054},"optimized_scores":{"best_composite_score":-0.15354,"best_fitness_score":0.17646,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":489.0,"contact_point_centroid":[0.53677,0.08435,0.05973],"force_p95":534.81538,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1592.62124,"mean_force":353.64339,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50879,0.1355,0.14347]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":516.0,"contact_point_centroid":[0.53911,-0.06948,0.05985],"force_p95":357.83165,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":420.60642,"mean_force":295.30175,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.47618,0.10178,0.16302]},{"body_a":"channel_base_body","body_b":"link6","contact_count":142.0,"contact_point_centroid":[0.52756,-0.10004,0.06495],"force_p95":390.65276,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":397.43036,"mean_force":352.99212,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.45769,0.07602,0.17982]},{"body_a":"peg","body_b":"link7","contact_count":315.0,"contact_point_centroid":[0.51393,0.07892,0.0572],"force_p95":115.14541,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":193.86951,"mean_force":43.7412,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48379,0.11368,0.15161]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50766,0.08266,0.00927],"force_p95":76.04394,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.78249,"mean_force":14.50838,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49038,0.11657,0.15261]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":273.0,"contact_point_centroid":[0.52576,0.0845,0.04212],"force_p95":32.38237,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.32988,"mean_force":12.24339,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48125,0.10848,0.1592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":193.0,"contact_point_centroid":[0.50521,0.08099,0.00932],"force_p95":0.79437,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.62582,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51441,0.16821,0.24599]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50132,0.19653,0.29402]},{"body_a":"peg","body_b":"channel_base_body","contact_count":547.0,"contact_point_centroid":[0.50601,0.08086,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55104,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51463,0.13619,0.13048]}],"total_contact_groups":9},"final_pose_error":0.38336,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50688,0.085,0.03379],"final_tcp_position":[0.44768,0.06503,0.18926],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":1592.62124,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":222.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54302,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":229.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_pre_contact","tcp_end":[0.52714,0.14219,0.20366],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":547.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54611,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":547.0,"raw_peak_contact_force":0.55104,"subtask_id":"contact_peg","tcp_end":[0.50369,0.13066,0.05864],"tcp_start":[0.52714,0.14219,0.20366],"tcp_to_object_dist_end":0.05571,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50688,0.085,0.03379],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16526,"object_to_goal_dist_start":0.16109,"object_z_max":0.03648,"peak_contact_force":390.66143,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2735.0,"raw_peak_contact_force":1592.62124,"subtask_id":"push_to_goal","tcp_end":[0.44768,0.06503,0.18926],"tcp_start":[0.50369,0.13066,0.05864],"tcp_to_object_dist_end":0.16755,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26316,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.12283,"descend_contact.contact_force_threshold":9.1809,"descend_contact.descend_speed":0.21438,"push_channel.max_push_time":2.25953,"push_channel.push_distance":0.22133,"push_channel.push_speed":0.13834},"optimized_scores":{"best_composite_score":-0.13166,"best_fitness_score":0.19834,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":232.0,"contact_point_centroid":[0.53869,0.10775,0.05944],"force_p95":628.39768,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1575.46306,"mean_force":438.81576,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51183,0.17169,0.12976]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":479.0,"contact_point_centroid":[0.53345,-0.06142,0.05984],"force_p95":317.33252,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":366.28709,"mean_force":251.01417,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.45087,0.09131,0.18113]},{"body_a":"channel_base_body","body_b":"link6","contact_count":230.0,"contact_point_centroid":[0.51679,-0.10094,0.06486],"force_p95":230.24444,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.1943,"mean_force":211.57763,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.38867,-0.02179,0.22628]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50556,0.10669,0.00935],"force_p95":72.31936,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":228.38751,"mean_force":9.38734,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4528,0.08722,0.17544]},{"body_a":"peg","body_b":"link7","contact_count":147.0,"contact_point_centroid":[0.50507,0.09893,0.05665],"force_p95":153.28452,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":227.84299,"mean_force":60.94509,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4832,0.14036,0.1426]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":405.0,"contact_point_centroid":[0.5253,0.10847,0.04613],"force_p95":38.12184,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.5275,"mean_force":5.18211,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4411,0.07093,0.18755]},{"body_a":"peg","body_b":"channel_base_body","contact_count":170.0,"contact_point_centroid":[0.50526,0.10473,0.00934],"force_p95":0.77094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.61278,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50914,0.17954,0.2478]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50076,0.19783,0.2947]},{"body_a":"peg","body_b":"channel_base_body","contact_count":551.0,"contact_point_centroid":[0.50579,0.10456,0.00939],"force_p95":0.57547,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58307,"mean_force":0.54636,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50941,0.15813,0.13229]}],"total_contact_groups":9},"final_pose_error":0.32668,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,0.1085,0.03376],"final_tcp_position":[0.37001,-0.07425,0.23559],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1575.46306,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":197.0,"n_steps_budget":630.0,"object_pos_end":[0.50592,0.10457,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54311,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":202.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_pre_contact","tcp_end":[0.51749,0.16281,0.20642],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":551.0,"n_steps_budget":600.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.50592,0.10457,0.03383],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.54321,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":551.0,"raw_peak_contact_force":0.58307,"subtask_id":"contact_peg","tcp_end":[0.50301,0.154,0.0588],"tcp_start":[0.51749,0.16281,0.20642],"tcp_to_object_dist_end":0.05534,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,0.1085,0.03376],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.18874,"object_to_goal_dist_start":0.18489,"object_z_max":0.03596,"peak_contact_force":221.228,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2493.0,"raw_peak_contact_force":1575.46306,"subtask_id":"push_to_goal","tcp_end":[0.37001,-0.07425,0.23559],"tcp_start":[0.50301,0.154,0.0588],"tcp_to_object_dist_end":0.30479,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```