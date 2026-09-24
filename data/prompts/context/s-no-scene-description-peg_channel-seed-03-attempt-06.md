## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → align → push | linear_cartesian | linear_cartesian | joint_interpolation | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 7 | 0.0312 | 0.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4965 | 0.10 | ✅ accepted |
| 4 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |
| 3 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |

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

## Current Skill (Q=0.031) — your mutation base

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

- **Composite score**: 0.031
- **task_score** (E): 0.000
- **fitness_score**: 0.191  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1459 |
| descend_contact | 1.00 | 1.00 | 0.1422 |
| align_orientation | 1.00 | 1.00 | 0.0229 |
| push_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.097, 0.200) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.557 | 3.954 |
| descend_contact | descend | 1.00 / force_exceeded | (0.505, 0.097, 0.200)→(0.499, 0.082, 0.060) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 22.391 | 22.391 |
| align_orientation | align | 1.00 / step_budget | (0.499, 0.082, 0.060)→(0.494, 0.104, 0.059) | (0.502, 0.081, 0.034)→(0.500, 0.092, 0.034) | 0.162→0.172 | 1.00 / 2.333 | 41.688 | 47.364 |
| push_channel | push | 0.00 / guard_failure | (0.494, 0.104, 0.059)→(0.494, 0.104, 0.059) | (0.500, 0.092, 0.034)→(0.499, 0.092, 0.034) | 0.172→0.172 | 1.00 / 2.333 | 48.624 | 48.624 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.011
- terminal_score: 0.000
- phase_score: 0.332
- phase_breakdown.contact_peg_score: 0.655
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_above_peg_score: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.199
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: 0.037
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.389


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41558,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.align_speed":0.34036,"approach_peg.approach_speed":0.36687,"descend_contact.contact_force_threshold":5.04771,"descend_contact.descend_speed":0.05261,"push_channel.max_push_time":1.07795,"push_channel.push_distance":0.19319,"push_channel.push_speed":0.11817},"optimized_scores":{"best_composite_score":0.03722,"best_fitness_score":0.19722,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49446,0.08551,0.00947],"force_p95":47.87327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.87327,"mean_force":47.87327,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48474,0.08103,0.05927]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49642,0.07892,0.05832],"force_p95":46.58924,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.58924,"mean_force":46.58924,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48474,0.08103,0.05927]},{"body_a":"peg","body_b":"channel_base_body","contact_count":280.0,"contact_point_centroid":[0.49403,0.08044,0.00945],"force_p95":43.35817,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.35519,"mean_force":40.50023,"phase_index":2.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.48617,0.07221,0.05944]},{"body_a":"attachment","body_b":"peg","contact_count":280.0,"contact_point_centroid":[0.49778,0.0698,0.05848],"force_p95":43.13359,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.88731,"mean_force":40.36281,"phase_index":2.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.48617,0.07221,0.05944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":957.0,"contact_point_centroid":[0.49411,0.05898,0.00939],"force_p95":0.55031,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.88055,"mean_force":0.55783,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.47781,0.06771,0.12706]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50033,0.05959,0.059],"force_p95":11.38524,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.38524,"mean_force":11.38524,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48846,0.05978,0.06072]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.49454,0.05907,0.00932],"force_p95":0.65931,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60076,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48294,0.1333,0.24426]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":214.0,"contact_point_centroid":[0.47498,0.06501,0.01],"force_p95":3.33807,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.56996,"mean_force":2.76881,"phase_index":2.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.48574,0.07498,0.05934]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49806,0.1943,0.29475]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47496,0.0676,0.01],"force_p95":2.77453,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.77453,"mean_force":2.77453,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48474,0.08103,0.05927]}],"total_contact_groups":10},"final_pose_error":0.35509,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49298,0.06822,0.03438],"final_tcp_position":[0.48473,0.08105,0.05926],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":47.87327,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":297.0,"n_steps_budget":600.0,"object_pos_end":[0.49407,0.05888,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5481,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":303.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_above_peg","tcp_end":[0.46914,0.07635,0.19952],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.49395,0.0588,0.03396],"object_pos_start":[0.49407,0.05888,0.03384],"object_to_goal_dist_end":0.13906,"object_to_goal_dist_start":0.13914,"object_z_max":0.03396,"peak_contact_force":11.88055,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":958.0,"raw_peak_contact_force":11.88055,"subtask_id":"contact_peg","tcp_end":[0.48848,0.05977,0.06061],"tcp_start":[0.46914,0.07635,0.19952],"tcp_to_object_dist_end":0.02722,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":280.0,"n_steps_budget":600.0,"object_pos_end":[0.49297,0.06821,0.03438],"object_pos_start":[0.49395,0.0588,0.03396],"object_to_goal_dist_end":0.14848,"object_to_goal_dist_start":0.13906,"object_z_max":0.03445,"peak_contact_force":40.17221,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":774.0,"raw_peak_contact_force":44.35519,"tcp_end":[0.48474,0.08103,0.05927],"tcp_start":[0.48848,0.05977,0.06061],"tcp_to_object_dist_end":0.02918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49298,0.06822,0.03438],"object_pos_start":[0.49297,0.06821,0.03438],"object_to_goal_dist_end":0.1485,"object_to_goal_dist_start":0.14848,"object_z_max":0.03438,"peak_contact_force":47.87327,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":47.87327,"subtask_id":"push_to_goal","tcp_end":[0.48473,0.08105,0.05926],"tcp_start":[0.48474,0.08103,0.05927],"tcp_to_object_dist_end":0.02918,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22222,"average_solve_count":45.0,"average_success_count":45.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.align_speed":0.36378,"approach_peg.approach_speed":0.27282,"descend_contact.contact_force_threshold":7.30454,"descend_contact.descend_speed":0.13367,"push_channel.max_push_time":2.82048,"push_channel.push_distance":0.16982,"push_channel.push_speed":0.14002},"optimized_scores":{"best_composite_score":0.017,"best_fitness_score":0.177,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50938,0.10749,0.00943],"force_p95":48.96958,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.96958,"mean_force":48.96958,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4996,0.10309,0.05907]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51123,0.10067,0.0582],"force_p95":48.46422,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.46422,"mean_force":48.46422,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4996,0.10309,0.05907]},{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.50936,0.10251,0.00941],"force_p95":47.48915,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.29391,"mean_force":44.20542,"phase_index":2.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.50143,0.09379,0.05922]},{"body_a":"attachment","body_b":"peg","contact_count":244.0,"contact_point_centroid":[0.51302,0.09127,0.05831],"force_p95":47.02213,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.83374,"mean_force":43.73144,"phase_index":2.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.50143,0.09379,0.05922]},{"body_a":"peg","body_b":"channel_base_body","contact_count":587.0,"contact_point_centroid":[0.50601,0.08089,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.1837,"mean_force":0.58533,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51529,0.08888,0.12889]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51598,0.0811,0.05877],"force_p95":22.71598,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.71598,"mean_force":22.71598,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50412,0.08154,0.06053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.50538,0.08082,0.00933],"force_p95":0.62698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.6078,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51481,0.14412,0.24437]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50097,0.19502,0.29473]}],"total_contact_groups":8},"final_pose_error":0.35346,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50342,0.09136,0.03439],"final_tcp_position":[0.49959,0.10312,0.05907],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":48.96958,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":279.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54666,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":286.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_above_peg","tcp_end":[0.52837,0.09661,0.19962],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":587.0,"n_steps_budget":720.0,"object_pos_end":[0.50596,0.08086,0.03377],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":23.1837,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":588.0,"raw_peak_contact_force":23.1837,"subtask_id":"contact_peg","tcp_end":[0.50409,0.08152,0.06031],"tcp_start":[0.52837,0.09661,0.19962],"tcp_to_object_dist_end":0.02661,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":244.0,"n_steps_budget":600.0,"object_pos_end":[0.50342,0.09133,0.03439],"object_pos_start":[0.50596,0.08086,0.03377],"object_to_goal_dist_end":0.17146,"object_to_goal_dist_start":0.16109,"object_z_max":0.03445,"peak_contact_force":43.39965,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":488.0,"raw_peak_contact_force":48.29391,"tcp_end":[0.4996,0.10309,0.05907],"tcp_start":[0.50409,0.08152,0.06031],"tcp_to_object_dist_end":0.0276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50342,0.09136,0.03439],"object_pos_start":[0.50342,0.09133,0.03439],"object_to_goal_dist_end":0.17149,"object_to_goal_dist_start":0.17146,"object_z_max":0.03439,"peak_contact_force":48.96958,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":48.96958,"subtask_id":"push_to_goal","tcp_end":[0.49959,0.10312,0.05907],"tcp_start":[0.4996,0.10309,0.05907],"tcp_to_object_dist_end":0.0276,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85714,"average_solve_count":56.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.align_speed":0.43245,"approach_peg.approach_speed":0.10741,"descend_contact.contact_force_threshold":16.04333,"descend_contact.descend_speed":0.12486,"push_channel.max_push_time":1.38691,"push_channel.push_distance":0.21051,"push_channel.push_speed":0.16786},"optimized_scores":{"best_composite_score":0.03924,"best_fitness_score":0.19924,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50537,0.1192,0.00923],"force_p95":48.50905,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.44371,"mean_force":40.52299,"phase_index":2.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.49918,0.11987,0.05885]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49988,0.1199,0.00914],"force_p95":47.11011,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.02927,"mean_force":39.34164,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49655,0.12907,0.05837]},{"body_a":"attachment","body_b":"peg","contact_count":339.0,"contact_point_centroid":[0.50962,0.11462,0.05806],"force_p95":48.0446,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.00766,"mean_force":40.03554,"phase_index":2.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.49918,0.11987,0.05885]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50592,0.12179,0.05767],"force_p95":46.71436,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.64872,"mean_force":38.89327,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49655,0.12907,0.05837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":614.0,"contact_point_centroid":[0.50597,0.10468,0.00939],"force_p95":0.57563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.10909,"mean_force":0.59773,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50983,0.11173,0.12975]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51516,0.10458,0.05874],"force_p95":31.63913,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.63913,"mean_force":31.63913,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.5033,0.10506,0.06043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":230.0,"contact_point_centroid":[0.50511,0.10469,0.00935],"force_p95":0.65421,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.59558,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50936,0.15638,0.24598]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50046,0.19651,0.29555]}],"total_contact_groups":8},"final_pose_error":0.4198,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50209,0.11678,0.03371],"final_tcp_position":[0.4965,0.12887,0.05831],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":49.44371,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":257.0,"n_steps_budget":870.0,"object_pos_end":[0.50598,0.10472,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.5773,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":262.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_above_peg","tcp_end":[0.51843,0.11892,0.20194],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":614.0,"n_steps_budget":750.0,"object_pos_end":[0.506,0.10461,0.03384],"object_pos_start":[0.50598,0.10472,0.03383],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":32.10909,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":615.0,"raw_peak_contact_force":32.10909,"subtask_id":"contact_peg","tcp_end":[0.50328,0.10504,0.06022],"tcp_start":[0.51843,0.11892,0.20194],"tcp_to_object_dist_end":0.02653,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.50216,0.11685,0.03381],"object_pos_start":[0.506,0.10461,0.03384],"object_to_goal_dist_end":0.19696,"object_to_goal_dist_start":0.18481,"object_z_max":0.0342,"peak_contact_force":41.49294,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":678.0,"raw_peak_contact_force":49.44371,"tcp_end":[0.49658,0.12911,0.05841],"tcp_start":[0.50328,0.10504,0.06022],"tcp_to_object_dist_end":0.02804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50209,0.11678,0.03371],"object_pos_start":[0.50216,0.11685,0.03381],"object_to_goal_dist_end":0.19689,"object_to_goal_dist_start":0.19696,"object_z_max":0.03381,"peak_contact_force":49.02927,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":49.02927,"subtask_id":"push_to_goal","tcp_end":[0.4965,0.12887,0.05831],"tcp_start":[0.49658,0.12911,0.05841],"tcp_to_object_dist_end":0.02798,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```