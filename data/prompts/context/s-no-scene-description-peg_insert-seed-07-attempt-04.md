## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0088 | 0.76 | ❌ rejected |
| 3 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0842 | 0.87 | ✅ accepted |
| 2 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0765 | 0.87 | ✅ accepted |
| 1 | approach → grasp → retract → approach → align → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | force_threshold_switch | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.1778 | 0.85 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.2960 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.009) — your mutation base

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

- **Composite score**: -0.009
- **task_score** (E): 0.761
- **fitness_score**: 0.498  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0803 |
| descend_to_peg | 0.00 | 0.00 | 0.0319 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0399 |
| approach_hole | 1.00 | 0.00 | 0.2877 |
| align_hole | 0.00 | 0.33 | 0.1549 |
| descend_insert | 1.00 | 1.00 | 0.0090 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.381) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.421) | 0.260→0.341 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.502, -0.000, 0.381)→(0.500, -0.000, 0.413) | (0.501, -0.000, 0.421)→(0.497, 0.000, 0.452) | 0.341→0.372 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.498, -0.000, 0.405)→(0.498, -0.000, 0.405) | (0.497, 0.000, 0.452)→(0.495, 0.000, 0.445) | 0.372→0.365 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.405)→(0.497, -0.000, 0.444) | (0.495, 0.000, 0.445)→(0.491, 0.000, 0.484) | 0.365→0.404 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 1.00 / step_budget | (0.497, -0.000, 0.444)→(0.505, 0.017, 0.159) | (0.491, 0.000, 0.484)→(0.515, 0.017, 0.198) | 0.404→0.123 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.00 / step_budget | (0.505, 0.017, 0.159)→(0.587, 0.021, 0.191) | (0.515, 0.017, 0.198)→(0.597, 0.002, 0.165) | 0.123→0.176 | 0.33 / 1.000 | 169.177 | 7618.379 |
| descend_insert | descend | 1.00 / force_exceeded | (0.587, 0.021, 0.191)→(0.587, 0.015, 0.193) | (0.597, 0.002, 0.165)→(0.597, -0.004, 0.167) | 0.176→0.174 | 1.00 / 1.000 | 260.434 | 134.010 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.958
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.958
- phase_score: 0.326
- phase_breakdown.approach_hole_score: 0.538
- phase_breakdown.approach_peg_score: 0.823
- phase_breakdown.insert_task_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.579
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.958
- **Median Q (composite search score)**: -0.046
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98052,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.04504,"align_hole.lateral_offset_x":0.00216,"align_hole.lateral_offset_y":-0.00559,"approach_hole.speed":0.11443,"approach_peg.speed":0.05756,"descend_insert.force_threshold":22.82904,"descend_insert.insertion_depth":0.05683,"descend_to_peg.contact_force_threshold":7.68125,"descend_to_peg.descend_speed":0.16115,"lift_peg.lift_height":0.064},"optimized_scores":{"best_composite_score":-0.05236,"best_fitness_score":0.45478,"best_task_score":0.63805},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":231.0,"contact_point_centroid":[0.58666,0.033,-0.00057],"force_p95":577.81806,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8562.0465,"mean_force":556.11121,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.5786,0.0346,0.01134]},{"body_a":"attachment","body_b":"peg_socket","contact_count":211.0,"contact_point_centroid":[0.56987,0.03182,0.02356],"force_p95":971.37851,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8063.42259,"mean_force":667.61992,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.57842,0.03551,0.01212]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.56865,-0.02671,0.07328],"force_p95":3256.34919,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3956.96747,"mean_force":1244.79271,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.61306,0.08827,0.04289]},{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.64853,-0.01244,-0.00061],"force_p95":2324.53262,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2335.89106,"mean_force":819.55409,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.60132,0.08244,0.03261]},{"body_a":"world","body_b":"link6","contact_count":183.0,"contact_point_centroid":[0.6289,-0.10311,-0.0004],"force_p95":461.14133,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2033.99582,"mean_force":323.3166,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.66382,0.05742,0.17865]}],"total_contact_groups":5},"final_pose_error":0.25255,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.61089,0.00098,0.25263],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":8562.0465,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.50104,-0.0,0.42099],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34099,"object_to_goal_dist_start":0.26034,"object_z_max":0.42092,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50236,-1e-05,0.38101],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49651,1e-05,0.45267],"object_pos_start":[0.50104,-0.0,0.42099],"object_to_goal_dist_end":0.37269,"object_to_goal_dist_start":0.34099,"object_z_max":0.45262,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49999,-1e-05,0.41282],"tcp_start":[0.50236,-1e-05,0.38101],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49521,2e-05,0.44471],"object_pos_start":[0.49651,1e-05,0.45267],"object_to_goal_dist_end":0.36474,"object_to_goal_dist_start":0.37269,"object_z_max":0.45268,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49799,-2e-05,0.4048],"tcp_start":[0.49799,-2e-05,0.4048],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49036,3e-05,0.4985],"object_pos_start":[0.49521,2e-05,0.44471],"object_to_goal_dist_end":0.41861,"object_to_goal_dist_start":0.36474,"object_z_max":0.49842,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49726,-2e-05,0.4591],"tcp_start":[0.49799,-2e-05,0.4048],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":920.0,"n_steps_budget":1000.0,"object_pos_end":[0.51647,0.03023,0.19752],"object_pos_start":[0.49036,3e-05,0.4985],"object_to_goal_dist_end":0.12246,"object_to_goal_dist_start":0.41861,"object_z_max":0.49854,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.50627,0.03013,0.15884],"tcp_start":[0.49726,-2e-05,0.4591],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.62054,-0.01149,0.21351],"object_pos_start":[0.51647,0.03023,0.19752],"object_to_goal_dist_end":0.18024,"object_to_goal_dist_start":0.12246,"object_z_max":0.21301,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":659.0,"raw_peak_contact_force":8562.0465,"tcp_end":[0.6201,0.00505,0.24992],"tcp_start":[0.50627,0.03013,0.15884],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.61283,-0.01424,0.21569],"object_pos_start":[0.62054,-0.01149,0.21351],"object_to_goal_dist_end":0.17705,"object_to_goal_dist_start":0.18024,"object_z_max":0.21675,"peak_contact_force":381.0492,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_task","tcp_end":[0.61089,0.00098,0.25263],"tcp_start":[0.6201,0.00505,0.24992],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08721,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.04103,"align_hole.lateral_offset_x":-0.00996,"align_hole.lateral_offset_y":-0.00191,"approach_hole.speed":0.07799,"approach_peg.speed":0.06198,"descend_insert.force_threshold":19.98796,"descend_insert.insertion_depth":0.02895,"descend_to_peg.contact_force_threshold":6.8812,"descend_to_peg.descend_speed":0.10595,"lift_peg.lift_height":0.02483},"optimized_scores":{"best_composite_score":-0.04592,"best_fitness_score":0.46122,"best_task_score":0.68833},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.63047,0.04583,-0.00012],"force_p95":3779.05861,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4345.41141,"mean_force":727.00233,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.55637,0.11618,0.02142]},{"body_a":"peg_socket","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54493,0.02209,0.05022],"force_p95":3434.34966,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3562.81289,"mean_force":1286.4362,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.56038,0.14948,0.04841]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.54436,0.04123,0.06903],"force_p95":1268.43423,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1539.39217,"mean_force":641.55286,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.55394,0.0431,0.05983]},{"body_a":"attachment","body_b":"world","contact_count":446.0,"contact_point_centroid":[0.56069,0.06864,-0.00036],"force_p95":587.17368,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1331.18736,"mean_force":296.67735,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.55406,0.07035,0.01255]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.67976,-0.01494,-0.00083],"force_p95":1277.45069,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1304.1023,"mean_force":844.82935,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.56261,0.15068,0.05057]},{"body_a":"peg_socket","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54459,0.02191,0.04638],"force_p95":1208.70248,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1264.2873,"mean_force":628.26311,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.56038,0.14948,0.04841]},{"body_a":"attachment","body_b":"peg_socket","contact_count":484.0,"contact_point_centroid":[0.54596,0.06514,0.0246],"force_p95":693.1725,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":769.90309,"mean_force":387.06332,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.5536,0.07054,0.01347]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.68627,-0.03592,-0.0001],"force_p95":384.45982,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.02864,"mean_force":226.34049,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.57976,0.14825,0.06225]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54612,0.0279,0.04999],"force_p95":0.0,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.57397,0.15394,0.05964]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54608,0.02728,0.05038],"force_p95":0.0,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.57397,0.15394,0.05964]}],"total_contact_groups":10},"final_pose_error":0.14396,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.58514,0.14264,0.06459],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":4345.41141,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.50104,-0.0,0.42071],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34071,"object_to_goal_dist_start":0.26034,"object_z_max":0.42063,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50234,-1e-05,0.38073],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49654,1e-05,0.45239],"object_pos_start":[0.50104,-0.0,0.42071],"object_to_goal_dist_end":0.3724,"object_to_goal_dist_start":0.34071,"object_z_max":0.45233,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5,-1e-05,0.41254],"tcp_start":[0.50234,-1e-05,0.38073],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49523,2e-05,0.44442],"object_pos_start":[0.49654,1e-05,0.45239],"object_to_goal_dist_end":0.36446,"object_to_goal_dist_start":0.3724,"object_z_max":0.4524,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49799,-2e-05,0.40452],"tcp_start":[0.49799,-2e-05,0.40452],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.49288,2e-05,0.46198],"object_pos_start":[0.49523,2e-05,0.44442],"object_to_goal_dist_end":0.38205,"object_to_goal_dist_start":0.36445,"object_z_max":0.46195,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49691,-3e-05,0.42219],"tcp_start":[0.49799,-2e-05,0.40452],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.49551,0.03702,0.19734],"object_pos_start":[0.49288,2e-05,0.46198],"object_to_goal_dist_end":0.12312,"object_to_goal_dist_start":0.38205,"object_z_max":0.46198,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48356,0.03674,0.15917],"tcp_start":[0.49691,-3e-05,0.42219],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.59455,0.1198,0.05642],"object_pos_start":[0.49551,0.03702,0.19734],"object_to_goal_dist_end":0.15442,"object_to_goal_dist_start":0.12312,"object_z_max":0.19734,"peak_contact_force":507.53127,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1007.0,"raw_peak_contact_force":4345.41141,"tcp_end":[0.57397,0.15394,0.05964],"tcp_start":[0.48356,0.03674,0.15917],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":42.0,"n_steps_budget":900.0,"object_pos_end":[0.6033,0.10724,0.06049],"object_pos_start":[0.59455,0.1198,0.05642],"object_to_goal_dist_end":0.15018,"object_to_goal_dist_start":0.15442,"object_z_max":0.06738,"peak_contact_force":50.65233,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":402.02864,"subtask_id":"insert_task","tcp_end":[0.58514,0.14264,0.06459],"tcp_start":[0.57397,0.15394,0.05964],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6213,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.04283,"align_hole.lateral_offset_x":0.00242,"align_hole.lateral_offset_y":0.00067,"approach_hole.speed":0.08491,"approach_peg.speed":0.05997,"descend_insert.force_threshold":27.10548,"descend_insert.insertion_depth":0.11301,"descend_to_peg.contact_force_threshold":11.83625,"descend_to_peg.descend_speed":0.13116,"lift_peg.lift_height":0.05709},"optimized_scores":{"best_composite_score":0.07189,"best_fitness_score":0.57903,"best_task_score":0.95806},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":25.0,"contact_point_centroid":[0.52591,-0.00787,0.04588],"force_p95":9816.5845,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9947.6798,"mean_force":3008.97998,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51684,-0.00168,0.05192]},{"body_a":"attachment","body_b":"peg_socket","contact_count":189.0,"contact_point_centroid":[0.51923,0.01302,0.07599],"force_p95":750.66989,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9595.01413,"mean_force":691.54585,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51196,0.00108,0.07288]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.55994,-0.02063,0.07977],"force_p95":2600.63148,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2734.28712,"mean_force":1486.99168,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51883,-0.00018,0.0467]},{"body_a":"peg_socket","body_b":"link7","contact_count":227.0,"contact_point_centroid":[0.58902,-0.06204,0.07987],"force_p95":697.11284,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1182.60525,"mean_force":473.80671,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51739,0.00838,0.08233]},{"body_a":"peg_socket","body_b":"link6","contact_count":65.0,"contact_point_centroid":[0.5895,-0.07699,0.07987],"force_p95":492.00639,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":704.58831,"mean_force":295.0841,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.62165,0.03107,0.20063]},{"body_a":"attachment","body_b":"peg_socket","contact_count":25.0,"contact_point_centroid":[0.49933,-0.00692,0.07379],"force_p95":591.4463,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":600.1312,"mean_force":368.98109,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51027,7e-05,0.06785]},{"body_a":"world","body_b":"link6","contact_count":153.0,"contact_point_centroid":[0.60403,-0.13647,-0.00011],"force_p95":432.76819,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":472.35311,"mean_force":367.88957,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.58055,-0.08286,0.26012]}],"total_contact_groups":7},"final_pose_error":0.30881,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.56566,-0.0972,0.26303],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":9947.6798,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.50104,-0.0,0.42071],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34071,"object_to_goal_dist_start":0.26034,"object_z_max":0.42063,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50234,-1e-05,0.38073],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49654,1e-05,0.45239],"object_pos_start":[0.50104,-0.0,0.42071],"object_to_goal_dist_end":0.3724,"object_to_goal_dist_start":0.34071,"object_z_max":0.45233,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5,-1e-05,0.41254],"tcp_start":[0.50234,-1e-05,0.38073],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49523,2e-05,0.44442],"object_pos_start":[0.49654,1e-05,0.45239],"object_to_goal_dist_end":0.36446,"object_to_goal_dist_start":0.3724,"object_z_max":0.4524,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49799,-2e-05,0.40452],"tcp_start":[0.49799,-2e-05,0.40452],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49084,3e-05,0.49168],"object_pos_start":[0.49523,2e-05,0.44442],"object_to_goal_dist_end":0.41178,"object_to_goal_dist_start":0.36445,"object_z_max":0.4916,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49719,-2e-05,0.45218],"tcp_start":[0.49799,-2e-05,0.40452],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":931.0,"n_steps_budget":1000.0,"object_pos_end":[0.53363,-0.01616,0.19773],"object_pos_start":[0.49084,3e-05,0.49168],"object_to_goal_dist_end":0.1235,"object_to_goal_dist_start":0.41178,"object_z_max":0.4917,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.52487,-0.01624,0.1587],"tcp_start":[0.49719,-2e-05,0.45218],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":605.0,"n_steps_budget":720.0,"object_pos_end":[0.57529,-0.10367,0.22477],"object_pos_start":[0.53363,-0.01616,0.19773],"object_to_goal_dist_end":0.19333,"object_to_goal_dist_start":0.1235,"object_z_max":0.2248,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":691.0,"raw_peak_contact_force":9947.6798,"tcp_end":[0.56564,-0.09727,0.26306],"tcp_start":[0.52487,-0.01624,0.1587],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.57531,-0.1036,0.22475],"object_pos_start":[0.57529,-0.10367,0.22477],"object_to_goal_dist_end":0.19328,"object_to_goal_dist_start":0.19333,"object_z_max":0.22477,"peak_contact_force":349.60179,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_task","tcp_end":[0.56566,-0.0972,0.26303],"tcp_start":[0.56564,-0.09727,0.26306],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```