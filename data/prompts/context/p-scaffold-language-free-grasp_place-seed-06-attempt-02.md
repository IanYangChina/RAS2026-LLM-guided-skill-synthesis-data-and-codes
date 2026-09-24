## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3194 | 0.17 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=0.318) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
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
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.318
- **task_score** (E): 0.167
- **fitness_score**: 0.558  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1989 |
| descend_1 | 1.00 | 1.00 | 0.0635 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1615 |
| release_1 | 1.00 | 1.00 | 0.0255 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.106) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 5.918 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.106)→(0.494, 0.024, 0.043) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.043)→(0.486, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.333 | 0.145 | 0.184 |
| lift_1 | lift | 1.00 / step_budget | (0.486, 0.023, 0.034)→(0.494, 0.024, 0.195) | (0.500, 0.024, 0.026)→(0.504, 0.024, 0.179) | 0.272→0.205 | 1.00 / 37.000 | 0.082 | 0.594 |
| release_1 | release | 1.00 / step_budget | (0.494, 0.024, 0.195)→(0.489, 0.023, 0.220) | (0.504, 0.024, 0.179)→(0.497, 0.023, 0.021) | 0.205→0.276 | 1.00 / 2.000 | 0.145 | 1.555 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.240
- phase_score: 0.259
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.approach_1_score: 0.486
- phase_breakdown.release_1_score: 0.019
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.815
- grasp_place_fitness: 0.596

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.596
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.240
- **Median Q (composite search score)**: 0.303
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.347


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17262,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07314,"approach_1.speed":0.04182,"grasp_1.grip_force":27.96646},"optimized_scores":{"best_composite_score":0.29699,"best_fitness_score":0.53699,"best_task_score":0.1221},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.49582,-0.01703,-0.01149],"force_p95":1.42898,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54083,"mean_force":0.68127,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49342,-0.01571,0.2116]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.50044,-0.01555,-0.00109],"force_p95":0.406,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60263,"mean_force":0.08198,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48902,-0.01552,0.03481]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20526.0,"contact_point_centroid":[0.49324,0.0034,0.11251],"force_p95":0.07391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32003,"mean_force":0.05,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49197,-0.01563,0.11067]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18205.0,"contact_point_centroid":[0.49247,-0.0348,0.11356],"force_p95":0.07928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31532,"mean_force":0.05519,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49198,-0.01563,0.11089]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01578,-0.00202],"force_p95":0.13096,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14428,"mean_force":0.12482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49156,-0.01553,0.0344]},{"body_a":"world","body_b":"grasp_target","contact_count":2920.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49837,-0.00723,0.19053]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1182.0,"contact_point_centroid":[0.4977,-0.03487,0.19509],"force_p95":0.0765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12785,"mean_force":0.04477,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49702,-0.01575,0.19306]},{"body_a":"world","body_b":"grasp_target","contact_count":2756.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49742,-0.01526,0.05437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1103.0,"contact_point_centroid":[0.49871,0.00338,0.19525],"force_p95":0.07744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12231,"mean_force":0.04777,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.497,-0.01575,0.19303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4141.0,"contact_point_centroid":[0.48968,-0.03477,0.0356],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09658,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49032,-0.01552,0.03308]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5098.0,"contact_point_centroid":[0.49138,0.00353,0.03478],"force_p95":0.06841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08875,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49032,-0.01552,0.03308]}],"total_contact_groups":11},"final_pose_error":0.03128,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.4997,-0.01477,0.02228],"final_tcp_position":[0.49833,-0.01578,0.19508],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.54083,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2920.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49907,-0.01466,0.08178],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.05597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2756.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49857,-0.01559,0.04189],"tcp_start":[0.49907,-0.01466,0.08178],"tcp_to_object_dist_end":0.01672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01587,0.0259],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31248,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13122,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11039.0,"raw_peak_contact_force":0.14428,"tcp_end":[0.49029,-0.01552,0.03305],"tcp_start":[0.49857,-0.01559,0.04189],"tcp_to_object_dist_end":0.01518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50787,-0.01609,0.18018],"object_pos_start":[0.50368,-0.01587,0.0259],"object_to_goal_dist_end":0.22867,"object_to_goal_dist_start":0.31248,"object_z_max":0.17999,"peak_contact_force":0.08254,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38864.0,"raw_peak_contact_force":0.60263,"tcp_end":[0.49833,-0.01578,0.19508],"tcp_start":[0.49029,-0.01552,0.03305],"tcp_to_object_dist_end":0.0177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4997,-0.01477,0.02228],"object_pos_start":[0.50787,-0.01609,0.18018],"object_to_goal_dist_end":0.31544,"object_to_goal_dist_start":0.22867,"object_z_max":0.18032,"peak_contact_force":0.16944,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2395.0,"raw_peak_contact_force":1.54083,"tcp_end":[0.49334,-0.0157,0.22],"tcp_start":[0.49833,-0.01578,0.19508],"tcp_to_object_dist_end":0.19783,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11888,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05778,"approach_1.speed":0.05807,"grasp_1.grip_force":15.04934},"optimized_scores":{"best_composite_score":0.35576,"best_fitness_score":0.59576,"best_task_score":0.23956},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.5019,0.03925,-0.01135],"force_p95":1.45135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52045,"mean_force":0.6534,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50214,0.03828,0.21082]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.50946,0.03779,-0.00119],"force_p95":0.40525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62878,"mean_force":0.08481,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49749,0.03838,0.03406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.50102,0.05762,0.11496],"force_p95":0.08364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33739,"mean_force":0.05875,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50076,0.03842,0.1122]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20615.0,"contact_point_centroid":[0.50262,0.0195,0.11232],"force_p95":0.07866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31322,"mean_force":0.04993,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50065,0.03842,0.11072]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.0397,-0.0021],"force_p95":0.15288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20404,"mean_force":0.13049,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5001,0.03861,0.03359]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5036.0,"contact_point_centroid":[0.50049,0.0195,0.03369],"force_p95":0.07322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1716,"mean_force":0.04307,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49885,0.03851,0.03222]},{"body_a":"world","body_b":"grasp_target","contact_count":3204.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50235,0.0184,0.18193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1059.0,"contact_point_centroid":[0.50586,0.05785,0.19526],"force_p95":0.07925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12994,"mean_force":0.04926,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50574,0.03861,0.19245]},{"body_a":"world","body_b":"grasp_target","contact_count":2376.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50593,0.03844,0.0478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1226.0,"contact_point_centroid":[0.50826,0.01968,0.19398],"force_p95":0.07529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11706,"mean_force":0.04366,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50577,0.03861,0.19249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4202.0,"contact_point_centroid":[0.49905,0.05781,0.03492],"force_p95":0.08506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09117,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49886,0.03851,0.03223]}],"total_contact_groups":11},"final_pose_error":0.03153,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51825,0.03863,0.01827],"final_tcp_position":[0.50708,0.0387,0.19457],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.52045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3204.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50712,0.03716,0.06555],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2376.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50716,0.03918,0.04132],"tcp_start":[0.50712,0.03716,0.06555],"tcp_to_object_dist_end":0.01622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03907,0.02563],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21286,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15133,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11038.0,"raw_peak_contact_force":0.20404,"tcp_end":[0.49882,0.03851,0.03219],"tcp_start":[0.50716,0.03918,0.04132],"tcp_to_object_dist_end":0.01515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51676,0.03953,0.17982],"object_pos_start":[0.51247,0.03907,0.02563],"object_to_goal_dist_end":0.17657,"object_to_goal_dist_start":0.21286,"object_z_max":0.17963,"peak_contact_force":0.0811,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37756.0,"raw_peak_contact_force":0.62878,"tcp_end":[0.50708,0.0387,0.19457],"tcp_start":[0.49882,0.03851,0.03219],"tcp_to_object_dist_end":0.01766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51825,0.03863,0.01827],"object_pos_start":[0.51676,0.03953,0.17982],"object_to_goal_dist_end":0.21434,"object_to_goal_dist_start":0.17657,"object_z_max":0.17996,"peak_contact_force":0.06973,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2395.0,"raw_peak_contact_force":1.52045,"tcp_end":[0.50206,0.03828,0.21922],"tcp_start":[0.50708,0.0387,0.19457],"tcp_to_object_dist_end":0.2016,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38028,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16229,"approach_1.speed":0.03827,"grasp_1.grip_force":24.90702},"optimized_scores":{"best_composite_score":0.30252,"best_fitness_score":0.54252,"best_task_score":0.1379},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.46486,0.04699,-0.00856],"force_p95":1.39555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60364,"mean_force":0.4359,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47265,0.04708,0.21278]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.47985,0.0466,-0.00119],"force_p95":0.34764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55161,"mean_force":0.07854,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46833,0.04716,0.03791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.47121,0.06644,0.11752],"force_p95":0.08494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32299,"mean_force":0.0586,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47141,0.04724,0.1148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20912.0,"contact_point_centroid":[0.4734,0.02833,0.11521],"force_p95":0.07842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29463,"mean_force":0.04912,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47133,0.04723,0.11366]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.0487,-0.00211],"force_p95":0.15486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20465,"mean_force":0.13112,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47081,0.04743,0.03727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5261.0,"contact_point_centroid":[0.47114,0.02829,0.0373],"force_p95":0.07375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17737,"mean_force":0.04135,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46961,0.04731,0.03604]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4896,0.02109,0.23553]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.47578,0.0667,0.19644],"force_p95":0.07992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13212,"mean_force":0.04937,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47613,0.04747,0.19362]},{"body_a":"world","body_b":"grasp_target","contact_count":2856.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47771,0.0459,0.10165]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1226.0,"contact_point_centroid":[0.47883,0.02857,0.1951],"force_p95":0.07607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11902,"mean_force":0.04362,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47615,0.04747,0.19365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4203.0,"contact_point_centroid":[0.46943,0.06663,0.03847],"force_p95":0.08825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09449,"mean_force":0.05204,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46961,0.04731,0.03604]}],"total_contact_groups":11},"final_pose_error":0.03051,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47356,0.04551,0.02319],"final_tcp_position":[0.47745,0.04758,0.19555],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":17.50751,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":17.50751,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.48074,0.04364,0.1705],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":714.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2856.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47766,0.0481,0.04433],"tcp_start":[0.48074,0.04364,0.1705],"tcp_to_object_dist_end":0.019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04803,0.0256],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2907,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15302,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11264.0,"raw_peak_contact_force":0.20465,"tcp_end":[0.46958,0.04731,0.03601],"tcp_start":[0.47766,0.0481,0.04433],"tcp_to_object_dist_end":0.01676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48615,0.04849,0.17798],"object_pos_start":[0.4827,0.04803,0.0256],"object_to_goal_dist_end":0.21084,"object_to_goal_dist_start":0.2907,"object_z_max":0.1778,"peak_contact_force":0.08143,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38050.0,"raw_peak_contact_force":0.55161,"tcp_end":[0.47745,0.04758,0.19555],"tcp_start":[0.46958,0.04731,0.03601],"tcp_to_object_dist_end":0.01963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47356,0.04551,0.02319],"object_pos_start":[0.48615,0.04849,0.17798],"object_to_goal_dist_end":0.29719,"object_to_goal_dist_start":0.21084,"object_z_max":0.17812,"peak_contact_force":0.19474,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2453.0,"raw_peak_contact_force":1.60364,"tcp_end":[0.47257,0.04708,0.221],"tcp_start":[0.47745,0.04758,0.19555],"tcp_to_object_dist_end":0.19782,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```