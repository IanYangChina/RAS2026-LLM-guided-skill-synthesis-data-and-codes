## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0499 | 0.44 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1430 | 0.32 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4106 | 0.13 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.2771 | 0.00 | ❌ rejected |
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3569 | 0.72 | ❌ rejected |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.050) — your mutation base

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

- **Composite score**: -0.050
- **task_score** (E): 0.440
- **fitness_score**: 0.357  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.233
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1658 |
| approach_1 | 1.00 | 1.00 | 0.1073 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.67 | 1.00 | 0.0501 |
| retract_1 | 1.00 | 1.00 | 0.1002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.502, 0.122, 0.156) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.517 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.502, 0.122, 0.156)→(0.498, 0.108, 0.050) | (0.501, 0.099, 0.034)→(0.502, 0.081, 0.040) | 0.180→0.162 | 1.00 / 2.000 | 10.475 | 15.201 |
| contact_1 | contact | 1.00 / force_exceeded | (0.498, 0.108, 0.050)→(0.498, 0.108, 0.050) | (0.502, 0.081, 0.040)→(0.502, 0.081, 0.040) | 0.162→0.161 | 1.00 / 2.000 | 29.000 | 29.000 |
| push_1 | push | 0.67 / time_limit | (0.498, 0.087, 0.048)→(0.497, 0.037, 0.043) | (0.502, 0.081, 0.040)→(0.505, 0.023, 0.025) | 0.161→0.104 | 1.00 / 2.333 | 4.547 | 37.608 |
| retract_1 | retract | 1.00 / step_budget | (0.497, 0.037, 0.043)→(0.502, 0.058, 0.140) | (0.504, 0.023, 0.025)→(0.498, 0.024, 0.025) | 0.104→0.105 | 1.00 / 1.333 | 0.559 | 43.786 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.471
- alignment_error: None
- force_efficiency: 0.011
- terminal_score: 0.428
- phase_score: 0.285
- phase_breakdown.reach_object_score: 0.163
- phase_breakdown.push_channel_score: 0.337

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.386
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.455
- **Median Q (composite search score)**: -0.048
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.286


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12602,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00181,"align_1.lateral_offset_y":0.00443,"approach_1.arc_height":0.05391,"approach_1.speed":0.02974,"contact_1.force_threshold":10.01255,"contact_1.speed":0.01786,"push_1.push_depth":0.11199,"push_1.push_duration":2.9589,"push_1.speed":0.03988,"retract_1.arc_height":0.06745,"retract_1.speed":0.02874},"optimized_scores":{"best_composite_score":-0.05384,"best_fitness_score":0.38616,"best_task_score":0.45492},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.50506,0.0271,0.00949],"force_p95":29.30078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.4701,"mean_force":19.072,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4984,0.04556,0.04504]},{"body_a":"attachment","body_b":"peg","contact_count":843.0,"contact_point_centroid":[0.50328,0.0367,0.0452],"force_p95":28.49794,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.02493,"mean_force":18.47986,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4984,0.04556,0.04504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":154.0,"contact_point_centroid":[0.50053,0.00708,0.00895],"force_p95":40.17628,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.41296,"mean_force":5.37767,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50086,0.04011,0.08541]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.50579,0.00813,0.04411],"force_p95":41.25903,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.64664,"mean_force":24.74756,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49923,0.0157,0.04379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5039,0.04397,0.00983],"force_p95":27.93574,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.93574,"mean_force":27.93574,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49991,0.07619,0.0504]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50161,0.06444,0.05044],"force_p95":27.69157,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.69157,"mean_force":27.69157,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49991,0.07619,0.0504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":581.0,"contact_point_centroid":[0.50328,0.06362,0.00946],"force_p95":12.90737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.5673,"mean_force":2.12563,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49954,0.10524,0.09765]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.50131,0.07188,0.05161],"force_p95":15.48116,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.21743,"mean_force":12.11485,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49969,0.08361,0.05157]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":114.0,"contact_point_centroid":[0.52502,0.02593,0.02667],"force_p95":8.72184,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.08271,"mean_force":4.46412,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49917,0.03113,0.04432]},{"body_a":"peg","body_b":"channel_base_body","contact_count":345.0,"contact_point_centroid":[0.50309,0.06753,0.00931],"force_p95":0.62657,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57157,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50039,0.14115,0.22295]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47493,-0.02803,0.02479],"force_p95":0.63053,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65782,"mean_force":0.43243,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50161,0.05594,0.10372]}],"total_contact_groups":11},"final_pose_error":0.04913,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49862,-0.00533,0.02444],"final_tcp_position":[0.50452,0.03335,0.14582],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":51.4701,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54268,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":345.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_object","tcp_end":[0.50193,0.08614,0.15368],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.04978,0.03991],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.12983,"object_to_goal_dist_start":0.14759,"object_z_max":0.03989,"peak_contact_force":11.19186,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":658.0,"raw_peak_contact_force":16.5673,"subtask_id":"reach_object","tcp_end":[0.49991,0.07619,0.0504],"tcp_start":[0.50193,0.08614,0.15368],"tcp_to_object_dist_end":0.02868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.50375,0.04958,0.03992],"object_pos_start":[0.50373,0.04978,0.03991],"object_to_goal_dist_end":0.12964,"object_to_goal_dist_start":0.12983,"object_z_max":0.03991,"peak_contact_force":27.93574,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":27.93574,"subtask_id":"reach_object","tcp_end":[0.49991,0.07607,0.05037],"tcp_start":[0.49991,0.07619,0.0504],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,-0.00594,0.02518],"object_pos_start":[0.50375,0.04958,0.03992],"object_to_goal_dist_end":0.07578,"object_to_goal_dist_start":0.12964,"object_z_max":0.04042,"peak_contact_force":2.2603,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1800.0,"raw_peak_contact_force":51.4701,"subtask_id":"push_channel","tcp_end":[0.49958,0.01259,0.04278],"tcp_start":[0.4996,0.01264,0.04281],"tcp_to_object_dist_end":0.0264,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.49862,-0.00533,0.02444],"object_pos_start":[0.50615,-0.00602,0.02517],"object_to_goal_dist_end":0.07629,"object_to_goal_dist_start":0.0757,"object_z_max":0.03524,"peak_contact_force":0.63169,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":192.0,"raw_peak_contact_force":42.41296,"tcp_end":[0.50452,0.03335,0.14582],"tcp_start":[0.49958,0.01259,0.04278],"tcp_to_object_dist_end":0.12752,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21774,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.01171,"align_1.lateral_offset_y":0.01118,"approach_1.arc_height":0.05502,"approach_1.speed":0.04138,"contact_1.force_threshold":12.33134,"contact_1.speed":0.01793,"push_1.push_depth":0.14414,"push_1.push_duration":3.41814,"push_1.speed":0.04698,"retract_1.arc_height":0.07435,"retract_1.speed":0.01983},"optimized_scores":{"best_composite_score":-0.04789,"best_fitness_score":0.34211,"best_task_score":0.42793},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":149.0,"contact_point_centroid":[0.50248,0.0502,0.00896],"force_p95":46.3143,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.4542,"mean_force":9.1466,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50016,0.06465,0.07771]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.50382,0.03991,0.04384],"force_p95":48.24963,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.81585,"mean_force":29.63931,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49962,0.04269,0.04362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50554,0.0666,0.00903],"force_p95":27.22317,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.40428,"mean_force":15.66327,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.499,0.07935,0.04446]},{"body_a":"attachment","body_b":"peg","contact_count":810.0,"contact_point_centroid":[0.50404,0.07781,0.04495],"force_p95":26.625,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.53402,"mean_force":18.5921,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4991,0.08237,0.04484]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50503,0.08853,0.00983],"force_p95":30.41793,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.41793,"mean_force":30.41793,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50059,0.12046,0.05026]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50244,0.10873,0.05032],"force_p95":30.18083,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.18083,"mean_force":30.18083,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50059,0.12046,0.05026]},{"body_a":"peg","body_b":"channel_base_body","contact_count":559.0,"contact_point_centroid":[0.50406,0.10802,0.00949],"force_p95":12.28596,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.01923,"mean_force":2.09256,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50688,0.15145,0.09868]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52506,0.05729,0.024],"force_p95":11.59769,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.98279,"mean_force":4.90208,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50135,0.05766,0.09846]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.50224,0.11663,0.05131],"force_p95":13.30087,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.65132,"mean_force":11.4355,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50054,0.12841,0.05127]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":96.0,"contact_point_centroid":[0.52501,0.07409,0.02636],"force_p95":10.15214,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.80076,"mean_force":4.7061,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49946,0.07573,0.04463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":283.0,"contact_point_centroid":[0.50336,0.11163,0.00935],"force_p95":0.68941,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57121,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50806,0.1642,0.22288]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.4749,0.02046,0.03646],"force_p95":0.98539,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04344,"mean_force":0.6096,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49958,0.07405,0.07303]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49926,0.19839,0.29773]}],"total_contact_groups":13},"final_pose_error":0.0497,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50308,0.03636,0.02424],"final_tcp_position":[0.50238,0.06725,0.13705],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":49.4542,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":305.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.1118,0.03394],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.50832,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":299.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_object","tcp_end":[0.51645,0.13249,0.15623],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.50472,0.09404,0.03996],"object_pos_start":[0.50372,0.1118,0.03394],"object_to_goal_dist_end":0.17411,"object_to_goal_dist_start":0.19193,"object_z_max":0.03994,"peak_contact_force":11.32251,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":636.0,"raw_peak_contact_force":14.01923,"subtask_id":"reach_object","tcp_end":[0.50059,0.12046,0.05026],"tcp_start":[0.51645,0.13249,0.15623],"tcp_to_object_dist_end":0.02865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.50476,0.09385,0.03998],"object_pos_start":[0.50472,0.09404,0.03996],"object_to_goal_dist_end":0.17391,"object_to_goal_dist_start":0.17411,"object_z_max":0.03996,"peak_contact_force":30.41793,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":30.41793,"subtask_id":"reach_object","tcp_end":[0.50059,0.12033,0.05023],"tcp_start":[0.50059,0.12046,0.05026],"tcp_to_object_dist_end":0.0287,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50398,0.03412,0.02407],"object_pos_start":[0.50476,0.09385,0.03998],"object_to_goal_dist_end":0.11529,"object_to_goal_dist_start":0.17391,"object_z_max":0.04035,"peak_contact_force":9.56168,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1906.0,"raw_peak_contact_force":32.40428,"subtask_id":"push_channel","tcp_end":[0.49997,0.03813,0.04193],"tcp_start":[0.50059,0.12033,0.05023],"tcp_to_object_dist_end":0.01874,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.03636,0.02424],"object_pos_start":[0.50398,0.03412,0.02407],"object_to_goal_dist_end":0.11747,"object_to_goal_dist_start":0.11529,"object_z_max":0.03368,"peak_contact_force":0.56472,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":214.0,"raw_peak_contact_force":49.4542,"tcp_end":[0.50238,0.06725,0.13705],"tcp_start":[0.49997,0.03813,0.04193],"tcp_to_object_dist_end":0.11696,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13208,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00318,"align_1.lateral_offset_y":0.01982,"approach_1.arc_height":0.05327,"approach_1.speed":0.03777,"contact_1.force_threshold":13.17942,"contact_1.speed":0.03051,"push_1.push_depth":0.17,"push_1.push_duration":3.63079,"push_1.speed":0.02648,"retract_1.arc_height":0.05002,"retract_1.speed":0.03881},"optimized_scores":{"best_composite_score":-0.04797,"best_fitness_score":0.34203,"best_task_score":0.43833},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":132.0,"contact_point_centroid":[0.49752,0.04769,0.00866],"force_p95":17.60202,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.48962,"mean_force":2.74162,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.495,0.07777,0.08362]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50307,0.05756,0.0439],"force_p95":38.09784,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.27831,"mean_force":13.9674,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49231,0.06041,0.04399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49985,0.07602,0.00959],"force_p95":25.83909,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.94968,"mean_force":16.17647,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49109,0.09509,0.04476]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49839,0.09491,0.00986],"force_p95":28.64657,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.64657,"mean_force":28.64657,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49282,0.12726,0.04953]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.49724,0.08677,0.04487],"force_p95":25.36609,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.493,"mean_force":15.70672,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49109,0.09509,0.04476]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49503,0.11558,0.04959],"force_p95":28.42152,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.42152,"mean_force":28.42152,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49282,0.12726,0.04953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.49661,0.11567,0.00948],"force_p95":11.26245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.01756,"mean_force":2.00451,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48972,0.16379,0.09648]},{"body_a":"attachment","body_b":"peg","contact_count":98.0,"contact_point_centroid":[0.49467,0.12495,0.05027],"force_p95":12.93391,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.79989,"mean_force":9.74998,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4926,0.13666,0.04985]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47491,0.01536,0.02433],"force_p95":9.64533,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.73112,"mean_force":3.12687,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49817,0.08428,0.11921]},{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.49635,0.11916,0.00939],"force_p95":0.64903,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56868,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49353,0.17131,0.22303]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49879,0.19781,0.29566]}],"total_contact_groups":11},"final_pose_error":0.04974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49361,0.03971,0.02483],"final_tcp_position":[0.50006,0.07297,0.13825],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":39.48962,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11911,0.03421],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19924,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49854,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":283.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_object","tcp_end":[0.48864,0.14669,0.15803],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.49778,0.10059,0.03999],"object_pos_start":[0.49601,0.11911,0.03421],"object_to_goal_dist_end":0.1806,"object_to_goal_dist_start":0.19924,"object_z_max":0.03997,"peak_contact_force":8.91099,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":741.0,"raw_peak_contact_force":15.01756,"subtask_id":"reach_object","tcp_end":[0.49282,0.12726,0.04953],"tcp_start":[0.48864,0.14669,0.15803],"tcp_to_object_dist_end":0.02876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49784,0.10042,0.04001],"object_pos_start":[0.49778,0.10059,0.03999],"object_to_goal_dist_end":0.18043,"object_to_goal_dist_start":0.1806,"object_z_max":0.03999,"peak_contact_force":28.64657,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":28.64657,"subtask_id":"reach_object","tcp_end":[0.49283,0.12714,0.04952],"tcp_start":[0.49282,0.12726,0.04953],"tcp_to_object_dist_end":0.0288,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50334,0.04044,0.02574],"object_pos_start":[0.49784,0.10042,0.04001],"object_to_goal_dist_end":0.12133,"object_to_goal_dist_start":0.18043,"object_z_max":0.04047,"peak_contact_force":1.81923,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2000.0,"raw_peak_contact_force":28.94968,"subtask_id":"push_channel","tcp_end":[0.4926,0.05964,0.04358],"tcp_start":[0.49283,0.12714,0.04952],"tcp_to_object_dist_end":0.02833,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.49361,0.03971,0.02483],"object_pos_start":[0.50334,0.04044,0.02574],"object_to_goal_dist_end":0.12084,"object_to_goal_dist_start":0.12133,"object_z_max":0.02954,"peak_contact_force":0.47973,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":163.0,"raw_peak_contact_force":39.48962,"tcp_end":[0.50006,0.07297,0.13825],"tcp_start":[0.4926,0.05964,0.04358],"tcp_to_object_dist_end":0.11837,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```