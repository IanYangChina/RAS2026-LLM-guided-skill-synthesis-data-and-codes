## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0360 | 0.00 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.1885 | 0.19 | ✅ accepted |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.1928 | 0.18 | ✅ accepted |
| 1 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.2026 | 0.16 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.1933 | 0.18 | ✅ accepted |

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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.036) — your mutation base

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

- **Composite score**: -0.036
- **task_score** (E): 0.000
- **fitness_score**: 0.154  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2452 |
| approach_1 | 1.00 | 1.00 | 0.0205 |
| contact_1 | 1.00 | 1.00 | 0.0000 |
| push_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.507, 0.123, 0.070) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.667 | 114.249 | 120.016 |
| approach_1 | approach | 1.00 / step_budget | (0.507, 0.123, 0.070)→(0.503, 0.111, 0.055) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 248.801 | 259.601 |
| contact_1 | contact | 1.00 / force_exceeded | (0.503, 0.111, 0.055)→(0.503, 0.111, 0.055) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 64.747 | 64.747 |
| push_1 | push | 0.00 / guard_failure | (0.503, 0.111, 0.055)→(0.503, 0.111, 0.055) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 55.274 | 55.274 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.278
- phase_breakdown.approach_score: 0.689
- phase_breakdown.contact_score: 0.670
- phase_breakdown.push_score: 0.010

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.167
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.036
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.381


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00203,"approach_1.speed":0.07925,"contact_1.contact_force":6.01112,"contact_1.speed":0.0137,"push_1.push_depth":0.18463,"push_1.push_speed":0.06783,"retract_1.speed":0.08239},"optimized_scores":{"best_composite_score":-0.02336,"best_fitness_score":0.16664,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":269.0,"contact_point_centroid":[0.48757,0.21093,-5e-05],"force_p95":269.93254,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.80135,"mean_force":210.07741,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48613,0.15008,0.05551]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48972,0.21016,-0.00013],"force_p95":87.19961,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.19961,"mean_force":87.19961,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48796,0.15028,0.05639]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48974,0.21018,-0.00013],"force_p95":45.81331,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.81331,"mean_force":45.81331,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48798,0.15029,0.05639]},{"body_a":"peg","body_b":"channel_base_body","contact_count":706.0,"contact_point_centroid":[0.49618,0.11909,0.00942],"force_p95":0.61334,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55158,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48795,0.1835,0.18055]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50465,0.21213,0.29589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":393.0,"contact_point_centroid":[0.49603,0.11917,0.00944],"force_p95":0.59804,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65754,"mean_force":0.54098,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48514,0.15137,0.05726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47818,0.12,0.00943],"force_p95":0.58581,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58581,"mean_force":0.58581,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48798,0.15029,0.05639]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51126,0.10942,0.00943],"force_p95":0.50324,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50324,"mean_force":0.50324,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48796,0.15028,0.05639]}],"total_contact_groups":8},"final_pose_error":0.18465,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.496,0.119,0.03386],"final_tcp_position":[0.48799,0.1503,0.05638],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":294.80135,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11902,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54361,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":730.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48226,0.15957,0.06952],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":393.0,"n_steps_budget":600.0,"object_pos_end":[0.49604,0.11899,0.03387],"object_pos_start":[0.49604,0.11902,0.03387],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19915,"object_z_max":0.03406,"peak_contact_force":267.56112,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":662.0,"raw_peak_contact_force":294.80135,"subtask_id":"contact","tcp_end":[0.48796,0.15028,0.05639],"tcp_start":[0.48226,0.15957,0.06952],"tcp_to_object_dist_end":0.03939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11899,0.03386],"object_pos_start":[0.49604,0.11899,0.03387],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19912,"object_z_max":0.03387,"peak_contact_force":87.19961,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":87.19961,"subtask_id":"contact","tcp_end":[0.48798,0.15029,0.05639],"tcp_start":[0.48796,0.15028,0.05639],"tcp_to_object_dist_end":0.03939,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.119,0.03386],"object_pos_start":[0.49601,0.11899,0.03386],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19913,"object_z_max":0.03386,"peak_contact_force":45.81331,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":45.81331,"subtask_id":"push","tcp_end":[0.48799,0.1503,0.05638],"tcp_start":[0.48798,0.15029,0.05639],"tcp_to_object_dist_end":0.03938,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00748,"approach_1.speed":0.08064,"contact_1.contact_force":5.37026,"contact_1.speed":0.02551,"push_1.push_depth":0.16466,"push_1.push_speed":0.072,"retract_1.speed":0.11943},"optimized_scores":{"best_composite_score":-0.03642,"best_fitness_score":0.15358,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":210.0,"contact_point_centroid":[0.51159,0.15763,-0.0001],"force_p95":251.42261,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.34047,"mean_force":198.61825,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50993,0.09547,0.05394]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52527,0.12,0.05969],"force_p95":168.19255,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":168.30667,"mean_force":141.80507,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51787,0.10709,0.06867]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":140.0,"contact_point_centroid":[0.5251,0.12,0.05989],"force_p95":143.53733,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.51356,"mean_force":130.03957,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51633,0.10624,0.06788]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51198,0.15747,-7e-05],"force_p95":58.30882,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.30882,"mean_force":58.30882,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51007,0.09502,0.05367]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51198,0.15747,-6e-05],"force_p95":51.22128,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.22128,"mean_force":51.22128,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51007,0.09501,0.05367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":794.0,"contact_point_centroid":[0.50579,0.06296,0.00937],"force_p95":0.55631,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56361,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50507,0.15799,0.18087]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50338,0.22033,0.28869]},{"body_a":"peg","body_b":"channel_base_body","contact_count":417.0,"contact_point_centroid":[0.5061,0.06303,0.00938],"force_p95":0.55244,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54658,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51245,0.09995,0.0596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.4984,0.04668,0.00938],"force_p95":0.54636,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54636,"mean_force":0.54636,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51007,0.09501,0.05367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49061,0.05373,0.00938],"force_p95":0.54411,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54411,"mean_force":0.54411,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51007,0.09502,0.05367]}],"total_contact_groups":10},"final_pose_error":0.16467,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50593,0.06299,0.03381],"final_tcp_position":[0.51008,0.09502,0.05366],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":254.34047,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":168.30667,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":836.0,"raw_peak_contact_force":168.30667,"subtask_id":"approach","tcp_end":[0.51796,0.10696,0.06814],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":417.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.50596,0.06303,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":250.89611,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":767.0,"raw_peak_contact_force":254.34047,"subtask_id":"contact","tcp_end":[0.51007,0.09501,0.05367],"tcp_start":[0.51796,0.10696,0.06814],"tcp_to_object_dist_end":0.03795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.50594,0.06296,0.03381],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":51.22128,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":51.22128,"subtask_id":"contact","tcp_end":[0.51007,0.09502,0.05367],"tcp_start":[0.51007,0.09501,0.05367],"tcp_to_object_dist_end":0.03794,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06299,0.03381],"object_pos_start":[0.50594,0.06296,0.03381],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.14322,"object_z_max":0.03381,"peak_contact_force":58.30882,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":58.30882,"subtask_id":"push","tcp_end":[0.51008,0.09502,0.05366],"tcp_start":[0.51007,0.09502,0.05367],"tcp_to_object_dist_end":0.03792,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11224,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.01016,"approach_1.speed":0.01898,"contact_1.contact_force":6.07589,"contact_1.speed":0.00582,"push_1.push_depth":0.02229,"push_1.push_speed":0.03056,"retract_1.speed":0.0898},"optimized_scores":{"best_composite_score":-0.04835,"best_fitness_score":0.14165,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":362.0,"contact_point_centroid":[0.51343,0.1493,-8e-05],"force_p95":228.17953,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.66264,"mean_force":193.84529,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51103,0.08819,0.05514]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":583.0,"contact_point_centroid":[0.52503,0.12,0.05994],"force_p95":196.27196,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.35966,"mean_force":162.5468,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52057,0.10112,0.07131]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52517,0.11999,0.05944],"force_p95":189.13634,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":189.49327,"mean_force":175.96202,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52174,0.10196,0.07055]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51399,0.14894,-6e-05],"force_p95":61.69845,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.69845,"mean_force":61.69845,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51131,0.08759,0.0549]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51399,0.14894,-6e-05],"force_p95":55.82158,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.82158,"mean_force":55.82158,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51131,0.08759,0.0549]},{"body_a":"peg","body_b":"channel_base_body","contact_count":821.0,"contact_point_centroid":[0.50596,0.0566,0.00936],"force_p95":0.60012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56598,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50719,0.15427,0.17935]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50264,0.22243,0.28633]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50615,0.05664,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55033,"mean_force":0.54674,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5167,0.096,0.06493]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50541,0.03868,0.00938],"force_p95":0.54975,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54975,"mean_force":0.54975,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51131,0.08759,0.0549]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49115,0.04674,0.00938],"force_p95":0.54553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54553,"mean_force":0.54553,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51131,0.08759,0.0549]}],"total_contact_groups":10},"final_pose_error":0.0223,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50611,0.05662,0.03378],"final_tcp_position":[0.51131,0.0876,0.05489],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":229.66264,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":173.8965,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":885.0,"raw_peak_contact_force":189.49327,"subtask_id":"approach","tcp_end":[0.5217,0.10203,0.07111],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":227.94631,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1945.0,"raw_peak_contact_force":229.66264,"subtask_id":"contact","tcp_end":[0.51131,0.08759,0.0549],"tcp_start":[0.5217,0.10203,0.07111],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":55.82158,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":55.82158,"subtask_id":"contact","tcp_end":[0.51131,0.08759,0.0549],"tcp_start":[0.51131,0.08759,0.0549],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":61.69845,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":61.69845,"subtask_id":"push","tcp_end":[0.51131,0.0876,0.05489],"tcp_start":[0.51131,0.08759,0.0549],"tcp_to_object_dist_end":0.03784,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```