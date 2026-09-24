## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3584 | 0.72 | ❌ rejected |
| 11 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.4006 | 0.00 | ❌ rejected |
| 10 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0499 | 0.44 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1430 | 0.32 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4106 | 0.13 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.732, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.358) — your mutation base

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

- **Composite score**: 0.358
- **task_score** (E): 0.725
- **fitness_score**: 0.548  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2592 |
| approach_1 | 1.00 | 1.00 | 0.0078 |
| contact_1 | 1.00 | 1.00 | 0.0095 |
| push_1 | 1.00 | 1.00 | 0.1222 |
| retract_1 | 0.00 | 1.00 | 0.1081 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.142, 0.049) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.547 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.496, 0.142, 0.049)→(0.496, 0.141, 0.041) | (0.501, 0.100, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.554 | 0.581 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.141, 0.041)→(0.494, 0.134, 0.035) | (0.501, 0.099, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 19.194 | 19.194 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.134, 0.035)→(0.497, 0.012, 0.037) | (0.501, 0.100, 0.034)→(0.507, -0.019, 0.037) | 0.180→0.062 | 1.00 / 2.667 | 23.163 | 120.742 |
| retract_1 | retract | 0.00 / step_budget | (0.497, 0.012, 0.037)→(0.495, 0.033, 0.143) | (0.507, -0.019, 0.037)→(0.503, -0.026, 0.031) | 0.062→0.055 | 1.00 / 1.000 | 0.569 | 71.791 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.734
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.734
- phase_score: 0.502
- phase_breakdown.contact_score: 0.685
- phase_breakdown.push_score: 0.312
- phase_breakdown.approach_score: 0.889

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.595
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.734
- **Median Q (composite search score)**: 0.339
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.451


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56291,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00836,"align_1.lateral_offset_y":0.00036,"approach_1.speed":0.02774,"push_1.push_depth":0.1,"retract_1.retract_height":0.05666,"retract_1.speed":0.06899},"optimized_scores":{"best_composite_score":0.40498,"best_fitness_score":0.59498,"best_task_score":0.73449},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":515.0,"contact_point_centroid":[0.54185,0.04736,0.05999],"force_p95":101.87077,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.22834,"mean_force":83.42555,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49691,0.04909,0.03693]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54252,-0.02761,0.05999],"force_p95":67.35251,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.23822,"mean_force":57.24252,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49786,-0.02199,0.03696]},{"body_a":"attachment","body_b":"peg","contact_count":441.0,"contact_point_centroid":[0.50308,0.0209,0.04358],"force_p95":25.39575,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.22947,"mean_force":6.607,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49723,0.03245,0.03703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":551.0,"contact_point_centroid":[0.50492,0.00582,0.00969],"force_p95":23.00956,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.87096,"mean_force":5.51122,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49693,0.0483,0.03694]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5409,0.10595,0.06],"force_p95":21.38604,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.38604,"mean_force":21.38604,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49613,0.10477,0.03653]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":290.0,"contact_point_centroid":[0.52512,0.00431,0.02636],"force_p95":7.92967,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.4068,"mean_force":1.72109,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49725,0.03229,0.03704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55733,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49866,0.1548,0.17095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50626,-0.05043,0.00941],"force_p95":0.55954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88227,"mean_force":0.54039,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49484,-8e-05,0.0912]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":262.0,"contact_point_centroid":[0.52504,-0.05001,0.05174],"force_p95":0.29594,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64775,"mean_force":0.05311,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49508,-0.00284,0.08424]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.50262,0.06719,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54663,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49681,0.10737,0.03878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50306,0.0668,0.00938],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55059,"mean_force":0.54668,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49837,0.11078,0.04561]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50518,-0.03164,0.05942],"force_p95":0.2547,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29082,"mean_force":0.10016,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49594,-0.01971,0.03992]}],"total_contact_groups":12},"final_pose_error":0.1527,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50685,-0.05006,0.03382],"final_tcp_position":[0.4956,0.01365,0.14797],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":115.22834,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5478,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":805.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.499,0.11132,0.04824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54714,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.55059,"tcp_end":[0.49833,0.11023,0.04214],"tcp_start":[0.499,0.11132,0.04824],"tcp_to_object_dist_end":0.04386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":65.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":21.38604,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":66.0,"raw_peak_contact_force":21.38604,"tcp_end":[0.49612,0.10471,0.03648],"tcp_start":[0.49833,0.11023,0.04214],"tcp_to_object_dist_end":0.03796,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50635,-0.05136,0.03595],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.02961,"object_to_goal_dist_start":0.14764,"object_z_max":0.03804,"peak_contact_force":0.57693,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1797.0,"raw_peak_contact_force":115.22834,"tcp_end":[0.49787,-0.02187,0.03696],"tcp_start":[0.49612,0.10471,0.03648],"tcp_to_object_dist_end":0.0307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50685,-0.05006,0.03382],"object_pos_start":[0.50635,-0.05136,0.03595],"object_to_goal_dist_end":0.03133,"object_to_goal_dist_start":0.02961,"object_z_max":0.03595,"peak_contact_force":0.54313,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1277.0,"raw_peak_contact_force":68.23822,"tcp_end":[0.4956,0.01365,0.14797],"tcp_start":[0.49787,-0.02187,0.03696],"tcp_to_object_dist_end":0.13121,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40789,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0063,"align_1.lateral_offset_y":0.00779,"approach_1.speed":0.0585,"push_1.push_depth":0.09981,"retract_1.retract_height":0.15582,"retract_1.speed":0.0656},"optimized_scores":{"best_composite_score":0.33902,"best_fitness_score":0.52902,"best_task_score":0.72869},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":536.0,"contact_point_centroid":[0.5445,0.08592,0.05999],"force_p95":107.0879,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.5582,"mean_force":86.41191,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49882,0.08957,0.03614]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54297,0.01932,0.06],"force_p95":91.69235,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.98083,"mean_force":61.66681,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49799,0.02246,0.0371]},{"body_a":"attachment","body_b":"peg","contact_count":324.0,"contact_point_centroid":[0.50052,0.07389,0.04046],"force_p95":13.53057,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.84779,"mean_force":2.81087,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49877,0.0856,0.03618]},{"body_a":"peg","body_b":"channel_base_body","contact_count":576.0,"contact_point_centroid":[0.49987,0.047,0.00969],"force_p95":9.16352,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.82038,"mean_force":1.98252,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49882,0.08718,0.03619]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":166.0,"contact_point_centroid":[0.4747,0.04833,0.02783],"force_p95":2.70417,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.39828,"mean_force":0.79279,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49895,0.078,0.0366]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55031,0.12,0.05999],"force_p95":12.95265,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12.95265,"mean_force":12.95265,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49974,0.14221,0.03418]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":91.0,"contact_point_centroid":[0.52512,0.08113,0.02511],"force_p95":2.90637,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.32788,"mean_force":0.86849,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49867,0.11051,0.03559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.50424,0.01164,0.05278],"force_p95":0.70585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97521,"mean_force":0.29496,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49648,0.02343,0.03983]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50632,-0.00564,0.00942],"force_p95":0.55734,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95615,"mean_force":0.54321,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49495,0.03379,0.09143]},{"body_a":"peg","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.50305,0.11172,0.00939],"force_p95":0.59814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62959,"mean_force":0.54561,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50081,0.14678,0.03747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.50512,0.11115,0.00939],"force_p95":0.58591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5936,"mean_force":0.54414,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50459,0.15291,0.04655]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19944,0.29874]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52502,-0.00517,0.05983],"force_p95":0.07037,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.07419,"mean_force":0.03683,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49545,0.02459,0.04233]}],"total_contact_groups":14},"final_pose_error":0.15792,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50658,-0.00481,0.03378],"final_tcp_position":[0.4956,0.0382,0.14683],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":125.5582,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":24.0,"n_steps_budget":600.0,"object_pos_end":[0.50368,0.11176,0.0338],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19187,"object_z_max":0.03382,"peak_contact_force":0.52478,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.5936,"tcp_end":[0.50369,0.15272,0.04351],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.04209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":130.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.11178,0.03379],"object_pos_start":[0.50368,0.11176,0.0338],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.1919,"object_z_max":0.03383,"peak_contact_force":12.95265,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":131.0,"raw_peak_contact_force":12.95265,"tcp_end":[0.49974,0.14217,0.03415],"tcp_start":[0.50369,0.15272,0.04351],"tcp_to_object_dist_end":0.03065,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50666,-0.0064,0.03572],"object_pos_start":[0.50376,0.11178,0.03379],"object_to_goal_dist_end":0.07402,"object_to_goal_dist_start":0.19192,"object_z_max":0.03751,"peak_contact_force":1.42424,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1693.0,"raw_peak_contact_force":125.5582,"tcp_end":[0.498,0.02257,0.0371],"tcp_start":[0.49974,0.14217,0.03415],"tcp_to_object_dist_end":0.03028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50658,-0.00481,0.03378],"object_pos_start":[0.50666,-0.0064,0.03572],"object_to_goal_dist_end":0.07573,"object_to_goal_dist_start":0.07402,"object_z_max":0.03593,"peak_contact_force":0.54052,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1037.0,"raw_peak_contact_force":95.98083,"tcp_end":[0.4956,0.0382,0.14683],"tcp_start":[0.498,0.02257,0.0371],"tcp_to_object_dist_end":0.12145,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36486,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00376,"align_1.lateral_offset_y":-0.00768,"approach_1.speed":0.07226,"push_1.push_depth":0.09974,"retract_1.retract_height":0.14255,"retract_1.speed":0.0566},"optimized_scores":{"best_composite_score":0.33123,"best_fitness_score":0.52123,"best_task_score":0.71052},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":485.0,"contact_point_centroid":[0.53766,0.09942,0.05999],"force_p95":110.62481,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.44016,"mean_force":91.34391,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49017,0.10717,0.0365]},{"body_a":"attachment","body_b":"peg","contact_count":624.0,"contact_point_centroid":[0.49915,0.07855,0.03658],"force_p95":81.18505,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.05923,"mean_force":42.59493,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49187,0.0873,0.03698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":724.0,"contact_point_centroid":[0.50556,0.06241,0.00973],"force_p95":53.96725,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.42256,"mean_force":22.48693,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49107,0.09621,0.0367]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":544.0,"contact_point_centroid":[0.52545,0.06095,0.02336],"force_p95":48.60002,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.21753,"mean_force":31.39969,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4925,0.08008,0.03717]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54102,0.03259,0.05999],"force_p95":50.77814,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.15468,"mean_force":45.03568,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49591,0.03503,0.03725]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.50163,0.02632,0.03549],"force_p95":8.3643,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.36465,"mean_force":1.4951,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49521,0.0352,0.0382]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54196,0.12,0.05998],"force_p95":23.24252,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.24252,"mean_force":23.24252,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48613,0.1552,0.03479]},{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.49746,-0.02096,0.00826],"force_p95":0.74317,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.5579,"mean_force":0.69781,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4932,0.04334,0.08539]},{"body_a":"peg","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.51896,0.07566,0.06862],"force_p95":7.2759,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.45816,"mean_force":4.8845,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49106,0.10156,0.03703]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52521,0.01138,0.02821],"force_p95":7.87401,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.1749,"mean_force":1.58431,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49555,0.03503,0.03772]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.475,-0.04679,0.02432],"force_p95":7.62972,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.74875,"mean_force":3.69817,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49305,0.04458,0.08755]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.49619,0.11915,0.0094],"force_p95":0.61089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55292,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49061,0.17919,0.17037]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.19927,0.29748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":44.0,"contact_point_centroid":[0.49725,0.11866,0.0094],"force_p95":0.60321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61227,"mean_force":0.5436,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48653,0.15704,0.03643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.49602,0.11999,0.00941],"force_p95":0.59684,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59878,"mean_force":0.54311,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48461,0.15937,0.04411]}],"total_contact_groups":15},"final_pose_error":0.17301,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49581,-0.02444,0.02413],"final_tcp_position":[0.49415,0.0462,0.13337],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":121.44016,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11947,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1996,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52313,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48315,0.16005,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":58.0,"n_steps_budget":600.0,"object_pos_end":[0.49607,0.11907,0.03384],"object_pos_start":[0.49601,0.11947,0.03385],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.1996,"object_z_max":0.03386,"peak_contact_force":0.58978,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":58.0,"raw_peak_contact_force":0.59878,"tcp_end":[0.48732,0.15888,0.03861],"tcp_start":[0.48315,0.16005,0.04931],"tcp_to_object_dist_end":0.04105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":44.0,"n_steps_budget":600.0,"object_pos_end":[0.49602,0.11947,0.03384],"object_pos_start":[0.49607,0.11907,0.03384],"object_to_goal_dist_end":0.19961,"object_to_goal_dist_start":0.1992,"object_z_max":0.03385,"peak_contact_force":23.24252,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":45.0,"raw_peak_contact_force":23.24252,"tcp_end":[0.48613,0.15514,0.03474],"tcp_start":[0.48732,0.15888,0.03861],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50787,0.00132,0.04002],"object_pos_start":[0.49602,0.11947,0.03384],"object_to_goal_dist_end":0.0817,"object_to_goal_dist_start":0.19961,"object_z_max":0.04048,"peak_contact_force":67.48714,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2385.0,"raw_peak_contact_force":121.44016,"tcp_end":[0.49593,0.0352,0.03728],"tcp_start":[0.48613,0.15514,0.03474],"tcp_to_object_dist_end":0.03603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49581,-0.02444,0.02413],"object_pos_start":[0.50787,0.00132,0.04002],"object_to_goal_dist_end":0.05793,"object_to_goal_dist_start":0.0817,"object_z_max":0.04074,"peak_contact_force":0.62419,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1054.0,"raw_peak_contact_force":51.15468,"tcp_end":[0.49415,0.0462,0.13337],"tcp_start":[0.49593,0.0352,0.03728],"tcp_to_object_dist_end":0.13011,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```