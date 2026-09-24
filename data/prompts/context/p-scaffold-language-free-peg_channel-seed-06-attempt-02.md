## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3576 | 0.73 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3601 | 0.73 | ✅ accepted |
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3561 | 0.72 | ✅ accepted |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
| push_1 | 1.00 | 1.00 | 0.1216 |
| retract_1 | 0.00 | 1.00 | 0.0968 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.142, 0.049) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.547 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.496, 0.142, 0.049)→(0.496, 0.141, 0.041) | (0.501, 0.100, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.554 | 0.581 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.141, 0.041)→(0.494, 0.134, 0.035) | (0.501, 0.099, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 19.194 | 19.194 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.134, 0.035)→(0.497, 0.013, 0.037) | (0.501, 0.100, 0.034)→(0.507, -0.018, 0.038) | 0.180→0.062 | 1.00 / 2.333 | 23.240 | 121.693 |
| retract_1 | retract | 0.00 / step_budget | (0.497, 0.013, 0.037)→(0.495, 0.032, 0.131) | (0.507, -0.018, 0.038)→(0.502, -0.027, 0.031) | 0.062→0.054 | 1.00 / 1.000 | 0.566 | 66.635 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.731
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.731
- phase_score: 0.498
- phase_breakdown.contact_score: 0.685
- phase_breakdown.push_score: 0.305
- phase_breakdown.approach_score: 0.889

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.591
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.746
- **Median Q (composite search score)**: 0.346
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.415


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3268,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00216,"align_1.lateral_offset_y":0.00162,"approach_1.speed":0.07473,"push_1.push_depth":0.09884,"retract_1.retract_height":0.0816,"retract_1.speed":0.05588},"optimized_scores":{"best_composite_score":0.40096,"best_fitness_score":0.59096,"best_task_score":0.73088},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":519.0,"contact_point_centroid":[0.54184,0.04753,0.05999],"force_p95":102.33803,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.37965,"mean_force":83.38249,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4969,0.04925,0.03693]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54253,-0.02642,0.05999],"force_p95":54.52323,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.82109,"mean_force":48.86617,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49785,-0.02086,0.03696]},{"body_a":"attachment","body_b":"peg","contact_count":423.0,"contact_point_centroid":[0.5031,0.02258,0.04343],"force_p95":24.53716,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.65793,"mean_force":6.58488,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49719,0.03409,0.03702]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.50569,0.0061,0.00975],"force_p95":22.67339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.51146,"mean_force":5.17559,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49692,0.04866,0.03694]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5409,0.10595,0.06],"force_p95":21.38604,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.38604,"mean_force":21.38604,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49613,0.10477,0.03653]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":315.0,"contact_point_centroid":[0.52513,0.01044,0.02732],"force_p95":8.76125,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.96079,"mean_force":1.87155,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49711,0.03811,0.037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55733,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49866,0.1548,0.17095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50586,-0.04962,0.00939],"force_p95":0.60099,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21346,"mean_force":0.54933,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49469,-0.00119,0.08298]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.50262,0.06719,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54663,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49681,0.10737,0.03878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50306,0.0668,0.00938],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55059,"mean_force":0.54668,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49837,0.11078,0.04561]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50544,-0.03119,0.05637],"force_p95":0.34721,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51408,"mean_force":0.06693,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49647,-0.01938,0.03872]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52503,-0.0475,0.01234],"force_p95":0.308,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3083,"mean_force":0.30533,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49787,-0.02075,0.03697]}],"total_contact_groups":12},"final_pose_error":0.17039,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,-0.04948,0.03377],"final_tcp_position":[0.49529,0.01168,0.13008],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":113.37965,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5478,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":805.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.499,0.11132,0.04824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54714,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.55059,"tcp_end":[0.49833,0.11023,0.04214],"tcp_start":[0.499,0.11132,0.04824],"tcp_to_object_dist_end":0.04386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":65.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":21.38604,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":66.0,"raw_peak_contact_force":21.38604,"tcp_end":[0.49612,0.10471,0.03648],"tcp_start":[0.49833,0.11023,0.04214],"tcp_to_object_dist_end":0.03796,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50672,-0.04955,0.03702],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.03132,"object_to_goal_dist_start":0.14764,"object_z_max":0.03788,"peak_contact_force":1.41421,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1803.0,"raw_peak_contact_force":113.37965,"tcp_end":[0.49787,-0.02071,0.03698],"tcp_start":[0.49612,0.10471,0.03648],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,-0.04948,0.03377],"object_pos_start":[0.50672,-0.04955,0.03702],"object_to_goal_dist_end":0.0317,"object_to_goal_dist_start":0.03132,"object_z_max":0.03702,"peak_contact_force":0.60185,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1012.0,"raw_peak_contact_force":54.82109,"tcp_end":[0.49529,0.01168,0.13008],"tcp_start":[0.49787,-0.02071,0.03698],"tcp_to_object_dist_end":0.11458,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28571,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00435,"align_1.lateral_offset_y":0.00467,"approach_1.speed":0.08192,"push_1.push_depth":0.09959,"retract_1.retract_height":0.14374,"retract_1.speed":0.05378},"optimized_scores":{"best_composite_score":0.34562,"best_fitness_score":0.53562,"best_task_score":0.74568},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":522.0,"contact_point_centroid":[0.54451,0.08678,0.05999],"force_p95":107.92239,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.29019,"mean_force":86.75581,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49881,0.09051,0.03613]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54294,0.01949,0.05999],"force_p95":88.21245,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.84849,"mean_force":56.38155,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49796,0.02262,0.03709]},{"body_a":"attachment","body_b":"peg","contact_count":395.0,"contact_point_centroid":[0.50383,0.06805,0.04323],"force_p95":24.42951,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.20457,"mean_force":5.86882,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49872,0.07968,0.03632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":534.0,"contact_point_centroid":[0.5046,0.04547,0.00977],"force_p95":23.43602,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.90406,"mean_force":4.69317,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49881,0.08894,0.03615]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55031,0.12,0.05999],"force_p95":12.95265,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12.95265,"mean_force":12.95265,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49974,0.14221,0.03418]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":201.0,"contact_point_centroid":[0.52514,0.05571,0.02571],"force_p95":4.88702,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.08436,"mean_force":1.08354,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49872,0.08442,0.03628]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50552,-0.00764,0.00939],"force_p95":0.58124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35951,"mean_force":0.55076,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4948,0.03329,0.08393]},{"body_a":"peg","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.50305,0.11172,0.00939],"force_p95":0.59814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62959,"mean_force":0.54561,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50081,0.14678,0.03747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.50512,0.11115,0.00939],"force_p95":0.58591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5936,"mean_force":0.54414,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50459,0.15291,0.04655]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19944,0.29874]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,-0.00814,0.06],"force_p95":0.21693,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21693,"mean_force":0.21693,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49797,0.02278,0.03709]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50546,0.01144,0.05793],"force_p95":0.16467,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19827,"mean_force":0.04685,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49664,0.02316,0.03883]}],"total_contact_groups":13},"final_pose_error":0.17266,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5056,-0.00753,0.03377],"final_tcp_position":[0.49536,0.03845,0.13174],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":125.29019,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":24.0,"n_steps_budget":600.0,"object_pos_end":[0.50368,0.11176,0.0338],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19187,"object_z_max":0.03382,"peak_contact_force":0.52478,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.5936,"tcp_end":[0.50369,0.15272,0.04351],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.04209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":130.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.11178,0.03379],"object_pos_start":[0.50368,0.11176,0.0338],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.1919,"object_z_max":0.03383,"peak_contact_force":12.95265,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":131.0,"raw_peak_contact_force":12.95265,"tcp_end":[0.49974,0.14217,0.03415],"tcp_start":[0.50369,0.15272,0.04351],"tcp_to_object_dist_end":0.03065,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50674,-0.00694,0.03658],"object_pos_start":[0.50376,0.11178,0.03379],"object_to_goal_dist_end":0.07345,"object_to_goal_dist_start":0.19192,"object_z_max":0.03736,"peak_contact_force":1.09988,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1652.0,"raw_peak_contact_force":125.29019,"tcp_end":[0.49797,0.02278,0.03709],"tcp_start":[0.49974,0.14217,0.03415],"tcp_to_object_dist_end":0.03099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5056,-0.00753,0.03377],"object_pos_start":[0.50674,-0.00694,0.03658],"object_to_goal_dist_end":0.07295,"object_to_goal_dist_start":0.07345,"object_z_max":0.03658,"peak_contact_force":0.54733,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1012.0,"raw_peak_contact_force":94.84849,"tcp_end":[0.49536,0.03845,0.13174],"tcp_start":[0.49797,0.02278,0.03709],"tcp_to_object_dist_end":0.10871,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00017,"align_1.lateral_offset_y":0.00048,"approach_1.speed":0.07379,"push_1.push_depth":0.09922,"retract_1.retract_height":0.09749,"retract_1.speed":0.05387},"optimized_scores":{"best_composite_score":0.32618,"best_fitness_score":0.51618,"best_task_score":0.69865},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":486.0,"contact_point_centroid":[0.53763,0.09964,0.05999],"force_p95":113.05064,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.40955,"mean_force":91.93318,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49012,0.10746,0.03649]},{"body_a":"attachment","body_b":"peg","contact_count":614.0,"contact_point_centroid":[0.4995,0.0783,0.03777],"force_p95":80.54437,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.22216,"mean_force":43.58853,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49187,0.08709,0.03699]},{"body_a":"peg","body_b":"channel_base_body","contact_count":734.0,"contact_point_centroid":[0.50508,0.06316,0.0097],"force_p95":53.1909,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.28456,"mean_force":22.24815,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.491,0.09684,0.0367]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":560.0,"contact_point_centroid":[0.52546,0.06206,0.02582],"force_p95":48.16662,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.83526,"mean_force":30.99151,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49233,0.08188,0.03713]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54102,0.03304,0.05999],"force_p95":49.84647,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.23643,"mean_force":44.40587,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49591,0.03545,0.03724]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.50161,0.02678,0.03548],"force_p95":9.23607,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.51718,"mean_force":1.70073,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4952,0.03562,0.03816]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54196,0.12,0.05998],"force_p95":23.24252,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.24252,"mean_force":23.24252,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48613,0.1552,0.03479]},{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.4972,-0.02079,0.00821],"force_p95":0.73998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.91697,"mean_force":0.69302,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49319,0.04365,0.08478]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52522,0.01759,0.02147],"force_p95":7.87591,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.83244,"mean_force":1.96025,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49562,0.03543,0.03759]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.475,-0.04583,0.02436],"force_p95":7.40975,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.68608,"mean_force":3.73028,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49262,0.04275,0.06887]},{"body_a":"peg","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.51833,0.06962,0.06915],"force_p95":6.47821,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.61955,"mean_force":4.38675,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49139,0.09639,0.03711]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.49619,0.11915,0.0094],"force_p95":0.61089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55292,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49061,0.17919,0.17037]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.19927,0.29748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":44.0,"contact_point_centroid":[0.49725,0.11866,0.0094],"force_p95":0.60321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61227,"mean_force":0.5436,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48653,0.15704,0.03643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.49602,0.11999,0.00941],"force_p95":0.59684,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59878,"mean_force":0.54311,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48461,0.15937,0.04411]}],"total_contact_groups":15},"final_pose_error":0.174,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49602,-0.02358,0.02412],"final_tcp_position":[0.49409,0.0465,0.13243],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":126.40955,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11947,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1996,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52313,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48315,0.16005,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":58.0,"n_steps_budget":600.0,"object_pos_end":[0.49607,0.11907,0.03384],"object_pos_start":[0.49601,0.11947,0.03385],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.1996,"object_z_max":0.03386,"peak_contact_force":0.58978,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":58.0,"raw_peak_contact_force":0.59878,"tcp_end":[0.48732,0.15888,0.03861],"tcp_start":[0.48315,0.16005,0.04931],"tcp_to_object_dist_end":0.04105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":44.0,"n_steps_budget":600.0,"object_pos_end":[0.49602,0.11947,0.03384],"object_pos_start":[0.49607,0.11907,0.03384],"object_to_goal_dist_end":0.19961,"object_to_goal_dist_start":0.1992,"object_z_max":0.03385,"peak_contact_force":23.24252,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":45.0,"raw_peak_contact_force":23.24252,"tcp_end":[0.48613,0.15514,0.03474],"tcp_start":[0.48732,0.15888,0.03861],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50782,0.00177,0.04],"object_pos_start":[0.49602,0.11947,0.03384],"object_to_goal_dist_end":0.08214,"object_to_goal_dist_start":0.19961,"object_z_max":0.04053,"peak_contact_force":67.20705,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2403.0,"raw_peak_contact_force":126.40955,"tcp_end":[0.49593,0.03563,0.03727],"tcp_start":[0.48613,0.15514,0.03474],"tcp_to_object_dist_end":0.03599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,-0.02358,0.02412],"object_pos_start":[0.50782,0.00177,0.04],"object_to_goal_dist_end":0.05875,"object_to_goal_dist_start":0.08214,"object_z_max":0.04075,"peak_contact_force":0.54915,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1049.0,"raw_peak_contact_force":50.23643,"tcp_end":[0.49409,0.0465,0.13243],"tcp_start":[0.49593,0.03563,0.03727],"tcp_to_object_dist_end":0.12902,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```