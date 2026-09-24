## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2129 | 0.85 | ❌ rejected |
| 12 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0451 | 0.84 | ❌ rejected |
| 11 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1831 | 0.85 | ❌ rejected |
| 10 | approach → insert | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 9 | -0.0302 | 0.85 | ❌ rejected |
| 9 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1827 | 0.85 | ❌ rejected |

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

## Current Skill (Q=-0.213) — your mutation base

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

- **Composite score**: -0.213
- **task_score** (E): 0.847
- **fitness_score**: 0.417  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_socket | 0.33 | 1.00 | 0.1210 |
| descend_to_entry | 0.00 | 0.33 | 0.0369 |
| insert_peg | 0.00 | 0.67 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_socket | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.463, -0.003, 0.188) | (0.504, -0.000, 0.340)→(0.498, -0.002, 0.169) | 0.260→0.092 | 1.00 / 1.333 | 255.281 | 1098.305 |
| descend_to_entry | descend | 0.00 / step_budget | (0.463, -0.003, 0.188)→(0.493, 0.002, 0.170) | (0.498, -0.002, 0.169)→(0.529, 0.001, 0.152) | 0.092→0.082 | 0.33 / 0.333 | 86.374 | 390.748 |
| insert_peg | insert | 0.00 / guard_failure | (0.493, 0.002, 0.169)→(0.493, 0.001, 0.169) | (0.529, 0.001, 0.152)→(0.529, 0.000, 0.152) | 0.082→0.082 | 0.67 / 0.667 | 145.537 | 314.769 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.817
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.817
- phase_score: 0.188
- phase_breakdown.reach_above_socket_score: 0.511
- phase_breakdown.insertion_depth_score: 0.000
- phase_breakdown.reach_socket_entry_score: 0.176

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.440
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.863
- **Median Q (composite search score)**: -0.223
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.09524,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_arc":0.14162,"approach_to_socket.approach_height":0.2009,"approach_to_socket.approach_speed":0.09998,"approach_to_socket.approach_tol":0.01158,"descend_to_entry.descend_speed":0.03607,"descend_to_entry.descend_tol":0.01254,"insert_peg.force_limit":88.99723,"insert_peg.insert_depth":0.06765,"insert_peg.insert_speed":0.01324,"insert_peg.insert_tol":0.02363,"insert_peg.retry_offset_x":0.00978,"insert_peg.retry_offset_y":0.00828},"optimized_scores":{"best_composite_score":-0.1903,"best_fitness_score":0.4397,"best_task_score":0.81652},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":282.0,"contact_point_centroid":[0.54606,0.02683,0.07918],"force_p95":895.44014,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1128.18561,"mean_force":326.68161,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.4511,0.02614,0.1857]},{"body_a":"peg_socket","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.54464,0.02716,0.07969],"force_p95":695.45344,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1116.37771,"mean_force":280.57282,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44689,0.02406,0.17354]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.44537,0.01336,0.07845],"force_p95":429.83115,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":955.18034,"mean_force":79.59836,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44126,0.01332,0.0913]},{"body_a":"peg_socket","body_b":"link7","contact_count":959.0,"contact_point_centroid":[0.54606,0.03721,0.07992],"force_p95":307.77567,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":421.4041,"mean_force":235.652,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.47707,0.03176,0.1878]},{"body_a":"peg_socket","body_b":"link6","contact_count":19.0,"contact_point_centroid":[0.54609,0.0272,0.07917],"force_p95":331.63253,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":332.17653,"mean_force":182.97045,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46153,0.02763,0.19431]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54615,0.04218,0.07999],"force_p95":287.6009,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":287.6009,"mean_force":287.6009,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.48833,0.03623,0.16185]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.45625,0.00889,0.07971],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44375,0.01319,0.09046]}],"total_contact_groups":7},"final_pose_error":0.20461,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48843,0.03638,0.16193],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1128.18561,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.4936,0.0289,0.17087],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09557,"object_to_goal_dist_start":0.26034,"object_z_max":0.34419,"peak_contact_force":270.157,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":706.0,"raw_peak_contact_force":1128.18561,"subtask_id":"reach_above_socket","tcp_end":[0.46107,0.02749,0.19411],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52334,0.03759,0.14255],"object_pos_start":[0.4936,0.0289,0.17087],"object_to_goal_dist_end":0.07662,"object_to_goal_dist_start":0.09557,"object_z_max":0.17322,"peak_contact_force":259.12248,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":978.0,"raw_peak_contact_force":421.4041,"subtask_id":"reach_socket_entry","tcp_end":[0.48833,0.03623,0.16185],"tcp_start":[0.46107,0.02749,0.19411],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5234,0.03758,0.14262],"object_pos_start":[0.52334,0.03759,0.14255],"object_to_goal_dist_end":0.07668,"object_to_goal_dist_start":0.07662,"object_z_max":0.14265,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":287.6009,"subtask_id":"insertion_depth","tcp_end":[0.48843,0.03638,0.16193],"tcp_start":[0.48841,0.03633,0.16194],"tcp_to_object_dist_end":0.03997,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":16.0,"average_failure_rate":0.25397,"average_mean_iterations":56.63492,"average_solve_count":63.0,"average_success_count":47.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_arc":0.14527,"approach_to_socket.approach_height":0.20778,"approach_to_socket.approach_speed":0.05433,"approach_to_socket.approach_tol":0.01983,"descend_to_entry.descend_speed":0.09049,"descend_to_entry.descend_tol":0.01235,"insert_peg.force_limit":85.49351,"insert_peg.insert_depth":0.04255,"insert_peg.insert_speed":0.01298,"insert_peg.insert_tol":0.02298,"insert_peg.retry_offset_x":0.00579,"insert_peg.retry_offset_y":0.01114},"optimized_scores":{"best_composite_score":-0.22522,"best_fitness_score":0.40478,"best_task_score":0.86171},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.56708,-0.00657,0.07886],"force_p95":640.82968,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1054.07932,"mean_force":244.73167,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44929,-0.00677,0.11341]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.46991,-0.00577,0.07929],"force_p95":936.77622,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":966.16785,"mean_force":357.07551,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45993,-0.00575,0.09108]},{"body_a":"peg_socket","body_b":"link6","contact_count":600.0,"contact_point_centroid":[0.58957,-0.01222,0.07985],"force_p95":271.08157,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":434.44833,"mean_force":242.25616,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45447,-0.00991,0.16449]},{"body_a":"peg_socket","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.58953,-0.01189,0.07986],"force_p95":339.51962,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":393.88556,"mean_force":267.00908,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.49233,-0.01368,0.17864]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5896,-0.0196,0.07996],"force_p95":347.67419,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":368.21305,"mean_force":230.09051,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49422,-0.01267,0.1751]},{"body_a":"peg_socket","body_b":"link6","contact_count":243.0,"contact_point_centroid":[0.58958,-0.01365,0.07991],"force_p95":239.69875,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.21303,"mean_force":193.60126,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.47581,-0.01453,0.18387]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.54686,0.01338,0.0792],"force_p95":102.24328,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":155.64687,"mean_force":16.71491,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45076,-0.00632,0.09828]},{"body_a":"peg_socket","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.5475,-0.04713,0.07954],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45056,-0.00628,0.09672]}],"total_contact_groups":8},"final_pose_error":0.19585,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.4942,-0.01299,0.17503],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1054.07932,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":727.0,"n_steps_budget":870.0,"object_pos_end":[0.49757,-0.01402,0.168],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08914,"object_to_goal_dist_start":0.26034,"object_z_max":0.34494,"peak_contact_force":248.0097,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":668.0,"raw_peak_contact_force":1054.07932,"subtask_id":"reach_above_socket","tcp_end":[0.46092,-0.01464,0.18401],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":333.0,"n_steps_budget":900.0,"object_pos_end":[0.53021,-0.01504,0.15793],"object_pos_start":[0.49757,-0.01402,0.168],"object_to_goal_dist_end":0.08493,"object_to_goal_dist_start":0.08914,"object_z_max":0.168,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":295.0,"raw_peak_contact_force":393.88556,"subtask_id":"reach_socket_entry","tcp_end":[0.49429,-0.01249,0.17535],"tcp_start":[0.46092,-0.01464,0.18401],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.53014,-0.01531,0.15765],"object_pos_start":[0.53021,-0.01504,0.15793],"object_to_goal_dist_end":0.08469,"object_to_goal_dist_start":0.08493,"object_z_max":0.15793,"peak_contact_force":162.82446,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":368.21305,"subtask_id":"insertion_depth","tcp_end":[0.4942,-0.01299,0.17503],"tcp_start":[0.4942,-0.0128,0.17503],"tcp_to_object_dist_end":0.03998,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":33.0,"average_failure_rate":0.36264,"average_mean_iterations":77.14286,"average_solve_count":91.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_socket.approach_arc":0.13687,"approach_to_socket.approach_height":0.20865,"approach_to_socket.approach_speed":0.05968,"approach_to_socket.approach_tol":0.01191,"descend_to_entry.descend_speed":0.04649,"descend_to_entry.descend_tol":0.0172,"insert_peg.force_limit":78.04368,"insert_peg.insert_depth":0.05435,"insert_peg.insert_speed":0.01127,"insert_peg.insert_tol":0.01819,"insert_peg.retry_offset_x":0.00779,"insert_peg.retry_offset_y":0.00945},"optimized_scores":{"best_composite_score":-0.22326,"best_fitness_score":0.40674,"best_task_score":0.86277},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.56675,-0.00946,0.07834],"force_p95":438.24115,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1112.64977,"mean_force":105.59435,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45296,-0.00842,0.10535]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.4765,-0.00755,0.07995],"force_p95":709.92116,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":788.80129,"mean_force":262.93376,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.46118,-0.00751,0.0906]},{"body_a":"peg_socket","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.54781,0.00729,0.0781],"force_p95":611.73342,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":698.95241,"mean_force":120.97299,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45235,-0.00835,0.10114]},{"body_a":"peg_socket","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.59638,-0.0146,0.07985],"force_p95":327.87722,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":356.95298,"mean_force":264.50214,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.49586,-0.01358,0.1779]},{"body_a":"peg_socket","body_b":"link6","contact_count":474.0,"contact_point_centroid":[0.59644,-0.01893,0.07992],"force_p95":246.97422,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":329.9634,"mean_force":182.54899,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.48276,-0.02077,0.18663]},{"body_a":"peg_socket","body_b":"link6","contact_count":587.0,"contact_point_centroid":[0.59618,-0.01643,0.07984],"force_p95":271.31963,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.63989,"mean_force":239.26199,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45787,-0.01419,0.15773]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.59639,-0.02418,0.07978],"force_p95":287.02278,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.49352,"mean_force":216.12542,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49655,-0.01874,0.17023]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.54835,-0.05353,0.07916],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45182,-0.00826,0.09634]}],"total_contact_groups":8},"final_pose_error":0.20333,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.49653,-0.01903,0.16996],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1112.64977,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":698.0,"n_steps_budget":840.0,"object_pos_end":[0.50325,-0.0207,0.16847],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09092,"object_to_goal_dist_start":0.26034,"object_z_max":0.345,"peak_contact_force":247.67758,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":669.0,"raw_peak_contact_force":1112.64977,"subtask_id":"reach_above_socket","tcp_end":[0.46659,-0.02155,0.18446],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.53322,-0.02077,0.15552],"object_pos_start":[0.50325,-0.0207,0.16847],"object_to_goal_dist_end":0.08508,"object_to_goal_dist_start":0.09092,"object_z_max":0.1705,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":517.0,"raw_peak_contact_force":356.95298,"subtask_id":"reach_socket_entry","tcp_end":[0.49658,-0.01803,0.17134],"tcp_start":[0.46659,-0.02155,0.18446],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.53321,-0.02137,0.15444],"object_pos_start":[0.53322,-0.02077,0.15552],"object_to_goal_dist_end":0.08426,"object_to_goal_dist_start":0.08508,"object_z_max":0.15552,"peak_contact_force":273.78605,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":288.49352,"subtask_id":"insertion_depth","tcp_end":[0.49653,-0.01903,0.16996],"tcp_start":[0.49653,-0.01884,0.17006],"tcp_to_object_dist_end":0.03989,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```