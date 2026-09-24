## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 1.2189 | 0.88 | ❌ rejected |
| 6 | approach → retract → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.3242 | 0.82 | ❌ rejected |
| 5 | approach → retract → descend → push | arc_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.5934 | 0.85 | ❌ rejected |
| 4 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7614 | 0.97 | ❌ rejected |
| 3 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4406 | 0.85 | ❌ rejected |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=1.219) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **rotate_1** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **pull_1** (`pull`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - pull_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 1.219
- **task_score** (E): 0.882
- **fitness_score**: 0.882  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.667
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1425 |
| descend_1 | 1.00 | 1.00 | 0.0002 |
| insert_1 | 1.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.478, -0.004, 0.160) | (0.504, -0.000, 0.340)→(0.514, -0.004, 0.144) | 0.260→0.066 | 1.00 / 1.667 | 284.417 | 1048.222 |
| descend_1 | descend | 1.00 / force_exceeded | (0.478, -0.004, 0.160)→(0.478, -0.004, 0.160) | (0.514, -0.004, 0.144)→(0.515, -0.004, 0.144) | 0.066→0.066 | 1.00 / 1.333 | 250.359 | 269.773 |
| insert_1 | push | 1.00 / force_exceeded | (0.478, -0.004, 0.160)→(0.478, -0.004, 0.160) | (0.515, -0.004, 0.144)→(0.515, -0.004, 0.144) | 0.066→0.067 | 1.00 / 1.000 | 251.611 | 251.611 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.894
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.894
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.894
- **Median Q (composite search score)**: 1.227
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.403


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fc05e51a25fc23cdfa051e1c0c9cb8327fc4318047dd2c0794162fe696d964b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `78de15924f40c9df864f10a8c33fe438e6928bbf6063e6b2cf47f87609839b79`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.08333,"average_solve_count":24.0,"average_success_count":24.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13024,"approach_1.lateral_x_offset":0.04961,"approach_1.lateral_y_offset":0.02606,"descend_1.descent_force_threshold":14.42861,"insert_1.insertion_depth":0.12386,"insert_1.insertion_force_threshold":37.24362},"optimized_scores":{"best_composite_score":1.19856,"best_fitness_score":0.86189,"best_task_score":0.86189},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.45891,0.00958,0.07938],"force_p95":852.02479,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":857.55615,"mean_force":628.07934,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45579,-0.00092,0.088]},{"body_a":"peg_socket","body_b":"link7","contact_count":414.0,"contact_point_centroid":[0.52654,-0.00744,0.06641],"force_p95":334.10065,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":779.26564,"mean_force":300.53482,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45596,-0.00946,0.11281]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.6793,-0.00746,-0.0],"force_p95":346.14184,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":346.14184,"mean_force":346.14184,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46158,-0.00815,0.11955]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52679,-0.013,0.06385],"force_p95":307.6514,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.46186,"mean_force":264.35727,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.4616,-0.00823,0.11957]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52678,-0.00728,0.06391],"force_p95":281.48612,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":287.89924,"mean_force":223.76809,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46159,-0.00818,0.11955]},{"body_a":"world","body_b":"link6","contact_count":88.0,"contact_point_centroid":[0.67924,-0.00753,-4e-05],"force_p95":173.12452,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.03361,"mean_force":39.46011,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46161,-0.00828,0.11961]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.52685,-0.00746,0.07998],"force_p95":141.54447,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.37053,"mean_force":116.10996,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46159,-0.00818,0.11955]},{"body_a":"attachment","body_b":"peg_socket","contact_count":96.0,"contact_point_centroid":[0.52685,-0.00755,0.07998],"force_p95":105.01227,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.80441,"mean_force":89.11186,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46158,-0.00828,0.11958]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52685,-0.0075,0.08],"force_p95":114.64717,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.64717,"mean_force":114.64717,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46159,-0.00821,0.11957]}],"total_contact_groups":9},"final_pose_error":0.16403,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.4616,-0.00833,0.11959],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":857.55615,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49919,-0.00779,0.10592],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02708,"object_to_goal_dist_start":0.26034,"object_z_max":0.34462,"peak_contact_force":271.23533,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":604.0,"raw_peak_contact_force":857.55615,"subtask_id":"reach_approach","tcp_end":[0.46158,-0.00815,0.11955],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.4992,-0.00785,0.10595],"object_pos_start":[0.49919,-0.00779,0.10592],"object_to_goal_dist_end":0.02713,"object_to_goal_dist_start":0.02708,"object_z_max":0.10594,"peak_contact_force":287.89924,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":346.14184,"tcp_end":[0.46159,-0.00821,0.11957],"tcp_start":[0.46158,-0.00815,0.11955],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49921,-0.00797,0.10598],"object_pos_start":[0.4992,-0.00785,0.10595],"object_to_goal_dist_end":0.02719,"object_to_goal_dist_start":0.02713,"object_z_max":0.10597,"peak_contact_force":312.46186,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":312.46186,"subtask_id":"reach_insertion","tcp_end":[0.4616,-0.00833,0.11959],"tcp_start":[0.46159,-0.00821,0.11957],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.72727,"average_solve_count":22.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19733,"approach_1.lateral_x_offset":0.0499,"approach_1.lateral_y_offset":-0.01385,"descend_1.descent_force_threshold":15.76089,"insert_1.insertion_depth":0.088,"insert_1.insertion_force_threshold":42.1272},"optimized_scores":{"best_composite_score":1.22709,"best_fitness_score":0.89043,"best_task_score":0.89043},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":315.0,"contact_point_centroid":[0.59537,-0.00783,0.07973],"force_p95":320.65581,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1179.83399,"mean_force":260.63983,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47144,-0.00599,0.16469]},{"body_a":"peg_socket","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.58004,-0.00512,0.07872],"force_p95":770.78528,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1088.14295,"mean_force":215.35359,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46934,-0.00486,0.12853]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.47668,-0.00364,0.07901],"force_p95":516.52964,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":939.1448,"mean_force":93.91448,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46992,-0.00363,0.09168]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.56361,-0.02928,0.07885],"force_p95":859.16647,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":906.20844,"mean_force":241.72606,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4671,-0.00356,0.09829]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59518,-0.00891,0.07948],"force_p95":146.41923,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.41923,"mean_force":146.41923,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49375,-0.00899,0.18159]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59524,-0.00878,0.0796],"force_p95":132.7828,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.7828,"mean_force":132.7828,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.49396,-0.00894,0.18171]}],"total_contact_groups":6},"final_pose_error":0.19444,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.49422,-0.00881,0.18177],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1179.83399,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.52921,-0.00847,0.16309],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08848,"object_to_goal_dist_start":0.26034,"object_z_max":0.34562,"peak_contact_force":276.18259,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":407.0,"raw_peak_contact_force":1179.83399,"subtask_id":"reach_approach","tcp_end":[0.49375,-0.00899,0.18159],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.52943,-0.00841,0.16322],"object_pos_start":[0.52921,-0.00847,0.16309],"object_to_goal_dist_end":0.08867,"object_to_goal_dist_start":0.08848,"object_z_max":0.16309,"peak_contact_force":146.41923,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":146.41923,"tcp_end":[0.49396,-0.00894,0.18171],"tcp_start":[0.49375,-0.00899,0.18159],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52972,-0.00826,0.16333],"object_pos_start":[0.52943,-0.00841,0.16322],"object_to_goal_dist_end":0.08886,"object_to_goal_dist_start":0.08867,"object_z_max":0.16322,"peak_contact_force":132.7828,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":132.7828,"subtask_id":"reach_insertion","tcp_end":[0.49422,-0.00881,0.18177],"tcp_start":[0.49396,-0.00894,0.18171],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.68182,"average_solve_count":22.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19842,"approach_1.lateral_x_offset":0.04993,"approach_1.lateral_y_offset":-0.01733,"descend_1.descent_force_threshold":17.02231,"insert_1.insertion_depth":0.18631,"insert_1.insertion_force_threshold":22.1367},"optimized_scores":{"best_composite_score":1.23093,"best_fitness_score":0.89427,"best_task_score":0.89427},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":253.0,"contact_point_centroid":[0.58139,0.00644,0.07953],"force_p95":541.13466,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1107.27464,"mean_force":278.23169,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46798,0.00324,0.14719]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.47373,0.00211,0.0785],"force_p95":429.1013,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":953.55845,"mean_force":79.4632,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46966,0.00209,0.09142]},{"body_a":"peg_socket","body_b":"link6","contact_count":97.0,"contact_point_centroid":[0.58429,0.00322,0.07974],"force_p95":786.86255,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":920.76231,"mean_force":317.77259,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47401,0.00483,0.17265]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58429,0.00386,0.07977],"force_p95":316.75705,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.75705,"mean_force":316.75705,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47885,0.00573,0.17939]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5843,0.00378,0.07978],"force_p95":309.58777,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.58777,"mean_force":309.58777,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47893,0.00566,0.17951]}],"total_contact_groups":5},"final_pose_error":0.29014,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.47899,0.00559,0.17962],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1107.27464,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":435.0,"n_steps_budget":600.0,"object_pos_end":[0.51488,0.00562,0.16202],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08355,"object_to_goal_dist_start":0.26034,"object_z_max":0.34567,"peak_contact_force":305.8321,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":362.0,"raw_peak_contact_force":1107.27464,"subtask_id":"reach_approach","tcp_end":[0.47885,0.00573,0.17939],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.51494,0.00555,0.16211],"object_pos_start":[0.51488,0.00562,0.16202],"object_to_goal_dist_end":0.08364,"object_to_goal_dist_start":0.08355,"object_z_max":0.16202,"peak_contact_force":316.75705,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":316.75705,"tcp_end":[0.47893,0.00566,0.17951],"tcp_start":[0.47885,0.00573,0.17939],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.515,0.00548,0.16219],"object_pos_start":[0.51494,0.00555,0.16211],"object_to_goal_dist_end":0.08373,"object_to_goal_dist_start":0.08364,"object_z_max":0.16211,"peak_contact_force":309.58777,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":309.58777,"subtask_id":"reach_insertion","tcp_end":[0.47899,0.00559,0.17962],"tcp_start":[0.47893,0.00566,0.17951],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```