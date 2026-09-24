## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2806 | 0.21 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2806 | 0.21 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2807 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.281) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.281
- **task_score** (E): 0.214
- **fitness_score**: 0.571  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1668 |
| descend_1 | 1.00 | 1.00 | 0.0834 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1355 |
| release_1 | 1.00 | 1.00 | 0.0251 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.021, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.021, 0.138)→(0.510, 0.018, 0.054) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.018, 0.054)→(0.502, 0.018, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 47.333 | 0.143 | 0.184 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.018, 0.045)→(0.511, 0.018, 0.180) | (0.516, 0.018, 0.026)→(0.519, 0.018, 0.155) | 0.236→0.204 | 1.00 / 38.000 | 0.079 | 0.453 |
| release_1 | release | 1.00 / step_budget | (0.511, 0.018, 0.180)→(0.506, 0.018, 0.204) | (0.519, 0.018, 0.155)→(0.505, 0.018, 0.025) | 0.204→0.241 | 1.00 / 2.667 | 0.134 | 1.362 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.287
- phase_score: 0.245
- phase_breakdown.release_1_score: 0.017
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.116
- phase_breakdown.descend_1_score: 0.868
- phase_breakdown.transport_arc_score: 0.000
- grasp_place_fitness: 0.608

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.608
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.287
- **Median Q (composite search score)**: 0.290
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.513


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90323,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.06807,"grasp_1.grip_force":14.49442,"lift_1.lift_height":0.18743,"lift_1.speed":0.09832},"optimized_scores":{"best_composite_score":0.31757,"best_fitness_score":0.60757,"best_task_score":0.28681},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":181.0,"contact_point_centroid":[0.51328,0.02931,-0.00792],"force_p95":1.39798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51,"mean_force":0.41119,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52141,0.02997,0.21565]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.5277,0.02973,-0.00115],"force_p95":0.31916,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46938,"mean_force":0.07464,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5149,0.03006,0.04582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19756.0,"contact_point_centroid":[0.51941,0.04927,0.12172],"force_p95":0.07463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30927,"mean_force":0.05126,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51891,0.03008,0.11919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20896.0,"contact_point_centroid":[0.52008,0.01096,0.1186],"force_p95":0.07832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29659,"mean_force":0.04903,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5187,0.03008,0.11676]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03082,-0.00206],"force_p95":0.13969,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17544,"mean_force":0.12726,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51743,0.03025,0.04551]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51035,0.02523,0.22077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5800.0,"contact_point_centroid":[0.51707,0.01093,0.04678],"force_p95":0.06774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13619,"mean_force":0.03814,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51619,0.03017,0.04409]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52316,0.03162,0.09539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1169.0,"contact_point_centroid":[0.52553,0.04942,0.19987],"force_p95":0.07399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10901,"mean_force":0.04472,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.525,0.03023,0.19829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1169.0,"contact_point_centroid":[0.52663,0.01113,0.19902],"force_p95":0.07816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10306,"mean_force":0.045,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.525,0.03023,0.19829]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5137.0,"contact_point_centroid":[0.51656,0.04947,0.04723],"force_p95":0.07066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07827,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5162,0.03017,0.04409]}],"total_contact_groups":11},"final_pose_error":0.01328,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5233,0.03017,0.02473],"final_tcp_position":[0.52638,0.03031,0.20056],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.51,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52407,0.03263,0.13738],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52475,0.03076,0.05409],"tcp_start":[0.52407,0.03263,0.13738],"tcp_to_object_dist_end":0.02866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.03056,0.02577],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18369,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.13928,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12737.0,"raw_peak_contact_force":0.17544,"tcp_end":[0.51616,0.03017,0.04405],"tcp_start":[0.52475,0.03076,0.05409],"tcp_to_object_dist_end":0.02321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.53433,0.03084,0.17603],"object_pos_start":[0.53045,0.03056,0.02577],"object_to_goal_dist_end":0.17595,"object_to_goal_dist_start":0.18369,"object_z_max":0.17591,"peak_contact_force":0.07807,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40798.0,"raw_peak_contact_force":0.46938,"tcp_end":[0.52638,0.03031,0.20056],"tcp_start":[0.51616,0.03017,0.04405],"tcp_to_object_dist_end":0.02579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5233,0.03017,0.02473],"object_pos_start":[0.53433,0.03084,0.17603],"object_to_goal_dist_end":0.18734,"object_to_goal_dist_start":0.17595,"object_z_max":0.17607,"peak_contact_force":0.13343,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2519.0,"raw_peak_contact_force":1.51,"tcp_end":[0.52134,0.02997,0.22462],"tcp_start":[0.52638,0.03031,0.20056],"tcp_to_object_dist_end":0.19991,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88608,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.09122,"grasp_1.grip_force":21.62125,"lift_1.lift_height":0.11988,"lift_1.speed":0.09374},"optimized_scores":{"best_composite_score":0.23439,"best_fitness_score":0.52439,"best_task_score":0.12181},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":302.0,"contact_point_centroid":[0.48895,-0.01506,-0.0044],"force_p95":0.81483,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08025,"mean_force":0.22983,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49304,-0.01515,0.14765]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.50131,-0.01433,-0.00115],"force_p95":0.26757,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43424,"mean_force":0.06541,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48906,-0.01478,0.04686]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13111.0,"contact_point_centroid":[0.49356,0.00417,0.0894],"force_p95":0.0723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28137,"mean_force":0.04801,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49241,-0.01497,0.08756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12412.0,"contact_point_centroid":[0.49267,-0.03418,0.09069],"force_p95":0.07187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27718,"mean_force":0.0499,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49243,-0.01497,0.08758]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01571,-0.00208],"force_p95":0.14602,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18987,"mean_force":0.1288,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49136,-0.01478,0.04638]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49872,0.00415,0.21755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5557.0,"contact_point_centroid":[0.4909,0.00445,0.04716],"force_p95":0.06348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12744,"mean_force":0.03981,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49015,-0.01477,0.04508]},{"body_a":"world","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4978,-0.01242,0.09532]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1171.0,"contact_point_centroid":[0.49794,-0.03435,0.13335],"force_p95":0.07417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1062,"mean_force":0.04512,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49725,-0.01519,0.13181]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.49846,0.00395,0.1326],"force_p95":0.07427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10278,"mean_force":0.0452,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49725,-0.01519,0.1318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5164.0,"contact_point_centroid":[0.49012,-0.03405,0.0486],"force_p95":0.06681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07357,"mean_force":0.04267,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49016,-0.01477,0.04509]}],"total_contact_groups":11},"final_pose_error":0.0127,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.48889,-0.01506,0.02651],"final_tcp_position":[0.49885,-0.01521,0.13387],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.08025,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.4995,-0.01009,0.13696],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1040.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49851,-0.0148,0.05423],"tcp_start":[0.4995,-0.01009,0.13696],"tcp_to_object_dist_end":0.02872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50377,-0.01528,0.0257],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31222,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14547,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12521.0,"raw_peak_contact_force":0.18987,"tcp_end":[0.49012,-0.01477,0.04505],"tcp_start":[0.49851,-0.0148,0.05423],"tcp_to_object_dist_end":0.02368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50836,-0.01574,0.11073],"object_pos_start":[0.50377,-0.01528,0.0257],"object_to_goal_dist_end":0.25755,"object_to_goal_dist_start":0.31222,"object_z_max":0.11062,"peak_contact_force":0.07669,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25674.0,"raw_peak_contact_force":0.43424,"tcp_end":[0.49885,-0.01521,0.13387],"tcp_start":[0.49012,-0.01477,0.04505],"tcp_to_object_dist_end":0.02503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48889,-0.01506,0.02651],"object_pos_start":[0.50836,-0.01574,0.11073],"object_to_goal_dist_end":0.31579,"object_to_goal_dist_start":0.25755,"object_z_max":0.11076,"peak_contact_force":0.13066,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2645.0,"raw_peak_contact_force":1.08025,"tcp_end":[0.49291,-0.01514,0.15892],"tcp_start":[0.49885,-0.01521,0.13387],"tcp_to_object_dist_end":0.13247,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90426,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.054,"grasp_1.grip_force":11.5273,"lift_1.lift_height":0.21013,"lift_1.speed":0.0991},"optimized_scores":{"best_composite_score":0.28981,"best_fitness_score":0.57981,"best_task_score":0.23262},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.49367,0.0377,-0.00774],"force_p95":1.38976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49429,"mean_force":0.41611,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50238,0.03855,0.22092]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.51008,0.0383,-0.00117],"force_p95":0.27447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45509,"mean_force":0.06564,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49734,0.03868,0.04673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19645.0,"contact_point_centroid":[0.50105,0.05789,0.12453],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29984,"mean_force":0.05195,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50066,0.0387,0.12243]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20562.0,"contact_point_centroid":[0.50224,0.01962,0.12181],"force_p95":0.08056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29147,"mean_force":0.05013,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5005,0.03869,0.12048]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03973,-0.00208],"force_p95":0.14444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1873,"mean_force":0.12846,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49988,0.0389,0.04629]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1169.0,"contact_point_centroid":[0.506,0.05805,0.20425],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16288,"mean_force":0.04546,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50588,0.03887,0.20299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1170.0,"contact_point_centroid":[0.50768,0.01979,0.20335],"force_p95":0.07992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15934,"mean_force":0.04576,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50588,0.03887,0.20298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5070.0,"contact_point_centroid":[0.50038,0.01965,0.04657],"force_p95":0.07311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14613,"mean_force":0.04334,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49867,0.0388,0.04495]},{"body_a":"world","body_b":"grasp_target","contact_count":2140.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50241,0.02887,0.22224]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50608,0.04006,0.09607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4908.0,"contact_point_centroid":[0.49903,0.05807,0.04753],"force_p95":0.07532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07749,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49868,0.0388,0.04495]}],"total_contact_groups":11},"final_pose_error":0.03121,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.50369,0.03875,0.02415],"final_tcp_position":[0.50716,0.03896,0.20509],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.49429,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2140.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50754,0.0408,0.13832],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50708,0.0395,0.05441],"tcp_start":[0.50754,0.0408,0.13832],"tcp_to_object_dist_end":0.0289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03932,0.02571],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21266,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14362,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11778.0,"raw_peak_contact_force":0.1873,"tcp_end":[0.49864,0.0388,0.04491],"tcp_start":[0.50708,0.0395,0.05441],"tcp_to_object_dist_end":0.02367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51443,0.0396,0.1794],"object_pos_start":[0.51248,0.03932,0.02571],"object_to_goal_dist_end":0.1779,"object_to_goal_dist_start":0.21266,"object_z_max":0.17921,"peak_contact_force":0.08356,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40349.0,"raw_peak_contact_force":0.45509,"tcp_end":[0.50716,0.03896,0.20509],"tcp_start":[0.49864,0.0388,0.04491],"tcp_to_object_dist_end":0.0267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,0.03875,0.02415],"object_pos_start":[0.51443,0.0396,0.1794],"object_to_goal_dist_end":0.21875,"object_to_goal_dist_start":0.1779,"object_z_max":0.17953,"peak_contact_force":0.13937,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2518.0,"raw_peak_contact_force":1.49429,"tcp_end":[0.50231,0.03855,0.22971],"tcp_start":[0.50716,0.03896,0.20509],"tcp_to_object_dist_end":0.20556,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```