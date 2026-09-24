## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0451 | 0.84 | ❌ rejected |
| 11 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1831 | 0.85 | ❌ rejected |
| 10 | approach → insert | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 9 | -0.0302 | 0.85 | ❌ rejected |
| 9 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1827 | 0.85 | ❌ rejected |
| 8 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 14 | -0.1147 | 0.86 | ❌ rejected |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.045) — your mutation base

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

- **Composite score**: 0.045
- **task_score** (E): 0.841
- **fitness_score**: 0.514  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 0.67 | 0.33 | 0.0623 |
| descend_to_entry | 0.33 | 0.33 | 0.1201 |
| insert_peg | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.501, 0.007, 0.270) | (0.504, -0.000, 0.340)→(0.517, 0.007, 0.289) | 0.260→0.214 | 0.33 / 0.333 | 93.685 | 344.005 |
| descend_to_entry | descend | 0.33 / step_budget | (0.501, 0.007, 0.270)→(0.499, -0.002, 0.151) | (0.517, 0.007, 0.289)→(0.516, -0.001, 0.170) | 0.214→0.098 | 0.33 / 0.333 | 33.800 | 33.800 |
| insert_peg | insert | 0.00 / guard_failure | (0.498, -0.003, 0.101)→(0.499, -0.003, 0.100) | (0.516, -0.001, 0.170)→(0.515, -0.003, 0.120) | 0.098→0.062 | 1.00 / 1.000 | 90.746 | 202.555 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.817
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.817
- phase_score: 0.023
- phase_breakdown.reach_above_socket_score: 0.025
- phase_breakdown.insertion_depth_score: 0.000
- phase_breakdown.reach_socket_entry_score: 0.079

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.621
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.873
- **Median Q (composite search score)**: 0.041
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.376


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.45833,"average_solve_count":48.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_height":0.25011,"approach_high.approach_speed":0.02289,"approach_high.approach_tol":0.02689,"descend_to_entry.descend_speed":0.01366,"descend_to_entry.force_threshold":10.02767,"insert_peg.force_limit":76.02257,"insert_peg.insert_depth":0.07453,"insert_peg.insert_speed":0.00926,"insert_peg.insert_tol":0.02257,"insert_peg.retry_offset_x":0.00947,"insert_peg.retry_offset_y":0.00944},"optimized_scores":{"best_composite_score":0.09405,"best_fitness_score":0.34072,"best_task_score":0.81668},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.44568,0.00987,0.07896],"force_p95":987.31809,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1032.01481,"mean_force":196.47036,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44143,0.00984,0.09229]},{"body_a":"peg_socket","body_b":"link7","contact_count":226.0,"contact_point_centroid":[0.54444,0.01766,0.07954],"force_p95":416.72103,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":942.51827,"mean_force":284.20131,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.43676,0.01327,0.15398]},{"body_a":"peg_socket","body_b":"link6","contact_count":630.0,"contact_point_centroid":[0.5461,0.0224,0.07989],"force_p95":299.58682,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.33581,"mean_force":278.69369,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.43856,0.02265,0.18813]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54614,0.02866,0.07997],"force_p95":101.40045,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.40045,"mean_force":101.40045,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.43996,0.02672,0.1975]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.54614,0.02866,0.07997],"force_p95":82.99705,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.32591,"mean_force":80.5262,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.43997,0.02672,0.19753]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.45617,0.00898,0.07996],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44497,0.00984,0.09194]}],"total_contact_groups":6},"final_pose_error":0.25166,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.43998,0.02672,0.19756],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1032.01481,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.47395,0.02752,0.17643],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10361,"object_to_goal_dist_start":0.26034,"object_z_max":0.3442,"peak_contact_force":281.0549,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":868.0,"raw_peak_contact_force":1032.01481,"subtask_id":"reach_above_socket","tcp_end":[0.43996,0.02672,0.1975],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47395,0.02752,0.17644],"object_pos_start":[0.47395,0.02752,0.17643],"object_to_goal_dist_end":0.10362,"object_to_goal_dist_start":0.10361,"object_z_max":0.17643,"peak_contact_force":101.40045,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":101.40045,"subtask_id":"reach_socket_entry","tcp_end":[0.43997,0.02673,0.19752],"tcp_start":[0.43996,0.02672,0.1975],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47396,0.02752,0.17645],"object_pos_start":[0.47395,0.02752,0.17644],"object_to_goal_dist_end":0.10363,"object_to_goal_dist_start":0.10362,"object_z_max":0.17647,"peak_contact_force":78.21534,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":83.32591,"subtask_id":"insertion_depth","tcp_end":[0.43998,0.02672,0.19756],"tcp_start":[0.43998,0.02672,0.19754],"tcp_to_object_dist_end":0.04001,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30769,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_height":0.28287,"approach_high.approach_speed":0.07124,"approach_high.approach_tol":0.02273,"descend_to_entry.descend_speed":0.01401,"descend_to_entry.force_threshold":7.7979,"insert_peg.force_limit":66.91267,"insert_peg.insert_depth":0.04918,"insert_peg.insert_speed":0.01456,"insert_peg.insert_tol":0.02093,"insert_peg.retry_offset_x":0.00585,"insert_peg.retry_offset_y":0.00832},"optimized_scores":{"best_composite_score":0.04056,"best_fitness_score":0.62056,"best_task_score":0.87317},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53883,-0.0149,0.04976],"force_p95":223.1957,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.43357,"mean_force":151.15506,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52414,-0.01514,0.05251]}],"total_contact_groups":1},"final_pose_error":0.07634,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52429,-0.01516,0.05196],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":233.43357,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.53579,-0.00196,0.34566],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.26806,"object_to_goal_dist_start":0.26034,"object_z_max":0.34535,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_socket","tcp_end":[0.52876,-0.00213,0.30628],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53333,-0.01335,0.16746],"object_pos_start":[0.53579,-0.00196,0.34566],"object_to_goal_dist_end":0.09454,"object_to_goal_dist_start":0.26806,"object_z_max":0.34592,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52581,-0.01351,0.12817],"tcp_start":[0.52876,-0.00213,0.30628],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.5321,-0.01498,0.09166],"object_pos_start":[0.53333,-0.01335,0.16746],"object_to_goal_dist_end":0.03729,"object_to_goal_dist_start":0.09454,"object_z_max":0.16746,"peak_contact_force":88.97678,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":233.43357,"subtask_id":"insertion_depth","tcp_end":[0.52429,-0.01516,0.05196],"tcp_start":[0.52421,-0.01515,0.05216],"tcp_to_object_dist_end":0.04046,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31472,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_height":0.28269,"approach_high.approach_speed":0.08381,"approach_high.approach_tol":0.01087,"descend_to_entry.descend_speed":0.01811,"descend_to_entry.force_threshold":6.20295,"insert_peg.force_limit":95.98077,"insert_peg.insert_depth":0.05492,"insert_peg.insert_speed":0.01459,"insert_peg.insert_tol":0.02615,"insert_peg.retry_offset_x":0.00656,"insert_peg.retry_offset_y":0.00876},"optimized_scores":{"best_composite_score":0.00081,"best_fitness_score":0.58081,"best_task_score":0.83318},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.54571,-0.02041,0.04952],"force_p95":277.31943,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.9043,"mean_force":183.66851,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.53105,-0.02083,0.05223]}],"total_contact_groups":1},"final_pose_error":0.08167,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.53127,-0.02086,0.05154],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":290.9043,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":22.0,"n_steps_budget":600.0,"object_pos_end":[0.54176,-0.00342,0.3463],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.26958,"object_to_goal_dist_start":0.26034,"object_z_max":0.34621,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_socket","tcp_end":[0.53422,-0.00368,0.30702],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54034,-0.01863,0.16505],"object_pos_start":[0.54176,-0.00342,0.3463],"object_to_goal_dist_end":0.09596,"object_to_goal_dist_start":0.26958,"object_z_max":0.3463,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.53231,-0.01888,0.12587],"tcp_start":[0.53422,-0.00368,0.30702],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.53952,-0.02059,0.09127],"object_pos_start":[0.54034,-0.01863,0.16505],"object_to_goal_dist_end":0.04596,"object_to_goal_dist_start":0.09596,"object_z_max":0.16505,"peak_contact_force":105.0456,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":290.9043,"subtask_id":"insertion_depth","tcp_end":[0.53127,-0.02086,0.05154],"tcp_start":[0.53115,-0.02085,0.0518],"tcp_to_object_dist_end":0.04058,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```