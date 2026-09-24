## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.2523 | 0.02 | ❌ rejected |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.3075 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | time_limit | pose_tolerance | 8 | -0.1029 | 0.00 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0974 | 0.12 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0986 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
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

## Current Skill (Q=-0.252) — your mutation base

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
- id: approach_1
  type: approach
  generator: linear_cartesian
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
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.252
- **task_score** (E): 0.017
- **fitness_score**: 0.188  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1902 |
| descend_1 | 1.00 | 1.00 | 0.0661 |
| contact_1 | 0.00 | 1.00 | 0.0197 |
| push_1 | 0.00 | 1.00 | 0.0000 |
| retract_1 | 1.00 | 1.00 | 0.0888 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.093, 0.145) | (0.512, 0.067, 0.040)→(0.502, 0.066, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.550 | 4.034 |
| descend_1 | descend | 1.00 / step_budget | (0.508, 0.093, 0.145)→(0.500, 0.087, 0.083) | (0.502, 0.066, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.545 | 0.558 |
| contact_1 | contact | 0.00 / step_budget | (0.500, 0.087, 0.083)→(0.498, 0.073, 0.070) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.542 | 0.554 |
| push_1 | push | 0.00 / guard_failure | (0.496, 0.049, 0.063)→(0.496, 0.049, 0.063) | (0.502, 0.067, 0.034)→(0.503, 0.059, 0.034) | 0.147→0.139 | 1.00 / 2.000 | 45.582 | 45.785 |
| retract_1 | retract | 1.00 / step_budget | (0.496, 0.049, 0.063)→(0.493, 0.049, 0.152) | (0.503, 0.059, 0.034)→(0.503, 0.059, 0.034) | 0.139→0.139 | 1.00 / 1.333 | 0.545 | 45.275 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.048
- alignment_error: None
- force_efficiency: 0.082
- terminal_score: 0.018
- phase_score: 0.314
- phase_breakdown.push_through_score: 0.050
- phase_breakdown.approach_peg_score: 0.822
- phase_breakdown.reach_contact_score: 0.600

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.196
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.019
- **Median Q (composite search score)**: -0.251
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.262


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10072,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.11398,"contact_1.contact_force":6.41462,"contact_1.speed":0.03931,"descend_1.speed":0.05056,"push_1.duration":2.15959,"push_1.push_speed":0.02625,"retract_1.speed":0.086},"optimized_scores":{"best_composite_score":-0.25114,"best_fitness_score":0.18886,"best_task_score":0.01935},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.50962,0.04818,0.00955],"force_p95":38.71722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.44414,"mean_force":18.95293,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49927,0.0566,0.06405]},{"body_a":"attachment","body_b":"peg","contact_count":313.0,"contact_point_centroid":[0.51004,0.05396,0.05877],"force_p95":38.95481,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.09255,"mean_force":25.0625,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49914,0.05374,0.06332]},{"body_a":"peg","body_b":"channel_base_body","contact_count":658.0,"contact_point_centroid":[0.50599,0.05521,0.00941],"force_p95":0.67988,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.93176,"mean_force":0.6577,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49675,0.04485,0.10665]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.50997,0.04544,0.05919],"force_p95":13.41778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.50631,"mean_force":2.70415,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49909,0.04504,0.06376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":601.0,"contact_point_centroid":[0.50581,0.06297,0.00936],"force_p95":0.56305,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56908,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51183,0.1427,0.21785]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49989,0.19773,0.29656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50598,0.06295,0.00938],"force_p95":0.55234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54652,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51516,0.08673,0.11483]},{"body_a":"peg","body_b":"channel_base_body","contact_count":287.0,"contact_point_centroid":[0.50588,0.06313,0.00938],"force_p95":0.55119,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55424,"mean_force":0.54658,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50278,0.07476,0.07407]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":68.0,"contact_point_centroid":[0.52504,0.05541,0.05885],"force_p95":0.01336,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.11144,"mean_force":0.00617,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49679,0.04486,0.10504]}],"total_contact_groups":9},"final_pose_error":0.0109,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50683,0.05541,0.03392],"final_tcp_position":[0.49687,0.04488,0.1522],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":46.44414,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":629.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55246,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":635.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52452,0.0898,0.14479],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":200.0,"n_steps_budget":930.0,"object_pos_end":[0.50595,0.06295,0.03381],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54416,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":200.0,"raw_peak_contact_force":0.55501,"subtask_id":"reach_contact","tcp_end":[0.5063,0.08378,0.08374],"tcp_start":[0.52452,0.0898,0.14479],"tcp_to_object_dist_end":0.0541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":287.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.50595,0.06295,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54183,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":287.0,"raw_peak_contact_force":0.55424,"subtask_id":"reach_contact","tcp_end":[0.50206,0.06923,0.06993],"tcp_start":[0.5063,0.08378,0.08374],"tcp_to_object_dist_end":0.03688,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.50678,0.05512,0.03436],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.1354,"object_to_goal_dist_start":0.14324,"object_z_max":0.03443,"peak_contact_force":46.18893,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":738.0,"raw_peak_contact_force":46.44414,"subtask_id":"push_through","tcp_end":[0.50002,0.04519,0.06264],"tcp_start":[0.50002,0.04522,0.06265],"tcp_to_object_dist_end":0.03073,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":658.0,"n_steps_budget":750.0,"object_pos_end":[0.50683,0.05541,0.03392],"object_pos_start":[0.50678,0.05509,0.03433],"object_to_goal_dist_end":0.13572,"object_to_goal_dist_start":0.13538,"object_z_max":0.03514,"peak_contact_force":0.54466,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":754.0,"raw_peak_contact_force":45.93176,"tcp_end":[0.49687,0.04488,0.1522],"tcp_start":[0.50002,0.04519,0.06264],"tcp_to_object_dist_end":0.11917,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85326,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05918,"contact_1.contact_force":4.48806,"contact_1.speed":0.03434,"descend_1.speed":0.03399,"push_1.duration":3.75278,"push_1.push_speed":0.01855,"retract_1.speed":0.10411},"optimized_scores":{"best_composite_score":-0.26134,"best_fitness_score":0.17866,"best_task_score":0.01308},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":409.0,"contact_point_centroid":[0.50989,0.04252,0.00954],"force_p95":37.33827,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.03075,"mean_force":18.20625,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49958,0.05123,0.06408]},{"body_a":"attachment","body_b":"peg","contact_count":299.0,"contact_point_centroid":[0.51032,0.04868,0.05877],"force_p95":37.45866,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.68131,"mean_force":24.22722,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49942,0.04854,0.06333]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50625,0.04931,0.0094],"force_p95":0.59012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.6604,"mean_force":0.69968,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49704,0.04046,0.10613]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.51042,0.04071,0.05903],"force_p95":19.32428,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.23742,"mean_force":4.41428,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49954,0.04065,0.06357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":696.0,"contact_point_centroid":[0.50591,0.05665,0.00936],"force_p95":0.60057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56944,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51509,0.13957,0.21766]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4999,0.19775,0.29664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":264.0,"contact_point_centroid":[0.5062,0.05666,0.00938],"force_p95":0.55183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5575,"mean_force":0.54649,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50363,0.06857,0.07408]},{"body_a":"peg","body_b":"channel_base_body","contact_count":203.0,"contact_point_centroid":[0.5061,0.0566,0.00938],"force_p95":0.55195,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55475,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51939,0.0805,0.11459]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52518,0.0495,0.05897],"force_p95":0.02546,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.06185,"mean_force":0.00449,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49807,0.04053,0.06818]}],"total_contact_groups":9},"final_pose_error":0.01196,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5068,0.04943,0.03378],"final_tcp_position":[0.49709,0.04048,0.15112],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":45.03075,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,0.05663,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54302,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":733.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53101,0.08356,0.14423],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,0.05664,0.03381],"object_pos_start":[0.50617,0.05663,0.0338],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.13691,"object_z_max":0.03381,"peak_contact_force":0.54205,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":203.0,"raw_peak_contact_force":0.55475,"subtask_id":"reach_contact","tcp_end":[0.50781,0.07752,0.08353],"tcp_start":[0.53101,0.08356,0.14423],"tcp_to_object_dist_end":0.05395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":264.0,"n_steps_budget":600.0,"object_pos_end":[0.5062,0.0566,0.03382],"object_pos_start":[0.50617,0.05664,0.03381],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13692,"object_z_max":0.03383,"peak_contact_force":0.54479,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":264.0,"raw_peak_contact_force":0.5575,"subtask_id":"reach_contact","tcp_end":[0.50243,0.06299,0.06993],"tcp_start":[0.50781,0.07752,0.08353],"tcp_to_object_dist_end":0.03686,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,0.04946,0.03418],"object_pos_start":[0.5062,0.0566,0.03382],"object_to_goal_dist_end":0.12977,"object_to_goal_dist_start":0.13688,"object_z_max":0.03442,"peak_contact_force":44.88228,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":708.0,"raw_peak_contact_force":45.03075,"subtask_id":"push_through","tcp_end":[0.50021,0.04076,0.06265],"tcp_start":[0.50022,0.04079,0.06267],"tcp_to_object_dist_end":0.03051,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.5068,0.04943,0.03378],"object_pos_start":[0.50686,0.04944,0.03414],"object_to_goal_dist_end":0.12976,"object_to_goal_dist_start":0.12975,"object_z_max":0.03479,"peak_contact_force":0.54612,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":580.0,"raw_peak_contact_force":44.6604,"tcp_end":[0.49709,0.04048,0.15112],"tcp_start":[0.50021,0.04076,0.06265],"tcp_to_object_dist_end":0.11808,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23276,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.12413,"contact_1.contact_force":8.478,"contact_1.speed":0.0362,"descend_1.speed":0.13234,"push_1.duration":0.64984,"push_1.push_speed":0.01601,"retract_1.speed":0.14936},"optimized_scores":{"best_composite_score":-0.24432,"best_fitness_score":0.19568,"best_task_score":0.01804},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":410.0,"contact_point_centroid":[0.49838,0.06518,0.00955],"force_p95":38.03969,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.87862,"mean_force":19.09775,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48736,0.07341,0.06424]},{"body_a":"attachment","body_b":"peg","contact_count":305.0,"contact_point_centroid":[0.49821,0.07103,0.05879],"force_p95":38.10786,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.53443,"mean_force":25.00801,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48743,0.0706,0.06356]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.49477,0.07207,0.00943],"force_p95":0.58467,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.23257,"mean_force":0.6912,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48581,0.06171,0.106]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.49892,0.06268,0.05902],"force_p95":10.62424,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.80809,"mean_force":3.67827,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48816,0.06197,0.06375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":519.0,"contact_point_centroid":[0.4941,0.07995,0.00937],"force_p95":0.59417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.57116,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48349,0.15145,0.21924]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49883,0.19777,0.29624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.49382,0.07989,0.00938],"force_p95":0.55738,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5642,"mean_force":0.5466,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47682,0.10325,0.11332]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49386,0.07993,0.00938],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55133,"mean_force":0.54667,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48682,0.09182,0.07276]}],"total_contact_groups":8},"final_pose_error":0.0121,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4949,0.07224,0.03404],"final_tcp_position":[0.48584,0.06173,0.15125],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":45.87862,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":547.0,"n_steps_budget":960.0,"object_pos_end":[0.49382,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55323,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":554.0,"raw_peak_contact_force":3.77147,"subtask_id":"approach_peg","tcp_end":[0.46947,0.10657,0.14715],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":250.0,"n_steps_budget":600.0,"object_pos_end":[0.49383,0.07994,0.03378],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":0.54765,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":250.0,"raw_peak_contact_force":0.5642,"subtask_id":"reach_contact","tcp_end":[0.48646,0.10026,0.08044],"tcp_start":[0.46947,0.10657,0.14715],"tcp_to_object_dist_end":0.05142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.49383,0.07996,0.03378],"object_pos_start":[0.49383,0.07994,0.03378],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":0.54038,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":397.0,"raw_peak_contact_force":0.55133,"subtask_id":"reach_contact","tcp_end":[0.48911,0.08602,0.06969],"tcp_start":[0.48646,0.10026,0.08044],"tcp_to_object_dist_end":0.03673,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.49522,0.07209,0.03447],"object_pos_start":[0.49383,0.07996,0.03378],"object_to_goal_dist_end":0.15226,"object_to_goal_dist_start":0.1602,"object_z_max":0.03447,"peak_contact_force":45.67507,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":715.0,"raw_peak_contact_force":45.87862,"subtask_id":"push_through","tcp_end":[0.4889,0.06213,0.06295],"tcp_start":[0.4889,0.06216,0.06297],"tcp_to_object_dist_end":0.03083,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":520.0,"n_steps_budget":600.0,"object_pos_end":[0.4949,0.07224,0.03404],"object_pos_start":[0.49521,0.07206,0.03444],"object_to_goal_dist_end":0.15245,"object_to_goal_dist_start":0.15224,"object_z_max":0.03492,"peak_contact_force":0.54424,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":541.0,"raw_peak_contact_force":45.23257,"tcp_end":[0.48584,0.06173,0.15125],"tcp_start":[0.4889,0.06213,0.06295],"tcp_to_object_dist_end":0.11803,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```