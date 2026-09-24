## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.3289 | 0.01 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | -0.3898 | 0.00 | ❌ rejected |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.1968 | 0.11 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | -0.1816 | 0.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.8850 | 0.51 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.329) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.12
  weight: 0.3
- id: push_through_channel
  target_entity: object
  metric: goal_progress
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
    offset:
    - 0.0
    - 0.08
    - 0.12
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - -0.015
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
  parameters:
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
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_timeout:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: push_through_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.12]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, -0.015]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_timeout: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.329
- **task_score** (E): 0.006
- **fitness_score**: 0.101  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1794 |
| align_to_channel | 0.33 | 1.00 | 0.0720 |
| push_through_channel | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.087, 0.164) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.539 | 3.526 |
| align_to_channel | descend | 0.33 / step_budget | (0.514, 0.087, 0.164)→(0.501, 0.086, 0.096) | (0.503, 0.080, 0.034)→(0.504, 0.078, 0.032) | 0.160→0.158 | 1.00 / 2.333 | 274.584 | 290.552 |
| push_through_channel | push | 0.00 / guard_failure | (0.501, 0.086, 0.096)→(0.501, 0.086, 0.096) | (0.504, 0.078, 0.032)→(0.504, 0.078, 0.032) | 0.158→0.158 | 1.00 / 2.333 | 71.382 | 83.421 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.029
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.018
- phase_score: 0.164
- phase_breakdown.push_through_channel_score: 0.000
- phase_breakdown.approach_peg_score: 0.821

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.106
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.018
- **Median Q (composite search score)**: -0.331
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.299


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53521,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_channel.align_speed":0.05832,"align_to_channel.align_tolerance":0.01302,"approach_peg.approach_speed":0.16936,"push_through_channel.push_distance":0.1778,"push_through_channel.push_force_limit":28.79081,"push_through_channel.push_lateral_offset":0.01371,"push_through_channel.push_speed":0.04497,"push_through_channel.push_timeout":3.79886},"optimized_scores":{"best_composite_score":-0.32414,"best_fitness_score":0.10586,"best_task_score":0.01826},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":23.0,"contact_point_centroid":[0.49603,0.29316,-0.0002],"force_p95":248.07093,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":259.03419,"mean_force":170.88838,"phase_index":1.0,"phase_name":"align_to_channel","phase_type":"descend","tcp_position_centroid":[0.49212,0.11268,0.06027]},{"body_a":"peg","body_b":"channel_base_body","contact_count":490.0,"contact_point_centroid":[0.49492,0.11946,0.00845],"force_p95":138.90543,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.27933,"mean_force":47.21211,"phase_index":1.0,"phase_name":"align_to_channel","phase_type":"descend","tcp_position_centroid":[0.48248,0.1212,0.08718]},{"body_a":"attachment","body_b":"peg","contact_count":195.0,"contact_point_centroid":[0.49278,0.12487,0.05102],"force_p95":142.00623,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.32356,"mean_force":117.25305,"phase_index":1.0,"phase_name":"align_to_channel","phase_type":"descend","tcp_position_centroid":[0.49253,0.11634,0.06098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.4953,0.11967,0.00687],"force_p95":113.24772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.1157,"mean_force":105.0288,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49235,0.11305,0.06089]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49322,0.13268,0.04967],"force_p95":112.58118,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.44498,"mean_force":104.43017,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49235,0.11305,0.06089]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.49801,0.30329,-0.00012],"force_p95":29.34422,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.60469,"mean_force":10.86823,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49235,0.11305,0.06089]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.4963,0.11915,0.00939],"force_p95":0.61715,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56048,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4913,0.16109,0.2297]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49933,0.19842,0.29745]}],"total_contact_groups":8},"final_pose_error":0.1779,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50041,0.11434,0.02948],"final_tcp_position":[0.49243,0.11312,0.061],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":259.03419,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":428.0,"n_steps_budget":630.0,"object_pos_end":[0.49604,0.1195,0.03419],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19962,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52183,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":427.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48454,0.12529,0.16738],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.50031,0.11431,0.0294],"object_pos_start":[0.49604,0.1195,0.03419],"object_to_goal_dist_end":0.1946,"object_to_goal_dist_start":0.19962,"object_z_max":0.03419,"peak_contact_force":232.47254,"phase_name":"align_to_channel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":708.0,"raw_peak_contact_force":259.03419,"tcp_end":[0.49232,0.11301,0.06084],"tcp_start":[0.48454,0.12529,0.16738],"tcp_to_object_dist_end":0.03247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50033,0.11431,0.02942],"object_pos_start":[0.50031,0.11431,0.0294],"object_to_goal_dist_end":0.1946,"object_to_goal_dist_start":0.1946,"object_z_max":0.02944,"peak_contact_force":114.1157,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":114.1157,"subtask_id":"push_through_channel","tcp_end":[0.49243,0.11312,0.061],"tcp_start":[0.49238,0.11308,0.06094],"tcp_to_object_dist_end":0.03258,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91304,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_channel.align_speed":0.06292,"align_to_channel.align_tolerance":0.00696,"approach_peg.approach_speed":0.18215,"push_through_channel.push_distance":0.18173,"push_through_channel.push_force_limit":24.00281,"push_through_channel.push_lateral_offset":0.01107,"push_through_channel.push_speed":0.0767,"push_through_channel.push_timeout":3.41418},"optimized_scores":{"best_composite_score":-0.33126,"best_fitness_score":0.09874,"best_task_score":1e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":627.0,"contact_point_centroid":[0.52505,0.11997,0.05992],"force_p95":298.79774,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.65405,"mean_force":274.70272,"phase_index":1.0,"phase_name":"align_to_channel","phase_type":"descend","tcp_position_centroid":[0.50887,0.07259,0.10888]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52504,0.11997,0.05994],"force_p95":67.02484,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.84696,"mean_force":55.9388,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5045,0.07702,0.1118]},{"body_a":"peg","body_b":"channel_base_body","contact_count":549.0,"contact_point_centroid":[0.50577,0.06303,0.00936],"force_p95":0.56549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57121,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51212,0.13227,0.22667]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50001,0.19686,0.29629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":949.0,"contact_point_centroid":[0.50594,0.06297,0.00938],"force_p95":0.55234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54657,"phase_index":1.0,"phase_name":"align_to_channel","phase_type":"descend","tcp_position_centroid":[0.50892,0.07135,0.11336]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52108,0.06945,0.00938],"force_p95":0.54788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54827,"mean_force":0.5456,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5045,0.07702,0.1118]}],"total_contact_groups":6},"final_pose_error":0.18179,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50604,0.06294,0.03382],"final_tcp_position":[0.50452,0.07705,0.11178],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":304.65405,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":577.0,"n_steps_budget":690.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55006,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":583.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52477,0.07084,0.1632],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":949.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06304,0.03382],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14321,"object_z_max":0.03382,"peak_contact_force":290.35901,"phase_name":"align_to_channel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1576.0,"raw_peak_contact_force":304.65405,"tcp_end":[0.50449,0.077,0.11182],"tcp_start":[0.52477,0.07084,0.1632],"tcp_to_object_dist_end":0.07925,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,0.06301,0.03382],"object_pos_start":[0.50602,0.06304,0.03382],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.1433,"object_z_max":0.03382,"peak_contact_force":50.62575,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":68.84696,"subtask_id":"push_through_channel","tcp_end":[0.50452,0.07705,0.11178],"tcp_start":[0.50451,0.07703,0.11179],"tcp_to_object_dist_end":0.07923,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37079,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_channel.align_speed":0.05095,"align_to_channel.align_tolerance":0.00808,"approach_peg.approach_speed":0.11822,"push_through_channel.push_distance":0.19218,"push_through_channel.push_force_limit":25.6543,"push_through_channel.push_lateral_offset":0.00871,"push_through_channel.push_speed":0.03257,"push_through_channel.push_timeout":3.99601},"optimized_scores":{"best_composite_score":-0.33125,"best_fitness_score":0.09875,"best_task_score":0.00012},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":707.0,"contact_point_centroid":[0.52506,0.11999,0.05992],"force_p95":300.10839,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.96773,"mean_force":277.84676,"phase_index":1.0,"phase_name":"align_to_channel","phase_type":"descend","tcp_position_centroid":[0.51217,0.06547,0.11331]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52505,0.11998,0.05994],"force_p95":65.50958,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.29903,"mean_force":52.56996,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50713,0.06832,0.11587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":646.0,"contact_point_centroid":[0.50591,0.05657,0.00936],"force_p95":0.60098,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57116,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51538,0.12924,0.22664]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49999,0.19708,0.29654]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50611,0.05666,0.00939],"force_p95":0.55106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55816,"mean_force":0.54642,"phase_index":1.0,"phase_name":"align_to_channel","phase_type":"descend","tcp_position_centroid":[0.51273,0.06462,0.11604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52272,0.05877,0.00939],"force_p95":0.5485,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54895,"mean_force":0.54529,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50713,0.06832,0.11587]}],"total_contact_groups":6},"final_pose_error":0.19223,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5062,0.05654,0.03385],"final_tcp_position":[0.50713,0.06835,0.11583],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":307.96773,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.05663,0.03379],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54388,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":683.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53125,0.06451,0.16268],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50622,0.05667,0.03385],"object_pos_start":[0.5061,0.05663,0.03379],"object_to_goal_dist_end":0.13695,"object_to_goal_dist_start":0.1369,"object_z_max":0.03386,"peak_contact_force":300.91907,"phase_name":"align_to_channel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1707.0,"raw_peak_contact_force":307.96773,"tcp_end":[0.50712,0.0683,0.11589],"tcp_start":[0.53125,0.06451,0.16268],"tcp_to_object_dist_end":0.08286,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50623,0.05663,0.03385],"object_pos_start":[0.50622,0.05667,0.03385],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13695,"object_z_max":0.03385,"peak_contact_force":49.4045,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":67.29903,"subtask_id":"push_through_channel","tcp_end":[0.50713,0.06835,0.11583],"tcp_start":[0.50713,0.06833,0.11585],"tcp_to_object_dist_end":0.08281,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```