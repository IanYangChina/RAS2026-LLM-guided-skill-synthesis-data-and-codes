## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.2771 | 0.00 | ❌ rejected |
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3569 | 0.72 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | -0.0271 | 0.37 | ❌ rejected |
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3579 | 0.72 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0324 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.277) — your mutation base

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

- **Composite score**: -0.277
- **task_score** (E): 0.000
- **fitness_score**: 0.163  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1942 |
| approach_1 | 1.00 | 1.00 | 0.0380 |
| contact_1 | 0.00 | 1.00 | 0.0375 |
| push_1 | 0.00 | 1.00 | 0.0013 |
| retract_1 | 1.00 | 1.00 | 0.0946 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.502, 0.115, 0.127) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.553 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.502, 0.115, 0.127)→(0.499, 0.127, 0.092) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.546 | 0.611 |
| contact_1 | contact | 0.00 / step_budget | (0.499, 0.127, 0.092)→(0.497, 0.092, 0.080) | (0.501, 0.099, 0.034)→(0.502, 0.113, 0.027) | 0.180→0.194 | 1.00 / 1.000 | 0.518 | 1.366 |
| push_1 | push | 0.00 / guard_failure | (0.510, 0.077, 0.048)→(0.509, 0.077, 0.046) | (0.502, 0.113, 0.027)→(0.502, 0.113, 0.027) | 0.194→0.194 | 1.00 / 2.333 | 839.392 | 1081.138 |
| retract_1 | retract | 1.00 / step_budget | (0.509, 0.077, 0.046)→(0.507, 0.081, 0.141) | (0.502, 0.113, 0.027)→(0.499, 0.204, 0.018) | 0.194→0.285 | 1.00 / 1.000 | 0.374 | 453.036 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.278
- phase_breakdown.reach_object_score: 0.926
- phase_breakdown.push_through_channel_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.167
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.274
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61111,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00984,"align_1.lateral_offset_y":0.00999,"approach_1.speed":0.04635,"push_1.push_depth":0.07143,"push_1.push_x_offset":-0.00051,"retract_1.retract_height":0.15137,"retract_1.speed":0.06818},"optimized_scores":{"best_composite_score":-0.27429,"best_fitness_score":0.16571,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51,0.05238,0.05825],"force_p95":473.64294,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":512.90605,"mean_force":211.85303,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51054,0.04179,0.05746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.50433,0.06667,0.00937],"force_p95":114.69477,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":511.79659,"mean_force":29.28796,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5069,0.04965,0.07146]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.52761,0.07857,0.05803],"force_p95":372.92991,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":465.20604,"mean_force":98.85335,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49647,0.05051,0.02825]},{"body_a":"peg","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.49685,0.09396,0.069],"force_p95":206.88036,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":219.06338,"mean_force":46.22897,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49711,0.05013,0.02941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4741,0.10962,0.05243],"force_p95":85.96714,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":217.03684,"mean_force":22.92623,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50206,0.05101,0.05846]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.49927,0.06128,0.03206],"force_p95":48.24823,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.39746,"mean_force":14.78107,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49786,0.04968,0.0299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":267.0,"contact_point_centroid":[0.49867,0.1065,0.00974],"force_p95":2.75576,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.95839,"mean_force":1.68488,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5053,0.05029,0.10495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":662.0,"contact_point_centroid":[0.50309,0.06745,0.00935],"force_p95":0.55494,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55964,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50373,0.14092,0.20973]},{"body_a":"peg","body_b":"world","contact_count":227.0,"contact_point_centroid":[0.49363,0.14054,-0.00012],"force_p95":0.64944,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24163,"mean_force":0.48808,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50724,0.05261,0.11165]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52519,0.11138,0.03625],"force_p95":1.0072,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16221,"mean_force":0.6476,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50701,0.04666,0.14552]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50297,0.06771,0.00938],"force_p95":0.55045,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55083,"mean_force":0.54663,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50522,0.08985,0.11041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":494.0,"contact_point_centroid":[0.50302,0.06746,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55079,"mean_force":0.54665,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49918,0.07649,0.08433]}],"total_contact_groups":12},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5011,0.12546,0.02717],"final_tcp_position":[0.50804,0.04543,0.18553],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":512.90605,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54748,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":662.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.50899,0.08423,0.12585],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":124.0,"n_steps_budget":630.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54578,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":124.0,"raw_peak_contact_force":0.55083,"subtask_id":"reach_object","tcp_end":[0.5019,0.09502,0.09318],"tcp_start":[0.50899,0.08423,0.12585],"tcp_to_object_dist_end":0.06549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":494.0,"n_steps_budget":600.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54361,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":494.0,"raw_peak_contact_force":0.55079,"tcp_end":[0.49935,0.05998,0.07983],"tcp_start":[0.5019,0.09502,0.09318],"tcp_to_object_dist_end":0.04679,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":22.0,"n_steps_budget":600.0,"object_pos_end":[0.50307,0.06741,0.03367],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":120.65233,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":25.0,"raw_peak_contact_force":512.90605,"subtask_id":"push_through_channel","tcp_end":[0.51059,0.04108,0.05341],"tcp_start":[0.51052,0.04145,0.05546],"tcp_to_object_dist_end":0.03376,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.5011,0.12546,0.02717],"object_pos_start":[0.50293,0.06867,0.03396],"object_to_goal_dist_end":0.20586,"object_to_goal_dist_start":0.14882,"object_z_max":0.04222,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":643.0,"raw_peak_contact_force":465.20604,"tcp_end":[0.50804,0.04543,0.18553],"tcp_start":[0.51059,0.04108,0.05341],"tcp_to_object_dist_end":0.17757,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18788,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00985,"align_1.lateral_offset_y":0.00994,"approach_1.speed":0.07559,"push_1.push_depth":0.19087,"push_1.push_x_offset":0.00223,"retract_1.retract_height":0.10599,"retract_1.speed":0.02897},"optimized_scores":{"best_composite_score":-0.28389,"best_fitness_score":0.15611,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52597,0.09108,0.0596],"force_p95":1357.97291,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1380.91698,"mean_force":1209.90404,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51558,0.08859,0.05991]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.51197,0.09895,0.05848],"force_p95":222.51689,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":256.0259,"mean_force":79.9538,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51488,0.08852,0.05638]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.48711,0.11678,0.00924],"force_p95":143.79204,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":255.11145,"mean_force":28.90617,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51087,0.09143,0.05343]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52604,0.09045,0.05979],"force_p95":176.49203,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.97622,"mean_force":61.80128,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51397,0.08912,0.05553]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51725,0.10005,0.05792],"force_p95":194.73193,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":198.02231,"mean_force":165.11851,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51564,0.08845,0.05919]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.50523,0.1113,0.00943],"force_p95":132.27935,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":197.66906,"mean_force":16.2067,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50932,0.09522,0.07212]},{"body_a":"peg","body_b":"world","contact_count":288.0,"contact_point_centroid":[0.48952,0.31175,-0.00183],"force_p95":2.01369,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.98123,"mean_force":0.71759,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51081,0.09597,0.10033]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.50359,0.11164,0.00938],"force_p95":0.61139,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55756,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50703,0.16199,0.20988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":487.0,"contact_point_centroid":[0.50367,0.11163,0.00942],"force_p95":0.58993,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64063,"mean_force":0.5427,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50074,0.12005,0.08411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.50368,0.1114,0.00945],"force_p95":0.59148,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62145,"mean_force":0.53985,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50986,0.13275,0.11108]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49987,0.19921,0.29883]}],"total_contact_groups":11},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49091,0.32733,0.01413],"final_tcp_position":[0.51259,0.09183,0.1443],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1380.91698,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11176,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5779,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":585.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.51536,0.12635,0.12732],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":130.0,"n_steps_budget":600.0,"object_pos_end":[0.50368,0.11176,0.03385],"object_pos_start":[0.50371,0.11176,0.03383],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19189,"object_z_max":0.034,"peak_contact_force":0.55987,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":130.0,"raw_peak_contact_force":0.62145,"subtask_id":"reach_object","tcp_end":[0.50434,0.1387,0.09307],"tcp_start":[0.51536,0.12635,0.12732],"tcp_to_object_dist_end":0.06507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":487.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.11174,0.03392],"object_pos_start":[0.50368,0.11176,0.03385],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.1919,"object_z_max":0.03401,"peak_contact_force":0.5448,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":487.0,"raw_peak_contact_force":0.64063,"tcp_end":[0.50012,0.10397,0.07973],"tcp_start":[0.50434,0.1387,0.09307],"tcp_to_object_dist_end":0.0466,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.1117,0.03385],"object_pos_start":[0.50371,0.11174,0.03392],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.19187,"object_z_max":0.03392,"peak_contact_force":1097.31891,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":1380.91698,"subtask_id":"push_through_channel","tcp_end":[0.51554,0.08823,0.0576],"tcp_start":[0.51562,0.08835,0.05856],"tcp_to_object_dist_end":0.03541,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.49091,0.32733,0.01413],"object_pos_start":[0.5035,0.1116,0.03369],"object_to_goal_dist_end":0.40825,"object_to_goal_dist_start":0.19174,"object_z_max":0.03666,"peak_contact_force":0.65501,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":309.0,"raw_peak_contact_force":256.0259,"tcp_end":[0.51259,0.09183,0.1443],"tcp_start":[0.51554,0.08823,0.0576],"tcp_to_object_dist_end":0.26995,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47692,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00225,"align_1.lateral_offset_y":0.01,"approach_1.speed":0.04579,"push_1.push_depth":0.06783,"push_1.push_x_offset":-0.00514,"retract_1.retract_height":0.084,"retract_1.speed":0.07025},"optimized_scores":{"best_composite_score":-0.27326,"best_fitness_score":0.16674,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54088,0.11976,0.05923],"force_p95":1344.65184,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1349.59052,"mean_force":1210.13786,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50326,0.1012,0.03034]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.53852,0.11944,0.05868],"force_p95":598.09585,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":637.8758,"mean_force":342.44112,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50029,0.10423,0.02864]},{"body_a":"peg","body_b":"world","contact_count":163.0,"contact_point_centroid":[0.49691,0.15495,-0.00156],"force_p95":1.10579,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.90546,"mean_force":0.63725,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49102,0.11677,0.08077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":534.0,"contact_point_centroid":[0.49626,0.11906,0.00942],"force_p95":0.61665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55481,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49007,0.16551,0.21036]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49945,0.19884,0.29759]},{"body_a":"peg","body_b":"world","contact_count":34.0,"contact_point_centroid":[0.49788,0.15716,-0.00203],"force_p95":0.77058,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77058,"mean_force":0.61008,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50444,0.102,0.06025]},{"body_a":"peg","body_b":"world","contact_count":211.0,"contact_point_centroid":[0.50059,0.15991,-0.00203],"force_p95":0.77044,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77049,"mean_force":0.60523,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4977,0.10994,0.05929]},{"body_a":"peg","body_b":"channel_base_body","contact_count":168.0,"contact_point_centroid":[0.49599,0.11906,0.00945],"force_p95":0.61191,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66044,"mean_force":0.54031,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48458,0.14096,0.11016]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.49627,0.1196,0.00949],"force_p95":0.57737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65219,"mean_force":0.52178,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4885,0.13368,0.08443]}],"total_contact_groups":9},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50369,0.16001,0.01404],"final_tcp_position":[0.49899,0.10489,0.09299],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1349.59052,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.1191,0.03394],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53274,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":558.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48214,0.13341,0.1287],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":168.0,"n_steps_budget":690.0,"object_pos_end":[0.49611,0.11903,0.03394],"object_pos_start":[0.49604,0.1191,0.03394],"object_to_goal_dist_end":0.19916,"object_to_goal_dist_start":0.19923,"object_z_max":0.03397,"peak_contact_force":0.5321,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":168.0,"raw_peak_contact_force":0.66044,"subtask_id":"reach_object","tcp_end":[0.4893,0.1469,0.0908],"tcp_start":[0.48214,0.13341,0.1287],"tcp_to_object_dist_end":0.06369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":498.0,"n_steps_budget":600.0,"object_pos_end":[0.49778,0.16005,0.01405],"object_pos_start":[0.49611,0.11903,0.03394],"object_to_goal_dist_end":0.24146,"object_to_goal_dist_start":0.19916,"object_z_max":0.03403,"peak_contact_force":0.46701,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":494.0,"raw_peak_contact_force":2.90546,"tcp_end":[0.492,0.11127,0.07977],"tcp_start":[0.4893,0.1469,0.0908],"tcp_to_object_dist_end":0.08205,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":34.0,"n_steps_budget":600.0,"object_pos_end":[0.49825,0.16,0.01405],"object_pos_start":[0.49778,0.16005,0.01405],"object_to_goal_dist_end":0.2414,"object_to_goal_dist_start":0.24146,"object_z_max":0.01406,"peak_contact_force":1300.2037,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":37.0,"raw_peak_contact_force":1349.59052,"subtask_id":"push_through_channel","tcp_end":[0.5022,0.10187,0.02847],"tcp_start":[0.50255,0.10155,0.0291],"tcp_to_object_dist_end":0.06002,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":750.0,"object_pos_end":[0.50369,0.16001,0.01404],"object_pos_start":[0.49828,0.16007,0.01405],"object_to_goal_dist_end":0.24144,"object_to_goal_dist_start":0.24147,"object_z_max":0.01405,"peak_contact_force":0.46699,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":220.0,"raw_peak_contact_force":637.8758,"tcp_end":[0.49899,0.10489,0.09299],"tcp_start":[0.5022,0.10187,0.02847],"tcp_to_object_dist_end":0.0964,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```