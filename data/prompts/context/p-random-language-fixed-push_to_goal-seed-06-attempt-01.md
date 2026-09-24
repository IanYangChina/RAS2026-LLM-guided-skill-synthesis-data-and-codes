## Search State

- **Seed**: 6
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0824 | 0.00 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0821 | 0.00 | ✅ accepted |

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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.082) — your mutation base

```yaml
skill: push_to_goal
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

```

## Design Metrics

- **Composite score**: -0.082
- **task_score** (E): 0.000
- **fitness_score**: 0.318  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2901 |
| lift_1 | 0.00 | 1.00 | 0.1699 |
| push_1 | 1.00 | 1.00 | 0.1929 |
| approach_1 | 0.33 | 1.00 | 0.1747 |
| approach_2 | 1.00 | 1.00 | 0.1054 |
| descend_1 | 0.00 | 1.00 | 0.1896 |
| grasp_1 | 1.00 | 1.00 | 0.0107 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.104, 0.032) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| lift_1 | lift | 0.00 / step_budget | (0.496, 0.104, 0.032)→(0.435, 0.003, 0.154) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.435, 0.003, 0.154)→(0.493, -0.127, 0.026) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_1 | approach | 0.33 / step_budget | (0.493, -0.127, 0.026)→(0.496, 0.047, 0.039) | (0.500, 0.029, 0.025)→(0.510, 0.079, 0.028) | 0.180→0.231 | 1.00 / 2.667 | 37.192 | 65.912 |
| approach_2 | approach | 1.00 / step_budget | (0.496, 0.047, 0.039)→(0.507, 0.150, 0.028) | (0.510, 0.079, 0.028)→(0.527, 0.156, 0.030) | 0.231→0.311 | 1.00 / 3.000 | 35.640 | 64.972 |
| descend_1 | descend | 0.00 / step_budget | (0.507, 0.150, 0.028)→(0.498, -0.038, 0.021) | (0.527, 0.156, 0.030)→(0.502, 0.123, 0.025) | 0.311→0.275 | 1.00 / 4.000 | 0.245 | 60.985 |
| grasp_1 | grasp | 1.00 / step_budget | (0.498, -0.038, 0.021)→(0.491, -0.038, 0.013) | (0.502, 0.123, 0.025)→(0.502, 0.123, 0.025) | 0.275→0.275 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.370
- lateral_force_integral: None
- approach_alignment: 0.578
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.572
- phase_breakdown.push_score: 0.873
- phase_breakdown.approach_score: 0.677
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.343
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.069
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.257


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74809,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00558,"approach_2.speed":0.04569,"lift_1.lift_height":0.1645,"push_1.push_distance":0.11348,"push_1.push_speed":0.09636},"optimized_scores":{"best_composite_score":-0.12145,"best_fitness_score":0.27855,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":508.0,"contact_point_centroid":[0.5103,0.00738,0.05096],"force_p95":82.72735,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.67035,"mean_force":22.21388,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49756,-0.00241,0.03627]},{"body_a":"world","body_b":"push_box","contact_count":2495.0,"contact_point_centroid":[0.51279,0.00387,-6e-05],"force_p95":42.39625,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.65484,"mean_force":7.25493,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49341,-0.05921,0.03389]},{"body_a":"push_box","body_b":"link7","contact_count":179.0,"contact_point_centroid":[0.53917,0.03579,0.05925],"force_p95":95.31334,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.79557,"mean_force":52.80109,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50141,0.03129,0.03212]},{"body_a":"world","body_b":"push_box","contact_count":1775.0,"contact_point_centroid":[0.55712,0.06758,-0.0003],"force_p95":85.2371,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.24405,"mean_force":27.39237,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51531,0.04613,0.02533]},{"body_a":"push_box","body_b":"link7","contact_count":787.0,"contact_point_centroid":[0.55912,0.08415,0.05471],"force_p95":86.04901,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.49833,"mean_force":55.65616,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51889,0.07527,0.0271]},{"body_a":"push_box","body_b":"link7","contact_count":250.0,"contact_point_centroid":[0.54704,0.07435,0.06072],"force_p95":61.39884,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.02894,"mean_force":24.96492,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51104,0.07326,0.03216]},{"body_a":"attachment","body_b":"push_box","contact_count":678.0,"contact_point_centroid":[0.53238,0.09207,0.04908],"force_p95":45.53212,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.98917,"mean_force":9.60938,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51381,0.08963,0.03404]},{"body_a":"world","body_b":"push_box","contact_count":1254.0,"contact_point_centroid":[0.56307,0.10318,-8e-05],"force_p95":27.69181,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.94543,"mean_force":7.6545,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51399,0.09057,0.03414]},{"body_a":"attachment","body_b":"push_box","contact_count":429.0,"contact_point_centroid":[0.54587,0.10781,0.06043],"force_p95":44.37491,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.65992,"mean_force":31.72456,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5217,0.10636,0.02827]},{"body_a":"world","body_b":"push_box","contact_count":3492.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49925,0.02864,0.16605]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46549,0.01415,0.09528]},{"body_a":"world","body_b":"push_box","contact_count":2992.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46281,-0.07786,0.09175]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.52094,0.05331,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49959,-0.03931,0.01459]}],"total_contact_groups":13},"final_pose_error":0.11095,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52094,0.05331,0.02499],"final_tcp_position":[0.50573,-0.03925,0.02147],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":120.67035,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50028,0.0578,0.03311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4348,-0.02857,0.16105],"tcp_start":[0.50028,0.0578,0.03311],"tcp_to_object_dist_end":0.15322,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2992.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49246,-0.1262,0.02697],"tcp_start":[0.4348,-0.02857,0.16105],"tcp_to_object_dist_end":0.10809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53212,0.07009,0.03154],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.22252,"object_to_goal_dist_start":0.13127,"object_z_max":0.03163,"peak_contact_force":95.28946,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3182.0,"raw_peak_contact_force":120.67035,"tcp_end":[0.50528,0.04385,0.03026],"tcp_start":[0.49246,-0.1262,0.02697],"tcp_to_object_dist_end":0.03756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":809.0,"n_steps_budget":1000.0,"object_pos_end":[0.56363,0.12171,0.0324],"object_pos_start":[0.53212,0.07009,0.03154],"object_to_goal_dist_end":0.27915,"object_to_goal_dist_start":0.22252,"object_z_max":0.03279,"peak_contact_force":31.32145,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2182.0,"raw_peak_contact_force":76.02894,"tcp_end":[0.5265,0.14233,0.02905],"tcp_start":[0.50528,0.04385,0.03026],"tcp_to_object_dist_end":0.04261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52094,0.05331,0.02499],"object_pos_start":[0.56363,0.12171,0.0324],"object_to_goal_dist_end":0.20438,"object_to_goal_dist_start":0.27915,"object_z_max":0.03518,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2991.0,"raw_peak_contact_force":93.24405,"tcp_end":[0.50573,-0.03925,0.02147],"tcp_start":[0.5265,0.14233,0.02905],"tcp_to_object_dist_end":0.09387,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52094,0.05331,0.02499],"object_pos_start":[0.52094,0.05331,0.02499],"object_to_goal_dist_end":0.20438,"object_to_goal_dist_start":0.20438,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49848,-0.03925,0.01334],"tcp_start":[0.50573,-0.03925,0.02147],"tcp_to_object_dist_end":0.09595,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58306,"average_solve_count":307.0,"average_success_count":307.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":9e-05,"approach_2.speed":0.02837,"lift_1.lift_height":0.25656,"push_1.push_distance":0.18183,"push_1.push_speed":0.09048},"optimized_scores":{"best_composite_score":-0.05688,"best_fitness_score":0.34312,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":157.0,"contact_point_centroid":[0.55016,0.11647,0.06215],"force_p95":76.88361,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.38097,"mean_force":47.8077,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51685,0.13617,0.03181]},{"body_a":"world","body_b":"push_box","contact_count":2660.0,"contact_point_centroid":[0.53782,0.11795,-0.00014],"force_p95":74.78845,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.35427,"mean_force":9.38582,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50842,0.02545,0.0232]},{"body_a":"push_box","body_b":"link7","contact_count":412.0,"contact_point_centroid":[0.55541,0.12329,0.05596],"force_p95":78.07607,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.98783,"mean_force":56.04896,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51664,0.11051,0.02766]},{"body_a":"world","body_b":"push_box","contact_count":1213.0,"contact_point_centroid":[0.55176,0.12665,-0.00011],"force_p95":54.11998,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.78506,"mean_force":12.93341,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50949,0.09705,0.03848]},{"body_a":"attachment","body_b":"push_box","contact_count":705.0,"contact_point_centroid":[0.52451,0.10277,0.05423],"force_p95":46.09274,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.63518,"mean_force":11.80735,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50914,0.09533,0.0388]},{"body_a":"attachment","body_b":"push_box","contact_count":263.0,"contact_point_centroid":[0.54223,0.12818,0.06059],"force_p95":43.03439,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.67673,"mean_force":31.54345,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51781,0.12457,0.0284]},{"body_a":"attachment","body_b":"push_box","contact_count":134.0,"contact_point_centroid":[0.50696,0.03752,0.05075],"force_p95":31.07744,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.72481,"mean_force":12.19971,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50259,0.0257,0.0445]},{"body_a":"world","body_b":"push_box","contact_count":3490.0,"contact_point_centroid":[0.5156,0.05029,-1e-05],"force_p95":2.49337,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.9902,"mean_force":0.73411,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49583,-0.05248,0.03854]},{"body_a":"world","body_b":"push_box","contact_count":3960.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50423,0.06072,0.1639]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47617,0.06905,0.08765]},{"body_a":"world","body_b":"push_box","contact_count":3452.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.469,-0.05589,0.08415]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.53089,0.11935,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49684,-0.04458,0.01463]}],"total_contact_groups":12},"final_pose_error":0.10552,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53089,0.11935,0.02499],"final_tcp_position":[0.50296,-0.04458,0.02146],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":87.38097,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3960.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51027,0.12151,0.03099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44615,0.01783,0.14851],"tcp_start":[0.51027,0.12151,0.03099],"tcp_to_object_dist_end":0.14453,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3452.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49343,-0.12672,0.02538],"tcp_start":[0.44615,0.01783,0.14851],"tcp_to_object_dist_end":0.17572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52144,0.07549,0.02663],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.22651,"object_to_goal_dist_start":0.19823,"object_z_max":0.02707,"peak_contact_force":16.12688,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3624.0,"raw_peak_contact_force":42.72481,"tcp_end":[0.50411,0.04231,0.04293],"tcp_start":[0.49343,-0.12672,0.02538],"tcp_to_object_dist_end":0.04082,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":1000.0,"object_pos_end":[0.55977,0.14955,0.03124],"object_pos_start":[0.52144,0.07549,0.02663],"object_to_goal_dist_end":0.30552,"object_to_goal_dist_start":0.22651,"object_z_max":0.03211,"peak_contact_force":74.94093,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2075.0,"raw_peak_contact_force":87.38097,"tcp_end":[0.52043,0.1459,0.02922],"tcp_start":[0.50411,0.04231,0.04293],"tcp_to_object_dist_end":0.03956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53089,0.11935,0.02499],"object_pos_start":[0.55977,0.14955,0.03124],"object_to_goal_dist_end":0.27111,"object_to_goal_dist_start":0.30552,"object_z_max":0.03311,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3335.0,"raw_peak_contact_force":87.35427,"tcp_end":[0.50296,-0.04458,0.02146],"tcp_start":[0.52043,0.1459,0.02922],"tcp_to_object_dist_end":0.16633,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53089,0.11935,0.02499],"object_pos_start":[0.53089,0.11935,0.02499],"object_to_goal_dist_end":0.27111,"object_to_goal_dist_start":0.27111,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49573,-0.04451,0.01339],"tcp_start":[0.50296,-0.04458,0.02146],"tcp_to_object_dist_end":0.16799,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71975,"average_solve_count":314.0,"average_success_count":314.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":6e-05,"approach_2.speed":0.03515,"lift_1.lift_height":0.20147,"push_1.push_distance":0.1921,"push_1.push_speed":0.07075},"optimized_scores":{"best_composite_score":-0.06898,"best_fitness_score":0.33102,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":137.0,"contact_point_centroid":[0.48069,0.05003,0.04566],"force_p95":24.92841,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.34032,"mean_force":9.1478,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48058,0.03816,0.04507]},{"body_a":"attachment","body_b":"push_box","contact_count":437.0,"contact_point_centroid":[0.47391,0.1208,0.03962],"force_p95":22.40191,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.50673,"mean_force":7.81777,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47535,0.10901,0.0391]},{"body_a":"world","body_b":"push_box","contact_count":3521.0,"contact_point_centroid":[0.47901,0.06092,-1e-05],"force_p95":1.0865,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.32119,"mean_force":0.61353,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48494,-0.0474,0.03921]},{"body_a":"world","body_b":"push_box","contact_count":1499.0,"contact_point_centroid":[0.46879,0.1459,-0.00014],"force_p95":9.497,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.10042,"mean_force":2.60713,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.4755,0.1065,0.03911]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.47113,0.17481,0.02589],"force_p95":2.35716,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.35716,"mean_force":2.35716,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47412,0.16326,0.02463]},{"body_a":"world","body_b":"push_box","contact_count":3977.0,"contact_point_centroid":[0.45513,0.19763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70019,"mean_force":0.24681,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47843,0.0624,0.02025]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48715,0.06586,0.16416]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44808,0.07594,0.09006]},{"body_a":"world","body_b":"push_box","contact_count":3920.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45783,-0.05478,0.08595]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.45514,0.19767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47995,-0.03096,0.01372]}],"total_contact_groups":10},"final_pose_error":0.12008,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45514,0.19767,0.02499],"final_tcp_position":[0.48594,-0.03085,0.02013],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":34.34032,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42362,0.02089,0.15291],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.14446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":980.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3920.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49282,-0.12681,0.02497],"tcp_start":[0.42362,0.02089,0.15291],"tcp_to_object_dist_end":0.18578,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47775,0.0925,0.0253],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.24352,"object_to_goal_dist_start":0.2095,"object_z_max":0.02578,"peak_contact_force":0.15955,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3658.0,"raw_peak_contact_force":34.34032,"tcp_end":[0.47984,0.05521,0.0432],"tcp_start":[0.49282,-0.12681,0.02497],"tcp_to_object_dist_end":0.04142,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.45622,0.19631,0.02512],"object_pos_start":[0.47775,0.0925,0.0253],"object_to_goal_dist_end":0.34906,"object_to_goal_dist_start":0.24352,"object_z_max":0.02587,"peak_contact_force":0.65718,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1936.0,"raw_peak_contact_force":31.50673,"tcp_end":[0.47412,0.16326,0.02463],"tcp_start":[0.47984,0.05521,0.0432],"tcp_to_object_dist_end":0.03758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45514,0.19767,0.02499],"object_pos_start":[0.45622,0.19631,0.02512],"object_to_goal_dist_end":0.35055,"object_to_goal_dist_start":0.34906,"object_z_max":0.0252,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3978.0,"raw_peak_contact_force":2.35716,"tcp_end":[0.48594,-0.03085,0.02013],"tcp_start":[0.47412,0.16326,0.02463],"tcp_to_object_dist_end":0.23063,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45514,0.19767,0.02499],"object_pos_start":[0.45514,0.19767,0.02499],"object_to_goal_dist_end":0.35055,"object_to_goal_dist_start":0.35055,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47886,-0.03091,0.01256],"tcp_start":[0.48594,-0.03085,0.02013],"tcp_to_object_dist_end":0.23014,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```