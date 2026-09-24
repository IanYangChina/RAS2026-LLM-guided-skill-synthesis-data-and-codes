## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7  | 0.0131 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6  | -0.1168 | 0.09 | ✅ accepted |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3  | -0.2944 | 0.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.294) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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

```

## Design Metrics

- **Composite score**: -0.294
- **task_score** (E): 0.000
- **fitness_score**: 0.116  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2206 |
| descend_1 | 0.00 | 1.00 | 0.0370 |
| push_1 | 0.00 | 1.00 | 0.0011 |
| retract_1 | 0.33 | 1.00 | 0.1635 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.098, 0.107) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.543 | 3.954 |
| descend_1 | descend | 0.00 / step_budget | (0.505, 0.098, 0.107)→(0.501, 0.092, 0.076) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.558 | 0.560 |
| push_1 | push | 0.00 / guard_failure | (0.516, 0.076, 0.058)→(0.517, 0.076, 0.057) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.667 | 981.930 | 1114.107 |
| retract_1 | retract | 0.33 / step_budget | (0.517, 0.076, 0.057)→(0.514, 0.092, 0.220) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.547 | 427.663 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.210
- phase_breakdown.push_through_channel_score: 0.001
- phase_breakdown.contact_peg_score: 0.699

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.126
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.295
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.268


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92391,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.41396,"descend_1.descend_force_threshold":29.96012,"descend_1.descend_speed":0.06836,"push_1.push_distance":0.18524,"push_1.push_speed":0.04427,"push_1.push_tolerance":0.02414,"retract_1.retract_height":0.09291},"optimized_scores":{"best_composite_score":-0.29522,"best_fitness_score":0.11478,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.4921,0.06093,0.00938],"force_p95":363.85974,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":393.16796,"mean_force":59.15826,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49554,0.06088,0.06695]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51122,0.0601,0.05775],"force_p95":388.70454,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":392.48036,"mean_force":331.99625,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50181,0.05305,0.05914]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.49409,0.06066,0.00936],"force_p95":12.82929,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":282.96439,"mean_force":4.30311,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50098,0.06567,0.13226]},{"body_a":"attachment","body_b":"peg","contact_count":74.0,"contact_point_centroid":[0.51298,0.06449,0.05651],"force_p95":240.40606,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":282.81386,"mean_force":50.78036,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50516,0.05828,0.05662]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":136.0,"contact_point_centroid":[0.47489,0.05978,0.03906],"force_p95":9.15493,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.00921,"mean_force":2.30946,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50274,0.06161,0.11167]},{"body_a":"peg","body_b":"channel_base_body","contact_count":523.0,"contact_point_centroid":[0.49431,0.05892,0.00935],"force_p95":0.56951,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57418,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48192,0.13658,0.20002]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49883,0.19725,0.29554]},{"body_a":"peg","body_b":"channel_base_body","contact_count":503.0,"contact_point_centroid":[0.49423,0.05889,0.00939],"force_p95":0.55014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54599,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47632,0.07265,0.08835]}],"total_contact_groups":8},"final_pose_error":0.03525,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49327,0.0599,0.03384],"final_tcp_position":[0.501,0.06127,0.21547],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":393.16796,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":552.0,"n_steps_budget":600.0,"object_pos_end":[0.4942,0.05886,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54222,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":558.0,"raw_peak_contact_force":4.20518,"subtask_id":"contact_peg","tcp_end":[0.46609,0.07701,0.10891],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":503.0,"n_steps_budget":600.0,"object_pos_end":[0.49431,0.05903,0.03393],"object_pos_start":[0.4942,0.05886,0.03387],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.13912,"object_z_max":0.03393,"peak_contact_force":0.54932,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":503.0,"raw_peak_contact_force":0.55382,"subtask_id":"contact_peg","tcp_end":[0.48833,0.06901,0.0722],"tcp_start":[0.46609,0.07701,0.10891],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.05875,0.03384],"object_pos_start":[0.49431,0.05903,0.03393],"object_to_goal_dist_end":0.13901,"object_to_goal_dist_start":0.13928,"object_z_max":0.03394,"peak_contact_force":393.16796,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":20.0,"raw_peak_contact_force":393.16796,"subtask_id":"push_through_channel","tcp_end":[0.50367,0.0519,0.05644],"tcp_start":[0.50261,0.0524,0.0577],"tcp_to_object_dist_end":0.02542,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49327,0.0599,0.03384],"object_pos_start":[0.49508,0.0586,0.03389],"object_to_goal_dist_end":0.1402,"object_to_goal_dist_start":0.13882,"object_z_max":0.03565,"peak_contact_force":0.54909,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1209.0,"raw_peak_contact_force":282.96439,"tcp_end":[0.501,0.06127,0.21547],"tcp_start":[0.50367,0.0519,0.05644],"tcp_to_object_dist_end":0.1818,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04167,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15195,"descend_1.descend_force_threshold":24.86111,"descend_1.descend_speed":0.08208,"push_1.push_distance":0.1514,"push_1.push_speed":0.14502,"push_1.push_tolerance":0.02064,"retract_1.retract_height":0.13266},"optimized_scores":{"best_composite_score":-0.30402,"best_fitness_score":0.10598,"best_task_score":0.00018},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.53188,0.0825,0.05852],"force_p95":1454.25173,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1464.23816,"mean_force":1366.16401,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52269,0.07522,0.05957]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.5315,0.08444,0.05846],"force_p95":382.80293,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":502.30076,"mean_force":148.36138,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52374,0.07586,0.06006]},{"body_a":"peg","body_b":"channel_base_body","contact_count":642.0,"contact_point_centroid":[0.50572,0.08089,0.00936],"force_p95":0.55571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57054,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51475,0.14608,0.19778]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5001,0.19779,0.29576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50561,0.08095,0.0094],"force_p95":0.55283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.23949,"mean_force":0.55383,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52032,0.09157,0.13862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.50561,0.08,0.00938],"force_p95":1.2796,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86981,"mean_force":0.65145,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51656,0.08284,0.07016]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.52224,0.08721,0.05822],"force_p95":1.47825,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.78465,"mean_force":0.46827,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52375,0.07543,0.0591]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.52273,0.08696,0.05805],"force_p95":1.26691,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.29736,"mean_force":0.9929,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52285,0.07503,0.05892]},{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.50618,0.08076,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51973,0.09402,0.09187]}],"total_contact_groups":9},"final_pose_error":0.07019,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50589,0.08081,0.03382],"final_tcp_position":[0.52063,0.0924,0.22246],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":1464.23816,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":671.0,"n_steps_budget":960.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55006,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":678.0,"raw_peak_contact_force":4.32595,"subtask_id":"contact_peg","tcp_end":[0.53002,0.09642,0.10603],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":153.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":153.0,"raw_peak_contact_force":0.55007,"subtask_id":"contact_peg","tcp_end":[0.50903,0.09174,0.07764],"tcp_start":[0.53002,0.09642,0.10603],"tcp_to_object_dist_end":0.0453,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":19.0,"n_steps_budget":660.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.03379,"peak_contact_force":1269.88002,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":24.0,"raw_peak_contact_force":1464.23816,"subtask_id":"push_through_channel","tcp_end":[0.52324,0.07478,0.05769],"tcp_start":[0.52299,0.07491,0.0584],"tcp_to_object_dist_end":0.03012,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.08081,0.03382],"object_pos_start":[0.50595,0.08084,0.03381],"object_to_goal_dist_end":0.16104,"object_to_goal_dist_start":0.16107,"object_z_max":0.03462,"peak_contact_force":0.5479,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1053.0,"raw_peak_contact_force":502.30076,"tcp_end":[0.52063,0.0924,0.22246],"tcp_start":[0.52324,0.07478,0.05769],"tcp_to_object_dist_end":0.18957,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85714,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13865,"descend_1.descend_force_threshold":15.54167,"descend_1.descend_speed":0.03876,"push_1.push_distance":0.12696,"push_1.push_speed":0.12312,"push_1.push_tolerance":0.01894,"retract_1.retract_height":0.15468},"optimized_scores":{"best_composite_score":-0.28396,"best_fitness_score":0.12604,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.53104,0.108,0.05882],"force_p95":1474.22484,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1484.9138,"mean_force":1381.89355,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52193,0.10059,0.06009]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.53051,0.10994,0.05867],"force_p95":371.00995,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":497.72351,"mean_force":104.17246,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52286,0.10122,0.0604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":610.0,"contact_point_centroid":[0.50568,0.1047,0.00937],"force_p95":0.57611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56487,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50929,0.15806,0.199]},{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.50983,0.10359,0.00939],"force_p95":1.22683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.60415,"mean_force":0.68153,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51491,0.10725,0.07095]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49991,0.19841,0.29643]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.52206,0.11233,0.05833],"force_p95":1.91548,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.98864,"mean_force":1.25705,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52214,0.10041,0.05941]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50554,0.10456,0.0094],"force_p95":0.57223,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5353,"mean_force":0.55113,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51968,0.1181,0.13779]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.52148,0.11263,0.05834],"force_p95":0.45761,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.05827,"mean_force":0.33352,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52303,0.10085,0.05938]},{"body_a":"peg","body_b":"channel_base_body","contact_count":140.0,"contact_point_centroid":[0.50557,0.10449,0.00939],"force_p95":0.57565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57608,"mean_force":0.54642,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51289,0.11706,0.09318]}],"total_contact_groups":9},"final_pose_error":0.09337,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50586,0.10465,0.0338],"final_tcp_position":[0.52002,0.12201,0.22207],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1484.9138,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":637.0,"n_steps_budget":990.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53584,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":642.0,"raw_peak_contact_force":3.33087,"subtask_id":"contact_peg","tcp_end":[0.51954,0.11918,0.10731],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":140.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.10471,0.03384],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":0.57566,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":140.0,"raw_peak_contact_force":0.57608,"subtask_id":"contact_peg","tcp_end":[0.50652,0.11514,0.07872],"tcp_start":[0.51954,0.11918,0.10731],"tcp_to_object_dist_end":0.04609,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":19.0,"n_steps_budget":660.0,"object_pos_end":[0.50595,0.10457,0.03384],"object_pos_start":[0.50597,0.10471,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18491,"object_z_max":0.03385,"peak_contact_force":1282.74268,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":24.0,"raw_peak_contact_force":1484.9138,"subtask_id":"push_through_channel","tcp_end":[0.52261,0.10019,0.05814],"tcp_start":[0.52231,0.1003,0.05888],"tcp_to_object_dist_end":0.02978,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.10465,0.0338],"object_pos_start":[0.50591,0.10452,0.03387],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.18472,"object_z_max":0.03457,"peak_contact_force":0.54288,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1060.0,"raw_peak_contact_force":497.72351,"tcp_end":[0.52002,0.12201,0.22207],"tcp_start":[0.52261,0.10019,0.05814],"tcp_to_object_dist_end":0.1896,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```