## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2591 | 0.08 | ❌ rejected |
| 8 | align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0157 | 0.00 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.1370 | 0.30 | ❌ rejected |
| 6 | align → approach → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2459 | 0.00 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.2272 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.08 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
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

## Current Skill (Q=-0.259) — your mutation base

```yaml
skill: peg_channel
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
  control: admittance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
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

- **Composite score**: -0.259
- **task_score** (E): 0.081
- **fitness_score**: 0.098  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1434 |
| approach_1 | 1.00 | 1.00 | 0.0820 |
| contact_1 | 0.67 | 1.00 | 0.0295 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.1302 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.106, 0.194) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.547 | 2.732 |
| approach_1 | approach | 1.00 / step_budget | (0.505, 0.106, 0.194)→(0.500, 0.080, 0.118) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.551 | 0.623 |
| contact_1 | contact | 0.67 / force_exceeded | (0.500, 0.080, 0.118)→(0.498, 0.077, 0.088) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.667 | 6.311 | 6.050 |
| push_1 | push | 0.00 / guard_failure | (0.498, 0.067, 0.085)→(0.498, 0.067, 0.085) | (0.502, 0.098, 0.034)→(0.503, 0.091, 0.037) | 0.178→0.171 | 1.00 / 2.667 | 43.370 | 85.561 |
| retract_1 | retract | 1.00 / step_budget | (0.498, 0.067, 0.085)→(0.496, 0.066, 0.216) | (0.503, 0.090, 0.037)→(0.504, 0.080, 0.031) | 0.170→0.160 | 1.00 / 1.000 | 0.570 | 124.969 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.276
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.173
- phase_score: 0.115
- phase_breakdown.reach_prepush_score: 0.362
- phase_breakdown.push_through_score: 0.009

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.138
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.173
- **Median Q (composite search score)**: -0.218
- **K-run variance**: 0.0117
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.302


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05732,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.13438,"approach_1.speed":0.04584,"contact_1.contact_force":11.3939,"contact_1.speed":0.02568,"push_1.force_limit":35.32303,"push_1.push_distance":0.14049,"push_1.speed":0.01762,"retract_1.speed":0.11131},"optimized_scores":{"best_composite_score":-0.40747,"best_fitness_score":0.08253,"best_task_score":0.06906},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.4745,0.11956,0.05697],"force_p95":179.10956,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.4855,"mean_force":110.79089,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49915,0.07904,0.07426]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.475,0.1196,0.05615],"force_p95":92.31809,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.5614,"mean_force":41.64246,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49912,0.07913,0.0743]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.525,0.11957,0.05935],"force_p95":44.27974,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.01461,"mean_force":8.52692,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49915,0.07894,0.07423]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.525,0.11965,0.05848],"force_p95":57.51447,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.49732,"mean_force":25.0129,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49912,0.07913,0.0743]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.50339,0.09945,0.00964],"force_p95":21.61444,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.08294,"mean_force":6.9281,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49965,0.08727,0.07581]},{"body_a":"peg","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.50364,0.1264,0.04494],"force_p95":21.93691,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.80857,"mean_force":10.74225,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49941,0.08633,0.07537]},{"body_a":"peg","body_b":"channel_base_body","contact_count":398.0,"contact_point_centroid":[0.50356,0.11172,0.00936],"force_p95":0.62005,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.564,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50253,0.15826,0.24432]},{"body_a":"peg","body_b":"channel_base_body","contact_count":384.0,"contact_point_centroid":[0.50538,0.09912,0.00946],"force_p95":0.60021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.00123,"mean_force":0.54581,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49735,0.07824,0.1377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":534.0,"contact_point_centroid":[0.50363,0.11154,0.00942],"force_p95":0.60044,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65978,"mean_force":0.54249,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49924,0.11163,0.15071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":239.0,"contact_point_centroid":[0.5037,0.11168,0.00942],"force_p95":0.59704,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63437,"mean_force":0.54277,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50004,0.09162,0.09721]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19899,0.29902]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50005,0.1154,0.06214],"force_p95":0.50729,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51197,"mean_force":0.46511,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49915,0.07897,0.07422]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52513,0.09978,0.0592],"force_p95":0.40083,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47685,"mean_force":0.12249,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49774,0.07914,0.08881]},{"body_a":"peg","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.50478,0.11938,0.05895],"force_p95":0.14775,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17524,"mean_force":0.04213,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49779,0.07921,0.08675]}],"total_contact_groups":14},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50583,0.10073,0.0341],"final_tcp_position":[0.49743,0.07805,0.20453],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":184.4855,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":420.0,"n_steps_budget":690.0,"object_pos_end":[0.50371,0.11174,0.0339],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5767,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":414.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_prepush","tcp_end":[0.50642,0.11938,0.19523],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11179,0.03385],"object_pos_start":[0.50371,0.11174,0.0339],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19188,"object_z_max":0.03398,"peak_contact_force":0.57292,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":534.0,"raw_peak_contact_force":0.65978,"subtask_id":"reach_prepush","tcp_end":[0.50136,0.09337,0.11783],"tcp_start":[0.50642,0.11938,0.19523],"tcp_to_object_dist_end":0.08601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11173,0.03395],"object_pos_start":[0.50374,0.11179,0.03385],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19193,"object_z_max":0.03397,"peak_contact_force":0.54689,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":239.0,"raw_peak_contact_force":0.63437,"subtask_id":"reach_prepush","tcp_end":[0.50038,0.09063,0.07723],"tcp_start":[0.50136,0.09337,0.11783],"tcp_to_object_dist_end":0.04826,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":44.0,"n_steps_budget":1000.0,"object_pos_end":[0.50332,0.10146,0.03615],"object_pos_start":[0.50373,0.11173,0.03395],"object_to_goal_dist_end":0.18154,"object_to_goal_dist_start":0.19186,"object_z_max":0.03615,"peak_contact_force":39.93935,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":56.0,"raw_peak_contact_force":101.5614,"subtask_id":"push_through","tcp_end":[0.49915,0.07873,0.07421],"tcp_start":[0.49915,0.07883,0.07425],"tcp_to_object_dist_end":0.04453,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":384.0,"n_steps_budget":840.0,"object_pos_end":[0.50583,0.10073,0.0341],"object_pos_start":[0.50333,0.10033,0.03614],"object_to_goal_dist_end":0.18092,"object_to_goal_dist_start":0.18041,"object_z_max":0.03634,"peak_contact_force":0.54961,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":424.0,"raw_peak_contact_force":184.4855,"subtask_id":"push_through","tcp_end":[0.49743,0.07805,0.20453],"tcp_start":[0.49915,0.07873,0.07421],"tcp_to_object_dist_end":0.17215,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20359,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.11887,"approach_1.speed":0.03915,"contact_1.contact_force":7.86325,"contact_1.speed":0.02251,"push_1.force_limit":28.52834,"push_1.push_distance":0.11856,"push_1.speed":0.03436,"retract_1.speed":0.07805},"optimized_scores":{"best_composite_score":-0.15187,"best_fitness_score":0.13813,"best_task_score":0.17297},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.4742,0.11964,0.05897],"force_p95":141.0303,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.6624,"mean_force":108.26827,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49077,0.07921,0.08412]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.475,0.11972,0.05846],"force_p95":97.96929,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.712,"mean_force":56.46107,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4907,0.07939,0.08407]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.49846,0.10441,0.0096],"force_p95":21.56032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.98651,"mean_force":4.07494,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49088,0.08996,0.08654]},{"body_a":"peg","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.49631,0.12728,0.05568],"force_p95":26.32553,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.74042,"mean_force":13.85472,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4909,0.0869,0.08596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":166.0,"contact_point_centroid":[0.49603,0.11923,0.00946],"force_p95":0.58227,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.96083,"mean_force":0.63856,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49135,0.09888,0.10317]},{"body_a":"peg","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49569,0.13921,0.05805],"force_p95":16.66204,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.66204,"mean_force":16.66204,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4916,0.09825,0.08965]},{"body_a":"peg","body_b":"channel_base_body","contact_count":386.0,"contact_point_centroid":[0.49932,0.08404,0.00884],"force_p95":0.86665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.53888,"mean_force":0.62311,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.489,0.07846,0.1479]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47492,0.09554,0.02411],"force_p95":6.21305,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.445,"mean_force":1.67604,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4887,0.07809,0.15196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":372.0,"contact_point_centroid":[0.49632,0.11904,0.00942],"force_p95":0.61818,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56007,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49151,0.16157,0.24444]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.06047,0.03887],"force_p95":1.729,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74334,"mean_force":1.59995,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48864,0.07813,0.13122]},{"body_a":"peg","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.49671,0.11912,0.05395],"force_p95":1.29783,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.52686,"mean_force":0.38171,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49078,0.07895,0.08398]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49936,0.19843,0.29791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":591.0,"contact_point_centroid":[0.49605,0.11909,0.00945],"force_p95":0.60197,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65499,"mean_force":0.54016,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48321,0.11888,0.15135]}],"total_contact_groups":13},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50052,0.07479,0.02414],"final_tcp_position":[0.48911,0.0783,0.2142],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":141.6624,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":750.0,"object_pos_end":[0.49604,0.11899,0.03411],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51421,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":396.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_prepush","tcp_end":[0.485,0.12641,0.19626],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11922,0.03393],"object_pos_start":[0.49604,0.11899,0.03411],"object_to_goal_dist_end":0.19935,"object_to_goal_dist_start":0.19912,"object_z_max":0.03421,"peak_contact_force":0.52999,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":591.0,"raw_peak_contact_force":0.65499,"subtask_id":"reach_prepush","tcp_end":[0.49238,0.10018,0.11716],"tcp_start":[0.485,0.12641,0.19626],"tcp_to_object_dist_end":0.08547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.1201,0.03391],"object_pos_start":[0.49605,0.11922,0.03393],"object_to_goal_dist_end":0.20023,"object_to_goal_dist_start":0.19935,"object_z_max":0.03405,"peak_contact_force":16.96083,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":167.0,"raw_peak_contact_force":16.96083,"subtask_id":"reach_prepush","tcp_end":[0.49161,0.09824,0.0895],"tcp_start":[0.49238,0.10018,0.11716],"tcp_to_object_dist_end":0.05989,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.4986,0.10707,0.04013],"object_pos_start":[0.49604,0.1201,0.03391],"object_to_goal_dist_end":0.18708,"object_to_goal_dist_start":0.20023,"object_z_max":0.04017,"peak_contact_force":42.76061,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":76.0,"raw_peak_contact_force":107.712,"subtask_id":"push_through","tcp_end":[0.49077,0.079,0.084],"tcp_start":[0.49075,0.0791,0.08403],"tcp_to_object_dist_end":0.05267,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50052,0.07479,0.02414],"object_pos_start":[0.49872,0.1064,0.04019],"object_to_goal_dist_end":0.1556,"object_to_goal_dist_start":0.18641,"object_z_max":0.04079,"peak_contact_force":0.61318,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":414.0,"raw_peak_contact_force":141.6624,"subtask_id":"push_through","tcp_end":[0.48911,0.0783,0.2142],"tcp_start":[0.49077,0.079,0.084],"tcp_to_object_dist_end":0.19043,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6381,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.15517,"approach_1.speed":0.06488,"contact_1.contact_force":1.08892,"contact_1.speed":0.02624,"push_1.force_limit":30.52916,"push_1.push_distance":0.12347,"push_1.speed":0.04699,"retract_1.speed":0.11282},"optimized_scores":{"best_composite_score":-0.2181,"best_fitness_score":0.0719,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52506,0.12,0.0599],"force_p95":40.68288,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.76008,"mean_force":11.42683,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50286,0.04329,0.09806]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52504,0.12,0.05993],"force_p95":44.87868,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.40912,"mean_force":33.36367,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50309,0.04338,0.09827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":526.0,"contact_point_centroid":[0.50568,0.063,0.00936],"force_p95":0.56756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57228,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51222,0.13247,0.24152]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50003,0.19685,0.29688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":374.0,"contact_point_centroid":[0.50603,0.06284,0.00938],"force_p95":0.55273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54655,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50123,0.04276,0.16196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":453.0,"contact_point_centroid":[0.50608,0.06301,0.00938],"force_p95":0.55145,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54659,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50983,0.06305,0.1465]},{"body_a":"peg","body_b":"channel_base_body","contact_count":113.0,"contact_point_centroid":[0.50602,0.06258,0.00938],"force_p95":0.55132,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55424,"mean_force":0.54655,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50392,0.04416,0.1084]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49875,0.07131,0.00939],"force_p95":0.55259,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55399,"mean_force":0.54704,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50309,0.04338,0.09827]}],"total_contact_groups":8},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50592,0.063,0.03382],"final_tcp_position":[0.50143,0.04291,0.22815],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":48.76008,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":554.0,"n_steps_budget":720.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54861,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":560.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_prepush","tcp_end":[0.52492,0.07149,0.19195],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":453.0,"n_steps_budget":840.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":0.55074,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":453.0,"raw_peak_contact_force":0.55501,"subtask_id":"reach_prepush","tcp_end":[0.5055,0.04523,0.11818],"tcp_start":[0.52492,0.07149,0.19195],"tcp_to_object_dist_end":0.08622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06296,0.03381],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":1.42563,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":113.0,"raw_peak_contact_force":0.55424,"subtask_id":"reach_prepush","tcp_end":[0.50317,0.04343,0.09845],"tcp_start":[0.5055,0.04523,0.11818],"tcp_to_object_dist_end":0.06759,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06302,0.03381],"object_pos_start":[0.50594,0.06296,0.03381],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14322,"object_z_max":0.03381,"peak_contact_force":47.40912,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":47.40912,"subtask_id":"push_through","tcp_end":[0.50298,0.04333,0.09807],"tcp_start":[0.50301,0.04333,0.09812],"tcp_to_object_dist_end":0.06728,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":374.0,"n_steps_budget":840.0,"object_pos_end":[0.50592,0.063,0.03382],"object_pos_start":[0.50603,0.06301,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14327,"object_z_max":0.03382,"peak_contact_force":0.54806,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":379.0,"raw_peak_contact_force":48.76008,"subtask_id":"push_through","tcp_end":[0.50143,0.04291,0.22815],"tcp_start":[0.50298,0.04333,0.09807],"tcp_to_object_dist_end":0.19542,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```