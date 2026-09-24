## Search State

- **Seed**: 6
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1436 | 0.17 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

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

## Current Skill (Q=0.144) — your mutation base

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

- **Composite score**: 0.144
- **task_score** (E): 0.173
- **fitness_score**: 0.544  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre | 1.00 | 1.00 | 0.1665 |
| descend_grasp | 1.00 | 1.00 | 0.0790 |
| grasp_hold | 1.00 | 1.00 | 0.0123 |
| lift_up | 1.00 | 1.00 | 0.1176 |
| transport_arc | 0.00 | 1.00 | 0.1004 |
| release_object | 1.00 | 1.00 | 0.0245 |
| retract_away | 0.67 | 1.00 | 0.1534 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.138) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.496, 0.022, 0.138)→(0.494, 0.024, 0.059) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 9.429 | 0.123 |
| grasp_hold | grasp | 1.00 / step_budget | (0.494, 0.024, 0.059)→(0.486, 0.023, 0.050) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.025) | 0.271→0.272 | 1.00 / 36.667 | 0.155 | 0.190 |
| lift_up | lift | 1.00 / step_budget | (0.486, 0.023, 0.050)→(0.482, 0.023, 0.168) | (0.500, 0.024, 0.025)→(0.486, 0.023, 0.134) | 0.272→0.223 | 1.00 / 18.667 | 0.141 | 0.387 |
| transport_arc | approach | 0.00 / step_budget | (0.482, 0.023, 0.168)→(0.517, 0.075, 0.232) | (0.486, 0.023, 0.134)→(0.488, 0.051, 0.016) | 0.223→0.267 | 1.00 / 8.667 | 94251.324 | 1.486 |
| release_object | release | 1.00 / step_budget | (0.517, 0.075, 0.232)→(0.513, 0.074, 0.256) | (0.488, 0.051, 0.016)→(0.488, 0.051, 0.016) | 0.267→0.267 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_away | retract | 0.67 / step_budget | (0.513, 0.074, 0.256)→(0.585, 0.179, 0.338) | (0.488, 0.051, 0.016)→(0.488, 0.051, 0.016) | 0.267→0.267 | 1.00 / 4.000 | 27.129 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.232
- phase_score: 0.424
- phase_breakdown.place_at_goal_score: 0.137
- phase_breakdown.lift_clearance_score: 0.637
- phase_breakdown.approach_object_score: 0.822
- grasp_place_fitness: 0.573

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.573
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.232
- **Median Q (composite search score)**: 0.130
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.292


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26271,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.0613,"descend_grasp.descend_speed":0.02584,"lift_up.lift_height":0.18604,"transport_arc.arc_height":0.05836,"transport_arc.transport_speed":0.05444},"optimized_scores":{"best_composite_score":0.1301,"best_fitness_score":0.5301,"best_task_score":0.14548},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3175.0,"contact_point_centroid":[0.48474,0.048,-0.0024],"force_p95":0.23265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81602,"mean_force":0.14919,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50204,0.02169,0.25213]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.50114,-0.0153,-0.00118],"force_p95":0.23125,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3845,"mean_force":0.05995,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.48861,-0.01535,0.0521]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11490.0,"contact_point_centroid":[0.4877,-0.03407,0.11311],"force_p95":0.13949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.327,"mean_force":0.08456,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.48623,-0.01531,0.11551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13121.0,"contact_point_centroid":[0.48772,0.003,0.11938],"force_p95":0.11594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31095,"mean_force":0.07403,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.48625,-0.01531,0.12207]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":286.0,"contact_point_centroid":[0.48876,-0.03176,0.20718],"force_p95":0.21988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30035,"mean_force":0.13941,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48646,-0.01382,0.21226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":523.0,"contact_point_centroid":[0.48915,0.00374,0.2076],"force_p95":0.15588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26598,"mean_force":0.09611,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48645,-0.01316,0.21297]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50385,-0.01568,-0.00205],"force_p95":0.13801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1551,"mean_force":0.127,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.49137,-0.01537,0.05151]},{"body_a":"world","body_b":"grasp_target","contact_count":2100.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49866,-0.00698,0.21958]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49759,-0.01485,0.09895]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48392,0.04912,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51453,0.05202,0.27648]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48392,0.04912,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.54576,0.11451,0.33773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4177.0,"contact_point_centroid":[0.49177,0.00363,0.04969],"force_p95":0.08283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10723,"mean_force":0.05363,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.49018,-0.01536,0.05021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4174.0,"contact_point_centroid":[0.49157,-0.03443,0.05034],"force_p95":0.08388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08909,"mean_force":0.05355,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.49018,-0.01536,0.05021]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3510.0,"contact_point_centroid":[0.5021,0.0214,0.2542],"force_p95":0.01109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01626,"mean_force":0.01038,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50189,0.0214,0.2519]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.51643,0.05225,0.27383],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.00993,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5164,0.05228,0.27112]}],"total_contact_groups":15},"final_pose_error":0.02115,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.48392,0.04912,0.01602],"final_tcp_position":[0.57944,0.17567,0.38222],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.81602,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2100.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49949,-0.01433,0.13864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49844,-0.01542,0.05934],"tcp_start":[0.49949,-0.01433,0.13864],"tcp_to_object_dist_end":0.03376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50379,-0.01556,0.02566],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31242,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.141,"phase_name":"grasp_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10151.0,"raw_peak_contact_force":0.1551,"tcp_end":[0.49015,-0.01536,0.05018],"tcp_start":[0.49844,-0.01542,0.05934],"tcp_to_object_dist_end":0.02805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49028,-0.01493,0.17486],"object_pos_start":[0.50379,-0.01556,0.02566],"object_to_goal_dist_end":0.23593,"object_to_goal_dist_start":0.31242,"object_z_max":0.17467,"peak_contact_force":0.15153,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24756.0,"raw_peak_contact_force":0.3845,"subtask_id":"lift_clearance","tcp_end":[0.48671,-0.01531,0.21073],"tcp_start":[0.49015,-0.01536,0.05018],"tcp_to_object_dist_end":0.03605,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48392,0.04912,0.01602],"object_pos_start":[0.49028,-0.01493,0.17486],"object_to_goal_dist_end":0.28916,"object_to_goal_dist_start":0.23593,"object_z_max":0.17651,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7494.0,"raw_peak_contact_force":1.81602,"subtask_id":"place_at_goal","tcp_end":[0.5174,0.05221,0.27319],"tcp_start":[0.48671,-0.01531,0.21073],"tcp_to_object_dist_end":0.25935,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48392,0.04912,0.01602],"object_pos_start":[0.48392,0.04912,0.01602],"object_to_goal_dist_end":0.28916,"object_to_goal_dist_start":0.28916,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51351,0.05188,0.29719],"tcp_start":[0.5174,0.05221,0.27319],"tcp_to_object_dist_end":0.28274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48392,0.04912,0.01602],"object_pos_start":[0.48392,0.04912,0.01602],"object_to_goal_dist_end":0.28916,"object_to_goal_dist_start":0.28916,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57944,0.17567,0.38222],"tcp_start":[0.51351,0.05188,0.29719],"tcp_to_object_dist_end":0.39905,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34896,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.04692,"descend_grasp.descend_speed":0.04996,"lift_up.lift_height":0.10608,"transport_arc.arc_height":0.03058,"transport_arc.transport_speed":0.08128},"optimized_scores":{"best_composite_score":0.17335,"best_fitness_score":0.57335,"best_task_score":0.23197},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.52124,0.03099,-0.00238],"force_p95":0.18161,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40207,"mean_force":0.14272,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54064,0.08774,0.1659]},{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.50933,0.03781,-0.0013],"force_p95":0.27311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40314,"mean_force":0.06766,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.49704,0.038,0.05166]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8309.0,"contact_point_centroid":[0.49505,0.05664,0.08968],"force_p95":0.13306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33071,"mean_force":0.07517,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.4946,0.03782,0.09119]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8491.0,"contact_point_centroid":[0.4963,0.01948,0.08968],"force_p95":0.11761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3029,"mean_force":0.07187,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.49461,0.03782,0.09194]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3083.0,"contact_point_centroid":[0.5072,0.0706,0.14673],"force_p95":0.15902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3028,"mean_force":0.11685,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50544,0.0518,0.15073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.50873,0.03514,0.14725],"force_p95":0.1167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22088,"mean_force":0.07614,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50628,0.05274,0.15127]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5126,0.03968,-0.00215],"force_p95":0.16167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20561,"mean_force":0.13371,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.49988,0.03824,0.05103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.49993,0.01922,0.04901],"force_p95":0.08872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19056,"mean_force":0.05419,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.49869,0.03815,0.04968]},{"body_a":"world","body_b":"grasp_target","contact_count":2272.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.50254,0.01773,0.21876]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50592,0.03744,0.09815]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52131,0.03074,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55388,0.1045,0.17048]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.52131,0.03074,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.58601,0.13671,0.23439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4551.0,"contact_point_centroid":[0.49849,0.05727,0.05047],"force_p95":0.0917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09377,"mean_force":0.05012,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.49869,0.03815,0.04969]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1901.0,"contact_point_centroid":[0.54299,0.08976,0.16867],"force_p95":0.01212,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01066,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54269,0.0898,0.16642]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.55669,0.10499,0.16793],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00992,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5566,0.10507,0.16565]}],"total_contact_groups":15},"final_pose_error":0.01482,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.52131,0.03074,0.01602],"final_tcp_position":[0.62164,0.16873,0.28198],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273005.05137,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2272.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5075,0.0363,0.13767],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":28.04065,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.507,0.03881,0.05912],"tcp_start":[0.5075,0.0363,0.13767],"tcp_to_object_dist_end":0.03357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5126,0.03892,0.02533],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21306,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16347,"phase_name":"grasp_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10466.0,"raw_peak_contact_force":0.20561,"tcp_end":[0.49866,0.03814,0.04965],"tcp_start":[0.507,0.03881,0.05912],"tcp_to_object_dist_end":0.02805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.49907,0.03839,0.11134],"object_pos_start":[0.5126,0.03892,0.02533],"object_to_goal_dist_end":0.18878,"object_to_goal_dist_start":0.21306,"object_z_max":0.11123,"peak_contact_force":0.13525,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16953.0,"raw_peak_contact_force":0.40314,"subtask_id":"lift_clearance","tcp_end":[0.49469,0.03783,0.14374],"tcp_start":[0.49866,0.03814,0.04965],"tcp_to_object_dist_end":0.0327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52131,0.03074,0.01602],"object_pos_start":[0.49907,0.03839,0.11134],"object_to_goal_dist_end":0.21917,"object_to_goal_dist_start":0.18878,"object_z_max":0.12244,"peak_contact_force":273005.05137,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12055.0,"raw_peak_contact_force":1.40207,"subtask_id":"place_at_goal","tcp_end":[0.558,0.10519,0.16803],"tcp_start":[0.49469,0.03783,0.14374],"tcp_to_object_dist_end":0.1732,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52131,0.03074,0.01602],"object_pos_start":[0.52131,0.03074,0.01602],"object_to_goal_dist_end":0.21917,"object_to_goal_dist_start":0.21917,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5523,0.10417,0.19084],"tcp_start":[0.558,0.10519,0.16803],"tcp_to_object_dist_end":0.19214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.52131,0.03074,0.01602],"object_pos_start":[0.52131,0.03074,0.01602],"object_to_goal_dist_end":0.21917,"object_to_goal_dist_start":0.21917,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62164,0.16873,0.28198],"tcp_start":[0.5523,0.10417,0.19084],"tcp_to_object_dist_end":0.31598,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99567,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.16951,"descend_grasp.descend_speed":0.01446,"lift_up.lift_height":0.10983,"transport_arc.arc_height":0.10795,"transport_arc.transport_speed":0.06305},"optimized_scores":{"best_composite_score":0.12731,"best_fitness_score":0.52731,"best_task_score":0.14158},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2871.0,"contact_point_centroid":[0.45737,0.07223,-0.00232],"force_p95":0.12463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24104,"mean_force":0.13658,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4659,0.05137,0.22076]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.47977,0.0461,-0.00123],"force_p95":0.22212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37339,"mean_force":0.05873,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46816,0.04669,0.05299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1693.0,"contact_point_centroid":[0.46352,0.02591,0.15571],"force_p95":0.15618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33347,"mean_force":0.10873,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46146,0.04371,0.16077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7574.0,"contact_point_centroid":[0.46755,0.02822,0.09391],"force_p95":0.12217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32767,"mean_force":0.07857,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46573,0.04646,0.09708]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7197.0,"contact_point_centroid":[0.46591,0.0652,0.09172],"force_p95":0.13309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31651,"mean_force":0.08243,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46577,0.04646,0.09411]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1582.0,"contact_point_centroid":[0.46281,0.06162,0.15687],"force_p95":0.1376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30391,"mean_force":0.1115,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46132,0.04361,0.1616]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04868,-0.00214],"force_p95":0.16133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20829,"mean_force":0.13273,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.47083,0.04696,0.05221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3537.0,"contact_point_centroid":[0.47193,0.02803,0.04913],"force_p95":0.10604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19518,"mean_force":0.05903,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.46967,0.04685,0.05099]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.48935,0.0217,0.21932]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47759,0.04585,0.0994]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45735,0.07237,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.47369,0.06734,0.25929]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45735,0.07237,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51324,0.12986,0.3136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4012.0,"contact_point_centroid":[0.46963,0.06584,0.05081],"force_p95":0.09524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09691,"mean_force":0.0533,"phase_index":2.0,"phase_name":"grasp_hold","phase_type":"grasp","tcp_position_centroid":[0.46968,0.04685,0.051]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2771.0,"contact_point_centroid":[0.46699,0.05227,0.22633],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4665,0.05225,0.22416]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.47585,0.06768,0.25555],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.0099,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.47565,0.06768,0.25345]}],"total_contact_groups":15},"final_pose_error":0.05515,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.45735,0.07237,0.01602],"final_tcp_position":[0.55512,0.19117,0.3504],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.79808,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48022,0.04443,0.13854],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47772,0.04762,0.05954],"tcp_start":[0.48022,0.04443,0.13854],"tcp_to_object_dist_end":0.03391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48278,0.0477,0.02551],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29095,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15941,"phase_name":"grasp_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9349.0,"raw_peak_contact_force":0.20829,"tcp_end":[0.46964,0.04684,0.05096],"tcp_start":[0.47772,0.04762,0.05954],"tcp_to_object_dist_end":0.02866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.46923,0.04695,0.1148],"object_pos_start":[0.48278,0.0477,0.02551],"object_to_goal_dist_end":0.24323,"object_to_goal_dist_start":0.29095,"object_z_max":0.11468,"peak_contact_force":0.136,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14910.0,"raw_peak_contact_force":0.37339,"subtask_id":"lift_clearance","tcp_end":[0.46582,0.04647,0.14907],"tcp_start":[0.46964,0.04684,0.05096],"tcp_to_object_dist_end":0.03444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45735,0.07237,0.01602],"object_pos_start":[0.46923,0.04695,0.1148],"object_to_goal_dist_end":0.29324,"object_to_goal_dist_start":0.24323,"object_z_max":0.13497,"peak_contact_force":9748.79808,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8917.0,"raw_peak_contact_force":1.24104,"subtask_id":"place_at_goal","tcp_end":[0.47663,0.06767,0.25516],"tcp_start":[0.46582,0.04647,0.14907],"tcp_to_object_dist_end":0.23996,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45735,0.07237,0.01602],"object_pos_start":[0.45735,0.07237,0.01602],"object_to_goal_dist_end":0.29324,"object_to_goal_dist_start":0.29324,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4726,0.06716,0.28034],"tcp_start":[0.47663,0.06767,0.25516],"tcp_to_object_dist_end":0.26481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45735,0.07237,0.01602],"object_pos_start":[0.45735,0.07237,0.01602],"object_to_goal_dist_end":0.29324,"object_to_goal_dist_start":0.29324,"object_z_max":0.01602,"peak_contact_force":81.14225,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55512,0.19117,0.3504],"tcp_start":[0.4726,0.06716,0.28034],"tcp_to_object_dist_end":0.36808,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```