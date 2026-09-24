## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1313 | 0.83 | ❌ rejected |
| 2 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 1 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.0873 | 0.89 | ❌ rejected |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.131) — your mutation base

```yaml
skill: peg_insert
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
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
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: 0.131
- **task_score** (E): 0.835
- **fitness_score**: 0.411  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1615 |
| align_1 | 0.67 | 0.67 | 0.0167 |
| insert_1 | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.458, 0.006, 0.146) | (0.504, -0.000, 0.340)→(0.495, 0.005, 0.134) | 0.260→0.056 | 1.00 / 1.000 | 296.090 | 1263.271 |
| align_1 | align | 0.67 / step_budget | (0.458, 0.006, 0.146)→(0.469, 0.010, 0.157) | (0.495, 0.005, 0.134)→(0.504, 0.008, 0.140) | 0.056→0.062 | 0.67 / 1.000 | 201.076 | 346.048 |
| insert_1 | insert | 0.00 / guard_failure | (0.469, 0.010, 0.157)→(0.469, 0.010, 0.157) | (0.504, 0.008, 0.140)→(0.504, 0.008, 0.140) | 0.062→0.062 | 1.00 / 1.000 | 216.690 | 320.432 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.843
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.843
- phase_score: 0.141
- phase_breakdown.reach_insert_score: 0.023
- phase_breakdown.reach_pre_insert_score: 0.417

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.422
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.843
- **Median Q (composite search score)**: 0.128
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.511


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `45273c8d1228632fd57317b0a02550505db6d7cbf023a115124b89e828802a94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `70dcb1d9cf130ce66aaa294bb82afc0ceb52288177fb1bbf0b6209922022fad5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.04762,"average_solve_count":42.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00842,"align_1.lateral_offset_y":-0.00998,"approach_1.approach_speed":0.155,"insert_1.insertion_force_threshold":21.28968,"insert_1.push_distance":0.05226},"optimized_scores":{"best_composite_score":0.14195,"best_fitness_score":0.42195,"best_task_score":0.84292},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.45595,0.0069,0.07862],"force_p95":1021.23262,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1070.07796,"mean_force":246.27247,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45147,0.00684,0.09154]},{"body_a":"peg_socket","body_b":"link7","contact_count":182.0,"contact_point_centroid":[0.55815,0.01595,0.07946],"force_p95":437.43106,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":822.76503,"mean_force":295.23338,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45099,0.01181,0.15019]},{"body_a":"peg_socket","body_b":"link6","contact_count":216.0,"contact_point_centroid":[0.56086,0.02141,0.07982],"force_p95":322.59315,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.02651,"mean_force":294.29185,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45359,0.02151,0.18438]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56089,0.03087,0.07994],"force_p95":348.11782,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":348.11782,"mean_force":348.11782,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47426,0.03169,0.21397]},{"body_a":"peg_socket","body_b":"link6","contact_count":539.0,"contact_point_centroid":[0.5609,0.02799,0.07993],"force_p95":291.77742,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.29075,"mean_force":268.45487,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45581,0.02797,0.19785]}],"total_contact_groups":5},"final_pose_error":0.18813,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.47419,0.03193,0.21391],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1070.07796,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.48555,0.02712,0.17046],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09554,"object_to_goal_dist_start":0.26034,"object_z_max":0.34441,"peak_contact_force":283.34092,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":410.0,"raw_peak_contact_force":1070.07796,"subtask_id":"reach_pre_insert","tcp_end":[0.45039,0.02644,0.18952],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50448,0.03155,0.18776],"object_pos_start":[0.48555,0.02712,0.17046],"object_to_goal_dist_end":0.11237,"object_to_goal_dist_start":0.09554,"object_z_max":0.18835,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":539.0,"raw_peak_contact_force":328.29075,"subtask_id":"reach_pre_insert","tcp_end":[0.47433,0.03159,0.21405],"tcp_start":[0.45039,0.02644,0.18952],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50431,0.03192,0.1876],"object_pos_start":[0.50448,0.03155,0.18776],"object_to_goal_dist_end":0.11231,"object_to_goal_dist_start":0.11237,"object_z_max":0.18776,"peak_contact_force":348.11782,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":348.11782,"subtask_id":"reach_insert","tcp_end":[0.47419,0.03193,0.21391],"tcp_start":[0.47433,0.03159,0.21405],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a0b26c055417598cbe086e53f7823e257fb75222f78e6d5a64925f365f02417e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.09756,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00883,"align_1.lateral_offset_y":0.00996,"approach_1.approach_speed":0.26649,"insert_1.insertion_force_threshold":31.96456,"insert_1.push_distance":0.06462},"optimized_scores":{"best_composite_score":0.12397,"best_fitness_score":0.40397,"best_task_score":0.83386},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":422.0,"contact_point_centroid":[0.54057,-0.00827,0.07965],"force_p95":308.54193,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1457.95045,"mean_force":295.94248,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46148,-0.00423,0.127]},{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.44351,-0.00588,0.07765],"force_p95":832.96489,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":883.24178,"mean_force":163.98803,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43984,-0.00351,0.08878]},{"body_a":"peg_socket","body_b":"link7","contact_count":486.0,"contact_point_centroid":[0.54085,-0.00979,0.07997],"force_p95":310.8741,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.45654,"mean_force":307.38841,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46964,-0.00394,0.1382]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54085,-0.00961,0.07997],"force_p95":301.95074,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":301.95074,"mean_force":301.95074,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46947,-0.00259,0.13783]}],"total_contact_groups":4},"final_pose_error":0.12372,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.46947,-0.00264,0.13783],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1457.95045,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50656,-0.00547,0.12614],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04692,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":309.03297,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":437.0,"raw_peak_contact_force":1457.95045,"subtask_id":"reach_pre_insert","tcp_end":[0.4678,-0.00488,0.13599],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":486.0,"n_steps_budget":600.0,"object_pos_end":[0.50793,-0.00414,0.12694],"object_pos_start":[0.50656,-0.00547,0.12614],"object_to_goal_dist_end":0.04779,"object_to_goal_dist_start":0.04692,"object_z_max":0.12754,"peak_contact_force":305.29674,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":486.0,"raw_peak_contact_force":318.45654,"subtask_id":"reach_pre_insert","tcp_end":[0.46947,-0.00259,0.13783],"tcp_start":[0.4678,-0.00488,0.13599],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":780.0,"object_pos_end":[0.50793,-0.00419,0.12694],"object_pos_start":[0.50793,-0.00414,0.12694],"object_to_goal_dist_end":0.04779,"object_to_goal_dist_start":0.04779,"object_z_max":0.12694,"peak_contact_force":301.95074,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":301.95074,"subtask_id":"reach_insert","tcp_end":[0.46947,-0.00264,0.13783],"tcp_start":[0.46947,-0.00259,0.13783],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d263ae29be72790e561c8447b0a7b2ba7baa0aae40b60396cc4b2e04f6cc146d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.07317,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00992,"align_1.lateral_offset_y":-0.00309,"approach_1.approach_speed":0.16259,"insert_1.insertion_force_threshold":22.32251,"insert_1.push_distance":0.09848},"optimized_scores":{"best_composite_score":0.12799,"best_fitness_score":0.40799,"best_task_score":0.82703},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":420.0,"contact_point_centroid":[0.52645,-0.00901,0.06982],"force_p95":296.0086,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1261.78581,"mean_force":291.49507,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45031,-0.00488,0.1078]},{"body_a":"attachment","body_b":"peg_socket","contact_count":17.0,"contact_point_centroid":[0.43536,0.00426,0.0797],"force_p95":615.0158,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":773.63593,"mean_force":107.62953,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43247,-0.00496,0.08725]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.43788,0.00914,0.07991],"force_p95":509.12491,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":534.17139,"mean_force":336.503,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43479,-0.00432,0.08543]},{"body_a":"peg_socket","body_b":"link7","contact_count":542.0,"contact_point_centroid":[0.52677,-0.01038,0.06547],"force_p95":328.14201,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.39693,"mean_force":313.4092,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46185,-0.0009,0.12082]},{"body_a":"world","body_b":"link6","contact_count":231.0,"contact_point_centroid":[0.67864,-0.01681,-3e-05],"force_p95":159.62227,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":387.81595,"mean_force":59.86305,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46294,-0.00056,0.12199]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67898,-0.0205,-2e-05],"force_p95":311.22825,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":311.22825,"mean_force":311.22825,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46292,0.00123,0.12056]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52677,-0.01125,0.06445],"force_p95":204.37194,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.37194,"mean_force":204.37194,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46292,0.00123,0.12056]}],"total_contact_groups":7},"final_pose_error":0.14089,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46293,0.00137,0.12055],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1261.78581,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49412,-0.00598,0.10501],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02638,"object_to_goal_dist_start":0.26034,"object_z_max":0.34424,"peak_contact_force":295.89497,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":442.0,"raw_peak_contact_force":1261.78581,"subtask_id":"reach_pre_insert","tcp_end":[0.45507,-0.00436,0.11348],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50022,-0.00301,0.10674],"object_pos_start":[0.49412,-0.00598,0.10501],"object_to_goal_dist_end":0.02691,"object_to_goal_dist_start":0.02638,"object_z_max":0.10887,"peak_contact_force":297.93237,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":773.0,"raw_peak_contact_force":391.39693,"subtask_id":"reach_pre_insert","tcp_end":[0.46292,0.00123,0.12056],"tcp_start":[0.45507,-0.00436,0.11348],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":900.0,"object_pos_end":[0.50023,-0.00287,0.10674],"object_pos_start":[0.50022,-0.00301,0.10674],"object_to_goal_dist_end":0.0269,"object_to_goal_dist_start":0.02691,"object_z_max":0.10674,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":311.22825,"subtask_id":"reach_insert","tcp_end":[0.46293,0.00137,0.12055],"tcp_start":[0.46292,0.00123,0.12056],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```