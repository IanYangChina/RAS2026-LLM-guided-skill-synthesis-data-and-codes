## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.4379 | 0.82 | ❌ rejected |
| 4 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.3951 | 0.86 | ❌ rejected |
| 3 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3393 | 0.74 | ❌ rejected |
| 2 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5025 | 0.91 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | 0.4018 | 0.77 | ❌ rejected |

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

## Current Skill (Q=0.438) — your mutation base

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

- **Composite score**: 0.438
- **task_score** (E): 0.823
- **fitness_score**: 0.478  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 1.00 | 0.00 | 0.0598 |
| align_hole | 0.00 | 1.00 | 0.1565 |
| contact_probe | 1.00 | 1.00 | 0.0001 |
| descend_insert | 1.00 | 1.00 | 0.0002 |
| release_peg | 1.00 | 1.00 | 0.0006 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, -0.010, 0.246) | (0.504, -0.000, 0.340)→(0.512, -0.010, 0.286) | 0.260→0.208 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.00 / step_budget | (0.507, -0.010, 0.246)→(0.520, -0.019, 0.095) | (0.512, -0.010, 0.286)→(0.557, -0.015, 0.102) | 0.208→0.070 | 1.00 / 1.667 | 362.893 | 4532.788 |
| contact_probe | contact | 1.00 / force_exceeded | (0.520, -0.019, 0.095)→(0.520, -0.019, 0.095) | (0.557, -0.015, 0.102)→(0.557, -0.015, 0.103) | 0.070→0.070 | 1.00 / 1.667 | 107.165 | 107.165 |
| descend_insert | descend | 1.00 / force_exceeded | (0.520, -0.019, 0.095)→(0.520, -0.019, 0.095) | (0.557, -0.015, 0.103)→(0.557, -0.015, 0.103) | 0.070→0.070 | 1.00 / 1.333 | 171.452 | 144.327 |
| release_peg | release | 1.00 / step_budget | (0.520, -0.019, 0.095)→(0.521, -0.019, 0.096) | (0.557, -0.015, 0.103)→(0.557, -0.016, 0.103) | 0.070→0.070 | 1.00 / 1.000 | 67.305 | 167.215 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.999
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.999
- phase_score: 0.272
- phase_breakdown.reach_above_hole_score: 0.078
- phase_breakdown.insert_peg_score: 0.355

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.563
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.999
- **Median Q (composite search score)**: 0.517
- **K-run variance**: 0.0134
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.305


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.39583,"average_solve_count":48.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.11729,"approach_hole.approach_speed":0.16979,"contact_probe.contact_force_limit":14.58903,"contact_probe.contact_speed":0.01656,"descend_insert.force_threshold":8.07571,"descend_insert.insert_depth":0.06929,"descend_insert.insert_speed":0.01963},"optimized_scores":{"best_composite_score":0.51682,"best_fitness_score":0.55682,"best_task_score":0.85603},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":105.0,"contact_point_centroid":[0.56563,-0.02583,0.0784],"force_p95":893.13717,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1434.49384,"mean_force":476.30095,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.52937,-0.02886,0.08731]},{"body_a":"peg_socket","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.58836,-0.00098,0.07978],"force_p95":775.41722,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1022.18889,"mean_force":500.33687,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50773,-0.03147,0.09021]},{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.55962,-0.02824,0.07998],"force_p95":69.57285,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.91527,"mean_force":69.93769,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.5108,-0.03307,0.08925]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.55962,-0.02842,0.07997],"force_p95":150.56423,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.96403,"mean_force":128.96606,"phase_index":3.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51057,-0.03326,0.08914]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.55963,-0.02847,0.0799],"force_p95":143.11823,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.11823,"mean_force":143.11823,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.51044,-0.03332,0.08901]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58959,-0.00153,0.07999],"force_p95":103.80902,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.80902,"mean_force":103.80902,"phase_index":3.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51052,-0.03329,0.0891]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58954,-0.0015,0.07998],"force_p95":27.86804,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.86804,"mean_force":27.86804,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.51044,-0.03332,0.08901]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.49918,-0.01917,0.07992],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49883,-0.03128,0.08865]}],"total_contact_groups":8},"final_pose_error":0.08219,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51081,-0.03308,0.0891],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1434.49384,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.52375,-0.01203,0.28563],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20735,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.51923,-0.01202,0.24589],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.54995,-0.0293,0.09375],"object_pos_start":[0.52375,-0.01203,0.28563],"object_to_goal_dist_end":0.05952,"object_to_goal_dist_start":0.20735,"object_z_max":0.28563,"peak_contact_force":605.78015,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":242.0,"raw_peak_contact_force":1434.49384,"subtask_id":"reach_above_hole","tcp_end":[0.51044,-0.03332,0.08901],"tcp_start":[0.51923,-0.01202,0.24589],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55004,-0.02927,0.09384],"object_pos_start":[0.54995,-0.0293,0.09375],"object_to_goal_dist_end":0.0596,"object_to_goal_dist_start":0.05952,"object_z_max":0.09375,"peak_contact_force":143.11823,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":143.11823,"subtask_id":"insert_peg","tcp_end":[0.51052,-0.03329,0.0891],"tcp_start":[0.51044,-0.03332,0.08901],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.55032,-0.02906,0.09388],"object_pos_start":[0.55004,-0.02927,0.09384],"object_to_goal_dist_end":0.05974,"object_to_goal_dist_start":0.0596,"object_z_max":0.0941,"peak_contact_force":234.3372,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":152.96403,"subtask_id":"insert_peg","tcp_end":[0.51081,-0.03308,0.0891],"tcp_start":[0.51052,-0.03329,0.0891],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55017,-0.02904,0.09395],"object_pos_start":[0.55032,-0.02906,0.09388],"object_to_goal_dist_end":0.05963,"object_to_goal_dist_start":0.05974,"object_z_max":0.09398,"peak_contact_force":68.80585,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":229.91527,"tcp_end":[0.51065,-0.03309,0.0893],"tcp_start":[0.51081,-0.03308,0.0891],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.11905,"average_solve_count":42.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.12428,"approach_hole.approach_speed":0.10469,"contact_probe.contact_force_limit":8.55132,"contact_probe.contact_speed":0.01459,"descend_insert.force_threshold":15.8356,"descend_insert.insert_depth":0.03629,"descend_insert.insert_speed":0.01744},"optimized_scores":{"best_composite_score":0.27415,"best_fitness_score":0.31415,"best_task_score":0.61465},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":188.0,"contact_point_centroid":[0.59544,-0.01167,0.07892],"force_p95":456.02986,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1450.53508,"mean_force":285.35963,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.59011,-0.02393,0.08529]},{"body_a":"attachment","body_b":"peg_socket","contact_count":194.0,"contact_point_centroid":[0.59647,-0.01077,0.07999],"force_p95":131.20133,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.69656,"mean_force":69.75699,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.59302,-0.02337,0.08734]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.59631,-0.01021,0.07984],"force_p95":164.29331,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.29331,"mean_force":164.29331,"phase_index":3.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.59231,-0.02245,0.08746]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.59632,-0.01013,0.07985],"force_p95":54.83929,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.83929,"mean_force":54.83929,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.59232,-0.02237,0.08747]}],"total_contact_groups":4},"final_pose_error":0.07098,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.59234,-0.02236,0.08749],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1450.53508,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":135.0,"n_steps_budget":600.0,"object_pos_end":[0.52923,-0.01692,0.28422],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20699,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.5247,-0.01691,0.24448],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.62362,-0.01678,0.11173],"object_pos_start":[0.52923,-0.01692,0.28422],"object_to_goal_dist_end":0.12873,"object_to_goal_dist_start":0.20699,"object_z_max":0.28422,"peak_contact_force":233.93999,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":188.0,"raw_peak_contact_force":1450.53508,"subtask_id":"reach_above_hole","tcp_end":[0.59232,-0.02237,0.08747],"tcp_start":[0.5247,-0.01691,0.24448],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.62362,-0.01683,0.11172],"object_pos_start":[0.62362,-0.01678,0.11173],"object_to_goal_dist_end":0.12873,"object_to_goal_dist_start":0.12873,"object_z_max":0.11173,"peak_contact_force":54.83929,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":54.83929,"subtask_id":"insert_peg","tcp_end":[0.59231,-0.02245,0.08746],"tcp_start":[0.59232,-0.02237,0.08747],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.62364,-0.01674,0.11175],"object_pos_start":[0.62362,-0.01683,0.11172],"object_to_goal_dist_end":0.12875,"object_to_goal_dist_start":0.12873,"object_z_max":0.11172,"peak_contact_force":164.29331,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":164.29331,"subtask_id":"insert_peg","tcp_end":[0.59234,-0.02236,0.08749],"tcp_start":[0.59231,-0.02245,0.08746],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62439,-0.01777,0.11152],"object_pos_start":[0.62364,-0.01674,0.11175],"object_to_goal_dist_end":0.12954,"object_to_goal_dist_start":0.12875,"object_z_max":0.11211,"peak_contact_force":63.87817,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":194.0,"raw_peak_contact_force":170.69656,"tcp_end":[0.59315,-0.02345,0.0872],"tcp_start":[0.59234,-0.02236,0.08749],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.39706,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.15037,"approach_hole.approach_speed":0.03404,"contact_probe.contact_force_limit":9.1019,"contact_probe.contact_speed":0.01679,"descend_insert.force_threshold":18.49565,"descend_insert.insert_depth":0.04211,"descend_insert.insert_speed":0.03894},"optimized_scores":{"best_composite_score":0.52275,"best_fitness_score":0.56275,"best_task_score":0.99918},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":216.0,"contact_point_centroid":[0.52943,-0.00382,0.06472],"force_p95":1000.20759,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10713.33576,"mean_force":684.75345,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.45378,-0.00066,0.10621]},{"body_a":"attachment","body_b":"peg_socket","contact_count":169.0,"contact_point_centroid":[0.52453,-0.00014,0.07906],"force_p95":4820.57913,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7721.06034,"mean_force":624.1361,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.46385,-0.00052,0.10312]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.53028,-0.00328,0.04988],"force_p95":3319.46546,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3325.64238,"mean_force":3176.49254,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.43926,-0.00094,0.09811]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53027,-6e-05,0.07995],"force_p95":123.53649,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.53649,"mean_force":123.53649,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.45762,-0.00054,0.10991]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53024,-0.00428,0.06415],"force_p95":115.72509,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.72509,"mean_force":115.72509,"phase_index":3.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45764,-0.00054,0.1099]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53027,-0.00428,0.06413],"force_p95":98.97095,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.03338,"mean_force":82.96081,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45769,-0.00054,0.10985]},{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.53028,-7e-05,0.07997],"force_p95":72.50484,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.8361,"mean_force":69.5348,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45786,-0.00056,0.10999]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53027,-6e-05,0.07994],"force_p95":78.37998,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.37998,"mean_force":78.37998,"phase_index":3.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45764,-0.00054,0.1099]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53023,-0.00429,0.06416],"force_p95":0.0,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.45762,-0.00054,0.10991]}],"total_contact_groups":9},"final_pose_error":0.07309,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.45766,-0.00054,0.10988],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":10713.33576,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":119.0,"n_steps_budget":1000.0,"object_pos_end":[0.48256,-5e-05,0.28802],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20875,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47804,-6e-05,0.24827],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.49682,-0.00031,0.10197],"object_pos_start":[0.48256,-5e-05,0.28802],"object_to_goal_dist_end":0.0222,"object_to_goal_dist_start":0.20875,"object_z_max":0.28802,"peak_contact_force":248.95809,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":391.0,"raw_peak_contact_force":10713.33576,"subtask_id":"reach_above_hole","tcp_end":[0.45762,-0.00054,0.10991],"tcp_start":[0.47804,-6e-05,0.24827],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49685,-0.00031,0.10196],"object_pos_start":[0.49682,-0.00031,0.10197],"object_to_goal_dist_end":0.02219,"object_to_goal_dist_start":0.0222,"object_z_max":0.10197,"peak_contact_force":123.53649,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":123.53649,"subtask_id":"insert_peg","tcp_end":[0.45764,-0.00054,0.1099],"tcp_start":[0.45762,-0.00054,0.10991],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49687,-0.00031,0.10195],"object_pos_start":[0.49685,-0.00031,0.10196],"object_to_goal_dist_end":0.02217,"object_to_goal_dist_start":0.02219,"object_z_max":0.10196,"peak_contact_force":115.72509,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":115.72509,"subtask_id":"insert_peg","tcp_end":[0.45766,-0.00054,0.10988],"tcp_start":[0.45764,-0.00054,0.1099],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49704,-0.00034,0.10208],"object_pos_start":[0.49687,-0.00031,0.10195],"object_to_goal_dist_end":0.02228,"object_to_goal_dist_start":0.02217,"object_z_max":0.10207,"peak_contact_force":69.23111,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":204.0,"raw_peak_contact_force":101.03338,"tcp_end":[0.45785,-0.00058,0.1101],"tcp_start":[0.45766,-0.00054,0.10988],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```