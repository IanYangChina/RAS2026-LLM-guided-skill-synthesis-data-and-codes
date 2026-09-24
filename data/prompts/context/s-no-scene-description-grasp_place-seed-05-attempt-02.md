## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1241 | 0.19 | ❌ rejected |
| 1 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.124) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_angle:
      type: angle
      range:
      - 0.1
      - 1.2
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: release_2
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.124
- **task_score** (E): 0.185
- **fitness_score**: 0.306  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1552 |
| descend_to_grasp | 0.00 | 1.00 | 0.2314 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1076 |
| approach_goal | 0.33 | 1.00 | 0.1007 |
| descend_to_place | 1.00 | 1.00 | 0.0942 |
| release | 1.00 | 0.67 | 0.0232 |
| retract | 1.00 | 0.67 | 0.0866 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.148) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 10.185 | 0.138 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.510, 0.016, 0.148)→(0.724, 0.053, 0.111) | (0.516, 0.018, 0.026)→(0.673, 0.044, 0.059) | 0.236→0.222 | 1.00 / 4.333 | 418.845 | 1815.818 |
| grasp | grasp | 1.00 / step_budget | (0.734, 0.051, 0.121)→(0.734, 0.051, 0.121) | (0.673, 0.044, 0.059)→(0.669, 0.074, 0.050) | 0.222→0.214 | 1.00 / 14.000 | 69.632 | 158.267 |
| lift | lift | 1.00 / step_budget | (0.734, 0.051, 0.121)→(0.669, 0.074, 0.187) | (0.668, 0.076, 0.049)→(0.671, 0.093, 0.053) | 0.213→0.205 | 1.00 / 6.667 | 2612.595 | 184.680 |
| approach_goal | approach | 0.33 / step_budget | (0.669, 0.074, 0.187)→(0.652, 0.125, 0.217) | (0.671, 0.093, 0.053)→(0.923, 0.043, -5.539) | 0.205→5.757 | 1.00 / 7.333 | 91000.869 | 0.651 |
| descend_to_place | descend | 1.00 / step_budget | (0.652, 0.125, 0.217)→(0.607, 0.175, 0.195) | (0.923, 0.043, -5.539)→(1.001, 0.024, -9.712) | 5.757→9.929 | 1.00 / 7.000 | 3249.742 | 0.086 |
| release | release | 1.00 / step_budget | (0.607, 0.175, 0.195)→(0.603, 0.175, 0.218) | (1.001, 0.024, -9.712)→(1.053, 0.011, -13.164) | 9.929→13.380 | 0.67 / 2.667 | 0.082 | 0.085 |
| retract | retract | 1.00 / step_budget | (0.603, 0.175, 0.218)→(0.604, 0.179, 0.304) | (1.053, 0.011, -13.164)→(1.188, -0.022, -24.410) | 13.380→24.627 | 0.67 / 2.667 | 0.082 | 0.082 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.000
- phase_score: 0.248
- phase_breakdown.approach_goal_score: 0.183
- phase_breakdown.approach_object_score: 0.672
- phase_breakdown.place_score: 0.379
- phase_breakdown.lift_score: 0.005
- phase_breakdown.descend_to_grasp_score: 0.003
- grasp_place_fitness: 0.445

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.445
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.434
- **Median Q (composite search score)**: -0.129
- **K-run variance**: 0.0125
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.369


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":18.0,"average_failure_rate":0.12766,"average_mean_iterations":29.07801,"average_solve_count":141.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.13822,"approach_object.approach_speed":0.14597,"descend_to_grasp.descend_height_offset":0.02984,"descend_to_place.place_height_offset":0.02038,"grasp.grasp_guard_threshold":0.00445},"optimized_scores":{"best_composite_score":-0.12877,"best_fitness_score":0.30123,"best_task_score":0.43351},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":34.0,"contact_point_centroid":[0.60405,0.06012,-0.00533],"force_p95":1569.71512,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1955.26179,"mean_force":464.01442,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.57571,0.08911,-0.01414]},{"body_a":"world","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.65358,-0.12284,-0.00249],"force_p95":993.64812,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1023.94971,"mean_force":794.59046,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.60155,0.10115,0.05461]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.63054,-0.02532,-0.00044],"force_p95":294.2686,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":484.02381,"mean_force":184.05221,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.58571,0.09704,0.0173]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.66288,-0.15171,-0.00027],"force_p95":280.70221,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.45103,"mean_force":88.75133,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.63868,0.09463,0.10078]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.65965,-0.15062,-5e-05],"force_p95":199.69074,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.64288,"mean_force":99.35594,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.63628,0.09584,0.10119]},{"body_a":"world","body_b":"left_finger","contact_count":478.0,"contact_point_centroid":[0.54112,0.06685,-0.011],"force_p95":38.92418,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.88411,"mean_force":10.53848,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.57598,0.08874,-0.01225]},{"body_a":"world","body_b":"right_finger","contact_count":444.0,"contact_point_centroid":[0.61229,0.10628,-0.0133],"force_p95":22.17119,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.74002,"mean_force":8.48339,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.57565,0.08816,-0.01348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.541,0.06,-0.01106],"force_p95":2.74507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.18589,"mean_force":0.61109,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.57531,0.08334,-0.01408]},{"body_a":"world","body_b":"grasp_target","contact_count":372.0,"contact_point_centroid":[0.52673,0.0378,-0.00685],"force_p95":3.90738,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.90283,"mean_force":0.78697,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.56827,0.05716,0.06322]},{"body_a":"grasp_target","body_b":"hand","contact_count":20.0,"contact_point_centroid":[0.51859,0.03224,0.02376],"force_p95":1.7572,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.82362,"mean_force":0.98356,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.59356,0.09955,0.03791]},{"body_a":"world","body_b":"grasp_target","contact_count":1827.0,"contact_point_centroid":[0.51029,0.15689,-0.00226],"force_p95":0.23426,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91741,"mean_force":0.14378,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.63899,0.09468,0.10087]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51054,0.01271,0.22487]},{"body_a":"world","body_b":"grasp_target","contact_count":3548.0,"contact_point_centroid":[0.50914,0.15743,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.57419,0.12482,0.13073]},{"body_a":"world","body_b":"grasp_target","contact_count":3316.0,"contact_point_centroid":[0.50914,0.15743,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55762,0.16721,0.18314]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.50914,0.15743,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59618,0.17786,0.16918]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50914,0.15743,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5938,0.17816,0.13913]}],"total_contact_groups":22},"final_pose_error":0.01388,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.50914,0.15743,0.02602],"final_tcp_position":[0.59899,0.17822,0.24445],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1955.26179,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52298,0.0263,0.14775],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.52122,0.07308,0.04186],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.14821,"object_to_goal_dist_start":0.18336,"object_z_max":0.04087,"peak_contact_force":720.23792,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1979.0,"raw_peak_contact_force":1955.26179,"subtask_id":"descend_to_grasp","tcp_end":[0.61119,0.09889,0.07152],"tcp_start":[0.52298,0.0263,0.14775],"tcp_to_object_dist_end":0.09819,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50914,0.15743,0.02602],"object_pos_start":[0.52122,0.07308,0.04186],"object_to_goal_dist_end":0.12537,"object_to_goal_dist_start":0.14821,"object_z_max":0.05388,"peak_contact_force":69.14139,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3106.0,"raw_peak_contact_force":308.45103,"tcp_end":[0.63921,0.0945,0.10094],"tcp_start":[0.63921,0.09453,0.10094],"tcp_to_object_dist_end":0.16276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":887.0,"n_steps_budget":1000.0,"object_pos_end":[0.50914,0.15743,0.02602],"object_pos_start":[0.50914,0.15743,0.02602],"object_to_goal_dist_end":0.12537,"object_to_goal_dist_start":0.12537,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7166.0,"raw_peak_contact_force":203.64288,"subtask_id":"lift","tcp_end":[0.51283,0.1545,0.1673],"tcp_start":[0.63921,0.0945,0.10094],"tcp_to_object_dist_end":0.14136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.50914,0.15743,0.02602],"object_pos_start":[0.50914,0.15743,0.02602],"object_to_goal_dist_end":0.12537,"object_to_goal_dist_start":0.12537,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6715.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.59614,0.17761,0.19977],"tcp_start":[0.51283,0.1545,0.1673],"tcp_to_object_dist_end":0.19536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.50914,0.15743,0.02602],"object_pos_start":[0.50914,0.15743,0.02602],"object_to_goal_dist_end":0.12537,"object_to_goal_dist_start":0.12537,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.59737,0.17826,0.13724],"tcp_start":[0.59614,0.17761,0.19977],"tcp_to_object_dist_end":0.14348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50914,0.15743,0.02602],"object_pos_start":[0.50914,0.15743,0.02602],"object_to_goal_dist_end":0.12537,"object_to_goal_dist_start":0.12537,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1010.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5926,0.17805,0.15949],"tcp_start":[0.59737,0.17826,0.13724],"tcp_to_object_dist_end":0.15876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50914,0.15743,0.02602],"object_pos_start":[0.50914,0.15743,0.02602],"object_to_goal_dist_end":0.12537,"object_to_goal_dist_start":0.12537,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59899,0.17822,0.24445],"tcp_start":[0.5926,0.17805,0.15949],"tcp_to_object_dist_end":0.2371,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.11823,"approach_object.approach_speed":0.10263,"descend_to_grasp.descend_height_offset":0.04234,"descend_to_place.place_height_offset":0.01466,"grasp.grasp_guard_threshold":0.00997},"optimized_scores":{"best_composite_score":-0.25832,"best_fitness_score":0.17168,"best_task_score":0.12253},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":240.0,"contact_point_centroid":[0.70648,-0.07197,-0.00108],"force_p95":553.44502,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1617.19104,"mean_force":141.89131,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.70326,0.00311,0.08811]},{"body_a":"world","body_b":"link6","contact_count":825.0,"contact_point_centroid":[0.6072,-0.19308,-0.00037],"force_p95":346.66286,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":725.59138,"mean_force":283.93981,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.73115,0.01276,0.12653]},{"body_a":"world","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.56989,-0.07482,-0.00046],"force_p95":670.01551,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":693.94237,"mean_force":483.79862,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5151,0.03178,0.02772]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.62063,-0.19857,-0.00011],"force_p95":196.05689,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.49996,"mean_force":151.51188,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.77496,-0.0033,0.12256]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62064,-0.1984,-0.00014],"force_p95":79.85592,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.39807,"mean_force":74.5765,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.77495,-0.00318,0.12261]},{"body_a":"world","body_b":"left_finger","contact_count":646.0,"contact_point_centroid":[0.48374,-0.02404,-0.01538],"force_p95":37.47143,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.43153,"mean_force":10.36306,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.51543,0.00421,-0.01575]},{"body_a":"world","body_b":"right_finger","contact_count":724.0,"contact_point_centroid":[0.54958,0.02968,-0.01394],"force_p95":21.788,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.65487,"mean_force":7.57829,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.51526,0.00554,-0.01347]},{"body_a":"world","body_b":"hand","contact_count":9.0,"contact_point_centroid":[0.75312,-0.09458,-1e-05],"force_p95":25.28071,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.5222,"mean_force":20.62425,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.76904,-0.00069,0.12254]},{"body_a":"grasp_target","body_b":"hand","contact_count":114.0,"contact_point_centroid":[0.52927,-0.01832,0.04156],"force_p95":3.66081,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.82162,"mean_force":0.81225,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52413,0.0195,0.01499]},{"body_a":"world","body_b":"grasp_target","contact_count":3033.0,"contact_point_centroid":[0.69,0.01681,-0.00244],"force_p95":0.36175,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.813,"mean_force":0.16712,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.71925,0.00534,0.11758]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":625.0,"contact_point_centroid":[0.49644,0.00317,0.03982],"force_p95":0.57664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.70937,"mean_force":0.29845,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52775,0.02556,0.02527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":377.0,"contact_point_centroid":[0.70108,0.03556,0.093],"force_p95":0.20681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54173,"mean_force":0.11673,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.67404,0.03733,0.12499]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4995,-0.0064,0.22612]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.7193,0.02081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.77495,-0.00318,0.12261]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.7193,0.02081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.74483,0.00905,0.13549]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.7193,0.02081,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.69214,0.05192,0.18371]}],"total_contact_groups":25},"final_pose_error":0.01268,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.7193,0.02081,0.01602],"final_tcp_position":[0.58682,0.18616,0.38551],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273004.12064,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50015,-0.01332,0.14936],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.7193,0.02081,0.01602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3149,"object_to_goal_dist_start":0.31223,"object_z_max":0.1013,"peak_contact_force":305.06418,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6592.0,"raw_peak_contact_force":1617.19104,"subtask_id":"descend_to_grasp","tcp_end":[0.77452,-0.00314,0.12279],"tcp_start":[0.50015,-0.01332,0.14936],"tcp_to_object_dist_end":0.12256,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.7193,0.02081,0.01602],"object_pos_start":[0.7193,0.02081,0.01602],"object_to_goal_dist_end":0.3149,"object_to_goal_dist_start":0.3149,"object_z_max":0.01602,"peak_contact_force":73.27558,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3555.0,"raw_peak_contact_force":84.39807,"tcp_end":[0.77499,-0.00334,0.12251],"tcp_start":[0.77499,-0.00331,0.12252],"tcp_to_object_dist_end":0.12258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":492.0,"n_steps_budget":600.0,"object_pos_end":[0.7193,0.02081,0.01602],"object_pos_start":[0.7193,0.02081,0.01602],"object_to_goal_dist_end":0.3149,"object_to_goal_dist_start":0.3149,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4176.0,"raw_peak_contact_force":196.49996,"subtask_id":"lift","tcp_end":[0.72029,0.01946,0.1541],"tcp_start":[0.77499,-0.00334,0.12251],"tcp_to_object_dist_end":0.13809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.7193,0.02081,0.01602],"object_pos_start":[0.7193,0.02081,0.01602],"object_to_goal_dist_end":0.3149,"object_to_goal_dist_start":0.3149,"object_z_max":0.01602,"peak_contact_force":273002.48478,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8416.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.66945,0.08058,0.21722],"tcp_start":[0.72029,0.01946,0.1541],"tcp_to_object_dist_end":0.21573,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.7193,0.02081,0.01602],"object_pos_start":[0.7193,0.02081,0.01602],"object_to_goal_dist_end":0.3149,"object_to_goal_dist_start":0.3149,"object_z_max":0.01602,"peak_contact_force":9749.10402,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7309.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.58913,0.1822,0.25465],"tcp_start":[0.66945,0.08058,0.21722],"tcp_to_object_dist_end":0.31613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.7193,0.02081,0.01602],"object_pos_start":[0.7193,0.02081,0.01602],"object_to_goal_dist_end":0.3149,"object_to_goal_dist_start":0.3149,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58739,0.18126,0.27888],"tcp_start":[0.58913,0.1822,0.25465],"tcp_to_object_dist_end":0.33502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.7193,0.02081,0.01602],"object_pos_start":[0.7193,0.02081,0.01602],"object_to_goal_dist_end":0.3149,"object_to_goal_dist_start":0.3149,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2652.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58682,0.18616,0.38551],"tcp_start":[0.58739,0.18126,0.27888],"tcp_to_object_dist_end":0.42592,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71505,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.07894,"approach_object.approach_speed":0.05026,"descend_to_grasp.descend_height_offset":0.03861,"descend_to_place.place_height_offset":0.04997,"grasp.grasp_guard_threshold":0.00432},"optimized_scores":{"best_composite_score":0.01493,"best_fitness_score":0.44493,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":759.0,"contact_point_centroid":[0.70957,-1e-05,-0.00038],"force_p95":234.94719,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1874.9999,"mean_force":145.15344,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.7457,0.05214,0.13122]},{"body_a":"world","body_b":"link6","contact_count":820.0,"contact_point_centroid":[0.62237,-0.1496,-0.00028],"force_p95":330.25502,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":975.31954,"mean_force":225.72764,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.74695,0.05281,0.13611]},{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.57642,-0.04215,-0.00029],"force_p95":385.05942,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":392.42377,"mean_force":218.78996,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54014,0.08534,0.02825]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.64806,-0.13216,-9e-05],"force_p95":151.11562,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.89673,"mean_force":111.4858,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.78705,0.06307,0.13978]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.64798,-0.13207,-0.00013],"force_p95":77.50407,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.95088,"mean_force":68.60378,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.787,0.06312,0.13974]},{"body_a":"world","body_b":"left_finger","contact_count":548.0,"contact_point_centroid":[0.49109,0.05187,-0.01278],"force_p95":38.4417,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.13931,"mean_force":10.33507,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52618,0.07452,-0.01293]},{"body_a":"world","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.74598,0.01222,-2e-05],"force_p95":32.34662,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.92,"mean_force":27.18615,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.78706,0.06306,0.13972]},{"body_a":"world","body_b":"hand","contact_count":493.0,"contact_point_centroid":[0.74592,0.0123,-2e-05],"force_p95":8.84356,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.56406,"mean_force":7.07518,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.78702,0.06313,0.13972]},{"body_a":"world","body_b":"right_finger","contact_count":514.0,"contact_point_centroid":[0.56319,0.09287,-0.01398],"force_p95":21.33854,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.38359,"mean_force":7.4984,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52602,0.07407,-0.01386]},{"body_a":"world","body_b":"grasp_target","contact_count":367.0,"contact_point_centroid":[0.51085,0.0437,-0.00628],"force_p95":3.79282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.48459,"mean_force":0.81631,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52937,0.05167,0.05607]},{"body_a":"grasp_target","body_b":"hand","contact_count":913.0,"contact_point_centroid":[0.7006,0.01116,0.1348],"force_p95":0.796,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.29085,"mean_force":0.48666,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.73063,0.05444,0.12608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6702.0,"contact_point_centroid":[0.69602,0.03306,0.14776],"force_p95":0.23922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.25968,"mean_force":0.09276,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.7128,0.05407,0.12015]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.78979,0.13195,-0.00775],"force_p95":1.4311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70864,"mean_force":0.49625,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.76402,0.05732,0.2319]},{"body_a":"grasp_target","body_b":"hand","contact_count":645.0,"contact_point_centroid":[0.75753,0.03316,0.14561],"force_p95":0.49213,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.74946,"mean_force":0.3691,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.77966,0.0565,0.18427]},{"body_a":"grasp_target","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.77058,0.02694,0.11521],"force_p95":0.55218,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.73316,"mean_force":0.4406,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.787,0.06312,0.13974]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3818.0,"contact_point_centroid":[0.78173,0.06235,0.12179],"force_p95":0.12522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18741,"mean_force":0.05483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.78702,0.06311,0.13973]}],"total_contact_groups":25},"final_pose_error":0.01282,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[2.33585,-0.24449,-73.27346],"final_tcp_position":[0.62652,0.17141,0.28229],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":7837.54031,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":30.30966,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1260.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50736,0.03387,0.14827],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.77706,0.0395,0.11914],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.20177,"object_to_goal_dist_start":0.21222,"object_z_max":0.15867,"peak_contact_force":231.23215,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11275.0,"raw_peak_contact_force":1874.9999,"subtask_id":"descend_to_grasp","tcp_end":[0.78662,0.06295,0.13973],"tcp_start":[0.50736,0.03387,0.14827],"tcp_to_object_dist_end":0.03263,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.77801,0.04478,0.10847],"object_pos_start":[0.77706,0.0395,0.11914],"object_to_goal_dist_end":0.20071,"object_to_goal_dist_start":0.20177,"object_z_max":0.11914,"peak_contact_force":66.47879,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6592.0,"raw_peak_contact_force":81.95088,"tcp_end":[0.78706,0.06306,0.13972],"tcp_start":[0.78706,0.06307,0.13972],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.78333,0.10073,0.11655],"object_pos_start":[0.7765,0.04871,0.10573],"object_to_goal_dist_end":0.17386,"object_to_goal_dist_start":0.19762,"object_z_max":0.16783,"peak_contact_force":7837.54031,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5854.0,"raw_peak_contact_force":153.89673,"subtask_id":"lift","tcp_end":[0.7751,0.04939,0.23874],"tcp_start":[0.78706,0.06306,0.13972],"tcp_to_object_dist_end":0.13279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[1.5394,-0.05027,-16.65821],"object_pos_start":[0.78333,0.10073,0.11655],"object_to_goal_dist_end":16.82943,"object_to_goal_dist_start":0.17386,"object_z_max":0.11655,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4570.0,"raw_peak_contact_force":1.70864,"subtask_id":"approach_goal","tcp_end":[0.69113,0.11756,0.23364],"tcp_start":[0.7751,0.04939,0.23874],"tcp_to_object_dist_end":16.91397,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[1.77416,-0.10752,-29.17725],"object_pos_start":[1.5394,-0.05027,-16.65821],"object_to_goal_dist_end":29.34602,"object_to_goal_dist_start":16.82943,"object_z_max":-16.65821,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1298.0,"raw_peak_contact_force":0.01276,"subtask_id":"place","tcp_end":[0.63368,0.16507,0.19263],"tcp_start":[0.69113,0.11756,0.23364],"tcp_to_object_dist_end":29.39328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[1.93172,-0.14594,-39.53344],"object_pos_start":[1.77416,-0.10752,-29.17725],"object_to_goal_dist_end":39.70117,"object_to_goal_dist_start":29.34602,"object_z_max":-29.17725,"peak_contact_force":0.0,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":230.0,"raw_peak_contact_force":0.01087,"tcp_end":[0.63043,0.1647,0.21477],"tcp_start":[0.63368,0.16507,0.19263],"tcp_to_object_dist_end":39.77072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[2.33585,-0.24449,-73.27346],"object_pos_start":[1.93172,-0.14594,-39.53344],"object_to_goal_dist_end":73.43954,"object_to_goal_dist_start":39.70117,"object_z_max":-39.53344,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.62652,0.17141,0.28229],"tcp_start":[0.63043,0.1647,0.21477],"tcp_to_object_dist_end":73.57679,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```