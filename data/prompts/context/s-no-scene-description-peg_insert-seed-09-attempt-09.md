## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → descend → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.1560 | 0.48 | ❌ rejected |
| 8 | approach → align → descend → insert → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | 0.2934 | 0.87 | ❌ rejected |
| 7 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.3292 | 0.86 | ❌ rejected |
| 6 | approach → align → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0831 | 0.57 | ❌ rejected |
| 5 | approach → align → contact → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 7 | 0.4379 | 0.82 | ❌ rejected |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.156) — your mutation base

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

- **Composite score**: 0.156
- **task_score** (E): 0.482
- **fitness_score**: 0.196  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 0.00 | 0.0676 |
| align_high | 0.00 | 1.00 | 0.1878 |
| descend_to_entry | 1.00 | 1.00 | 0.0000 |
| insert_deep | 1.00 | 1.00 | 0.0000 |
| release_peg | 1.00 | 1.00 | 0.0004 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, -0.011, 0.361) | (0.504, -0.000, 0.340)→(0.514, -0.011, 0.401) | 0.260→0.323 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_high | align | 0.00 / step_budget | (0.509, -0.011, 0.361)→(0.401, -0.017, 0.208) | (0.514, -0.011, 0.401)→(0.437, -0.016, 0.191) | 0.323→0.131 | 1.00 / 1.000 | 191.175 | 792.579 |
| descend_to_entry | descend | 1.00 / force_exceeded | (0.401, -0.017, 0.208)→(0.401, -0.017, 0.208) | (0.437, -0.016, 0.191)→(0.437, -0.016, 0.191) | 0.131→0.131 | 1.00 / 1.000 | 85.669 | 85.669 |
| insert_deep | insert | 1.00 / force_exceeded | (0.401, -0.017, 0.208)→(0.401, -0.017, 0.208) | (0.437, -0.016, 0.191)→(0.437, -0.016, 0.191) | 0.131→0.131 | 1.00 / 1.000 | 70.873 | 67.776 |
| release_peg | release | 1.00 / step_budget | (0.401, -0.017, 0.208)→(0.401, -0.017, 0.208) | (0.437, -0.016, 0.191)→(0.437, -0.016, 0.191) | 0.131→0.130 | 1.00 / 1.000 | 66.294 | 73.846 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.557
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.557
- phase_score: 0.005
- phase_breakdown.reach_above_hole_score: 0.017
- phase_breakdown.insert_peg_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.226
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.557
- **Median Q (composite search score)**: 0.182
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.285


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94253,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_high.align_speed":0.12228,"approach_high.approach_speed":0.02767,"descend_to_entry.contact_force_threshold":12.64346,"descend_to_entry.descend_speed":0.02073,"insert_deep.insert_depth":0.06769,"insert_deep.insert_force_threshold":28.85984,"insert_deep.insert_speed":0.02946},"optimized_scores":{"best_composite_score":0.18208,"best_fitness_score":0.22208,"best_task_score":0.54666},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":135.0,"contact_point_centroid":[0.58927,-0.01486,0.07895],"force_p95":315.41515,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":804.22386,"mean_force":218.39157,"phase_index":1.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.41325,-0.02034,0.19182]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58962,-0.0139,0.07999],"force_p95":89.22369,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.22369,"mean_force":89.22369,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.41729,-0.0211,0.19856]},{"body_a":"peg_socket","body_b":"link6","contact_count":200.0,"contact_point_centroid":[0.58961,-0.01342,0.07998],"force_p95":71.74794,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.96346,"mean_force":67.33343,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.41758,-0.02106,0.19832]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58962,-0.01385,0.08],"force_p95":55.09273,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.09273,"mean_force":55.09273,"phase_index":3.0,"phase_name":"insert_deep","phase_type":"insert","tcp_position_centroid":[0.4173,-0.0211,0.19852]}],"total_contact_groups":4},"final_pose_error":0.21746,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.41732,-0.02108,0.19849],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":804.22386,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.52793,-0.01417,0.401],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.32253,"object_to_goal_dist_start":0.26034,"object_z_max":0.40075,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52336,-0.01418,0.36126],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.45419,-0.01921,0.18322],"object_pos_start":[0.52793,-0.01417,0.401],"object_to_goal_dist_end":0.11456,"object_to_goal_dist_start":0.32253,"object_z_max":0.40943,"peak_contact_force":180.29599,"phase_name":"align_high","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":135.0,"raw_peak_contact_force":804.22386,"subtask_id":"reach_above_hole","tcp_end":[0.41729,-0.0211,0.19856],"tcp_start":[0.52336,-0.01418,0.36126],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4542,-0.01921,0.18319],"object_pos_start":[0.45419,-0.01921,0.18322],"object_to_goal_dist_end":0.11452,"object_to_goal_dist_start":0.11456,"object_z_max":0.18322,"peak_contact_force":89.22369,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":89.22369,"subtask_id":"insert_peg","tcp_end":[0.4173,-0.0211,0.19852],"tcp_start":[0.41729,-0.0211,0.19856],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.45422,-0.01919,0.18316],"object_pos_start":[0.4542,-0.01921,0.18319],"object_to_goal_dist_end":0.11448,"object_to_goal_dist_start":0.11452,"object_z_max":0.18319,"peak_contact_force":64.38175,"phase_name":"insert_deep","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":55.09273,"subtask_id":"insert_peg","tcp_end":[0.41732,-0.02108,0.19849],"tcp_start":[0.4173,-0.0211,0.19852],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4546,-0.01917,0.18295],"object_pos_start":[0.45422,-0.01919,0.18316],"object_to_goal_dist_end":0.11413,"object_to_goal_dist_start":0.11448,"object_z_max":0.18316,"peak_contact_force":66.4812,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":71.96346,"tcp_end":[0.4177,-0.02107,0.19826],"tcp_start":[0.41732,-0.02108,0.19849],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.19048,"average_solve_count":42.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_high.align_speed":0.10771,"approach_high.approach_speed":0.11468,"descend_to_entry.contact_force_threshold":17.8597,"descend_to_entry.descend_speed":0.01899,"insert_deep.insert_depth":0.06532,"insert_deep.insert_force_threshold":32.24586,"insert_deep.insert_speed":0.02201},"optimized_scores":{"best_composite_score":0.18589,"best_fitness_score":0.22589,"best_task_score":0.55667},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":106.0,"contact_point_centroid":[0.59603,-0.01931,0.07854],"force_p95":428.52371,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":886.87022,"mean_force":224.44668,"phase_index":1.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.41915,-0.02858,0.18694]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59646,-0.01893,0.07994],"force_p95":95.85651,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.85651,"mean_force":95.85651,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.42349,-0.02947,0.1948]},{"body_a":"peg_socket","body_b":"link6","contact_count":199.0,"contact_point_centroid":[0.59647,-0.01819,0.07998],"force_p95":72.53635,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.2649,"mean_force":67.96973,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.42381,-0.02924,0.19457]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59646,-0.01882,0.07995],"force_p95":72.97971,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.97971,"mean_force":72.97971,"phase_index":3.0,"phase_name":"insert_deep","phase_type":"insert","tcp_position_centroid":[0.42351,-0.02941,0.19475]}],"total_contact_groups":4},"final_pose_error":0.21263,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.42354,-0.02938,0.19473],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":886.87022,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":227.0,"n_steps_budget":600.0,"object_pos_end":[0.53398,-0.01967,0.40171],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.3241,"object_to_goal_dist_start":0.26034,"object_z_max":0.40146,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.52937,-0.01967,0.36198],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":223.0,"n_steps_budget":600.0,"object_pos_end":[0.46063,-0.02718,0.18013],"object_pos_start":[0.53398,-0.01967,0.40171],"object_to_goal_dist_end":0.11097,"object_to_goal_dist_start":0.3241,"object_z_max":0.41021,"peak_contact_force":179.97272,"phase_name":"align_high","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":106.0,"raw_peak_contact_force":886.87022,"subtask_id":"reach_above_hole","tcp_end":[0.42349,-0.02947,0.1948],"tcp_start":[0.52937,-0.01967,0.36198],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.46066,-0.02713,0.18009],"object_pos_start":[0.46063,-0.02718,0.18013],"object_to_goal_dist_end":0.11092,"object_to_goal_dist_start":0.11097,"object_z_max":0.18013,"peak_contact_force":95.85651,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":95.85651,"subtask_id":"insert_peg","tcp_end":[0.42351,-0.02941,0.19475],"tcp_start":[0.42349,-0.02947,0.1948],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.46069,-0.0271,0.18008],"object_pos_start":[0.46066,-0.02713,0.18009],"object_to_goal_dist_end":0.11089,"object_to_goal_dist_start":0.11092,"object_z_max":0.18009,"peak_contact_force":72.97971,"phase_name":"insert_deep","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":72.97971,"subtask_id":"insert_peg","tcp_end":[0.42354,-0.02938,0.19473],"tcp_start":[0.42351,-0.02941,0.19475],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46108,-0.02694,0.1799],"object_pos_start":[0.46069,-0.0271,0.18008],"object_to_goal_dist_end":0.11054,"object_to_goal_dist_start":0.11089,"object_z_max":0.18008,"peak_contact_force":66.21867,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":199.0,"raw_peak_contact_force":73.2649,"tcp_end":[0.42393,-0.02924,0.19453],"tcp_start":[0.42354,-0.02938,0.19473],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23364,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_high.align_speed":0.08533,"approach_high.approach_speed":0.02034,"descend_to_entry.contact_force_threshold":19.62065,"descend_to_entry.descend_speed":0.01237,"insert_deep.insert_depth":0.06378,"insert_deep.insert_force_threshold":29.63086,"insert_deep.insert_speed":0.02242},"optimized_scores":{"best_composite_score":0.10005,"best_fitness_score":0.14005,"best_task_score":0.34226},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":161.0,"contact_point_centroid":[0.52995,0.0012,0.07921],"force_p95":299.6244,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":686.64176,"mean_force":231.70984,"phase_index":1.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.35936,-0.00085,0.2275]},{"body_a":"peg_socket","body_b":"link6","contact_count":200.0,"contact_point_centroid":[0.53028,0.00116,0.07999],"force_p95":75.51928,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.30967,"mean_force":70.18863,"phase_index":4.0,"phase_name":"release_peg","phase_type":"release","tcp_position_centroid":[0.36248,-0.00086,0.23179]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.53027,0.00124,0.07996],"force_p95":75.25692,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.25692,"mean_force":75.25692,"phase_index":3.0,"phase_name":"insert_deep","phase_type":"insert","tcp_position_centroid":[0.36225,-0.00086,0.23172]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.53027,0.00124,0.07996],"force_p95":71.92687,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.92687,"mean_force":71.92687,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.36225,-0.00086,0.23172]}],"total_contact_groups":4},"final_pose_error":0.24106,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.36225,-0.00086,0.23172],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":686.64176,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.47904,-6e-05,0.40022],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.3209,"object_to_goal_dist_start":0.26034,"object_z_max":0.39993,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.47449,-7e-05,0.36048],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.39639,-0.00068,0.21088],"object_pos_start":[0.47904,-6e-05,0.40022],"object_to_goal_dist_end":0.16693,"object_to_goal_dist_start":0.3209,"object_z_max":0.40879,"peak_contact_force":213.25739,"phase_name":"align_high","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":161.0,"raw_peak_contact_force":686.64176,"subtask_id":"reach_above_hole","tcp_end":[0.36225,-0.00086,0.23172],"tcp_start":[0.47449,-7e-05,0.36048],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.39639,-0.00068,0.21088],"object_pos_start":[0.39639,-0.00068,0.21088],"object_to_goal_dist_end":0.16693,"object_to_goal_dist_start":0.16693,"object_z_max":0.21088,"peak_contact_force":71.92687,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":71.92687,"subtask_id":"insert_peg","tcp_end":[0.36225,-0.00086,0.23172],"tcp_start":[0.36225,-0.00086,0.23172],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.3964,-0.00068,0.21089],"object_pos_start":[0.39639,-0.00068,0.21088],"object_to_goal_dist_end":0.16693,"object_to_goal_dist_start":0.16693,"object_z_max":0.21088,"peak_contact_force":75.25692,"phase_name":"insert_deep","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":75.25692,"subtask_id":"insert_peg","tcp_end":[0.36225,-0.00086,0.23172],"tcp_start":[0.36225,-0.00086,0.23172],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.39674,-0.00069,0.21088],"object_pos_start":[0.3964,-0.00068,0.21089],"object_to_goal_dist_end":0.16671,"object_to_goal_dist_start":0.16693,"object_z_max":0.21097,"peak_contact_force":66.18316,"phase_name":"release_peg","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":76.30967,"tcp_end":[0.36261,-0.00087,0.23173],"tcp_start":[0.36225,-0.00086,0.23172],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```