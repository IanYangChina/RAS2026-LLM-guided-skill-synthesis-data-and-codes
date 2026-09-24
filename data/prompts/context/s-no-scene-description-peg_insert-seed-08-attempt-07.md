## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2109 | 0.83 | ❌ rejected |
| 6 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 12 | 0.1236 | 0.86 | ✅ accepted |
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1338 | 0.86 | ✅ accepted |
| 4 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2426 | 0.86 | ✅ accepted |
| 3 | retract → approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0138 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.211) — your mutation base

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

- **Composite score**: -0.211
- **task_score** (E): 0.834
- **fitness_score**: 0.419  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_socket | 0.00 | 1.00 | 0.1151 |
| descend_to_entry | 0.00 | 1.00 | 0.0355 |
| insert_peg | 0.00 | 0.67 | 0.0853 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_socket | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.464, -0.012, 0.202) | (0.504, -0.000, 0.340)→(0.497, -0.008, 0.181) | 0.260→0.109 | 1.00 / 1.000 | 283.416 | 1054.483 |
| descend_to_entry | descend | 0.00 / step_budget | (0.464, -0.012, 0.202)→(0.494, -0.011, 0.196) | (0.497, -0.008, 0.181)→(0.527, -0.007, 0.175) | 0.109→0.106 | 1.00 / 1.000 | 280.850 | 433.699 |
| insert_peg | insert | 0.00 / step_budget | (0.494, -0.011, 0.196)→(0.521, 0.006, 0.224) | (0.527, -0.007, 0.175)→(0.557, 0.010, 0.211) | 0.106→0.152 | 0.67 / 1.000 | 220.464 | 510.257 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.801
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.801
- phase_score: 0.245
- phase_breakdown.reach_above_socket_score: 0.326
- phase_breakdown.insertion_depth_score: 0.284
- phase_breakdown.reach_socket_entry_score: 0.024

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.467
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.854
- **Median Q (composite search score)**: -0.227
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.291


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.36893,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_arc":0.0571,"approach_to_socket.approach_height":0.24979,"approach_to_socket.approach_speed":0.04686,"approach_to_socket.approach_tol":0.00923,"descend_to_entry.descend_speed":0.02577,"descend_to_entry.descend_tol":0.00539,"insert_peg.contact_guard_threshold":0.89971,"insert_peg.insert_depth":0.04464,"insert_peg.insert_speed":0.01571,"insert_peg.insert_tol":0.01368,"insert_peg.retry_offset_x":0.00583,"insert_peg.retry_offset_y":0.00753},"optimized_scores":{"best_composite_score":-0.163,"best_fitness_score":0.467,"best_task_score":0.80063},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":81.0,"contact_point_centroid":[0.5372,0.0114,0.07848],"force_p95":649.10611,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1070.27282,"mean_force":286.7273,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.42808,0.01366,0.13126]},{"body_a":"peg_socket","body_b":"link6","contact_count":365.0,"contact_point_centroid":[0.54608,0.02501,0.07983],"force_p95":302.94501,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":789.71146,"mean_force":277.14557,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.43339,0.02407,0.18164]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.51559,0.00838,0.0794],"force_p95":465.83283,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":477.53153,"mean_force":278.12326,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.42804,0.01106,0.09928]},{"body_a":"peg_socket","body_b":"link7","contact_count":881.0,"contact_point_centroid":[0.54609,0.03703,0.07993],"force_p95":307.89067,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":395.66073,"mean_force":271.36231,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.48185,0.03504,0.18096]},{"body_a":"peg_socket","body_b":"link6","contact_count":993.0,"contact_point_centroid":[0.54613,0.03261,0.07996],"force_p95":236.88417,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.02666,"mean_force":190.01627,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.455,0.03053,0.20379]},{"body_a":"peg_socket","body_b":"link6","contact_count":67.0,"contact_point_centroid":[0.54613,0.03255,0.07994],"force_p95":276.06207,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":287.21759,"mean_force":241.57259,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.47189,0.03187,0.20607]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.43477,0.01083,0.0793],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.43121,0.01079,0.09315]}],"total_contact_groups":7},"final_pose_error":0.1797,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.49128,0.0436,0.15992],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1070.27282,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":660.0,"object_pos_end":[0.47301,0.03035,0.17569],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10395,"object_to_goal_dist_start":0.26034,"object_z_max":0.34399,"peak_contact_force":281.02044,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":468.0,"raw_peak_contact_force":1070.27282,"subtask_id":"reach_above_socket","tcp_end":[0.43881,0.02952,0.19643],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4993,0.03215,0.18318],"object_pos_start":[0.47301,0.03035,0.17569],"object_to_goal_dist_end":0.10808,"object_to_goal_dist_start":0.10395,"object_z_max":0.18463,"peak_contact_force":242.20448,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":993.0,"raw_peak_contact_force":294.02666,"subtask_id":"reach_socket_entry","tcp_end":[0.46996,0.03153,0.21036],"tcp_start":[0.43881,0.02952,0.19643],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52567,0.04222,0.13954],"object_pos_start":[0.4993,0.03215,0.18318],"object_to_goal_dist_end":0.07737,"object_to_goal_dist_start":0.10808,"object_z_max":0.18322,"peak_contact_force":247.16162,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":948.0,"raw_peak_contact_force":395.66073,"subtask_id":"insertion_depth","tcp_end":[0.49128,0.0436,0.15992],"tcp_start":[0.46996,0.03153,0.21036],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":103.0,"average_failure_rate":0.54787,"average_mean_iterations":112.62766,"average_solve_count":188.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_arc":0.07762,"approach_to_socket.approach_height":0.1916,"approach_to_socket.approach_speed":0.07602,"approach_to_socket.approach_tol":0.01606,"descend_to_entry.descend_speed":0.02169,"descend_to_entry.descend_tol":0.01264,"insert_peg.contact_guard_threshold":0.84701,"insert_peg.insert_depth":0.06338,"insert_peg.insert_speed":0.01647,"insert_peg.insert_tol":0.02366,"insert_peg.retry_offset_x":0.00737,"insert_peg.retry_offset_y":0.00814},"optimized_scores":{"best_composite_score":-0.2422,"best_fitness_score":0.3878,"best_task_score":0.84681},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.5448,0.01305,0.07767],"force_p95":821.47136,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1023.96303,"mean_force":207.26625,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44926,0.01056,0.10586]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.46966,0.01025,0.07988],"force_p95":791.25079,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":793.12829,"mean_force":522.49384,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45862,0.01021,0.09172]},{"body_a":"peg_socket","body_b":"link7","contact_count":192.0,"contact_point_centroid":[0.58953,-0.00691,0.07984],"force_p95":314.71784,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":387.64197,"mean_force":259.24377,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.49539,-0.00194,0.17747]},{"body_a":"peg_socket","body_b":"link6","contact_count":760.0,"contact_point_centroid":[0.58957,0.00052,0.07992],"force_p95":291.68535,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":361.73205,"mean_force":218.22255,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.48326,0.00144,0.20086]},{"body_a":"peg_socket","body_b":"link6","contact_count":544.0,"contact_point_centroid":[0.58951,0.01139,0.07986],"force_p95":292.6401,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.87024,"mean_force":247.65606,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45678,0.01266,0.16326]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.58959,-0.00749,0.07994],"force_p95":265.05512,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.01693,"mean_force":200.99802,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49779,-0.00484,0.17537]},{"body_a":"peg_socket","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.55986,0.00802,0.07854],"force_p95":126.64127,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.61046,"mean_force":24.77609,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44907,0.01057,0.10629]}],"total_contact_groups":7},"final_pose_error":0.37373,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.5312,0.02384,0.33311],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1023.96303,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.50177,0.00444,0.18026],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10037,"object_to_goal_dist_start":0.26034,"object_z_max":0.34454,"peak_contact_force":296.41667,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":616.0,"raw_peak_contact_force":1023.96303,"subtask_id":"reach_above_socket","tcp_end":[0.46706,0.00518,0.20012],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53339,-0.00508,0.15741],"object_pos_start":[0.50177,0.00444,0.18026],"object_to_goal_dist_end":0.08446,"object_to_goal_dist_start":0.10037,"object_z_max":0.18275,"peak_contact_force":175.16007,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":952.0,"raw_peak_contact_force":387.64197,"subtask_id":"reach_socket_entry","tcp_end":[0.49768,-0.00495,0.17544],"tcp_start":[0.46706,0.00518,0.20012],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.57097,0.02555,0.32921],"object_pos_start":[0.53339,-0.00508,0.15741],"object_to_goal_dist_end":0.26037,"object_to_goal_dist_start":0.08446,"object_z_max":0.32726,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":274.01693,"subtask_id":"insertion_depth","tcp_end":[0.5312,0.02384,0.33311],"tcp_start":[0.49768,-0.00495,0.17544],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":79.0,"average_failure_rate":0.395,"average_mean_iterations":82.245,"average_solve_count":200.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_arc":0.06075,"approach_to_socket.approach_height":0.18767,"approach_to_socket.approach_speed":0.05243,"approach_to_socket.approach_tol":0.01731,"descend_to_entry.descend_speed":0.01628,"descend_to_entry.descend_tol":0.01033,"insert_peg.contact_guard_threshold":0.91609,"insert_peg.insert_depth":0.066,"insert_peg.insert_speed":0.01658,"insert_peg.insert_tol":0.02428,"insert_peg.retry_offset_x":0.00608,"insert_peg.retry_offset_y":0.00534},"optimized_scores":{"best_composite_score":-0.22743,"best_fitness_score":0.40257,"best_task_score":0.85354},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.56802,-0.0135,0.07795],"force_p95":863.25968,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1069.21202,"mean_force":147.65501,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45275,-0.01234,0.10663]},{"body_a":"world","body_b":"link5","contact_count":130.0,"contact_point_centroid":[0.65064,0.09146,-0.00014],"force_p95":700.35925,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":861.09397,"mean_force":503.14671,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.5337,-0.04136,0.18752]},{"body_a":"peg_socket","body_b":"link5","contact_count":14.0,"contact_point_centroid":[0.54079,0.03654,0.07996],"force_p95":609.49214,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":662.02557,"mean_force":436.02402,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.53948,-0.04823,0.18087]},{"body_a":"peg_socket","body_b":"link7","contact_count":610.0,"contact_point_centroid":[0.55671,-0.07907,0.07993],"force_p95":557.51211,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":619.42968,"mean_force":477.47721,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.4969,-0.06787,0.2068]},{"body_a":"peg_socket","body_b":"link7","contact_count":802.0,"contact_point_centroid":[0.59311,-0.07417,0.07988],"force_p95":520.33709,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":567.3676,"mean_force":379.89126,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52554,-0.04933,0.19792]},{"body_a":"peg_socket","body_b":"link7","contact_count":421.0,"contact_point_centroid":[0.5747,-0.07783,0.07991],"force_p95":520.59335,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":551.48283,"mean_force":456.7083,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.51016,-0.06349,0.2042]},{"body_a":"peg_socket","body_b":"link6","contact_count":874.0,"contact_point_centroid":[0.59622,-0.02284,0.07982],"force_p95":306.39551,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.86869,"mean_force":261.91624,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.46864,-0.03488,0.18121]},{"body_a":"peg_socket","body_b":"link6","contact_count":24.0,"contact_point_centroid":[0.59645,-0.01849,0.07996],"force_p95":218.7945,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.29966,"mean_force":139.83527,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.48713,-0.07013,0.20896]},{"body_a":"peg_socket","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.54747,0.00745,0.07843],"force_p95":150.99367,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.1794,"mean_force":51.70668,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.4522,-0.01214,0.10006]},{"body_a":"peg_socket","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.54776,-0.05362,0.0787],"force_p95":2.98511,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.90072,"mean_force":1.1056,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45192,-0.01211,0.09874]}],"total_contact_groups":10},"final_pose_error":0.22226,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.54007,-0.04856,0.1798],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1069.21202,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51734,-0.05765,0.18845],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12404,"object_to_goal_dist_start":0.26034,"object_z_max":0.34523,"peak_contact_force":272.81193,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":950.0,"raw_peak_contact_force":1069.21202,"subtask_id":"reach_above_socket","tcp_end":[0.48626,-0.07051,0.2101],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54854,-0.04937,0.18378],"object_pos_start":[0.51734,-0.05765,0.18845],"object_to_goal_dist_end":0.12476,"object_to_goal_dist_start":0.12404,"object_z_max":0.18849,"peak_contact_force":425.18602,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1055.0,"raw_peak_contact_force":619.42968,"subtask_id":"reach_socket_entry","tcp_end":[0.51565,-0.06069,0.20353],"tcp_start":[0.48626,-0.07051,0.2101],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":870.0,"n_steps_budget":1000.0,"object_pos_end":[0.57508,-0.03663,0.16458],"object_pos_start":[0.54854,-0.04937,0.18378],"object_to_goal_dist_end":0.11888,"object_to_goal_dist_start":0.12476,"object_z_max":0.18378,"peak_contact_force":414.22948,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":946.0,"raw_peak_contact_force":861.09397,"subtask_id":"insertion_depth","tcp_end":[0.54007,-0.04856,0.1798],"tcp_start":[0.51565,-0.06069,0.20353],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```