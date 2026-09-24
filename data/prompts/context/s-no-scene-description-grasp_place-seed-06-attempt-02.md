## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1266 | 0.20 | ❌ rejected |
| 1 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=0.127) — your mutation base

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

- **Composite score**: 0.127
- **task_score** (E): 0.204
- **fitness_score**: 0.577  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1738 |
| descend_to_grasp | 1.00 | 1.00 | 0.0898 |
| grasp | 1.00 | 1.00 | 0.0118 |
| lift | 1.00 | 1.00 | 0.1334 |
| transport_to_goal | 0.00 | 1.00 | 0.0968 |
| descend_to_place | 1.00 | 1.00 | 0.1247 |
| release | 1.00 | 1.00 | 0.0215 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.032, 0.133) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.032, 0.133)→(0.495, 0.025, 0.043) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.495, 0.025, 0.043)→(0.487, 0.025, 0.035) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 | 1.00 / 43.000 | 0.166 | 0.196 |
| lift | lift | 1.00 / step_budget | (0.487, 0.025, 0.035)→(0.495, 0.024, 0.168) | (0.500, 0.025, 0.026)→(0.509, 0.024, 0.148) | 0.271→0.207 | 1.00 / 21.333 | 55994.068 | 0.491 |
| transport_to_goal | approach | 0.00 / step_budget | (0.495, 0.024, 0.168)→(0.522, 0.076, 0.243) | (0.509, 0.024, 0.148)→(0.516, 0.062, 0.016) | 0.207→0.249 | 1.00 / 4.000 | 0.123 | 1.745 |
| descend_to_place | descend | 1.00 / step_budget | (0.522, 0.076, 0.243)→(0.585, 0.178, 0.221) | (0.516, 0.062, 0.016)→(0.516, 0.062, 0.016) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.585, 0.178, 0.221)→(0.580, 0.177, 0.241) | (0.516, 0.062, 0.016)→(0.516, 0.062, 0.016) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.319
- phase_score: 0.593
- phase_breakdown.reach_object_score: 0.821
- phase_breakdown.place_at_goal_score: 0.000
- phase_breakdown.grasp_object_score: 1.000
- phase_breakdown.lift_object_score: 0.732
- grasp_place_fitness: 0.627

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.627
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.319
- **Median Q (composite search score)**: 0.109
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.392


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18182,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.arc_height":0.0569,"approach_object.speed":0.18376,"descend_to_grasp.descend_z_offset":0.00718,"lift.lift_height":0.1656,"transport_to_goal.arc_height":0.0296,"transport_to_goal.speed":0.15873},"optimized_scores":{"best_composite_score":0.09325,"best_fitness_score":0.54325,"best_task_score":0.1343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2697.0,"contact_point_centroid":[0.51247,0.01048,-0.00244],"force_p95":0.12838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83055,"mean_force":0.14275,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51935,0.03826,0.24903]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.50171,-0.01336,-0.00119],"force_p95":0.2927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50062,"mean_force":0.06024,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48938,-0.01426,0.03496]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12850.0,"contact_point_centroid":[0.49547,0.00502,0.09803],"force_p95":0.08017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27919,"mean_force":0.0477,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49224,-0.01429,0.09647]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13235.0,"contact_point_centroid":[0.4953,-0.03361,0.09674],"force_p95":0.07878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27354,"mean_force":0.04721,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49217,-0.01429,0.09527]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.50385,-0.01549,-0.00212],"force_p95":0.15954,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23333,"mean_force":0.13199,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49196,-0.01429,0.03441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1846.0,"contact_point_centroid":[0.50588,-0.02401,0.1868],"force_p95":0.11267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18624,"mean_force":0.076,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50076,-0.0053,0.19136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1571.0,"contact_point_centroid":[0.50604,0.01308,0.18617],"force_p95":0.13219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18543,"mean_force":0.08758,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50055,-0.0058,0.19055]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3359.0,"contact_point_centroid":[0.49123,0.00522,0.03583],"force_p95":0.05943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14855,"mean_force":0.03179,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49068,-0.01427,0.03306]},{"body_a":"world","body_b":"grasp_target","contact_count":2336.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49887,0.02785,0.21151]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49803,-0.01049,0.08533]},{"body_a":"world","body_b":"grasp_target","contact_count":3628.0,"contact_point_centroid":[0.51249,0.01057,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55889,0.13086,0.26686]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51249,0.01057,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57955,0.18184,0.2616]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.49124,-0.03375,0.03491],"force_p95":0.05603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08319,"mean_force":0.02777,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49069,-0.01427,0.03306]}],"total_contact_groups":13},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51249,0.01057,0.01602],"final_tcp_position":[0.58243,0.18282,0.26048],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":30.38666,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2336.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49965,-0.00675,0.12922],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1120.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49876,-0.01434,0.04172],"tcp_start":[0.49965,-0.00675,0.12922],"tcp_to_object_dist_end":0.01654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01446,0.02554],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31181,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15434,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9148.0,"raw_peak_contact_force":0.23333,"subtask_id":"grasp_object","tcp_end":[0.49065,-0.01427,0.03302],"tcp_start":[0.49876,-0.01434,0.04172],"tcp_to_object_dist_end":0.01507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.51311,-0.01446,0.15926],"object_pos_start":[0.50373,-0.01446,0.02554],"object_to_goal_dist_end":0.23262,"object_to_goal_dist_start":0.31181,"object_z_max":0.15916,"peak_contact_force":30.38666,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26227.0,"raw_peak_contact_force":0.50062,"subtask_id":"lift_object","tcp_end":[0.49951,-0.01439,0.17894],"tcp_start":[0.49065,-0.01427,0.03302],"tcp_to_object_dist_end":0.02392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51249,0.01057,0.01602],"object_pos_start":[0.51311,-0.01446,0.15926],"object_to_goal_dist_end":0.30115,"object_to_goal_dist_start":0.23262,"object_z_max":0.17841,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6114.0,"raw_peak_contact_force":1.83055,"subtask_id":"place_at_goal","tcp_end":[0.53304,0.069,0.27991],"tcp_start":[0.49951,-0.01439,0.17894],"tcp_to_object_dist_end":0.27106,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":907.0,"n_steps_budget":1000.0,"object_pos_end":[0.51249,0.01057,0.01602],"object_pos_start":[0.51249,0.01057,0.01602],"object_to_goal_dist_end":0.30115,"object_to_goal_dist_start":0.30115,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3628.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58243,0.18282,0.26048],"tcp_start":[0.53304,0.069,0.27991],"tcp_to_object_dist_end":0.30712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.01057,0.01602],"object_pos_start":[0.51249,0.01057,0.01602],"object_to_goal_dist_end":0.30115,"object_to_goal_dist_start":0.30115,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.57854,0.1814,0.28135],"tcp_start":[0.58243,0.18282,0.26048],"tcp_to_object_dist_end":0.32241,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70423,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.arc_height":0.03779,"approach_object.speed":0.18782,"descend_to_grasp.descend_z_offset":0.01671,"lift.lift_height":0.15145,"transport_to_goal.arc_height":0.02616,"transport_to_goal.speed":0.03345},"optimized_scores":{"best_composite_score":0.17719,"best_fitness_score":0.62719,"best_task_score":0.31925},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":520.0,"contact_point_centroid":[0.55354,0.08748,-0.00392],"force_p95":0.82572,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69457,"mean_force":0.21091,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53774,0.07574,0.2064]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.51072,0.03916,-0.00111],"force_p95":0.2667,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41198,"mean_force":0.09422,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49806,0.03931,0.04379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11889.0,"contact_point_centroid":[0.50391,0.01976,0.09772],"force_p95":0.07195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26327,"mean_force":0.04283,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50091,0.0391,0.09598]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11334.0,"contact_point_centroid":[0.50385,0.05854,0.09668],"force_p95":0.07236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25398,"mean_force":0.04462,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50083,0.03911,0.09474]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.51251,0.03966,-0.00202],"force_p95":0.22172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22323,"mean_force":0.15785,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50058,0.03955,0.04349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6696.0,"contact_point_centroid":[0.5227,0.03345,0.17898],"force_p95":0.09738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15927,"mean_force":0.06168,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51697,0.05257,0.18059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7611.0,"contact_point_centroid":[0.52381,0.07283,0.18022],"force_p95":0.08048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14734,"mean_force":0.05461,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51803,0.05382,0.18217]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13237,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50232,0.04151,0.22507]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3318.0,"contact_point_centroid":[0.49985,0.01993,0.04488],"force_p95":0.0649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1352,"mean_force":0.04272,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49929,0.03944,0.04207]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55397,0.08724,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1237,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58173,0.12618,0.17887]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5063,0.04257,0.09358]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55397,0.08724,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61059,0.16088,0.16125]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3940.0,"contact_point_centroid":[0.49989,0.0589,0.04385],"force_p95":0.0632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11908,"mean_force":0.03885,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49929,0.03944,0.04207]}],"total_contact_groups":13},"final_pose_error":0.01697,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55397,0.08724,0.01602],"final_tcp_position":[0.61489,0.16208,0.16074],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50762,0.04516,0.13667],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1072.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.50735,0.04014,0.05108],"tcp_start":[0.50762,0.04516,0.13667],"tcp_to_object_dist_end":0.02559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03944,0.02587],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21253,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.21562,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8870.0,"raw_peak_contact_force":0.22323,"subtask_id":"grasp_object","tcp_end":[0.49925,0.03944,0.04203],"tcp_start":[0.50735,0.04014,0.05108],"tcp_to_object_dist_end":0.02084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.52008,0.03926,0.14053],"object_pos_start":[0.51242,0.03944,0.02587],"object_to_goal_dist_end":0.17127,"object_to_goal_dist_start":0.21253,"object_z_max":0.14041,"peak_contact_force":167951.73011,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23363.0,"raw_peak_contact_force":0.41198,"subtask_id":"lift_object","tcp_end":[0.50798,0.03913,0.16512],"tcp_start":[0.49925,0.03944,0.04203],"tcp_to_object_dist_end":0.02741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55399,0.0873,0.01601],"object_pos_start":[0.52008,0.03926,0.14053],"object_to_goal_dist_end":0.17124,"object_to_goal_dist_start":0.17127,"object_z_max":0.16751,"peak_contact_force":0.12372,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14827.0,"raw_peak_contact_force":1.69457,"subtask_id":"place_at_goal","tcp_end":[0.54014,0.07839,0.20869],"tcp_start":[0.50798,0.03913,0.16512],"tcp_to_object_dist_end":0.19338,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55397,0.08724,0.01602],"object_pos_start":[0.55399,0.0873,0.01601],"object_to_goal_dist_end":0.17127,"object_to_goal_dist_start":0.17124,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.1237,"subtask_id":"place_at_goal","tcp_end":[0.61489,0.16208,0.16074],"tcp_start":[0.54014,0.07839,0.20869],"tcp_to_object_dist_end":0.17394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55397,0.08724,0.01602],"object_pos_start":[0.55397,0.08724,0.01602],"object_to_goal_dist_end":0.17127,"object_to_goal_dist_start":0.17127,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.60893,0.16035,0.18073],"tcp_start":[0.61489,0.16208,0.16074],"tcp_to_object_dist_end":0.1884,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88435,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.arc_height":0.11268,"approach_object.speed":0.11146,"descend_to_grasp.descend_z_offset":0.00242,"lift.lift_height":0.1452,"transport_to_goal.arc_height":0.05019,"transport_to_goal.speed":0.05699},"optimized_scores":{"best_composite_score":0.10927,"best_fitness_score":0.55927,"best_task_score":0.15966},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2074.0,"contact_point_centroid":[0.48279,0.08767,-0.00252],"force_p95":0.19487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70864,"mean_force":0.14767,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48715,0.06918,0.22106]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.48049,0.04856,-0.00106],"force_p95":0.3704,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55948,"mean_force":0.05689,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46897,0.0485,0.03095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12356.0,"contact_point_centroid":[0.4742,0.06767,0.08817],"force_p95":0.07696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27917,"mean_force":0.04587,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47159,0.04826,0.08637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12911.0,"contact_point_centroid":[0.47406,0.02895,0.08798],"force_p95":0.07657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27261,"mean_force":0.04394,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47156,0.04826,0.08637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3547.0,"contact_point_centroid":[0.48157,0.03333,0.17209],"force_p95":0.11694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21071,"mean_force":0.0697,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47754,0.05229,0.17549]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3906.0,"contact_point_centroid":[0.48154,0.07148,0.17296],"force_p95":0.10985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18162,"mean_force":0.06829,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47769,0.05262,0.17671]},{"body_a":"world","body_b":"grasp_target","contact_count":2972.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49086,0.06329,0.23389]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.48268,0.0487,-0.00201],"force_p95":0.12768,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13027,"mean_force":0.1241,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47138,0.04877,0.03044]},{"body_a":"world","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47761,0.05358,0.08468]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48278,0.0877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52626,0.13917,0.23828]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48278,0.0877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55307,0.18846,0.24229]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4430.0,"contact_point_centroid":[0.46983,0.06816,0.03168],"force_p95":0.04798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08318,"mean_force":0.0253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47014,0.04865,0.0292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4217.0,"contact_point_centroid":[0.46997,0.02916,0.03225],"force_p95":0.04838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08039,"mean_force":0.02625,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47014,0.04865,0.0292]}],"total_contact_groups":13},"final_pose_error":0.04801,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48278,0.0877,0.01602],"final_tcp_position":[0.55619,0.18954,0.2405],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.70864,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":744.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2972.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47963,0.05786,0.13256],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47796,0.04948,0.0372],"tcp_start":[0.47963,0.05786,0.13256],"tcp_to_object_dist_end":0.01216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48257,0.04865,0.02592],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29014,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.128,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10279.0,"raw_peak_contact_force":0.13027,"subtask_id":"grasp_object","tcp_end":[0.47011,0.04865,0.02916],"tcp_start":[0.47796,0.04948,0.0372],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.49428,0.04845,0.1448],"object_pos_start":[0.48257,0.04865,0.02592],"object_to_goal_dist_end":0.21808,"object_to_goal_dist_start":0.29014,"object_z_max":0.14469,"peak_contact_force":0.08723,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25397.0,"raw_peak_contact_force":0.55948,"subtask_id":"lift_object","tcp_end":[0.47825,0.04829,0.15941],"tcp_start":[0.47011,0.04865,0.02916],"tcp_to_object_dist_end":0.02169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48278,0.0877,0.01602],"object_pos_start":[0.49428,0.04845,0.1448],"object_to_goal_dist_end":0.27521,"object_to_goal_dist_start":0.21808,"object_z_max":0.16762,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9527.0,"raw_peak_contact_force":1.70864,"subtask_id":"place_at_goal","tcp_end":[0.49341,0.07969,0.24042],"tcp_start":[0.47825,0.04829,0.15941],"tcp_to_object_dist_end":0.2248,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48278,0.0877,0.01602],"object_pos_start":[0.48278,0.0877,0.01602],"object_to_goal_dist_end":0.27521,"object_to_goal_dist_start":0.27521,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.55619,0.18954,0.2405],"tcp_start":[0.49341,0.07969,0.24042],"tcp_to_object_dist_end":0.2572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48278,0.0877,0.01602],"object_pos_start":[0.48278,0.0877,0.01602],"object_to_goal_dist_end":0.27521,"object_to_goal_dist_start":0.27521,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.55195,0.18797,0.26234],"tcp_start":[0.55619,0.18954,0.2405],"tcp_to_object_dist_end":0.27479,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```