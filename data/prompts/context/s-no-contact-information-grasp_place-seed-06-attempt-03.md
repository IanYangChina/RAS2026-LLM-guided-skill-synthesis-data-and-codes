## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0707 | 0.25 | ❌ rejected |
| 2 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1415 | 0.25 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.071) — your mutation base

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

- **Composite score**: 0.071
- **task_score** (E): 0.246
- **fitness_score**: 0.491  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_to_object | 1.00 | 0.1569 |
| descend_to_grasp | 1.00 | 0.0843 |
| grasp_1 | 1.00 | 0.0117 |
| lift_above_goal | 1.00 | 0.1922 |
| approach_to_goal | 1.00 | 0.2091 |
| release_and_retract | 1.00 | 0.0962 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.027, 0.149) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.497, 0.027, 0.149)→(0.495, 0.024, 0.065) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.065)→(0.487, 0.024, 0.056) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 |
| lift_above_goal | lift | 1.00 / step_budget | (0.487, 0.024, 0.056)→(0.484, 0.024, 0.248) | (0.500, 0.024, 0.026)→(0.488, 0.034, 0.106) | 0.272→0.238 |
| approach_to_goal | approach | 1.00 / step_budget | (0.484, 0.024, 0.248)→(0.587, 0.182, 0.204) | (0.488, 0.034, 0.106)→(0.542, 0.101, 0.012) | 0.238→0.231 |
| release_and_retract | release | 1.00 / step_budget | (0.587, 0.182, 0.204)→(0.583, 0.181, 0.300) | (0.542, 0.101, 0.012)→(0.542, 0.101, 0.016) | 0.231→0.227 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.418
- phase_score: 0.633
- phase_breakdown.place_at_goal_score: 0.672
- phase_breakdown.reach_object_score: 0.268
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.lift_clearance_score: 0.390
- grasp_place_fitness: 0.661

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.661
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.418
- **Median Q (composite search score)**: 0.117
- **K-run variance**: 0.0258
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.409


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02548,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_goal.transport_speed":0.08262,"approach_to_object.approach_speed":0.17943,"descend_to_grasp.descend_speed":0.07822,"lift_above_goal.lift_distance":0.15048,"lift_above_goal.lift_speed":0.09553,"release_and_retract.retract_speed":0.17917},"optimized_scores":{"best_composite_score":0.11666,"best_fitness_score":0.53666,"best_task_score":0.17086},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1481.0,"contact_point_centroid":[0.54329,0.06698,-0.00271],"force_p95":0.30939,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58808,"mean_force":0.15576,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.55196,0.12185,0.22147]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50205,-0.014,-0.00139],"force_p95":0.26566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30247,"mean_force":0.06475,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.48969,-0.01424,0.05701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3935.0,"contact_point_centroid":[0.49002,0.00419,0.11171],"force_p95":0.14538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28456,"mean_force":0.10503,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.48743,-0.0142,0.11538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4201.0,"contact_point_centroid":[0.48996,-0.03248,0.11217],"force_p95":0.14626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27495,"mean_force":0.09983,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.48744,-0.0142,0.11593]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1455.0,"contact_point_centroid":[0.50498,0.03159,0.18627],"force_p95":0.14924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21168,"mean_force":0.1112,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.49905,0.01343,0.1912]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01563,-0.0021],"force_p95":0.15398,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20754,"mean_force":0.13035,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49208,-0.01427,0.0568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1607.0,"contact_point_centroid":[0.5053,-0.00325,0.18679],"force_p95":0.12569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17732,"mean_force":0.10047,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.49966,0.01469,0.19156]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49949,0.00429,0.22429]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49814,-0.01062,0.10501]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.54335,0.06713,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.57573,0.17324,0.29175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2899.0,"contact_point_centroid":[0.4911,0.00454,0.05202],"force_p95":0.09322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11099,"mean_force":0.07081,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01425,0.05557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3117.0,"contact_point_centroid":[0.49085,-0.03306,0.05243],"force_p95":0.09142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09411,"mean_force":0.06696,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01425,0.05557]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1371.0,"contact_point_centroid":[0.5562,0.12966,0.226],"force_p95":0.01173,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01626,"mean_force":0.01049,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.55586,0.12966,0.22375]},{"body_a":"left_finger","body_b":"right_finger","contact_count":669.0,"contact_point_centroid":[0.57665,0.17363,0.27225],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01038,"phase_index":5.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.57622,0.17362,0.26997]}],"total_contact_groups":14},"final_pose_error":0.02992,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54335,0.06713,0.01602],"final_tcp_position":[0.5763,0.17333,0.30677],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50002,-0.00698,0.14709],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12144,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49882,-0.01432,0.0643],"tcp_start":[0.50002,-0.00698,0.14709],"tcp_to_object_dist_end":0.03863,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50378,-0.01485,0.02563],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_success","tcp_end":[0.49093,-0.01425,0.05554],"tcp_start":[0.49882,-0.01432,0.0643],"tcp_to_object_dist_end":0.03255,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":417.0,"n_steps_budget":990.0,"object_pos_end":[0.49416,-0.01449,0.14998],"object_pos_start":[0.50378,-0.01485,0.02563],"object_to_goal_dist_end":0.24292,"object_to_goal_dist_start":0.31198,"object_z_max":0.14971,"phase_name":"lift_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.48752,-0.01419,0.18655],"tcp_start":[0.49093,-0.01425,0.05554],"tcp_to_object_dist_end":0.03717,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.54335,0.06713,0.01602],"object_pos_start":[0.49416,-0.01449,0.14998],"object_to_goal_dist_end":0.26504,"object_to_goal_dist_start":0.24292,"object_z_max":0.15876,"phase_name":"approach_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.57797,0.174,0.23663],"tcp_start":[0.48752,-0.01419,0.18655],"tcp_to_object_dist_end":0.24757,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":156.0,"n_steps_budget":600.0,"object_pos_end":[0.54335,0.06713,0.01602],"object_pos_start":[0.54335,0.06713,0.01602],"object_to_goal_dist_end":0.26504,"object_to_goal_dist_start":0.26504,"object_z_max":0.01602,"phase_name":"release_and_retract","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.57487,0.17267,0.33289],"tcp_start":[0.57797,0.174,0.23663],"tcp_to_object_dist_end":0.33547,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.375,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_goal.transport_speed":0.10336,"approach_to_object.approach_speed":0.17529,"descend_to_grasp.descend_speed":0.03359,"lift_above_goal.lift_distance":0.15025,"lift_above_goal.lift_speed":0.0324,"release_and_retract.retract_speed":0.12436},"optimized_scores":{"best_composite_score":0.24058,"best_fitness_score":0.66058,"best_task_score":0.41814},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":59.0,"contact_point_centroid":[0.60894,0.16434,-0.00546],"force_p95":1.22297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6449,"mean_force":0.69624,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.61077,0.15813,0.14099]},{"body_a":"world","body_b":"grasp_target","contact_count":1260.0,"contact_point_centroid":[0.61217,0.15744,-0.00242],"force_p95":0.13694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49463,"mean_force":0.12488,"phase_index":5.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.60895,0.15912,0.19446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4001.0,"contact_point_centroid":[0.54002,0.06781,0.16138],"force_p95":0.17841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27176,"mean_force":0.09765,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.54083,0.08651,0.16571]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.5087,0.03903,-0.00152],"force_p95":0.25024,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25872,"mean_force":0.10911,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.49822,0.03873,0.05616]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5885.0,"contact_point_centroid":[0.49514,0.05714,0.11536],"force_p95":0.11121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24997,"mean_force":0.08037,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.49582,0.03853,0.11871]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5581.0,"contact_point_centroid":[0.49471,0.01982,0.1122],"force_p95":0.11528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22147,"mean_force":0.0838,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.49582,0.03853,0.11549]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5009.0,"contact_point_centroid":[0.54423,0.1081,0.16021],"force_p95":0.114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2118,"mean_force":0.07545,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.54409,0.08986,0.16455]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03968,-0.00207],"force_p95":0.14266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18671,"mean_force":0.12774,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5005,0.03892,0.05663]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.50288,0.0272,0.2279]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50596,0.03995,0.10603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2973.0,"contact_point_centroid":[0.49952,0.02006,0.05245],"force_p95":0.0914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10578,"mean_force":0.06898,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49936,0.03883,0.05535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2968.0,"contact_point_centroid":[0.49961,0.05762,0.05205],"force_p95":0.09337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09371,"mean_force":0.07012,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49936,0.03883,0.05535]},{"body_a":"left_finger","body_b":"right_finger","contact_count":441.0,"contact_point_centroid":[0.61004,0.15932,0.19007],"force_p95":0.01405,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01076,"phase_index":5.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.60961,0.1593,0.18787]}],"total_contact_groups":13},"final_pose_error":0.02981,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6122,0.15744,0.01602],"final_tcp_position":[0.60977,0.15925,0.21064],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50744,0.04062,0.14895],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12304,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50729,0.03949,0.06441],"tcp_start":[0.50744,0.04062,0.14895],"tcp_to_object_dist_end":0.03874,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03919,0.02576],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21272,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_success","tcp_end":[0.49933,0.03882,0.05532],"tcp_start":[0.50729,0.03949,0.06441],"tcp_to_object_dist_end":0.03234,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.49865,0.03873,0.15142],"object_pos_start":[0.51246,0.03919,0.02576],"object_to_goal_dist_end":0.1859,"object_to_goal_dist_start":0.21272,"object_z_max":0.15115,"phase_name":"lift_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.49592,0.03853,0.186],"tcp_start":[0.49933,0.03882,0.05532],"tcp_to_object_dist_end":0.03468,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.61324,0.15843,0.00425],"object_pos_start":[0.49865,0.03873,0.15142],"object_to_goal_dist_end":0.1422,"object_to_goal_dist_start":0.1859,"object_z_max":0.15167,"phase_name":"approach_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.61275,0.16019,0.14028],"tcp_start":[0.49592,0.03853,0.186],"tcp_to_object_dist_end":0.13604,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":165.0,"n_steps_budget":600.0,"object_pos_end":[0.6122,0.15744,0.01602],"object_pos_start":[0.61324,0.15843,0.00425],"object_to_goal_dist_end":0.13079,"object_to_goal_dist_start":0.1422,"object_z_max":0.01643,"phase_name":"release_and_retract","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.60716,0.15838,0.2362],"tcp_start":[0.61275,0.16019,0.14028],"tcp_to_object_dist_end":0.22024,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92488,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_goal.transport_speed":0.09964,"approach_to_object.approach_speed":0.1114,"descend_to_grasp.descend_speed":0.07399,"lift_above_goal.lift_distance":0.33456,"lift_above_goal.lift_speed":0.08594,"release_and_retract.retract_speed":0.12883},"optimized_scores":{"best_composite_score":-0.145,"best_fitness_score":0.275,"best_task_score":0.14945},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2101.0,"contact_point_centroid":[0.47113,0.07607,-0.00242],"force_p95":0.20699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52171,"mean_force":0.14048,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.46832,0.04726,0.28254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4009.0,"contact_point_centroid":[0.46942,0.06535,0.10965],"force_p95":0.14618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28633,"mean_force":0.09971,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.46735,0.04716,0.11386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3603.0,"contact_point_centroid":[0.46864,0.02881,0.10754],"force_p95":0.16456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28526,"mean_force":0.10852,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.46735,0.04716,0.11186]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48273,0.04867,-0.00209],"force_p95":0.15079,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20246,"mean_force":0.12938,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47185,0.04763,0.0579]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49113,0.03085,0.22931]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47903,0.04828,0.10684]},{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.47072,0.07738,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.51871,0.1293,0.30166]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.47072,0.07738,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.56793,0.21213,0.28802]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2660.0,"contact_point_centroid":[0.46987,0.02869,0.05308],"force_p95":0.09831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11055,"mean_force":0.07671,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47077,0.04752,0.05676]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3234.0,"contact_point_centroid":[0.47083,0.06623,0.05334],"force_p95":0.08873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08907,"mean_force":0.06437,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47078,0.04752,0.05676]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1894.0,"contact_point_centroid":[0.46871,0.04728,0.30284],"force_p95":0.01144,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01563,"mean_force":0.01067,"phase_index":3.0,"phase_name":"lift_above_goal","phase_type":"lift","tcp_position_centroid":[0.46836,0.04726,0.30053]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2248.0,"contact_point_centroid":[0.5193,0.12955,0.30368],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01052,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.51885,0.12953,0.30147]},{"body_a":"left_finger","body_b":"right_finger","contact_count":704.0,"contact_point_centroid":[0.56869,0.21255,0.2683],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01032,"phase_index":5.0,"phase_name":"release_and_retract","phase_type":"release","tcp_position_centroid":[0.56826,0.21252,0.26617]}],"total_contact_groups":13},"final_pose_error":0.02999,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47072,0.07738,0.01602],"final_tcp_position":[0.56862,0.2123,0.30437],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.48223,0.04854,0.14994],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12393,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.47836,0.04827,0.06487],"tcp_start":[0.48223,0.04854,0.14994],"tcp_to_object_dist_end":0.03909,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48265,0.04789,0.02567],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29076,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_success","tcp_end":[0.47075,0.04752,0.05673],"tcp_start":[0.47836,0.04827,0.06487],"tcp_to_object_dist_end":0.03327,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.47072,0.07738,0.01602],"object_pos_start":[0.48265,0.04789,0.02567],"object_to_goal_dist_end":0.28512,"object_to_goal_dist_start":0.29076,"object_z_max":0.14309,"phase_name":"lift_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.46909,0.04733,0.37143],"tcp_start":[0.47075,0.04752,0.05673],"tcp_to_object_dist_end":0.35668,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":531.0,"n_steps_budget":1000.0,"object_pos_end":[0.47072,0.07738,0.01602],"object_pos_start":[0.47072,0.07738,0.01602],"object_to_goal_dist_end":0.28512,"object_to_goal_dist_start":0.28512,"object_z_max":0.01602,"phase_name":"approach_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.5703,0.21317,0.2343],"tcp_start":[0.46909,0.04733,0.37143],"tcp_to_object_dist_end":0.27568,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":163.0,"n_steps_budget":600.0,"object_pos_end":[0.47072,0.07738,0.01602],"object_pos_start":[0.47072,0.07738,0.01602],"object_to_goal_dist_end":0.28512,"object_to_goal_dist_start":0.28512,"object_z_max":0.01602,"phase_name":"release_and_retract","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.56725,0.21148,0.33044],"tcp_start":[0.5703,0.21317,0.2343],"tcp_to_object_dist_end":0.35519,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```