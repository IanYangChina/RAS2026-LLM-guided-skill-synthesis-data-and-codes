## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1338 | 0.86 | ✅ accepted |
| 4 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2426 | 0.86 | ✅ accepted |
| 3 | retract → approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0138 | 0.80 | ❌ rejected |
| 2 | retract → approach → descend → insert | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.1028 | 0.68 | ❌ rejected |
| 1 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0456 | 0.85 | ✅ accepted |

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

## Current Skill (Q=0.134) — your mutation base

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
  generator: linear_cartesian
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
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
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
  guards:
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: insertion_depth

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **insert_peg** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.055, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insert_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: 0.134
- **task_score** (E): 0.857
- **fitness_score**: 0.453  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_socket | 0.67 | 0.33 | 0.1453 |
| descend_to_entry | 0.33 | 0.33 | 0.0008 |
| insert_peg | 0.00 | 0.67 | 0.0059 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_socket | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.014, 0.158) | (0.504, -0.000, 0.340)→(0.529, -0.014, 0.148) | 0.260→0.078 | 0.33 / 0.333 | 109.996 | 1777.685 |
| descend_to_entry | descend | 0.33 / guard_failure | (0.491, -0.015, 0.157)→(0.491, -0.016, 0.157) | (0.529, -0.014, 0.148)→(0.529, -0.015, 0.148) | 0.078→0.079 | 0.33 / 0.333 | 116.874 | 116.874 |
| insert_peg | insert | 0.00 / guard_failure | (0.493, -0.015, 0.155)→(0.496, -0.014, 0.150) | (0.530, -0.016, 0.148)→(0.534, -0.016, 0.142) | 0.079→0.077 | 0.67 / 0.667 | 133.558 | 133.558 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.848
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.848
- phase_score: 0.161
- phase_breakdown.reach_above_socket_score: 0.361
- phase_breakdown.insertion_depth_score: 0.000
- phase_breakdown.reach_socket_entry_score: 0.261

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.484
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.864
- **Median Q (composite search score)**: 0.054
- **K-run variance**: 0.0214
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.330


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.36585,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_height":0.10262,"approach_to_socket.approach_speed":0.09843,"approach_to_socket.approach_tol":0.00917,"descend_to_entry.descend_speed":0.02124,"descend_to_entry.force_threshold":3.28496,"insert_peg.insert_depth":0.04334,"insert_peg.insert_speed":0.01344,"insert_peg.insert_tol":0.02264},"optimized_scores":{"best_composite_score":0.33887,"best_fitness_score":0.43554,"best_task_score":0.84793},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45457,0.00833,0.07947],"force_p95":3256.87928,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3291.19332,"mean_force":1362.74704,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45061,0.00365,0.09175]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.45888,0.00362,0.07874],"force_p95":2894.18108,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2917.39562,"mean_force":1157.46721,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45314,0.00369,0.09137]},{"body_a":"peg_socket","body_b":"link7","contact_count":907.0,"contact_point_centroid":[0.54602,0.00936,0.07991],"force_p95":304.89353,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":735.03668,"mean_force":287.34594,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.46793,0.00407,0.12841]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54583,0.01674,0.07986],"force_p95":350.62092,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.62092,"mean_force":350.62092,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.47262,0.00725,0.13758]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54583,0.0166,0.07986],"force_p95":83.33618,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.40194,"mean_force":69.41312,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.47262,0.0071,0.13762]}],"total_contact_groups":5},"final_pose_error":0.15977,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.47263,0.00703,0.13763],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":3291.19332,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51118,0.01068,0.12755],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05,"object_to_goal_dist_start":0.26034,"object_z_max":0.34442,"peak_contact_force":329.98877,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":931.0,"raw_peak_contact_force":3291.19332,"subtask_id":"reach_above_socket","tcp_end":[0.47262,0.00725,0.13758],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51118,0.01059,0.12758],"object_pos_start":[0.51118,0.01068,0.12755],"object_to_goal_dist_end":0.05001,"object_to_goal_dist_start":0.05,"object_z_max":0.12755,"peak_contact_force":350.62092,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":350.62092,"subtask_id":"reach_socket_entry","tcp_end":[0.47262,0.00715,0.13761],"tcp_start":[0.47262,0.00725,0.13758],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51119,0.01054,0.12758],"object_pos_start":[0.51118,0.01059,0.12758],"object_to_goal_dist_end":0.05,"object_to_goal_dist_start":0.05001,"object_z_max":0.12758,"peak_contact_force":84.40194,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":84.40194,"subtask_id":"insertion_depth","tcp_end":[0.47263,0.00703,0.13763],"tcp_start":[0.47263,0.00706,0.13762],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":102.0,"average_failure_rate":0.64151,"average_mean_iterations":131.06918,"average_solve_count":159.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_height":0.12437,"approach_to_socket.approach_speed":0.0904,"approach_to_socket.approach_tol":0.01385,"descend_to_entry.descend_speed":0.02377,"descend_to_entry.force_threshold":13.02929,"insert_peg.insert_depth":0.05624,"insert_peg.insert_speed":0.00834,"insert_peg.insert_tol":0.02928},"optimized_scores":{"best_composite_score":0.05438,"best_fitness_score":0.48438,"best_task_score":0.8575},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.4699,-0.00186,0.07947],"force_p95":971.50581,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":993.81578,"mean_force":638.98375,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.46041,-0.00187,0.0914]},{"body_a":"peg_socket","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.5739,-0.00442,0.07951],"force_p95":619.83791,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":961.68265,"mean_force":307.20871,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.4625,-0.00455,0.13588]},{"body_a":"peg_socket","body_b":"link6","contact_count":781.0,"contact_point_centroid":[0.58952,-0.00755,0.07985],"force_p95":301.02643,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":875.25285,"mean_force":250.67997,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.4614,-0.00591,0.1775]},{"body_a":"peg_socket","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.54424,0.01328,0.07909],"force_p95":180.54611,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.14175,"mean_force":41.76967,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44776,-0.00239,0.09945]}],"total_contact_groups":4},"final_pose_error":0.1719,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.5255,-0.02989,0.14013],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":993.81578,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.55318,-0.02933,0.15447],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0961,"object_to_goal_dist_start":0.26034,"object_z_max":0.34461,"peak_contact_force":0.0,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":857.0,"raw_peak_contact_force":993.81578,"subtask_id":"reach_above_socket","tcp_end":[0.5134,-0.02629,0.1573],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.55432,-0.03119,0.15417],"object_pos_start":[0.55318,-0.02933,0.15447],"object_to_goal_dist_end":0.09708,"object_to_goal_dist_start":0.0961,"object_z_max":0.15447,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.51657,-0.03184,0.1551],"tcp_start":[0.51554,-0.03021,0.1558],"tcp_to_object_dist_end":0.03777,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.56527,-0.03371,0.14212],"object_pos_start":[0.55646,-0.03444,0.15363],"object_to_goal_dist_end":0.0962,"object_to_goal_dist_start":0.09897,"object_z_max":0.15363,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_depth","tcp_end":[0.5255,-0.02989,0.14013],"tcp_start":[0.51657,-0.03184,0.1551],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.10417,"average_solve_count":48.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_height":0.14162,"approach_to_socket.approach_speed":0.09744,"approach_to_socket.approach_tol":0.01359,"descend_to_entry.descend_speed":0.02017,"descend_to_entry.force_threshold":5.44735,"insert_peg.insert_depth":0.04192,"insert_peg.insert_speed":0.01322,"insert_peg.insert_tol":0.01265},"optimized_scores":{"best_composite_score":0.00805,"best_fitness_score":0.43805,"best_task_score":0.86408},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.54602,0.00737,0.07773],"force_p95":823.51535,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1048.04697,"mean_force":218.45996,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.4503,-0.00367,0.10193]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47654,-0.00309,0.07983],"force_p95":842.9746,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":845.53315,"mean_force":418.50234,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45955,-0.00306,0.08956]},{"body_a":"peg_socket","body_b":"link6","contact_count":679.0,"contact_point_centroid":[0.59614,-0.0105,0.07981],"force_p95":333.11947,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":640.46018,"mean_force":254.1874,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.46528,-0.00904,0.16789]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.59613,-0.03057,0.07978],"force_p95":315.93763,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.27283,"mean_force":269.61829,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.4888,-0.02061,0.17182]},{"body_a":"peg_socket","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.56673,-0.00373,0.07858],"force_p95":280.13013,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":301.11454,"mean_force":65.41464,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45018,-0.00373,0.10421]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.54629,-0.05347,0.07951],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.4493,-0.00351,0.09485]}],"total_contact_groups":6},"final_pose_error":0.19452,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.48885,-0.02054,0.17165],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1048.04697,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.52218,-0.0247,0.16245],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08889,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":0.0,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":751.0,"raw_peak_contact_force":1048.04697,"subtask_id":"reach_above_socket","tcp_end":[0.48587,-0.0237,0.1792],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52182,-0.02469,0.16231],"object_pos_start":[0.52218,-0.0247,0.16245],"object_to_goal_dist_end":0.08866,"object_to_goal_dist_start":0.08889,"object_z_max":0.16245,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.48512,-0.02309,0.17838],"tcp_start":[0.48521,-0.02329,0.17867],"tcp_to_object_dist_end":0.0401,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.52564,-0.02383,0.1565],"object_pos_start":[0.52158,-0.02467,0.162],"object_to_goal_dist_end":0.08413,"object_to_goal_dist_start":0.08831,"object_z_max":0.162,"peak_contact_force":316.27283,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":316.27283,"subtask_id":"insertion_depth","tcp_end":[0.48885,-0.02054,0.17165],"tcp_start":[0.48886,-0.02057,0.17169],"tcp_to_object_dist_end":0.03992,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```