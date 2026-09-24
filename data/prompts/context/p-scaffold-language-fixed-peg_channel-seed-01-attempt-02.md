## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2013 | 0.57 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2338 | 0.64 | ✅ accepted |
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2185 | 0.60 | ✅ accepted |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.201) — your mutation base

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

- **Composite score**: 0.201
- **task_score** (E): 0.571
- **fitness_score**: 0.591  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
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
| push_1 | 0.33 | 1.00 | 0.1560 |
| retract_1 | 0.00 | 1.00 | 0.1662 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.484, 0.125, 0.055) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.667 | 221.293 | 237.641 |
| approach_1 | approach | 1.00 / step_budget | (0.484, 0.125, 0.055)→(0.491, 0.121, 0.042) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.549 | 210.115 |
| contact_1 | contact | 1.00 / step_budget | (0.491, 0.121, 0.042)→(0.494, 0.113, 0.036) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.159 | 1.00 / 2.000 | 163.289 | 193.991 |
| push_1 | push | 0.33 / step_budget | (0.494, 0.113, 0.036)→(0.498, -0.043, 0.037) | (0.497, 0.079, 0.034)→(0.501, -0.072, 0.035) | 0.159→0.019 | 1.00 / 3.000 | 48.713 | 141.571 |
| retract_1 | retract | 0.00 / step_budget | (0.498, -0.043, 0.037)→(0.497, 0.008, 0.195) | (0.501, -0.072, 0.035)→(0.500, -0.067, 0.034) | 0.019→0.018 | 1.00 / 1.000 | 0.542 | 68.631 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.994
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.994
- phase_score: 0.498
- phase_breakdown.push_score: 0.266
- phase_breakdown.approach_score: 0.898
- phase_breakdown.contact_score: 0.794

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.696
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.994
- **Median Q (composite search score)**: 0.194
- **K-run variance**: 0.0069
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.455


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50595,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00579,"approach_1.approach_height":0.05749,"approach_1.speed":0.03132,"contact_1.speed":0.03699,"push_1.push_distance":0.19996,"push_1.push_speed":0.09901},"optimized_scores":{"best_composite_score":0.30647,"best_fitness_score":0.69647,"best_task_score":0.99384},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":761.0,"contact_point_centroid":[0.54362,0.06784,0.05998],"force_p95":122.5293,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.41002,"mean_force":103.14826,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49796,0.07193,0.03633]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":283.0,"contact_point_centroid":[0.54773,0.12,0.05998],"force_p95":128.3165,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.33072,"mean_force":80.04581,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49551,0.14659,0.0343]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54344,-0.01923,0.05999],"force_p95":63.13221,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.62368,"mean_force":58.70897,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49874,-0.01414,0.03689]},{"body_a":"attachment","body_b":"peg","contact_count":303.0,"contact_point_centroid":[0.49915,0.05728,0.03927],"force_p95":14.68179,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.60655,"mean_force":2.61227,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49799,0.06896,0.03631]},{"body_a":"peg","body_b":"channel_base_body","contact_count":775.0,"contact_point_centroid":[0.49847,0.03309,0.00953],"force_p95":6.25524,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.75236,"mean_force":1.4759,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49798,0.07161,0.03634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50076,0.11464,0.00945],"force_p95":0.65217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.27037,"mean_force":0.63327,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49521,0.1481,0.0352]},{"body_a":"attachment","body_b":"peg","contact_count":46.0,"contact_point_centroid":[0.50067,0.13372,0.04272],"force_p95":2.79028,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.98287,"mean_force":1.04541,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49668,0.14564,0.03421]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":208.0,"contact_point_centroid":[0.47477,0.0368,0.03839],"force_p95":1.69395,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.28851,"mean_force":0.57335,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49823,0.06767,0.03667]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":65.0,"contact_point_centroid":[0.5253,-0.02984,0.04169],"force_p95":5.774,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.13282,"mean_force":0.95775,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49881,0.00016,0.03695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":755.0,"contact_point_centroid":[0.50092,0.11599,0.00939],"force_p95":0.61661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55392,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4977,0.17803,0.1717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50435,-0.04337,0.00945],"force_p95":0.55816,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91199,"mean_force":0.54221,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49592,0.00961,0.11561]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50075,0.11655,0.00946],"force_p95":0.5787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58479,"mean_force":0.54094,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49639,0.15694,0.04619]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50221,-0.02595,0.04222],"force_p95":0.47905,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4806,"mean_force":0.40411,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49875,-0.01407,0.0369]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52504,-0.04515,0.05937],"force_p95":0.19961,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20685,"mean_force":0.14223,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49734,-0.01263,0.03956]}],"total_contact_groups":14},"final_pose_error":0.10256,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50492,-0.04298,0.03433],"final_tcp_position":[0.49675,0.01891,0.19926],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":134.41002,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11605,0.03394],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54801,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":755.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49706,0.15726,0.04892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11601,0.03391],"object_pos_start":[0.50095,0.11605,0.03394],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19615,"object_z_max":0.03394,"peak_contact_force":0.54838,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.58479,"tcp_end":[0.49634,0.15677,0.04264],"tcp_start":[0.49706,0.15726,0.04892],"tcp_to_object_dist_end":0.04193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.50145,0.11511,0.03456],"object_pos_start":[0.50092,0.11601,0.03391],"object_to_goal_dist_end":0.1952,"object_to_goal_dist_start":0.19611,"object_z_max":0.03456,"peak_contact_force":103.05412,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":747.0,"raw_peak_contact_force":131.33072,"tcp_end":[0.49714,0.14524,0.03415],"tcp_start":[0.49634,0.15677,0.04264],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50342,-0.04345,0.0343],"object_pos_start":[0.50145,0.11511,0.03456],"object_to_goal_dist_end":0.03715,"object_to_goal_dist_start":0.1952,"object_z_max":0.03795,"peak_contact_force":0.9926,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2112.0,"raw_peak_contact_force":134.41002,"tcp_end":[0.49876,-0.01394,0.03691],"tcp_start":[0.49714,0.14524,0.03415],"tcp_to_object_dist_end":0.02999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50492,-0.04298,0.03433],"object_pos_start":[0.50342,-0.04345,0.0343],"object_to_goal_dist_end":0.03778,"object_to_goal_dist_start":0.03715,"object_z_max":0.03545,"peak_contact_force":0.53999,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1009.0,"raw_peak_contact_force":63.62368,"tcp_end":[0.49675,0.01891,0.19926],"tcp_start":[0.49876,-0.01394,0.03691],"tcp_to_object_dist_end":0.17635,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61988,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00617,"approach_1.approach_height":0.14318,"approach_1.speed":0.02967,"contact_1.speed":0.04259,"push_1.push_distance":0.19858,"push_1.push_speed":0.09973},"optimized_scores":{"best_composite_score":0.19434,"best_fitness_score":0.58434,"best_task_score":0.4364},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4749,0.12,0.0598],"force_p95":341.5277,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.62701,"mean_force":311.80708,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47984,0.111,0.05723]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47497,0.11792,0.05994],"force_p95":283.70214,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.29523,"mean_force":209.67753,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48303,0.11067,0.05591]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":409.0,"contact_point_centroid":[0.535,0.10349,0.05995],"force_p95":214.24986,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.3783,"mean_force":173.94326,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48947,0.10213,0.03793]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":717.0,"contact_point_centroid":[0.54082,0.02221,0.05999],"force_p95":118.24665,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.93387,"mean_force":98.82563,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49548,0.02367,0.03786]},{"body_a":"attachment","body_b":"peg","contact_count":584.0,"contact_point_centroid":[0.50171,-0.00111,0.04402],"force_p95":49.32585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.60212,"mean_force":11.23982,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49592,0.01034,0.03787]},{"body_a":"peg","body_b":"channel_base_body","contact_count":71.0,"contact_point_centroid":[0.50548,-0.10079,0.05563],"force_p95":68.92812,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.91723,"mean_force":35.96732,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49786,-0.0545,0.03748]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54335,-0.0532,0.05998],"force_p95":73.99852,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.02943,"mean_force":66.35852,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49831,-0.05711,0.03739]},{"body_a":"peg","body_b":"channel_base_body","contact_count":52.0,"contact_point_centroid":[0.50423,-0.10087,0.05949],"force_p95":16.51009,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.2828,"mean_force":7.45183,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49688,-0.05409,0.03981]},{"body_a":"attachment","body_b":"peg","contact_count":65.0,"contact_point_centroid":[0.50213,-0.06449,0.05037],"force_p95":14.19099,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.04165,"mean_force":6.05259,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49652,-0.05287,0.04118]},{"body_a":"peg","body_b":"channel_base_body","contact_count":746.0,"contact_point_centroid":[0.50315,-0.01827,0.00977],"force_p95":28.82915,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.70908,"mean_force":5.90142,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49548,0.02367,0.03786]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":230.0,"contact_point_centroid":[0.52512,-0.0272,0.02349],"force_p95":10.46145,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.32765,"mean_force":1.9544,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49626,-0.00056,0.03788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":951.0,"contact_point_centroid":[0.5002,-0.07784,0.00941],"force_p95":0.5669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.42585,"mean_force":0.56428,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49545,-0.01813,0.11496]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.4749,0.06017,0.01668],"force_p95":5.78523,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.69231,"mean_force":1.33793,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49323,0.08905,0.0378]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.49531,0.0638,0.00938],"force_p95":0.56258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55591,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48773,0.15105,0.1656]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49933,0.19869,0.29695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.49515,0.0639,0.0094],"force_p95":0.55087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54517,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4894,0.10228,0.03802]}],"total_contact_groups":17},"final_pose_error":0.10767,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50001,-0.07733,0.03378],"final_tcp_position":[0.49647,0.00312,0.19244],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":355.62701,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49535,0.06392,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":334.70153,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":908.0,"raw_peak_contact_force":355.62701,"tcp_end":[0.481,0.11081,0.05671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":95.0,"n_steps_budget":600.0,"object_pos_end":[0.49532,0.06402,0.034],"object_pos_start":[0.49535,0.06392,0.03399],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14412,"object_z_max":0.034,"peak_contact_force":0.55289,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":125.0,"raw_peak_contact_force":307.29523,"tcp_end":[0.48856,0.10593,0.04095],"tcp_start":[0.481,0.11081,0.05671],"tcp_to_object_dist_end":0.04301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.49527,0.06412,0.03403],"object_pos_start":[0.49532,0.06402,0.034],"object_to_goal_dist_end":0.14432,"object_to_goal_dist_start":0.14422,"object_z_max":0.03403,"peak_contact_force":207.25489,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":848.0,"raw_peak_contact_force":232.3783,"tcp_end":[0.49312,0.0992,0.03757],"tcp_start":[0.48856,0.10593,0.04095],"tcp_to_object_dist_end":0.03533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50526,-0.0856,0.03504],"object_pos_start":[0.49527,0.06412,0.03403],"object_to_goal_dist_end":0.00914,"object_to_goal_dist_start":0.14432,"object_z_max":0.03873,"peak_contact_force":81.82472,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2357.0,"raw_peak_contact_force":170.93387,"tcp_end":[0.49832,-0.05705,0.0374],"tcp_start":[0.49312,0.0992,0.03757],"tcp_to_object_dist_end":0.02947,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50001,-0.07733,0.03378],"object_pos_start":[0.50526,-0.0856,0.03504],"object_to_goal_dist_end":0.00677,"object_to_goal_dist_start":0.00914,"object_z_max":0.03732,"peak_contact_force":0.54654,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1071.0,"raw_peak_contact_force":75.02943,"tcp_end":[0.49647,0.00312,0.19244],"tcp_start":[0.49832,-0.05705,0.0374],"tcp_to_object_dist_end":0.17793,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62791,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00092,"approach_1.approach_height":0.29103,"approach_1.speed":0.0777,"contact_1.speed":0.03437,"push_1.push_distance":0.14453,"push_1.push_speed":0.09602},"optimized_scores":{"best_composite_score":0.10315,"best_fitness_score":0.49315,"best_task_score":0.282},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":106.0,"contact_point_centroid":[0.47492,0.11854,0.05985],"force_p95":346.92903,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.37637,"mean_force":313.68239,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47019,0.10819,0.06243]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":69.0,"contact_point_centroid":[0.47497,0.11524,0.05995],"force_p95":296.63938,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.46444,"mean_force":213.26593,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48035,0.10608,0.0574]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":401.0,"contact_point_centroid":[0.53365,0.0977,0.05996],"force_p95":212.3218,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.26527,"mean_force":164.13477,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48832,0.09664,0.03752]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":706.0,"contact_point_centroid":[0.53989,0.02142,0.05999],"force_p95":108.4888,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.37026,"mean_force":88.69111,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49481,0.02306,0.03733]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54267,-0.05513,0.05999],"force_p95":67.24033,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.24033,"mean_force":67.24033,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49792,-0.05896,0.03683]},{"body_a":"attachment","body_b":"peg","contact_count":361.0,"contact_point_centroid":[0.49583,-0.005,0.03889],"force_p95":38.55094,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.64233,"mean_force":7.36389,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49543,0.00671,0.03727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":64.0,"contact_point_centroid":[0.49342,-0.10126,0.04199],"force_p95":50.05569,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.06228,"mean_force":29.8947,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49762,-0.05542,0.0369]},{"body_a":"attachment","body_b":"peg","contact_count":48.0,"contact_point_centroid":[0.49526,-0.06759,0.03946],"force_p95":24.01898,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.99768,"mean_force":13.63128,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4965,-0.05593,0.03891]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.49324,-0.1011,0.05874],"force_p95":31.28408,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.34781,"mean_force":13.13949,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49589,-0.0535,0.04173]},{"body_a":"peg","body_b":"channel_base_body","contact_count":748.0,"contact_point_centroid":[0.49845,-0.0151,0.00962],"force_p95":6.82103,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.12151,"mean_force":1.69337,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4948,0.02331,0.03733]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":52.0,"contact_point_centroid":[0.4748,-0.08511,0.05521],"force_p95":18.3027,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.84187,"mean_force":11.13208,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49642,-0.05571,0.03908]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":393.0,"contact_point_centroid":[0.47481,-0.0118,0.02656],"force_p95":1.05125,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.76057,"mean_force":0.48549,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49503,0.01828,0.03736]},{"body_a":"peg","body_b":"channel_base_body","contact_count":854.0,"contact_point_centroid":[0.49433,0.05892,0.00937],"force_p95":0.55492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56328,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48064,0.14718,0.16216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49899,0.19829,0.29587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.49468,-0.08164,0.0094],"force_p95":0.56109,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72385,"mean_force":0.54713,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4952,-0.01912,0.11472]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.49388,0.05891,0.0094],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54556,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48822,0.09686,0.03765]}],"total_contact_groups":17},"final_pose_error":0.10819,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4946,-0.08176,0.03379],"final_tcp_position":[0.49635,0.00248,0.1919],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":355.37637,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.0591,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":328.62809,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":995.0,"raw_peak_contact_force":355.37637,"tcp_end":[0.4745,0.10691,0.06026],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":139.0,"n_steps_budget":600.0,"object_pos_end":[0.49397,0.05907,0.03393],"object_pos_start":[0.49422,0.0591,0.03391],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13935,"object_z_max":0.03393,"peak_contact_force":0.54501,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":208.0,"raw_peak_contact_force":322.46444,"tcp_end":[0.48761,0.10116,0.04108],"tcp_start":[0.4745,0.10691,0.06026],"tcp_to_object_dist_end":0.04317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.49406,0.05869,0.03401],"object_pos_start":[0.49397,0.05907,0.03393],"object_to_goal_dist_end":0.13894,"object_to_goal_dist_start":0.13933,"object_z_max":0.03401,"peak_contact_force":179.55904,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":840.0,"raw_peak_contact_force":218.26527,"tcp_end":[0.49186,0.09352,0.0371],"tcp_start":[0.48761,0.10116,0.04108],"tcp_to_object_dist_end":0.03504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49319,-0.08759,0.03524],"object_pos_start":[0.49406,0.05869,0.03401],"object_to_goal_dist_end":0.01126,"object_to_goal_dist_start":0.13894,"object_z_max":0.03789,"peak_contact_force":63.3208,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2272.0,"raw_peak_contact_force":119.37026,"tcp_end":[0.49798,-0.05885,0.03686],"tcp_start":[0.49186,0.09352,0.0371],"tcp_to_object_dist_end":0.02919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4946,-0.08176,0.03379],"object_pos_start":[0.49319,-0.08759,0.03524],"object_to_goal_dist_end":0.00842,"object_to_goal_dist_start":0.01126,"object_z_max":0.03599,"peak_contact_force":0.53962,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1122.0,"raw_peak_contact_force":67.24033,"tcp_end":[0.49635,0.00248,0.1919],"tcp_start":[0.49798,-0.05885,0.03686],"tcp_to_object_dist_end":0.17916,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```