## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6  | -0.1168 | 0.09 | ✅ accepted |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3  | 0.0131 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.013) — your mutation base

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

- **Composite score**: 0.013
- **task_score** (E): 0.001
- **fitness_score**: 0.123  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1828 |
| descend_1 | 1.00 | 1.00 | 0.0951 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.1943 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.095, 0.154) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.546 | 3.954 |
| descend_1 | descend | 1.00 / force_exceeded | (0.505, 0.095, 0.154)→(0.499, 0.085, 0.060) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 24.749 | 24.749 |
| push_1 | push | 0.00 / guard_failure | (0.499, 0.084, 0.060)→(0.499, 0.084, 0.060) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.161 | 1.00 / 2.000 | 15.883 | 40.177 |
| retract_1 | retract | 1.00 / step_budget | (0.499, 0.084, 0.060)→(0.498, -0.056, 0.193) | (0.502, 0.081, 0.034)→(0.501, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.542 | 30.102 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.003
- alignment_error: None
- force_efficiency: 0.214
- terminal_score: 0.002
- phase_score: 0.205
- phase_breakdown.push_through_channel_score: 0.002
- phase_breakdown.approach_peg_score: 0.677

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.123
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.002
- **Median Q (composite search score)**: 0.013
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04494,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.25158,"descend_1.contact_force_threshold":11.44509,"descend_1.descend_z":-0.0132,"push_1.push_distance":0.1558,"push_1.push_speed":0.20068,"retract_1.retract_height":0.1619},"optimized_scores":{"best_composite_score":0.01339,"best_fitness_score":0.12339,"best_task_score":0.00069},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.48384,0.06158,0.0093],"force_p95":41.36014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.17401,"mean_force":21.41777,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48163,0.06277,0.06018]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49346,0.06244,0.05867],"force_p95":40.80889,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.66757,"mean_force":20.89422,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48163,0.06277,0.06018]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.49342,0.05835,0.00937],"force_p95":0.67527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.4206,"mean_force":0.86205,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48607,0.00974,0.12661]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49287,0.0626,0.05875],"force_p95":25.67782,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.81745,"mean_force":11.48134,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48112,0.06099,0.06014]},{"body_a":"peg","body_b":"channel_base_body","contact_count":559.0,"contact_point_centroid":[0.49423,0.05896,0.00939],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.79845,"mean_force":0.58057,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47384,0.06833,0.10502]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49367,0.06227,0.05889],"force_p95":19.30945,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.30945,"mean_force":19.30945,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48186,0.06341,0.06063]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47486,0.05744,0.05862],"force_p95":14.32883,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.14731,"mean_force":3.52062,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48068,0.06026,0.0611]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.49451,0.05885,0.00933],"force_p95":0.61938,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48264,0.13261,0.22]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49834,0.19515,0.29389]}],"total_contact_groups":9},"final_pose_error":0.0295,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49385,0.05861,0.03385],"final_tcp_position":[0.49502,-0.05663,0.1846],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":44.17401,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":600.0,"object_pos_end":[0.49422,0.05894,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54866,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":349.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.4682,0.07372,0.15291],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":559.0,"n_steps_budget":870.0,"object_pos_end":[0.49422,0.05911,0.03391],"object_pos_start":[0.49422,0.05894,0.03385],"object_to_goal_dist_end":0.13937,"object_to_goal_dist_start":0.13919,"object_z_max":0.03391,"peak_contact_force":19.79845,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":560.0,"raw_peak_contact_force":19.79845,"tcp_end":[0.48188,0.0634,0.06051],"tcp_start":[0.4682,0.07372,0.15291],"tcp_to_object_dist_end":0.02963,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":9.0,"n_steps_budget":600.0,"object_pos_end":[0.49359,0.05854,0.03388],"object_pos_start":[0.49422,0.05911,0.03391],"object_to_goal_dist_end":0.13882,"object_to_goal_dist_start":0.13937,"object_z_max":0.03391,"peak_contact_force":23.9583,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":44.17401,"subtask_id":"push_through_channel","tcp_end":[0.48147,0.06151,0.05992],"tcp_start":[0.48147,0.0617,0.05996],"tcp_to_object_dist_end":0.02887,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.49385,0.05861,0.03385],"object_pos_start":[0.49359,0.05824,0.03387],"object_to_goal_dist_end":0.13889,"object_to_goal_dist_start":0.13852,"object_z_max":0.0342,"peak_contact_force":0.54698,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":339.0,"raw_peak_contact_force":26.4206,"tcp_end":[0.49502,-0.05663,0.1846],"tcp_start":[0.48147,0.06151,0.05992],"tcp_to_object_dist_end":0.18976,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02041,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31714,"descend_1.contact_force_threshold":10.08359,"descend_1.descend_z":-0.00969,"push_1.push_distance":0.13315,"push_1.push_speed":0.15336,"retract_1.retract_height":0.19538},"optimized_scores":{"best_composite_score":0.01252,"best_fitness_score":0.12252,"best_task_score":0.0018},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49584,0.0725,0.00932],"force_p95":36.17885,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.03302,"mean_force":26.77869,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50929,0.08411,0.05973]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.52115,0.08396,0.05841],"force_p95":35.58332,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.41466,"mean_force":26.31867,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50929,0.08411,0.05973]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.50606,0.08088,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.77999,"mean_force":0.62655,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51824,0.08914,0.10598]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52148,0.084,0.05869],"force_p95":32.26889,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.26889,"mean_force":32.26889,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50962,0.08452,0.06037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":389.0,"contact_point_centroid":[0.50465,0.0797,0.00943],"force_p95":0.62749,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.64333,"mean_force":0.87229,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50354,0.02308,0.1435]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.52018,0.08352,0.05884],"force_p95":26.77471,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.35362,"mean_force":9.97781,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50836,0.08256,0.06011]},{"body_a":"peg","body_b":"channel_base_body","contact_count":300.0,"contact_point_centroid":[0.50543,0.08092,0.00934],"force_p95":0.58131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59763,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51484,0.14347,0.22026]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50084,0.19567,0.29366]}],"total_contact_groups":8},"final_pose_error":0.02948,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50488,0.07987,0.03426],"final_tcp_position":[0.49953,-0.0567,0.21733],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":37.03302,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55013,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":336.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52881,0.09419,0.15328],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":404.0,"n_steps_budget":840.0,"object_pos_end":[0.50599,0.08086,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":32.77999,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":405.0,"raw_peak_contact_force":32.77999,"tcp_end":[0.50959,0.0845,0.06014],"tcp_start":[0.52881,0.09419,0.15328],"tcp_to_object_dist_end":0.02686,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.50559,0.08051,0.0338],"object_pos_start":[0.50599,0.08086,0.03378],"object_to_goal_dist_end":0.16072,"object_to_goal_dist_start":0.16109,"object_z_max":0.03384,"peak_contact_force":17.53944,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":37.03302,"subtask_id":"push_through_channel","tcp_end":[0.50908,0.08329,0.05941],"tcp_start":[0.5091,0.08343,0.05946],"tcp_to_object_dist_end":0.02599,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.50488,0.07987,0.03426],"object_pos_start":[0.50558,0.08025,0.03384],"object_to_goal_dist_end":0.16005,"object_to_goal_dist_start":0.16047,"object_z_max":0.03513,"peak_contact_force":0.545,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":402.0,"raw_peak_contact_force":30.64333,"tcp_end":[0.49953,-0.0567,0.21733],"tcp_start":[0.50908,0.08329,0.05941],"tcp_to_object_dist_end":0.22846,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04211,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.23695,"descend_1.contact_force_threshold":6.00868,"descend_1.descend_z":-0.01841,"push_1.push_distance":0.15562,"push_1.push_speed":0.17709,"retract_1.retract_height":0.15173},"optimized_scores":{"best_composite_score":0.0134,"best_fitness_score":0.1234,"best_task_score":0.00162},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49691,0.10361,0.00933],"force_p95":38.54828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.32487,"mean_force":25.20867,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50665,0.10736,0.05983]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.5185,0.10739,0.05848],"force_p95":37.93516,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.73238,"mean_force":24.71221,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50665,0.10736,0.05983]},{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.50469,0.10348,0.00942],"force_p95":0.6587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.24118,"mean_force":0.90497,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50184,0.03414,0.12517]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.51749,0.10716,0.05892],"force_p95":29.12237,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.84019,"mean_force":10.04968,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50578,0.10531,0.06018]},{"body_a":"peg","body_b":"channel_base_body","contact_count":424.0,"contact_point_centroid":[0.50573,0.10458,0.00939],"force_p95":0.57551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.66851,"mean_force":0.59615,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51181,0.11165,0.10661]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51881,0.10717,0.05876],"force_p95":21.24842,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.24842,"mean_force":21.24842,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50696,0.10789,0.06044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.50546,0.10473,0.00936],"force_p95":0.61114,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58776,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50962,0.15505,0.22118]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50054,0.19663,0.294]}],"total_contact_groups":8},"final_pose_error":0.02956,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50539,0.10411,0.03399],"final_tcp_position":[0.49891,-0.05367,0.17833],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":39.32487,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":300.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.10458,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53971,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":305.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51888,0.11597,0.15492],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":424.0,"n_steps_budget":900.0,"object_pos_end":[0.50592,0.10473,0.03383],"object_pos_start":[0.50596,0.10458,0.03383],"object_to_goal_dist_end":0.18493,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":21.66851,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":425.0,"raw_peak_contact_force":21.66851,"tcp_end":[0.50695,0.10787,0.06022],"tcp_start":[0.51888,0.11597,0.15492],"tcp_to_object_dist_end":0.0266,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.50554,0.10432,0.03385],"object_pos_start":[0.50592,0.10473,0.03383],"object_to_goal_dist_end":0.1845,"object_to_goal_dist_start":0.18493,"object_z_max":0.03388,"peak_contact_force":6.15032,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":39.32487,"subtask_id":"push_through_channel","tcp_end":[0.50644,0.10635,0.05951],"tcp_start":[0.50643,0.10653,0.05957],"tcp_to_object_dist_end":0.02576,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.50539,0.10411,0.03399],"object_pos_start":[0.50559,0.10403,0.03389],"object_to_goal_dist_end":0.18429,"object_to_goal_dist_start":0.18422,"object_z_max":0.03539,"peak_contact_force":0.53416,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":370.0,"raw_peak_contact_force":33.24118,"tcp_end":[0.49891,-0.05367,0.17833],"tcp_start":[0.50644,0.10635,0.05951],"tcp_to_object_dist_end":0.21394,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```