## Search State

- **Seed**: 0
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2420 | 0.01 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1857 | 0.74 | ✅ accepted |

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

## Current Skill (Q=-0.242) — your mutation base

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

- **Composite score**: -0.242
- **task_score** (E): 0.012
- **fitness_score**: 0.068  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2203 |
| descend_1 | 1.00 | 1.00 | 0.0491 |
| push_1 | 0.00 | 1.00 | 0.0014 |
| retract_1 | 1.00 | 1.00 | 0.1477 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.096, 0.107) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.558 | 2.179 |
| descend_1 | descend | 1.00 / force_exceeded | (0.495, 0.096, 0.107)→(0.506, 0.093, 0.060) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 341.579 | 341.579 |
| push_1 | push | 0.00 / guard_failure | (0.505, 0.095, 0.057)→(0.505, 0.095, 0.056) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.333 | 495.477 | 629.283 |
| retract_1 | retract | 1.00 / step_budget | (0.505, 0.095, 0.056)→(0.503, 0.099, 0.204) | (0.500, 0.081, 0.033)→(0.492, 0.091, 0.028) | 0.161→0.172 | 1.00 / 1.000 | 0.537 | 299.908 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.034
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.023
- phase_score: 0.123
- phase_breakdown.reach_pre_contact_score: 0.444
- phase_breakdown.push_to_goal_score: 0.043

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.083
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.023
- **Median Q (composite search score)**: -0.238
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.283


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84375,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15806,"approach_1.approach_tolerance":0.00847,"descend_1.descend_force_threshold":15.49028,"descend_1.descend_speed":0.05345,"push_1.push_distance":0.18531,"push_1.push_speed":0.03297,"push_1.push_tolerance":0.01255,"retract_1.retract_height":0.15402,"retract_1.retract_speed":0.05597,"retract_1.retract_tolerance":0.0209},"optimized_scores":{"best_composite_score":-0.23816,"best_fitness_score":0.07184,"best_task_score":0.01423},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52564,0.07532,0.05885],"force_p95":1131.18261,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1137.3033,"mean_force":984.91323,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51681,0.06983,0.06057]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52575,0.07724,0.05964],"force_p95":812.69063,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":812.69063,"mean_force":812.69063,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51786,0.06902,0.06306]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.49983,0.0612,0.00955],"force_p95":2.9685,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":257.64166,"mean_force":5.11027,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51111,0.08208,0.1216]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.50904,0.07881,0.06079],"force_p95":251.83832,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":257.55645,"mean_force":64.59115,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50384,0.08198,0.05965]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52602,0.07308,0.05973],"force_p95":140.22896,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.29015,"mean_force":133.47094,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51429,0.07163,0.05835]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51548,0.07511,0.05868],"force_p95":83.08434,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.08434,"mean_force":83.08434,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51643,0.07014,0.05973]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50524,0.04851,0.00938],"force_p95":74.77007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.01666,"mean_force":28.03681,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51681,0.06983,0.06057]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47408,0.07334,0.05861],"force_p95":27.72757,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.12371,"mean_force":9.91149,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50047,0.08575,0.06066]},{"body_a":"peg","body_b":"channel_base_body","contact_count":651.0,"contact_point_centroid":[0.50362,0.06161,0.00935],"force_p95":0.58205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55902,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50286,0.1372,0.19876]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.19876,0.29835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.50435,0.0618,0.00938],"force_p95":0.5513,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55154,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51717,0.06968,0.08972]}],"total_contact_groups":11},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4992,0.05839,0.03556],"final_tcp_position":[0.5134,0.07462,0.19386],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":1137.3033,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":674.0,"n_steps_budget":960.0,"object_pos_end":[0.50379,0.06159,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.55144,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":670.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_pre_contact","tcp_end":[0.5071,0.07819,0.10629],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":29.0,"n_steps_budget":750.0,"object_pos_end":[0.50379,0.06157,0.03378],"object_pos_start":[0.50379,0.06159,0.03378],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14177,"object_z_max":0.03378,"peak_contact_force":812.69063,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30.0,"raw_peak_contact_force":812.69063,"subtask_id":"reach_pre_contact","tcp_end":[0.51723,0.0695,0.06154],"tcp_start":[0.5071,0.07819,0.10629],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06155,0.03378],"object_pos_start":[0.50379,0.06157,0.03378],"object_to_goal_dist_end":0.14174,"object_to_goal_dist_start":0.14175,"object_z_max":0.03378,"peak_contact_force":741.33997,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":1137.3033,"subtask_id":"push_to_goal","tcp_end":[0.51594,0.07046,0.05914],"tcp_start":[0.51643,0.07014,0.05973],"tcp_to_object_dist_end":0.0295,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.4992,0.05839,0.03556],"object_pos_start":[0.50355,0.06158,0.03381],"object_to_goal_dist_end":0.13847,"object_to_goal_dist_start":0.14176,"object_z_max":0.03824,"peak_contact_force":0.53931,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":546.0,"raw_peak_contact_force":257.64166,"subtask_id":"push_to_goal","tcp_end":[0.5134,0.07462,0.19386],"tcp_start":[0.51594,0.07046,0.05914],"tcp_to_object_dist_end":0.15977,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83505,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.12727,"approach_1.approach_tolerance":0.01275,"descend_1.descend_force_threshold":22.52574,"descend_1.descend_speed":0.04445,"push_1.push_distance":0.17341,"push_1.push_speed":0.05101,"push_1.push_tolerance":0.01463,"retract_1.retract_height":0.17406,"retract_1.retract_speed":0.06467,"retract_1.retract_tolerance":0.01},"optimized_scores":{"best_composite_score":-0.26051,"best_fitness_score":0.04949,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51118,0.13123,0.0573],"force_p95":302.92295,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":304.3427,"mean_force":238.40693,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51059,0.13255,0.0558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50652,0.11998,0.00925],"force_p95":302.81559,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":304.07441,"mean_force":238.68415,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51059,0.13255,0.0558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.48378,0.11952,0.00888],"force_p95":183.84265,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":194.74278,"mean_force":71.27589,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50159,0.15346,0.04457]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.50642,0.14932,0.04831],"force_p95":183.05109,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":193.16508,"mean_force":61.34866,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50014,0.15642,0.0444]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51156,0.13045,0.05895],"force_p95":121.50427,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.50427,"mean_force":121.50427,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51182,0.13082,0.05878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":33.0,"contact_point_centroid":[0.50045,0.11585,0.00943],"force_p95":0.61531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":121.48155,"mean_force":4.20467,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51099,0.12557,0.0881]},{"body_a":"peg","body_b":"world","contact_count":544.0,"contact_point_centroid":[0.48311,0.15663,-0.00188],"force_p95":0.69949,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.45987,"mean_force":0.66171,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5058,0.14887,0.12521]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47491,0.11998,0.01628],"force_p95":1.94123,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96491,"mean_force":0.82804,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49057,0.17625,0.0436]},{"body_a":"peg","body_b":"channel_base_body","contact_count":594.0,"contact_point_centroid":[0.50087,0.116,0.00937],"force_p95":0.63069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55778,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49811,0.16434,0.20143]}],"total_contact_groups":9},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.48214,0.15733,0.01413],"final_tcp_position":[0.50786,0.13826,0.2079],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":304.3427,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,0.11605,0.03382],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.57898,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":594.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49773,0.13013,0.1085],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":33.0,"n_steps_budget":930.0,"object_pos_end":[0.50079,0.11619,0.03386],"object_pos_start":[0.50098,0.11605,0.03382],"object_to_goal_dist_end":0.19629,"object_to_goal_dist_start":0.19615,"object_z_max":0.03392,"peak_contact_force":121.50427,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34.0,"raw_peak_contact_force":121.50427,"subtask_id":"reach_pre_contact","tcp_end":[0.51094,0.13173,0.05723],"tcp_start":[0.49773,0.13013,0.1085],"tcp_to_object_dist_end":0.02984,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50081,0.11633,0.03368],"object_pos_start":[0.50079,0.11619,0.03386],"object_to_goal_dist_end":0.19643,"object_to_goal_dist_start":0.19629,"object_z_max":0.03386,"peak_contact_force":304.3427,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":304.3427,"subtask_id":"push_to_goal","tcp_end":[0.51023,0.13433,0.05312],"tcp_start":[0.51031,0.1335,0.05438],"tcp_to_object_dist_end":0.02811,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.48214,0.15733,0.01413],"object_pos_start":[0.50092,0.11697,0.03333],"object_to_goal_dist_end":0.2394,"object_to_goal_dist_start":0.19709,"object_z_max":0.03333,"peak_contact_force":0.53282,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":600.0,"raw_peak_contact_force":194.74278,"subtask_id":"push_to_goal","tcp_end":[0.50786,0.13826,0.2079],"tcp_start":[0.51023,0.13433,0.05312],"tcp_to_object_dist_end":0.1964,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26144,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.18996,"approach_1.approach_tolerance":0.01541,"descend_1.descend_force_threshold":15.84587,"descend_1.descend_speed":0.0585,"push_1.push_distance":0.20247,"push_1.push_speed":0.05202,"push_1.push_tolerance":0.0106,"retract_1.retract_height":0.17266,"retract_1.retract_speed":0.01888,"retract_1.retract_tolerance":0.02376},"optimized_scores":{"best_composite_score":-0.22719,"best_fitness_score":0.08281,"best_task_score":0.02257},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47478,0.09789,0.05145],"force_p95":445.80467,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":447.33961,"mean_force":330.14265,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48621,0.09689,0.04881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49395,0.07495,0.00916],"force_p95":445.65801,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":446.20342,"mean_force":353.16969,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48928,0.07913,0.05899]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50083,0.08097,0.05705],"force_p95":443.999,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":444.5092,"mean_force":352.32519,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48928,0.07913,0.05899]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.49457,0.06024,0.00937],"force_p95":37.0664,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":340.80087,"mean_force":5.78827,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48632,0.09387,0.12627]},{"body_a":"attachment","body_b":"peg","contact_count":56.0,"contact_point_centroid":[0.49826,0.09324,0.05346],"force_p95":257.41438,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":338.84174,"mean_force":51.62386,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48736,0.09648,0.0526]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50165,0.08014,0.05913],"force_p95":90.54338,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.54338,"mean_force":90.54338,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49045,0.0774,0.06243]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.49127,0.06307,0.0094],"force_p95":0.5514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.31605,"mean_force":3.53828,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48951,0.0744,0.08958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":604.0,"contact_point_centroid":[0.49548,0.06394,0.00937],"force_p95":0.57169,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55963,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48834,0.13781,0.19817]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49928,0.19782,0.29652]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47496,0.06083,0.05915],"force_p95":0.11839,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12421,"mean_force":0.08276,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48615,0.09165,0.08177]}],"total_contact_groups":10},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49437,0.05837,0.03378],"final_tcp_position":[0.48652,0.0854,0.20935],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":447.33961,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":631.0,"n_steps_budget":780.0,"object_pos_end":[0.49496,0.06404,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14426,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5442,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":632.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.47892,0.08054,0.10705],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":30.0,"n_steps_budget":720.0,"object_pos_end":[0.49497,0.0638,0.03381],"object_pos_start":[0.49496,0.06404,0.03396],"object_to_goal_dist_end":0.14402,"object_to_goal_dist_start":0.14426,"object_z_max":0.03396,"peak_contact_force":90.54338,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":31.0,"raw_peak_contact_force":90.54338,"subtask_id":"reach_pre_contact","tcp_end":[0.4896,0.07835,0.06062],"tcp_start":[0.47892,0.08054,0.10705],"tcp_to_object_dist_end":0.03097,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49504,0.06391,0.03353],"object_pos_start":[0.49497,0.0638,0.03381],"object_to_goal_dist_end":0.14414,"object_to_goal_dist_start":0.14402,"object_z_max":0.03381,"peak_contact_force":440.74926,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":446.20342,"subtask_id":"push_to_goal","tcp_end":[0.48887,0.081,0.05599],"tcp_start":[0.48902,0.07997,0.05741],"tcp_to_object_dist_end":0.02889,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.49437,0.05837,0.03378],"object_pos_start":[0.49528,0.06457,0.03322],"object_to_goal_dist_end":0.13863,"object_to_goal_dist_start":0.1448,"object_z_max":0.03888,"peak_contact_force":0.53848,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":622.0,"raw_peak_contact_force":447.33961,"subtask_id":"push_to_goal","tcp_end":[0.48652,0.0854,0.20935],"tcp_start":[0.48887,0.081,0.05599],"tcp_to_object_dist_end":0.1778,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```