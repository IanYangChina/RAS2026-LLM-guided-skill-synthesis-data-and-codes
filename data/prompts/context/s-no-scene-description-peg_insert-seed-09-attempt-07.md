## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3292 | 0.86 | ❌ rejected |
| 6 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0831 | 0.57 | ❌ rejected |
| 5 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.4379 | 0.82 | ❌ rejected |
| 4 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.3951 | 0.86 | ❌ rejected |
| 3 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3393 | 0.74 | ❌ rejected |

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

## Current Skill (Q=0.329) — your mutation base

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

- **Composite score**: 0.329
- **task_score** (E): 0.857
- **fitness_score**: 0.639  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 1.00 | 0.00 | 0.0599 |
| align_hole | 1.00 | 0.00 | 0.0107 |
| descend_insert | 0.00 | 0.00 | 0.1766 |
| release_peg | 1.00 | 0.67 | 0.0062 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, -0.010, 0.246) | (0.504, -0.000, 0.340)→(0.512, -0.010, 0.286) | 0.260→0.208 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 1.00 / step_budget | (0.507, -0.010, 0.246)→(0.508, -0.011, 0.236) | (0.512, -0.010, 0.286)→(0.513, -0.011, 0.276) | 0.208→0.198 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_insert | descend | 0.00 / step_budget | (0.508, -0.011, 0.236)→(0.507, -0.013, 0.060) | (0.513, -0.011, 0.276)→(0.512, -0.013, 0.099) | 0.198→0.039 | 0.00 / 0.000 | 0.000 | 0.000 |
| release_peg | release | 1.00 / step_budget | (0.507, -0.013, 0.060)→(0.503, -0.013, 0.055) | (0.512, -0.013, 0.099)→(0.508, -0.013, 0.095) | 0.039→0.037 | 0.67 / 0.667 | 43.993 | 53.427 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.877
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.877
- phase_score: 0.518
- phase_breakdown.reach_above_hole_score: 0.587
- phase_breakdown.insert_peg_score: 0.488

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.662
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.877
- **Median Q (composite search score)**: 0.349
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: descend_insert.insert_depth
- **Final σ (mean)**: 0.489


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.09629,"approach_hole.approach_speed":0.06317,"descend_insert.force_threshold":13.0756,"descend_insert.insert_depth":0.12118,"descend_insert.insert_speed":0.04547},"optimized_scores":{"best_composite_score":0.35157,"best_fitness_score":0.66157,"best_task_score":0.87707},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":130.0,"contact_point_centroid":[0.53309,-0.01597,0.04995],"force_p95":69.08226,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.46335,"mean_force":58.89813,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.51825,-0.01591,0.0521]}],"total_contact_groups":1},"final_pose_error":0.0986,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52258,-0.01594,0.05715],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":69.46335,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":128.0,"n_steps_budget":780.0,"object_pos_end":[0.52368,-0.01205,0.28548],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20719,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.51914,-0.01204,0.24574],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":45.0,"n_steps_budget":600.0,"object_pos_end":[0.52668,-0.01419,0.27524],"object_pos_start":[0.52368,-0.01205,0.28548],"object_to_goal_dist_end":0.19757,"object_to_goal_dist_start":0.20719,"object_z_max":0.28548,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52182,-0.01417,0.23554],"tcp_start":[0.51914,-0.01204,0.24574],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52793,-0.01596,0.0968],"object_pos_start":[0.52668,-0.01419,0.27524],"object_to_goal_dist_end":0.03629,"object_to_goal_dist_start":0.19757,"object_z_max":0.27524,"peak_contact_force":0.0,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.52258,-0.01594,0.05715],"tcp_start":[0.52182,-0.01417,0.23554],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52413,-0.01594,0.09174],"object_pos_start":[0.52793,-0.01596,0.0968],"object_to_goal_dist_end":0.03121,"object_to_goal_dist_start":0.03629,"object_z_max":0.0968,"peak_contact_force":55.55266,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":130.0,"raw_peak_contact_force":69.46335,"tcp_end":[0.5183,-0.01591,0.05217],"tcp_start":[0.52258,-0.01594,0.05715],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99167,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.04678,"approach_hole.approach_speed":0.0796,"descend_insert.force_threshold":27.80358,"descend_insert.insert_depth":0.13032,"descend_insert.insert_speed":0.02976},"optimized_scores":{"best_composite_score":0.28725,"best_fitness_score":0.59725,"best_task_score":0.83761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":173.0,"contact_point_centroid":[0.54192,-0.02201,0.04996],"force_p95":89.46722,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.81677,"mean_force":75.82544,"phase_index":3.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.52707,-0.02192,0.05203]}],"total_contact_groups":1},"final_pose_error":0.105,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.5291,-0.02195,0.05441],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":90.81677,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":135.0,"n_steps_budget":660.0,"object_pos_end":[0.52914,-0.01686,0.2844],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20715,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52461,-0.01685,0.24466],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":600.0,"object_pos_end":[0.53308,-0.01989,0.27378],"object_pos_start":[0.52914,-0.01686,0.2844],"object_to_goal_dist_end":0.19759,"object_to_goal_dist_start":0.20715,"object_z_max":0.2844,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52821,-0.01987,0.23408],"tcp_start":[0.52461,-0.01685,0.24466],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53447,-0.02198,0.09405],"object_pos_start":[0.53308,-0.01989,0.27378],"object_to_goal_dist_end":0.04323,"object_to_goal_dist_start":0.19759,"object_z_max":0.27378,"peak_contact_force":0.0,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.5291,-0.02195,0.05441],"tcp_start":[0.52821,-0.01987,0.23408],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53274,-0.02196,0.09167],"object_pos_start":[0.53447,-0.02198,0.09405],"object_to_goal_dist_end":0.04112,"object_to_goal_dist_start":0.04323,"object_z_max":0.09405,"peak_contact_force":76.42769,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":173.0,"raw_peak_contact_force":90.81677,"tcp_end":[0.52716,-0.02193,0.05206],"tcp_start":[0.5291,-0.02195,0.05441],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97248,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_speed":0.11087,"approach_hole.approach_speed":0.19143,"descend_insert.force_threshold":10.03862,"descend_insert.insert_depth":0.15,"descend_insert.insert_speed":0.03591},"optimized_scores":{"best_composite_score":0.3488,"best_fitness_score":0.6588,"best_task_score":0.85712},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.13757,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.46826,-0.00011,0.06756],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":112.0,"n_steps_budget":600.0,"object_pos_end":[0.4825,-5e-05,0.28764],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20837,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47801,-6e-05,0.24789],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":36.0,"n_steps_budget":600.0,"object_pos_end":[0.47865,-6e-05,0.27884],"object_pos_start":[0.4825,-5e-05,0.28764],"object_to_goal_dist_end":0.19999,"object_to_goal_dist_start":0.20837,"object_z_max":0.28764,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47391,-7e-05,0.23913],"tcp_start":[0.47801,-6e-05,0.24789],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47343,-0.0001,0.10723],"object_pos_start":[0.47865,-6e-05,0.27884],"object_to_goal_dist_end":0.03805,"object_to_goal_dist_start":0.19999,"object_z_max":0.27884,"peak_contact_force":0.0,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_peg","tcp_end":[0.46826,-0.00011,0.06756],"tcp_start":[0.47391,-7e-05,0.23913],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46799,-0.00018,0.10051],"object_pos_start":[0.47343,-0.0001,0.10723],"object_to_goal_dist_end":0.03802,"object_to_goal_dist_start":0.03805,"object_z_max":0.10723,"peak_contact_force":0.0,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46212,-0.0002,0.06094],"tcp_start":[0.46826,-0.00011,0.06756],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```