## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → grasp → lift → align → insert → release → retract | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_motion | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.4052 | 0.00 | ❌ rejected |
| 4 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3047 | 0.61 | ❌ rejected |
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3041 | 0.61 | ✅ accepted |
| 2 | approach → contact → grasp → insert → retract | linear_cartesian | linear_cartesian | — | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | force_exceeded | pose_tolerance | 9 | 0.0641 | 0.01 | ❌ rejected |
| 1 | approach → contact → grasp → insert → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | force_exceeded | pose_tolerance | 8 | 0.2346 | 0.18 | ❌ rejected |

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

## Current Skill (Q=-0.405) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: -0.405
- **task_score** (E): 0.000
- **fitness_score**: 0.345  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1907 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.0691 |
| align_1 | 1.00 | 1.00 | 0.2049 |
| insert_1 | 0.00 | 1.00 | 0.0494 |
| release_1 | 1.00 | 1.00 | 0.0100 |
| retract_1 | 0.67 | 1.00 | 0.1163 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.091, 0.145) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.541 | 3.242 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.090, 0.136)→(0.511, 0.090, 0.136) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 1.000 | 0.543 | 0.559 |
| lift_1 | lift | 1.00 / step_budget | (0.511, 0.090, 0.136)→(0.503, 0.084, 0.204) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.165 | 1.00 / 1.000 | 0.541 | 0.559 |
| align_1 | align | 1.00 / step_budget | (0.503, 0.084, 0.204)→(0.500, -0.080, 0.081) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 1.000 | 0.545 | 0.559 |
| insert_1 | insert | 0.00 / step_budget | (0.500, -0.080, 0.081)→(0.495, -0.129, 0.078) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.165 | 1.00 / 1.000 | 0.549 | 0.559 |
| release_1 | release | 1.00 / step_budget | (0.495, -0.129, 0.078)→(0.489, -0.127, 0.070) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 1.333 | 2.656 | 2.659 |
| retract_1 | retract | 0.67 / step_budget | (0.489, -0.127, 0.070)→(0.486, -0.127, 0.186) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.164 | 1.00 / 1.000 | 0.547 | 26.048 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.959
- terminal_score: 0.000
- phase_score: 0.593
- phase_breakdown.align_channel_score: 0.951
- phase_breakdown.insert_channel_score: 0.000
- phase_breakdown.lift_peg_score: 0.720
- phase_breakdown.approach_peg_score: 0.819

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.356
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.403
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.255


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09465,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_x":0.00259,"align_1.align_offset_y":-0.00894,"align_1.align_speed":0.06062,"approach_1.approach_speed":0.06818,"grasp_1.grasp_duration":0.75724,"insert_1.insertion_depth":0.17135,"insert_1.insertion_force":15.46781,"insert_1.insertion_speed":0.02585,"lift_1.lift_speed":0.04955,"release_1.release_duration":1.03436,"retract_1.retract_height":0.1791,"retract_1.retract_speed":0.05794},"optimized_scores":{"best_composite_score":-0.41815,"best_fitness_score":0.33185,"best_task_score":5e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":658.0,"contact_point_centroid":[0.50575,0.08085,0.00936],"force_p95":0.55547,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56996,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51461,0.14166,0.21771]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49995,0.19771,0.29652]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50601,0.08092,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52502,0.08672,0.1365]},{"body_a":"peg","body_b":"channel_base_body","contact_count":698.0,"contact_point_centroid":[0.50595,0.08083,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51246,0.08331,0.16897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":832.0,"contact_point_centroid":[0.50599,0.0809,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50048,-0.0002,0.14023]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50593,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49457,-0.10589,0.07754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50611,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54675,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.48955,-0.12902,0.07266]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50592,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4844,-0.12792,0.1194]}],"total_contact_groups":8},"final_pose_error":0.0797,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50596,0.08088,0.03378],"final_tcp_position":[0.48462,-0.12795,0.16959],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":4.32595,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5464,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":694.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.53,0.0878,0.14455],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":550.0,"raw_peak_contact_force":0.55007,"tcp_end":[0.52432,0.08661,0.13539],"tcp_start":[0.52432,0.08661,0.13539],"tcp_to_object_dist_end":0.10342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.5464,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":698.0,"raw_peak_contact_force":0.55006,"subtask_id":"lift_peg","tcp_end":[0.50433,0.08075,0.20393],"tcp_start":[0.52432,0.08661,0.13539],"tcp_to_object_dist_end":0.17016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08085,0.03378],"object_pos_start":[0.50595,0.08088,0.03378],"object_to_goal_dist_end":0.16108,"object_to_goal_dist_start":0.16111,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":832.0,"raw_peak_contact_force":0.55006,"subtask_id":"align_channel","tcp_end":[0.49901,-0.07985,0.08143],"tcp_start":[0.50433,0.08075,0.20393],"tcp_to_object_dist_end":0.16776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08088,0.03378],"object_pos_start":[0.50596,0.08085,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16108,"object_z_max":0.03378,"peak_contact_force":0.55006,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55006,"subtask_id":"insert_channel","tcp_end":[0.49366,-0.12982,0.07797],"tcp_start":[0.49901,-0.07985,0.08143],"tcp_to_object_dist_end":0.21564,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50595,0.08085,0.03378],"object_pos_start":[0.50597,0.08088,0.03378],"object_to_goal_dist_end":0.16108,"object_to_goal_dist_start":0.16111,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.48759,-0.1286,0.07013],"tcp_start":[0.49366,-0.12982,0.07797],"tcp_to_object_dist_end":0.21338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08088,0.03378],"object_pos_start":[0.50595,0.08085,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16108,"object_z_max":0.03378,"peak_contact_force":0.55006,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.48462,-0.12795,0.16959],"tcp_start":[0.48759,-0.1286,0.07013],"tcp_to_object_dist_end":0.25002,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28505,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_x":0.0038,"align_1.align_offset_y":-0.00986,"align_1.align_speed":0.0694,"approach_1.approach_speed":0.09605,"grasp_1.grasp_duration":1.10065,"insert_1.insertion_depth":0.08347,"insert_1.insertion_force":14.81361,"insert_1.insertion_speed":0.01834,"lift_1.lift_speed":0.06129,"release_1.release_duration":0.79253,"retract_1.retract_height":0.19516,"retract_1.retract_speed":0.09383},"optimized_scores":{"best_composite_score":-0.40343,"best_fitness_score":0.34657,"best_task_score":0.00035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50051,-0.11241,0.06499],"force_p95":75.32516,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.04357,"mean_force":61.03409,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48917,-0.11249,0.06891]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.50051,-0.11242,0.06499],"force_p95":6.82725,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.8776,"mean_force":5.29991,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.48917,-0.11249,0.0689]},{"body_a":"peg","body_b":"channel_base_body","contact_count":554.0,"contact_point_centroid":[0.50556,0.10464,0.00937],"force_p95":0.57694,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56671,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50921,0.15362,0.21874]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49984,0.1981,0.29667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.506,0.10471,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57624,"mean_force":0.54636,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51461,0.10941,0.13802]},{"body_a":"peg","body_b":"channel_base_body","contact_count":685.0,"contact_point_centroid":[0.50581,0.10458,0.00939],"force_p95":0.57568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57572,"mean_force":0.54631,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50717,0.10636,0.17021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":913.0,"contact_point_centroid":[0.50592,0.10467,0.00939],"force_p95":0.57561,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57566,"mean_force":0.54636,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50072,0.01052,0.13958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50586,0.10461,0.00939],"force_p95":0.57552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57558,"mean_force":0.54634,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49587,-0.09838,0.07644]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50616,0.10445,0.00939],"force_p95":0.57548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57549,"mean_force":0.54625,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49107,-0.11284,0.07131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50586,0.10463,0.00939],"force_p95":0.57542,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57547,"mean_force":0.54633,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48622,-0.11193,0.14437]}],"total_contact_groups":10},"final_pose_error":0.04242,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,0.10452,0.03384],"final_tcp_position":[0.4866,-0.11199,0.22172],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":77.04357,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.10472,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.52851,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":586.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51952,0.11066,0.14594],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50584,0.10459,0.03384],"object_pos_start":[0.50594,0.10472,0.03383],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.53561,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":550.0,"raw_peak_contact_force":0.57624,"tcp_end":[0.51392,0.10927,0.13693],"tcp_start":[0.51392,0.10927,0.13693],"tcp_to_object_dist_end":0.10352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":685.0,"n_steps_budget":810.0,"object_pos_end":[0.50592,0.10471,0.03383],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":0.52971,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":685.0,"raw_peak_contact_force":0.57572,"subtask_id":"lift_peg","tcp_end":[0.50372,0.10431,0.20411],"tcp_start":[0.51392,0.10927,0.13693],"tcp_to_object_dist_end":0.17029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":913.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.10462,0.03384],"object_pos_start":[0.50592,0.10471,0.03383],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":0.54104,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":913.0,"raw_peak_contact_force":0.57566,"subtask_id":"align_channel","tcp_end":[0.50011,-0.08073,0.08065],"tcp_start":[0.50372,0.10431,0.20411],"tcp_to_object_dist_end":0.19126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.10465,0.03384],"object_pos_start":[0.50598,0.10462,0.03384],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.18482,"object_z_max":0.03384,"peak_contact_force":0.54951,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.57558,"subtask_id":"insert_channel","tcp_end":[0.49519,-0.11354,0.07656],"tcp_start":[0.50011,-0.08073,0.08065],"tcp_to_object_dist_end":0.22259,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50584,0.10454,0.03384],"object_pos_start":[0.50596,0.10465,0.03384],"object_to_goal_dist_end":0.18474,"object_to_goal_dist_start":0.18485,"object_z_max":0.03384,"peak_contact_force":6.8776,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":222.0,"raw_peak_contact_force":6.8776,"tcp_end":[0.48917,-0.11249,0.0689],"tcp_start":[0.49519,-0.11354,0.07656],"tcp_to_object_dist_end":0.22048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10452,0.03384],"object_pos_start":[0.50584,0.10454,0.03384],"object_to_goal_dist_end":0.18472,"object_to_goal_dist_start":0.18474,"object_z_max":0.03384,"peak_contact_force":0.54426,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1003.0,"raw_peak_contact_force":77.04357,"tcp_end":[0.4866,-0.11199,0.22172],"tcp_start":[0.48917,-0.11249,0.0689],"tcp_to_object_dist_end":0.28731,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41892,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_x":0.00433,"align_1.align_offset_y":-0.00726,"align_1.align_speed":0.06661,"approach_1.approach_speed":0.07672,"grasp_1.grasp_duration":1.0649,"insert_1.insertion_depth":0.09251,"insert_1.insertion_force":11.28123,"insert_1.insertion_speed":0.03819,"lift_1.lift_speed":0.07618,"release_1.release_duration":0.8402,"retract_1.retract_height":0.14015,"retract_1.retract_speed":0.04943},"optimized_scores":{"best_composite_score":-0.39408,"best_fitness_score":0.35592,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":653.0,"contact_point_centroid":[0.50309,0.06745,0.00935],"force_p95":0.55495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55982,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49901,0.13648,0.21959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50304,0.06743,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55083,"mean_force":0.54665,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49483,0.07434,0.1379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":558.0,"contact_point_centroid":[0.50305,0.06745,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55066,"mean_force":0.54665,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49573,0.07052,0.17001]},{"body_a":"peg","body_b":"channel_base_body","contact_count":763.0,"contact_point_centroid":[0.50307,0.0675,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55059,"mean_force":0.54665,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49891,-0.00586,0.14065]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50305,0.06744,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55056,"mean_force":0.54665,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49597,-0.11121,0.07784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.5029,0.06737,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54664,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49091,-0.14156,0.07276]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50303,0.06747,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54665,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48573,-0.14034,0.11801]}],"total_contact_groups":7},"final_pose_error":0.0439,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50302,0.0675,0.0338],"final_tcp_position":[0.48595,-0.14038,0.16654],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":2.06903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54812,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":653.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.49972,0.07532,0.14514],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.5467,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":550.0,"raw_peak_contact_force":0.55083,"tcp_end":[0.49415,0.07424,0.13689],"tcp_start":[0.49415,0.07424,0.13689],"tcp_to_object_dist_end":0.1037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":558.0,"n_steps_budget":660.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54682,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":558.0,"raw_peak_contact_force":0.55066,"subtask_id":"lift_peg","tcp_end":[0.49971,0.0675,0.20394],"tcp_start":[0.49415,0.07424,0.13689],"tcp_to_object_dist_end":0.17018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":763.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.06742,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.5478,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":0.55059,"subtask_id":"align_channel","tcp_end":[0.50041,-0.07836,0.08187],"tcp_start":[0.49971,0.0675,0.20394],"tcp_to_object_dist_end":0.15353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06743,0.0338],"object_pos_start":[0.50304,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54737,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55056,"subtask_id":"insert_channel","tcp_end":[0.49504,-0.14242,0.07817],"tcp_start":[0.50041,-0.07836,0.08187],"tcp_to_object_dist_end":0.21464,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.503,0.06748,0.0338],"object_pos_start":[0.50301,0.06743,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54522,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.55055,"tcp_end":[0.48894,-0.14109,0.07018],"tcp_start":[0.49504,-0.14242,0.07817],"tcp_to_object_dist_end":0.21219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.0675,0.0338],"object_pos_start":[0.503,0.06748,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54563,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55055,"tcp_end":[0.48595,-0.14038,0.16654],"tcp_start":[0.48894,-0.14109,0.07018],"tcp_to_object_dist_end":0.24724,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```