## Search State

- **Seed**: 6
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0828 | 0.00 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.083) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
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
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: -0.083
- **task_score** (E): 0.000
- **fitness_score**: 0.317  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2592 |
| lift_1 | 0.00 | 1.00 | 0.1708 |
| push_1 | 1.00 | 1.00 | 0.1866 |
| approach_1 | 0.33 | 1.00 | 0.1654 |
| approach_2 | 0.67 | 1.00 | 0.0446 |
| descend_1 | 0.67 | 0.67 | 0.0778 |
| grasp_1 | 1.00 | 0.67 | 0.0060 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.142, 0.049) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.547 | 2.127 |
| lift_1 | lift | 0.00 / step_budget | (0.496, 0.142, 0.049)→(0.430, 0.046, 0.174) | (0.501, 0.100, 0.034)→(0.503, 0.113, 0.027) | 0.180→0.194 | 1.00 / 1.000 | 0.598 | 1.939 |
| push_1 | push | 1.00 / step_budget | (0.430, 0.046, 0.174)→(0.494, -0.067, 0.042) | (0.503, 0.113, 0.027)→(0.517, 0.114, 0.027) | 0.194→0.196 | 1.00 / 1.333 | 0.843 | 119.122 |
| approach_1 | approach | 0.33 / step_budget | (0.494, -0.067, 0.042)→(0.499, 0.098, 0.041) | (0.517, 0.114, 0.027)→(0.551, 0.136, 0.028) | 0.196→0.230 | 1.00 / 1.667 | 154.417 | 249.909 |
| approach_2 | approach | 0.67 / step_budget | (0.499, 0.098, 0.041)→(0.501, 0.141, 0.039) | (0.551, 0.136, 0.028)→(0.587, 0.159, 0.014) | 0.230→0.276 | 1.00 / 2.333 | 96.199 | 175.806 |
| descend_1 | descend | 0.67 / step_budget | (0.501, 0.141, 0.039)→(0.561, 0.179, 0.023) | (0.587, 0.159, 0.014)→(0.668, 0.163, -2.221) | 0.276→2.417 | 0.67 / 1.333 | 165.567 | 320.317 |
| grasp_1 | grasp | 1.00 / step_budget | (0.561, 0.179, 0.023)→(0.559, 0.179, 0.018) | (0.668, 0.163, -2.221)→(0.718, 0.160, -6.986) | 2.417→7.178 | 0.67 / 1.333 | 37.677 | 49.899 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.680
- phase_breakdown.push_score: 0.868
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.798

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.408
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.044
- **K-run variance**: 0.0089
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.449


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.704,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00254,"approach_2.speed":0.03946,"lift_1.lift_height":0.1973,"push_1.push_distance":0.17028,"push_1.push_speed":0.07135},"optimized_scores":{"best_composite_score":-0.04396,"best_fitness_score":0.35604,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":431.0,"contact_point_centroid":[0.55498,0.11999,0.05992],"force_p95":262.92458,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.1442,"mean_force":216.87262,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50873,0.16407,0.03031]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.54383,0.08879,0.05993],"force_p95":281.77749,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.40853,"mean_force":127.6257,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49906,0.08845,0.03635]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":101.0,"contact_point_centroid":[0.50261,-0.10005,0.065],"force_p95":159.42744,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":189.87508,"mean_force":119.95969,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49328,-0.08785,0.04543]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.54837,0.10495,0.05999],"force_p95":125.44918,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.61551,"mean_force":63.42301,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50032,0.1171,0.03527]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":449.0,"contact_point_centroid":[0.55499,0.12,0.05998],"force_p95":72.8891,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.18833,"mean_force":63.08852,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51348,0.17866,0.02659]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50875,-0.10001,0.065],"force_p95":59.07052,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.22573,"mean_force":48.67363,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49758,-0.08775,0.04103]},{"body_a":"attachment","body_b":"peg","contact_count":242.0,"contact_point_centroid":[0.50161,0.07248,0.0432],"force_p95":23.71287,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.33784,"mean_force":14.19171,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49827,0.06127,0.04448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50375,0.0769,0.0095],"force_p95":18.10197,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.01694,"mean_force":3.9581,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49633,-0.00066,0.04711]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52511,0.10616,0.02811],"force_p95":14.4236,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.50161,"mean_force":5.12865,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49894,0.08013,0.03923]},{"body_a":"peg","body_b":"world","contact_count":380.0,"contact_point_centroid":[0.50553,0.15143,-0.00198],"force_p95":0.89244,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.50591,"mean_force":0.71899,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49916,0.12526,0.03642]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50684,0.11923,0.03316],"force_p95":9.91892,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.99722,"mean_force":3.24401,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49976,0.11325,0.03632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55733,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49866,0.1548,0.17095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":81.0,"contact_point_centroid":[0.50575,0.11985,0.00971],"force_p95":0.81254,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51062,"mean_force":0.49298,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49906,0.09373,0.03641]},{"body_a":"peg","body_b":"world","contact_count":455.0,"contact_point_centroid":[0.47466,0.15472,-0.00198],"force_p95":0.72589,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72602,"mean_force":0.60577,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50872,0.164,0.03034]},{"body_a":"peg","body_b":"world","contact_count":450.0,"contact_point_centroid":[0.44269,0.15548,-0.00199],"force_p95":0.72586,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72586,"mean_force":0.60636,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51348,0.17866,0.02659]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50306,0.06744,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54665,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46261,0.06826,0.11123]}],"total_contact_groups":17},"final_pose_error":0.0261,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.43182,0.15584,0.0141],"final_tcp_position":[0.51294,0.17835,0.02675],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":327.1442,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5478,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":805.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.499,0.11132,0.04824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54731,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55077,"tcp_end":[0.43006,0.02624,0.17825],"tcp_start":[0.499,0.11132,0.04824],"tcp_to_object_dist_end":0.16699,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":909.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06743,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":1.41451,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1010.0,"raw_peak_contact_force":189.87508,"tcp_end":[0.49758,-0.08776,0.04106],"tcp_start":[0.43006,0.02624,0.17825],"tcp_to_object_dist_end":0.15545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.11962,0.03515],"object_pos_start":[0.50301,0.06743,0.0338],"object_to_goal_dist_end":0.19977,"object_to_goal_dist_start":0.14759,"object_z_max":0.03972,"peak_contact_force":0.50131,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1266.0,"raw_peak_contact_force":284.40853,"tcp_end":[0.49968,0.08935,0.03644],"tcp_start":[0.49758,-0.08776,0.04106],"tcp_to_object_dist_end":0.03094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.49628,0.15397,0.01411],"object_pos_start":[0.50594,0.11962,0.03515],"object_to_goal_dist_end":0.23542,"object_to_goal_dist_start":0.19977,"object_z_max":0.03531,"peak_contact_force":51.62679,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":137.61551,"tcp_end":[0.50272,0.15028,0.03361],"tcp_start":[0.49968,0.08935,0.03644],"tcp_to_object_dist_end":0.02087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.45602,0.15518,0.01409],"object_pos_start":[0.49628,0.15397,0.01411],"object_to_goal_dist_end":0.24065,"object_to_goal_dist_start":0.23542,"object_z_max":0.01411,"peak_contact_force":247.18946,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":886.0,"raw_peak_contact_force":327.1442,"tcp_end":[0.51294,0.17835,0.02675],"tcp_start":[0.50272,0.15028,0.03361],"tcp_to_object_dist_end":0.06275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43182,0.15584,0.0141],"object_pos_start":[0.45602,0.15518,0.01409],"object_to_goal_dist_end":0.24686,"object_to_goal_dist_start":0.24065,"object_z_max":0.0141,"peak_contact_force":56.02639,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":899.0,"raw_peak_contact_force":75.18833,"tcp_end":[0.51371,0.17875,0.0265],"tcp_start":[0.51294,0.17835,0.02675],"tcp_to_object_dist_end":0.08593,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71179,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00123,"approach_2.speed":0.04802,"lift_1.lift_height":0.25828,"push_1.push_distance":0.19998,"push_1.push_speed":0.08589},"optimized_scores":{"best_composite_score":0.00821,"best_fitness_score":0.40821,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":353.0,"contact_point_centroid":[0.55498,0.11999,0.05994],"force_p95":267.5632,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.52075,"mean_force":186.5561,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51073,0.1723,0.02837]},{"body_a":"attachment","body_b":"peg","contact_count":293.0,"contact_point_centroid":[0.51106,0.15879,0.02888],"force_p95":48.83768,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.95442,"mean_force":27.86568,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50813,0.16737,0.03]},{"body_a":"peg","body_b":"world","contact_count":406.0,"contact_point_centroid":[0.50358,0.15602,-0.00261],"force_p95":47.86379,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.91638,"mean_force":20.52905,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51025,0.17138,0.02868]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":449.0,"contact_point_centroid":[0.55499,0.12,0.05998],"force_p95":72.93186,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.50772,"mean_force":63.44538,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51823,0.18495,0.02402]},{"body_a":"peg","body_b":"world","contact_count":340.0,"contact_point_centroid":[0.50538,0.15018,-0.00201],"force_p95":25.83875,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.6375,"mean_force":3.23177,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49689,0.12846,0.0419]},{"body_a":"attachment","body_b":"peg","contact_count":35.0,"contact_point_centroid":[0.51046,0.15082,0.03123],"force_p95":40.36772,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.20633,"mean_force":25.36414,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49941,0.15084,0.03576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50364,0.11216,0.00942],"force_p95":0.5962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.06842,"mean_force":0.5563,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49325,0.00546,0.05095]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50107,0.09644,0.05435],"force_p95":2.5179,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.61294,"mean_force":1.39226,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49674,0.08473,0.04985]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50352,0.11122,0.00941],"force_p95":0.60591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43975,"mean_force":0.54793,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46978,0.10378,0.10742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.49753,0.12798,0.05958],"force_p95":1.1545,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.97536,"mean_force":0.44372,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4931,0.13894,0.06131]},{"body_a":"peg","body_b":"world","contact_count":450.0,"contact_point_centroid":[0.48507,0.16784,-0.00193],"force_p95":0.64425,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64469,"mean_force":0.60649,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51823,0.18495,0.02402]},{"body_a":"peg","body_b":"channel_base_body","contact_count":848.0,"contact_point_centroid":[0.50371,0.11163,0.0094],"force_p95":0.5913,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63314,"mean_force":0.54452,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46463,-0.01391,0.10332]},{"body_a":"peg","body_b":"channel_base_body","contact_count":49.0,"contact_point_centroid":[0.50381,0.11985,0.00978],"force_p95":0.52882,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55073,"mean_force":0.42163,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49614,0.09862,0.04641]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19944,0.29874]}],"total_contact_groups":15},"final_pose_error":0.01631,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.47907,0.16488,0.01415],"final_tcp_position":[0.5177,0.18467,0.02422],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":304.52075,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11176,0.0338],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19187,"object_z_max":0.03525,"peak_contact_force":0.61004,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1017.0,"raw_peak_contact_force":2.43975,"tcp_end":[0.43774,0.05553,0.1705],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.1619,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11166,0.0338],"object_pos_start":[0.50377,0.11176,0.0338],"object_to_goal_dist_end":0.1918,"object_to_goal_dist_start":0.1919,"object_z_max":0.03399,"peak_contact_force":0.55348,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":848.0,"raw_peak_contact_force":0.63314,"tcp_end":[0.4931,-0.08125,0.04104],"tcp_start":[0.43774,0.05553,0.1705],"tcp_to_object_dist_end":0.19334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50408,0.12244,0.03537],"object_pos_start":[0.5037,0.11166,0.0338],"object_to_goal_dist_end":0.20254,"object_to_goal_dist_start":0.1918,"object_z_max":0.03547,"peak_contact_force":0.50026,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1012.0,"raw_peak_contact_force":3.06842,"tcp_end":[0.49715,0.09493,0.04762],"tcp_start":[0.4931,-0.08125,0.04104],"tcp_to_object_dist_end":0.03091,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":395.0,"n_steps_budget":900.0,"object_pos_end":[0.50827,0.1517,0.01292],"object_pos_start":[0.50408,0.12244,0.03537],"object_to_goal_dist_end":0.23342,"object_to_goal_dist_start":0.20254,"object_z_max":0.03537,"peak_contact_force":37.65749,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":46.6375,"tcp_end":[0.50016,0.15337,0.03479],"tcp_start":[0.49715,0.09493,0.04762],"tcp_to_object_dist_end":0.02338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":406.0,"n_steps_budget":600.0,"object_pos_end":[0.49126,0.17091,0.01416],"object_pos_start":[0.50827,0.1517,0.01292],"object_to_goal_dist_end":0.25239,"object_to_goal_dist_start":0.23342,"object_z_max":0.01419,"peak_contact_force":249.5111,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":304.52075,"tcp_end":[0.5177,0.18467,0.02422],"tcp_start":[0.50016,0.15337,0.03479],"tcp_to_object_dist_end":0.03145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47907,0.16488,0.01415],"object_pos_start":[0.49126,0.17091,0.01416],"object_to_goal_dist_end":0.24713,"object_to_goal_dist_start":0.25239,"object_z_max":0.01416,"peak_contact_force":57.006,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":899.0,"raw_peak_contact_force":74.50772,"tcp_end":[0.51845,0.18504,0.02393],"tcp_start":[0.5177,0.18467,0.02422],"tcp_to_object_dist_end":0.04531,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4526,"average_solve_count":327.0,"average_success_count":327.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00579,"approach_2.speed":0.03043,"lift_1.lift_height":0.17315,"push_1.push_distance":0.19746,"push_1.push_speed":0.01464},"optimized_scores":{"best_composite_score":-0.21261,"best_fitness_score":0.18739,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":78.0,"contact_point_centroid":[0.54658,0.10952,0.0599],"force_p95":344.16814,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":462.24977,"mean_force":243.64694,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50016,0.10755,0.03983]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":410.0,"contact_point_centroid":[0.52507,0.08169,0.05996],"force_p95":242.54189,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":426.63123,"mean_force":162.12881,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50382,0.08139,0.0443]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":957.0,"contact_point_centroid":[0.52504,0.11487,0.05997],"force_p95":172.08642,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":343.16368,"mean_force":110.64176,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49985,0.11387,0.04466]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":328.0,"contact_point_centroid":[0.55499,0.12,0.05995],"force_p95":270.76078,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":329.28585,"mean_force":207.33019,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5017,0.12216,0.05241]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":940.0,"contact_point_centroid":[0.54894,0.11642,0.05996],"force_p95":194.81493,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.07295,"mean_force":142.52736,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49985,0.11392,0.04468]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":77.0,"contact_point_centroid":[0.52504,0.11997,0.05996],"force_p95":250.1923,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.70521,"mean_force":153.82739,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50367,0.1242,0.05363]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47498,-0.02634,0.05997],"force_p95":165.41791,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":166.85771,"mean_force":127.16238,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48526,-0.02348,0.0547]},{"body_a":"peg","body_b":"world","contact_count":601.0,"contact_point_centroid":[0.49712,0.15864,-0.00186],"force_p95":0.72597,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.8278,"mean_force":0.61334,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4405,0.08822,0.1344]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.49619,0.11915,0.0094],"force_p95":0.61089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55292,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49061,0.17919,0.17037]},{"body_a":"peg","body_b":"world","contact_count":428.0,"contact_point_centroid":[0.78093,0.17198,-0.00186],"force_p95":0.72585,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87928,"mean_force":0.5825,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50695,0.12472,0.05056]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.19927,0.29748]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.58986,0.16436,-0.00199],"force_p95":0.72595,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72611,"mean_force":0.60602,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50079,0.04548,0.04522]},{"body_a":"peg","body_b":"world","contact_count":821.0,"contact_point_centroid":[0.52089,0.1614,-0.00199],"force_p95":0.72591,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72593,"mean_force":0.60597,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45665,0.0123,0.10643]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.69995,0.16869,-0.00199],"force_p95":0.72587,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72587,"mean_force":0.60602,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49985,0.11391,0.04471]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49585,0.11953,0.00942],"force_p95":0.60298,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62344,"mean_force":0.52859,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46838,0.13841,0.07114]}],"total_contact_groups":15},"final_pose_error":0.10905,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[1.24429,0.15803,-20.98585],"final_tcp_position":[0.65359,0.17509,0.01861],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":462.24977,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11947,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1996,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52313,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48315,0.16005,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50294,0.16045,0.01409],"object_pos_start":[0.49601,0.11947,0.03385],"object_to_goal_dist_end":0.24186,"object_to_goal_dist_start":0.1996,"object_z_max":0.03393,"peak_contact_force":0.63703,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":998.0,"raw_peak_contact_force":2.8278,"tcp_end":[0.4234,0.05711,0.17396],"tcp_start":[0.48315,0.16005,0.04931],"tcp_to_object_dist_end":0.2063,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.54483,0.1625,0.01409],"object_pos_start":[0.50294,0.16045,0.01409],"object_to_goal_dist_end":0.24796,"object_to_goal_dist_start":0.24186,"object_z_max":0.01409,"peak_contact_force":0.56225,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":828.0,"raw_peak_contact_force":166.85771,"tcp_end":[0.49194,-0.03178,0.04268],"tcp_start":[0.4234,0.05711,0.17396],"tcp_to_object_dist_end":0.20336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64319,0.16651,0.0141],"object_pos_start":[0.54483,0.1625,0.01409],"object_to_goal_dist_end":0.28625,"object_to_goal_dist_start":0.24796,"object_z_max":0.0141,"peak_contact_force":462.24977,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1488.0,"raw_peak_contact_force":462.24977,"tcp_end":[0.50026,0.11059,0.04034],"tcp_start":[0.49194,-0.03178,0.04268],"tcp_to_object_dist_end":0.1557,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.75649,0.17089,0.01409],"object_pos_start":[0.64319,0.16651,0.0141],"object_to_goal_dist_end":0.35973,"object_to_goal_dist_start":0.28625,"object_z_max":0.0141,"peak_contact_force":199.31251,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2897.0,"raw_peak_contact_force":343.16368,"tcp_end":[0.50027,0.12069,0.04825],"tcp_start":[0.50026,0.11059,0.04034],"tcp_to_object_dist_end":0.26332,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[1.05538,0.16437,-6.69109],"object_pos_start":[0.75649,0.17089,0.01409],"object_to_goal_dist_end":6.75838,"object_to_goal_dist_start":0.35973,"object_z_max":0.01504,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":833.0,"raw_peak_contact_force":329.28585,"tcp_end":[0.65359,0.17509,0.01861],"tcp_start":[0.50027,0.12069,0.04825],"tcp_to_object_dist_end":6.72172,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[1.24429,0.15803,-20.98585],"object_pos_start":[1.05538,0.16437,-6.69109],"object_to_goal_dist_end":21.04036,"object_to_goal_dist_start":6.75838,"object_z_max":-6.69109,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.6453,0.17297,0.00481],"tcp_start":[0.65359,0.17509,0.01861],"tcp_to_object_dist_end":20.99921,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```