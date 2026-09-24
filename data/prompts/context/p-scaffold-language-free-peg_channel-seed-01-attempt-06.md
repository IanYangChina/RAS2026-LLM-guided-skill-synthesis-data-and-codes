## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2156 | 0.60 | ❌ rejected |
| 5 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0486 | 0.00 | ❌ rejected |
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.1950 | 0.59 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1858 | 0.16 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1872 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.60 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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

## Current Skill (Q=0.216) — your mutation base

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
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
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
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.216
- **task_score** (E): 0.603
- **fitness_score**: 0.606  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2578 |
| approach_1 | 1.00 | 1.00 | 0.0161 |
| contact_1 | 1.00 | 1.00 | 0.0109 |
| push_1 | 1.00 | 1.00 | 0.1561 |
| retract_1 | 0.00 | 1.00 | 0.1662 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.484, 0.125, 0.055) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.667 | 221.293 | 237.641 |
| approach_1 | approach | 1.00 / step_budget | (0.484, 0.125, 0.055)→(0.491, 0.121, 0.042) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.549 | 210.115 |
| contact_1 | contact | 1.00 / step_budget | (0.491, 0.121, 0.042)→(0.494, 0.113, 0.036) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.159 | 1.00 / 2.000 | 162.815 | 189.610 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.113, 0.036)→(0.498, -0.043, 0.037) | (0.497, 0.079, 0.034)→(0.495, -0.073, 0.035) | 0.159→0.019 | 1.00 / 3.333 | 81.004 | 123.899 |
| retract_1 | retract | 0.00 / step_budget | (0.498, -0.043, 0.037)→(0.497, 0.008, 0.194) | (0.495, -0.073, 0.035)→(0.495, -0.067, 0.034) | 0.019→0.018 | 1.00 / 1.000 | 0.547 | 72.262 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.991
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.985
- phase_score: 0.495
- phase_breakdown.push_score: 0.262
- phase_breakdown.approach_score: 0.898
- phase_breakdown.contact_score: 0.794

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.691
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.985
- **Median Q (composite search score)**: 0.250
- **K-run variance**: 0.0076
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.325


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50595,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00186,"approach_1.approach_height":0.15448,"approach_1.speed":0.029,"contact_1.speed":0.02479,"push_1.push_distance":0.17307,"push_1.push_speed":0.09773},"optimized_scores":{"best_composite_score":0.3011,"best_fitness_score":0.6911,"best_task_score":0.98468},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":743.0,"contact_point_centroid":[0.54352,0.06907,0.05998],"force_p95":117.99117,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.71134,"mean_force":98.64647,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49784,0.0732,0.03634]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":283.0,"contact_point_centroid":[0.54773,0.12,0.05998],"force_p95":128.3165,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.33072,"mean_force":80.04581,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49551,0.14659,0.0343]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54319,-0.01826,0.05999],"force_p95":70.28622,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.10934,"mean_force":62.324,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49847,-0.01321,0.03693]},{"body_a":"attachment","body_b":"peg","contact_count":418.0,"contact_point_centroid":[0.50265,0.06205,0.04294],"force_p95":25.59713,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.86461,"mean_force":4.41313,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49785,0.07362,0.03636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":736.0,"contact_point_centroid":[0.50429,0.02958,0.00969],"force_p95":19.23643,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.90269,"mean_force":2.86068,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49785,0.07181,0.03634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50076,0.11464,0.00945],"force_p95":0.65217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.27037,"mean_force":0.63327,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49521,0.1481,0.0352]},{"body_a":"attachment","body_b":"peg","contact_count":46.0,"contact_point_centroid":[0.50067,0.13372,0.04272],"force_p95":2.79028,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.98287,"mean_force":1.04541,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49668,0.14564,0.03421]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":393.0,"contact_point_centroid":[0.52523,0.05289,0.03469],"force_p95":4.31694,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.10365,"mean_force":0.84486,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49773,0.08232,0.03634]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.4747,-0.04,0.04631],"force_p95":4.37558,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.71895,"mean_force":0.75855,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49852,-0.00973,0.03696]},{"body_a":"peg","body_b":"channel_base_body","contact_count":755.0,"contact_point_centroid":[0.50092,0.11599,0.00939],"force_p95":0.61661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55392,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4977,0.17803,0.1717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49592,-0.04268,0.00942],"force_p95":0.55541,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74466,"mean_force":0.54474,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49572,0.0102,0.11568]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50075,0.11655,0.00946],"force_p95":0.5787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58479,"mean_force":0.54094,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49639,0.15694,0.04619]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49737,-0.02463,0.03872],"force_p95":0.32417,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34026,"mean_force":0.21562,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49745,-0.01264,0.03858]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47495,-0.0439,0.05908],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49848,-0.01305,0.03693]}],"total_contact_groups":14},"final_pose_error":0.10253,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49582,-0.04248,0.03383],"final_tcp_position":[0.49665,0.01923,0.19934],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":131.71134,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11605,0.03394],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54801,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":755.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49706,0.15726,0.04892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11601,0.03391],"object_pos_start":[0.50095,0.11605,0.03394],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19615,"object_z_max":0.03394,"peak_contact_force":0.54838,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.58479,"tcp_end":[0.49634,0.15677,0.04264],"tcp_start":[0.49706,0.15726,0.04892],"tcp_to_object_dist_end":0.04193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.50145,0.11511,0.03456],"object_pos_start":[0.50092,0.11601,0.03391],"object_to_goal_dist_end":0.1952,"object_to_goal_dist_start":0.19611,"object_z_max":0.03456,"peak_contact_force":103.05412,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":747.0,"raw_peak_contact_force":131.33072,"tcp_end":[0.49714,0.14524,0.03415],"tcp_start":[0.49634,0.15677,0.04264],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49424,-0.04313,0.03512],"object_pos_start":[0.50145,0.11511,0.03456],"object_to_goal_dist_end":0.03764,"object_to_goal_dist_start":0.1952,"object_z_max":0.0378,"peak_contact_force":72.73748,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2319.0,"raw_peak_contact_force":131.71134,"tcp_end":[0.49848,-0.01305,0.03693],"tcp_start":[0.49714,0.14524,0.03415],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49582,-0.04248,0.03383],"object_pos_start":[0.49424,-0.04313,0.03512],"object_to_goal_dist_end":0.03825,"object_to_goal_dist_start":0.03764,"object_z_max":0.03512,"peak_contact_force":0.54371,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1009.0,"raw_peak_contact_force":71.10934,"tcp_end":[0.49665,0.01923,0.19934],"tcp_start":[0.49848,-0.01305,0.03693],"tcp_to_object_dist_end":0.17664,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61047,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0027,"approach_1.approach_height":0.24708,"approach_1.speed":0.08416,"contact_1.speed":0.0244,"push_1.push_distance":0.14233,"push_1.push_speed":0.09916},"optimized_scores":{"best_composite_score":0.24993,"best_fitness_score":0.63993,"best_task_score":0.54985},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4749,0.12,0.0598],"force_p95":341.5277,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.62701,"mean_force":311.80708,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47984,0.111,0.05723]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47497,0.11792,0.05994],"force_p95":283.70214,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.29523,"mean_force":209.67753,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48303,0.11067,0.05591]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":435.0,"contact_point_centroid":[0.53504,0.1035,0.05995],"force_p95":212.11864,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":219.23522,"mean_force":172.06937,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48951,0.10214,0.03793]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":716.0,"contact_point_centroid":[0.54121,0.0231,0.05999],"force_p95":112.69041,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.17373,"mean_force":92.43282,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49589,0.02462,0.03782]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5439,-0.05557,0.05998],"force_p95":78.57199,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.59466,"mean_force":73.82105,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49889,-0.05936,0.03733]},{"body_a":"peg","body_b":"channel_base_body","contact_count":62.0,"contact_point_centroid":[0.49576,-0.10152,0.04162],"force_p95":60.79688,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.2963,"mean_force":32.51044,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49857,-0.05578,0.0374]},{"body_a":"attachment","body_b":"peg","contact_count":329.0,"contact_point_centroid":[0.49636,-0.00084,0.0388],"force_p95":43.7983,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.23412,"mean_force":8.26839,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49636,0.01086,0.03778]},{"body_a":"peg","body_b":"channel_base_body","contact_count":77.0,"contact_point_centroid":[0.49367,-0.10126,0.05672],"force_p95":23.52211,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.56138,"mean_force":9.45679,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4969,-0.05472,0.04102]},{"body_a":"attachment","body_b":"peg","contact_count":90.0,"contact_point_centroid":[0.49592,-0.06534,0.04289],"force_p95":23.56655,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.23555,"mean_force":8.1875,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49667,-0.05362,0.04241]},{"body_a":"peg","body_b":"channel_base_body","contact_count":753.0,"contact_point_centroid":[0.49721,-0.01185,0.00953],"force_p95":5.30264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.72619,"mean_force":1.47586,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49583,0.02644,0.03784]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":314.0,"contact_point_centroid":[0.47485,0.01124,0.03104],"force_p95":0.93593,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.55699,"mean_force":0.4266,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49524,0.0419,0.03787]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52541,-0.04222,0.05815],"force_p95":5.86545,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.36241,"mean_force":1.10163,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49729,-0.01069,0.03784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":919.0,"contact_point_centroid":[0.49532,-0.07768,0.0094],"force_p95":0.56257,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.2578,"mean_force":0.55843,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49583,-0.01851,0.11703]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47494,-0.08209,0.06],"force_p95":2.02224,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.49411,"mean_force":1.24294,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4957,-0.05079,0.045]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.49531,0.0638,0.00938],"force_p95":0.56258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55591,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48773,0.15105,0.1656]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49933,0.19869,0.29695]}],"total_contact_groups":18},"final_pose_error":0.10806,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49536,-0.07713,0.03385],"final_tcp_position":[0.4967,0.00229,0.19201],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":355.62701,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49535,0.06392,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":334.70153,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":908.0,"raw_peak_contact_force":355.62701,"tcp_end":[0.481,0.11081,0.05671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":95.0,"n_steps_budget":600.0,"object_pos_end":[0.49532,0.06402,0.034],"object_pos_start":[0.49535,0.06392,0.03399],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14412,"object_z_max":0.034,"peak_contact_force":0.55289,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":125.0,"raw_peak_contact_force":307.29523,"tcp_end":[0.48856,0.10593,0.04095],"tcp_start":[0.481,0.11081,0.05671],"tcp_to_object_dist_end":0.04301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":465.0,"n_steps_budget":630.0,"object_pos_end":[0.4952,0.06416,0.03403],"object_pos_start":[0.49532,0.06402,0.034],"object_to_goal_dist_end":0.14436,"object_to_goal_dist_start":0.14422,"object_z_max":0.03403,"peak_contact_force":205.83251,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":900.0,"raw_peak_contact_force":219.23522,"tcp_end":[0.49314,0.09923,0.03759],"tcp_start":[0.48856,0.10593,0.04095],"tcp_to_object_dist_end":0.03532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49548,-0.08823,0.03515],"object_pos_start":[0.4952,0.06416,0.03403],"object_to_goal_dist_end":0.01057,"object_to_goal_dist_start":0.14436,"object_z_max":0.03804,"peak_contact_force":69.46339,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2188.0,"raw_peak_contact_force":122.17373,"tcp_end":[0.49889,-0.05926,0.03733],"tcp_start":[0.49314,0.09923,0.03759],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49536,-0.07713,0.03385],"object_pos_start":[0.49548,-0.08823,0.03515],"object_to_goal_dist_end":0.00821,"object_to_goal_dist_start":0.01057,"object_z_max":0.03831,"peak_contact_force":0.5464,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1098.0,"raw_peak_contact_force":78.59466,"tcp_end":[0.4967,0.00229,0.19201],"tcp_start":[0.49889,-0.05926,0.03733],"tcp_to_object_dist_end":0.17698,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62791,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00418,"approach_1.approach_height":0.19414,"approach_1.speed":0.05258,"contact_1.speed":0.02855,"push_1.push_distance":0.15228,"push_1.push_speed":0.09475},"optimized_scores":{"best_composite_score":0.09562,"best_fitness_score":0.48562,"best_task_score":0.27448},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":106.0,"contact_point_centroid":[0.47492,0.11854,0.05985],"force_p95":346.92903,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.37637,"mean_force":313.68239,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47019,0.10819,0.06243]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":69.0,"contact_point_centroid":[0.47497,0.11524,0.05995],"force_p95":296.63938,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.46444,"mean_force":213.26593,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48035,0.10608,0.0574]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":401.0,"contact_point_centroid":[0.53365,0.0977,0.05996],"force_p95":212.3218,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.26527,"mean_force":164.13477,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48832,0.09664,0.03752]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":709.0,"contact_point_centroid":[0.53978,0.02202,0.05999],"force_p95":109.49295,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.81111,"mean_force":89.69069,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49469,0.02373,0.03734]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5424,-0.0541,0.05998],"force_p95":66.69474,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.08215,"mean_force":58.68238,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49764,-0.058,0.03684]},{"body_a":"attachment","body_b":"peg","contact_count":430.0,"contact_point_centroid":[0.49896,-0.00166,0.04147],"force_p95":30.93391,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.05445,"mean_force":7.05278,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49524,0.00986,0.03733]},{"body_a":"peg","body_b":"channel_base_body","contact_count":52.0,"contact_point_centroid":[0.49445,-0.10116,0.04145],"force_p95":49.97622,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.03981,"mean_force":26.69422,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49743,-0.05503,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":705.0,"contact_point_centroid":[0.50089,-0.01289,0.0097],"force_p95":17.85257,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.99551,"mean_force":2.72459,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49459,0.02655,0.03736]},{"body_a":"peg","body_b":"channel_base_body","contact_count":56.0,"contact_point_centroid":[0.49323,-0.10125,0.05205],"force_p95":24.33999,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.60188,"mean_force":12.02777,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49608,-0.05471,0.03952]},{"body_a":"attachment","body_b":"peg","contact_count":47.0,"contact_point_centroid":[0.49538,-0.06695,0.03957],"force_p95":19.10912,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.45579,"mean_force":9.88164,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49628,-0.05525,0.03906]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":160.0,"contact_point_centroid":[0.52516,-0.00904,0.02301],"force_p95":10.40037,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.53845,"mean_force":1.79024,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49508,0.01806,0.03747]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":38.0,"contact_point_centroid":[0.47482,-0.08417,0.05999],"force_p95":13.27287,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.30315,"mean_force":9.03189,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49591,-0.05447,0.03956]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":132.0,"contact_point_centroid":[0.47478,-0.03083,0.02362],"force_p95":2.66325,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.1479,"mean_force":0.60431,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4954,-0.00046,0.03715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":854.0,"contact_point_centroid":[0.49433,0.05892,0.00937],"force_p95":0.55492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56328,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48064,0.14718,0.16216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49899,0.19829,0.29587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":947.0,"contact_point_centroid":[0.49524,-0.0813,0.00939],"force_p95":0.5624,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89149,"mean_force":0.54882,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49498,-0.01853,0.11472]}],"total_contact_groups":18},"final_pose_error":0.10812,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49509,-0.08139,0.03389],"final_tcp_position":[0.49622,0.00284,0.19198],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":355.37637,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.0591,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":328.62809,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":995.0,"raw_peak_contact_force":355.37637,"tcp_end":[0.4745,0.10691,0.06026],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":139.0,"n_steps_budget":600.0,"object_pos_end":[0.49397,0.05907,0.03393],"object_pos_start":[0.49422,0.0591,0.03391],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13935,"object_z_max":0.03393,"peak_contact_force":0.54501,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":208.0,"raw_peak_contact_force":322.46444,"tcp_end":[0.48761,0.10116,0.04108],"tcp_start":[0.4745,0.10691,0.06026],"tcp_to_object_dist_end":0.04317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.49406,0.05869,0.03401],"object_pos_start":[0.49397,0.05907,0.03393],"object_to_goal_dist_end":0.13894,"object_to_goal_dist_start":0.13933,"object_z_max":0.03401,"peak_contact_force":179.55904,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":840.0,"raw_peak_contact_force":218.26527,"tcp_end":[0.49186,0.09352,0.0371],"tcp_start":[0.48761,0.10116,0.04108],"tcp_to_object_dist_end":0.03504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,-0.08695,0.03567],"object_pos_start":[0.49406,0.05869,0.03401],"object_to_goal_dist_end":0.0101,"object_to_goal_dist_start":0.13894,"object_z_max":0.0387,"peak_contact_force":100.81112,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2188.0,"raw_peak_contact_force":117.81111,"tcp_end":[0.49765,-0.05789,0.03685],"tcp_start":[0.49186,0.09352,0.0371],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49509,-0.08139,0.03389],"object_pos_start":[0.49409,-0.08695,0.03567],"object_to_goal_dist_end":0.00796,"object_to_goal_dist_start":0.0101,"object_z_max":0.0367,"peak_contact_force":0.54947,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1091.0,"raw_peak_contact_force":67.08215,"tcp_end":[0.49622,0.00284,0.19198],"tcp_start":[0.49765,-0.05789,0.03685],"tcp_to_object_dist_end":0.17914,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```