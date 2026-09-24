## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.4942 | 0.85 | ❌ rejected |
| 8 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.2720 | 0.76 | ❌ rejected |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 6 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6230 | 0.82 | ❌ rejected |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.494) — your mutation base

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

- **Composite score**: 0.494
- **task_score** (E): 0.847
- **fitness_score**: 0.591  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_hole | 0.00 | 1.00 | 0.1658 |
| align_to_hole | 1.00 | 0.00 | 0.0472 |
| insert_peg | 1.00 | 1.00 | 0.0407 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_hole | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.458, 0.005, 0.142) | (0.504, -0.000, 0.340)→(0.496, 0.005, 0.130) | 0.260→0.053 | 1.00 / 1.000 | 295.364 | 1221.299 |
| align_to_hole | align | 1.00 / step_budget | (0.458, 0.005, 0.142)→(0.486, 0.007, 0.170) | (0.496, 0.005, 0.130)→(0.524, 0.007, 0.157) | 0.053→0.082 | 0.00 / 0.000 | 0.000 | 171.808 |
| insert_peg | insert | 1.00 / force_exceeded | (0.486, 0.007, 0.170)→(0.482, 0.004, 0.129) | (0.524, 0.007, 0.157)→(0.519, 0.004, 0.117) | 0.082→0.045 | 1.00 / 1.000 | 380.328 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.857
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.857
- phase_score: 0.503
- phase_breakdown.approach_hole_score: 0.121
- phase_breakdown.insert_peg_score: 0.607
- phase_breakdown.align_hole_score: 0.748

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.645
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.857
- **Median Q (composite search score)**: 0.530
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.383


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.88636,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_lateral_x":-0.00385,"align_to_hole.align_lateral_y":-0.01906,"align_to_hole.align_tolerance":0.00829,"approach_to_hole.approach_speed":0.24891,"approach_to_hole.approach_tolerance":0.01714,"insert_peg.insertion_depth":0.13152,"insert_peg.insertion_force_threshold":25.31223,"insert_peg.insertion_speed":0.07222},"optimized_scores":{"best_composite_score":0.40449,"best_fitness_score":0.50116,"best_task_score":0.8519},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.46063,0.01029,0.07834],"force_p95":1003.57435,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1094.32382,"mean_force":234.50525,"phase_index":0.0,"phase_name":"approach_to_hole","phase_type":"approach","tcp_position_centroid":[0.45603,0.01026,0.09094]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.47109,0.00594,0.07971],"force_p95":710.23619,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1009.72006,"mean_force":145.88008,"phase_index":0.0,"phase_name":"approach_to_hole","phase_type":"approach","tcp_position_centroid":[0.45942,0.01011,0.09048]},{"body_a":"peg_socket","body_b":"link7","contact_count":209.0,"contact_point_centroid":[0.55938,0.0202,0.07959],"force_p95":405.62569,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":717.60443,"mean_force":299.17828,"phase_index":0.0,"phase_name":"approach_to_hole","phase_type":"approach","tcp_position_centroid":[0.45499,0.0165,0.15409]},{"body_a":"peg_socket","body_b":"link6","contact_count":132.0,"contact_point_centroid":[0.56087,0.02605,0.07985],"force_p95":323.95414,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.74706,"mean_force":295.23934,"phase_index":0.0,"phase_name":"approach_to_hole","phase_type":"approach","tcp_position_centroid":[0.45521,0.02546,0.18274]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56094,0.02912,0.07999],"force_p95":74.31411,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.31411,"mean_force":74.31411,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.45221,0.0288,0.18537]}],"total_contact_groups":5},"final_pose_error":0.22342,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.4835,0.02187,0.17077],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1094.32382,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.48779,0.02949,0.1671],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09277,"object_to_goal_dist_start":0.26034,"object_z_max":0.34457,"peak_contact_force":280.10565,"phase_name":"approach_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":360.0,"raw_peak_contact_force":1094.32382,"subtask_id":"approach_hole","tcp_end":[0.45221,0.0288,0.18537],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":102.0,"n_steps_budget":600.0,"object_pos_end":[0.51937,0.02292,0.15691],"object_pos_start":[0.48779,0.02949,0.1671],"object_to_goal_dist_end":0.08256,"object_to_goal_dist_start":0.09277,"object_z_max":0.16728,"peak_contact_force":0.0,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1.0,"raw_peak_contact_force":74.31411,"subtask_id":"align_hole","tcp_end":[0.48392,0.02209,0.17543],"tcp_start":[0.45221,0.0288,0.18537],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.51883,0.02256,0.15203],"object_pos_start":[0.51937,0.02292,0.15691],"object_to_goal_dist_end":0.07779,"object_to_goal_dist_start":0.08256,"object_z_max":0.15691,"peak_contact_force":426.0812,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.4835,0.02187,0.17077],"tcp_start":[0.48392,0.02209,0.17543],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a0b26c055417598cbe086e53f7823e257fb75222f78e6d5a64925f365f02417e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.39474,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_lateral_x":0.01996,"align_to_hole.align_lateral_y":0.01854,"align_to_hole.align_tolerance":0.01395,"approach_to_hole.approach_speed":0.18614,"approach_to_hole.approach_tolerance":0.0234,"insert_peg.insertion_depth":0.12716,"insert_peg.insertion_force_threshold":29.44388,"insert_peg.insertion_speed":0.02763},"optimized_scores":{"best_composite_score":0.54822,"best_fitness_score":0.64489,"best_task_score":0.85716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":365.0,"contact_point_centroid":[0.54064,-0.01054,0.0797],"force_p95":311.04783,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1455.37432,"mean_force":303.00007,"phase_index":0.0,"phase_name":"approach_to_hole","phase_type":"approach","tcp_position_centroid":[0.46278,-0.0061,0.12024]},{"body_a":"attachment","body_b":"peg_socket","contact_count":20.0,"contact_point_centroid":[0.4486,-0.0168,0.0794],"force_p95":804.64247,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":898.19542,"mean_force":375.6762,"phase_index":0.0,"phase_name":"approach_to_hole","phase_type":"approach","tcp_position_centroid":[0.44434,-0.00505,0.08699]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54089,-0.01143,0.07998],"force_p95":240.12086,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.75015,"mean_force":91.44854,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.4685,-0.00692,0.12936]}],"total_contact_groups":3},"final_pose_error":0.15683,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.48807,-0.00322,0.10898],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1455.37432,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50744,-0.00725,0.12057],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04188,"object_to_goal_dist_start":0.26034,"object_z_max":0.34439,"peak_contact_force":311.34291,"phase_name":"approach_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":1455.37432,"subtask_id":"approach_hole","tcp_end":[0.46843,-0.00692,0.12941],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":248.0,"n_steps_budget":600.0,"object_pos_end":[0.53298,0.00065,0.1574],"object_pos_start":[0.50744,-0.00725,0.12057],"object_to_goal_dist_end":0.08414,"object_to_goal_dist_start":0.04188,"object_z_max":0.15727,"peak_contact_force":0.0,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4.0,"raw_peak_contact_force":264.75015,"subtask_id":"align_hole","tcp_end":[0.4941,0.00099,0.16677],"tcp_start":[0.46843,-0.00692,0.12941],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.52682,-0.00355,0.09905],"object_pos_start":[0.53298,0.00065,0.1574],"object_to_goal_dist_end":0.03309,"object_to_goal_dist_start":0.08414,"object_z_max":0.1574,"peak_contact_force":390.61534,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.48807,-0.00322,0.10898],"tcp_start":[0.4941,0.00099,0.16677],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d263ae29be72790e561c8447b0a7b2ba7baa0aae40b60396cc4b2e04f6cc146d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.67143,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_lateral_x":0.01972,"align_to_hole.align_lateral_y":0.01999,"align_to_hole.align_tolerance":0.00544,"approach_to_hole.approach_speed":0.11603,"approach_to_hole.approach_tolerance":0.02508,"insert_peg.insertion_depth":0.10495,"insert_peg.insertion_force_threshold":28.59877,"insert_peg.insertion_speed":0.04502},"optimized_scores":{"best_composite_score":0.52996,"best_fitness_score":0.62663,"best_task_score":0.83264},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":363.0,"contact_point_centroid":[0.5264,-0.01327,0.06794],"force_p95":294.85161,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1114.19861,"mean_force":290.48942,"phase_index":0.0,"phase_name":"approach_to_hole","phase_type":"approach","tcp_position_centroid":[0.44996,-0.00653,0.10451]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.43544,-0.0203,0.0797],"force_p95":81.09573,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.32419,"mean_force":15.14649,"phase_index":0.0,"phase_name":"approach_to_hole","phase_type":"approach","tcp_position_centroid":[0.43326,-0.0061,0.08354]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52682,-0.01211,0.06423],"force_p95":166.91964,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.35909,"mean_force":99.68698,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.45463,-0.00622,0.11037]}],"total_contact_groups":3},"final_pose_error":0.1338,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47359,-0.00708,0.10795],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1114.19861,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49374,-0.00756,0.1023],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02436,"object_to_goal_dist_start":0.26034,"object_z_max":0.34425,"peak_contact_force":294.64325,"phase_name":"approach_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":379.0,"raw_peak_contact_force":1114.19861,"subtask_id":"approach_hole","tcp_end":[0.4546,-0.00622,0.11041],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":312.0,"n_steps_budget":600.0,"object_pos_end":[0.51952,-0.00306,0.15769],"object_pos_start":[0.49374,-0.00756,0.1023],"object_to_goal_dist_end":0.08016,"object_to_goal_dist_start":0.02436,"object_z_max":0.15753,"peak_contact_force":0.0,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3.0,"raw_peak_contact_force":176.35909,"subtask_id":"align_hole","tcp_end":[0.48049,-0.00172,0.16635],"tcp_start":[0.4546,-0.00622,0.11041],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.5125,-0.00842,0.09874],"object_pos_start":[0.51952,-0.00306,0.15769],"object_to_goal_dist_end":0.02405,"object_to_goal_dist_start":0.08016,"object_z_max":0.15774,"peak_contact_force":324.28663,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.47359,-0.00708,0.10795],"tcp_start":[0.48049,-0.00172,0.16635],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```