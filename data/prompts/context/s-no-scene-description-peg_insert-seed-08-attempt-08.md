## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 14 | -0.1147 | 0.86 | ❌ rejected |
| 7 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2109 | 0.83 | ❌ rejected |
| 6 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 12 | 0.1236 | 0.86 | ✅ accepted |
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1338 | 0.86 | ✅ accepted |
| 4 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2426 | 0.86 | ✅ accepted |

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

## Current Skill (Q=-0.115) — your mutation base

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

- **Composite score**: -0.115
- **task_score** (E): 0.859
- **fitness_score**: 0.504  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_socket | 0.67 | 0.33 | 0.0222 |
| descend_to_entry | 0.33 | 0.33 | 0.1239 |
| insert_peg | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_socket | approach | 0.67 / step_budget | (0.487, 0.003, 0.230)→(0.508, 0.001, 0.234) | (0.504, -0.000, 0.340)→(0.526, 0.001, 0.266) | 0.260→0.188 | 0.33 / 0.333 | 200.189 | 350.945 |
| descend_to_entry | descend | 0.33 / step_budget | (0.508, 0.001, 0.234)→(0.505, -0.006, 0.110) | (0.525, 0.001, 0.265)→(0.523, -0.006, 0.141) | 0.187→0.068 | 0.33 / 0.333 | 273.338 | 273.338 |
| insert_peg | insert | 0.00 / guard_failure | (0.503, -0.008, 0.064)→(0.503, -0.008, 0.064) | (0.523, -0.006, 0.141)→(0.522, -0.008, 0.095) | 0.068→0.034 | 1.00 / 1.333 | 50.718 | 399.502 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.855
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.855
- phase_score: 0.078
- phase_breakdown.reach_above_socket_score: 0.058
- phase_breakdown.insertion_depth_score: 0.031
- phase_breakdown.reach_socket_entry_score: 0.222

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.578
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.879
- **Median Q (composite search score)**: -0.152
- **K-run variance**: 0.0059
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.294


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.28571,"average_solve_count":14.0,"average_success_count":14.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_force_guard":32.01074,"approach_to_socket.approach_height":0.16384,"approach_to_socket.approach_speed":0.09917,"approach_to_socket.approach_tol":0.02284,"approach_to_socket.retry_offset_x":0.00991,"approach_to_socket.retry_offset_y":0.00466,"descend_to_entry.descend_speed":0.01643,"descend_to_entry.force_threshold":9.13351,"insert_peg.force_limit":42.91638,"insert_peg.insert_depth":0.04821,"insert_peg.insert_speed":0.0093,"insert_peg.insert_tol":0.02221,"insert_peg.retry_offset_x":0.00742,"insert_peg.retry_offset_y":0.00527},"optimized_scores":{"best_composite_score":-0.00805,"best_fitness_score":0.38862,"best_task_score":0.85512},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.46952,0.00821,0.07856],"force_p95":1025.86476,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1052.83627,"mean_force":812.1748,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.46362,0.00823,0.09092]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.46519,0.00841,0.07727],"force_p95":820.0141,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":820.0141,"mean_force":820.0141,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.45979,0.00838,0.08853]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.46268,0.00821,0.07671],"force_p95":703.86142,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":713.03992,"mean_force":627.26543,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.45771,0.00834,0.08757]}],"total_contact_groups":3},"final_pose_error":0.11851,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.45632,0.0083,0.08729],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1052.83627,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":89.0,"n_steps_budget":780.0,"object_pos_end":[0.50019,0.00839,0.1065],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0278,"object_to_goal_dist_start":0.26034,"object_z_max":0.3445,"peak_contact_force":600.56703,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":1052.83627,"subtask_id":"reach_above_socket","tcp_end":[0.45979,0.00838,0.08853],"tcp_start":[0.46136,0.0083,0.08946],"tcp_to_object_dist_end":0.04422,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49612,0.00854,0.1017],"object_pos_start":[0.4971,0.00854,0.10295],"object_to_goal_dist_end":0.02364,"object_to_goal_dist_start":0.02466,"object_z_max":0.10295,"peak_contact_force":820.0141,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":820.0141,"subtask_id":"reach_socket_entry","tcp_end":[0.45858,0.00836,0.08789],"tcp_start":[0.45979,0.00838,0.08853],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49539,0.00852,0.10074],"object_pos_start":[0.49612,0.00854,0.1017],"object_to_goal_dist_end":0.02289,"object_to_goal_dist_start":0.02364,"object_z_max":0.1017,"peak_contact_force":0.7979,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":713.03992,"subtask_id":"insertion_depth","tcp_end":[0.45632,0.0083,0.08729],"tcp_start":[0.45691,0.00832,0.08731],"tcp_to_object_dist_end":0.04132,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38824,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_force_guard":18.35664,"approach_to_socket.approach_height":0.28528,"approach_to_socket.approach_speed":0.04395,"approach_to_socket.approach_tol":0.02571,"approach_to_socket.retry_offset_x":0.00743,"approach_to_socket.retry_offset_y":0.00574,"descend_to_entry.descend_speed":0.01972,"descend_to_entry.force_threshold":10.03781,"insert_peg.force_limit":60.08474,"insert_peg.insert_depth":0.05823,"insert_peg.insert_speed":0.01579,"insert_peg.insert_tol":0.0161,"insert_peg.retry_offset_x":0.00406,"insert_peg.retry_offset_y":0.00786},"optimized_scores":{"best_composite_score":-0.15188,"best_fitness_score":0.57812,"best_task_score":0.87889},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53822,-0.01362,0.04972],"force_p95":234.52602,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":248.31485,"mean_force":144.70684,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52352,-0.01389,0.05243]}],"total_contact_groups":1},"final_pose_error":0.08553,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52361,-0.01391,0.05203],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":248.31485,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.53576,-0.00196,0.34563],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.26803,"object_to_goal_dist_start":0.26034,"object_z_max":0.34534,"peak_contact_force":0.0,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_socket","tcp_end":[0.52873,-0.00213,0.30625],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53315,-0.01158,0.15895],"object_pos_start":[0.53576,-0.00196,0.34563],"object_to_goal_dist_end":0.0864,"object_to_goal_dist_start":0.26803,"object_z_max":0.34586,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52563,-0.01174,0.11966],"tcp_start":[0.52873,-0.00213,0.30625],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.5315,-0.01374,0.09158],"object_pos_start":[0.53315,-0.01158,0.15895],"object_to_goal_dist_end":0.03626,"object_to_goal_dist_start":0.0864,"object_z_max":0.15895,"peak_contact_force":75.37911,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":248.31485,"subtask_id":"insertion_depth","tcp_end":[0.52361,-0.01391,0.05203],"tcp_start":[0.52357,-0.0139,0.05216],"tcp_to_object_dist_end":0.04033,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63522,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_force_guard":27.91896,"approach_to_socket.approach_height":0.28348,"approach_to_socket.approach_speed":0.06008,"approach_to_socket.approach_tol":0.01311,"approach_to_socket.retry_offset_x":0.01072,"approach_to_socket.retry_offset_y":0.01182,"descend_to_entry.descend_speed":0.01812,"descend_to_entry.force_threshold":9.85654,"insert_peg.force_limit":49.04624,"insert_peg.insert_depth":0.0867,"insert_peg.insert_speed":0.01889,"insert_peg.insert_tol":0.01571,"insert_peg.retry_offset_x":0.00717,"insert_peg.retry_offset_y":0.00665},"optimized_scores":{"best_composite_score":-0.18409,"best_fitness_score":0.54591,"best_task_score":0.84389},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.54442,-0.01823,0.04983],"force_p95":224.63209,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.15048,"mean_force":141.69807,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52977,-0.01862,0.05285]}],"total_contact_groups":1},"final_pose_error":0.11444,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.52987,-0.01865,0.05245],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":237.15048,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":22.0,"n_steps_budget":600.0,"object_pos_end":[0.54175,-0.00341,0.34629],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.26957,"object_to_goal_dist_start":0.26034,"object_z_max":0.34617,"peak_contact_force":0.0,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_socket","tcp_end":[0.53421,-0.00367,0.30701],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54,-0.01581,0.16307],"object_pos_start":[0.54175,-0.00341,0.34629],"object_to_goal_dist_end":0.09355,"object_to_goal_dist_start":0.26957,"object_z_max":0.34629,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.53197,-0.01606,0.12389],"tcp_start":[0.53421,-0.00367,0.30701],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.53828,-0.01838,0.0919],"object_pos_start":[0.54,-0.01581,0.16307],"object_to_goal_dist_end":0.0441,"object_to_goal_dist_start":0.09355,"object_z_max":0.16307,"peak_contact_force":75.97711,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":237.15048,"subtask_id":"insertion_depth","tcp_end":[0.52987,-0.01865,0.05245],"tcp_start":[0.52982,-0.01863,0.05259],"tcp_to_object_dist_end":0.04034,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```