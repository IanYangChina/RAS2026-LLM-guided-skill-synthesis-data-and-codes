## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 14 | -0.3170 | 0.43 | ❌ rejected |
| 13 | align → approach → contact → push | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0943 | 0.00 | ❌ rejected |
| 12 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3584 | 0.72 | ❌ rejected |
| 11 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.4006 | 0.00 | ❌ rejected |
| 10 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0499 | 0.44 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=-0.317) — your mutation base

```yaml
skill: peg_channel
phases:
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
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
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

```

## Design Metrics

- **Composite score**: -0.317
- **task_score** (E): 0.430
- **fitness_score**: 0.340  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.790

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1379 |
| approach_1 | 1.00 | 1.00 | 0.1299 |
| contact_1 | 1.00 | 1.00 | 0.0576 |
| push_1 | 0.00 | 1.00 | 0.0013 |
| retract_1 | 1.00 | 1.00 | 0.0995 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.109, 0.197) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.521 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.499, 0.109, 0.197)→(0.498, 0.148, 0.073) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.529 | 0.596 |
| contact_1 | contact | 1.00 / force_exceeded | (0.498, 0.148, 0.073)→(0.497, 0.106, 0.035) | (0.501, 0.099, 0.034)→(0.506, 0.077, 0.036) | 0.180→0.158 | 1.00 / 2.000 | 2612.687 | 6.866 |
| push_1 | push | 0.00 / guard_failure | (0.501, 0.101, 0.032)→(0.502, 0.100, 0.031) | (0.506, 0.077, 0.036)→(0.507, 0.071, 0.036) | 0.158→0.151 | 1.00 / 1.667 | 2.971 | 524.714 |
| retract_1 | retract | 1.00 / step_budget | (0.502, 0.100, 0.031)→(0.503, 0.075, 0.127) | (0.507, 0.070, 0.036)→(0.505, 0.022, 0.027) | 0.150→0.104 | 1.00 / 1.000 | 0.553 | 425.384 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.693
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.693
- phase_score: 0.481
- phase_breakdown.reach_peg_score: 0.121
- phase_breakdown.reach_exit_score: 0.636

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.566
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.693
- **Median Q (composite search score)**: -0.260
- **K-run variance**: 0.0706
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.367


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31548,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00266,"align_1.lateral_offset_y":0.00585,"align_1.tolerance":0.0055,"approach_1.speed":0.04818,"approach_1.tolerance":0.00839,"contact_1.contact_force_threshold":10.62237,"contact_1.contact_speed":0.02886,"push_1.force_guard_threshold":41.21949,"push_1.push_depth":0.13939,"push_1.push_speed":0.03221,"push_1.retry_offset_x":0.00378,"push_1.retry_offset_y":0.00284,"retract_1.retract_height":0.08984,"retract_1.speed":0.0789},"optimized_scores":{"best_composite_score":-0.02382,"best_fitness_score":0.56618,"best_task_score":0.69346},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52587,0.06675,0.05986],"force_p95":1440.1406,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1458.32189,"mean_force":1276.50897,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50951,0.06425,0.02839]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52606,0.06344,0.05981],"force_p95":1231.18613,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1262.70469,"mean_force":584.88988,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.509,0.05917,0.02651]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.54132,0.08005,0.05955],"force_p95":1145.74807,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1164.28308,"mean_force":676.31286,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50919,0.05892,0.02633]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50376,0.06346,0.03944],"force_p95":39.4486,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.47429,"mean_force":16.43656,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50073,0.07516,0.03377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.50662,0.04231,0.00986],"force_p95":34.70904,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.81399,"mean_force":16.29309,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50508,0.06994,0.03132]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52546,0.04162,0.03052],"force_p95":29.21309,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.46762,"mean_force":9.33959,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50365,0.0716,0.03208]},{"body_a":"peg","body_b":"channel_base_body","contact_count":718.0,"contact_point_centroid":[0.49921,-0.04194,0.00805],"force_p95":0.77559,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.31065,"mean_force":0.65949,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50613,0.05159,0.0746]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47497,-0.0651,0.02399],"force_p95":7.6532,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.95395,"mean_force":2.4325,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50643,0.0609,0.03779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":800.0,"contact_point_centroid":[0.50432,0.05272,0.0097],"force_p95":3.85873,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.50303,"mean_force":1.92845,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49713,0.09518,0.04481]},{"body_a":"attachment","body_b":"peg","contact_count":452.0,"contact_point_centroid":[0.50104,0.07555,0.04529],"force_p95":3.6249,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.17527,"mean_force":2.63351,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49759,0.08726,0.04022]},{"body_a":"peg","body_b":"channel_base_body","contact_count":886.0,"contact_point_centroid":[0.50308,0.06747,0.00936],"force_p95":0.55304,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55636,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4978,0.13671,0.24101]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52591,0.01673,0.02527],"force_p95":1.49638,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71504,"mean_force":0.75001,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51023,0.05915,0.02604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":574.0,"contact_point_centroid":[0.50301,0.06748,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55075,"mean_force":0.54665,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49696,0.10365,0.1284]}],"total_contact_groups":13},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50155,-0.04349,0.02406],"final_tcp_position":[0.50565,0.03187,0.11676],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3919.7749,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":902.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5479,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":886.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.49752,0.07791,0.18959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54365,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":574.0,"raw_peak_contact_force":0.55075,"subtask_id":"reach_peg","tcp_end":[0.49895,0.11714,0.06094],"tcp_start":[0.49752,0.07791,0.18959],"tcp_to_object_dist_end":0.05677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,0.04912,0.03577],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.12938,"object_to_goal_dist_start":0.14762,"object_z_max":0.03577,"peak_contact_force":3919.7749,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1252.0,"raw_peak_contact_force":4.50303,"subtask_id":"reach_peg","tcp_end":[0.49834,0.07789,0.03508],"tcp_start":[0.49895,0.11714,0.06094],"tcp_to_object_dist_end":0.03005,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.50874,0.03111,0.03569],"object_pos_start":[0.50697,0.04912,0.03577],"object_to_goal_dist_end":0.11154,"object_to_goal_dist_start":0.12938,"object_z_max":0.03585,"peak_contact_force":1.43173,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":1458.32189,"subtask_id":"reach_exit","tcp_end":[0.5107,0.06197,0.02725],"tcp_start":[0.51002,0.06344,0.02793],"tcp_to_object_dist_end":0.03205,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50155,-0.04349,0.02406],"object_pos_start":[0.50889,0.029,0.03585],"object_to_goal_dist_end":0.03987,"object_to_goal_dist_start":0.10944,"object_z_max":0.04116,"peak_contact_force":0.59294,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":792.0,"raw_peak_contact_force":1262.70469,"subtask_id":"reach_exit","tcp_end":[0.50565,0.03187,0.11676],"tcp_start":[0.5107,0.06197,0.02725],"tcp_to_object_dist_end":0.11954,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3121,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00528,"align_1.lateral_offset_y":-0.00644,"align_1.tolerance":0.01132,"approach_1.speed":0.0762,"approach_1.tolerance":0.02678,"contact_1.contact_force_threshold":19.13482,"contact_1.contact_speed":0.02193,"push_1.force_guard_threshold":41.80813,"push_1.push_depth":0.17863,"push_1.push_speed":0.0336,"push_1.retry_offset_x":-0.00399,"push_1.retry_offset_y":0.00042,"retract_1.retract_height":0.07602,"retract_1.speed":0.06727},"optimized_scores":{"best_composite_score":-0.26011,"best_fitness_score":0.32989,"best_task_score":0.46075},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50378,0.1075,0.04489],"force_p95":46.22825,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.53335,"mean_force":21.24546,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5005,0.11914,0.03735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.51205,0.0741,0.00994],"force_p95":44.68948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.98202,"mean_force":24.05664,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50026,0.11938,0.03748]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52513,0.09014,0.03548],"force_p95":36.36892,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.04459,"mean_force":12.514,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50038,0.11927,0.03742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":657.0,"contact_point_centroid":[0.50645,0.04005,0.00833],"force_p95":7.88169,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.03513,"mean_force":1.08122,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50118,0.10775,0.07024]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":83.0,"contact_point_centroid":[0.52508,0.04889,0.02287],"force_p95":9.88507,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.38443,"mean_force":4.07171,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50084,0.11238,0.05911]},{"body_a":"peg","body_b":"channel_base_body","contact_count":487.0,"contact_point_centroid":[0.50513,0.09739,0.00971],"force_p95":7.91538,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.60172,"mean_force":3.47495,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49962,0.13823,0.05606]},{"body_a":"attachment","body_b":"peg","contact_count":250.0,"contact_point_centroid":[0.50196,0.11699,0.04613],"force_p95":7.83314,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.22762,"mean_force":5.88824,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49966,0.1287,0.04646]},{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50346,0.11173,0.00935],"force_p95":0.62566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56497,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50504,0.15541,0.24445]},{"body_a":"peg","body_b":"channel_base_body","contact_count":201.0,"contact_point_centroid":[0.50372,0.11157,0.00941],"force_p95":0.59273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6165,"mean_force":0.5429,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50693,0.13965,0.14172]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49984,0.19894,0.29901]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50456,0.10537,0.0395],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50258,0.11706,0.0361]}],"total_contact_groups":11},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50586,0.03806,0.02414],"final_tcp_position":[0.50326,0.09101,0.10306],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3915.07817,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":414.0,"n_steps_budget":930.0,"object_pos_end":[0.50371,0.11175,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51771,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":408.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.51121,0.11407,0.19576],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11175,0.03397],"object_pos_start":[0.50371,0.11175,0.03381],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19189,"object_z_max":0.03397,"peak_contact_force":0.51529,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":201.0,"raw_peak_contact_force":0.6165,"subtask_id":"reach_peg","tcp_end":[0.50269,0.15823,0.07975],"tcp_start":[0.51121,0.11407,0.19576],"tcp_to_object_dist_end":0.06525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,0.09085,0.03563],"object_pos_start":[0.50371,0.11175,0.03397],"object_to_goal_dist_end":0.17104,"object_to_goal_dist_start":0.19188,"object_z_max":0.03762,"peak_contact_force":3915.07817,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":737.0,"raw_peak_contact_force":8.60172,"subtask_id":"reach_peg","tcp_end":[0.49974,0.11994,0.03782],"tcp_start":[0.50269,0.15823,0.07975],"tcp_to_object_dist_end":0.03005,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,0.0894,0.03576],"object_pos_start":[0.50695,0.09085,0.03563],"object_to_goal_dist_end":0.1696,"object_to_goal_dist_start":0.17104,"object_z_max":0.03576,"peak_contact_force":7.4824,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":50.53335,"subtask_id":"reach_exit","tcp_end":[0.50224,0.11742,0.03635],"tcp_start":[0.50125,0.11838,0.03689],"tcp_to_object_dist_end":0.02842,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":679.0,"n_steps_budget":780.0,"object_pos_end":[0.50586,0.03806,0.02414],"object_pos_start":[0.50691,0.08827,0.03588],"object_to_goal_dist_end":0.11926,"object_to_goal_dist_start":0.16846,"object_z_max":0.04076,"peak_contact_force":0.52112,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":742.0,"raw_peak_contact_force":12.03513,"subtask_id":"reach_exit","tcp_end":[0.50326,0.09101,0.10306],"tcp_start":[0.50224,0.11742,0.03635],"tcp_to_object_dist_end":0.09507,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48718,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00315,"align_1.lateral_offset_y":0.00302,"align_1.tolerance":0.02209,"approach_1.speed":0.09521,"approach_1.tolerance":0.02637,"contact_1.contact_force_threshold":10.49758,"contact_1.contact_speed":0.0259,"push_1.force_guard_threshold":40.87312,"push_1.push_depth":0.11903,"push_1.push_speed":0.02201,"push_1.retry_offset_x":0.00165,"push_1.retry_offset_y":0.00186,"retract_1.retract_height":0.15216,"retract_1.speed":0.08129},"optimized_scores":{"best_composite_score":-0.66695,"best_fitness_score":0.12305,"best_task_score":0.13677},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49859,0.10883,0.04734],"force_p95":64.82827,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.28546,"mean_force":60.71356,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4922,0.12021,0.03112]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50761,0.07601,0.00997],"force_p95":63.9054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.31238,"mean_force":60.24259,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4922,0.12021,0.03112]},{"body_a":"peg","body_b":"channel_base_body","contact_count":695.0,"contact_point_centroid":[0.49987,0.10012,0.00975],"force_p95":6.67094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.49365,"mean_force":3.08178,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49071,0.14223,0.0513]},{"body_a":"attachment","body_b":"peg","contact_count":402.0,"contact_point_centroid":[0.49526,0.12103,0.04766],"force_p95":6.54249,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.14574,"mean_force":4.56265,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49129,0.1326,0.04238]},{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.49676,0.11903,0.00936],"force_p95":0.73399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.58456,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.494,0.16567,0.24837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50577,0.07089,0.00944],"force_p95":0.70824,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41144,"mean_force":0.55176,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49498,0.11842,0.09807]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":95.0,"contact_point_centroid":[0.52549,0.0718,0.0494],"force_p95":0.85417,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.05439,"mean_force":0.28999,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49146,0.12163,0.04503]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49944,0.19773,0.29678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":212.0,"contact_point_centroid":[0.49593,0.11926,0.00943],"force_p95":0.60881,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62105,"mean_force":0.54019,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49049,0.15739,0.14624]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50086,0.10816,0.06191],"force_p95":0.04744,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04935,"mean_force":0.03026,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.493,0.11963,0.03073]}],"total_contact_groups":10},"final_pose_error":0.0295,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5065,0.07185,0.03379],"final_tcp_position":[0.50011,0.10308,0.16173],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":65.28546,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":205.0,"n_steps_budget":870.0,"object_pos_end":[0.49604,0.11904,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49637,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":204.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48952,0.1364,0.20634],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11901,0.03405],"object_pos_start":[0.49604,0.11904,0.03386],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19917,"object_z_max":0.03414,"peak_contact_force":0.52672,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":212.0,"raw_peak_contact_force":0.62105,"subtask_id":"reach_peg","tcp_end":[0.49232,0.16924,0.07979],"tcp_start":[0.48952,0.1364,0.20634],"tcp_to_object_dist_end":0.06804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.50396,0.09243,0.03578],"object_pos_start":[0.49605,0.11901,0.03405],"object_to_goal_dist_end":0.17253,"object_to_goal_dist_start":0.19914,"object_z_max":0.03719,"peak_contact_force":3.20728,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1097.0,"raw_peak_contact_force":7.49365,"subtask_id":"reach_peg","tcp_end":[0.49206,0.12032,0.03118],"tcp_start":[0.49232,0.16924,0.07979],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50423,0.09219,0.03587],"object_pos_start":[0.50396,0.09243,0.03578],"object_to_goal_dist_end":0.17229,"object_to_goal_dist_start":0.17253,"object_z_max":0.03587,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":65.28546,"subtask_id":"reach_exit","tcp_end":[0.49288,0.11971,0.03082],"tcp_start":[0.49234,0.1201,0.03105],"tcp_to_object_dist_end":0.03019,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5065,0.07185,0.03379],"object_pos_start":[0.50488,0.09163,0.03633],"object_to_goal_dist_end":0.15211,"object_to_goal_dist_start":0.17173,"object_z_max":0.03976,"peak_contact_force":0.54468,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1066.0,"raw_peak_contact_force":1.41144,"subtask_id":"reach_exit","tcp_end":[0.50011,0.10308,0.16173],"tcp_start":[0.49288,0.11971,0.03082],"tcp_to_object_dist_end":0.13186,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```