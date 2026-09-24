## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6230 | 0.82 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 3 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1313 | 0.83 | ❌ rejected |
| 2 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 1 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.0873 | 0.89 | ❌ rejected |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.623) — your mutation base

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

- **Composite score**: 0.623
- **task_score** (E): 0.816
- **fitness_score**: 0.816  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 0.00 | 1.00 | 0.1631 |
| align_1 | 1.00 | 0.33 | 0.0455 |
| push_1 | 0.67 | 0.67 | 0.0101 |
| align_2 | 0.67 | 0.33 | 0.0240 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.443, -0.000, 0.148) | (0.504, -0.000, 0.340)→(0.482, -0.000, 0.139) | 0.260→0.062 | 1.00 / 1.000 | 256.026 | 1127.987 |
| align_1 | align | 1.00 / step_budget | (0.443, -0.000, 0.148)→(0.480, 0.002, 0.138) | (0.482, -0.000, 0.139)→(0.518, 0.002, 0.127) | 0.062→0.057 | 0.33 / 0.333 | 37.410 | 210.094 |
| push_1 | push | 0.67 / force_exceeded | (0.480, 0.002, 0.138)→(0.479, 0.003, 0.128) | (0.518, 0.002, 0.127)→(0.517, 0.003, 0.116) | 0.057→0.049 | 0.67 / 0.667 | 140.130 | 140.130 |
| align_2 | align | 0.67 / step_budget | (0.479, 0.003, 0.128)→(0.490, 0.002, 0.148) | (0.517, 0.003, 0.116)→(0.529, 0.002, 0.138) | 0.049→0.074 | 0.33 / 0.333 | 62.549 | 456.948 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.816
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.816
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.816
- **Median Q (composite search score)**: 0.706
- **K-run variance**: 0.0139
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":40.0,"average_failure_rate":0.45455,"average_mean_iterations":94.95455,"average_solve_count":88.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00087,"align_1.lateral_offset_y":0.0019,"align_2.lateral_offset_x":-0.00658,"align_2.lateral_offset_y":0.00298,"push_1.force_limit":30.83559,"push_1.push_distance":0.08369},"optimized_scores":{"best_composite_score":0.45629,"best_fitness_score":0.81629,"best_task_score":0.81629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":186.0,"contact_point_centroid":[0.55505,0.00153,0.07949],"force_p95":550.17661,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1069.08124,"mean_force":272.66047,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.4431,-0.00011,0.13616]},{"body_a":"peg_socket","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.5296,-0.00361,0.07857],"force_p95":940.97664,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1010.59256,"mean_force":463.21808,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.43602,-0.00011,0.10619]},{"body_a":"peg_socket","body_b":"link7","contact_count":384.0,"contact_point_centroid":[0.56092,0.00984,0.07991],"force_p95":146.15211,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":262.96686,"mean_force":122.84608,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46584,0.01045,0.14902]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.44229,-9e-05,0.07938],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.43693,-0.0001,0.09289]}],"total_contact_groups":4},"final_pose_error":0.03538,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49262,0.03663,0.11526],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1069.08124,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.48594,-9e-05,0.14153],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06312,"object_to_goal_dist_start":0.26034,"object_z_max":0.34427,"peak_contact_force":248.96839,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":223.0,"raw_peak_contact_force":1069.08124,"tcp_end":[0.44689,-8e-05,0.1502],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53334,0.0347,0.11747],"object_pos_start":[0.48594,-9e-05,0.14153],"object_to_goal_dist_end":0.06099,"object_to_goal_dist_start":0.06312,"object_z_max":0.14235,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":384.0,"raw_peak_contact_force":262.96686,"subtask_id":"reach_entry","tcp_end":[0.49447,0.03475,0.12689],"tcp_start":[0.44689,-8e-05,0.1502],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":40.0,"n_steps_budget":840.0,"object_pos_end":[0.5318,0.037,0.10657],"object_pos_start":[0.53334,0.0347,0.11747],"object_to_goal_dist_end":0.05556,"object_to_goal_dist_start":0.06099,"object_z_max":0.11747,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.49301,0.03679,0.11634],"tcp_start":[0.49447,0.03475,0.12689],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.53139,0.03684,0.10543],"object_pos_start":[0.5318,0.037,0.10657],"object_to_goal_dist_end":0.05467,"object_to_goal_dist_start":0.05556,"object_z_max":0.10657,"peak_contact_force":0.0,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49262,0.03663,0.11526],"tcp_start":[0.49301,0.03679,0.11634],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a0b26c055417598cbe086e53f7823e257fb75222f78e6d5a64925f365f02417e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.08197,"average_mean_iterations":22.98361,"average_solve_count":61.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0053,"align_1.lateral_offset_y":-0.00068,"align_2.lateral_offset_x":-0.00273,"align_2.lateral_offset_y":0.00068,"push_1.force_limit":31.18939,"push_1.push_distance":0.11655},"optimized_scores":{"best_composite_score":0.70629,"best_fitness_score":0.81629,"best_task_score":0.81629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":51.0,"contact_point_centroid":[0.65033,0.11447,-0.00037],"force_p95":946.39177,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1094.78341,"mean_force":531.70792,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49434,-0.00569,0.15533]},{"body_a":"peg_socket","body_b":"link7","contact_count":176.0,"contact_point_centroid":[0.5388,0.00242,0.07926],"force_p95":489.52066,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1057.18186,"mean_force":291.91031,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.43156,-0.00011,0.15167]},{"body_a":"world","body_b":"link6","contact_count":167.0,"contact_point_centroid":[0.68876,-0.01009,-0.00016],"force_p95":361.12791,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":475.07156,"mean_force":286.06713,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.48734,-0.01068,0.15124]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54091,-0.01589,0.07997],"force_p95":372.00657,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.00657,"mean_force":372.00657,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48437,-0.0125,0.16373]},{"body_a":"peg_socket","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.54087,-0.01627,0.07998],"force_p95":240.8405,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.38448,"mean_force":153.78891,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.48496,-0.01255,0.15916]},{"body_a":"peg_socket","body_b":"link7","contact_count":482.0,"contact_point_centroid":[0.5409,-0.00451,0.07994],"force_p95":146.88489,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.07102,"mean_force":118.01629,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4584,-0.00574,0.17051]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.44013,-0.0001,0.07924],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.43646,-9e-05,0.09302]}],"total_contact_groups":7},"final_pose_error":0.14541,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.51722,-0.01468,0.22007],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1094.78341,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.47053,-9e-05,0.15602],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08153,"object_to_goal_dist_start":0.26034,"object_z_max":0.34427,"peak_contact_force":256.1665,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":184.0,"raw_peak_contact_force":1057.18186,"tcp_end":[0.43349,-7e-05,0.17113],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.51891,-0.01264,0.14356],"object_pos_start":[0.47053,-9e-05,0.15602],"object_to_goal_dist_end":0.06751,"object_to_goal_dist_start":0.08153,"object_z_max":0.15637,"peak_contact_force":112.22935,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":482.0,"raw_peak_contact_force":251.07102,"subtask_id":"reach_entry","tcp_end":[0.48437,-0.0125,0.16373],"tcp_start":[0.43349,-7e-05,0.17113],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51894,-0.01262,0.14355],"object_pos_start":[0.51891,-0.01264,0.14356],"object_to_goal_dist_end":0.06751,"object_to_goal_dist_start":0.06751,"object_z_max":0.14356,"peak_contact_force":372.00657,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":372.00657,"subtask_id":"insert_peg","tcp_end":[0.48439,-0.01248,0.16371],"tcp_start":[0.48437,-0.0125,0.16373],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":392.0,"n_steps_budget":600.0,"object_pos_end":[0.55559,-0.01469,0.20875],"object_pos_start":[0.51894,-0.01262,0.14355],"object_to_goal_dist_end":0.14101,"object_to_goal_dist_start":0.06751,"object_z_max":0.20705,"peak_contact_force":0.0,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":308.0,"raw_peak_contact_force":1094.78341,"tcp_end":[0.51722,-0.01468,0.22007],"tcp_start":[0.48439,-0.01248,0.16371],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d263ae29be72790e561c8447b0a7b2ba7baa0aae40b60396cc4b2e04f6cc146d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22727,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-4e-05,"align_1.lateral_offset_y":0.00415,"align_2.lateral_offset_x":-0.00622,"align_2.lateral_offset_y":0.00703,"push_1.force_limit":17.66534,"push_1.push_distance":0.07724},"optimized_scores":{"best_composite_score":0.70629,"best_fitness_score":0.81629,"best_task_score":0.81629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":187.0,"contact_point_centroid":[0.52616,-0.0041,0.07935],"force_p95":382.04873,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1257.69697,"mean_force":278.40057,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.44388,-0.00022,0.11631]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.43264,-0.00129,0.07905],"force_p95":955.60683,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1064.88435,"mean_force":249.60344,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.42977,-0.00025,0.09188]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.43748,0.00906,0.07986],"force_p95":488.81574,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":552.07336,"mean_force":170.6073,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.4331,-0.00012,0.09079]},{"body_a":"attachment","body_b":"peg_socket","contact_count":484.0,"contact_point_centroid":[0.52684,-0.016,0.07995],"force_p95":185.75561,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.06204,"mean_force":146.04268,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.46076,-0.01593,0.1072]},{"body_a":"peg_socket","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.52684,-0.0058,0.07999],"force_p95":57.82305,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.24556,"mean_force":29.18199,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44966,-0.00184,0.12232]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52685,-0.01604,0.07995],"force_p95":48.38218,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.38218,"mean_force":48.38218,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45982,-0.01613,0.10472]}],"total_contact_groups":6},"final_pose_error":0.02992,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46129,-0.01558,0.10987],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1257.69697,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.48828,-0.00014,0.11856],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04031,"object_to_goal_dist_start":0.26034,"object_z_max":0.34427,"peak_contact_force":262.94268,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":202.0,"raw_peak_contact_force":1257.69697,"tcp_end":[0.44856,-0.00016,0.12327],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":461.0,"n_steps_budget":600.0,"object_pos_end":[0.50155,-0.01536,0.11871],"object_pos_start":[0.48828,-0.00014,0.11856],"object_to_goal_dist_end":0.04168,"object_to_goal_dist_start":0.04031,"object_z_max":0.11871,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":54.0,"raw_peak_contact_force":116.24556,"subtask_id":"reach_entry","tcp_end":[0.4619,-0.01539,0.12397],"tcp_start":[0.44856,-0.00016,0.12327],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":87.0,"n_steps_budget":780.0,"object_pos_end":[0.4994,-0.01612,0.09883],"object_pos_start":[0.50155,-0.01536,0.11871],"object_to_goal_dist_end":0.0248,"object_to_goal_dist_start":0.04168,"object_z_max":0.11871,"peak_contact_force":48.38218,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":48.38218,"subtask_id":"insert_peg","tcp_end":[0.45981,-0.01614,0.10454],"tcp_start":[0.4619,-0.01539,0.12397],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50033,-0.01574,0.10117],"object_pos_start":[0.4994,-0.01612,0.09883],"object_to_goal_dist_end":0.02638,"object_to_goal_dist_start":0.0248,"object_z_max":0.10117,"peak_contact_force":187.64652,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":484.0,"raw_peak_contact_force":276.06204,"tcp_end":[0.46129,-0.01558,0.10987],"tcp_start":[0.45981,-0.01614,0.10454],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```