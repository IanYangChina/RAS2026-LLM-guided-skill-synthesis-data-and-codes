## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1831 | 0.85 | ❌ rejected |
| 10 | approach → insert | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 9 | -0.0302 | 0.85 | ❌ rejected |
| 9 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1827 | 0.85 | ❌ rejected |
| 8 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 14 | -0.1147 | 0.86 | ❌ rejected |
| 7 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2109 | 0.83 | ❌ rejected |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.183) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_above_socket
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: reach_socket_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.2
- id: insertion_depth
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_to_socket
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
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
    approach_arc:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tol:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_above_socket
- id: descend_to_entry
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_socket_entry
- id: insert_peg
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.055
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    force_limit:
      type: scalar
      range:
      - 40.0
      - 80.0
      default: 50.0
      binds_to:
      - path: guards.force_limit_guard.threshold
        mode: replace
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insert_tol:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.006
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_offset_y:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.006
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.006
    - 0.006
    - 0.0
  subtask_id: insertion_depth

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_arc: status=consumed; consumers=generator.arc_height (replace)
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **insert_peg** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.055, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_limit_guard.threshold (replace)
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insert_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.006, 0.006, 0.0]

## Design Metrics

- **Composite score**: 0.183
- **task_score** (E): 0.852
- **fitness_score**: 0.380  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 0.33 | 1.00 | 0.1123 |
| descend_to_entry | 1.00 | 1.00 | 0.0000 |
| insert_peg | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.468, -0.006, 0.197) | (0.504, -0.000, 0.340)→(0.502, -0.005, 0.176) | 0.260→0.100 | 1.00 / 1.000 | 277.829 | 955.010 |
| descend_to_entry | descend | 1.00 / force_exceeded | (0.468, -0.006, 0.197)→(0.468, -0.006, 0.197) | (0.502, -0.005, 0.176)→(0.502, -0.005, 0.176) | 0.100→0.100 | 1.00 / 1.000 | 119.819 | 129.295 |
| insert_peg | insert | 0.00 / guard_failure | (0.468, -0.006, 0.197)→(0.468, -0.006, 0.197) | (0.502, -0.005, 0.176)→(0.502, -0.005, 0.176) | 0.100→0.100 | 1.00 / 1.000 | 107.561 | 107.561 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.825
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.825
- phase_score: 0.094
- phase_breakdown.reach_above_socket_score: 0.273
- phase_breakdown.insertion_depth_score: 0.000
- phase_breakdown.reach_socket_entry_score: 0.061

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.386
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.867
- **Median Q (composite search score)**: 0.182
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.366


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6af64227b04102c511381eb024ec48290b429fbc7fcb6f0c4b42c66d0a974e9f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5cd76595591baa0f9f71873dced18f865534f529ba8f9daf4a3973579a78fb36`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.7,"average_solve_count":40.0,"average_success_count":40.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_arc":0.16067,"approach_high.approach_height":0.18684,"approach_high.approach_speed":0.05073,"approach_high.approach_tol":0.01458,"descend_to_entry.descend_speed":0.02738,"descend_to_entry.force_threshold":4.52476,"insert_peg.force_limit_guard_threshold":44.16527,"insert_peg.insert_depth":0.06775,"insert_peg.insert_speed":0.01384,"insert_peg.insert_tol":0.02242},"optimized_scores":{"best_composite_score":0.18961,"best_fitness_score":0.38627,"best_task_score":0.82463},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.44798,0.00941,0.07897],"force_p95":569.11831,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1034.76057,"mean_force":103.47606,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44385,0.00937,0.09234]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.4565,0.00897,0.07962],"force_p95":702.47432,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":936.63242,"mean_force":156.1054,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44704,0.0093,0.09196]},{"body_a":"peg_socket","body_b":"link7","contact_count":190.0,"contact_point_centroid":[0.54475,0.01909,0.07945],"force_p95":453.60384,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":929.24199,"mean_force":297.8678,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.43989,0.01479,0.15362]},{"body_a":"peg_socket","body_b":"link6","contact_count":695.0,"contact_point_centroid":[0.54611,0.02705,0.07992],"force_p95":322.51134,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":333.11797,"mean_force":305.65351,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4553,0.02693,0.20052]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54613,0.02981,0.07997],"force_p95":83.25656,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.25656,"mean_force":83.25656,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.4672,0.03145,0.21334]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54612,0.02984,0.07996],"force_p95":72.99299,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.99299,"mean_force":72.99299,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46719,0.03147,0.21333]}],"total_contact_groups":6},"final_pose_error":0.25691,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.4672,0.03145,0.21335],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1034.76057,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49646,0.03207,0.18607],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11087,"object_to_goal_dist_start":0.26034,"object_z_max":0.34432,"peak_contact_force":322.66054,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":901.0,"raw_peak_contact_force":1034.76057,"subtask_id":"reach_above_socket","tcp_end":[0.46719,0.03147,0.21333],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49647,0.03205,0.18608],"object_pos_start":[0.49646,0.03207,0.18607],"object_to_goal_dist_end":0.11088,"object_to_goal_dist_start":0.11087,"object_z_max":0.18607,"peak_contact_force":72.99299,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":72.99299,"subtask_id":"reach_socket_entry","tcp_end":[0.4672,0.03145,0.21334],"tcp_start":[0.46719,0.03147,0.21333],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49647,0.03204,0.18609],"object_pos_start":[0.49647,0.03205,0.18608],"object_to_goal_dist_end":0.11088,"object_to_goal_dist_start":0.11088,"object_z_max":0.18608,"peak_contact_force":83.25656,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":83.25656,"subtask_id":"insertion_depth","tcp_end":[0.4672,0.03145,0.21335],"tcp_start":[0.4672,0.03145,0.21334],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.8,"average_solve_count":30.0,"average_success_count":30.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_arc":0.0921,"approach_high.approach_height":0.20624,"approach_high.approach_speed":0.06061,"approach_high.approach_tol":0.01985,"descend_to_entry.descend_speed":0.0165,"descend_to_entry.force_threshold":5.22916,"insert_peg.force_limit_guard_threshold":37.82695,"insert_peg.insert_depth":0.08034,"insert_peg.insert_speed":0.00856,"insert_peg.insert_tol":0.01153},"optimized_scores":{"best_composite_score":0.17724,"best_fitness_score":0.37391,"best_task_score":0.86588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.47056,-0.00764,0.0792],"force_p95":1017.98453,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1052.15107,"mean_force":250.83543,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4624,-0.00761,0.09155]},{"body_a":"peg_socket","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.56947,-0.00936,0.07871],"force_p95":676.9988,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":943.62367,"mean_force":219.42466,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45556,-0.00871,0.11469]},{"body_a":"peg_socket","body_b":"link6","contact_count":536.0,"contact_point_centroid":[0.58958,-0.01507,0.07983],"force_p95":270.82085,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":539.55273,"mean_force":245.53013,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4575,-0.0129,0.16369]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58962,-0.01418,0.08],"force_p95":106.93173,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.93173,"mean_force":106.93173,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46228,-0.01769,0.18049]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58962,-0.01416,0.08],"force_p95":98.97649,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.97649,"mean_force":98.97649,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.4623,-0.01767,0.18048]},{"body_a":"peg_socket","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.55414,0.01319,0.07954],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45758,-0.00793,0.09578]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.55438,-0.04713,0.07959],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45728,-0.00795,0.09606]}],"total_contact_groups":7},"final_pose_error":0.24522,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.4623,-0.01766,0.18046],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1052.15107,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":669.0,"n_steps_budget":810.0,"object_pos_end":[0.49922,-0.01705,0.16514],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08684,"object_to_goal_dist_start":0.26034,"object_z_max":0.34506,"peak_contact_force":245.20285,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":614.0,"raw_peak_contact_force":1052.15107,"subtask_id":"reach_above_socket","tcp_end":[0.46228,-0.01769,0.18049],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49923,-0.01703,0.16513],"object_pos_start":[0.49922,-0.01705,0.16514],"object_to_goal_dist_end":0.08682,"object_to_goal_dist_start":0.08684,"object_z_max":0.16514,"peak_contact_force":78.50584,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":106.93173,"subtask_id":"reach_socket_entry","tcp_end":[0.4623,-0.01767,0.18048],"tcp_start":[0.46228,-0.01769,0.18049],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49924,-0.01702,0.16511],"object_pos_start":[0.49923,-0.01703,0.16513],"object_to_goal_dist_end":0.0868,"object_to_goal_dist_start":0.08682,"object_z_max":0.16513,"peak_contact_force":98.97649,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":98.97649,"subtask_id":"insertion_depth","tcp_end":[0.4623,-0.01766,0.18046],"tcp_start":[0.4623,-0.01767,0.18048],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.16667,"average_solve_count":30.0,"average_success_count":30.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_arc":0.11797,"approach_high.approach_height":0.18587,"approach_high.approach_speed":0.07556,"approach_high.approach_tol":0.01262,"descend_to_entry.descend_speed":0.00775,"descend_to_entry.force_threshold":6.14411,"insert_peg.force_limit_guard_threshold":42.89071,"insert_peg.insert_depth":0.07904,"insert_peg.insert_speed":0.0109,"insert_peg.insert_tol":0.01996},"optimized_scores":{"best_composite_score":0.18232,"best_fitness_score":0.37898,"best_task_score":0.86652},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.47651,-0.00864,0.07992],"force_p95":777.18926,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":778.11745,"mean_force":768.83556,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46782,-0.00863,0.09262]},{"body_a":"peg_socket","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.54758,0.00733,0.07858],"force_p95":657.69354,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":715.38931,"mean_force":120.09672,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45208,-0.0097,0.10106]},{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.56672,-0.011,0.07844],"force_p95":587.00214,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":648.38175,"mean_force":104.46406,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4522,-0.00987,0.10627]},{"body_a":"peg_socket","body_b":"link6","contact_count":614.0,"contact_point_centroid":[0.59617,-0.01922,0.07984],"force_p95":283.30254,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":361.84104,"mean_force":248.56604,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46323,-0.01843,0.16901]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59636,-0.02281,0.07979],"force_p95":207.95927,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.95927,"mean_force":207.95927,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.47568,-0.03098,0.19614]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59637,-0.02282,0.07981],"force_p95":140.45065,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.45065,"mean_force":140.45065,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.4757,-0.03095,0.19613]},{"body_a":"peg_socket","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54753,-0.0535,0.07937],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45127,-0.00964,0.0982]}],"total_contact_groups":7},"final_pose_error":0.25762,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.47573,-0.03102,0.19619],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":778.11745,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":727.0,"n_steps_budget":840.0,"object_pos_end":[0.51067,-0.02891,0.17686],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10165,"object_to_goal_dist_start":0.26034,"object_z_max":0.34505,"peak_contact_force":265.62381,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":681.0,"raw_peak_contact_force":778.11745,"subtask_id":"reach_above_socket","tcp_end":[0.47568,-0.03098,0.19614],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51069,-0.02889,0.17686],"object_pos_start":[0.51067,-0.02891,0.17686],"object_to_goal_dist_end":0.10164,"object_to_goal_dist_start":0.10165,"object_z_max":0.17686,"peak_contact_force":207.95927,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":207.95927,"subtask_id":"reach_socket_entry","tcp_end":[0.4757,-0.03095,0.19613],"tcp_start":[0.47568,-0.03098,0.19614],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51072,-0.02896,0.17693],"object_pos_start":[0.51069,-0.02889,0.17686],"object_to_goal_dist_end":0.10173,"object_to_goal_dist_start":0.10164,"object_z_max":0.17686,"peak_contact_force":140.45065,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":140.45065,"subtask_id":"insertion_depth","tcp_end":[0.47573,-0.03102,0.19619],"tcp_start":[0.4757,-0.03095,0.19613],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```