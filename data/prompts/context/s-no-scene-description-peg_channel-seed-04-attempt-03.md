## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3041 | 0.61 | ✅ accepted |
| 2 | approach → contact → grasp → insert → retract | linear_cartesian | linear_cartesian | — | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | force_exceeded | pose_tolerance | 9 | 0.0641 | 0.01 | ❌ rejected |
| 1 | approach → contact → grasp → insert → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | force_exceeded | pose_tolerance | 8 | 0.2346 | 0.18 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3038 | 0.61 | ✅ accepted |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.304) — your mutation base

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

- **Composite score**: 0.304
- **task_score** (E): 0.606
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1839 |
| align_1 | 1.00 | 1.00 | 0.1182 |
| release_1 | 1.00 | 1.00 | 0.1725 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.089, 0.154) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.544 | 3.242 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.089, 0.154)→(0.501, 0.121, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.082, 0.035) | 0.165→0.162 | 1.00 / 1.333 | 0.729 | 60.875 |
| release_1 | release | 1.00 / step_budget | (0.501, 0.121, 0.042)→(0.498, -0.052, 0.037) | (0.505, 0.082, 0.035)→(0.506, -0.081, 0.036) | 0.162→0.010 | 1.00 / 3.333 | 85.735 | 99.450 |
| insert_1 | insert | 1.00 / force_exceeded | (0.498, -0.052, 0.037)→(0.498, -0.052, 0.037) | (0.506, -0.081, 0.036)→(0.506, -0.081, 0.036) | 0.010→0.010 | 1.00 / 3.000 | 92.011 | 92.144 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.972
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.972
- phase_score: 0.186
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.894
- phase_breakdown.push_score: 0.011

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.500
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.972
- **Median Q (composite search score)**: 0.275
- **K-run variance**: 0.0164
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.374


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88679,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00666,"align_1.lateral_offset_y":0.0028,"insert_1.insertion_depth":0.09058,"insert_1.insertion_force":9.21441,"push_1.push_distance":0.08528,"push_1.push_speed":0.09813},"optimized_scores":{"best_composite_score":0.16399,"best_fitness_score":0.19066,"best_task_score":0.30946},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":543.0,"contact_point_centroid":[0.54257,-0.00298,0.05999],"force_p95":73.99782,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.56996,"mean_force":57.1468,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4978,-0.00228,0.03684]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54272,-0.04858,0.05998],"force_p95":78.82298,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.82298,"mean_force":78.82298,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.05262,0.03664]},{"body_a":"attachment","body_b":"peg","contact_count":872.0,"contact_point_centroid":[0.50367,0.00037,0.04421],"force_p95":17.11795,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.61898,"mean_force":6.04755,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49777,0.012,0.03687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":642.0,"contact_point_centroid":[0.50593,-0.01587,0.00984],"force_p95":17.05196,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.33417,"mean_force":6.54428,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49782,0.02789,0.03704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":163.0,"contact_point_centroid":[0.50704,-0.10024,0.06036],"force_p95":13.7224,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.42488,"mean_force":7.94487,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.498,-0.05251,0.03665]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":447.0,"contact_point_centroid":[0.52505,-0.02886,0.03081],"force_p95":5.28424,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.7206,"mean_force":1.12934,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49781,-0.00093,0.03682]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50699,-0.10019,0.05045],"force_p95":4.89464,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.89464,"mean_force":4.89464,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.05262,0.03664]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5072,-0.06456,0.05611],"force_p95":4.79638,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.79638,"mean_force":4.79638,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49808,-0.05262,0.03664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49737,0.13923,0.21909]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49933,0.19811,0.29721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":379.0,"contact_point_centroid":[0.50607,0.08075,0.00938],"force_p95":0.55863,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.51892,"mean_force":0.55219,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49772,0.09949,0.0943]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50265,0.09854,0.05878],"force_p95":2.31232,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.31232,"mean_force":2.31232,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49967,0.11009,0.06001]}],"total_contact_groups":12},"final_pose_error":0.02766,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,-0.08238,0.03614],"final_tcp_position":[0.49808,-0.05262,0.03664],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":83.56996,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.49671,0.08414,0.1487],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11534,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":780.0,"object_pos_end":[0.50599,0.08086,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03379,"peak_contact_force":0.54627,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":380.0,"raw_peak_contact_force":2.51892,"tcp_end":[0.50101,0.11612,0.04086],"tcp_start":[0.49671,0.08414,0.1487],"tcp_to_object_dist_end":0.03631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,-0.08238,0.03614],"object_pos_start":[0.50599,0.08086,0.03378],"object_to_goal_dist_end":0.00833,"object_to_goal_dist_start":0.1611,"object_z_max":0.03762,"peak_contact_force":70.68877,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2667.0,"raw_peak_contact_force":83.56996,"tcp_end":[0.49808,-0.05262,0.03664],"tcp_start":[0.50101,0.11612,0.04086],"tcp_to_object_dist_end":0.03107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,-0.08238,0.03614],"object_pos_start":[0.50699,-0.08238,0.03614],"object_to_goal_dist_end":0.00833,"object_to_goal_dist_start":0.00833,"object_z_max":0.03614,"peak_contact_force":78.82298,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":78.82298,"tcp_end":[0.49808,-0.05262,0.03664],"tcp_start":[0.49808,-0.05262,0.03664],"tcp_to_object_dist_end":0.03107,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88889,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00282,"align_1.lateral_offset_y":0.00851,"insert_1.insertion_depth":0.08439,"insert_1.insertion_force":6.35599,"push_1.push_distance":0.06454,"push_1.push_speed":0.09983},"optimized_scores":{"best_composite_score":0.27506,"best_fitness_score":0.30173,"best_task_score":0.5373},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":93.0,"contact_point_centroid":[0.51156,0.12696,0.055],"force_p95":151.75825,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":179.55517,"mean_force":107.05664,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50284,0.13291,0.05668]},{"body_a":"peg","body_b":"channel_base_body","contact_count":362.0,"contact_point_centroid":[0.50732,0.10797,0.00915],"force_p95":144.86059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":166.31378,"mean_force":27.81974,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4988,0.11759,0.08151]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":328.0,"contact_point_centroid":[0.54284,-0.02071,0.05998],"force_p95":80.48494,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.31675,"mean_force":59.16879,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49814,-0.02063,0.03682]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54265,-0.03884,0.05998],"force_p95":78.79199,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.79199,"mean_force":78.79199,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49802,-0.04337,0.03671]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":91.0,"contact_point_centroid":[0.5252,0.10867,0.04413],"force_p95":30.00925,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.79644,"mean_force":10.02477,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50399,0.13543,0.05411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":723.0,"contact_point_centroid":[0.50629,-0.0199,0.0099],"force_p95":12.78777,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.392,"mean_force":4.83958,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49884,0.02509,0.03722]},{"body_a":"attachment","body_b":"peg","contact_count":906.0,"contact_point_centroid":[0.50366,0.01539,0.04217],"force_p95":12.05609,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.1309,"mean_force":3.596,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4987,0.02706,0.03704]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":403.0,"contact_point_centroid":[0.52504,0.01469,0.01972],"force_p95":3.19186,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.34006,"mean_force":0.75586,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49892,0.04279,0.03718]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4973,0.1454,0.20799]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4994,0.19849,0.29746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50688,-0.08769,0.00999],"force_p95":0.60318,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60318,"mean_force":0.60318,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49802,-0.04337,0.03671]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50343,-0.0551,0.04189],"force_p95":0.28987,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28987,"mean_force":0.28987,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49802,-0.04337,0.03671]}],"total_contact_groups":12},"final_pose_error":0.03683,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50698,-0.07231,0.03667],"final_tcp_position":[0.49802,-0.04337,0.03671],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":179.55517,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49656,0.09539,0.12631],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09341,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":362.0,"n_steps_budget":690.0,"object_pos_end":[0.50715,0.09774,0.03629],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.17792,"object_to_goal_dist_start":0.18484,"object_z_max":0.0361,"peak_contact_force":1.09505,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":546.0,"raw_peak_contact_force":179.55517,"tcp_end":[0.50439,0.14096,0.04272],"tcp_start":[0.49656,0.09539,0.12631],"tcp_to_object_dist_end":0.04378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,-0.07231,0.03667],"object_pos_start":[0.50715,0.09774,0.03629],"object_to_goal_dist_end":0.0109,"object_to_goal_dist_start":0.17792,"object_z_max":0.03849,"peak_contact_force":73.90571,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2360.0,"raw_peak_contact_force":81.31675,"tcp_end":[0.49802,-0.04337,0.03671],"tcp_start":[0.50439,0.14096,0.04272],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50698,-0.07231,0.03667],"object_pos_start":[0.50697,-0.07231,0.03667],"object_to_goal_dist_end":0.01091,"object_to_goal_dist_start":0.0109,"object_z_max":0.03667,"peak_contact_force":78.79199,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":78.79199,"tcp_end":[0.49802,-0.04337,0.03671],"tcp_start":[0.49802,-0.04337,0.03671],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6746,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00196,"align_1.lateral_offset_y":-0.00251,"insert_1.insertion_depth":0.08692,"insert_1.insertion_force":15.39394,"push_1.push_distance":0.13575,"push_1.push_speed":0.0622},"optimized_scores":{"best_composite_score":0.47339,"best_fitness_score":0.50006,"best_task_score":0.97167},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":481.0,"contact_point_centroid":[0.54218,-0.02815,0.05999],"force_p95":118.90565,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.46459,"mean_force":70.13423,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49745,-0.02834,0.03682]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54367,-0.05535,0.05998],"force_p95":118.79758,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.81762,"mean_force":118.61728,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49908,-0.05896,0.03647]},{"body_a":"attachment","body_b":"peg","contact_count":878.0,"contact_point_centroid":[0.50296,-0.01484,0.04437],"force_p95":82.53324,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.692,"mean_force":22.31736,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49677,-0.00349,0.03701]},{"body_a":"peg","body_b":"channel_base_body","contact_count":262.0,"contact_point_centroid":[0.50557,-0.10231,0.05482],"force_p95":84.6284,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.72722,"mean_force":61.56138,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49855,-0.05782,0.03656]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.5049,-0.07057,0.04902],"force_p95":73.69005,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.87176,"mean_force":72.05467,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49908,-0.05896,0.03647]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50478,-0.10306,0.06002],"force_p95":73.55754,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.7398,"mean_force":71.91719,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49908,-0.05896,0.03647]},{"body_a":"peg","body_b":"channel_base_body","contact_count":680.0,"contact_point_centroid":[0.50624,-0.03442,0.00983],"force_p95":16.05027,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.79758,"mean_force":5.59859,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49668,0.00744,0.03726]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":337.0,"contact_point_centroid":[0.52508,-0.00365,0.02384],"force_p95":6.17217,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.08229,"mean_force":1.85393,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49598,0.02269,0.03717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49752,0.14204,0.24001]},{"body_a":"peg","body_b":"channel_base_body","contact_count":471.0,"contact_point_centroid":[0.50305,0.06736,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49674,0.09625,0.1148]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51412,-0.10314,0.00999],"force_p95":0.12546,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12546,"mean_force":0.12546,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49908,-0.05897,0.03647]}],"total_contact_groups":11},"final_pose_error":0.02136,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50474,-0.08801,0.0351],"final_tcp_position":[0.49908,-0.05896,0.03647],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":133.46459,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.497,0.08837,0.18774],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15548,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":471.0,"n_steps_budget":990.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.5468,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":471.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.4986,0.10496,0.04226],"tcp_start":[0.497,0.08837,0.18774],"tcp_to_object_dist_end":0.0387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.50469,-0.08803,0.03509],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.01051,"object_to_goal_dist_start":0.14761,"object_z_max":0.0383,"peak_contact_force":112.60953,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2638.0,"raw_peak_contact_force":133.46459,"tcp_end":[0.49908,-0.05897,0.03647],"tcp_start":[0.4986,0.10496,0.04226],"tcp_to_object_dist_end":0.02963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.50474,-0.08801,0.0351],"object_pos_start":[0.50469,-0.08803,0.03509],"object_to_goal_dist_end":0.01052,"object_to_goal_dist_start":0.01051,"object_z_max":0.03509,"peak_contact_force":118.41693,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":7.0,"raw_peak_contact_force":118.81762,"tcp_end":[0.49908,-0.05896,0.03647],"tcp_start":[0.49908,-0.05897,0.03647],"tcp_to_object_dist_end":0.02963,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```