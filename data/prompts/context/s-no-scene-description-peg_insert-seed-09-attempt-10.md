## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5028 | 0.91 | ✅ accepted |
| 9 | approach → align → descend → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.1560 | 0.48 | ❌ rejected |
| 8 | approach → align → descend → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | 0.2934 | 0.87 | ❌ rejected |
| 7 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3292 | 0.86 | ❌ rejected |
| 6 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0831 | 0.57 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.503) — your mutation base

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

- **Composite score**: 0.503
- **task_score** (E): 0.907
- **fitness_score**: 0.563  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 1.00 | 0.00 | 0.0598 |
| align_hole | 0.00 | 1.00 | 0.1520 |
| descend_insert | 1.00 | 1.00 | 0.0001 |
| release_peg | 1.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, -0.010, 0.246) | (0.504, -0.000, 0.340)→(0.512, -0.010, 0.286) | 0.260→0.208 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.00 / step_budget | (0.507, -0.010, 0.246)→(0.495, -0.021, 0.095) | (0.512, -0.010, 0.286)→(0.534, -0.019, 0.096) | 0.208→0.048 | 1.00 / 2.000 | 564.632 | 5139.444 |
| descend_insert | descend | 1.00 / force_exceeded | (0.495, -0.021, 0.095)→(0.495, -0.021, 0.096) | (0.534, -0.019, 0.096)→(0.534, -0.019, 0.096) | 0.048→0.048 | 1.00 / 1.667 | 187.119 | 145.890 |
| release_peg | release | 1.00 / step_budget | (0.495, -0.021, 0.096)→(0.495, -0.021, 0.096) | (0.534, -0.019, 0.096)→(0.534, -0.018, 0.097) | 0.048→0.048 | 1.00 / 1.667 | 59.056 | 189.442 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.864
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.864
- phase_score: 0.373
- phase_breakdown.reach_above_hole_score: 0.054
- phase_breakdown.insert_peg_score: 0.509

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.569
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.999
- **Median Q (composite search score)**: 0.503
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.02439,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.10771,"approach_hole.approach_speed":0.11468,"descend_insert.force_threshold":14.82461,"descend_insert.insert_depth":0.07197,"descend_insert.insert_speed":0.02266},"optimized_scores":{"best_composite_score":0.49636,"best_fitness_score":0.55636,"best_task_score":0.85603},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":105.0,"contact_point_centroid":[0.56563,-0.02583,0.0784],"force_p95":893.13717,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1434.49384,"mean_force":476.30095,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.52937,-0.02886,0.08731]},{"body_a":"peg_socket","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.58836,-0.00098,0.07978],"force_p95":775.41722,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1022.18889,"mean_force":500.33687,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50773,-0.03147,0.09021]},{"body_a":"peg_socket","body_b":"link7","contact_count":191.0,"contact_point_centroid":[0.5896,-0.00128,0.08],"force_p95":175.92536,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":193.71272,"mean_force":56.93832,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51055,-0.03306,0.08919]},{"body_a":"attachment","body_b":"peg_socket","contact_count":194.0,"contact_point_centroid":[0.55963,-0.02822,0.07996],"force_p95":179.15377,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":193.42336,"mean_force":75.44137,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51056,-0.03306,0.08919]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.55963,-0.02847,0.0799],"force_p95":143.11823,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.11823,"mean_force":143.11823,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51044,-0.03332,0.08901]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58954,-0.0015,0.07998],"force_p95":27.86804,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.86804,"mean_force":27.86804,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51044,-0.03332,0.08901]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.49918,-0.01917,0.07992],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49883,-0.03128,0.08865]}],"total_contact_groups":7},"final_pose_error":0.08486,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51052,-0.03329,0.0891],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1434.49384,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.52375,-0.01203,0.28563],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20735,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.51923,-0.01202,0.24589],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.54995,-0.0293,0.09375],"object_pos_start":[0.52375,-0.01203,0.28563],"object_to_goal_dist_end":0.05952,"object_to_goal_dist_start":0.20735,"object_z_max":0.28563,"peak_contact_force":605.78015,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":242.0,"raw_peak_contact_force":1434.49384,"subtask_id":"reach_above_hole","tcp_end":[0.51044,-0.03332,0.08901],"tcp_start":[0.51923,-0.01202,0.24589],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55004,-0.02927,0.09384],"object_pos_start":[0.54995,-0.0293,0.09375],"object_to_goal_dist_end":0.0596,"object_to_goal_dist_start":0.05952,"object_z_max":0.09375,"peak_contact_force":143.11823,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":143.11823,"subtask_id":"insert_peg","tcp_end":[0.51052,-0.03329,0.0891],"tcp_start":[0.51044,-0.03332,0.08901],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55009,-0.02904,0.09395],"object_pos_start":[0.55004,-0.02927,0.09384],"object_to_goal_dist_end":0.05956,"object_to_goal_dist_start":0.0596,"object_z_max":0.09411,"peak_contact_force":54.28544,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":385.0,"raw_peak_contact_force":193.71272,"tcp_end":[0.51057,-0.03306,0.08928],"tcp_start":[0.51052,-0.03329,0.0891],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28571,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.144,"approach_hole.approach_speed":0.02017,"descend_insert.force_threshold":27.00001,"descend_insert.insert_depth":0.06426,"descend_insert.insert_speed":0.02646},"optimized_scores":{"best_composite_score":0.5093,"best_fitness_score":0.5693,"best_task_score":0.86429},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.59554,0.00026,0.0798],"force_p95":2697.94277,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3270.50176,"mean_force":967.41305,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51397,-0.02723,0.08838]},{"body_a":"attachment","body_b":"peg_socket","contact_count":134.0,"contact_point_centroid":[0.57227,-0.02437,0.07855],"force_p95":2204.49883,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2850.53035,"mean_force":824.59132,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.53042,-0.02698,0.0863]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.52309,-0.05366,0.07989],"force_p95":752.24124,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":763.88817,"mean_force":580.3803,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51981,-0.04009,0.08438]},{"body_a":"attachment","body_b":"peg_socket","contact_count":193.0,"contact_point_centroid":[0.56649,-0.02529,0.07996],"force_p95":205.22412,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.88776,"mean_force":80.28595,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51595,-0.02847,0.08766]},{"body_a":"peg_socket","body_b":"link7","contact_count":191.0,"contact_point_centroid":[0.59645,0.00025,0.07999],"force_p95":195.88897,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.99321,"mean_force":66.15994,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51595,-0.02847,0.08766]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.56649,-0.02545,0.07994],"force_p95":171.01645,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.01645,"mean_force":171.01645,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51591,-0.02858,0.08756]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59645,8e-05,0.07999],"force_p95":62.77478,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.77478,"mean_force":62.77478,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51591,-0.02858,0.08756]}],"total_contact_groups":7},"final_pose_error":0.07494,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.51602,-0.02869,0.08764],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":3270.50176,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.52893,-0.01687,0.28422],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20695,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52437,-0.01685,0.24448],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.5554,-0.02603,0.0934],"object_pos_start":[0.52893,-0.01687,0.28422],"object_to_goal_dist_end":0.06266,"object_to_goal_dist_start":0.20695,"object_z_max":0.28422,"peak_contact_force":839.15744,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":265.0,"raw_peak_contact_force":3270.50176,"subtask_id":"reach_above_hole","tcp_end":[0.51591,-0.02858,0.08756],"tcp_start":[0.52437,-0.01685,0.24448],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5555,-0.0261,0.09351],"object_pos_start":[0.5554,-0.02603,0.0934],"object_to_goal_dist_end":0.0628,"object_to_goal_dist_start":0.06266,"object_z_max":0.0934,"peak_contact_force":294.70142,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":171.01645,"subtask_id":"insert_peg","tcp_end":[0.51602,-0.02869,0.08764],"tcp_start":[0.51591,-0.02858,0.08756],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55547,-0.02589,0.09352],"object_pos_start":[0.5555,-0.0261,0.09351],"object_to_goal_dist_end":0.06269,"object_to_goal_dist_start":0.0628,"object_z_max":0.09377,"peak_contact_force":53.64801,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":384.0,"raw_peak_contact_force":258.88776,"tcp_end":[0.51597,-0.02846,0.08773],"tcp_start":[0.51602,-0.02869,0.08764],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44776,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.09975,"approach_hole.approach_speed":0.03456,"descend_insert.force_threshold":11.55764,"descend_insert.insert_depth":0.10787,"descend_insert.insert_speed":0.00516},"optimized_scores":{"best_composite_score":0.50267,"best_fitness_score":0.56267,"best_task_score":0.99918},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":216.0,"contact_point_centroid":[0.52943,-0.00382,0.06472],"force_p95":1000.20759,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10713.33576,"mean_force":684.75345,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.45378,-0.00066,0.10621]},{"body_a":"attachment","body_b":"peg_socket","contact_count":169.0,"contact_point_centroid":[0.52453,-0.00014,0.07906],"force_p95":4820.57913,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7721.06034,"mean_force":624.1361,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.46385,-0.00052,0.10312]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.53028,-0.00328,0.04988],"force_p95":3319.46546,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3325.64238,"mean_force":3176.49254,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.43926,-0.00094,0.09811]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53027,-6e-05,0.07995],"force_p95":123.53649,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.53649,"mean_force":123.53649,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45762,-0.00054,0.10991]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53026,-0.00428,0.06414],"force_p95":112.77688,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.72509,"mean_force":89.82726,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45768,-0.00054,0.10986]},{"body_a":"attachment","body_b":"peg_socket","contact_count":200.0,"contact_point_centroid":[0.53028,-7e-05,0.07997],"force_p95":73.20933,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.29611,"mean_force":69.59234,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.45785,-0.00056,0.10999]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53023,-0.00429,0.06416],"force_p95":0.0,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45762,-0.00054,0.10991]}],"total_contact_groups":7},"final_pose_error":0.13835,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.45764,-0.00054,0.1099],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":10713.33576,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":119.0,"n_steps_budget":1000.0,"object_pos_end":[0.48256,-5e-05,0.28802],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20875,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47804,-6e-05,0.24827],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.49682,-0.00031,0.10197],"object_pos_start":[0.48256,-5e-05,0.28802],"object_to_goal_dist_end":0.0222,"object_to_goal_dist_start":0.20875,"object_z_max":0.28802,"peak_contact_force":248.95809,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":391.0,"raw_peak_contact_force":10713.33576,"subtask_id":"reach_above_hole","tcp_end":[0.45762,-0.00054,0.10991],"tcp_start":[0.47804,-6e-05,0.24827],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49685,-0.00031,0.10196],"object_pos_start":[0.49682,-0.00031,0.10197],"object_to_goal_dist_end":0.02219,"object_to_goal_dist_start":0.0222,"object_z_max":0.10197,"peak_contact_force":123.53649,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":123.53649,"subtask_id":"insert_peg","tcp_end":[0.45764,-0.00054,0.1099],"tcp_start":[0.45762,-0.00054,0.10991],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49703,-0.00034,0.10208],"object_pos_start":[0.49685,-0.00031,0.10196],"object_to_goal_dist_end":0.02228,"object_to_goal_dist_start":0.02219,"object_z_max":0.10208,"peak_contact_force":69.23506,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":205.0,"raw_peak_contact_force":115.72509,"tcp_end":[0.45785,-0.00058,0.1101],"tcp_start":[0.45764,-0.00054,0.1099],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```