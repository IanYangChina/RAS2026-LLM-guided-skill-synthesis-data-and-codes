## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.1417 | 0.25 | ❌ rejected |
| 1 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.1416 | 0.25 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | -0.5159 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.516) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
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
- id: push_1
  type: push
  generator: impedance_motion
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
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    yaw_angle:
      type: angle
      range:
      - 0.1
      - 1.57

```

## Design Metrics

- **Composite score**: -0.516
- **task_score** (E): 0.148
- **fitness_score**: 0.164  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_pre_grasp | 0.00 | 1.00 | 0.1318 |
| descend_grasp | 0.00 | 1.00 | 0.0560 |
| grasp_object | 1.00 | 1.00 | 0.0025 |
| lift_object | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_pre_grasp | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.428, 0.052, 0.210) | (0.500, 0.024, 0.030)→(0.459, 0.028, 0.016) | 0.269→0.293 | 1.00 / 5.000 | 304.415 | 1547.497 |
| descend_grasp | descend | 0.00 / step_budget | (0.428, 0.052, 0.210)→(0.462, 0.049, 0.170) | (0.459, 0.028, 0.016)→(0.459, 0.028, 0.016) | 0.293→0.293 | 1.00 / 5.667 | 331.211 | 923.882 |
| grasp_object | grasp | 1.00 / step_budget | (0.462, 0.049, 0.170)→(0.461, 0.048, 0.168) | (0.459, 0.028, 0.016)→(0.459, 0.028, 0.016) | 0.293→0.293 | 1.00 / 9.667 | 68.978 | 463.980 |
| lift_object | lift | 0.00 / guard_failure | (0.461, 0.048, 0.168)→(0.461, 0.048, 0.168) | (0.459, 0.028, 0.016)→(0.459, 0.028, 0.016) | 0.293→0.293 | 1.00 / 9.667 | 78.212 | 78.212 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.214
- phase_score: 0.071
- phase_breakdown.reach_pre_grasp_score: 0.070
- phase_breakdown.lift_clear_score: 0.189
- phase_breakdown.transport_goal_score: 0.000
- grasp_place_fitness: 0.196

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.196
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.214
- **Median Q (composite search score)**: -0.527
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.277


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":14.0,"average_failure_rate":0.25926,"average_mean_iterations":58.2037,"average_solve_count":54.0,"average_success_count":40.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_pre_grasp.arc_height":0.02651,"align_pre_grasp.speed":0.07401,"descend_grasp.descend_offset_z":0.01191,"descend_release.descend_speed":0.06405,"grasp_object.grasp_duration":0.06163,"lift_object.guard_force_threshold":11.05993,"release_object.release_duration":0.1153,"retract_after_place.retract_speed":0.10829,"transport_to_goal.transport_arc_height":0.07416,"transport_to_goal.transport_speed":0.09262},"optimized_scores":{"best_composite_score":-0.52697,"best_fitness_score":0.15303,"best_task_score":0.10652},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63227,0.01057,-0.00046],"force_p95":203.13073,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1347.47122,"mean_force":203.65601,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39753,0.00987,0.13397]},{"body_a":"world","body_b":"link6","contact_count":942.0,"contact_point_centroid":[0.64563,0.01362,-0.00025],"force_p95":415.44544,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":917.48768,"mean_force":287.37495,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44537,0.00942,0.18939]},{"body_a":"link5","body_b":"hand","contact_count":26.0,"contact_point_centroid":[0.52953,0.09926,0.12327],"force_p95":345.76478,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.56272,"mean_force":207.08644,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46354,0.00537,0.15816]},{"body_a":"world","body_b":"link6","contact_count":446.0,"contact_point_centroid":[0.70111,0.00103,-0.00013],"force_p95":104.42429,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.34461,"mean_force":71.88915,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46373,0.00161,0.15227]},{"body_a":"link5","body_b":"hand","contact_count":501.0,"contact_point_centroid":[0.53721,0.09635,0.11138],"force_p95":134.78782,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.51504,"mean_force":37.46558,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46372,0.00173,0.15242]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.70138,0.00112,-0.00012],"force_p95":81.36206,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.36206,"mean_force":81.36206,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46374,0.00144,0.15208]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.54004,0.09584,0.10984],"force_p95":18.22141,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.22141,"mean_force":18.22141,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46374,0.00144,0.15208]},{"body_a":"grasp_target","body_b":"link7","contact_count":264.0,"contact_point_centroid":[0.4929,-0.02589,0.03937],"force_p95":1.14531,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.32438,"mean_force":0.50929,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38669,0.00614,0.10074]},{"body_a":"grasp_target","body_b":"hand","contact_count":264.0,"contact_point_centroid":[0.47994,-0.03033,0.05338],"force_p95":2.56702,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.04262,"mean_force":0.57413,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.38699,0.00612,0.10006]},{"body_a":"world","body_b":"grasp_target","contact_count":3373.0,"contact_point_centroid":[0.4719,-0.01931,-0.00269],"force_p95":0.40724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39722,"mean_force":0.18201,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.41224,0.00967,0.1474]},{"body_a":"world","body_b":"grasp_target","contact_count":3876.0,"contact_point_centroid":[0.46095,-0.02016,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44589,0.00926,0.18894]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46095,-0.02016,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46373,0.00163,0.15229]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.46095,-0.02016,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46374,0.00144,0.15208]},{"body_a":"left_finger","body_b":"right_finger","contact_count":351.0,"contact_point_centroid":[0.46579,0.00125,0.15044],"force_p95":0.01366,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01083,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46374,0.00144,0.15208]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.46563,0.00139,0.15117],"force_p95":0.01076,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01076,"mean_force":0.01076,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46374,0.00144,0.15208]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.52739,0.01041,-0.00281],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37399,0.00508,0.05151]}],"total_contact_groups":16},"final_pose_error":0.2,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.46095,-0.02016,0.01602],"final_tcp_position":[0.46374,0.00144,0.15207],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1347.47122,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46095,-0.02016,0.01602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.33591,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":195.00616,"phase_name":"align_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4808.0,"raw_peak_contact_force":1347.47122,"subtask_id":"reach_pre_grasp","tcp_end":[0.41391,0.01531,0.17259],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16728,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.46095,-0.02016,0.01602],"object_pos_start":[0.46095,-0.02016,0.01602],"object_to_goal_dist_end":0.33591,"object_to_goal_dist_start":0.33591,"object_z_max":0.01602,"peak_contact_force":362.15945,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4844.0,"raw_peak_contact_force":917.48768,"tcp_end":[0.46359,0.00474,0.15593],"tcp_start":[0.41391,0.01531,0.17259],"tcp_to_object_dist_end":0.14214,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46095,-0.02016,0.01602],"object_pos_start":[0.46095,-0.02016,0.01602],"object_to_goal_dist_end":0.33591,"object_to_goal_dist_start":0.33591,"object_z_max":0.01602,"peak_contact_force":65.66848,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3098.0,"raw_peak_contact_force":256.34461,"tcp_end":[0.46374,0.00144,0.15208],"tcp_start":[0.46359,0.00474,0.15593],"tcp_to_object_dist_end":0.13779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.46095,-0.02016,0.01602],"object_pos_start":[0.46095,-0.02016,0.01602],"object_to_goal_dist_end":0.33591,"object_to_goal_dist_start":0.33591,"object_z_max":0.01602,"peak_contact_force":81.36206,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10.0,"raw_peak_contact_force":81.36206,"subtask_id":"lift_clear","tcp_end":[0.46374,0.00144,0.15207],"tcp_start":[0.46374,0.00144,0.15208],"tcp_to_object_dist_end":0.13778,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.1,"average_solve_count":40.0,"average_success_count":40.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_pre_grasp.arc_height":0.05406,"align_pre_grasp.speed":0.08913,"descend_grasp.descend_offset_z":0.00023,"descend_release.descend_speed":0.04764,"grasp_object.grasp_duration":0.08858,"lift_object.guard_force_threshold":11.92968,"release_object.release_duration":0.09241,"retract_after_place.retract_speed":0.09888,"transport_to_goal.transport_arc_height":0.06431,"transport_to_goal.transport_speed":0.07254},"optimized_scores":{"best_composite_score":-0.4838,"best_fitness_score":0.1962,"best_task_score":0.21398},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":869.0,"contact_point_centroid":[0.6134,0.03597,-0.00043],"force_p95":268.62427,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1643.19697,"mean_force":233.0091,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.39856,0.03319,0.16246]},{"body_a":"world","body_b":"link6","contact_count":990.0,"contact_point_centroid":[0.63193,0.06308,-0.00024],"force_p95":537.54693,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":945.99665,"mean_force":379.85199,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44837,0.06201,0.21017]},{"body_a":"world","body_b":"link6","contact_count":444.0,"contact_point_centroid":[0.67582,0.07393,-0.00013],"force_p95":78.36524,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":478.01268,"mean_force":71.49893,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46201,0.06648,0.16951]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67591,0.07402,-0.00013],"force_p95":77.42679,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.42679,"mean_force":77.42679,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46201,0.06654,0.1694]},{"body_a":"grasp_target","body_b":"link7","contact_count":113.0,"contact_point_centroid":[0.48668,0.02554,0.03615],"force_p95":3.72196,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.03548,"mean_force":0.84402,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37815,0.01223,0.09041]},{"body_a":"grasp_target","body_b":"hand","contact_count":94.0,"contact_point_centroid":[0.4833,0.04612,0.05117],"force_p95":2.77626,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.22422,"mean_force":0.96251,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37751,0.01197,0.08526]},{"body_a":"world","body_b":"grasp_target","contact_count":3736.0,"contact_point_centroid":[0.48258,0.05164,-0.00225],"force_p95":0.31828,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24244,"mean_force":0.15671,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.41143,0.03163,0.17114]},{"body_a":"grasp_target","body_b":"link6","contact_count":60.0,"contact_point_centroid":[0.52296,0.03539,0.01692],"force_p95":0.86362,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.91573,"mean_force":0.46714,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37262,0.0119,0.08643]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47656,0.05402,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44848,0.06203,0.20991]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47656,0.05402,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46201,0.06648,0.16952]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47656,0.05402,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46201,0.06654,0.1694]},{"body_a":"left_finger","body_b":"right_finger","contact_count":337.0,"contact_point_centroid":[0.46403,0.06656,0.16795],"force_p95":0.01397,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01121,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46201,0.06653,0.1694]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5.0,"contact_point_centroid":[0.46442,0.06662,0.16601],"force_p95":0.0096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0096,"mean_force":0.0096,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46201,0.06654,0.1694]},{"body_a":"world","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.52164,0.01646,-0.00287],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.3678,0.0112,0.05574]}],"total_contact_groups":14},"final_pose_error":0.2,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.47656,0.05402,0.01602],"final_tcp_position":[0.46201,0.06654,0.1694],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1643.19697,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47656,0.05402,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.23128,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":319.24659,"phase_name":"align_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4889.0,"raw_peak_contact_force":1643.19697,"subtask_id":"reach_pre_grasp","tcp_end":[0.43202,0.06087,0.23362],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22221,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47656,0.05402,0.01602],"object_pos_start":[0.47656,0.05402,0.01602],"object_to_goal_dist_end":0.23128,"object_to_goal_dist_start":0.23128,"object_z_max":0.01602,"peak_contact_force":322.14607,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4990.0,"raw_peak_contact_force":945.99665,"tcp_end":[0.46214,0.0663,0.17069],"tcp_start":[0.43202,0.06087,0.23362],"tcp_to_object_dist_end":0.15583,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47656,0.05402,0.01602],"object_pos_start":[0.47656,0.05402,0.01602],"object_to_goal_dist_end":0.23128,"object_to_goal_dist_start":0.23128,"object_z_max":0.01602,"peak_contact_force":72.82539,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2581.0,"raw_peak_contact_force":478.01268,"tcp_end":[0.46201,0.06654,0.1694],"tcp_start":[0.46214,0.0663,0.17069],"tcp_to_object_dist_end":0.15457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47656,0.05402,0.01602],"object_pos_start":[0.47656,0.05402,0.01602],"object_to_goal_dist_end":0.23128,"object_to_goal_dist_start":0.23128,"object_z_max":0.01602,"peak_contact_force":77.42679,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10.0,"raw_peak_contact_force":77.42679,"subtask_id":"lift_clear","tcp_end":[0.46201,0.06654,0.1694],"tcp_start":[0.46201,0.06654,0.1694],"tcp_to_object_dist_end":0.15457,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.7,"average_solve_count":40.0,"average_success_count":40.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_pre_grasp.arc_height":0.14395,"align_pre_grasp.speed":0.14952,"descend_grasp.descend_offset_z":-0.00428,"descend_release.descend_speed":0.06133,"grasp_object.grasp_duration":0.13719,"lift_object.guard_force_threshold":15.63644,"release_object.release_duration":0.05051,"retract_after_place.retract_speed":0.06375,"transport_to_goal.transport_arc_height":0.04415,"transport_to_goal.transport_speed":0.09512},"optimized_scores":{"best_composite_score":-0.53685,"best_fitness_score":0.14315,"best_task_score":0.12417},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":865.0,"contact_point_centroid":[0.60885,0.05733,-0.00042],"force_p95":429.1314,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1651.82172,"mean_force":294.12898,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.40879,0.05338,0.18057]},{"body_a":"world","body_b":"link6","contact_count":998.0,"contact_point_centroid":[0.64017,0.08257,-0.00027],"force_p95":455.24713,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":908.16135,"mean_force":341.15106,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44967,0.07778,0.20623]},{"body_a":"world","body_b":"link6","contact_count":446.0,"contact_point_centroid":[0.66799,0.07859,-0.00013],"force_p95":77.45022,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":657.58192,"mean_force":72.27778,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45872,0.0766,0.18202]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.6681,0.07856,-0.00013],"force_p95":75.84682,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.84682,"mean_force":75.84682,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45871,0.07658,0.1819]},{"body_a":"grasp_target","body_b":"hand","contact_count":55.0,"contact_point_centroid":[0.46239,0.04378,0.04294],"force_p95":3.70544,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.06061,"mean_force":1.51589,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.3778,0.01978,0.0662]},{"body_a":"grasp_target","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.48198,0.02897,0.01628],"force_p95":3.02707,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.00618,"mean_force":0.77731,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.37257,0.01992,0.06995]},{"body_a":"world","body_b":"grasp_target","contact_count":3838.0,"contact_point_centroid":[0.44505,0.05122,-0.00217],"force_p95":0.18353,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.2452,"mean_force":0.14347,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.41978,0.04987,0.18613]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43865,0.05164,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44969,0.07777,0.20619]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.43865,0.05164,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45872,0.0766,0.18203]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43865,0.05164,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45871,0.07658,0.1819]},{"body_a":"left_finger","body_b":"right_finger","contact_count":334.0,"contact_point_centroid":[0.46058,0.07671,0.18046],"force_p95":0.01382,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01131,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45871,0.07658,0.1819]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.46045,0.07669,0.18073],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.01092,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45871,0.07658,0.1819]},{"body_a":"world","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.52408,0.01816,-0.00302],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.36928,0.01929,0.05309]}],"total_contact_groups":13},"final_pose_error":0.2,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.43865,0.05164,0.01602],"final_tcp_position":[0.45871,0.07658,0.18189],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1651.82172,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43865,0.05164,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31291,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":398.99129,"phase_name":"align_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4823.0,"raw_peak_contact_force":1651.82172,"subtask_id":"reach_pre_grasp","tcp_end":[0.43956,0.0803,0.2228],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20876,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43865,0.05164,0.01602],"object_pos_start":[0.43865,0.05164,0.01602],"object_to_goal_dist_end":0.31291,"object_to_goal_dist_start":0.31291,"object_z_max":0.01602,"peak_contact_force":309.32673,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4998.0,"raw_peak_contact_force":908.16135,"tcp_end":[0.45879,0.07658,0.18287],"tcp_start":[0.43956,0.0803,0.2228],"tcp_to_object_dist_end":0.16991,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43865,0.05164,0.01602],"object_pos_start":[0.43865,0.05164,0.01602],"object_to_goal_dist_end":0.31291,"object_to_goal_dist_start":0.31291,"object_z_max":0.01602,"peak_contact_force":68.44088,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2580.0,"raw_peak_contact_force":657.58192,"tcp_end":[0.45871,0.07658,0.1819],"tcp_start":[0.45879,0.07658,0.18287],"tcp_to_object_dist_end":0.16894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43865,0.05164,0.01602],"object_pos_start":[0.43865,0.05164,0.01602],"object_to_goal_dist_end":0.31291,"object_to_goal_dist_start":0.31291,"object_z_max":0.01602,"peak_contact_force":75.84682,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9.0,"raw_peak_contact_force":75.84682,"subtask_id":"lift_clear","tcp_end":[0.45871,0.07658,0.18189],"tcp_start":[0.45871,0.07658,0.1819],"tcp_to_object_dist_end":0.16894,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```