## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0842 | 0.87 | ✅ accepted |
| 2 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0765 | 0.87 | ✅ accepted |
| 1 | approach → grasp → retract → approach → align → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | force_threshold_switch | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.1778 | 0.85 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.2960 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.084) — your mutation base

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

- **Composite score**: 0.084
- **task_score** (E): 0.874
- **fitness_score**: 0.541  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0801 |
| descend_to_peg | 0.00 | 0.00 | 0.0319 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0372 |
| approach_hole | 0.00 | 0.00 | 0.2012 |
| align_hole | 0.67 | 1.00 | 0.1393 |
| descend_insert | 1.00 | 1.00 | 0.0006 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.381) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.421) | 0.260→0.341 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.502, -0.000, 0.381)→(0.500, -0.000, 0.412) | (0.501, -0.000, 0.421)→(0.497, 0.000, 0.452) | 0.341→0.372 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.498, -0.000, 0.404)→(0.498, -0.000, 0.404) | (0.497, 0.000, 0.452)→(0.495, 0.000, 0.444) | 0.372→0.364 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.404)→(0.497, -0.000, 0.442) | (0.495, 0.000, 0.444)→(0.492, 0.000, 0.481) | 0.364→0.401 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.497, -0.000, 0.442)→(0.502, 0.010, 0.242) | (0.492, 0.000, 0.481)→(0.509, 0.011, 0.281) | 0.401→0.202 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.67 / step_budget | (0.502, 0.010, 0.242)→(0.507, 0.030, 0.111) | (0.509, 0.011, 0.281)→(0.543, 0.027, 0.103) | 0.202→0.072 | 1.00 / 2.000 | 699.711 | 1422.425 |
| descend_insert | descend | 1.00 / force_exceeded | (0.507, 0.030, 0.111)→(0.507, 0.031, 0.111) | (0.543, 0.027, 0.103)→(0.543, 0.027, 0.103) | 0.072→0.072 | 1.00 / 2.000 | 667.765 | 667.765 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.898
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.898
- phase_score: 0.375
- phase_breakdown.approach_hole_score: 0.134
- phase_breakdown.approach_peg_score: 0.820
- phase_breakdown.insert_task_score: 0.342

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.584
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.898
- **Median Q (composite search score)**: 0.073
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.238


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.01685,"average_mean_iterations":7.23596,"average_solve_count":178.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":0.00463,"align_hole.lateral_offset_y":-0.00622,"approach_hole.speed":0.04981,"approach_peg.speed":0.06425,"descend_insert.force_threshold":24.29351,"descend_insert.insertion_depth":0.11524,"descend_to_peg.contact_force_threshold":7.51559,"descend_to_peg.descend_speed":0.13697,"lift_peg.lift_height":0.04671},"optimized_scores":{"best_composite_score":0.05294,"best_fitness_score":0.51009,"best_task_score":0.87952},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":698.0,"contact_point_centroid":[0.56961,0.01119,0.07818],"force_p95":893.10611,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1415.68469,"mean_force":361.25689,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49222,0.03894,0.10006]},{"body_a":"attachment","body_b":"peg_socket","contact_count":137.0,"contact_point_centroid":[0.56892,0.03805,0.07991],"force_p95":1116.84624,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1279.54275,"mean_force":605.34866,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49885,0.05204,0.10124]},{"body_a":"attachment","body_b":"peg_socket","contact_count":21.0,"contact_point_centroid":[0.4775,0.01124,0.07918],"force_p95":983.44228,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":988.14666,"mean_force":284.70207,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.47556,0.02555,0.07795]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56989,0.00554,0.07998],"force_p95":140.35455,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.35455,"mean_force":140.35455,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51962,0.08283,0.1238]}],"total_contact_groups":4},"final_pose_error":0.16845,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.52078,0.08378,0.12462],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1415.68469,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":812.0,"n_steps_budget":870.0,"object_pos_end":[0.50105,-0.0,0.42078],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34078,"object_to_goal_dist_start":0.26034,"object_z_max":0.42069,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50235,-1e-05,0.3808],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49654,1e-05,0.45246],"object_pos_start":[0.50105,-0.0,0.42078],"object_to_goal_dist_end":0.37248,"object_to_goal_dist_start":0.34078,"object_z_max":0.45241,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5,-1e-05,0.41261],"tcp_start":[0.50235,-1e-05,0.3808],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49523,2e-05,0.4445],"object_pos_start":[0.49654,1e-05,0.45246],"object_to_goal_dist_end":0.36453,"object_to_goal_dist_start":0.37248,"object_z_max":0.45247,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.498,-2e-05,0.40459],"tcp_start":[0.498,-2e-05,0.40459],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.4915,2e-05,0.48227],"object_pos_start":[0.49523,2e-05,0.4445],"object_to_goal_dist_end":0.40236,"object_to_goal_dist_start":0.36453,"object_z_max":0.4822,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49711,-3e-05,0.44266],"tcp_start":[0.498,-2e-05,0.40459],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50907,0.0192,0.2878],"object_pos_start":[0.4915,2e-05,0.48227],"object_to_goal_dist_end":0.20888,"object_to_goal_dist_start":0.40236,"object_z_max":0.48228,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.50239,0.01911,0.24836],"tcp_start":[0.49711,-3e-05,0.44266],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":811.0,"n_steps_budget":930.0,"object_pos_end":[0.55305,0.06477,0.1113],"object_pos_start":[0.50907,0.0192,0.2878],"object_to_goal_dist_end":0.08938,"object_to_goal_dist_start":0.20888,"object_z_max":0.2878,"peak_contact_force":370.30714,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":856.0,"raw_peak_contact_force":1415.68469,"tcp_end":[0.51962,0.08283,0.1238],"tcp_start":[0.50239,0.01911,0.24836],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55387,0.06531,0.11179],"object_pos_start":[0.55305,0.06477,0.1113],"object_to_goal_dist_end":0.09043,"object_to_goal_dist_start":0.08938,"object_z_max":0.1113,"peak_contact_force":140.35455,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":140.35455,"subtask_id":"insert_task","tcp_end":[0.52078,0.08378,0.12462],"tcp_start":[0.51962,0.08283,0.1238],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89888,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.00501,"align_hole.lateral_offset_y":-0.00099,"approach_hole.speed":0.04157,"approach_peg.speed":0.06698,"descend_insert.force_threshold":13.5428,"descend_insert.insertion_depth":0.12913,"descend_to_peg.contact_force_threshold":5.77572,"descend_to_peg.descend_speed":0.09904,"lift_peg.lift_height":0.04888},"optimized_scores":{"best_composite_score":0.07269,"best_fitness_score":0.52983,"best_task_score":0.84462},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":291.0,"contact_point_centroid":[0.54564,0.04025,0.07993],"force_p95":579.78835,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1149.06856,"mean_force":319.05942,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.47266,0.04636,0.10645]},{"body_a":"peg_socket","body_b":"link7","contact_count":812.0,"contact_point_centroid":[0.54586,0.02739,0.06891],"force_p95":522.98904,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1009.15508,"mean_force":337.00278,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.4702,0.04018,0.10514]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54596,0.03063,0.06647],"force_p95":414.27079,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":414.27079,"mean_force":414.27079,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.47789,0.05462,0.11326]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.45474,0.02257,0.0796],"force_p95":214.63901,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.68698,"mean_force":109.10929,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.45336,0.03142,0.07971]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54612,0.04413,0.07985],"force_p95":126.87174,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.87174,"mean_force":126.87174,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.47789,0.05462,0.11326]}],"total_contact_groups":5},"final_pose_error":0.16336,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.47788,0.05465,0.11326],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1149.06856,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.50106,-0.0,0.4205],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.3405,"object_to_goal_dist_start":0.26034,"object_z_max":0.42042,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50234,-1e-05,0.38052],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49656,1e-05,0.45218],"object_pos_start":[0.50106,-0.0,0.4205],"object_to_goal_dist_end":0.3722,"object_to_goal_dist_start":0.3405,"object_z_max":0.45213,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50001,-1e-05,0.41233],"tcp_start":[0.50234,-1e-05,0.38052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49525,2e-05,0.44422],"object_pos_start":[0.49656,1e-05,0.45218],"object_to_goal_dist_end":0.36425,"object_to_goal_dist_start":0.3722,"object_z_max":0.4522,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.498,-2e-05,0.40431],"tcp_start":[0.498,-2e-05,0.40431],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49138,2e-05,0.48397],"object_pos_start":[0.49525,2e-05,0.44422],"object_to_goal_dist_end":0.40406,"object_to_goal_dist_start":0.36425,"object_z_max":0.4839,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49712,-3e-05,0.44438],"tcp_start":[0.498,-2e-05,0.40431],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49569,0.0238,0.287],"object_pos_start":[0.49138,2e-05,0.48397],"object_to_goal_dist_end":0.20841,"object_to_goal_dist_start":0.40406,"object_z_max":0.48399,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48788,0.02363,0.24777],"tcp_start":[0.49712,-3e-05,0.44438],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":901.0,"n_steps_budget":930.0,"object_pos_end":[0.51618,0.04904,0.10313],"object_pos_start":[0.49569,0.0238,0.287],"object_to_goal_dist_end":0.05658,"object_to_goal_dist_start":0.20841,"object_z_max":0.287,"peak_contact_force":516.0356,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1119.0,"raw_peak_contact_force":1149.06856,"tcp_end":[0.47789,0.05462,0.11326],"tcp_start":[0.48788,0.02363,0.24777],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51617,0.04905,0.10313],"object_pos_start":[0.51618,0.04904,0.10313],"object_to_goal_dist_end":0.05659,"object_to_goal_dist_start":0.05658,"object_z_max":0.10313,"peak_contact_force":414.27079,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":414.27079,"subtask_id":"insert_task","tcp_end":[0.47788,0.05465,0.11326],"tcp_start":[0.47789,0.05462,0.11326],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.05333,"average_mean_iterations":14.66667,"average_solve_count":150.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.00077,"align_hole.lateral_offset_y":0.00999,"approach_hole.speed":0.08104,"approach_peg.speed":0.06931,"descend_insert.force_threshold":21.72656,"descend_insert.insertion_depth":0.11045,"descend_to_peg.contact_force_threshold":12.23501,"descend_to_peg.descend_speed":0.12757,"lift_peg.lift_height":0.04153},"optimized_scores":{"best_composite_score":0.12702,"best_fitness_score":0.58417,"best_task_score":0.89808},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":403.0,"contact_point_centroid":[0.58912,0.0039,0.07992],"force_p95":1076.41598,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1702.521,"mean_force":470.12717,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51214,-0.03114,0.09338]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58955,0.00552,0.07999],"force_p95":1448.67083,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1448.67083,"mean_force":1448.67083,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.52272,-0.0462,0.09473]},{"body_a":"attachment","body_b":"peg_socket","contact_count":172.0,"contact_point_centroid":[0.56157,-0.02554,0.07915],"force_p95":1183.52009,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1448.53964,"mean_force":438.65622,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.52498,-0.03325,0.09037]},{"body_a":"attachment","body_b":"peg_socket","contact_count":73.0,"contact_point_centroid":[0.51987,-0.04711,0.07989],"force_p95":742.66471,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1189.15047,"mean_force":438.68364,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51759,-0.0404,0.09276]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52302,-0.04706,0.07988],"force_p95":939.68142,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":939.68142,"mean_force":939.68142,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.52272,-0.0462,0.09473]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.58962,-0.02245,0.07984],"force_p95":80.51549,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.51549,"mean_force":80.51549,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.52272,-0.0462,0.09473]}],"total_contact_groups":6},"final_pose_error":0.12873,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52274,-0.04638,0.0947],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1702.521,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.50106,-0.0,0.42047],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34048,"object_to_goal_dist_start":0.26034,"object_z_max":0.42038,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50234,-1e-05,0.3805],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49656,1e-05,0.45216],"object_pos_start":[0.50106,-0.0,0.42047],"object_to_goal_dist_end":0.37217,"object_to_goal_dist_start":0.34048,"object_z_max":0.4521,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50001,-1e-05,0.41231],"tcp_start":[0.50234,-1e-05,0.3805],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49525,1e-05,0.44419],"object_pos_start":[0.49656,1e-05,0.45216],"object_to_goal_dist_end":0.36422,"object_to_goal_dist_start":0.37217,"object_z_max":0.45217,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.498,-2e-05,0.40429],"tcp_start":[0.498,-2e-05,0.40429],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49185,2e-05,0.47725],"object_pos_start":[0.49525,1e-05,0.44419],"object_to_goal_dist_end":0.39733,"object_to_goal_dist_start":0.36422,"object_z_max":0.47719,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49706,-3e-05,0.43759],"tcp_start":[0.498,-2e-05,0.40429],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52254,-0.01124,0.26809],"object_pos_start":[0.49185,2e-05,0.47725],"object_to_goal_dist_end":0.18977,"object_to_goal_dist_start":0.39733,"object_z_max":0.47726,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.51592,-0.01129,0.22864],"tcp_start":[0.49706,-3e-05,0.43759],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":541.0,"n_steps_budget":810.0,"object_pos_end":[0.56043,-0.03285,0.0947],"object_pos_start":[0.52254,-0.01124,0.26809],"object_to_goal_dist_end":0.07033,"object_to_goal_dist_start":0.18977,"object_z_max":0.26809,"peak_contact_force":1212.79029,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":648.0,"raw_peak_contact_force":1702.521,"tcp_end":[0.52272,-0.0462,0.09473],"tcp_start":[0.51592,-0.01129,0.22864],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":810.0,"object_pos_end":[0.56045,-0.03304,0.09465],"object_pos_start":[0.56043,-0.03285,0.0947],"object_to_goal_dist_end":0.07043,"object_to_goal_dist_start":0.07033,"object_z_max":0.0947,"peak_contact_force":1448.67083,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":1448.67083,"subtask_id":"insert_task","tcp_end":[0.52274,-0.04638,0.0947],"tcp_start":[0.52272,-0.0462,0.09473],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```