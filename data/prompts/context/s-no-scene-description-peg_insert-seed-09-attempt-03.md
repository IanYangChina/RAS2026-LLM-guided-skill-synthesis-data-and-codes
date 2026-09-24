## Search State

- **Seed**: 9
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3393 | 0.74 | ❌ rejected |
| 2 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5025 | 0.91 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | 0.4018 | 0.77 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | 0.4018 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.339) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_hole
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: insert_peg
  weight: 0.7
phases:
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_hole
- id: align_hole
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_hole
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
      distance: 0.08
      axis: world_z
      mode: replace_offset_projection
      sign: negative
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
    insert_depth:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insert_peg
- id: release_peg
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_hole** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_hole** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_insert** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.08, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **release_peg** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.339
- **task_score** (E): 0.745
- **fitness_score**: 0.399  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 1.00 | 0.00 | 0.0598 |
| align_hole | 0.00 | 1.00 | 0.1660 |
| descend_insert | 1.00 | 1.00 | 0.0001 |
| release_peg | 1.00 | 1.00 | 0.0022 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, -0.010, 0.246) | (0.504, -0.000, 0.340)→(0.512, -0.010, 0.286) | 0.260→0.208 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.00 / step_budget | (0.507, -0.010, 0.246)→(0.545, -0.016, 0.090) | (0.512, -0.010, 0.286)→(0.579, -0.012, 0.104) | 0.208→0.091 | 1.00 / 1.000 | 274.412 | 4140.998 |
| descend_insert | descend | 1.00 / force_exceeded | (0.545, -0.016, 0.090)→(0.545, -0.016, 0.090) | (0.579, -0.012, 0.104)→(0.580, -0.012, 0.104) | 0.091→0.091 | 1.00 / 1.000 | 296.973 | 296.973 |
| release_peg | release | 1.00 / step_budget | (0.545, -0.016, 0.090)→(0.547, -0.016, 0.091) | (0.580, -0.012, 0.104)→(0.581, -0.012, 0.105) | 0.091→0.093 | 1.00 / 1.333 | 63.484 | 253.616 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.995
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.995
- phase_score: 0.269
- phase_breakdown.reach_above_hole_score: 0.072
- phase_breakdown.insert_peg_score: 0.353

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.560
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.995
- **Median Q (composite search score)**: 0.279
- **K-run variance**: 0.0131
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.3
- **Final σ (mean)**: 0.331


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ad55441961509110caa3e00662ff00c043a366a9841ef346adcb2ae98eb0fa2d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `848090e975b2909410760ed4539d133eb61635ea5a8640e3622d2871416125a9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.05882,"average_solve_count":51.0,"average_success_count":51.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.08486,"approach_hole.approach_speed":0.05553,"descend_insert.force_threshold":38.21749,"descend_insert.insert_depth":0.05463,"descend_insert.insert_speed":0.01591},"optimized_scores":{"best_composite_score":0.27936,"best_fitness_score":0.33936,"best_task_score":0.64731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":42.0,"contact_point_centroid":[0.58575,-0.00706,0.07603],"force_p95":1253.52412,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1465.41587,"mean_force":425.8437,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.57906,-0.02066,0.07756]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.58822,-0.00713,0.07896],"force_p95":299.33191,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.33191,"mean_force":299.33191,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.5839,-0.02051,0.08402]},{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.58949,-0.00716,0.07991],"force_p95":108.3284,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.67339,"mean_force":76.95067,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.58629,-0.02049,0.08595]}],"total_contact_groups":3},"final_pose_error":0.08016,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.584,-0.02043,0.08416],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1465.41587,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":130.0,"n_steps_budget":900.0,"object_pos_end":[0.5235,-0.01197,0.28581],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20749,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.51895,-0.01196,0.24607],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":600.0,"object_pos_end":[0.61679,-0.01744,0.10657],"object_pos_start":[0.5235,-0.01197,0.28581],"object_to_goal_dist_end":0.12104,"object_to_goal_dist_start":0.20749,"object_z_max":0.28581,"peak_contact_force":259.47215,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":42.0,"raw_peak_contact_force":1465.41587,"subtask_id":"reach_above_hole","tcp_end":[0.5839,-0.02051,0.08402],"tcp_start":[0.51895,-0.01196,0.24607],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.61696,-0.01745,0.10663],"object_pos_start":[0.61679,-0.01744,0.10657],"object_to_goal_dist_end":0.12121,"object_to_goal_dist_start":0.12104,"object_z_max":0.10657,"peak_contact_force":299.33191,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":299.33191,"subtask_id":"insert_peg","tcp_end":[0.584,-0.02043,0.08416],"tcp_start":[0.5839,-0.02051,0.08402],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61944,-0.01766,0.10865],"object_pos_start":[0.61696,-0.01745,0.10663],"object_to_goal_dist_end":0.12409,"object_to_goal_dist_start":0.12121,"object_z_max":0.10891,"peak_contact_force":64.49932,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":233.67339,"tcp_end":[0.58664,-0.02053,0.08594],"tcp_start":[0.584,-0.02043,0.08416],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.2439,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.13611,"approach_hole.approach_speed":0.09668,"descend_insert.force_threshold":33.24608,"descend_insert.insert_depth":0.13195,"descend_insert.insert_speed":0.03487},"optimized_scores":{"best_composite_score":0.23892,"best_fitness_score":0.29892,"best_task_score":0.59201},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":42.0,"contact_point_centroid":[0.59259,-0.00998,0.07611],"force_p95":1278.51843,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1487.94105,"mean_force":457.41762,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.59114,-0.02453,0.07442]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.59517,-0.0113,0.07896],"force_p95":295.12438,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.12438,"mean_force":295.12438,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.59609,-0.02603,0.07969]},{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.59639,-0.01091,0.07993],"force_p95":110.44983,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.78986,"mean_force":74.98767,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.59845,-0.02565,0.08156]}],"total_contact_groups":3},"final_pose_error":0.14468,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.59622,-0.026,0.07981],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1487.94105,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":135.0,"n_steps_budget":600.0,"object_pos_end":[0.52923,-0.01692,0.28422],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20699,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.5247,-0.01691,0.24448],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":600.0,"object_pos_end":[0.62687,-0.01842,0.10408],"object_pos_start":[0.52923,-0.01692,0.28422],"object_to_goal_dist_end":0.13044,"object_to_goal_dist_start":0.20699,"object_z_max":0.28422,"peak_contact_force":291.36643,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":42.0,"raw_peak_contact_force":1487.94105,"subtask_id":"reach_above_hole","tcp_end":[0.59609,-0.02603,0.07969],"tcp_start":[0.5247,-0.01691,0.24448],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.62704,-0.0185,0.10417],"object_pos_start":[0.62687,-0.01842,0.10408],"object_to_goal_dist_end":0.13063,"object_to_goal_dist_start":0.13044,"object_z_max":0.10408,"peak_contact_force":295.12438,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":295.12438,"subtask_id":"insert_peg","tcp_end":[0.59622,-0.026,0.07981],"tcp_start":[0.59609,-0.02603,0.07969],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62938,-0.01832,0.10618],"object_pos_start":[0.62704,-0.0185,0.10417],"object_to_goal_dist_end":0.13327,"object_to_goal_dist_start":0.13063,"object_z_max":0.10643,"peak_contact_force":63.64954,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":233.78986,"tcp_end":[0.59875,-0.02569,0.08154],"tcp_start":[0.59622,-0.026,0.07981],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.85366,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.10989,"approach_hole.approach_speed":0.15725,"descend_insert.force_threshold":34.05202,"descend_insert.insert_depth":0.12823,"descend_insert.insert_speed":0.01454},"optimized_scores":{"best_composite_score":0.49953,"best_fitness_score":0.55953,"best_task_score":0.99531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":73.0,"contact_point_centroid":[0.52815,-0.00306,0.06566],"force_p95":8033.52114,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9469.6376,"mean_force":1293.07225,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.44874,-0.00103,0.10215]},{"body_a":"attachment","body_b":"peg_socket","contact_count":45.0,"contact_point_centroid":[0.50859,-0.00034,0.07653],"force_p95":6695.9045,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7125.60312,"mean_force":1697.08669,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48309,-0.00047,0.08714]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53028,-0.00343,0.0499],"force_p95":2834.25597,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2837.57568,"mean_force":2765.36655,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.44049,-0.00095,0.09849]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53023,-0.00468,0.06478],"force_p95":296.46373,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.46373,"mean_force":296.46373,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45515,-0.00099,0.10633]},{"body_a":"peg_socket","body_b":"link7","contact_count":187.0,"contact_point_centroid":[0.53028,-0.00467,0.06436],"force_p95":72.98675,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.38331,"mean_force":27.18183,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45528,-0.00099,0.10599]},{"body_a":"attachment","body_b":"peg_socket","contact_count":190.0,"contact_point_centroid":[0.53028,-0.00049,0.07997],"force_p95":87.11599,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.31815,"mean_force":65.63401,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45529,-0.00099,0.10598]}],"total_contact_groups":6},"final_pose_error":0.15531,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.45517,-0.00098,0.10634],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":9469.6376,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":112.0,"n_steps_budget":600.0,"object_pos_end":[0.4825,-5e-05,0.28764],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20837,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47801,-6e-05,0.24789],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":194.0,"n_steps_budget":600.0,"object_pos_end":[0.49474,-0.00076,0.10064],"object_pos_start":[0.4825,-5e-05,0.28764],"object_to_goal_dist_end":0.02131,"object_to_goal_dist_start":0.20837,"object_z_max":0.28764,"peak_contact_force":272.39657,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":123.0,"raw_peak_contact_force":9469.6376,"subtask_id":"reach_above_hole","tcp_end":[0.45515,-0.00099,0.10633],"tcp_start":[0.47801,-6e-05,0.24789],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49476,-0.00076,0.10063],"object_pos_start":[0.49474,-0.00076,0.10064],"object_to_goal_dist_end":0.0213,"object_to_goal_dist_start":0.02131,"object_z_max":0.10064,"peak_contact_force":296.46373,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":296.46373,"subtask_id":"insert_peg","tcp_end":[0.45517,-0.00098,0.10634],"tcp_start":[0.45515,-0.00099,0.10633],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4949,-0.00076,0.10028],"object_pos_start":[0.49476,-0.00076,0.10063],"object_to_goal_dist_end":0.02092,"object_to_goal_dist_start":0.0213,"object_z_max":0.10063,"peak_contact_force":62.30264,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":377.0,"raw_peak_contact_force":293.38331,"tcp_end":[0.45532,-0.001,0.10605],"tcp_start":[0.45517,-0.00098,0.10634],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```