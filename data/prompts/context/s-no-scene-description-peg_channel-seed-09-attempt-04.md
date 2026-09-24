## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.1558 | 0.00 | ❌ rejected |
| 3 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2569 | 0.06 | ❌ rejected |
| 2 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2568 | 0.06 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2566 | 0.06 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2578 | 0.06 | ✅ accepted |

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

## Current Skill (Q=-0.156) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0

```

## Design Metrics

- **Composite score**: -0.156
- **task_score** (E): 0.000
- **fitness_score**: 0.084  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1771 |
| align_lateral | 1.00 | 1.00 | 0.0455 |
| contact_peg | 1.00 | 1.00 | 0.0406 |
| push_channel | 0.00 | 1.00 | 0.0001 |
| retract | 1.00 | 1.00 | 0.0772 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.076, 0.177) | (0.512, 0.067, 0.040)→(0.502, 0.066, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.530 | 4.034 |
| align_lateral | align | 1.00 / step_budget | (0.509, 0.076, 0.177)→(0.502, 0.067, 0.137) | (0.502, 0.066, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.548 | 0.590 |
| contact_peg | contact | 1.00 / force_exceeded | (0.502, 0.067, 0.137)→(0.499, 0.066, 0.096) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 70.004 | 70.004 |
| push_channel | push | 0.00 / guard_failure | (0.499, 0.066, 0.096)→(0.499, 0.066, 0.096) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 48.755 | 80.041 |
| retract | retract | 1.00 / step_budget | (0.499, 0.066, 0.096)→(0.500, 0.065, 0.173) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.552 | 68.542 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.141
- phase_breakdown.push_through_channel_score: 0.000
- phase_breakdown.approach_peg_score: 0.471

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.085
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.156
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.262


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68817,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_tolerance":0.00716,"approach_peg.approach_speed":0.04834,"contact_peg.contact_force_threshold":8.29843,"push_channel.max_time":3.18521,"push_channel.push_distance":0.16637,"push_channel.push_speed":0.0348,"retract.retract_speed":0.07415},"optimized_scores":{"best_composite_score":-0.15551,"best_fitness_score":0.08449,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52502,0.12,0.05997],"force_p95":62.81263,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.81263,"mean_force":62.81263,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50438,0.06251,0.09945]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.52508,0.12,0.05989],"force_p95":28.62145,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.88778,"mean_force":5.84111,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50407,0.06237,0.09901]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52508,0.12,0.0599],"force_p95":35.53438,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.40928,"mean_force":27.66027,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50435,0.06251,0.09921]},{"body_a":"peg","body_b":"channel_base_body","contact_count":409.0,"contact_point_centroid":[0.50569,0.06304,0.00935],"force_p95":0.58109,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57962,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50603,0.14263,0.23653]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50252,0.21901,0.28797]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.50594,0.06291,0.00938],"force_p95":0.55269,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54658,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50276,0.06169,0.13519]},{"body_a":"peg","body_b":"channel_base_body","contact_count":179.0,"contact_point_centroid":[0.50589,0.063,0.00938],"force_p95":0.55249,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50543,0.06301,0.11862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":190.0,"contact_point_centroid":[0.50598,0.06299,0.00938],"force_p95":0.55121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55402,"mean_force":0.5466,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.51648,0.06839,0.15691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.5206,0.05442,0.00939],"force_p95":0.54666,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54689,"mean_force":0.54459,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50435,0.06251,0.09921]}],"total_contact_groups":9},"final_pose_error":0.011,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50594,0.06299,0.03381],"final_tcp_position":[0.50361,0.06194,0.17311],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":62.81263,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54229,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":443.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52538,0.07312,0.17622],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":190.0,"n_steps_budget":600.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.50601,0.06295,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54609,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":190.0,"raw_peak_contact_force":0.55402,"tcp_end":[0.50769,0.06405,0.13818],"tcp_start":[0.52538,0.07312,0.17622],"tcp_to_object_dist_end":0.10439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":179.0,"n_steps_budget":660.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":62.81263,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":180.0,"raw_peak_contact_force":62.81263,"tcp_end":[0.50437,0.06251,0.09927],"tcp_start":[0.50769,0.06405,0.13818],"tcp_to_object_dist_end":0.06548,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06295,0.03381],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":18.91126,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":36.40928,"subtask_id":"push_through_channel","tcp_end":[0.50428,0.06247,0.09906],"tcp_start":[0.50433,0.0625,0.09915],"tcp_to_object_dist_end":0.06527,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50594,0.06299,0.03381],"object_pos_start":[0.50598,0.06294,0.03381],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54395,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":520.0,"raw_peak_contact_force":40.88778,"tcp_end":[0.50361,0.06194,0.17311],"tcp_start":[0.50428,0.06247,0.09906],"tcp_to_object_dist_end":0.13932,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69149,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_tolerance":0.00599,"approach_peg.approach_speed":0.07862,"contact_peg.contact_force_threshold":8.62081,"push_channel.max_time":3.08624,"push_channel.push_distance":0.12121,"push_channel.push_speed":0.03104,"retract.retract_speed":0.03686},"optimized_scores":{"best_composite_score":-0.1553,"best_fitness_score":0.0847,"best_task_score":2e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52504,0.12,0.05995],"force_p95":72.47132,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.47132,"mean_force":72.47132,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50526,0.05624,0.10006]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52509,0.12,0.05987],"force_p95":41.2585,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.46537,"mean_force":30.39666,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50523,0.05624,0.0998]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.5251,0.12,0.05986],"force_p95":28.60501,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.66353,"mean_force":5.876,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50494,0.0561,0.09958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":424.0,"contact_point_centroid":[0.50582,0.05659,0.00935],"force_p95":0.60239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58407,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50932,0.13952,0.23715]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50184,0.22085,0.28566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":202.0,"contact_point_centroid":[0.50617,0.05666,0.00937],"force_p95":0.60112,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60533,"mean_force":0.54651,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.52036,0.06226,0.15632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.50609,0.0566,0.00938],"force_p95":0.59212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60254,"mean_force":0.54674,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50328,0.05543,0.13549]},{"body_a":"peg","body_b":"channel_base_body","contact_count":173.0,"contact_point_centroid":[0.50604,0.05665,0.00937],"force_p95":0.60092,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6014,"mean_force":0.54688,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50648,0.05672,0.11865]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.52287,0.05005,0.00937],"force_p95":0.52426,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52566,"mean_force":0.51161,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50523,0.05624,0.0998]}],"total_contact_groups":9},"final_pose_error":0.01092,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5061,0.05661,0.03379],"final_tcp_position":[0.50378,0.05565,0.17313],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":72.47132,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05659,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52919,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":461.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53169,0.0672,0.17586],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":202.0,"n_steps_budget":600.0,"object_pos_end":[0.50609,0.05663,0.03377],"object_pos_start":[0.50614,0.05659,0.03377],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13687,"object_z_max":0.03377,"peak_contact_force":0.59519,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":202.0,"raw_peak_contact_force":0.60533,"tcp_end":[0.50889,0.05771,0.13764],"tcp_start":[0.53169,0.0672,0.17586],"tcp_to_object_dist_end":0.10391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":173.0,"n_steps_budget":660.0,"object_pos_end":[0.50617,0.0566,0.03376],"object_pos_start":[0.50609,0.05663,0.03377],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13691,"object_z_max":0.03377,"peak_contact_force":72.47132,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":174.0,"raw_peak_contact_force":72.47132,"tcp_end":[0.50526,0.05625,0.09986],"tcp_start":[0.50889,0.05771,0.13764],"tcp_to_object_dist_end":0.0661,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05661,0.03377],"object_pos_start":[0.50617,0.0566,0.03376],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.13688,"object_z_max":0.03377,"peak_contact_force":18.32795,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":42.46537,"subtask_id":"push_through_channel","tcp_end":[0.50516,0.0562,0.09964],"tcp_start":[0.50521,0.05623,0.09974],"tcp_to_object_dist_end":0.06588,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.5061,0.05661,0.03379],"object_pos_start":[0.50611,0.05662,0.03376],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1369,"object_z_max":0.03379,"peak_contact_force":0.5456,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":520.0,"raw_peak_contact_force":40.66353,"tcp_end":[0.50378,0.05565,0.17313],"tcp_start":[0.50516,0.0562,0.09964],"tcp_to_object_dist_end":0.13936,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69149,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_tolerance":0.00663,"approach_peg.approach_speed":0.05234,"contact_peg.contact_force_threshold":7.47654,"push_channel.max_time":2.53506,"push_channel.push_distance":0.15418,"push_channel.push_speed":0.01814,"retract.retract_speed":0.04198},"optimized_scores":{"best_composite_score":-0.1567,"best_fitness_score":0.0833,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.47499,0.11995,0.05997],"force_p95":158.63796,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.24908,"mean_force":135.13788,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48808,0.07847,0.08896]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11999,0.05999],"force_p95":122.6234,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.07567,"mean_force":109.55302,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48816,0.07861,0.08885]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,0.11997,0.05998],"force_p95":74.72684,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.72684,"mean_force":74.72684,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48801,0.07841,0.08919]},{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.49422,0.07999,0.00936],"force_p95":0.6091,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.58146,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.47842,0.15024,0.23426]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5011,0.21958,0.28661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":221.0,"contact_point_centroid":[0.4937,0.07993,0.00938],"force_p95":0.58283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64427,"mean_force":0.54667,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48774,0.07868,0.11105]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49385,0.07994,0.00938],"force_p95":0.58028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64319,"mean_force":0.54645,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48858,0.07818,0.13013]},{"body_a":"peg","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.49394,0.07992,0.00938],"force_p95":0.57976,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60927,"mean_force":0.54652,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.47935,0.08364,0.1536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.47783,0.08781,0.00938],"force_p95":0.54384,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54526,"mean_force":0.53101,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48808,0.07847,0.08896]}],"total_contact_groups":9},"final_pose_error":0.0113,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49382,0.07994,0.03378],"final_tcp_position":[0.49125,0.0788,0.17282],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":161.24908,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07994,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.51785,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":400.0,"raw_peak_contact_force":3.77147,"subtask_id":"approach_peg","tcp_end":[0.47114,0.0888,0.1775],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":369.0,"n_steps_budget":600.0,"object_pos_end":[0.49381,0.07995,0.03377],"object_pos_start":[0.49382,0.07994,0.03377],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":0.50355,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":369.0,"raw_peak_contact_force":0.60927,"tcp_end":[0.48886,0.07962,0.13377],"tcp_start":[0.47114,0.0888,0.1775],"tcp_to_object_dist_end":0.10012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":221.0,"n_steps_budget":660.0,"object_pos_end":[0.49379,0.07997,0.03377],"object_pos_start":[0.49381,0.07995,0.03377],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.16019,"object_z_max":0.03379,"peak_contact_force":74.72684,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":222.0,"raw_peak_contact_force":74.72684,"tcp_end":[0.48805,0.07844,0.089],"tcp_start":[0.48886,0.07962,0.13377],"tcp_to_object_dist_end":0.05556,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.4938,0.07996,0.03377],"object_pos_start":[0.49379,0.07997,0.03377],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16021,"object_z_max":0.03377,"peak_contact_force":109.02668,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":161.24908,"subtask_id":"push_through_channel","tcp_end":[0.48814,0.07857,0.08887],"tcp_start":[0.4881,0.0785,0.08892],"tcp_to_object_dist_end":0.05541,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49382,0.07994,0.03378],"object_pos_start":[0.49382,0.07994,0.03377],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16018,"object_z_max":0.03383,"peak_contact_force":0.56786,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":545.0,"raw_peak_contact_force":124.07567,"tcp_end":[0.49125,0.0788,0.17282],"tcp_start":[0.48814,0.07857,0.08887],"tcp_to_object_dist_end":0.13907,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```