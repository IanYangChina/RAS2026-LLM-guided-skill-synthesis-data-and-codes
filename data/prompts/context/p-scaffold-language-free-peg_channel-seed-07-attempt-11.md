## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3421 | 0.62 | ❌ rejected |
| 10 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3443 | 0.62 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2591 | 0.08 | ❌ rejected |
| 8 | align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0157 | 0.00 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.1370 | 0.30 | ❌ rejected |

**Proposal policy**: task_score is 0.62 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.342) — your mutation base

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

- **Composite score**: 0.342
- **task_score** (E): 0.619
- **fitness_score**: 0.482  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2543 |
| approach_1 | 1.00 | 1.00 | 0.0065 |
| contact_1 | 1.00 | 1.00 | 0.0062 |
| push_1 | 1.00 | 1.00 | 0.1224 |
| retract_1 | 0.00 | 1.00 | 0.1098 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.504, 0.142, 0.054) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.333 | 106.254 | 119.349 |
| approach_1 | approach | 1.00 / step_budget | (0.504, 0.142, 0.054)→(0.505, 0.141, 0.049) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.333 | 80.389 | 90.277 |
| contact_1 | contact | 1.00 / force_exceeded | (0.505, 0.141, 0.049)→(0.504, 0.137, 0.044) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 38.967 | 38.967 |
| push_1 | push | 1.00 / time_limit | (0.504, 0.137, 0.044)→(0.506, 0.015, 0.046) | (0.502, 0.098, 0.034)→(0.507, -0.003, 0.037) | 0.178→0.077 | 1.00 / 2.333 | 125.337 | 182.886 |
| retract_1 | retract | 0.00 / step_budget | (0.506, 0.015, 0.046)→(0.499, 0.005, 0.154) | (0.507, -0.003, 0.037)→(0.502, -0.012, 0.031) | 0.077→0.070 | 1.00 / 1.333 | 3.073 | 68.425 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.994
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.994
- phase_score: 0.491
- phase_breakdown.contact_score: 0.732
- phase_breakdown.push_score: 0.286
- phase_breakdown.approach_score: 0.865

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.692
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.994
- **Median Q (composite search score)**: 0.465
- **K-run variance**: 0.0568
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.327


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30409,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00301,"approach_1.speed":0.08894,"contact_1.contact_force":3.07556,"contact_1.speed":0.02581,"push_1.push_distance":0.14389,"retract_1.speed":0.02833},"optimized_scores":{"best_composite_score":0.55205,"best_fitness_score":0.69205,"best_task_score":0.99402},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":718.0,"contact_point_centroid":[0.54479,0.07,0.05998],"force_p95":114.7071,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.19628,"mean_force":92.10941,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49915,0.07429,0.03621]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54291,-0.02307,0.05999],"force_p95":49.47162,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.78622,"mean_force":44.42014,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4982,-0.01772,0.03696]},{"body_a":"peg","body_b":"channel_base_body","contact_count":757.0,"contact_point_centroid":[0.50083,0.03275,0.00966],"force_p95":15.23705,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.03958,"mean_force":2.22321,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49914,0.07234,0.03624]},{"body_a":"attachment","body_b":"peg","contact_count":396.0,"contact_point_centroid":[0.50121,0.0439,0.03998],"force_p95":18.79078,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.86761,"mean_force":3.46482,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49908,0.05557,0.03646]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":192.0,"contact_point_centroid":[0.47479,0.05676,0.03334],"force_p95":1.39735,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.74431,"mean_force":0.54285,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49943,0.08706,0.03642]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55026,0.12,0.05999],"force_p95":12.74104,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12.74104,"mean_force":12.74104,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49975,0.14201,0.03419]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":174.0,"contact_point_centroid":[0.52521,-0.00716,0.0248],"force_p95":3.0867,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.27958,"mean_force":0.75144,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49899,0.0216,0.03693]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50621,-0.04804,0.00941],"force_p95":0.5734,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.59122,"mean_force":0.54407,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.495,-0.01404,0.08439]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.50521,-0.02917,0.05813],"force_p95":0.68545,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.11805,"mean_force":0.21975,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49629,-0.01741,0.04022]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":129.0,"contact_point_centroid":[0.50316,0.11166,0.00939],"force_p95":0.5982,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62959,"mean_force":0.54595,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50082,0.14653,0.0375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.50512,0.11115,0.00939],"force_p95":0.58591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5936,"mean_force":0.54414,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50458,0.15277,0.04656]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19944,0.29874]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":380.0,"contact_point_centroid":[0.52502,-0.04729,0.05413],"force_p95":0.27654,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36539,"mean_force":0.03975,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49507,-0.01443,0.07911]}],"total_contact_groups":14},"final_pose_error":0.16858,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50698,-0.04727,0.03378],"final_tcp_position":[0.49552,-0.01085,0.13183],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":130.19628,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":24.0,"n_steps_budget":600.0,"object_pos_end":[0.50368,0.11176,0.0338],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19187,"object_z_max":0.03382,"peak_contact_force":0.52478,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.5936,"tcp_end":[0.50369,0.1524,0.04354],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.04179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":129.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.11178,0.03379],"object_pos_start":[0.50368,0.11176,0.0338],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.1919,"object_z_max":0.03383,"peak_contact_force":12.74104,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":130.0,"raw_peak_contact_force":12.74104,"tcp_end":[0.49975,0.14197,0.03417],"tcp_start":[0.50369,0.1524,0.04354],"tcp_to_object_dist_end":0.03045,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,-0.04655,0.03596],"object_pos_start":[0.50371,0.11178,0.03379],"object_to_goal_dist_end":0.03425,"object_to_goal_dist_start":0.19191,"object_z_max":0.03779,"peak_contact_force":15.1705,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2237.0,"raw_peak_contact_force":130.19628,"tcp_end":[0.49825,-0.01745,0.03699],"tcp_start":[0.49975,0.14197,0.03417],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,-0.04727,0.03378],"object_pos_start":[0.50616,-0.04655,0.03596],"object_to_goal_dist_end":0.03404,"object_to_goal_dist_start":0.03425,"object_z_max":0.03621,"peak_contact_force":0.01057,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1394.0,"raw_peak_contact_force":49.78622,"tcp_end":[0.49552,-0.01085,0.13183],"tcp_start":[0.49825,-0.01745,0.03699],"tcp_to_object_dist_end":0.10522,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35152,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.0036,"approach_1.speed":0.05426,"contact_1.contact_force":9.76997,"contact_1.speed":0.02557,"push_1.push_distance":0.12827,"retract_1.speed":0.03259},"optimized_scores":{"best_composite_score":0.46542,"best_fitness_score":0.60542,"best_task_score":0.86299},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":622.0,"contact_point_centroid":[0.53745,0.09112,0.05999],"force_p95":120.38184,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.3879,"mean_force":95.66361,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48978,0.0996,0.0366]},{"body_a":"attachment","body_b":"peg","contact_count":792.0,"contact_point_centroid":[0.49925,0.06618,0.03659],"force_p95":98.87671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.13062,"mean_force":57.6971,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49161,0.07419,0.03716]},{"body_a":"peg","body_b":"channel_base_body","contact_count":954.0,"contact_point_centroid":[0.50642,0.0545,0.00966],"force_p95":67.66067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.99678,"mean_force":30.66997,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49071,0.08647,0.03683]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":759.0,"contact_point_centroid":[0.52571,0.05133,0.02864],"force_p95":61.02149,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.27397,"mean_force":39.56042,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49187,0.07092,0.03725]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5412,0.00339,0.05999],"force_p95":46.80617,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.1378,"mean_force":43.42977,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4962,0.00737,0.03726]},{"body_a":"peg","body_b":"link7","contact_count":260.0,"contact_point_centroid":[0.52019,0.07138,0.06784],"force_p95":30.0415,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.55886,"mean_force":11.32734,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49031,0.09602,0.03722]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54211,0.12,0.05997],"force_p95":30.13514,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.13514,"mean_force":30.13514,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48592,0.15621,0.03475]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.5017,-0.00154,0.03596],"force_p95":10.38059,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.13158,"mean_force":3.06742,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49522,0.00719,0.03868]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.4994,-0.04823,0.00824],"force_p95":0.74786,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.52226,"mean_force":0.72176,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49342,0.00589,0.08523]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.5253,-0.00994,0.02164],"force_p95":9.03681,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.06898,"mean_force":4.43604,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49597,0.00725,0.03751]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.475,-0.07438,0.02419],"force_p95":8.27728,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.27974,"mean_force":4.33019,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49423,0.00465,0.12949]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.49619,0.11915,0.0094],"force_p95":0.61089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55292,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49061,0.17919,0.17037]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.19927,0.29748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.49486,0.11811,0.0094],"force_p95":0.60511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61227,"mean_force":0.54642,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48627,0.15763,0.03604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":60.0,"contact_point_centroid":[0.49662,0.11999,0.00941],"force_p95":0.59669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59878,"mean_force":0.54283,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48431,0.15937,0.04348]}],"total_contact_groups":15},"final_pose_error":0.16734,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4941,-0.05052,0.0243],"final_tcp_position":[0.49428,0.00456,0.13282],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":130.3879,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11947,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1996,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52313,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48315,0.16005,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":60.0,"n_steps_budget":600.0,"object_pos_end":[0.49605,0.11901,0.03384],"object_pos_start":[0.49601,0.11947,0.03385],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.1996,"object_z_max":0.03386,"peak_contact_force":0.51833,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":60.0,"raw_peak_contact_force":0.59878,"tcp_end":[0.48689,0.15887,0.03758],"tcp_start":[0.48315,0.16005,0.04931],"tcp_to_object_dist_end":0.04107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":31.0,"n_steps_budget":600.0,"object_pos_end":[0.49607,0.11942,0.03383],"object_pos_start":[0.49605,0.11901,0.03384],"object_to_goal_dist_end":0.19956,"object_to_goal_dist_start":0.19914,"object_z_max":0.03384,"peak_contact_force":30.13514,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":32.0,"raw_peak_contact_force":30.13514,"tcp_end":[0.48591,0.15614,0.03469],"tcp_start":[0.48689,0.15887,0.03758],"tcp_to_object_dist_end":0.0381,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.50807,-0.02608,0.03987],"object_pos_start":[0.49607,0.11942,0.03383],"object_to_goal_dist_end":0.05452,"object_to_goal_dist_start":0.19956,"object_z_max":0.04042,"peak_contact_force":77.20406,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3387.0,"raw_peak_contact_force":130.3879,"tcp_end":[0.49623,0.00755,0.03729],"tcp_start":[0.48591,0.15614,0.03469],"tcp_to_object_dist_end":0.03575,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4941,-0.05052,0.0243],"object_pos_start":[0.50807,-0.02608,0.03987],"object_to_goal_dist_end":0.03392,"object_to_goal_dist_start":0.05452,"object_z_max":0.04068,"peak_contact_force":8.66712,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1049.0,"raw_peak_contact_force":47.1378,"tcp_end":[0.49428,0.00456,0.13282],"tcp_start":[0.49623,0.00755,0.03729],"tcp_to_object_dist_end":0.1217,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76821,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00703,"approach_1.speed":0.05856,"contact_1.contact_force":9.22722,"contact_1.speed":0.00503,"push_1.push_distance":0.19998,"retract_1.speed":0.08479},"optimized_scores":{"best_composite_score":0.00895,"best_fitness_score":0.14895,"best_task_score":0.0002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":114.0,"contact_point_centroid":[0.53488,0.11266,0.05979],"force_p95":345.12221,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":353.73417,"mean_force":317.18085,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52374,0.11275,0.06404]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":959.0,"contact_point_centroid":[0.53418,0.07124,0.05996],"force_p95":278.39025,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.07437,"mean_force":206.39929,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5232,0.07158,0.06474]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":426.0,"contact_point_centroid":[0.53649,0.11267,0.05993],"force_p95":266.86038,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.63949,"mean_force":246.60197,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52542,0.11271,0.0645]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.53319,0.05291,0.05996],"force_p95":102.38632,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.35218,"mean_force":75.68081,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5223,0.05395,0.06485]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53694,0.11245,0.05993],"force_p95":74.02593,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.02593,"mean_force":74.02593,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52585,0.1125,0.06447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":876.0,"contact_point_centroid":[0.5058,0.06299,0.00937],"force_p95":0.55584,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56201,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51235,0.14948,0.1623]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49981,0.19843,0.29603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50609,0.06292,0.00938],"force_p95":0.55274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52542,0.11271,0.0645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50596,0.06304,0.00939],"force_p95":0.55121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55493,"mean_force":0.5464,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52323,0.07234,0.06474]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50605,0.06293,0.00939],"force_p95":0.55082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55491,"mean_force":0.54625,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51237,0.0374,0.13088]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48833,0.05973,0.00938],"force_p95":0.54874,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54874,"mean_force":0.54874,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52585,0.1125,0.06447]}],"total_contact_groups":11},"final_pose_error":0.10387,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50592,0.06286,0.03388],"final_tcp_position":[0.50629,0.02192,0.19866],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":353.73417,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":317.66646,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1024.0,"raw_peak_contact_force":353.73417,"tcp_end":[0.52444,0.11271,0.06453],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.06298,0.03381],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":240.12447,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":852.0,"raw_peak_contact_force":269.63949,"tcp_end":[0.52585,0.1125,0.06447],"tcp_start":[0.52444,0.11271,0.06453],"tcp_to_object_dist_end":0.06156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.063,0.03381],"object_pos_start":[0.50593,0.06298,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":74.02593,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":74.02593,"tcp_end":[0.52586,0.1125,0.06447],"tcp_start":[0.52585,0.1125,0.06447],"tcp_to_object_dist_end":0.06153,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50608,0.06303,0.03386],"object_pos_start":[0.50594,0.063,0.03381],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14326,"object_z_max":0.03386,"peak_contact_force":283.63686,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1959.0,"raw_peak_contact_force":288.07437,"tcp_end":[0.52231,0.05391,0.06481],"tcp_start":[0.52586,0.1125,0.06447],"tcp_to_object_dist_end":0.03612,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.06286,0.03388],"object_pos_start":[0.50608,0.06303,0.03386],"object_to_goal_dist_end":0.14312,"object_to_goal_dist_start":0.14329,"object_z_max":0.03388,"peak_contact_force":0.5414,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":108.35218,"tcp_end":[0.50629,0.02192,0.19866],"tcp_start":[0.52231,0.05391,0.06481],"tcp_to_object_dist_end":0.1698,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```