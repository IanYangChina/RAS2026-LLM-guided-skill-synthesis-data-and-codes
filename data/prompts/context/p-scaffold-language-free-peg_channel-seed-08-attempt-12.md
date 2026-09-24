## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.2059 | 0.16 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1693 | 0.00 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2430 | 0.00 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.1176 | 0.00 | ❌ rejected |
| 8 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.1014 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=-0.206) — your mutation base

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
  control: position_control
  termination: pose_tolerance
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: contact_detected
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
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.206
- **task_score** (E): 0.155
- **fitness_score**: 0.234  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2541 |
| approach_1 | 1.00 | 1.00 | 0.0048 |
| contact_1 | 1.00 | 1.00 | 0.0066 |
| push_1 | 0.33 | 1.00 | 0.0505 |
| retract_1 | 0.00 | 1.00 | 0.1013 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.127, 0.059) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.667 | 212.187 | 238.952 |
| approach_1 | approach | 1.00 / step_budget | (0.513, 0.127, 0.059)→(0.515, 0.126, 0.055) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 152.843 | 165.828 |
| contact_1 | contact | 1.00 / step_budget | (0.515, 0.126, 0.055)→(0.516, 0.120, 0.054) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 207.423 | 211.448 |
| push_1 | push | 0.33 / step_budget | (0.516, 0.120, 0.054)→(0.513, 0.070, 0.055) | (0.503, 0.080, 0.034)→(0.502, 0.052, 0.034) | 0.160→0.132 | 1.00 / 2.333 | 189.423 | 208.120 |
| retract_1 | retract | 0.00 / step_budget | (0.513, 0.070, 0.055)→(0.504, 0.064, 0.156) | (0.502, 0.052, 0.034)→(0.502, 0.052, 0.034) | 0.132→0.133 | 1.00 / 1.000 | 0.547 | 95.227 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.512
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.466
- phase_score: 0.375
- phase_breakdown.push_score: 0.053
- phase_breakdown.approach_score: 0.951
- phase_breakdown.contact_score: 0.767

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.411
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.466
- **Median Q (composite search score)**: -0.294
- **K-run variance**: 0.0157
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.269


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10227,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00064,"contact_1.contact_force":10.63406,"contact_1.speed":0.02463,"push_1.push_depth":0.0614,"push_1.push_distance":0.05252,"push_1.push_speed":0.0537,"retract_1.speed":0.04529},"optimized_scores":{"best_composite_score":-0.0285,"best_fitness_score":0.4115,"best_task_score":0.46564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":393.0,"contact_point_centroid":[0.54367,0.12,0.05997],"force_p95":122.7645,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.29094,"mean_force":103.22288,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48862,0.1536,0.03457]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54206,0.06582,0.06],"force_p95":92.17856,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.58225,"mean_force":57.99492,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49709,0.06649,0.03688]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":710.0,"contact_point_centroid":[0.54118,0.10703,0.05999],"force_p95":86.16875,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.1436,"mean_force":72.04665,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49433,0.11348,0.036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":792.0,"contact_point_centroid":[0.49596,0.07407,0.00972],"force_p95":3.8727,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.92616,"mean_force":1.06893,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49442,0.11218,0.03604]},{"body_a":"attachment","body_b":"peg","contact_count":397.0,"contact_point_centroid":[0.49502,0.10026,0.03734],"force_p95":5.41503,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.3072,"mean_force":1.30865,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49441,0.11211,0.03603]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":182.0,"contact_point_centroid":[0.47479,0.09,0.03396],"force_p95":1.22592,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.68378,"mean_force":0.37636,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49386,0.12042,0.03592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49359,0.0365,0.00942],"force_p95":0.57674,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.10863,"mean_force":0.54837,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49411,0.06865,0.08341]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.49471,0.05469,0.03994],"force_p95":2.24298,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.07995,"mean_force":0.61392,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4955,0.06662,0.03942]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":361.0,"contact_point_centroid":[0.47498,0.03708,0.05427],"force_p95":0.2771,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.62968,"mean_force":0.06987,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49427,0.06841,0.07844]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.49619,0.11915,0.0094],"force_p95":0.61089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55292,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49061,0.17919,0.17037]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.19927,0.29748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":438.0,"contact_point_centroid":[0.49599,0.1194,0.00944],"force_p95":0.59629,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73379,"mean_force":0.54132,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48849,0.15385,0.03467]},{"body_a":"peg","body_b":"channel_base_body","contact_count":60.0,"contact_point_centroid":[0.49662,0.11999,0.00941],"force_p95":0.59669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59878,"mean_force":0.54283,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48431,0.15937,0.04348]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49767,0.13993,0.05309],"force_p95":0.21976,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2466,"mean_force":0.15014,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49058,0.15162,0.03448]}],"total_contact_groups":14},"final_pose_error":0.18195,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49304,0.03712,0.03378],"final_tcp_position":[0.49479,0.06657,0.13074],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":126.29094,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11947,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1996,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52313,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48315,0.16005,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":60.0,"n_steps_budget":600.0,"object_pos_end":[0.49605,0.11901,0.03384],"object_pos_start":[0.49601,0.11947,0.03385],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.1996,"object_z_max":0.03386,"peak_contact_force":0.51833,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":60.0,"raw_peak_contact_force":0.59878,"tcp_end":[0.48689,0.15887,0.03758],"tcp_start":[0.48315,0.16005,0.04931],"tcp_to_object_dist_end":0.04107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":438.0,"n_steps_budget":600.0,"object_pos_end":[0.49604,0.119,0.03405],"object_pos_start":[0.49605,0.11901,0.03384],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19914,"object_z_max":0.0341,"peak_contact_force":115.62552,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":845.0,"raw_peak_contact_force":126.29094,"tcp_end":[0.49243,0.14926,0.03436],"tcp_start":[0.48689,0.15887,0.03758],"tcp_to_object_dist_end":0.03048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.49272,0.03664,0.03461],"object_pos_start":[0.49604,0.119,0.03405],"object_to_goal_dist_end":0.11699,"object_to_goal_dist_start":0.19913,"object_z_max":0.03617,"peak_contact_force":45.33677,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2081.0,"raw_peak_contact_force":93.1436,"tcp_end":[0.49708,0.06657,0.03688],"tcp_start":[0.49243,0.14926,0.03436],"tcp_to_object_dist_end":0.03033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49304,0.03712,0.03378],"object_pos_start":[0.49272,0.03664,0.03461],"object_to_goal_dist_end":0.1175,"object_to_goal_dist_start":0.11699,"object_z_max":0.03515,"peak_contact_force":0.55319,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1391.0,"raw_peak_contact_force":97.58225,"tcp_end":[0.49479,0.06657,0.13074],"tcp_start":[0.49708,0.06657,0.03688],"tcp_to_object_dist_end":0.10135,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30851,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00359,"contact_1.contact_force":8.47087,"contact_1.speed":0.02845,"push_1.push_depth":0.09738,"push_1.push_distance":0.07754,"push_1.push_speed":0.06208,"retract_1.speed":0.0664},"optimized_scores":{"best_composite_score":-0.29513,"best_fitness_score":0.14487,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":114.0,"contact_point_centroid":[0.53488,0.11266,0.05979],"force_p95":345.12221,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":353.73417,"mean_force":317.18085,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52374,0.11275,0.06404]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":426.0,"contact_point_centroid":[0.53649,0.11267,0.05993],"force_p95":266.86038,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.63949,"mean_force":246.60197,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52542,0.11271,0.0645]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":980.0,"contact_point_centroid":[0.53314,0.08674,0.05995],"force_p95":260.80623,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":261.44675,"mean_force":205.85724,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52212,0.08702,0.06463]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":934.0,"contact_point_centroid":[0.53733,0.11109,0.05994],"force_p95":251.30616,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.06186,"mean_force":215.13942,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52625,0.11117,0.06448]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.53118,0.074,0.05997],"force_p95":81.78422,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.84475,"mean_force":61.23606,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5202,0.07477,0.06472]},{"body_a":"peg","body_b":"channel_base_body","contact_count":876.0,"contact_point_centroid":[0.5058,0.06299,0.00937],"force_p95":0.55584,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56201,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51235,0.14948,0.1623]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49981,0.19843,0.29603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50591,0.06291,0.00939],"force_p95":0.55131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55544,"mean_force":0.54622,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51171,0.07207,0.12037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50609,0.06292,0.00938],"force_p95":0.55274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52542,0.11271,0.0645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":934.0,"contact_point_centroid":[0.50599,0.06297,0.00939],"force_p95":0.55121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55493,"mean_force":0.5464,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52625,0.11117,0.06448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.506,0.06304,0.00939],"force_p95":0.55069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55462,"mean_force":0.54626,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52215,0.08721,0.06463]}],"total_contact_groups":11},"final_pose_error":0.13946,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5059,0.06308,0.03387],"final_tcp_position":[0.50718,0.06309,0.17583],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":353.73417,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":317.66646,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1024.0,"raw_peak_contact_force":353.73417,"tcp_end":[0.52444,0.11271,0.06453],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.06298,0.03381],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":240.12447,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":852.0,"raw_peak_contact_force":269.63949,"tcp_end":[0.52585,0.1125,0.06447],"tcp_start":[0.52444,0.11271,0.06453],"tcp_to_object_dist_end":0.06156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.50588,0.06294,0.03386],"object_pos_start":[0.50593,0.06298,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14323,"object_z_max":0.03386,"peak_contact_force":253.30878,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1868.0,"raw_peak_contact_force":254.06186,"tcp_end":[0.52622,0.10843,0.06446],"tcp_start":[0.52585,0.1125,0.06447],"tcp_to_object_dist_end":0.05847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.06287,0.03387],"object_pos_start":[0.50588,0.06294,0.03386],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.1432,"object_z_max":0.03387,"peak_contact_force":261.33912,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1980.0,"raw_peak_contact_force":261.44675,"tcp_end":[0.52021,0.07476,0.0647],"tcp_start":[0.52622,0.10843,0.06446],"tcp_to_object_dist_end":0.03595,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5059,0.06308,0.03387],"object_pos_start":[0.50604,0.06287,0.03387],"object_to_goal_dist_end":0.14333,"object_to_goal_dist_start":0.14313,"object_z_max":0.03388,"peak_contact_force":0.54239,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":84.84475,"tcp_end":[0.50718,0.06309,0.17583],"tcp_start":[0.52021,0.07476,0.0647],"tcp_to_object_dist_end":0.14197,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37766,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00407,"contact_1.contact_force":4.72389,"contact_1.speed":0.02952,"push_1.push_depth":0.09933,"push_1.push_distance":0.09818,"push_1.push_speed":0.08463,"retract_1.speed":0.05727},"optimized_scores":{"best_composite_score":-0.29416,"best_fitness_score":0.14584,"best_task_score":2e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":115.0,"contact_point_centroid":[0.54111,0.10688,0.05978],"force_p95":348.37484,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":360.87221,"mean_force":319.04148,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52992,0.10705,0.06389]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":979.0,"contact_point_centroid":[0.53544,0.07801,0.05995],"force_p95":262.20424,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.77112,"mean_force":219.99766,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52433,0.07861,0.06436]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":934.0,"contact_point_centroid":[0.54175,0.10487,0.05995],"force_p95":251.3111,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.98973,"mean_force":202.29017,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53058,0.10506,0.06429]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":455.0,"contact_point_centroid":[0.54216,0.10676,0.05994],"force_p95":225.76828,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.24613,"mean_force":204.86906,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53105,0.10687,0.0644]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.53292,0.06762,0.05997],"force_p95":96.9781,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.25348,"mean_force":67.13183,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52186,0.06889,0.0644]},{"body_a":"peg","body_b":"channel_base_body","contact_count":893.0,"contact_point_centroid":[0.50599,0.05663,0.00937],"force_p95":0.59924,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56446,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51585,0.14624,0.1622]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4999,0.19822,0.29562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.5061,0.05663,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55018,"mean_force":0.54674,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53105,0.10687,0.0644]},{"body_a":"peg","body_b":"channel_base_body","contact_count":934.0,"contact_point_centroid":[0.50612,0.05658,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53058,0.10506,0.06429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50617,0.05661,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52438,0.07886,0.06436]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50612,0.05664,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51359,0.06855,0.1125]}],"total_contact_groups":11},"final_pose_error":0.1531,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50615,0.0566,0.03378],"final_tcp_position":[0.5093,0.06334,0.16093],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":360.87221,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":318.37129,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1045.0,"raw_peak_contact_force":360.87221,"tcp_end":[0.53064,0.107,0.06441],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50615,0.0566,0.03378],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":217.88766,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":910.0,"raw_peak_contact_force":227.24613,"tcp_end":[0.53079,0.10651,0.06431],"tcp_start":[0.53064,0.107,0.06441],"tcp_to_object_dist_end":0.06349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.50615,0.0566,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":253.33383,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1868.0,"raw_peak_contact_force":253.98973,"tcp_end":[0.53022,0.1023,0.06416],"tcp_start":[0.53079,0.10651,0.06431],"tcp_to_object_dist_end":0.05991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.0566,0.03378],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":261.5924,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1979.0,"raw_peak_contact_force":269.77112,"tcp_end":[0.52187,0.06885,0.06439],"tcp_start":[0.53022,0.1023,0.06416],"tcp_to_object_dist_end":0.03654,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.0566,0.03378],"object_pos_start":[0.50612,0.0566,0.03378],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":0.545,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":103.25348,"tcp_end":[0.5093,0.06334,0.16093],"tcp_start":[0.52187,0.06885,0.06439],"tcp_to_object_dist_end":0.12737,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```