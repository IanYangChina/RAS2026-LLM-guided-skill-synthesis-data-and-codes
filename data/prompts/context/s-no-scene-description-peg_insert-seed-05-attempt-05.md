## Search State

- **Seed**: 5
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4773 | 0.86 | ❌ rejected |
| 4 | push → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.9106 | 0.86 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ❌ rejected |
| 1 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5974 | 0.83 | ❌ rejected |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=0.477) — your mutation base

```yaml
skill: peg_insert
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
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
- id: release_2
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.477
- **task_score** (E): 0.859
- **fitness_score**: 0.424  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_push | 0.67 | 1.00 | 0.1179 |
| insert_peg | 1.00 | 1.00 | 0.0001 |
| retract_free | 1.00 | 0.00 | 0.0390 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_push | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.466, 0.011, 0.189) | (0.504, -0.000, 0.340)→(0.500, 0.011, 0.170) | 0.260→0.092 | 1.00 / 1.000 | 290.013 | 1088.819 |
| insert_peg | insert | 1.00 / force_exceeded | (0.466, 0.011, 0.189)→(0.466, 0.011, 0.189) | (0.500, 0.011, 0.170)→(0.501, 0.011, 0.170) | 0.092→0.092 | 1.00 / 1.000 | 319.197 | 319.197 |
| retract_free | retract | 1.00 / step_budget | (0.466, 0.011, 0.189)→(0.500, 0.021, 0.179) | (0.501, 0.011, 0.170)→(0.535, 0.021, 0.160) | 0.092→0.093 | 0.00 / 0.000 | 0.000 | 308.903 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.864
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.864
- phase_score: 0.153
- phase_breakdown.approach_target_score: 0.509
- phase_breakdown.insertion_progress_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.437
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.864
- **Median Q (composite search score)**: 0.473
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.364


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `5e5af3f51d5f63e3a348998ea00f94a7255959965642a40069d0a7b5ef8ede34`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `cc7f64fba434a86728ba6288ab9746a03660fc43702ba486c544717f06e4937d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.46341,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_push.speed":0.138,"insert_peg.force_threshold":26.33275,"insert_peg.insert_depth":0.07254,"insert_peg.speed":0.0446,"retract_free.speed":0.06816},"optimized_scores":{"best_composite_score":0.49059,"best_fitness_score":0.43725,"best_task_score":0.86416},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.467,0.00355,0.07879],"force_p95":1039.37849,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1086.50923,"mean_force":316.26019,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.46084,0.00355,0.09131]},{"body_a":"peg_socket","body_b":"link6","contact_count":292.0,"contact_point_centroid":[0.58434,0.01171,0.07981],"force_p95":302.34768,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":893.02235,"mean_force":260.1282,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.46242,0.01303,0.17011]},{"body_a":"peg_socket","body_b":"link7","contact_count":158.0,"contact_point_centroid":[0.57752,0.00947,0.07954],"force_p95":423.79856,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":785.54655,"mean_force":260.54426,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.46251,0.00617,0.13763]},{"body_a":"peg_socket","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.55388,-0.00546,0.07938],"force_p95":426.20065,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":441.83612,"mean_force":292.16709,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.45824,0.00377,0.10174]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58427,0.01652,0.07976],"force_p95":330.11393,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":330.11393,"mean_force":330.11393,"phase_index":1.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.47487,0.0187,0.19265]},{"body_a":"peg_socket","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.58433,0.01921,0.07984],"force_p95":298.39703,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.11382,"mean_force":176.95703,"phase_index":2.0,"phase_name":"retract_free","phase_type":"retract","tcp_position_centroid":[0.48082,0.01914,0.1887]},{"body_a":"peg_socket","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.58434,0.02226,0.07996],"force_p95":223.79824,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.37114,"mean_force":157.687,"phase_index":2.0,"phase_name":"retract_free","phase_type":"retract","tcp_position_centroid":[0.48895,0.02105,0.18302]}],"total_contact_groups":7},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51299,0.03517,0.18751],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1086.50923,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50961,0.01872,0.17281],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09517,"object_to_goal_dist_start":0.26034,"object_z_max":0.34459,"peak_contact_force":296.88402,"phase_name":"approach_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":486.0,"raw_peak_contact_force":1086.50923,"subtask_id":"approach_target","tcp_end":[0.47487,0.0187,0.19265],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50967,0.0187,0.1729],"object_pos_start":[0.50961,0.01872,0.17281],"object_to_goal_dist_end":0.09526,"object_to_goal_dist_start":0.09517,"object_z_max":0.17281,"peak_contact_force":330.11393,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":330.11393,"subtask_id":"insertion_progress","tcp_end":[0.47496,0.01867,0.19277],"tcp_start":[0.47487,0.0187,0.19265],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":175.0,"n_steps_budget":600.0,"object_pos_end":[0.54551,0.03578,0.16086],"object_pos_start":[0.50967,0.0187,0.1729],"object_to_goal_dist_end":0.09945,"object_to_goal_dist_start":0.09526,"object_z_max":0.17335,"peak_contact_force":0.0,"phase_name":"retract_free","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":16.0,"raw_peak_contact_force":324.11382,"tcp_end":[0.51131,0.03568,0.18161],"tcp_start":[0.47496,0.01867,0.19277],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `619899a8ac3451ebc6b92c72992387b20e095386c555898a9ee2a3180ddd0ca3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.17073,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_push.speed":0.14467,"insert_peg.force_threshold":26.94182,"insert_peg.insert_depth":0.07087,"insert_peg.speed":0.01005,"retract_free.speed":0.09208},"optimized_scores":{"best_composite_score":0.47254,"best_fitness_score":0.41921,"best_task_score":0.85622},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.46122,-0.00212,0.07843],"force_p95":1043.52383,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1090.42177,"mean_force":232.81711,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.4565,-0.00204,0.09107]},{"body_a":"peg_socket","body_b":"link7","contact_count":398.0,"contact_point_centroid":[0.56189,-0.00288,0.07973],"force_p95":331.9568,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":818.58503,"mean_force":283.99433,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.4584,-0.00489,0.15753]},{"body_a":"peg_socket","body_b":"link6","contact_count":38.0,"contact_point_centroid":[0.56296,-0.00993,0.0798],"force_p95":308.51324,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.41479,"mean_force":280.71088,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.45685,-0.00828,0.1775]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56302,-0.0101,0.07993],"force_p95":287.12816,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":287.12816,"mean_force":287.12816,"phase_index":1.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.45822,-0.00849,0.17972]},{"body_a":"peg_socket","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.56303,-0.01006,0.07995],"force_p95":249.60859,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":285.90115,"mean_force":117.05641,"phase_index":2.0,"phase_name":"retract_free","phase_type":"retract","tcp_position_centroid":[0.45834,-0.00845,0.17983]}],"total_contact_groups":5},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.48986,-0.01309,0.18508],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1090.42177,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49421,-0.00853,0.16227],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08292,"object_to_goal_dist_start":0.26034,"object_z_max":0.3445,"peak_contact_force":279.60509,"phase_name":"approach_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":449.0,"raw_peak_contact_force":1090.42177,"subtask_id":"approach_target","tcp_end":[0.45822,-0.00849,0.17972],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,-0.00852,0.16234],"object_pos_start":[0.49421,-0.00853,0.16227],"object_to_goal_dist_end":0.08298,"object_to_goal_dist_start":0.08292,"object_z_max":0.16227,"peak_contact_force":287.12816,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":287.12816,"subtask_id":"insertion_progress","tcp_end":[0.45827,-0.00847,0.1798],"tcp_start":[0.45822,-0.00849,0.17972],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":85.0,"n_steps_budget":600.0,"object_pos_end":[0.52348,-0.01316,0.16122],"object_pos_start":[0.49426,-0.00852,0.16234],"object_to_goal_dist_end":0.08557,"object_to_goal_dist_start":0.08298,"object_z_max":0.16842,"peak_contact_force":0.0,"phase_name":"retract_free","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5.0,"raw_peak_contact_force":285.90115,"tcp_end":[0.48778,-0.01331,0.17927],"tcp_start":[0.45827,-0.00847,0.1798],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `09a021eaed2a28b8f97b40a956e668b0df532c8dfcbc8d48b91f00ceefb0c83a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.2439,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_push.speed":0.14394,"insert_peg.force_threshold":31.48936,"insert_peg.insert_depth":0.07119,"insert_peg.speed":0.04572,"retract_free.speed":0.0748},"optimized_scores":{"best_composite_score":0.46872,"best_fitness_score":0.41539,"best_task_score":0.85766},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.46239,0.00475,0.07853],"force_p95":1040.34664,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1089.52569,"mean_force":292.81379,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.45768,0.00467,0.09128]},{"body_a":"peg_socket","body_b":"link7","contact_count":198.0,"contact_point_centroid":[0.56705,0.01294,0.07955],"force_p95":403.25166,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":713.98783,"mean_force":291.43965,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.45891,0.0092,0.14891]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56996,0.02061,0.07992],"force_p95":340.3484,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.3484,"mean_force":340.3484,"phase_index":1.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46345,0.02235,0.19558]},{"body_a":"peg_socket","body_b":"link6","contact_count":234.0,"contact_point_centroid":[0.56992,0.01786,0.07981],"force_p95":306.91176,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.4023,"mean_force":271.96014,"phase_index":0.0,"phase_name":"approach_push","phase_type":"approach","tcp_position_centroid":[0.45598,0.01863,0.17968]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56998,0.02064,0.07995],"force_p95":296.50062,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.6931,"mean_force":167.88879,"phase_index":2.0,"phase_name":"retract_free","phase_type":"retract","tcp_position_centroid":[0.46355,0.02236,0.19575]}],"total_contact_groups":5},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50303,0.04015,0.18331],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1089.52569,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49768,0.0227,0.17489],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0976,"object_to_goal_dist_start":0.26034,"object_z_max":0.34451,"peak_contact_force":293.55086,"phase_name":"approach_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":445.0,"raw_peak_contact_force":1089.52569,"subtask_id":"approach_target","tcp_end":[0.46345,0.02235,0.19558],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49774,0.0227,0.17499],"object_pos_start":[0.49768,0.0227,0.17489],"object_to_goal_dist_end":0.09769,"object_to_goal_dist_start":0.0976,"object_z_max":0.17489,"peak_contact_force":340.3484,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":340.3484,"subtask_id":"insertion_progress","tcp_end":[0.46352,0.02234,0.1957],"tcp_start":[0.46345,0.02235,0.19558],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":163.0,"n_steps_budget":600.0,"object_pos_end":[0.5353,0.03891,0.15655],"object_pos_start":[0.49774,0.0227,0.17499],"object_to_goal_dist_end":0.09284,"object_to_goal_dist_start":0.09769,"object_z_max":0.17558,"peak_contact_force":0.0,"phase_name":"retract_free","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3.0,"raw_peak_contact_force":316.6931,"tcp_end":[0.50117,0.04024,0.17737],"tcp_start":[0.46352,0.02234,0.1957],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```