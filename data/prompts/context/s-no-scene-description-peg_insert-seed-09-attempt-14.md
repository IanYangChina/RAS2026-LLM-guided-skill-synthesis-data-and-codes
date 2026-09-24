## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3390 | 0.74 | ❌ rejected |
| 13 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.4877 | 0.90 | ❌ rejected |
| 12 | approach → align → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2520 | 0.86 | ❌ rejected |
| 11 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5027 | 0.91 | ❌ rejected |
| 10 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5028 | 0.91 | ✅ accepted |

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
- **task_score** (E): 0.744
- **fitness_score**: 0.399  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 1.00 | 0.00 | 0.0598 |
| align_hole | 0.00 | 1.00 | 0.1655 |
| descend_insert | 1.00 | 1.00 | 0.0001 |
| release_peg | 1.00 | 1.00 | 0.0021 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, -0.010, 0.246) | (0.504, -0.000, 0.340)→(0.512, -0.010, 0.286) | 0.260→0.208 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.00 / step_budget | (0.507, -0.010, 0.246)→(0.545, -0.016, 0.091) | (0.512, -0.010, 0.286)→(0.579, -0.012, 0.104) | 0.208→0.091 | 1.00 / 1.000 | 275.422 | 5090.232 |
| descend_insert | descend | 1.00 / force_exceeded | (0.545, -0.016, 0.091)→(0.545, -0.016, 0.091) | (0.579, -0.012, 0.104)→(0.580, -0.012, 0.104) | 0.091→0.091 | 1.00 / 1.000 | 298.335 | 298.335 |
| release_peg | release | 1.00 / step_budget | (0.545, -0.016, 0.091)→(0.547, -0.016, 0.092) | (0.580, -0.012, 0.104)→(0.581, -0.012, 0.105) | 0.091→0.093 | 1.00 / 1.333 | 63.382 | 233.010 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.999
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.999
- phase_score: 0.269
- phase_breakdown.reach_above_hole_score: 0.073
- phase_breakdown.insert_peg_score: 0.353

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.561
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.999
- **Median Q (composite search score)**: 0.277
- **K-run variance**: 0.0133
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.02439,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.11299,"approach_hole.approach_speed":0.13115,"descend_insert.force_threshold":18.74832,"descend_insert.insert_depth":0.1529,"descend_insert.insert_speed":0.03286},"optimized_scores":{"best_composite_score":0.27676,"best_fitness_score":0.33676,"best_task_score":0.64055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":43.0,"contact_point_centroid":[0.5865,-0.00719,0.07675],"force_p95":1225.33318,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1423.31825,"mean_force":421.96351,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.58007,-0.02047,0.07948]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.58845,-0.00733,0.07912],"force_p95":301.12469,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":301.12469,"mean_force":301.12469,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.58391,-0.02033,0.08493]},{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.5895,-0.0077,0.07991],"force_p95":100.84763,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.67665,"mean_force":75.23544,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.58574,-0.02049,0.08676]}],"total_contact_groups":3},"final_pose_error":0.16709,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.58399,-0.02025,0.08506],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1423.31825,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.52375,-0.01203,0.28563],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20735,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.51923,-0.01202,0.24589],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":600.0,"object_pos_end":[0.61681,-0.01725,0.10748],"object_pos_start":[0.52375,-0.01203,0.28563],"object_to_goal_dist_end":0.12123,"object_to_goal_dist_start":0.20735,"object_z_max":0.28563,"peak_contact_force":262.18061,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":43.0,"raw_peak_contact_force":1423.31825,"subtask_id":"reach_above_hole","tcp_end":[0.58391,-0.02033,0.08493],"tcp_start":[0.51923,-0.01202,0.24589],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.61695,-0.01726,0.10752],"object_pos_start":[0.61681,-0.01725,0.10748],"object_to_goal_dist_end":0.12138,"object_to_goal_dist_start":0.12123,"object_z_max":0.10748,"peak_contact_force":301.12469,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":301.12469,"subtask_id":"insert_peg","tcp_end":[0.58399,-0.02025,0.08506],"tcp_start":[0.58391,-0.02033,0.08493],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61891,-0.01766,0.10939],"object_pos_start":[0.61695,-0.01726,0.10752],"object_to_goal_dist_end":0.12376,"object_to_goal_dist_start":0.12138,"object_z_max":0.10961,"peak_contact_force":64.69684,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":235.67665,"tcp_end":[0.58605,-0.02055,0.08676],"tcp_start":[0.58399,-0.02025,0.08506],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.68085,"average_solve_count":47.0,"average_success_count":47.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.1237,"approach_hole.approach_speed":0.06841,"descend_insert.force_threshold":23.77714,"descend_insert.insert_depth":0.11079,"descend_insert.insert_speed":0.02924},"optimized_scores":{"best_composite_score":0.23938,"best_fitness_score":0.29938,"best_task_score":0.59228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":42.0,"contact_point_centroid":[0.59268,-0.01005,0.07616],"force_p95":1275.34693,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1482.31353,"mean_force":456.74517,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.59097,-0.0246,0.07485]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.59518,-0.01145,0.07897],"force_p95":296.02527,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.02527,"mean_force":296.02527,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.59578,-0.02617,0.0801]},{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.59639,-0.01113,0.07993],"force_p95":112.8318,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.24098,"mean_force":75.15966,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.59815,-0.02587,0.08191]}],"total_contact_groups":3},"final_pose_error":0.12594,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.5959,-0.02615,0.08022],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1482.31353,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":139.0,"n_steps_budget":780.0,"object_pos_end":[0.52907,-0.0169,0.28422],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20697,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52452,-0.01688,0.24448],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":600.0,"object_pos_end":[0.62662,-0.01863,0.10443],"object_pos_start":[0.52907,-0.0169,0.28422],"object_to_goal_dist_end":0.13029,"object_to_goal_dist_start":0.20697,"object_z_max":0.28422,"peak_contact_force":290.66291,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":42.0,"raw_peak_contact_force":1482.31353,"subtask_id":"reach_above_hole","tcp_end":[0.59578,-0.02617,0.0801],"tcp_start":[0.52452,-0.01688,0.24448],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.62678,-0.01872,0.10452],"object_pos_start":[0.62662,-0.01863,0.10443],"object_to_goal_dist_end":0.13048,"object_to_goal_dist_start":0.13029,"object_z_max":0.10443,"peak_contact_force":296.02527,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":296.02527,"subtask_id":"insert_peg","tcp_end":[0.5959,-0.02615,0.08022],"tcp_start":[0.59578,-0.02617,0.0801],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62914,-0.01862,0.10646],"object_pos_start":[0.62678,-0.01872,0.10452],"object_to_goal_dist_end":0.13313,"object_to_goal_dist_start":0.13048,"object_z_max":0.10672,"peak_contact_force":63.6187,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":232.24098,"tcp_end":[0.59844,-0.02592,0.08187],"tcp_start":[0.5959,-0.02615,0.08022],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.04167,"average_solve_count":48.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.1412,"approach_hole.approach_speed":0.0595,"descend_insert.force_threshold":18.35878,"descend_insert.insert_depth":0.13788,"descend_insert.insert_speed":0.02078},"optimized_scores":{"best_composite_score":0.5008,"best_fitness_score":0.5608,"best_task_score":0.99852},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":72.0,"contact_point_centroid":[0.52782,-0.00325,0.06567],"force_p95":11432.60147,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12365.0634,"mean_force":1721.03247,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.44849,-0.00127,0.10306]},{"body_a":"attachment","body_b":"peg_socket","contact_count":45.0,"contact_point_centroid":[0.50827,-0.00036,0.07665],"force_p95":7517.57727,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7825.72544,"mean_force":1933.79224,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48278,-0.00052,0.08742]},{"body_a":"peg_socket","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.53027,-0.00315,0.04973],"force_p95":5008.82257,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5010.46949,"mean_force":4175.29014,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.43884,-0.00118,0.09862]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53023,-0.00453,0.06483],"force_p95":297.85397,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.85397,"mean_force":297.85397,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45539,-0.00102,0.10684]},{"body_a":"peg_socket","body_b":"link7","contact_count":168.0,"contact_point_centroid":[0.53027,-0.00456,0.06432],"force_p95":112.97918,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.11309,"mean_force":28.87412,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45552,-0.00108,0.10642]},{"body_a":"attachment","body_b":"peg_socket","contact_count":191.0,"contact_point_centroid":[0.53028,-0.00053,0.07998],"force_p95":88.19786,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.74748,"mean_force":65.25113,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45552,-0.00108,0.1064]}],"total_contact_groups":6},"final_pose_error":0.1654,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.45541,-0.00102,0.10684],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":12365.0634,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":115.0,"n_steps_budget":810.0,"object_pos_end":[0.48243,-5e-05,0.28812],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20886,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47787,-6e-05,0.24838],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":194.0,"n_steps_budget":600.0,"object_pos_end":[0.49495,-0.00077,0.10091],"object_pos_start":[0.48243,-5e-05,0.28812],"object_to_goal_dist_end":0.02153,"object_to_goal_dist_start":0.20886,"object_z_max":0.28812,"peak_contact_force":273.42111,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":125.0,"raw_peak_contact_force":12365.0634,"subtask_id":"reach_above_hole","tcp_end":[0.45539,-0.00102,0.10684],"tcp_start":[0.47787,-6e-05,0.24838],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49497,-0.00076,0.10091],"object_pos_start":[0.49495,-0.00077,0.10091],"object_to_goal_dist_end":0.02152,"object_to_goal_dist_start":0.02153,"object_z_max":0.10091,"peak_contact_force":297.85397,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":297.85397,"subtask_id":"insert_peg","tcp_end":[0.45541,-0.00102,0.10684],"tcp_start":[0.45539,-0.00102,0.10684],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49511,-0.00083,0.10047],"object_pos_start":[0.49497,-0.00076,0.10091],"object_to_goal_dist_end":0.02106,"object_to_goal_dist_start":0.02152,"object_z_max":0.10091,"peak_contact_force":61.83079,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":359.0,"raw_peak_contact_force":231.11309,"tcp_end":[0.45556,-0.0011,0.10646],"tcp_start":[0.45541,-0.00102,0.10684],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```