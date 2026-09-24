## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3569 | 0.72 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | -0.0271 | 0.37 | ❌ rejected |
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3579 | 0.72 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0324 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3576 | 0.73 | ❌ rejected |

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

## Current Skill (Q=0.357) — your mutation base

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

- **Composite score**: 0.357
- **task_score** (E): 0.725
- **fitness_score**: 0.547  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
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
| push_1 | 1.00 | 1.00 | 0.1198 |
| retract_1 | 0.00 | 1.00 | 0.0958 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.142, 0.049) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.547 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.496, 0.142, 0.049)→(0.496, 0.141, 0.041) | (0.501, 0.100, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.554 | 0.581 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.141, 0.041)→(0.494, 0.134, 0.035) | (0.501, 0.099, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 19.194 | 19.194 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.134, 0.035)→(0.497, 0.014, 0.037) | (0.501, 0.100, 0.034)→(0.506, -0.017, 0.037) | 0.180→0.064 | 1.00 / 2.333 | 17.570 | 120.419 |
| retract_1 | retract | 0.00 / step_budget | (0.497, 0.014, 0.037)→(0.495, 0.033, 0.131) | (0.506, -0.017, 0.037)→(0.502, -0.024, 0.031) | 0.064→0.057 | 1.00 / 1.000 | 0.534 | 56.001 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.727
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.727
- phase_score: 0.502
- phase_breakdown.contact_score: 0.685
- phase_breakdown.push_score: 0.312
- phase_breakdown.approach_score: 0.889

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.592
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.750
- **Median Q (composite search score)**: 0.348
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.332


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30864,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00429,"align_1.lateral_offset_y":0.00823,"approach_1.speed":0.07508,"push_1.push_depth":0.1,"retract_1.retract_height":0.1114,"retract_1.speed":0.04131},"optimized_scores":{"best_composite_score":0.40212,"best_fitness_score":0.59212,"best_task_score":0.72745},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":513.0,"contact_point_centroid":[0.54184,0.04736,0.05999],"force_p95":102.39235,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.23032,"mean_force":83.61646,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49691,0.04909,0.03693]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54252,-0.02764,0.05999],"force_p95":49.72817,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.04522,"mean_force":44.76973,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49785,-0.02201,0.03695]},{"body_a":"attachment","body_b":"peg","contact_count":444.0,"contact_point_centroid":[0.50313,0.02069,0.04376],"force_p95":25.27765,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.64673,"mean_force":6.93661,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49723,0.03224,0.03703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":565.0,"contact_point_centroid":[0.50516,0.00493,0.0097],"force_p95":24.31371,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.46584,"mean_force":5.6977,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49694,0.04754,0.03694]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5409,0.10595,0.06],"force_p95":21.38604,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.38604,"mean_force":21.38604,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49613,0.10477,0.03653]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":253.0,"contact_point_centroid":[0.5251,0.0098,0.02739],"force_p95":7.61449,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.83683,"mean_force":1.74868,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49715,0.0378,0.03703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50668,-0.04964,0.00941],"force_p95":0.59983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.18125,"mean_force":0.54645,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49469,-0.00239,0.08197]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.5049,-0.0324,0.05292],"force_p95":0.63552,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.63556,"mean_force":0.32203,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49655,-0.02057,0.03862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55733,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49866,0.1548,0.17095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.50262,0.06719,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54663,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49681,0.10737,0.03878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50306,0.0668,0.00938],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55059,"mean_force":0.54668,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49837,0.11078,0.04561]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":195.0,"contact_point_centroid":[0.52501,-0.04891,0.05882],"force_p95":0.05632,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17355,"mean_force":0.0091,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49474,-0.00091,0.08715]}],"total_contact_groups":12},"final_pose_error":0.17181,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50694,-0.04893,0.03379],"final_tcp_position":[0.49526,0.01074,0.1286],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":115.23032,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5478,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":805.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.499,0.11132,0.04824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54714,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.55059,"tcp_end":[0.49833,0.11023,0.04214],"tcp_start":[0.499,0.11132,0.04824],"tcp_to_object_dist_end":0.04386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":65.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":21.38604,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":66.0,"raw_peak_contact_force":21.38604,"tcp_end":[0.49612,0.10471,0.03648],"tcp_start":[0.49833,0.11023,0.04214],"tcp_to_object_dist_end":0.03796,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50642,-0.05066,0.03656],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.03023,"object_to_goal_dist_start":0.14764,"object_z_max":0.03804,"peak_contact_force":11.11243,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1775.0,"raw_peak_contact_force":115.23032,"tcp_end":[0.49788,-0.02185,0.03698],"tcp_start":[0.49612,0.10471,0.03648],"tcp_to_object_dist_end":0.03005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50694,-0.04893,0.03379],"object_pos_start":[0.50642,-0.05066,0.03656],"object_to_goal_dist_end":0.03243,"object_to_goal_dist_start":0.03023,"object_z_max":0.03672,"peak_contact_force":0.54629,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1220.0,"raw_peak_contact_force":50.04522,"tcp_end":[0.49526,0.01074,0.1286],"tcp_start":[0.49788,-0.02185,0.03698],"tcp_to_object_dist_end":0.11262,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28758,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00181,"align_1.lateral_offset_y":0.00621,"approach_1.speed":0.05124,"push_1.push_depth":0.09975,"retract_1.retract_height":0.17699,"retract_1.speed":0.05522},"optimized_scores":{"best_composite_score":0.34761,"best_fitness_score":0.53761,"best_task_score":0.75027},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":538.0,"contact_point_centroid":[0.5445,0.08572,0.05999],"force_p95":107.9762,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.86628,"mean_force":86.31451,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49882,0.08938,0.03615]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54296,0.01931,0.05999],"force_p95":52.01773,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.34849,"mean_force":45.78207,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49798,0.02245,0.03709]},{"body_a":"attachment","body_b":"peg","contact_count":301.0,"contact_point_centroid":[0.5001,0.0777,0.04014],"force_p95":13.41827,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.64883,"mean_force":2.69196,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49881,0.08937,0.03612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":570.0,"contact_point_centroid":[0.49863,0.04745,0.00962],"force_p95":8.60173,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.4671,"mean_force":1.82663,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49882,0.08684,0.03619]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":195.0,"contact_point_centroid":[0.47483,0.03929,0.03105],"force_p95":1.97906,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.45629,"mean_force":0.7044,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49885,0.06948,0.0367]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55031,0.12,0.05999],"force_p95":12.95265,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12.95265,"mean_force":12.95265,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49974,0.14221,0.03418]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.52514,0.09985,0.03116],"force_p95":3.24144,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.19727,"mean_force":1.023,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49873,0.12902,0.03515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50582,-0.00849,0.0094],"force_p95":0.57446,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.20527,"mean_force":0.54839,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49484,0.03313,0.08378]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52551,-0.01132,0.05879],"force_p95":0.80514,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97091,"mean_force":0.22461,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49723,0.02265,0.03799]},{"body_a":"peg","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.50305,0.11172,0.00939],"force_p95":0.59814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62959,"mean_force":0.54561,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50081,0.14678,0.03747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.50512,0.11115,0.00939],"force_p95":0.58591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5936,"mean_force":0.54414,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50459,0.15291,0.04655]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19944,0.29874]}],"total_contact_groups":13},"final_pose_error":0.17264,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50578,-0.00827,0.03377],"final_tcp_position":[0.49537,0.03835,0.13173],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":123.86628,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":24.0,"n_steps_budget":600.0,"object_pos_end":[0.50368,0.11176,0.0338],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19187,"object_z_max":0.03382,"peak_contact_force":0.52478,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.5936,"tcp_end":[0.50369,0.15272,0.04351],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.04209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":130.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.11178,0.03379],"object_pos_start":[0.50368,0.11176,0.0338],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.1919,"object_z_max":0.03383,"peak_contact_force":12.95265,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":131.0,"raw_peak_contact_force":12.95265,"tcp_end":[0.49974,0.14217,0.03415],"tcp_start":[0.50369,0.15272,0.04351],"tcp_to_object_dist_end":0.03065,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50479,-0.00941,0.03447],"object_pos_start":[0.50376,0.11178,0.03379],"object_to_goal_dist_end":0.07097,"object_to_goal_dist_start":0.19192,"object_z_max":0.03811,"peak_contact_force":0.67091,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1665.0,"raw_peak_contact_force":123.86628,"tcp_end":[0.49801,0.02262,0.03711],"tcp_start":[0.49974,0.14217,0.03415],"tcp_to_object_dist_end":0.03285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50578,-0.00827,0.03377],"object_pos_start":[0.50479,-0.00941,0.03447],"object_to_goal_dist_end":0.07224,"object_to_goal_dist_start":0.07097,"object_z_max":0.03481,"peak_contact_force":0.49972,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1020.0,"raw_peak_contact_force":52.34849,"tcp_end":[0.49537,0.03835,0.13173],"tcp_start":[0.49801,0.02262,0.03711],"tcp_to_object_dist_end":0.10899,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33548,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00509,"align_1.lateral_offset_y":-0.0028,"approach_1.speed":0.04696,"push_1.push_depth":0.09303,"retract_1.retract_height":0.15193,"retract_1.speed":0.02619},"optimized_scores":{"best_composite_score":0.32107,"best_fitness_score":0.51107,"best_task_score":0.69717},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":449.0,"contact_point_centroid":[0.53766,0.10207,0.05999],"force_p95":108.88361,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.16166,"mean_force":89.96396,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49006,0.11013,0.03645]},{"body_a":"attachment","body_b":"peg","contact_count":561.0,"contact_point_centroid":[0.49927,0.08169,0.03673],"force_p95":84.8195,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.69559,"mean_force":45.46082,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4918,0.09026,0.03696]},{"body_a":"peg","body_b":"channel_base_body","contact_count":676.0,"contact_point_centroid":[0.50565,0.0668,0.00971],"force_p95":55.62286,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.4739,"mean_force":22.64433,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49091,0.10001,0.03665]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54076,0.04033,0.06],"force_p95":64.63626,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.60884,"mean_force":55.88301,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49563,0.04236,0.03727]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":520.0,"contact_point_centroid":[0.52553,0.06702,0.02347],"force_p95":51.80435,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.89665,"mean_force":32.47821,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49221,0.08595,0.0371]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.50126,0.03376,0.0356],"force_p95":12.83494,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.64484,"mean_force":2.68475,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49464,0.04238,0.03837]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52526,0.02467,0.02177],"force_p95":18.43279,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.1695,"mean_force":4.04578,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49517,0.04213,0.03762]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54196,0.12,0.05998],"force_p95":23.24252,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.24252,"mean_force":23.24252,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48613,0.1552,0.03479]},{"body_a":"peg","body_b":"channel_base_body","contact_count":987.0,"contact_point_centroid":[0.49976,-0.01277,0.00819],"force_p95":0.72632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.34476,"mean_force":0.66725,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49292,0.04908,0.08422]},{"body_a":"peg","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.51871,0.07532,0.0688],"force_p95":7.66778,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.68927,"mean_force":5.09681,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49113,0.10165,0.03705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.49619,0.11915,0.0094],"force_p95":0.61089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55292,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49061,0.17919,0.17037]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.19927,0.29748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":44.0,"contact_point_centroid":[0.49725,0.11866,0.0094],"force_p95":0.60321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61227,"mean_force":0.5436,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48653,0.15704,0.03643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.49602,0.11999,0.00941],"force_p95":0.59684,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59878,"mean_force":0.54311,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48461,0.15937,0.04411]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,-0.03827,0.02416],"force_p95":0.40265,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40265,"mean_force":0.40265,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49383,0.05097,0.12918]}],"total_contact_groups":15},"final_pose_error":0.17642,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49475,-0.0145,0.02419],"final_tcp_position":[0.49388,0.05088,0.13119],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":122.16166,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11947,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1996,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52313,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48315,0.16005,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":58.0,"n_steps_budget":600.0,"object_pos_end":[0.49607,0.11907,0.03384],"object_pos_start":[0.49601,0.11947,0.03385],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.1996,"object_z_max":0.03386,"peak_contact_force":0.58978,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":58.0,"raw_peak_contact_force":0.59878,"tcp_end":[0.48732,0.15888,0.03861],"tcp_start":[0.48315,0.16005,0.04931],"tcp_to_object_dist_end":0.04105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":44.0,"n_steps_budget":600.0,"object_pos_end":[0.49602,0.11947,0.03384],"object_pos_start":[0.49607,0.11907,0.03384],"object_to_goal_dist_end":0.19961,"object_to_goal_dist_start":0.1992,"object_z_max":0.03385,"peak_contact_force":23.24252,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":45.0,"raw_peak_contact_force":23.24252,"tcp_end":[0.48613,0.15514,0.03474],"tcp_start":[0.48732,0.15888,0.03861],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.50807,0.00895,0.03997],"object_pos_start":[0.49602,0.11947,0.03384],"object_to_goal_dist_end":0.08931,"object_to_goal_dist_start":0.19961,"object_z_max":0.04056,"peak_contact_force":40.92664,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2230.0,"raw_peak_contact_force":122.16166,"tcp_end":[0.49563,0.04242,0.03727],"tcp_start":[0.48613,0.15514,0.03474],"tcp_to_object_dist_end":0.03582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49475,-0.0145,0.02419],"object_pos_start":[0.50807,0.00895,0.03997],"object_to_goal_dist_end":0.06759,"object_to_goal_dist_start":0.08931,"object_z_max":0.04075,"peak_contact_force":0.55737,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1041.0,"raw_peak_contact_force":65.60884,"tcp_end":[0.49388,0.05088,0.13119],"tcp_start":[0.49563,0.04242,0.03727],"tcp_to_object_dist_end":0.12539,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```