## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.4877 | 0.90 | ❌ rejected |
| 12 | approach → align → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2520 | 0.86 | ❌ rejected |
| 11 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5027 | 0.91 | ❌ rejected |
| 10 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5028 | 0.91 | ✅ accepted |
| 9 | approach → align → descend → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.1560 | 0.48 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.90). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.488) — your mutation base

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

- **Composite score**: 0.488
- **task_score** (E): 0.901
- **fitness_score**: 0.548  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 1.00 | 0.00 | 0.0599 |
| align_hole | 0.00 | 1.00 | 0.1539 |
| descend_insert | 1.00 | 1.00 | 0.0001 |
| release_peg | 1.00 | 1.00 | 0.0005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, -0.010, 0.246) | (0.504, -0.000, 0.340)→(0.512, -0.010, 0.286) | 0.260→0.208 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.00 / step_budget | (0.507, -0.010, 0.246)→(0.495, -0.025, 0.094) | (0.512, -0.010, 0.286)→(0.534, -0.021, 0.096) | 0.208→0.049 | 1.00 / 2.000 | 474.656 | 4430.907 |
| descend_insert | descend | 1.00 / force_exceeded | (0.495, -0.025, 0.094)→(0.495, -0.025, 0.094) | (0.534, -0.021, 0.096)→(0.534, -0.021, 0.096) | 0.049→0.049 | 1.00 / 2.000 | 144.408 | 144.408 |
| release_peg | release | 1.00 / step_budget | (0.495, -0.025, 0.094)→(0.495, -0.024, 0.094) | (0.534, -0.021, 0.096)→(0.534, -0.021, 0.096) | 0.049→0.049 | 1.00 / 2.000 | 53.939 | 311.992 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.874
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.874
- phase_score: 0.359
- phase_breakdown.reach_above_hole_score: 0.052
- phase_breakdown.insert_peg_score: 0.491

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.565
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.997
- **Median Q (composite search score)**: 0.502
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 3.7
- **Final σ (mean)**: 0.259


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.02439,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.06562,"approach_hole.approach_speed":0.10535,"descend_insert.force_threshold":20.63106,"descend_insert.insert_depth":0.11735,"descend_insert.insert_speed":0.02402},"optimized_scores":{"best_composite_score":0.50538,"best_fitness_score":0.56538,"best_task_score":0.87427},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":186.0,"contact_point_centroid":[0.56257,-0.02451,0.07902],"force_p95":699.85064,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1433.82092,"mean_force":439.75583,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.52051,-0.02827,0.0868]},{"body_a":"peg_socket","body_b":"link7","contact_count":214.0,"contact_point_centroid":[0.58887,0.0007,0.07987],"force_p95":715.81935,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1010.26695,"mean_force":509.41598,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50839,-0.02938,0.08869]},{"body_a":"peg_socket","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.5896,-0.00029,0.07999],"force_p95":126.3658,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":315.03449,"mean_force":49.02817,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51057,-0.03296,0.08604]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.5131,-0.04707,0.07999],"force_p95":293.49357,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.83532,"mean_force":260.95954,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51016,-0.03367,0.08602]},{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.55962,-0.02659,0.07999],"force_p95":95.40085,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.19081,"mean_force":53.91195,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51057,-0.03296,0.08604]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58941,-0.00093,0.07994],"force_p95":110.73504,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.73504,"mean_force":110.73504,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51021,-0.03361,0.08598]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.55962,-0.02718,0.07998],"force_p95":37.17955,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.17955,"mean_force":37.17955,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51021,-0.03361,0.08598]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.49918,-0.0152,0.07993],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49852,-0.02729,0.08871]}],"total_contact_groups":8},"final_pose_error":0.12591,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51022,-0.0335,0.08597],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1433.82092,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.52375,-0.01203,0.28563],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20735,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.51923,-0.01202,0.24589],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.54918,-0.02829,0.09326],"object_pos_start":[0.52375,-0.01203,0.28563],"object_to_goal_dist_end":0.05827,"object_to_goal_dist_start":0.20735,"object_z_max":0.28563,"peak_contact_force":519.00087,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":421.0,"raw_peak_contact_force":1433.82092,"subtask_id":"reach_above_hole","tcp_end":[0.51021,-0.03361,0.08598],"tcp_start":[0.51923,-0.01202,0.24589],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54919,-0.02818,0.09326],"object_pos_start":[0.54918,-0.02829,0.09326],"object_to_goal_dist_end":0.05822,"object_to_goal_dist_start":0.05827,"object_z_max":0.09326,"peak_contact_force":110.73504,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":110.73504,"subtask_id":"insert_peg","tcp_end":[0.51022,-0.0335,0.08597],"tcp_start":[0.51021,-0.03361,0.08598],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54958,-0.02763,0.09335],"object_pos_start":[0.54919,-0.02818,0.09326],"object_to_goal_dist_end":0.05831,"object_to_goal_dist_start":0.05822,"object_z_max":0.09336,"peak_contact_force":51.03527,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":400.0,"raw_peak_contact_force":315.03449,"tcp_end":[0.51061,-0.03294,0.08607],"tcp_start":[0.51022,-0.0335,0.08597],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.2439,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.11299,"approach_hole.approach_speed":0.13115,"descend_insert.force_threshold":13.74832,"descend_insert.insert_depth":0.1329,"descend_insert.insert_speed":0.03286},"optimized_scores":{"best_composite_score":0.45611,"best_fitness_score":0.51611,"best_task_score":0.83028},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":212.0,"contact_point_centroid":[0.59584,-0.00675,0.07984],"force_p95":813.44216,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2182.94189,"mean_force":550.54174,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51562,-0.03774,0.08691]},{"body_a":"attachment","body_b":"peg_socket","contact_count":139.0,"contact_point_centroid":[0.57151,-0.03028,0.07898],"force_p95":969.25661,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1688.1377,"mean_force":480.42801,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.53099,-0.03447,0.08571]},{"body_a":"attachment","body_b":"peg_socket","contact_count":69.0,"contact_point_centroid":[0.52003,-0.05349,0.07995],"force_p95":536.44323,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":610.79378,"mean_force":359.4843,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51705,-0.04013,0.0858]},{"body_a":"peg_socket","body_b":"link7","contact_count":196.0,"contact_point_centroid":[0.59645,-0.00651,0.07999],"force_p95":164.0235,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":531.13862,"mean_force":65.97016,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51759,-0.03968,0.08566]},{"body_a":"attachment","body_b":"peg_socket","contact_count":196.0,"contact_point_centroid":[0.56649,-0.03294,0.07997],"force_p95":148.55245,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":385.57878,"mean_force":68.50314,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51759,-0.03968,0.08566]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59625,-0.0067,0.07992],"force_p95":224.48936,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.48936,"mean_force":224.48936,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51717,-0.03983,0.08566]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.56648,-0.03302,0.07998],"force_p95":27.78231,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.78231,"mean_force":27.78231,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51717,-0.03983,0.08566]}],"total_contact_groups":7},"final_pose_error":0.1408,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.51724,-0.03979,0.08561],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":2182.94189,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":135.0,"n_steps_budget":600.0,"object_pos_end":[0.52923,-0.01692,0.28422],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20699,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.5247,-0.01691,0.24448],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.55604,-0.03418,0.09322],"object_pos_start":[0.52923,-0.01692,0.28422],"object_to_goal_dist_end":0.06696,"object_to_goal_dist_start":0.20699,"object_z_max":0.28422,"peak_contact_force":656.9432,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":420.0,"raw_peak_contact_force":2182.94189,"subtask_id":"reach_above_hole","tcp_end":[0.51717,-0.03983,0.08566],"tcp_start":[0.5247,-0.01691,0.24448],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55611,-0.03414,0.09318],"object_pos_start":[0.55604,-0.03418,0.09322],"object_to_goal_dist_end":0.06699,"object_to_goal_dist_start":0.06696,"object_z_max":0.09322,"peak_contact_force":224.48936,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":224.48936,"subtask_id":"insert_peg","tcp_end":[0.51724,-0.03979,0.08561],"tcp_start":[0.51717,-0.03983,0.08566],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55649,-0.03404,0.0933],"object_pos_start":[0.55611,-0.03414,0.09318],"object_to_goal_dist_end":0.06728,"object_to_goal_dist_start":0.06699,"object_z_max":0.09339,"peak_contact_force":49.94989,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":392.0,"raw_peak_contact_force":531.13862,"tcp_end":[0.51762,-0.03967,0.08572],"tcp_start":[0.51724,-0.03979,0.08561],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.84906,"average_solve_count":53.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.10496,"approach_hole.approach_speed":0.05084,"descend_insert.force_threshold":20.03642,"descend_insert.insert_depth":0.10951,"descend_insert.insert_speed":0.02972},"optimized_scores":{"best_composite_score":0.50169,"best_fitness_score":0.56169,"best_task_score":0.99701},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":303.0,"contact_point_centroid":[0.52969,-0.00427,0.06459],"force_p95":604.24157,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9675.95698,"mean_force":489.8214,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.45469,-0.00085,0.10683]},{"body_a":"attachment","body_b":"peg_socket","contact_count":254.0,"contact_point_centroid":[0.52645,-0.00038,0.07941],"force_p95":1068.31225,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7112.35441,"mean_force":398.8516,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.46162,-0.00074,0.10517]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53028,-0.00329,0.04996],"force_p95":3128.55343,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3134.71125,"mean_force":3086.31134,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.43897,-0.00082,0.09768]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53028,-0.0004,0.07996],"force_p95":97.99826,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.99826,"mean_force":97.99826,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45774,-0.00084,0.11012]},{"body_a":"attachment","body_b":"peg_socket","contact_count":198.0,"contact_point_centroid":[0.53028,-0.0004,0.07998],"force_p95":74.76158,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.80328,"mean_force":60.76647,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45791,-0.00086,0.11024]},{"body_a":"peg_socket","body_b":"link7","contact_count":166.0,"contact_point_centroid":[0.53028,-0.00466,0.06421],"force_p95":51.63483,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.50436,"mean_force":20.3633,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45792,-0.00087,0.11026]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53022,-0.00464,0.06418],"force_p95":14.83275,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":14.83275,"mean_force":14.83275,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45774,-0.00084,0.11012]}],"total_contact_groups":7},"final_pose_error":0.14021,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.45774,-0.00084,0.11014],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":9675.95698,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":117.0,"n_steps_budget":960.0,"object_pos_end":[0.48237,-5e-05,0.28775],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20849,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47783,-6e-05,0.24801],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.49692,-0.00063,0.10208],"object_pos_start":[0.48237,-5e-05,0.28775],"object_to_goal_dist_end":0.0223,"object_to_goal_dist_start":0.20849,"object_z_max":0.28775,"peak_contact_force":248.02348,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":560.0,"raw_peak_contact_force":9675.95698,"subtask_id":"reach_above_hole","tcp_end":[0.45774,-0.00084,0.11012],"tcp_start":[0.47783,-6e-05,0.24801],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49692,-0.00063,0.10209],"object_pos_start":[0.49692,-0.00063,0.10208],"object_to_goal_dist_end":0.02231,"object_to_goal_dist_start":0.0223,"object_z_max":0.10208,"peak_contact_force":97.99826,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":97.99826,"subtask_id":"insert_peg","tcp_end":[0.45774,-0.00084,0.11014],"tcp_start":[0.45774,-0.00084,0.11012],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49712,-0.00065,0.10217],"object_pos_start":[0.49692,-0.00063,0.10209],"object_to_goal_dist_end":0.02236,"object_to_goal_dist_start":0.02231,"object_z_max":0.10217,"peak_contact_force":60.83333,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":364.0,"raw_peak_contact_force":89.80328,"tcp_end":[0.45795,-0.00087,0.1103],"tcp_start":[0.45774,-0.00084,0.11014],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```