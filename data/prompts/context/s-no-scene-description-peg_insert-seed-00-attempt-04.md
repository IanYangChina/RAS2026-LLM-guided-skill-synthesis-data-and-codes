## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.7240 | 0.88 | ✅ accepted |
| 3 | approach → align → descend → insert | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1414 | 0.84 | ❌ rejected |
| 2 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.7244 | 0.88 | ✅ accepted |
| 1 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | -0.0851 | 0.60 | ✅ accepted |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | -0.0851 | 0.60 | ✅ accepted |

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

## Current Skill (Q=0.724) — your mutation base

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

- **Composite score**: 0.724
- **task_score** (E): 0.881
- **fitness_score**: 0.671  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1159 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| insert_1 | 0.00 | 1.00 | 0.1290 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.457, -0.003, 0.193) | (0.504, -0.000, 0.340)→(0.490, -0.003, 0.173) | 0.260→0.093 | 1.00 / 1.000 | 291.303 | 1232.725 |
| descend_1 | descend | 1.00 / force_exceeded | (0.457, -0.003, 0.193)→(0.457, -0.003, 0.193) | (0.490, -0.003, 0.173)→(0.490, -0.003, 0.173) | 0.093→0.094 | 1.00 / 1.000 | 306.526 | 306.526 |
| insert_1 | insert | 0.00 / step_budget | (0.457, -0.003, 0.193)→(0.488, -0.002, 0.069) | (0.490, -0.003, 0.173)→(0.490, -0.002, 0.109) | 0.094→0.037 | 1.00 / 1.000 | 399.952 | 566.871 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.922
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.922
- phase_score: 0.618
- phase_breakdown.insert_peg_score: 0.709
- phase_breakdown.approach_hole_score: 0.405

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.740
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.922
- **Median Q (composite search score)**: 0.699
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.252


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.29104,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06762,"descend_1.contact_force_threshold":10.42629,"insert_1.insert_depth":0.05861,"insert_1.insert_speed":0.02824,"insert_1.pose_tolerance":0.01129},"optimized_scores":{"best_composite_score":0.79291,"best_fitness_score":0.73958,"best_task_score":0.92214},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.4542,-0.00242,0.07874],"force_p95":1000.54915,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1052.27363,"mean_force":167.5419,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44973,-0.00238,0.09176]},{"body_a":"peg_socket","body_b":"link7","contact_count":246.0,"contact_point_centroid":[0.56695,-0.0013,0.07954],"force_p95":371.94831,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":950.05862,"mean_force":272.07818,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45354,-0.00374,0.14724]},{"body_a":"attachment","body_b":"peg_socket","contact_count":437.0,"contact_point_centroid":[0.48095,-0.00814,0.07989],"force_p95":397.0377,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.97078,"mean_force":380.71193,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49227,-0.0163,0.07929]},{"body_a":"peg_socket","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.54049,0.01173,0.0795],"force_p95":433.5231,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":452.15724,"mean_force":258.20314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44747,-0.00254,0.09799]},{"body_a":"peg_socket","body_b":"link6","contact_count":12.0,"contact_point_centroid":[0.57093,-0.01414,0.07995],"force_p95":404.29235,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":430.17659,"mean_force":349.05761,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.45028,-0.01273,0.19025]},{"body_a":"peg_socket","body_b":"link6","contact_count":523.0,"contact_point_centroid":[0.57092,-0.00999,0.07988],"force_p95":283.05435,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.18038,"mean_force":253.81813,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44767,-0.00826,0.16883]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.57088,-0.01351,0.07985],"force_p95":313.15783,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.15783,"mean_force":313.15783,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45711,-0.01222,0.19185]}],"total_contact_groups":7},"final_pose_error":0.05964,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.49547,-0.01653,0.07895],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":1052.27363,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.49222,-0.01182,0.17269],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09376,"object_to_goal_dist_start":0.26034,"object_z_max":0.34445,"peak_contact_force":281.93267,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":798.0,"raw_peak_contact_force":1052.27363,"subtask_id":"approach_hole","tcp_end":[0.45711,-0.01222,0.19185],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.49227,-0.01179,0.17278],"object_pos_start":[0.49222,-0.01182,0.17269],"object_to_goal_dist_end":0.09384,"object_to_goal_dist_start":0.09376,"object_z_max":0.17269,"peak_contact_force":313.15783,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":313.15783,"subtask_id":"approach_hole","tcp_end":[0.45717,-0.01219,0.19195],"tcp_start":[0.45711,-0.01222,0.19185],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49797,-0.01629,0.11887],"object_pos_start":[0.49227,-0.01179,0.17278],"object_to_goal_dist_end":0.04219,"object_to_goal_dist_start":0.09384,"object_z_max":0.20532,"peak_contact_force":367.00113,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":449.0,"raw_peak_contact_force":520.97078,"subtask_id":"insert_peg","tcp_end":[0.49547,-0.01653,0.07895],"tcp_start":[0.45717,-0.01219,0.19195],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.76984,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.02005,"descend_1.contact_force_threshold":6.92428,"insert_1.insert_depth":0.10034,"insert_1.insert_speed":0.04,"insert_1.pose_tolerance":0.01584},"optimized_scores":{"best_composite_score":0.69877,"best_fitness_score":0.64544,"best_task_score":0.86812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":547.0,"contact_point_centroid":[0.56091,0.00398,0.07992],"force_p95":281.08572,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1251.57173,"mean_force":278.47389,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4506,0.00597,0.17689]},{"body_a":"peg_socket","body_b":"link7","contact_count":367.0,"contact_point_centroid":[0.55886,0.00753,0.07972],"force_p95":366.33108,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1143.11484,"mean_force":271.20145,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44737,0.00371,0.15547]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45044,0.00246,0.07904],"force_p95":987.02862,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1038.53744,"mean_force":179.45975,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44617,0.00244,0.09245]},{"body_a":"attachment","body_b":"peg_socket","contact_count":605.0,"contact_point_centroid":[0.47094,0.01243,0.0799],"force_p95":413.88995,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":584.43997,"mean_force":392.54467,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47821,0.02252,0.07931]},{"body_a":"peg_socket","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.56093,0.00623,0.07997],"force_p95":438.51275,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.04366,"mean_force":355.4914,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44448,0.00843,0.18136]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56093,0.00554,0.07996],"force_p95":284.83717,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.83717,"mean_force":284.83717,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45123,0.00822,0.18336]}],"total_contact_groups":6},"final_pose_error":0.10152,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.48273,0.02337,0.07874],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1251.57173,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48708,0.00802,0.16564],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08698,"object_to_goal_dist_start":0.26034,"object_z_max":0.34438,"peak_contact_force":272.41286,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":925.0,"raw_peak_contact_force":1251.57173,"subtask_id":"approach_hole","tcp_end":[0.45123,0.00822,0.18336],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.48709,0.00794,0.16567],"object_pos_start":[0.48708,0.00802,0.16564],"object_to_goal_dist_end":0.087,"object_to_goal_dist_start":0.08698,"object_z_max":0.16564,"peak_contact_force":284.83717,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":284.83717,"subtask_id":"approach_hole","tcp_end":[0.45123,0.00813,0.1834],"tcp_start":[0.45123,0.00822,0.18336],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48651,0.02329,0.11856],"object_pos_start":[0.48709,0.00794,0.16567],"object_to_goal_dist_end":0.04702,"object_to_goal_dist_start":0.087,"object_z_max":0.18733,"peak_contact_force":374.39476,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":616.0,"raw_peak_contact_force":584.43997,"subtask_id":"insert_peg","tcp_end":[0.48273,0.02337,0.07874],"tcp_start":[0.45123,0.00813,0.1834],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37748,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0378,"descend_1.contact_force_threshold":14.84397,"insert_1.insert_depth":0.08433,"insert_1.insert_speed":0.03658,"insert_1.pose_tolerance":0.01449},"optimized_scores":{"best_composite_score":0.6804,"best_fitness_score":0.62706,"best_task_score":0.8523},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":404.0,"contact_point_centroid":[0.5404,0.00034,0.07962],"force_p95":385.15564,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1394.32815,"mean_force":288.17751,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44173,-0.00281,0.17004]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.44363,-0.00347,0.07787],"force_p95":816.31362,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":866.14858,"mean_force":126.86453,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43998,-0.0018,0.08962]},{"body_a":"peg_socket","body_b":"link6","contact_count":493.0,"contact_point_centroid":[0.54089,-0.00567,0.07993],"force_p95":318.3228,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":839.79266,"mean_force":301.6193,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45402,-0.00446,0.19743]},{"body_a":"attachment","body_b":"peg_socket","contact_count":464.0,"contact_point_centroid":[0.49385,-0.01054,0.04992],"force_p95":484.09991,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":595.20095,"mean_force":467.51204,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47924,-0.01359,0.05007]},{"body_a":"peg_socket","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.5409,-0.00667,0.07996],"force_p95":426.17172,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":454.30799,"mean_force":383.82839,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4524,-0.00603,0.20186]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5409,-0.00637,0.07997],"force_p95":321.58303,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":321.58303,"mean_force":321.58303,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4612,-0.0054,0.20509]}],"total_contact_groups":6},"final_pose_error":0.05471,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.48553,-0.014,0.05014],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1394.32815,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49175,-0.0052,0.17927],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09974,"object_to_goal_dist_start":0.26034,"object_z_max":0.34437,"peak_contact_force":319.56485,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":910.0,"raw_peak_contact_force":1394.32815,"subtask_id":"approach_hole","tcp_end":[0.4612,-0.0054,0.20509],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.49178,-0.00513,0.17929],"object_pos_start":[0.49175,-0.0052,0.17927],"object_to_goal_dist_end":0.09976,"object_to_goal_dist_start":0.09974,"object_z_max":0.17927,"peak_contact_force":321.58303,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":321.58303,"subtask_id":"approach_hole","tcp_end":[0.46124,-0.00533,0.20512],"tcp_start":[0.4612,-0.0054,0.20509],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48609,-0.0138,0.09014],"object_pos_start":[0.49178,-0.00513,0.17929],"object_to_goal_dist_end":0.02206,"object_to_goal_dist_start":0.09976,"object_z_max":0.20832,"peak_contact_force":458.45899,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":481.0,"raw_peak_contact_force":595.20095,"subtask_id":"insert_peg","tcp_end":[0.48553,-0.014,0.05014],"tcp_start":[0.46124,-0.00533,0.20512],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```