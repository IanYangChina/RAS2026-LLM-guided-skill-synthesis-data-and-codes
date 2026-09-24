## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2602 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2420 | 0.01 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1857 | 0.74 | ✅ accepted |

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

## Current Skill (Q=-0.260) — your mutation base

```yaml
skill: peg_channel
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: -0.260
- **task_score** (E): 0.003
- **fitness_score**: 0.050  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1817 |
| contact_1 | 1.00 | 1.00 | 0.0928 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.0464 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.094, 0.154) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.562 | 2.179 |
| contact_1 | contact | 1.00 / force_exceeded | (0.495, 0.094, 0.154)→(0.492, 0.093, 0.061) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 16.651 | 16.651 |
| push_1 | push | 0.00 / guard_failure | (0.491, 0.094, 0.061)→(0.491, 0.094, 0.061) | (0.500, 0.080, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 30.673 | 42.959 |
| retract_1 | retract | 1.00 / step_budget | (0.491, 0.094, 0.061)→(0.495, 0.089, 0.106) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.554 | 30.056 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.007
- alignment_error: None
- force_efficiency: 0.151
- terminal_score: 0.006
- phase_score: 0.086
- phase_breakdown.reach_pre_contact_score: 0.201
- phase_breakdown.push_to_goal_score: 0.037

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.054
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.006
- **Median Q (composite search score)**: -0.257
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.328


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21622,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09553,"approach_1.approach_tolerance":0.01119,"contact_1.descend_force_threshold":10.19739,"contact_1.descend_speed":0.03721,"push_1.push_distance":0.09143,"push_1.push_speed":0.04953,"push_1.push_tolerance":0.02019,"retract_1.retract_height":0.105,"retract_1.retract_speed":0.04514,"retract_1.retract_tolerance":0.0372},"optimized_scores":{"best_composite_score":-0.25599,"best_fitness_score":0.05401,"best_task_score":0.00607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.51473,0.0748,0.05835],"force_p95":41.27908,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.44525,"mean_force":24.70074,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50315,0.07618,0.06076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.49667,0.07082,0.00926],"force_p95":41.59354,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.27214,"mean_force":25.23795,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50315,0.07618,0.06076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.49927,0.06314,0.00944],"force_p95":13.84712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.26275,"mean_force":2.29736,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50145,0.0765,0.07848]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.51394,0.07521,0.05863],"force_p95":35.64286,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.92626,"mean_force":9.34202,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50254,0.07777,0.06083]},{"body_a":"peg","body_b":"channel_base_body","contact_count":514.0,"contact_point_centroid":[0.50375,0.0616,0.00938],"force_p95":0.55904,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.52016,"mean_force":0.57157,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50402,0.07569,0.10563]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51505,0.07502,0.05876],"force_p95":13.06683,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.06683,"mean_force":13.06683,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50338,0.07569,0.06144]},{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.50352,0.06159,0.00932],"force_p95":0.60494,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56912,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50319,0.13564,0.22186]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49982,0.19831,0.29814]}],"total_contact_groups":8},"final_pose_error":0.03687,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50315,0.06046,0.03469],"final_tcp_position":[0.50121,0.07225,0.10369],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":42.44525,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.06158,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.58507,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":379.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_pre_contact","tcp_end":[0.50718,0.07625,0.15256],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.06156,0.03377],"object_pos_start":[0.50379,0.06158,0.03376],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14177,"object_z_max":0.03389,"peak_contact_force":13.52016,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":515.0,"raw_peak_contact_force":13.52016,"subtask_id":"reach_pre_contact","tcp_end":[0.5034,0.07569,0.06128],"tcp_start":[0.50718,0.07625,0.15256],"tcp_to_object_dist_end":0.03093,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50353,0.06236,0.03407],"object_pos_start":[0.50375,0.06156,0.03377],"object_to_goal_dist_end":0.14253,"object_to_goal_dist_start":0.14175,"object_z_max":0.03414,"peak_contact_force":39.69075,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":42.44525,"subtask_id":"push_to_goal","tcp_end":[0.50305,0.07744,0.06035],"tcp_start":[0.50308,0.07729,0.06038],"tcp_to_object_dist_end":0.03031,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.50315,0.06046,0.03469],"object_pos_start":[0.50345,0.06254,0.03418],"object_to_goal_dist_end":0.1406,"object_to_goal_dist_start":0.1427,"object_z_max":0.03479,"peak_contact_force":0.53725,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":94.0,"raw_peak_contact_force":39.26275,"subtask_id":"push_to_goal","tcp_end":[0.50121,0.07225,0.10369],"tcp_start":[0.50305,0.07744,0.06035],"tcp_to_object_dist_end":0.07003,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21429,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10271,"approach_1.approach_tolerance":0.01647,"contact_1.descend_force_threshold":8.47944,"contact_1.descend_speed":0.05693,"push_1.push_distance":0.07224,"push_1.push_speed":0.03211,"push_1.push_tolerance":0.02327,"retract_1.retract_height":0.10626,"retract_1.retract_speed":0.04839,"retract_1.retract_tolerance":0.0342},"optimized_scores":{"best_composite_score":-0.26728,"best_fitness_score":0.04272,"best_task_score":0.00044},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48345,0.12,0.00939],"force_p95":43.12305,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.58629,"mean_force":29.53102,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49468,0.12574,0.06127]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50634,0.12514,0.05867],"force_p95":42.67934,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.14046,"mean_force":29.07098,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49468,0.12574,0.06127]},{"body_a":"peg","body_b":"channel_base_body","contact_count":90.0,"contact_point_centroid":[0.497,0.11596,0.00951],"force_p95":9.86052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.54879,"mean_force":1.55279,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49455,0.12571,0.08108]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50581,0.12526,0.059],"force_p95":21.01916,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.08721,"mean_force":6.59744,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49415,0.12568,0.06138]},{"body_a":"peg","body_b":"channel_base_body","contact_count":526.0,"contact_point_centroid":[0.50093,0.11603,0.00942],"force_p95":0.61352,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.2282,"mean_force":0.57781,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49531,0.12583,0.1075]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50636,0.12514,0.05879],"force_p95":18.77605,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.77605,"mean_force":18.77605,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4947,0.12575,0.06154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":293.0,"contact_point_centroid":[0.5009,0.11604,0.00933],"force_p95":0.7027,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49868,0.16242,0.22545]}],"total_contact_groups":7},"final_pose_error":0.0339,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50044,0.11597,0.03381],"final_tcp_position":[0.49622,0.12303,0.1073],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":44.58629,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.501,0.11609,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19619,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55774,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":293.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49841,0.12664,0.15663],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.50088,0.11609,0.03381],"object_pos_start":[0.501,0.11609,0.03386],"object_to_goal_dist_end":0.19619,"object_to_goal_dist_start":0.19619,"object_z_max":0.03402,"peak_contact_force":19.2282,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":527.0,"raw_peak_contact_force":19.2282,"subtask_id":"reach_pre_contact","tcp_end":[0.49472,0.12576,0.06137],"tcp_start":[0.49841,0.12664,0.15663],"tcp_to_object_dist_end":0.02985,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50082,0.11608,0.03384],"object_pos_start":[0.50088,0.11609,0.03381],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19619,"object_z_max":0.03388,"peak_contact_force":29.9539,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":44.58629,"subtask_id":"push_to_goal","tcp_end":[0.49459,0.12571,0.06111],"tcp_start":[0.49464,0.12572,0.06118],"tcp_to_object_dist_end":0.02958,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.50044,0.11597,0.03381],"object_pos_start":[0.5007,0.11605,0.03391],"object_to_goal_dist_end":0.19606,"object_to_goal_dist_start":0.19615,"object_z_max":0.0349,"peak_contact_force":0.57726,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":104.0,"raw_peak_contact_force":21.54879,"subtask_id":"push_to_goal","tcp_end":[0.49622,0.12303,0.1073],"tcp_start":[0.49459,0.12571,0.06111],"tcp_to_object_dist_end":0.07395,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0604,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11816,"approach_1.approach_tolerance":0.01347,"contact_1.descend_force_threshold":9.99178,"contact_1.descend_speed":0.02408,"push_1.push_distance":0.11228,"push_1.push_speed":0.07997,"push_1.push_tolerance":0.02768,"retract_1.retract_height":0.1001,"retract_1.retract_speed":0.08866,"retract_1.retract_tolerance":0.02855},"optimized_scores":{"best_composite_score":-0.25734,"best_fitness_score":0.05266,"best_task_score":0.00357},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.48909,0.06261,0.00938],"force_p95":37.36303,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.84478,"mean_force":12.29458,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47672,0.07854,0.06127]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.48833,0.07772,0.05869],"force_p95":36.37647,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.87416,"mean_force":11.72099,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47672,0.07854,0.06127]},{"body_a":"peg","body_b":"channel_base_body","contact_count":107.0,"contact_point_centroid":[0.4928,0.06469,0.00943],"force_p95":0.61856,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.35546,"mean_force":0.87772,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48068,0.0784,0.08299]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.48755,0.07798,0.05842],"force_p95":20.33881,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.98785,"mean_force":4.07354,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47611,0.08024,0.06095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":566.0,"contact_point_centroid":[0.4949,0.06379,0.0094],"force_p95":0.55033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.20561,"mean_force":0.57501,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47755,0.07804,0.10632]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.48866,0.07795,0.05912],"force_p95":16.7753,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.7753,"mean_force":16.7753,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47699,0.07802,0.06189]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.49575,0.06399,0.00935],"force_p95":0.62804,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57029,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48929,0.13605,0.22127]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49921,0.19695,0.29618]}],"total_contact_groups":8},"final_pose_error":0.02832,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49509,0.06298,0.03445],"final_tcp_position":[0.48691,0.07282,0.10834],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":41.84478,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.49497,0.064,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54392,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":370.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.48063,0.07858,0.15331],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.49516,0.0636,0.034],"object_pos_start":[0.49497,0.064,0.03392],"object_to_goal_dist_end":0.14381,"object_to_goal_dist_start":0.14422,"object_z_max":0.034,"peak_contact_force":17.20561,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":567.0,"raw_peak_contact_force":17.20561,"subtask_id":"reach_pre_contact","tcp_end":[0.47699,0.07803,0.06174],"tcp_start":[0.48063,0.07858,0.15331],"tcp_to_object_dist_end":0.03616,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":900.0,"object_pos_end":[0.49501,0.06446,0.03407],"object_pos_start":[0.49516,0.0636,0.034],"object_to_goal_dist_end":0.14466,"object_to_goal_dist_start":0.14381,"object_z_max":0.03413,"peak_contact_force":22.37529,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":41.84478,"subtask_id":"push_to_goal","tcp_end":[0.47641,0.0799,0.06079],"tcp_start":[0.47648,0.0797,0.06085],"tcp_to_object_dist_end":0.03603,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":600.0,"object_pos_end":[0.49509,0.06298,0.03445],"object_pos_start":[0.49489,0.06469,0.03417],"object_to_goal_dist_end":0.14317,"object_to_goal_dist_start":0.1449,"object_z_max":0.03456,"peak_contact_force":0.546,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":116.0,"raw_peak_contact_force":29.35546,"subtask_id":"push_to_goal","tcp_end":[0.48691,0.07282,0.10834],"tcp_start":[0.47641,0.0799,0.06079],"tcp_to_object_dist_end":0.07499,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```