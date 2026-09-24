## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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
| approach_1 | 0.33 | 1.00 | 0.1162 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| insert_1 | 0.00 | 1.00 | 0.1290 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.456, -0.003, 0.193) | (0.504, -0.000, 0.340)→(0.490, -0.003, 0.172) | 0.260→0.093 | 1.00 / 1.000 | 290.679 | 1232.216 |
| descend_1 | descend | 1.00 / force_exceeded | (0.456, -0.003, 0.193)→(0.456, -0.003, 0.193) | (0.490, -0.003, 0.172)→(0.490, -0.003, 0.172) | 0.093→0.093 | 1.00 / 1.000 | 305.860 | 305.860 |
| insert_1 | insert | 0.00 / step_budget | (0.456, -0.003, 0.193)→(0.489, -0.002, 0.069) | (0.490, -0.003, 0.172)→(0.491, -0.002, 0.109) | 0.093→0.037 | 1.00 / 1.000 | 279.061 | 561.552 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.922
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.922
- phase_score: 0.618
- phase_breakdown.insert_peg_score: 0.710
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
- **Final σ (mean)**: 0.360


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02963,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0675,"descend_1.contact_force_threshold":12.12628,"insert_1.insert_depth":0.0544,"insert_1.insert_speed":0.01658,"insert_1.pose_tolerance":0.01119},"optimized_scores":{"best_composite_score":0.79312,"best_fitness_score":0.73979,"best_task_score":0.92226},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.4542,-0.00242,0.07874],"force_p95":1000.54915,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1052.27363,"mean_force":167.5419,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44973,-0.00238,0.09176]},{"body_a":"peg_socket","body_b":"link7","contact_count":246.0,"contact_point_centroid":[0.56695,-0.0013,0.07954],"force_p95":371.94831,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":950.05862,"mean_force":272.07818,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45354,-0.00374,0.14724]},{"body_a":"attachment","body_b":"peg_socket","contact_count":424.0,"contact_point_centroid":[0.48095,-0.00876,0.07989],"force_p95":395.84084,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.35571,"mean_force":379.08825,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49266,-0.01637,0.07926]},{"body_a":"peg_socket","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.54049,0.01173,0.0795],"force_p95":433.5231,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":452.15724,"mean_force":258.20314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44747,-0.00254,0.09799]},{"body_a":"peg_socket","body_b":"link6","contact_count":12.0,"contact_point_centroid":[0.57093,-0.01414,0.07995],"force_p95":404.31078,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":430.20776,"mean_force":349.06131,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.45028,-0.01273,0.19025]},{"body_a":"peg_socket","body_b":"link6","contact_count":523.0,"contact_point_centroid":[0.57092,-0.00999,0.07988],"force_p95":283.05435,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.18038,"mean_force":253.81813,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44767,-0.00826,0.16883]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.57088,-0.01351,0.07985],"force_p95":313.15783,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.15783,"mean_force":313.15783,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45711,-0.01222,0.19185]}],"total_contact_groups":7},"final_pose_error":0.05537,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.49588,-0.0166,0.07884],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":1052.27363,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.49222,-0.01182,0.17269],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09376,"object_to_goal_dist_start":0.26034,"object_z_max":0.34445,"peak_contact_force":281.93267,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":798.0,"raw_peak_contact_force":1052.27363,"subtask_id":"approach_hole","tcp_end":[0.45711,-0.01222,0.19185],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.49227,-0.01179,0.17278],"object_pos_start":[0.49222,-0.01182,0.17269],"object_to_goal_dist_end":0.09384,"object_to_goal_dist_start":0.09376,"object_z_max":0.17269,"peak_contact_force":313.15783,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":313.15783,"subtask_id":"approach_hole","tcp_end":[0.45717,-0.01219,0.19195],"tcp_start":[0.45711,-0.01222,0.19185],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49833,-0.01637,0.11877],"object_pos_start":[0.49227,-0.01179,0.17278],"object_to_goal_dist_end":0.04212,"object_to_goal_dist_start":0.09384,"object_z_max":0.20589,"peak_contact_force":4.77368,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":436.0,"raw_peak_contact_force":496.35571,"subtask_id":"insert_peg","tcp_end":[0.49588,-0.0166,0.07884],"tcp_start":[0.45717,-0.01219,0.19195],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.62774,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.02002,"descend_1.contact_force_threshold":13.66129,"insert_1.insert_depth":0.08927,"insert_1.insert_speed":0.01802,"insert_1.pose_tolerance":0.01547},"optimized_scores":{"best_composite_score":0.69858,"best_fitness_score":0.64525,"best_task_score":0.86799},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":547.0,"contact_point_centroid":[0.56091,0.00398,0.07992],"force_p95":281.08572,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1251.57173,"mean_force":278.47389,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4506,0.00597,0.17689]},{"body_a":"peg_socket","body_b":"link7","contact_count":367.0,"contact_point_centroid":[0.55886,0.00753,0.07972],"force_p95":366.33108,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1143.11484,"mean_force":271.20145,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44737,0.00371,0.15547]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45044,0.00246,0.07904],"force_p95":987.02862,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1038.53744,"mean_force":179.45975,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44617,0.00244,0.09245]},{"body_a":"attachment","body_b":"peg_socket","contact_count":589.0,"contact_point_centroid":[0.47094,0.01475,0.07989],"force_p95":409.11197,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":574.91634,"mean_force":391.28423,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47937,0.02327,0.07927]},{"body_a":"peg_socket","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.56093,0.00622,0.07996],"force_p95":438.61874,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.15495,"mean_force":355.50317,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44448,0.00842,0.18135]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56093,0.00554,0.07996],"force_p95":284.83717,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.83717,"mean_force":284.83717,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45123,0.00822,0.18336]}],"total_contact_groups":6},"final_pose_error":0.09052,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.48365,0.02406,0.07877],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1251.57173,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48708,0.00802,0.16564],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08698,"object_to_goal_dist_start":0.26034,"object_z_max":0.34438,"peak_contact_force":272.41286,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":925.0,"raw_peak_contact_force":1251.57173,"subtask_id":"approach_hole","tcp_end":[0.45123,0.00822,0.18336],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.48709,0.00794,0.16567],"object_pos_start":[0.48708,0.00802,0.16564],"object_to_goal_dist_end":0.087,"object_to_goal_dist_start":0.08698,"object_z_max":0.16564,"peak_contact_force":284.83717,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":284.83717,"subtask_id":"approach_hole","tcp_end":[0.45123,0.00813,0.1834],"tcp_start":[0.45123,0.00822,0.18336],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48699,0.024,0.11863],"object_pos_start":[0.48709,0.00794,0.16567],"object_to_goal_dist_end":0.0473,"object_to_goal_dist_start":0.087,"object_z_max":0.18965,"peak_contact_force":372.8223,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":600.0,"raw_peak_contact_force":574.91634,"subtask_id":"insert_peg","tcp_end":[0.48365,0.02406,0.07877],"tcp_start":[0.45123,0.00813,0.1834],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32484,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03701,"descend_1.contact_force_threshold":11.02114,"insert_1.insert_depth":0.0833,"insert_1.insert_speed":0.02438,"insert_1.pose_tolerance":0.01696},"optimized_scores":{"best_composite_score":0.68139,"best_fitness_score":0.62806,"best_task_score":0.8516},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.54044,0.00038,0.07966],"force_p95":353.26564,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1392.80268,"mean_force":287.33201,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44223,-0.00284,0.17101]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.44353,-0.00343,0.07793],"force_p95":815.7217,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":865.64764,"mean_force":126.7758,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43988,-0.00177,0.08975]},{"body_a":"peg_socket","body_b":"link6","contact_count":447.0,"contact_point_centroid":[0.54088,-0.00573,0.07993],"force_p95":316.52324,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":842.76998,"mean_force":302.17663,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45417,-0.00453,0.19732]},{"body_a":"attachment","body_b":"peg_socket","contact_count":518.0,"contact_point_centroid":[0.49469,-0.01103,0.04993],"force_p95":480.41008,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":613.38396,"mean_force":464.7353,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47998,-0.0137,0.05014]},{"body_a":"peg_socket","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.54089,-0.00671,0.07994],"force_p95":441.20532,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":447.44254,"mean_force":376.7542,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.45089,-0.00598,0.20079]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5409,-0.00637,0.07997],"force_p95":319.58373,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.58373,"mean_force":319.58373,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46056,-0.00538,0.20425]}],"total_contact_groups":6},"final_pose_error":0.05388,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.48692,-0.01418,0.05021],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1392.80268,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4913,-0.00519,0.17866],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09918,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":317.69208,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":910.0,"raw_peak_contact_force":1392.80268,"subtask_id":"approach_hole","tcp_end":[0.46056,-0.00538,0.20425],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.49133,-0.00513,0.17868],"object_pos_start":[0.4913,-0.00519,0.17866],"object_to_goal_dist_end":0.09919,"object_to_goal_dist_start":0.09918,"object_z_max":0.17866,"peak_contact_force":319.58373,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":319.58373,"subtask_id":"approach_hole","tcp_end":[0.4606,-0.00531,0.20428],"tcp_start":[0.46056,-0.00538,0.20425],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48765,-0.01396,0.0902],"object_pos_start":[0.49133,-0.00513,0.17868],"object_to_goal_dist_end":0.02125,"object_to_goal_dist_start":0.09919,"object_z_max":0.20543,"peak_contact_force":459.5884,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":535.0,"raw_peak_contact_force":613.38396,"subtask_id":"insert_peg","tcp_end":[0.48692,-0.01418,0.05021],"tcp_start":[0.4606,-0.00531,0.20428],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```