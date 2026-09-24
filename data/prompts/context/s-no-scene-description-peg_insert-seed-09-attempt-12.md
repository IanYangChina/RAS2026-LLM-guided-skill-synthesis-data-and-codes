## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2520 | 0.86 | ❌ rejected |
| 11 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5027 | 0.91 | ❌ rejected |
| 10 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.5028 | 0.91 | ✅ accepted |
| 9 | approach → align → descend → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.1560 | 0.48 | ❌ rejected |
| 8 | approach → align → descend → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | 0.2934 | 0.87 | ❌ rejected |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.252) — your mutation base

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

- **Composite score**: 0.252
- **task_score** (E): 0.856
- **fitness_score**: 0.512  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 1.00 | 0.00 | 0.0220 |
| align_hole | 0.00 | 1.00 | 0.1758 |
| descend_insert | 0.00 | 0.67 | 0.0000 |
| release_peg | 1.00 | 1.00 | 0.0005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, -0.007, 0.287) | (0.504, -0.000, 0.340)→(0.511, -0.007, 0.327) | 0.260→0.248 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.00 / step_budget | (0.507, -0.007, 0.287)→(0.480, -0.020, 0.117) | (0.511, -0.007, 0.327)→(0.518, -0.018, 0.119) | 0.248→0.066 | 1.00 / 1.000 | 233.140 | 2205.467 |
| descend_insert | insert | 0.00 / guard_failure | (0.480, -0.020, 0.117)→(0.480, -0.020, 0.117) | (0.518, -0.018, 0.119)→(0.518, -0.018, 0.119) | 0.066→0.066 | 0.67 / 0.667 | 55.022 | 114.958 |
| release_peg | release | 1.00 / step_budget | (0.480, -0.020, 0.117)→(0.480, -0.020, 0.117) | (0.518, -0.018, 0.119)→(0.518, -0.018, 0.119) | 0.066→0.066 | 1.00 / 1.000 | 64.133 | 75.633 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.921
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.921
- phase_score: 0.430
- phase_breakdown.reach_above_hole_score: 0.022
- phase_breakdown.insert_peg_score: 0.605

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.626
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.921
- **Median Q (composite search score)**: 0.282
- **K-run variance**: 0.0116
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.3
- **Final σ (mean)**: 0.237


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.13333,"average_solve_count":45.0,"average_success_count":45.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.05953,"approach_hole.approach_speed":0.17607,"descend_insert.insert_depth":0.10804,"descend_insert.insert_speed":0.01629},"optimized_scores":{"best_composite_score":0.36624,"best_fitness_score":0.62624,"best_task_score":0.92076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":167.0,"contact_point_centroid":[0.58931,-0.01999,0.07949],"force_p95":492.47152,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1256.35851,"mean_force":270.10229,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50125,-0.02053,0.08838]},{"body_a":"attachment","body_b":"peg_socket","contact_count":24.0,"contact_point_centroid":[0.49669,-0.00392,0.07871],"force_p95":978.1893,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1094.48093,"mean_force":392.3009,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49661,-0.01754,0.07249]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.58949,-0.02056,0.07983],"force_p95":98.85536,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.38259,"mean_force":73.85931,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"insert","tcp_position_centroid":[0.50115,-0.02266,0.09085]},{"body_a":"peg_socket","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.5896,-0.01859,0.07998],"force_p95":73.32895,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.6564,"mean_force":66.21875,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.50144,-0.02252,0.09111]}],"total_contact_groups":4},"final_pose_error":0.12244,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.50116,-0.02264,0.09091],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1256.35851,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":56.0,"n_steps_budget":600.0,"object_pos_end":[0.51797,-0.00828,0.32702],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.24781,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.51357,-0.00828,0.28726],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.53976,-0.02054,0.10109],"object_pos_start":[0.51797,-0.00828,0.32702],"object_to_goal_dist_end":0.04947,"object_to_goal_dist_start":0.24781,"object_z_max":0.32702,"peak_contact_force":222.23333,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":191.0,"raw_peak_contact_force":1256.35851,"subtask_id":"reach_above_hole","tcp_end":[0.50117,-0.02268,0.0908],"tcp_start":[0.51357,-0.00828,0.28726],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.53974,-0.02053,0.10113],"object_pos_start":[0.53976,-0.02054,0.10109],"object_to_goal_dist_end":0.04947,"object_to_goal_dist_start":0.04947,"object_z_max":0.10117,"peak_contact_force":79.97024,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":102.38259,"subtask_id":"insert_peg","tcp_end":[0.50116,-0.02264,0.09091],"tcp_start":[0.50115,-0.02265,0.09089],"tcp_to_object_dist_end":0.03997,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54017,-0.02032,0.1013],"object_pos_start":[0.53976,-0.0205,0.10118],"object_to_goal_dist_end":0.0498,"object_to_goal_dist_start":0.0495,"object_z_max":0.10144,"peak_contact_force":64.07926,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":77.6564,"tcp_end":[0.50157,-0.02248,0.09103],"tcp_start":[0.50116,-0.02264,0.09091],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.38636,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.06562,"approach_hole.approach_speed":0.10535,"descend_insert.insert_depth":0.12753,"descend_insert.insert_speed":0.0265},"optimized_scores":{"best_composite_score":0.2818,"best_fitness_score":0.5418,"best_task_score":0.85622},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.56649,-0.02463,0.07999],"force_p95":4334.9839,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4347.93746,"mean_force":4218.40183,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50364,-0.02913,0.06694]},{"body_a":"attachment","body_b":"peg_socket","contact_count":26.0,"contact_point_centroid":[0.50397,-0.01832,0.07902],"force_p95":3304.74734,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4308.2493,"mean_force":685.69333,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50623,-0.02965,0.06992]},{"body_a":"peg_socket","body_b":"link7","contact_count":136.0,"contact_point_centroid":[0.59609,-0.02572,0.07937],"force_p95":820.28167,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1326.03397,"mean_force":282.71981,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50998,-0.03311,0.07999]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.59646,-0.02615,0.07998],"force_p95":148.69839,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.41964,"mean_force":111.78829,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"insert","tcp_position_centroid":[0.51145,-0.03626,0.08437]},{"body_a":"peg_socket","body_b":"link7","contact_count":199.0,"contact_point_centroid":[0.59646,-0.02357,0.07998],"force_p95":65.33166,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.55464,"mean_force":63.01184,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51177,-0.03589,0.08405]}],"total_contact_groups":5},"final_pose_error":0.13479,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.51156,-0.03606,0.08432],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":4347.93746,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":76.0,"n_steps_budget":600.0,"object_pos_end":[0.52442,-0.0135,0.32449],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.24608,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.51995,-0.01349,0.28474],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":223.0,"n_steps_budget":600.0,"object_pos_end":[0.54926,-0.03223,0.09658],"object_pos_start":[0.52442,-0.0135,0.32449],"object_to_goal_dist_end":0.06116,"object_to_goal_dist_start":0.24608,"object_z_max":0.32449,"peak_contact_force":218.77375,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":164.0,"raw_peak_contact_force":4347.93746,"subtask_id":"reach_above_hole","tcp_end":[0.51138,-0.03635,0.0844],"tcp_start":[0.51995,-0.01349,0.28474],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.54932,-0.03214,0.09657],"object_pos_start":[0.54926,-0.03223,0.09658],"object_to_goal_dist_end":0.06116,"object_to_goal_dist_start":0.06116,"object_z_max":0.09658,"peak_contact_force":0.0,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":154.41964,"subtask_id":"insert_peg","tcp_end":[0.51156,-0.03606,0.08432],"tcp_start":[0.51155,-0.03611,0.08434],"tcp_to_object_dist_end":0.03989,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54978,-0.03176,0.09615],"object_pos_start":[0.54942,-0.03195,0.09654],"object_to_goal_dist_end":0.06122,"object_to_goal_dist_start":0.06113,"object_z_max":0.09654,"peak_contact_force":61.78052,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":199.0,"raw_peak_contact_force":65.55464,"tcp_end":[0.51192,-0.0359,0.08393],"tcp_start":[0.51156,-0.03606,0.08432],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.06818,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.11299,"approach_hole.approach_speed":0.13115,"descend_insert.insert_depth":0.08899,"descend_insert.insert_speed":0.03234},"optimized_scores":{"best_composite_score":0.10791,"best_fitness_score":0.36791,"best_task_score":0.79006},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.43225,0.0011,0.07801],"force_p95":942.90529,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1012.10576,"mean_force":146.83672,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.428,-0.00034,0.08992]},{"body_a":"peg_socket","body_b":"link7","contact_count":293.0,"contact_point_centroid":[0.52943,0.00278,0.07962],"force_p95":391.58059,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":945.54976,"mean_force":276.93809,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.42586,-0.00049,0.16198]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53028,0.00416,0.07998],"force_p95":88.02644,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.07279,"mean_force":86.86701,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"insert","tcp_position_centroid":[0.42752,-0.00051,0.17662]},{"body_a":"peg_socket","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.53028,0.00418,0.07998],"force_p95":77.47128,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.68657,"mean_force":69.1226,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.42768,-0.00052,0.17692]}],"total_contact_groups":4},"final_pose_error":0.19051,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.42751,-0.00051,0.17666],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":1012.10576,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":40.0,"n_steps_budget":600.0,"object_pos_end":[0.49164,-5e-05,0.32977],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.24991,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.4873,-6e-05,0.29001],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.46373,-0.00045,0.15961],"object_pos_start":[0.49164,-5e-05,0.32977],"object_to_goal_dist_end":0.08748,"object_to_goal_dist_start":0.24991,"object_z_max":0.32977,"peak_contact_force":258.41195,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":306.0,"raw_peak_contact_force":1012.10576,"subtask_id":"reach_above_hole","tcp_end":[0.42752,-0.00051,0.1766],"tcp_start":[0.4873,-6e-05,0.29001],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.46373,-0.00045,0.15962],"object_pos_start":[0.46373,-0.00045,0.15961],"object_to_goal_dist_end":0.0875,"object_to_goal_dist_start":0.08748,"object_z_max":0.15965,"peak_contact_force":85.09666,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":88.07279,"subtask_id":"insert_peg","tcp_end":[0.42751,-0.00051,0.17666],"tcp_start":[0.42751,-0.00051,0.17664],"tcp_to_object_dist_end":0.04002,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46395,-0.00046,0.15986],"object_pos_start":[0.46372,-0.00045,0.15966],"object_to_goal_dist_end":0.08762,"object_to_goal_dist_start":0.08753,"object_z_max":0.15988,"peak_contact_force":66.54021,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":83.68657,"tcp_end":[0.42779,-0.00052,0.17696],"tcp_start":[0.42751,-0.00051,0.17666],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```