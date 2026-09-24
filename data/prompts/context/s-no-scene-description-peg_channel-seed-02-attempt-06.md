## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1482 | 0.18 | ✅ accepted |
| 5 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0612 | 0.00 | ❌ rejected |
| 4 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1447 | 0.17 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1936 | 0.13 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1931 | 0.13 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

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

## Current Skill (Q=0.148) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.15
- id: center_at_channel
  anchor: fixture
  weight: 0.15
- id: traverse_channel
  weight: 0.7
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.2
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_force:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_confirm
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_peg
- id: center_at_channel
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: body
    entity: channel_base_body
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    align_height:
      type: scalar
      range:
      - 0.08
      - 0.16
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: center_at_channel
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: traverse_channel
- id: retract_up
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.2
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_confirm, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **center_at_channel** (`align`)
  - target: source=yaml, anchor=body, entity=channel_base_body, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_height: status=consumed; consumers=target.offset.z (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_up** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.148
- **task_score** (E): 0.181
- **fitness_score**: 0.238  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1647 |
| descend_to_peg | 1.00 | 1.00 | 0.1008 |
| center_at_channel | 0.67 | 1.00 | 0.0442 |
| push_through_channel | 0.33 | 1.00 | 0.1031 |
| retract_up | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.077, 0.196) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.077, 0.196)→(0.491, 0.070, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 44.367 | 44.367 |
| center_at_channel | align | 0.67 / step_budget | (0.491, 0.070, 0.097)→(0.504, 0.030, 0.093) | (0.498, 0.068, 0.034)→(0.500, 0.060, 0.035) | 0.148→0.140 | 1.00 / 2.667 | 67.866 | 223.625 |
| push_through_channel | push | 0.33 / step_budget | (0.504, 0.030, 0.093)→(0.511, -0.073, 0.089) | (0.500, 0.060, 0.035)→(0.495, -0.004, 0.024) | 0.140→0.078 | 1.00 / 2.667 | 375.529 | 429.226 |
| retract_up | retract | 1.00 / step_budget | (0.511, -0.073, 0.089)→(0.509, -0.073, 0.178) | (0.495, -0.004, 0.024)→(0.497, -0.004, 0.025) | 0.078→0.078 | 1.00 / 1.333 | 2.676 | 123.090 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.403
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.261
- phase_score: 0.254
- phase_breakdown.center_at_channel_score: 0.000
- phase_breakdown.reach_peg_score: 0.190
- phase_breakdown.traverse_channel_score: 0.322

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.257
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.261
- **Median Q (composite search score)**: 0.164
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.374


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9375,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.12176,"center_at_channel.align_height":0.09381,"descend_to_peg.descend_force":16.56072,"push_through_channel.push_distance":0.15712},"optimized_scores":{"best_composite_score":0.16664,"best_fitness_score":0.25664,"best_task_score":0.26089},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":264.0,"contact_point_centroid":[0.52503,-0.0206,0.05996],"force_p95":359.90872,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":405.92766,"mean_force":275.7397,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50443,-0.0747,0.09604]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":179.0,"contact_point_centroid":[0.47498,0.11849,0.05996],"force_p95":231.90119,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":243.0986,"mean_force":157.36773,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49159,0.05351,0.10381]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.47499,0.06471,0.05999],"force_p95":145.11702,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.56838,"mean_force":97.69567,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50125,-0.02123,0.09679]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":172.0,"contact_point_centroid":[0.475,0.07888,0.05999],"force_p95":123.34421,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.78078,"mean_force":68.04522,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50462,-0.072,0.09612]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.475,0.05689,0.06],"force_p95":118.39824,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.58906,"mean_force":89.68087,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50716,-0.0807,0.09627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49704,0.00214,0.00822],"force_p95":82.03559,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.98262,"mean_force":8.62807,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50342,-0.05712,0.09634]},{"body_a":"peg","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.49614,0.05453,0.06407],"force_p95":96.04875,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.83808,"mean_force":70.75218,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5008,0.01061,0.09766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.49578,0.05916,0.0094],"force_p95":83.19219,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.96925,"mean_force":14.11829,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49268,0.04976,0.10313]},{"body_a":"peg","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.49506,0.07405,0.06002],"force_p95":87.36807,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.72848,"mean_force":62.64159,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49854,0.02661,0.09889]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.06],"force_p95":50.43751,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.43751,"mean_force":50.43751,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48477,0.06683,0.10737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49462,-0.00161,0.00807],"force_p95":0.68815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.18631,"mean_force":0.70802,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50494,-0.08093,0.14031]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47499,0.02316,0.02449],"force_p95":8.66026,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.76019,"mean_force":3.84554,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50478,-0.08092,0.15261]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52504,-0.02542,0.05995],"force_p95":6.07852,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.75391,"mean_force":2.2513,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50716,-0.08072,0.09629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":635.0,"contact_point_centroid":[0.49528,0.06387,0.00937],"force_p95":0.56794,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55896,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4866,0.14385,0.2272]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50402,0.21531,0.29297]},{"body_a":"peg","body_b":"channel_base_body","contact_count":305.0,"contact_point_centroid":[0.49545,0.06375,0.0094],"force_p95":0.55043,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54537,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48161,0.06916,0.13642]}],"total_contact_groups":16},"final_pose_error":0.01114,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49461,-0.00055,0.02413],"final_tcp_position":[0.505,-0.0809,0.18532],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":405.92766,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.49516,0.06366,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54402,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":663.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.48017,0.07225,0.16687],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":305.0,"n_steps_budget":720.0,"object_pos_end":[0.49526,0.06409,0.03401],"object_pos_start":[0.49516,0.06366,0.03396],"object_to_goal_dist_end":0.14429,"object_to_goal_dist_start":0.14387,"object_z_max":0.03401,"peak_contact_force":50.43751,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":306.0,"raw_peak_contact_force":50.43751,"subtask_id":"reach_peg","tcp_end":[0.48479,0.06683,0.10722],"tcp_start":[0.48017,0.07225,0.16687],"tcp_to_object_dist_end":0.07401,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":244.0,"n_steps_budget":600.0,"object_pos_end":[0.49643,0.05069,0.03548],"object_pos_start":[0.49526,0.06409,0.03401],"object_to_goal_dist_end":0.13081,"object_to_goal_dist_start":0.14429,"object_z_max":0.03546,"peak_contact_force":89.5439,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":476.0,"raw_peak_contact_force":243.0986,"subtask_id":"center_at_channel","tcp_end":[0.50005,0.01942,0.09759],"tcp_start":[0.48479,0.06683,0.10722],"tcp_to_object_dist_end":0.06963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":417.0,"n_steps_budget":990.0,"object_pos_end":[0.49599,-0.00178,0.02413],"object_pos_start":[0.49643,0.05069,0.03548],"object_to_goal_dist_end":0.07991,"object_to_goal_dist_start":0.13081,"object_z_max":0.04051,"peak_contact_force":305.91806,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":915.0,"raw_peak_contact_force":405.92766,"subtask_id":"traverse_channel","tcp_end":[0.50717,-0.08068,0.09624],"tcp_start":[0.50005,0.01942,0.09759],"tcp_to_object_dist_end":0.10747,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49461,-0.00055,0.02413],"object_pos_start":[0.49599,-0.00178,0.02413],"object_to_goal_dist_end":0.0812,"object_to_goal_dist_start":0.07991,"object_z_max":0.02472,"peak_contact_force":0.60162,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":564.0,"raw_peak_contact_force":121.58906,"tcp_end":[0.505,-0.0809,0.18532],"tcp_start":[0.50717,-0.08068,0.09624],"tcp_to_object_dist_end":0.1804,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93985,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.1826,"center_at_channel.align_height":0.09013,"descend_to_peg.descend_force":19.08823,"push_through_channel.push_distance":0.15878},"optimized_scores":{"best_composite_score":0.11422,"best_fitness_score":0.20422,"best_task_score":0.15145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":442.0,"contact_point_centroid":[0.52503,0.0012,0.05996],"force_p95":375.45159,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.98821,"mean_force":281.1732,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50577,-0.05352,0.09625]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.47499,0.06113,0.05999],"force_p95":229.33911,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.25897,"mean_force":95.56886,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5019,-0.0251,0.0963]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":115.0,"contact_point_centroid":[0.47498,0.11453,0.05998],"force_p95":168.31583,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.618,"mean_force":132.39916,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49148,0.0406,0.10488]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":237.0,"contact_point_centroid":[0.475,0.10186,0.05999],"force_p95":86.34766,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.11232,"mean_force":63.95798,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50725,-0.05789,0.09641]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.475,0.10419,0.06],"force_p95":127.95067,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.30398,"mean_force":97.77082,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50969,-0.06116,0.09675]},{"body_a":"peg","body_b":"channel_base_body","contact_count":170.0,"contact_point_centroid":[0.49657,0.05377,0.00936],"force_p95":92.55132,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.99414,"mean_force":16.11593,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49174,0.04005,0.1047]},{"body_a":"peg","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.49469,0.07124,0.0594],"force_p95":99.67207,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.85696,"mean_force":57.67553,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49841,0.02365,0.09887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.4942,-0.00536,0.00817],"force_p95":81.08929,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.36078,"mean_force":7.94725,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50518,-0.0467,0.09635]},{"body_a":"peg","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.49685,0.05234,0.06329],"force_p95":97.53267,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.23899,"mean_force":72.26004,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50138,0.00819,0.0972]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47497,0.11999,0.05996],"force_p95":57.54771,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.54771,"mean_force":57.54771,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48178,0.06147,0.11273]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52504,-0.0049,0.05995],"force_p95":9.83388,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11.56927,"mean_force":2.89232,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50967,-0.06119,0.09681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49323,-0.00965,0.0081],"force_p95":7.38932,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.34849,"mean_force":1.17654,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50749,-0.06148,0.14082]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":72.0,"contact_point_centroid":[0.47497,-0.01476,0.02483],"force_p95":9.39403,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.86189,"mean_force":4.61451,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50755,-0.06146,0.16436]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47499,-0.02619,0.02444],"force_p95":9.0917,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.23607,"mean_force":3.61056,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50304,-0.05472,0.09583]},{"body_a":"peg","body_b":"channel_base_body","contact_count":592.0,"contact_point_centroid":[0.49439,0.05889,0.00936],"force_p95":0.56469,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57092,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48056,0.14251,0.25316]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50217,0.22046,0.28755]}],"total_contact_groups":17},"final_pose_error":0.01113,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49284,-0.01025,0.02579],"final_tcp_position":[0.50755,-0.06144,0.18582],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":423.98821,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":621.0,"n_steps_budget":1000.0,"object_pos_end":[0.49423,0.05904,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54625,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":627.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46775,0.06872,0.22422],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.49393,0.05886,0.03396],"object_pos_start":[0.49423,0.05904,0.03388],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13929,"object_z_max":0.03396,"peak_contact_force":57.54771,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":590.0,"raw_peak_contact_force":57.54771,"subtask_id":"reach_peg","tcp_end":[0.48181,0.06146,0.11256],"tcp_start":[0.46775,0.06872,0.22422],"tcp_to_object_dist_end":0.07958,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":170.0,"n_steps_budget":600.0,"object_pos_end":[0.49599,0.04922,0.03484],"object_pos_start":[0.49393,0.05886,0.03396],"object_to_goal_dist_end":0.12939,"object_to_goal_dist_start":0.13912,"object_z_max":0.03481,"peak_contact_force":113.50493,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":331.0,"raw_peak_contact_force":223.618,"subtask_id":"center_at_channel","tcp_end":[0.50045,0.01859,0.09709],"tcp_start":[0.48181,0.06146,0.11256],"tcp_to_object_dist_end":0.06952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":544.0,"n_steps_budget":990.0,"object_pos_end":[0.49348,-0.00949,0.02413],"object_pos_start":[0.49599,0.04922,0.03484],"object_to_goal_dist_end":0.07257,"object_to_goal_dist_start":0.12939,"object_z_max":0.04057,"peak_contact_force":365.11109,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1307.0,"raw_peak_contact_force":423.98821,"subtask_id":"traverse_channel","tcp_end":[0.50971,-0.06114,0.09674],"tcp_start":[0.50045,0.01859,0.09709],"tcp_to_object_dist_end":0.09057,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49284,-0.01025,0.02579],"object_pos_start":[0.49348,-0.00949,0.02413],"object_to_goal_dist_end":0.07154,"object_to_goal_dist_start":0.07257,"object_z_max":0.02577,"peak_contact_force":6.9022,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":621.0,"raw_peak_contact_force":131.30398,"tcp_end":[0.50755,-0.06144,0.18582],"tcp_start":[0.50971,-0.06114,0.09674],"tcp_to_object_dist_end":0.16866,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95105,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.15475,"center_at_channel.align_height":0.13198,"descend_to_peg.descend_force":12.54255,"push_through_channel.push_distance":0.17136},"optimized_scores":{"best_composite_score":0.16367,"best_fitness_score":0.25367,"best_task_score":0.13127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":131.0,"contact_point_centroid":[0.52503,-0.01115,0.05995],"force_p95":457.3793,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":457.76145,"mean_force":356.14087,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51505,-0.07406,0.07858]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":365.0,"contact_point_centroid":[0.47496,0.11993,0.05996],"force_p95":136.55258,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.15808,"mean_force":72.89517,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50992,0.07556,0.07028]},{"body_a":"peg","body_b":"link7","contact_count":160.0,"contact_point_centroid":[0.50447,0.06251,0.06198],"force_p95":144.32948,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.76129,"mean_force":113.27847,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51437,0.00489,0.08501]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.5019,0.02355,0.00861],"force_p95":128.29645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.33979,"mean_force":48.19382,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51441,-0.02925,0.08238]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":422.0,"contact_point_centroid":[0.52501,0.11989,0.05964],"force_p95":123.17602,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.02644,"mean_force":67.82,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51077,0.0739,0.07084]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52504,-0.0124,0.05994],"force_p95":101.84436,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.37794,"mean_force":33.98087,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51727,-0.07673,0.07452]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":148.0,"contact_point_centroid":[0.52509,0.05258,0.04743],"force_p95":43.74568,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.8181,"mean_force":28.68144,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51427,0.00795,0.08495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.51039,0.07638,0.00954],"force_p95":33.58312,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.657,"mean_force":18.05443,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51072,0.07356,0.07115]},{"body_a":"attachment","body_b":"peg","contact_count":437.0,"contact_point_centroid":[0.50987,0.07856,0.05876],"force_p95":33.0331,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.25246,"mean_force":20.69255,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51012,0.07552,0.07016]},{"body_a":"peg","body_b":"channel_base_body","contact_count":548.0,"contact_point_centroid":[0.50592,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.11435,"mean_force":0.5916,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5181,0.08459,0.13372]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50668,0.09882,0.0587],"force_p95":24.65204,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.65204,"mean_force":24.65204,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50668,0.08073,0.07079]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":280.0,"contact_point_centroid":[0.52506,0.07973,0.04257],"force_p95":6.37078,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.54768,"mean_force":2.15394,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51277,0.07201,0.07069]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47492,-0.02277,0.0245],"force_p95":8.22112,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.27404,"mean_force":2.57635,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51317,-0.07269,0.08137]},{"body_a":"peg","body_b":"channel_base_body","contact_count":579.0,"contact_point_centroid":[0.50575,0.08087,0.00936],"force_p95":0.55712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57312,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50951,0.15225,0.241]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50277,0.2214,0.28712]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49974,-3e-05,0.00798],"force_p95":0.77009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77011,"mean_force":0.60563,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51472,-0.07685,0.11846]}],"total_contact_groups":16},"final_pose_error":0.01108,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50343,-0.00019,0.02406],"final_tcp_position":[0.5148,-0.07681,0.16374],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":457.76145,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5482,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":615.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.53065,0.08919,0.19755],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":548.0,"n_steps_budget":930.0,"object_pos_end":[0.50596,0.0809,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":25.11435,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":549.0,"raw_peak_contact_force":25.11435,"subtask_id":"reach_peg","tcp_end":[0.50664,0.08072,0.07056],"tcp_start":[0.53065,0.08919,0.19755],"tcp_to_object_dist_end":0.03679,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":515.0,"n_steps_budget":660.0,"object_pos_end":[0.50701,0.07944,0.03394],"object_pos_start":[0.50596,0.0809,0.03378],"object_to_goal_dist_end":0.15971,"object_to_goal_dist_start":0.16113,"object_z_max":0.03482,"peak_contact_force":0.54819,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2019.0,"raw_peak_contact_force":204.15808,"subtask_id":"center_at_channel","tcp_end":[0.51271,0.05156,0.08412],"tcp_start":[0.50664,0.08072,0.07056],"tcp_to_object_dist_end":0.05769,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.49613,0.00027,0.02404],"object_pos_start":[0.50701,0.07944,0.03394],"object_to_goal_dist_end":0.08193,"object_to_goal_dist_start":0.15971,"object_z_max":0.03817,"peak_contact_force":455.55766,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":803.0,"raw_peak_contact_force":457.76145,"subtask_id":"traverse_channel","tcp_end":[0.51731,-0.07667,0.07452],"tcp_start":[0.51271,0.05156,0.08412],"tcp_to_object_dist_end":0.09443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50343,-0.00019,0.02406],"object_pos_start":[0.49613,0.00027,0.02404],"object_to_goal_dist_end":0.08146,"object_to_goal_dist_start":0.08193,"object_z_max":0.02406,"peak_contact_force":0.52458,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":577.0,"raw_peak_contact_force":116.37794,"tcp_end":[0.5148,-0.07681,0.16374],"tcp_start":[0.51731,-0.07667,0.07452],"tcp_to_object_dist_end":0.15972,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```