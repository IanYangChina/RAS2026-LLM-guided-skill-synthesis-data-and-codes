## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → align → descend → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | 0.2934 | 0.87 | ❌ rejected |
| 7 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3292 | 0.86 | ❌ rejected |
| 6 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0831 | 0.57 | ❌ rejected |
| 5 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.4379 | 0.82 | ❌ rejected |
| 4 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.3951 | 0.86 | ❌ rejected |

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

## Current Skill (Q=0.293) — your mutation base

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

- **Composite score**: 0.293
- **task_score** (E): 0.867
- **fitness_score**: 0.483  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 0.00 | 1.00 | 0.1503 |
| align_hole | 0.00 | 1.00 | 0.0159 |
| descend_to_entry | 0.33 | 0.67 | 0.0321 |
| insert_peg | 1.00 | 1.00 | 0.0004 |
| release_peg | 1.00 | 1.00 | 0.0005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.462, -0.009, 0.156) | (0.504, -0.000, 0.340)→(0.500, -0.009, 0.143) | 0.260→0.064 | 1.00 / 1.000 | 268.876 | 1242.622 |
| align_hole | align | 0.00 / step_budget | (0.462, -0.009, 0.156)→(0.462, -0.018, 0.169) | (0.500, -0.009, 0.143)→(0.499, -0.016, 0.153) | 0.064→0.075 | 1.00 / 1.333 | 240.280 | 332.679 |
| descend_to_entry | descend | 0.33 / step_budget | (0.462, -0.018, 0.169)→(0.489, -0.016, 0.155) | (0.499, -0.016, 0.153)→(0.526, -0.016, 0.139) | 0.075→0.067 | 0.67 / 0.667 | 260.049 | 373.111 |
| insert_peg | insert | 1.00 / force_exceeded | (0.489, -0.016, 0.155)→(0.490, -0.016, 0.155) | (0.526, -0.016, 0.139)→(0.526, -0.017, 0.139) | 0.067→0.067 | 1.00 / 1.000 | 212.754 | 128.510 |
| release_peg | release | 1.00 / step_budget | (0.490, -0.016, 0.155)→(0.490, -0.016, 0.155) | (0.526, -0.017, 0.139)→(0.526, -0.017, 0.139) | 0.067→0.067 | 1.00 / 1.000 | 67.046 | 320.219 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.837
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.837
- phase_score: 0.283
- phase_breakdown.reach_above_hole_score: 0.082
- phase_breakdown.insert_peg_score: 0.369

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.505
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.884
- **Median Q (composite search score)**: 0.285
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.181


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":13.0,"average_failure_rate":0.16667,"average_mean_iterations":39.4359,"average_solve_count":78.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.07087,"approach_hole.approach_speed":0.11226,"descend_to_entry.descend_speed":0.08955,"insert_peg.force_threshold":17.47695,"insert_peg.insert_depth":0.07609,"insert_peg.insert_speed":0.03586},"optimized_scores":{"best_composite_score":0.28455,"best_fitness_score":0.47455,"best_task_score":0.88026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":324.0,"contact_point_centroid":[0.58957,-0.01043,0.07976],"force_p95":281.20223,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1223.11439,"mean_force":250.47839,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.45837,-0.00795,0.15838]},{"body_a":"peg_socket","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.57213,-0.00607,0.07855],"force_p95":684.07437,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1202.51693,"mean_force":223.89491,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.45826,-0.00592,0.11689]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.47169,-0.00502,0.0782],"force_p95":1064.59372,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1108.86017,"mean_force":237.2335,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.46494,-0.00498,0.08991]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.5587,0.01326,0.07935],"force_p95":559.62616,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":595.57997,"mean_force":208.04176,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.46216,-0.00525,0.09456]},{"body_a":"peg_socket","body_b":"link7","contact_count":73.0,"contact_point_centroid":[0.58939,-0.0152,0.0799],"force_p95":403.16021,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":421.60834,"mean_force":268.1515,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.49605,-0.01772,0.17943]},{"body_a":"peg_socket","body_b":"link6","contact_count":293.0,"contact_point_centroid":[0.58956,-0.01629,0.07989],"force_p95":242.35602,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.87284,"mean_force":190.24666,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.47748,-0.02106,0.19137]},{"body_a":"peg_socket","body_b":"link6","contact_count":686.0,"contact_point_centroid":[0.58958,-0.01185,0.07987],"force_p95":266.71978,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":306.16222,"mean_force":238.15787,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.45244,-0.01481,0.17467]},{"body_a":"peg_socket","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.5896,-0.02567,0.07995],"force_p95":76.02206,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.55205,"mean_force":69.05847,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.4992,-0.02051,0.17139]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.55942,-0.04709,0.0798],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.46191,-0.00515,0.09241]}],"total_contact_groups":9},"final_pose_error":0.17032,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.49909,-0.01993,0.17145],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1223.11439,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49887,-0.01067,0.16114],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08184,"object_to_goal_dist_start":0.26034,"object_z_max":0.34502,"peak_contact_force":249.07533,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":411.0,"raw_peak_contact_force":1223.11439,"subtask_id":"reach_above_hole","tcp_end":[0.46145,-0.01072,0.17524],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.497,-0.0207,0.17665],"object_pos_start":[0.49887,-0.01067,0.16114],"object_to_goal_dist_end":0.09888,"object_to_goal_dist_start":0.08184,"object_z_max":0.17661,"peak_contact_force":250.11313,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":686.0,"raw_peak_contact_force":306.16222,"subtask_id":"reach_above_hole","tcp_end":[0.46148,-0.02257,0.19494],"tcp_start":[0.46145,-0.01072,0.17524],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":422.0,"n_steps_budget":870.0,"object_pos_end":[0.53507,-0.02086,0.15493],"object_pos_start":[0.497,-0.0207,0.17665],"object_to_goal_dist_end":0.08532,"object_to_goal_dist_start":0.09888,"object_z_max":0.17665,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":366.0,"raw_peak_contact_force":421.60834,"subtask_id":"insert_peg","tcp_end":[0.49898,-0.01948,0.17212],"tcp_start":[0.46148,-0.02257,0.19494],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53521,-0.02122,0.15429],"object_pos_start":[0.53507,-0.02086,0.15493],"object_to_goal_dist_end":0.0849,"object_to_goal_dist_start":0.08532,"object_z_max":0.15493,"peak_contact_force":252.73104,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.49909,-0.01993,0.17145],"tcp_start":[0.49898,-0.01948,0.17212],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53533,-0.02167,0.15428],"object_pos_start":[0.53521,-0.02122,0.15429],"object_to_goal_dist_end":0.08506,"object_to_goal_dist_start":0.0849,"object_z_max":0.15429,"peak_contact_force":65.98682,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":305.55205,"tcp_end":[0.49922,-0.0204,0.17143],"tcp_start":[0.49909,-0.01993,0.17145],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":13.0,"average_failure_rate":0.19118,"average_mean_iterations":44.26471,"average_solve_count":68.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.17266,"approach_hole.approach_speed":0.11051,"descend_to_entry.descend_speed":0.10281,"insert_peg.force_threshold":16.13614,"insert_peg.insert_depth":0.09913,"insert_peg.insert_speed":0.03197},"optimized_scores":{"best_composite_score":0.28106,"best_fitness_score":0.47106,"best_task_score":0.88408},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.4775,-0.00676,0.07886],"force_p95":1068.7486,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1105.68442,"mean_force":259.28287,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.46737,-0.00673,0.09015]},{"body_a":"peg_socket","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.57608,-0.00792,0.07882],"force_p95":529.41975,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":880.24163,"mean_force":196.6388,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.45994,-0.00778,0.11435]},{"body_a":"peg_socket","body_b":"link6","contact_count":323.0,"contact_point_centroid":[0.59641,-0.01448,0.07976],"force_p95":282.69241,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.68919,"mean_force":247.37926,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.46055,-0.01144,0.15959]},{"body_a":"world","body_b":"link5","contact_count":199.0,"contact_point_centroid":[0.65544,0.08177,-8e-05],"force_p95":261.48465,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":518.60617,"mean_force":101.04734,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.50252,-0.02857,0.17593]},{"body_a":"peg_socket","body_b":"link6","contact_count":246.0,"contact_point_centroid":[0.59644,-0.02253,0.07993],"force_p95":342.67198,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":447.72677,"mean_force":204.33336,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.48206,-0.02884,0.19459]},{"body_a":"peg_socket","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.59642,-0.02263,0.0799],"force_p95":367.30854,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":390.93352,"mean_force":282.78828,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.4997,-0.02608,0.17886]},{"body_a":"peg_socket","body_b":"link6","contact_count":508.0,"contact_point_centroid":[0.59642,-0.01759,0.07984],"force_p95":269.76638,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":330.12666,"mean_force":237.81954,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.45746,-0.02249,0.1795]},{"body_a":"peg_socket","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.55995,0.00708,0.07868],"force_p95":100.42982,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.25225,"mean_force":22.21402,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.463,-0.00712,0.09734]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.59647,-0.02821,0.07998],"force_p95":200.79652,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":208.43495,"mean_force":98.31237,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.50231,-0.02855,0.17525]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.65517,0.08264,-0.00016],"force_p95":146.86888,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.86888,"mean_force":146.86888,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.50211,-0.02785,0.17567]}],"total_contact_groups":10},"final_pose_error":0.19769,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.50218,-0.02802,0.17551],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1105.68442,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50329,-0.01624,0.16588],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08746,"object_to_goal_dist_start":0.26034,"object_z_max":0.34516,"peak_contact_force":273.6274,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":405.0,"raw_peak_contact_force":1105.68442,"subtask_id":"reach_above_hole","tcp_end":[0.46634,-0.01628,0.1812],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50219,-0.0287,0.17984],"object_pos_start":[0.50329,-0.01624,0.16588],"object_to_goal_dist_end":0.1039,"object_to_goal_dist_start":0.08746,"object_z_max":0.17978,"peak_contact_force":280.52608,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":508.0,"raw_peak_contact_force":330.12666,"subtask_id":"reach_above_hole","tcp_end":[0.46701,-0.03074,0.19875],"tcp_start":[0.46634,-0.01628,0.1812],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":810.0,"object_pos_end":[0.53797,-0.02868,0.15796],"object_pos_start":[0.50219,-0.0287,0.17984],"object_to_goal_dist_end":0.09133,"object_to_goal_dist_start":0.1039,"object_z_max":0.17985,"peak_contact_force":664.31362,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":301.0,"raw_peak_contact_force":447.72677,"subtask_id":"insert_peg","tcp_end":[0.50211,-0.02785,0.17567],"tcp_start":[0.46701,-0.03074,0.19875],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53805,-0.02881,0.15782],"object_pos_start":[0.53797,-0.02868,0.15796],"object_to_goal_dist_end":0.09129,"object_to_goal_dist_start":0.09133,"object_z_max":0.15796,"peak_contact_force":146.86888,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":146.86888,"subtask_id":"insert_peg","tcp_end":[0.50218,-0.02802,0.17551],"tcp_start":[0.50211,-0.02785,0.17567],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53843,-0.02931,0.15829],"object_pos_start":[0.53805,-0.02881,0.15782],"object_to_goal_dist_end":0.092,"object_to_goal_dist_start":0.09129,"object_z_max":0.15867,"peak_contact_force":65.66556,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":203.0,"raw_peak_contact_force":518.60617,"tcp_end":[0.5025,-0.02861,0.17586],"tcp_start":[0.50218,-0.02802,0.17551],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.21538,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.10771,"approach_hole.approach_speed":0.11468,"descend_to_entry.descend_speed":0.09074,"insert_peg.force_threshold":13.79455,"insert_peg.insert_depth":0.07102,"insert_peg.insert_speed":0.02674},"optimized_scores":{"best_composite_score":0.31465,"best_fitness_score":0.50465,"best_task_score":0.83706},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":363.0,"contact_point_centroid":[0.52979,-0.00406,0.06884],"force_p95":283.87861,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1399.0671,"mean_force":282.50027,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.45292,3e-05,0.10489]},{"body_a":"attachment","body_b":"peg_socket","contact_count":19.0,"contact_point_centroid":[0.43848,0.01019,0.07961],"force_p95":811.15886,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":900.34677,"mean_force":89.55768,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.43569,-0.00016,0.08421]},{"body_a":"peg_socket","body_b":"link7","contact_count":645.0,"contact_point_centroid":[0.53022,-0.00401,0.06397],"force_p95":329.22568,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":361.74754,"mean_force":254.09661,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.46296,4e-05,0.11713]},{"body_a":"attachment","body_b":"peg_socket","contact_count":373.0,"contact_point_centroid":[0.53027,0.00015,0.07996],"force_p95":254.69556,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.76201,"mean_force":167.03677,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.46312,1e-05,0.11709]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53024,-0.00401,0.06423],"force_p95":237.49666,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":249.99649,"mean_force":124.99824,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.45903,-4e-05,0.11207]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53026,0.00019,0.07994],"force_p95":238.66235,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.66235,"mean_force":238.66235,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46732,3e-05,0.11766]},{"body_a":"world","body_b":"link6","contact_count":30.0,"contact_point_centroid":[0.68251,0.00064,-0.00011],"force_p95":206.49075,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.88318,"mean_force":70.31041,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.46535,7e-05,0.12034]},{"body_a":"attachment","body_b":"peg_socket","contact_count":443.0,"contact_point_centroid":[0.53026,0.00017,0.07993],"force_p95":116.37525,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":169.52759,"mean_force":110.45531,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.4637,0.0,0.11487]},{"body_a":"attachment","body_b":"peg_socket","contact_count":197.0,"contact_point_centroid":[0.53027,0.00017,0.07997],"force_p95":73.17659,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.4993,"mean_force":70.66357,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.46741,1e-05,0.11783]}],"total_contact_groups":9},"final_pose_error":0.10871,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.46735,3e-05,0.11765],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":1399.0671,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49675,0.00012,0.10297],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0232,"object_to_goal_dist_start":0.26034,"object_z_max":0.34424,"peak_contact_force":283.92585,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":382.0,"raw_peak_contact_force":1399.0671,"subtask_id":"reach_above_hole","tcp_end":[0.45753,9e-05,0.11081],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":645.0,"n_steps_budget":720.0,"object_pos_end":[0.49794,5e-05,0.10291],"object_pos_start":[0.49675,0.00012,0.10297],"object_to_goal_dist_end":0.02301,"object_to_goal_dist_start":0.0232,"object_z_max":0.10659,"peak_contact_force":190.19954,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1048.0,"raw_peak_contact_force":361.74754,"subtask_id":"reach_above_hole","tcp_end":[0.45898,-4e-05,0.11199],"tcp_start":[0.45753,9e-05,0.11081],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":458.0,"n_steps_budget":600.0,"object_pos_end":[0.50509,0.00012,0.10451],"object_pos_start":[0.49794,5e-05,0.10291],"object_to_goal_dist_end":0.02503,"object_to_goal_dist_start":0.02301,"object_z_max":0.10462,"peak_contact_force":115.83459,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":445.0,"raw_peak_contact_force":249.99649,"subtask_id":"insert_peg","tcp_end":[0.46732,3e-05,0.11766],"tcp_start":[0.45898,-4e-05,0.11199],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50513,0.00011,0.10451],"object_pos_start":[0.50509,0.00012,0.10451],"object_to_goal_dist_end":0.02504,"object_to_goal_dist_start":0.02503,"object_z_max":0.10451,"peak_contact_force":238.66235,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":238.66235,"subtask_id":"insert_peg","tcp_end":[0.46735,3e-05,0.11765],"tcp_start":[0.46732,3e-05,0.11766],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50514,9e-05,0.1047],"object_pos_start":[0.50513,0.00011,0.10451],"object_to_goal_dist_end":0.02523,"object_to_goal_dist_start":0.02504,"object_z_max":0.10469,"peak_contact_force":69.48607,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":197.0,"raw_peak_contact_force":136.4993,"tcp_end":[0.46741,0.0,0.11796],"tcp_start":[0.46735,3e-05,0.11765],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```