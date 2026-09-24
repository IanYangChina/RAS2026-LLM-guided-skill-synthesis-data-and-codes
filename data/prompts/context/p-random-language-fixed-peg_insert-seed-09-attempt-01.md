## Search State

- **Seed**: 9
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → grasp → approach → align → contact → insert → retract | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.3006 | 0.55 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | 0.4018 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.55 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5296199363176067, -0.017054623272995572, 0.08]
- Frozen socket pose: [0.5296199363176067, -0.017054623272995572, 0.025] (static fixture for this episode)
- Goal object position: (0.5296199363176067, -0.017054623272995572, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5296, -0.0171, 0.08]
  frozen_socket_position: [0.5296, -0.0171, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5296199363176067, -0.017054623272995572, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5296199363176067, -0.017054623272995572, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| align | object | (0.00, 0.00, 0.12) | distance | — |
| approach | object | (0.00, 0.00, 0.09) | distance | — |
| contact | object | (0.00, 0.00, 0.07) | distance | — |
| insert | object | (0.00, 0.00, 0.06) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.301) — your mutation base

```yaml
skill: peg_insert
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
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

```

## Design Metrics

- **Composite score**: -0.301
- **task_score** (E): 0.550
- **fitness_score**: 0.249  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0790 |
| grasp_peg | 1.00 | 0.00 | 0.0084 |
| approach_socket | 0.00 | 0.00 | 0.3968 |
| align_socket | 0.00 | 0.00 | 0.1576 |
| contact_entry | 0.00 | 0.00 | 0.1320 |
| insert_down | 0.00 | 0.33 | 0.6209 |
| retract_up | 0.50 | 0.00 | 0.4914 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.379) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.419) | 0.260→0.339 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.502, -0.000, 0.379)→(0.500, -0.000, 0.371) | (0.501, -0.000, 0.419)→(0.499, -0.000, 0.411) | 0.339→0.331 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_socket | approach | 0.00 / step_budget | (0.500, -0.000, 0.371)→(0.555, -0.075, 0.755) | (0.499, -0.000, 0.411)→(0.552, -0.061, 0.718) | 0.331→0.644 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_socket | align | 0.00 / step_budget | (0.555, -0.075, 0.755)→(0.414, -0.099, 0.820) | (0.552, -0.061, 0.718)→(0.423, -0.094, 0.782) | 0.644→0.716 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_entry | contact | 0.00 / step_budget | (0.414, -0.099, 0.820)→(0.313, -0.141, 0.788) | (0.423, -0.094, 0.782)→(0.329, -0.128, 0.755) | 0.716→0.710 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_down | insert | 0.00 / step_budget | (0.313, -0.141, 0.788)→(0.596, -0.094, 0.282) | (0.329, -0.128, 0.755)→(0.586, -0.076, 0.298) | 0.710→0.304 | 0.33 / 0.333 | 812.931 | 812.931 |
| retract_up | retract | 0.50 / step_budget | (0.657, -0.150, 0.389)→(0.634, 0.138, 0.406) | (0.657, -0.133, 0.403)→(0.636, 0.138, 0.398) | 0.422→0.379 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.756
- alignment_error: None
- force_efficiency: 1.000
- terminal_score: 0.756
- phase_score: 0.145
- phase_breakdown.align_score: 0.001
- phase_breakdown.approach_score: 0.001
- phase_breakdown.insert_score: 0.290
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.390
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.894
- **Median Q (composite search score)**: -0.192
- **K-run variance**: 0.0311
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.260


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9cec5bdbb03cce7c3c09816ace5d94f97b8f61fe750542a4a790173a53dc00b4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `aa1cc88294efeb3bf6fcf727f27d837e44fca2942932baa7feaaed37c752b2f3`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":7.0,"average_failure_rate":0.03139,"average_mean_iterations":15.55605,"average_solve_count":223.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_socket.speed_align":0.07565,"approach_peg.speed_approach":0.12182,"contact_entry.probe_force":6.82102,"contact_entry.probe_speed":0.02036,"grasp_peg.grip_force":16.74734,"insert_down.insert_depth":0.02877,"insert_down.insert_speed":0.04981,"retract_up.retract_speed":0.09918},"optimized_scores":{"best_composite_score":-0.16041,"best_fitness_score":0.38959,"best_task_score":0.75631},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.04794,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.53029,0.0128,0.12249],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50112,-0.0,0.41897],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.33897,"object_to_goal_dist_start":0.26034,"object_z_max":0.41885,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.50229,-1e-05,0.37899],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49937,-1e-05,0.41096],"object_pos_start":[0.50112,-0.0,0.41897],"object_to_goal_dist_end":0.33096,"object_to_goal_dist_start":0.33897,"object_z_max":0.41906,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49983,-3e-05,0.37097],"tcp_start":[0.50229,-1e-05,0.37899],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56481,-0.05037,0.72991],"object_pos_start":[0.49937,-1e-05,0.41096],"object_to_goal_dist_end":0.65508,"object_to_goal_dist_start":0.33096,"object_z_max":0.75019,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.56894,-0.06006,0.7685],"tcp_start":[0.49983,-3e-05,0.37097],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44805,-0.07141,0.79011],"object_pos_start":[0.56481,-0.05037,0.72991],"object_to_goal_dist_end":0.71558,"object_to_goal_dist_start":0.65508,"object_z_max":0.79009,"peak_contact_force":0.0,"phase_name":"align_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.44109,-0.0752,0.82932],"tcp_start":[0.56894,-0.06006,0.7685],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.32843,-0.09992,0.78906],"object_pos_start":[0.44805,-0.07141,0.79011],"object_to_goal_dist_end":0.73633,"object_to_goal_dist_start":0.71558,"object_z_max":0.80087,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.3115,-0.10932,0.82406],"tcp_start":[0.44109,-0.0752,0.82932],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58409,0.02581,0.44878],"object_pos_start":[0.32843,-0.09992,0.78906],"object_to_goal_dist_end":0.37913,"object_to_goal_dist_start":0.73633,"object_z_max":1.11359,"peak_contact_force":0.0,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert","tcp_end":[0.55072,0.00858,0.43502],"tcp_start":[0.3115,-0.10932,0.82406],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56571,0.03127,0.12038],"object_pos_start":[0.58409,0.02581,0.44878],"object_to_goal_dist_end":0.08322,"object_to_goal_dist_start":0.37913,"object_z_max":0.44878,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.53029,0.0128,0.12249],"tcp_start":[0.55072,0.00858,0.43502],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `688a3926bc1208c752fc2d1535fab63bd957243e02b13eac53840dc266efeb6b`; realized-scene SHA-256: `3df42339bb213b8d34da19ed0076dd8b56ad93b79493c43fb7ab2bb6b5f8a158`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.01504,"average_mean_iterations":11.7594,"average_solve_count":133.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_socket.speed_align":0.0747,"approach_peg.speed_approach":0.11133,"contact_entry.probe_force":5.34438,"contact_entry.probe_speed":0.03754,"grasp_peg.grip_force":17.96285,"insert_down.insert_depth":0.03911,"insert_down.insert_speed":0.04022,"retract_up.retract_speed":0.09745},"optimized_scores":{"best_composite_score":-0.19194,"best_fitness_score":0.35806,"best_task_score":0.89371},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.47886,0.02143,0.07692],"force_p95":2438.79203,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2438.79203,"mean_force":2438.79203,"phase_index":5.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.48029,0.01159,0.08512]}],"total_contact_groups":1},"final_pose_error":0.08096,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.47297,0.01798,0.06934],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":2438.79203,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50112,-0.0,0.41897],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.33897,"object_to_goal_dist_start":0.26034,"object_z_max":0.41885,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.50229,-1e-05,0.37899],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49937,-1e-05,0.41096],"object_pos_start":[0.50112,-0.0,0.41897],"object_to_goal_dist_end":0.33096,"object_to_goal_dist_start":0.33897,"object_z_max":0.41906,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49983,-3e-05,0.37097],"tcp_start":[0.50229,-1e-05,0.37899],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57641,-0.04954,0.72567],"object_pos_start":[0.49937,-1e-05,0.41096],"object_to_goal_dist_end":0.65206,"object_to_goal_dist_start":0.33096,"object_z_max":0.75163,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.58164,-0.0581,0.7644],"tcp_start":[0.49983,-3e-05,0.37097],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48005,-0.07325,0.77999],"object_pos_start":[0.57641,-0.04954,0.72567],"object_to_goal_dist_end":0.7041,"object_to_goal_dist_start":0.65206,"object_z_max":0.77995,"peak_contact_force":0.0,"phase_name":"align_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47597,-0.07721,0.81958],"tcp_start":[0.58164,-0.0581,0.7644],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.35316,-0.09774,0.79076],"object_pos_start":[0.48005,-0.07325,0.77999],"object_to_goal_dist_end":0.73233,"object_to_goal_dist_start":0.7041,"object_z_max":0.79827,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.33816,-0.10668,0.82675],"tcp_start":[0.47597,-0.07721,0.81958],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.4437,0.03912,0.08655],"object_pos_start":[0.35316,-0.09774,0.79076],"object_to_goal_dist_end":0.06887,"object_to_goal_dist_start":0.73233,"object_z_max":0.79417,"peak_contact_force":2438.79203,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":2438.79203,"subtask_id":"insert","tcp_end":[0.47297,0.01798,0.06934],"tcp_start":[0.33816,-0.10668,0.82675],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a628d07ffd5fd1634a1f36dba43ee92c313515a1a075bf67fe2ba29ce8996148`; realized-scene SHA-256: `025a988ff91962c08fa963a737fe7ec85e866c8c15bf8e1bf01c5bb6961db318`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.47029,-6e-05,0.025]},{"name":"target","value":[0.47029,-6e-05,0.025]},{"name":"socket","value":[0.47029,-6e-05,0.025]},{"name":"goal","value":[0.47029,-6e-05,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-6e-05,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.35616,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_socket.speed_align":0.03388,"approach_peg.speed_approach":0.05061,"contact_entry.probe_force":6.81097,"contact_entry.probe_speed":0.04659,"grasp_peg.grip_force":25.0776,"insert_down.insert_depth":0.02967,"insert_down.insert_speed":0.02722,"retract_up.retract_speed":0.11064},"optimized_scores":{"best_composite_score":-0.54953,"best_fitness_score":0.00047,"best_task_score":0.00041},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.64933,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.73739,0.26372,0.68982],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":781.0,"n_steps_budget":1000.0,"object_pos_end":[0.50105,-0.0,0.42045],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34046,"object_to_goal_dist_start":0.26034,"object_z_max":0.42037,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.50233,-1e-05,0.38048],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49931,-1e-05,0.41241],"object_pos_start":[0.50105,-0.0,0.42045],"object_to_goal_dist_end":0.33241,"object_to_goal_dist_start":0.34046,"object_z_max":0.42049,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49988,-3e-05,0.37241],"tcp_start":[0.50233,-1e-05,0.38048],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51391,-0.08419,0.69973],"object_pos_start":[0.49931,-1e-05,0.41241],"object_to_goal_dist_end":0.62558,"object_to_goal_dist_start":0.33241,"object_z_max":0.71324,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5148,-0.1055,0.73357],"tcp_start":[0.49988,-3e-05,0.37241],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.33942,-0.13606,0.77589],"object_pos_start":[0.51391,-0.08419,0.69973],"object_to_goal_dist_end":0.72702,"object_to_goal_dist_start":0.62558,"object_z_max":0.80323,"peak_contact_force":0.0,"phase_name":"align_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.32416,-0.1452,0.81172],"tcp_start":[0.5148,-0.1055,0.73357],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.30547,-0.18575,0.68498],"object_pos_start":[0.33942,-0.13606,0.77589],"object_to_goal_dist_end":0.66208,"object_to_goal_dist_start":0.72702,"object_z_max":0.77593,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.28852,-0.20705,0.71429],"tcp_start":[0.32416,-0.1452,0.81172],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.72967,-0.29277,0.35784],"object_pos_start":[0.30547,-0.18575,0.68498],"object_to_goal_dist_end":0.46438,"object_to_goal_dist_start":0.66208,"object_z_max":0.70253,"peak_contact_force":0.0,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert","tcp_end":[0.76312,-0.30795,0.34201],"tcp_start":[0.28852,-0.20705,0.71429],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.70591,0.24422,0.6747],"object_pos_start":[0.72967,-0.29277,0.35784],"object_to_goal_dist_end":0.67506,"object_to_goal_dist_start":0.46438,"object_z_max":0.67185,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.73739,0.26372,0.68982],"tcp_start":[0.76312,-0.30795,0.34201],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```