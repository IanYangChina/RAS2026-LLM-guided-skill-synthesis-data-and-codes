## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → align → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1924 | 0.82 | ❌ rejected |
| 6 | approach → insert | arc_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | pose_tolerance | 5 | 0.1530 | 0.82 | ❌ rejected |
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.7240 | 0.88 | ❌ rejected |
| 4 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.7240 | 0.88 | ✅ accepted |
| 3 | approach → align → descend → insert | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1414 | 0.84 | ❌ rejected |

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

## Current Skill (Q=0.192) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_hole
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: insert_peg
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_hole
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: approach_hole
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    pose_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: insert_peg

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.08, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.192
- **task_score** (E): 0.819
- **fitness_score**: 0.402  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1501 |
| align_1 | 0.00 | 1.00 | 0.0094 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| insert_1 | 0.00 | 1.00 | 0.0004 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.443, -0.003, 0.163) | (0.504, -0.000, 0.340)→(0.481, -0.002, 0.150) | 0.260→0.075 | 1.00 / 2.000 | 288.085 | 1057.754 |
| align_1 | align | 0.00 / step_budget | (0.443, -0.003, 0.163)→(0.445, -0.009, 0.166) | (0.481, -0.002, 0.150)→(0.482, -0.007, 0.153) | 0.075→0.077 | 1.00 / 1.667 | 230.313 | 389.688 |
| descend_1 | descend | 1.00 / force_exceeded | (0.445, -0.009, 0.166)→(0.445, -0.009, 0.166) | (0.482, -0.007, 0.153)→(0.482, -0.007, 0.153) | 0.077→0.077 | 1.00 / 1.667 | 330.616 | 330.616 |
| insert_1 | insert | 0.00 / guard_failure | (0.445, -0.010, 0.166)→(0.445, -0.010, 0.166) | (0.482, -0.007, 0.153)→(0.482, -0.007, 0.153) | 0.077→0.077 | 1.00 / 1.000 | 181.319 | 386.662 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.841
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.841
- phase_score: 0.139
- phase_breakdown.insert_peg_score: 0.167
- phase_breakdown.approach_hole_score: 0.074

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.420
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.841
- **Median Q (composite search score)**: 0.186
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.415


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `193ea3a1ce1ed79056963f057d25ec25a24d300f4824e32f67c8dd96cb6cee27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a8b82e05e54fe244d72795229d8ab0587efc7638aafbc9b6be7ad9630911a897`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.13462,"average_solve_count":52.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_tolerance":0.01207,"approach_1.approach_speed":0.07002,"approach_1.arc_height":0.06019,"descend_1.contact_force_threshold":10.04177,"insert_1.insert_depth":0.08347,"insert_1.insert_speed":0.03367,"insert_1.pose_tolerance":0.01242,"insert_1.retry_lateral_offset":0.01338},"optimized_scores":{"best_composite_score":0.21021,"best_fitness_score":0.42021,"best_task_score":0.84134},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45608,-0.0101,0.07893],"force_p95":989.88914,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1034.71601,"mean_force":196.98168,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45185,-0.01003,0.09225]},{"body_a":"peg_socket","body_b":"link7","contact_count":350.0,"contact_point_centroid":[0.56799,-0.01243,0.07969],"force_p95":515.24719,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":943.79438,"mean_force":269.20168,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4506,-0.01449,0.14924]},{"body_a":"peg_socket","body_b":"link6","contact_count":185.0,"contact_point_centroid":[0.57078,-0.0181,0.07941],"force_p95":579.39309,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":601.49344,"mean_force":342.98638,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44926,-0.01567,0.15446]},{"body_a":"peg_socket","body_b":"link6","contact_count":753.0,"contact_point_centroid":[0.57089,-0.01651,0.07982],"force_p95":314.10546,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":444.15822,"mean_force":215.14881,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44289,-0.02046,0.14279]},{"body_a":"peg_socket","body_b":"link7","contact_count":753.0,"contact_point_centroid":[0.57,-0.01523,0.07996],"force_p95":249.27941,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":382.70892,"mean_force":155.91238,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44289,-0.02046,0.14279]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.57095,-0.01707,0.08],"force_p95":320.10415,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.45894,"mean_force":253.91102,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44439,-0.02555,0.14532]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.57095,-0.01701,0.08],"force_p95":283.65853,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.65853,"mean_force":283.65853,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44441,-0.02549,0.14536]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.57028,-0.02174,0.07999],"force_p95":214.79064,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.52296,"mean_force":135.58734,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44434,-0.02557,0.14521]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.57027,-0.02177,0.07998],"force_p95":143.52433,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.52433,"mean_force":143.52433,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44441,-0.02549,0.14536]}],"total_contact_groups":9},"final_pose_error":0.16282,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.44401,-0.02569,0.14476],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":1034.71601,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.48422,-0.01631,0.14003],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06418,"object_to_goal_dist_start":0.26034,"object_z_max":0.34468,"peak_contact_force":371.96978,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":545.0,"raw_peak_contact_force":1034.71601,"subtask_id":"approach_hole","tcp_end":[0.44487,-0.01616,0.1472],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.4838,-0.02318,0.13881],"object_pos_start":[0.48422,-0.01631,0.14003],"object_to_goal_dist_end":0.06526,"object_to_goal_dist_start":0.06418,"object_z_max":0.14003,"peak_contact_force":163.01508,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1506.0,"raw_peak_contact_force":444.15822,"subtask_id":"approach_hole","tcp_end":[0.44441,-0.02549,0.14536],"tcp_start":[0.44487,-0.01616,0.1472],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.48381,-0.0232,0.13882],"object_pos_start":[0.4838,-0.02318,0.13881],"object_to_goal_dist_end":0.06527,"object_to_goal_dist_start":0.06526,"object_z_max":0.13881,"peak_contact_force":283.65853,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":283.65853,"subtask_id":"approach_hole","tcp_end":[0.44442,-0.0255,0.14537],"tcp_start":[0.44441,-0.02549,0.14536],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48376,-0.02326,0.13875],"object_pos_start":[0.48381,-0.0232,0.13882],"object_to_goal_dist_end":0.06524,"object_to_goal_dist_start":0.06527,"object_z_max":0.13882,"peak_contact_force":225.52296,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":327.45894,"subtask_id":"insert_peg","tcp_end":[0.44401,-0.02569,0.14476],"tcp_start":[0.44424,-0.02563,0.14501],"tcp_to_object_dist_end":0.04028,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.11765,"average_solve_count":51.0,"average_success_count":51.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_tolerance":0.01138,"approach_1.approach_speed":0.05597,"approach_1.arc_height":0.03608,"descend_1.contact_force_threshold":4.4712,"insert_1.insert_depth":0.04359,"insert_1.insert_speed":0.03929,"insert_1.pose_tolerance":0.01198,"insert_1.retry_lateral_offset":0.0145},"optimized_scores":{"best_composite_score":0.18553,"best_fitness_score":0.39553,"best_task_score":0.80493},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":403.0,"contact_point_centroid":[0.55788,0.02457,0.07975],"force_p95":427.26158,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1038.51525,"mean_force":171.67156,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44142,0.0183,0.15406]},{"body_a":"peg_socket","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.52937,0.00579,0.07844],"force_p95":893.25316,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":968.12831,"mean_force":410.92638,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43444,0.01427,0.10358]},{"body_a":"peg_socket","body_b":"link6","contact_count":401.0,"contact_point_centroid":[0.56089,0.02336,0.07974],"force_p95":359.37163,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":585.72967,"mean_force":234.39923,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44227,0.01851,0.15883]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.56094,0.02413,0.07999],"force_p95":317.63942,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.43355,"mean_force":310.49228,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44569,0.0093,0.16781]},{"body_a":"peg_socket","body_b":"link6","contact_count":692.0,"contact_point_centroid":[0.56092,0.02482,0.07996],"force_p95":255.29533,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.15693,"mean_force":242.37411,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44004,0.01096,0.15525]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56094,0.02433,0.07999],"force_p95":253.58696,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.58696,"mean_force":253.58696,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44577,0.00959,0.16765]},{"body_a":"peg_socket","body_b":"link7","contact_count":75.0,"contact_point_centroid":[0.55968,0.0292,0.08],"force_p95":114.00446,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.04611,"mean_force":47.10177,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44002,0.01388,0.15484]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.44177,0.01289,0.07974],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43692,0.01283,0.09373]}],"total_contact_groups":8},"final_pose_error":0.14535,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.44521,0.00886,0.16787],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1038.51525,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.47939,0.0205,0.14669],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07275,"object_to_goal_dist_start":0.26034,"object_z_max":0.3442,"peak_contact_force":259.04857,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":1038.51525,"subtask_id":"approach_hole","tcp_end":[0.44076,0.01825,0.15685],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.48305,0.01538,0.15434],"object_pos_start":[0.47939,0.0205,0.14669],"object_to_goal_dist_end":0.07779,"object_to_goal_dist_start":0.07275,"object_z_max":0.15428,"peak_contact_force":256.13752,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":767.0,"raw_peak_contact_force":289.15693,"subtask_id":"approach_hole","tcp_end":[0.44577,0.00959,0.16765],"tcp_start":[0.44076,0.01825,0.15685],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.48309,0.0153,0.1544],"object_pos_start":[0.48305,0.01538,0.15434],"object_to_goal_dist_end":0.07782,"object_to_goal_dist_start":0.07779,"object_z_max":0.15434,"peak_contact_force":253.58696,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":253.58696,"subtask_id":"approach_hole","tcp_end":[0.44583,0.0095,0.16774],"tcp_start":[0.44577,0.00959,0.16765],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48307,0.01511,0.1545],"object_pos_start":[0.48309,0.0153,0.1544],"object_to_goal_dist_end":0.07788,"object_to_goal_dist_start":0.07782,"object_z_max":0.15454,"peak_contact_force":318.43355,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":318.43355,"subtask_id":"insert_peg","tcp_end":[0.44521,0.00886,0.16787],"tcp_start":[0.44554,0.0091,0.16788],"tcp_to_object_dist_end":0.04063,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.10417,"average_solve_count":48.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_tolerance":0.0099,"approach_1.approach_speed":0.04266,"approach_1.arc_height":0.09281,"descend_1.contact_force_threshold":18.45479,"insert_1.insert_depth":0.07647,"insert_1.insert_speed":0.02773,"insert_1.pose_tolerance":0.00748,"insert_1.retry_lateral_offset":0.01508},"optimized_scores":{"best_composite_score":0.1814,"best_fitness_score":0.3914,"best_task_score":0.8113},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":439.0,"contact_point_centroid":[0.53971,-0.00604,0.07972],"force_p95":334.68384,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1100.03126,"mean_force":220.344,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4365,-0.00895,0.16833]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.43948,-0.00529,0.07893],"force_p95":501.23403,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":911.3346,"mean_force":91.13346,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43555,-0.0052,0.09232]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.54086,-0.0132,0.07922],"force_p95":497.45453,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":514.09456,"mean_force":390.3801,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44577,-0.0123,0.18584]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54086,-0.01325,0.07922],"force_p95":454.60129,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":454.60129,"mean_force":454.60129,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44596,-0.01227,0.186]},{"body_a":"peg_socket","body_b":"link6","contact_count":510.0,"contact_point_centroid":[0.54087,-0.0127,0.07917],"force_p95":314.27785,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":435.74933,"mean_force":274.44665,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45289,-0.01107,0.19154]},{"body_a":"peg_socket","body_b":"link6","contact_count":249.0,"contact_point_centroid":[0.54086,-0.01185,0.07928],"force_p95":270.30085,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.60824,"mean_force":242.91581,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43992,-0.01018,0.18034]},{"body_a":"peg_socket","body_b":"link7","contact_count":499.0,"contact_point_centroid":[0.54032,-0.00667,0.07996],"force_p95":165.59274,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":306.58198,"mean_force":120.23162,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45275,-0.01108,0.19143]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54022,-0.00697,0.07999],"force_p95":300.58529,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.58529,"mean_force":300.58529,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44596,-0.01227,0.186]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54022,-0.00691,0.07999],"force_p95":276.84268,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":285.24175,"mean_force":225.59265,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44577,-0.0123,0.18584]}],"total_contact_groups":9},"final_pose_error":0.18535,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.44525,-0.01233,0.18538],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1100.03126,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":604.0,"n_steps_budget":720.0,"object_pos_end":[0.47839,-0.01073,0.16419],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08758,"object_to_goal_dist_start":0.26034,"object_z_max":0.34405,"peak_contact_force":233.23557,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":698.0,"raw_peak_contact_force":1100.03126,"subtask_id":"approach_hole","tcp_end":[0.44338,-0.01065,0.18353],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":512.0,"n_steps_budget":600.0,"object_pos_end":[0.48047,-0.01211,0.16578],"object_pos_start":[0.47839,-0.01073,0.16419],"object_to_goal_dist_end":0.08881,"object_to_goal_dist_start":0.08758,"object_z_max":0.1723,"peak_contact_force":271.78537,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1009.0,"raw_peak_contact_force":435.74933,"subtask_id":"approach_hole","tcp_end":[0.44596,-0.01227,0.186],"tcp_start":[0.44338,-0.01065,0.18353],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.48045,-0.01209,0.16577],"object_pos_start":[0.48047,-0.01211,0.16578],"object_to_goal_dist_end":0.0888,"object_to_goal_dist_start":0.08881,"object_z_max":0.16578,"peak_contact_force":454.60129,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":454.60129,"subtask_id":"approach_hole","tcp_end":[0.44593,-0.01224,0.18598],"tcp_start":[0.44596,-0.01227,0.186],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48035,-0.01214,0.1657],"object_pos_start":[0.48045,-0.01209,0.16577],"object_to_goal_dist_end":0.08876,"object_to_goal_dist_start":0.0888,"object_z_max":0.16577,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":514.09456,"subtask_id":"insert_peg","tcp_end":[0.44525,-0.01233,0.18538],"tcp_start":[0.44558,-0.01233,0.18567],"tcp_to_object_dist_end":0.04024,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```