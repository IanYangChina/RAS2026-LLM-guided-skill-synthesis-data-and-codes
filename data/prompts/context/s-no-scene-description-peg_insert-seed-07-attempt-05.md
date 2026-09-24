## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0733 | 0.82 | ❌ rejected |
| 4 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0088 | 0.76 | ❌ rejected |
| 3 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0842 | 0.87 | ✅ accepted |
| 2 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0765 | 0.87 | ✅ accepted |
| 1 | approach → grasp → retract → approach → align → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | force_threshold_switch | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.1778 | 0.85 | ✅ accepted |

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

## Current Skill (Q=-0.073) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: approach_hole
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: insert_task
  weight: 0.5
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
- id: grasp_peg
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.002
    - 0.002
    - 0.0
- id: lift_peg
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_hole
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
    - 0.05
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_hole
- id: align_hole
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.003
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
- id: descend_insert
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.06
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: insert_task

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **grasp_peg** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.002, 0.002, 0.0]
- **lift_peg** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_hole** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_hole** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.003
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **descend_insert** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.06, mode=replace_offset_projection, sign=negative}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=3, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: -0.073
- **task_score** (E): 0.820
- **fitness_score**: 0.577  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0802 |
| descend_to_peg | 0.00 | 0.00 | 0.0319 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0368 |
| approach_hole | 0.33 | 0.00 | 0.2134 |
| align_hole | 0.67 | 0.67 | 0.1498 |
| descend_insert | 0.67 | 0.67 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.381) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.421) | 0.260→0.341 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.502, -0.000, 0.381)→(0.500, -0.000, 0.412) | (0.501, -0.000, 0.421)→(0.497, 0.000, 0.452) | 0.341→0.372 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.498, -0.000, 0.404)→(0.498, -0.000, 0.404) | (0.497, 0.000, 0.452)→(0.495, 0.000, 0.444) | 0.372→0.364 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.404)→(0.497, -0.000, 0.441) | (0.495, 0.000, 0.444)→(0.492, 0.000, 0.481) | 0.364→0.401 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.33 / step_budget | (0.497, -0.000, 0.441)→(0.502, 0.015, 0.230) | (0.492, 0.000, 0.481)→(0.510, 0.015, 0.269) | 0.401→0.192 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.67 / step_budget | (0.502, 0.015, 0.230)→(0.522, 0.019, 0.088) | (0.510, 0.015, 0.269)→(0.559, 0.018, 0.095) | 0.192→0.074 | 0.67 / 1.000 | 278.201 | 2998.855 |
| descend_insert | descend | 0.67 / step_budget | (0.522, 0.019, 0.088)→(0.522, 0.019, 0.088) | (0.559, 0.018, 0.095)→(0.559, 0.018, 0.095) | 0.074→0.074 | 0.67 / 1.000 | 263.174 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.896
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.896
- phase_score: 0.442
- phase_breakdown.approach_hole_score: 0.291
- phase_breakdown.approach_peg_score: 0.830
- phase_breakdown.insert_task_score: 0.377

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.624
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.896
- **Median Q (composite search score)**: -0.090
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.302


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0c4288e4b4f4eb50f7d141bdaea44f8ed4eecfe7429f8148c247811f0f5250bc`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2ae90e10c3e712e9da92b27bc0ded08b6d103e49e03139a26a0fa45d3ac81c97`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":22.0,"average_failure_rate":0.10427,"average_mean_iterations":24.51185,"average_solve_count":211.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.05032,"align_hole.lateral_offset_x":-0.00828,"align_hole.lateral_offset_y":0.00791,"approach_hole.speed":0.03225,"approach_peg.speed":0.0802,"descend_insert.force_threshold":17.89669,"descend_insert.insertion_depth":0.08163,"descend_to_peg.contact_force_threshold":8.22162,"descend_to_peg.descend_speed":0.16379,"lift_peg.lift_height":0.05718},"optimized_scores":{"best_composite_score":-0.08991,"best_fitness_score":0.56009,"best_task_score":0.83621},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.47901,0.02102,0.07959],"force_p95":2873.74928,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2905.39473,"mean_force":515.1471,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48107,0.03355,0.07287]},{"body_a":"attachment","body_b":"peg_socket","contact_count":49.0,"contact_point_centroid":[0.54007,0.04659,0.07986],"force_p95":1135.57871,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2851.22911,"mean_force":417.4745,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49389,0.05242,0.0895]},{"body_a":"peg_socket","body_b":"link7","contact_count":915.0,"contact_point_centroid":[0.56981,0.01751,0.07995],"force_p95":440.76127,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1227.5731,"mean_force":295.40678,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49005,0.04577,0.09246]},{"body_a":"attachment","body_b":"peg_socket","contact_count":376.0,"contact_point_centroid":[0.49431,0.06182,0.07994],"force_p95":350.10075,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":810.64824,"mean_force":169.45769,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49217,0.05299,0.09144]}],"total_contact_groups":4},"final_pose_error":0.10002,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.49457,0.0566,0.09402],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":2905.39473,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.50108,-0.0,0.42006],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34007,"object_to_goal_dist_start":0.26034,"object_z_max":0.41996,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50233,-1e-05,0.38008],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49661,1e-05,0.45175],"object_pos_start":[0.50108,-0.0,0.42006],"object_to_goal_dist_end":0.37176,"object_to_goal_dist_start":0.34007,"object_z_max":0.45169,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50002,-1e-05,0.41189],"tcp_start":[0.50233,-1e-05,0.38008],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49529,1e-05,0.44378],"object_pos_start":[0.49661,1e-05,0.45175],"object_to_goal_dist_end":0.36381,"object_to_goal_dist_start":0.37176,"object_z_max":0.45176,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49801,-2e-05,0.40387],"tcp_start":[0.49801,-2e-05,0.40387],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49089,2e-05,0.49122],"object_pos_start":[0.49529,1e-05,0.44378],"object_to_goal_dist_end":0.41132,"object_to_goal_dist_start":0.36381,"object_z_max":0.49114,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4972,-2e-05,0.45172],"tcp_start":[0.49801,-2e-05,0.40387],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50965,0.02193,0.29828],"object_pos_start":[0.49089,2e-05,0.49122],"object_to_goal_dist_end":0.2196,"object_to_goal_dist_start":0.41132,"object_z_max":0.49124,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.50361,0.02184,0.25874],"tcp_start":[0.4972,-2e-05,0.45172],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53402,0.0501,0.09503],"object_pos_start":[0.50965,0.02193,0.29828],"object_to_goal_dist_end":0.0624,"object_to_goal_dist_start":0.2196,"object_z_max":0.29828,"peak_contact_force":522.15692,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1354.0,"raw_peak_contact_force":2905.39473,"tcp_end":[0.49457,0.0566,0.09402],"tcp_start":[0.50361,0.02184,0.25874],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":0.0,"n_steps_budget":660.0,"object_pos_end":[0.53402,0.0501,0.09503],"object_pos_start":[0.53402,0.0501,0.09503],"object_to_goal_dist_end":0.0624,"object_to_goal_dist_start":0.0624,"peak_contact_force":478.83204,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_task","tcp_end":[0.49457,0.0566,0.09402],"tcp_start":[0.49457,0.0566,0.09402],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":24.0,"average_failure_rate":0.14907,"average_mean_iterations":33.34161,"average_solve_count":161.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.05759,"align_hole.lateral_offset_x":0.00592,"align_hole.lateral_offset_y":-0.00151,"approach_hole.speed":0.12574,"approach_peg.speed":0.06062,"descend_insert.force_threshold":20.66371,"descend_insert.insertion_depth":0.09569,"descend_to_peg.contact_force_threshold":7.4645,"descend_to_peg.descend_speed":0.1682,"lift_peg.lift_height":0.02033},"optimized_scores":{"best_composite_score":-0.10364,"best_fitness_score":0.54636,"best_task_score":0.72633},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":659.0,"contact_point_centroid":[0.54568,0.03555,0.07972],"force_p95":338.12825,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1532.42758,"mean_force":291.35949,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.54696,0.0479,0.07836]}],"total_contact_groups":1},"final_pose_error":0.11284,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.55187,0.04226,0.07599],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1532.42758,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.50104,-0.0,0.42071],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34071,"object_to_goal_dist_start":0.26034,"object_z_max":0.42063,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50234,-1e-05,0.38073],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49654,1e-05,0.45239],"object_pos_start":[0.50104,-0.0,0.42071],"object_to_goal_dist_end":0.3724,"object_to_goal_dist_start":0.34071,"object_z_max":0.45233,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5,-1e-05,0.41254],"tcp_start":[0.50234,-1e-05,0.38073],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49523,2e-05,0.44442],"object_pos_start":[0.49654,1e-05,0.45239],"object_to_goal_dist_end":0.36446,"object_to_goal_dist_start":0.3724,"object_z_max":0.4524,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49799,-2e-05,0.40452],"tcp_start":[0.49799,-2e-05,0.40452],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49316,2e-05,0.45776],"object_pos_start":[0.49523,2e-05,0.44442],"object_to_goal_dist_end":0.37783,"object_to_goal_dist_start":0.36445,"object_z_max":0.45774,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49687,-3e-05,0.41794],"tcp_start":[0.49799,-2e-05,0.40452],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49464,0.03598,0.2325],"object_pos_start":[0.49316,2e-05,0.45776],"object_to_goal_dist_end":0.15678,"object_to_goal_dist_start":0.37783,"object_z_max":0.45776,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48408,0.0357,0.19392],"tcp_start":[0.49687,-3e-05,0.41794],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.58772,0.03141,0.09003],"object_pos_start":[0.49464,0.03598,0.2325],"object_to_goal_dist_end":0.09371,"object_to_goal_dist_start":0.15678,"object_z_max":0.2325,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":659.0,"raw_peak_contact_force":1532.42758,"tcp_end":[0.55187,0.04226,0.07599],"tcp_start":[0.48408,0.0357,0.19392],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":720.0,"object_pos_end":[0.58772,0.03141,0.09003],"object_pos_start":[0.58772,0.03141,0.09003],"object_to_goal_dist_end":0.09371,"object_to_goal_dist_start":0.09371,"peak_contact_force":0.0,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_task","tcp_end":[0.55187,0.04226,0.07599],"tcp_start":[0.55187,0.04226,0.07599],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.11429,"average_mean_iterations":26.98286,"average_solve_count":175.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.03856,"align_hole.lateral_offset_x":-0.00146,"align_hole.lateral_offset_y":0.00595,"approach_hole.speed":0.10436,"approach_peg.speed":0.05571,"descend_insert.force_threshold":13.34371,"descend_insert.insertion_depth":0.06489,"descend_to_peg.contact_force_threshold":8.66745,"descend_to_peg.descend_speed":0.14417,"lift_peg.lift_height":0.05848},"optimized_scores":{"best_composite_score":-0.02647,"best_fitness_score":0.62353,"best_task_score":0.89645},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":245.0,"contact_point_centroid":[0.5606,-0.02188,0.07927],"force_p95":1795.61275,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4558.74215,"mean_force":692.88434,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51577,-0.02584,0.08825]},{"body_a":"peg_socket","body_b":"link7","contact_count":853.0,"contact_point_centroid":[0.58933,0.00578,0.07994],"force_p95":848.08515,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4083.7204,"mean_force":489.31833,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51333,-0.03256,0.0895]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.49861,-0.01061,0.07987],"force_p95":1014.89192,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1020.22561,"mean_force":462.23101,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49776,-0.02394,0.0862]},{"body_a":"attachment","body_b":"peg_socket","contact_count":352.0,"contact_point_centroid":[0.51892,-0.04713,0.07995],"force_p95":457.37063,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":531.11552,"mean_force":303.49781,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51452,-0.03547,0.08788]}],"total_contact_groups":4},"final_pose_error":0.08489,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51856,-0.04245,0.09535],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":4558.74215,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.50103,-0.0,0.42112],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34112,"object_to_goal_dist_start":0.26034,"object_z_max":0.42105,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50236,-1e-05,0.38114],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.4965,1e-05,0.4528],"object_pos_start":[0.50103,-0.0,0.42112],"object_to_goal_dist_end":0.37282,"object_to_goal_dist_start":0.34112,"object_z_max":0.45274,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49999,-1e-05,0.41295],"tcp_start":[0.50236,-1e-05,0.38114],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.4952,2e-05,0.44484],"object_pos_start":[0.4965,1e-05,0.4528],"object_to_goal_dist_end":0.36487,"object_to_goal_dist_start":0.37282,"object_z_max":0.45281,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49799,-2e-05,0.40493],"tcp_start":[0.49799,-2e-05,0.40493],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49071,3e-05,0.49355],"object_pos_start":[0.4952,2e-05,0.44484],"object_to_goal_dist_end":0.41366,"object_to_goal_dist_start":0.36487,"object_z_max":0.49348,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49721,-2e-05,0.45408],"tcp_start":[0.49799,-2e-05,0.40493],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52555,-0.01309,0.27666],"object_pos_start":[0.49071,3e-05,0.49355],"object_to_goal_dist_end":0.19874,"object_to_goal_dist_start":0.41366,"object_z_max":0.49358,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.51962,-0.01316,0.2371],"tcp_start":[0.49721,-2e-05,0.45408],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55598,-0.0289,0.09937],"object_pos_start":[0.52555,-0.01309,0.27666],"object_to_goal_dist_end":0.06591,"object_to_goal_dist_start":0.19874,"object_z_max":0.27666,"peak_contact_force":312.44502,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1464.0,"raw_peak_contact_force":4558.74215,"tcp_end":[0.51856,-0.04245,0.09535],"tcp_start":[0.51962,-0.01316,0.2371],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.55598,-0.0289,0.09937],"object_pos_start":[0.55598,-0.0289,0.09937],"object_to_goal_dist_end":0.06591,"object_to_goal_dist_start":0.06591,"peak_contact_force":310.68996,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_task","tcp_end":[0.51856,-0.04245,0.09535],"tcp_start":[0.51856,-0.04245,0.09535],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```