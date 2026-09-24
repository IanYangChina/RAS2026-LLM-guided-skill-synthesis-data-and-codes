## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=-0.141) — your mutation base

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

- **Composite score**: -0.141
- **task_score** (E): 0.250
- **fitness_score**: 0.339  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| align_1 | 0.00 | 0.2373 |
| lift_1 | 0.67 | 0.1438 |
| push_1 | 0.00 | 0.1125 |
| approach_1 | 1.00 | 0.1181 |
| approach_2 | 1.00 | 0.0023 |
| descend_1 | 1.00 | 0.0662 |
| grasp_1 | 1.00 | 0.0124 |
| rotate_1 | 0.67 | 0.1621 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| align_1 | align | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.574, 0.155, 0.137) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| lift_1 | lift | 0.67 / step_budget | (0.574, 0.155, 0.137)→(0.506, 0.044, 0.140) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| push_1 | push | 0.00 / step_budget | (0.506, 0.044, 0.140)→(0.554, 0.133, 0.102) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| approach_1 | approach | 1.00 / step_budget | (0.554, 0.133, 0.102)→(0.500, 0.033, 0.121) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| approach_2 | approach | 1.00 / step_budget | (0.500, 0.033, 0.121)→(0.499, 0.031, 0.120) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.499, 0.031, 0.120)→(0.495, 0.025, 0.054) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.054)→(0.486, 0.025, 0.045) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 |
| rotate_1 | rotate | 0.67 / step_budget | (0.486, 0.025, 0.045)→(0.570, 0.158, 0.081) | (0.500, 0.025, 0.026)→(0.540, 0.125, 0.016) | 0.271→0.216 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.363
- phase_score: 0.246
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.874
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.168
- grasp_place_fitness: 0.396

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.396
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.363
- **Median Q (composite search score)**: -0.159
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.369


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48322,"average_solve_count":298.0,"average_success_count":298.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00281,"approach_2.speed":0.03829,"lift_1.lift_height":0.23523,"push_1.push_distance":0.15396,"push_1.push_speed":0.01662,"rotate_1.yaw_angle":1.48285},"optimized_scores":{"best_composite_score":-0.1814,"best_fitness_score":0.2986,"best_task_score":0.17023},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2622.0,"contact_point_centroid":[0.52123,0.03988,-0.003],"force_p95":0.53273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65517,"mean_force":0.25148,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.52567,0.06284,0.05925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5328.0,"contact_point_centroid":[0.50409,0.03836,0.04814],"force_p95":0.19769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51851,"mean_force":0.10494,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50394,0.01999,0.04909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8204.0,"contact_point_centroid":[0.50596,0.00313,0.04932],"force_p95":0.18532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26358,"mean_force":0.10054,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50472,0.02173,0.0494]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01568,-0.00213],"force_p95":0.15796,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21225,"mean_force":0.13198,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49166,-0.01422,0.04642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.49191,0.00497,0.0467],"force_p95":0.06909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14907,"mean_force":0.04341,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49046,-0.01422,0.04511]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.50382,-0.01567,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54361,0.08925,0.17811]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54643,0.0938,0.1693]},{"body_a":"world","body_b":"grasp_target","contact_count":3504.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54027,0.0808,0.13135]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50299,-0.00677,0.12316]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49951,-0.01084,0.08863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5212.0,"contact_point_centroid":[0.4903,-0.03347,0.04855],"force_p95":0.06608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07237,"mean_force":0.04242,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49047,-0.01422,0.04512]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1087.0,"contact_point_centroid":[0.55108,0.11195,0.07334],"force_p95":0.01264,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01067,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.55066,0.11202,0.07096]}],"total_contact_groups":13},"final_pose_error":0.08424,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53049,0.07133,0.01602],"final_tcp_position":[0.56001,0.13006,0.07536],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2152,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51785,0.02634,0.22441],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.20328,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.57499,0.15515,0.12396],"tcp_start":[0.51785,0.02634,0.22441],"tcp_to_object_dist_end":0.20938,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.50373,-0.00599,0.12393],"tcp_start":[0.57499,0.15515,0.12396],"tcp_to_object_dist_end":0.09839,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.50224,-0.00766,0.12251],"tcp_start":[0.50373,-0.00599,0.12393],"tcp_to_object_dist_end":0.09684,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.49883,-0.01421,0.05428],"tcp_start":[0.50224,-0.00766,0.12251],"tcp_to_object_dist_end":0.02874,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5038,-0.01492,0.02554],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49043,-0.01421,0.04508],"tcp_start":[0.49883,-0.01421,0.05428],"tcp_to_object_dist_end":0.02368,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53049,0.07133,0.01602],"object_pos_start":[0.5038,-0.01492,0.02554],"object_to_goal_dist_end":0.26559,"object_to_goal_dist_start":0.31208,"object_z_max":0.02932,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.56001,0.13006,0.07536],"tcp_start":[0.49043,-0.01421,0.04508],"tcp_to_object_dist_end":0.08856,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42308,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00035,"approach_2.speed":0.06213,"lift_1.lift_height":0.05946,"push_1.push_distance":0.11733,"push_1.push_speed":0.02295,"rotate_1.yaw_angle":0.82216},"optimized_scores":{"best_composite_score":-0.0843,"best_fitness_score":0.3957,"best_task_score":0.36306},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2269.0,"contact_point_centroid":[0.53562,0.10174,-0.00256],"force_p95":0.50163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71763,"mean_force":0.24894,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.53912,0.10947,0.0631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7100.0,"contact_point_centroid":[0.51805,0.09704,0.05243],"force_p95":0.18224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51513,"mean_force":0.09804,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.51921,0.07795,0.05284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10637.0,"contact_point_centroid":[0.52404,0.06275,0.05326],"force_p95":0.17055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29973,"mean_force":0.09228,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.52152,0.08173,0.05399]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.51251,0.03972,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03983,-0.00202],"force_p95":0.13064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13143,"mean_force":0.12462,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50017,0.03977,0.0462]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54255,0.10279,0.10813]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52989,0.08512,0.08196]},{"body_a":"world","body_b":"grasp_target","contact_count":2192.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52862,0.08338,0.10296]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51103,0.04606,0.11846]},{"body_a":"world","body_b":"grasp_target","contact_count":812.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50787,0.04292,0.08663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4855.0,"contact_point_centroid":[0.49845,0.05892,0.04827],"force_p95":0.07757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10293,"mean_force":0.04477,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49896,0.03967,0.04485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5580.0,"contact_point_centroid":[0.50044,0.02046,0.047],"force_p95":0.07364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10043,"mean_force":0.04005,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49896,0.03967,0.04485]},{"body_a":"left_finger","body_b":"right_finger","contact_count":695.0,"contact_point_centroid":[0.57322,0.16341,0.08281],"force_p95":0.01335,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01078,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.57312,0.16358,0.08051]}],"total_contact_groups":13},"final_pose_error":0.03628,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55134,0.14714,0.01602],"final_tcp_position":[0.57998,0.1743,0.08402],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17132,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":450.0,"n_steps_budget":900.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51342,0.04939,0.08409],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.05887,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.54656,0.11435,0.08439],"tcp_start":[0.51342,0.04939,0.08409],"tcp_to_object_dist_end":0.10068,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.51163,0.04663,0.11889],"tcp_start":[0.54656,0.11435,0.08439],"tcp_to_object_dist_end":0.09313,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.51027,0.04542,0.11822],"tcp_start":[0.51163,0.04663,0.11889],"tcp_to_object_dist_end":0.0924,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.50738,0.04043,0.05434],"tcp_start":[0.51027,0.04542,0.11822],"tcp_to_object_dist_end":0.02879,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.03999,0.02591],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21218,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49893,0.03967,0.04481],"tcp_start":[0.50738,0.04043,0.05434],"tcp_to_object_dist_end":0.0232,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55134,0.14714,0.01602],"object_pos_start":[0.51238,0.03999,0.02591],"object_to_goal_dist_end":0.15198,"object_to_goal_dist_start":0.21218,"object_z_max":0.03908,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.57998,0.1743,0.08402],"tcp_start":[0.49893,0.03967,0.04481],"tcp_to_object_dist_end":0.07863,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51293,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00967,"approach_2.speed":0.02156,"lift_1.lift_height":0.08792,"push_1.push_distance":0.1167,"push_1.push_speed":0.03891,"rotate_1.yaw_angle":0.83853},"optimized_scores":{"best_composite_score":-0.15875,"best_fitness_score":0.32125,"best_task_score":0.21576},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1963.0,"contact_point_centroid":[0.51168,0.10143,-0.00269],"force_p95":0.48319,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67843,"mean_force":0.26042,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.51584,0.10607,0.06126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8121.0,"contact_point_centroid":[0.49657,0.10492,0.05378],"force_p95":0.18182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52244,"mean_force":0.09583,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49844,0.08593,0.05448]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11446.0,"contact_point_centroid":[0.50438,0.07103,0.05461],"force_p95":0.16555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31965,"mean_force":0.09066,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50166,0.08976,0.05568]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.4827,0.04873,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53682,0.07971,0.21414]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48268,0.04886,-0.00202],"force_p95":0.13133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13212,"mean_force":0.12493,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47122,0.04876,0.04731]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52919,0.10658,0.12096]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51428,0.09687,0.10173]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5132,0.0964,0.11164]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48419,0.05634,0.12047]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47977,0.05252,0.08779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.47186,0.02946,0.04697],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11457,"mean_force":0.04356,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47005,0.04865,0.04609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.46901,0.06785,0.04922],"force_p95":0.08061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0974,"mean_force":0.04478,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47005,0.04865,0.04609]},{"body_a":"left_finger","body_b":"right_finger","contact_count":456.0,"contact_point_centroid":[0.56519,0.16312,0.0825],"force_p95":0.01397,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01095,"phase_index":7.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.56481,0.16323,0.08013]}],"total_contact_groups":13},"final_pose_error":0.04607,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53843,0.15787,0.01602],"final_tcp_position":[0.57031,0.16957,0.08225],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.57391,0.15482,0.13706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17863,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":475.0,"n_steps_budget":900.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48635,0.05725,0.1104],"tcp_start":[0.57391,0.15482,0.13706],"tcp_to_object_dist_end":0.08489,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.54047,0.12991,0.09844],"tcp_start":[0.48635,0.05725,0.1104],"tcp_to_object_dist_end":0.12317,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.48491,0.05703,0.12098],"tcp_start":[0.54047,0.12991,0.09844],"tcp_to_object_dist_end":0.09535,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.48317,0.05552,0.12015],"tcp_start":[0.48491,0.05703,0.12098],"tcp_to_object_dist_end":0.09438,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.47821,0.04953,0.0547],"tcp_start":[0.48317,0.05552,0.12015],"tcp_to_object_dist_end":0.02904,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04902,0.02589],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28992,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.47002,0.04864,0.04605],"tcp_start":[0.47821,0.04953,0.0547],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53843,0.15787,0.01602],"object_pos_start":[0.48259,0.04902,0.02589],"object_to_goal_dist_end":0.23004,"object_to_goal_dist_start":0.28992,"object_z_max":0.04005,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.57031,0.16957,0.08225],"tcp_start":[0.47002,0.04864,0.04605],"tcp_to_object_dist_end":0.07443,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```