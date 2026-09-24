## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1447 | 0.17 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1936 | 0.13 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1931 | 0.13 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1968 | 0.13 | ✅ accepted |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.1029 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.145) — your mutation base

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

- **Composite score**: 0.145
- **task_score** (E): 0.171
- **fitness_score**: 0.235  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1575 |
| descend_to_peg | 1.00 | 1.00 | 0.1107 |
| center_at_channel | 0.67 | 1.00 | 0.0434 |
| push_through_channel | 0.67 | 1.00 | 0.1139 |
| retract_up | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.077, 0.206) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.077, 0.206)→(0.491, 0.069, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 45.384 | 45.384 |
| center_at_channel | align | 0.67 / step_budget | (0.491, 0.069, 0.097)→(0.503, 0.030, 0.094) | (0.498, 0.068, 0.034)→(0.500, 0.061, 0.035) | 0.148→0.141 | 1.00 / 2.333 | 51.867 | 212.941 |
| push_through_channel | push | 0.67 / step_budget | (0.503, 0.030, 0.094)→(0.509, -0.084, 0.089) | (0.500, 0.061, 0.035)→(0.497, -0.006, 0.024) | 0.141→0.076 | 1.00 / 2.333 | 333.943 | 388.545 |
| retract_up | retract | 1.00 / step_budget | (0.509, -0.084, 0.089)→(0.507, -0.084, 0.179) | (0.497, -0.006, 0.024)→(0.496, -0.006, 0.024) | 0.076→0.076 | 1.00 / 1.000 | 0.651 | 124.733 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.431
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.258
- phase_score: 0.248
- phase_breakdown.center_at_channel_score: 0.000
- phase_breakdown.reach_peg_score: 0.188
- phase_breakdown.traverse_channel_score: 0.314

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.252
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.258
- **Median Q (composite search score)**: 0.158
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.426


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94161,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.16116,"center_at_channel.align_height":0.09347,"descend_to_peg.descend_force":10.62393,"push_through_channel.push_distance":0.1826},"optimized_scores":{"best_composite_score":0.16214,"best_fitness_score":0.25214,"best_task_score":0.25841},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":508.0,"contact_point_centroid":[0.52504,-0.0111,0.05994],"force_p95":497.26555,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":522.81292,"mean_force":326.57856,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50645,-0.06599,0.09639]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":157.0,"contact_point_centroid":[0.47498,0.11822,0.05997],"force_p95":206.80176,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":240.28708,"mean_force":139.6653,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49302,0.05078,0.10304]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.47499,0.06532,0.05999],"force_p95":143.56865,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.79051,"mean_force":84.98364,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50161,-0.02081,0.09654]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":305.0,"contact_point_centroid":[0.475,0.09396,0.05999],"force_p95":90.15355,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.68696,"mean_force":53.51962,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50718,-0.06693,0.09651]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.475,0.092,0.06],"force_p95":134.0266,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.0266,"mean_force":134.0266,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51012,-0.07327,0.09665]},{"body_a":"peg","body_b":"channel_base_body","contact_count":607.0,"contact_point_centroid":[0.49727,-0.00259,0.00812],"force_p95":73.43775,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.38404,"mean_force":6.07491,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50566,-0.05759,0.09647]},{"body_a":"peg","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.49654,0.05402,0.06386],"force_p95":95.43247,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.01912,"mean_force":70.54984,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50107,0.01017,0.09738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":220.0,"contact_point_centroid":[0.49667,0.05888,0.00943],"force_p95":82.91319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.70256,"mean_force":15.74389,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49386,0.04775,0.10248]},{"body_a":"peg","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.4956,0.07411,0.05984],"force_p95":87.61407,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.46706,"mean_force":63.24812,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49893,0.02662,0.09854]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47498,0.11997,0.05996],"force_p95":51.1412,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.1412,"mean_force":51.1412,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4867,0.06613,0.10688]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52506,-0.01695,0.05991],"force_p95":13.61409,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":17.01762,"mean_force":3.40352,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51007,-0.07331,0.09672]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49537,-0.00504,0.00806],"force_p95":0.66872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.97909,"mean_force":0.62026,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50787,-0.07354,0.14079]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,0.01909,0.02424],"force_p95":7.3945,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.62588,"mean_force":2.4476,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50941,-0.07343,0.09845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":588.0,"contact_point_centroid":[0.49535,0.06398,0.00937],"force_p95":0.57665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56003,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48651,0.14493,0.24397]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5039,0.21522,0.29289]},{"body_a":"peg","body_b":"channel_base_body","contact_count":490.0,"contact_point_centroid":[0.49503,0.06367,0.0094],"force_p95":0.55083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54533,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48278,0.06929,0.15472]}],"total_contact_groups":16},"final_pose_error":0.0108,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49615,-0.00506,0.02415],"final_tcp_position":[0.50796,-0.07351,0.18607],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":522.81292,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":615.0,"n_steps_budget":1000.0,"object_pos_end":[0.49492,0.06374,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14396,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54836,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":616.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.48057,0.07318,0.20414],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":490.0,"n_steps_budget":960.0,"object_pos_end":[0.49529,0.06367,0.03402],"object_pos_start":[0.49492,0.06374,0.03395],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14396,"object_z_max":0.03402,"peak_contact_force":51.1412,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":491.0,"raw_peak_contact_force":51.1412,"subtask_id":"reach_peg","tcp_end":[0.48672,0.06612,0.10673],"tcp_start":[0.48057,0.07318,0.20414],"tcp_to_object_dist_end":0.07325,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":220.0,"n_steps_budget":600.0,"object_pos_end":[0.49698,0.05057,0.03534],"object_pos_start":[0.49529,0.06367,0.03402],"object_to_goal_dist_end":0.13069,"object_to_goal_dist_start":0.14387,"object_z_max":0.03532,"peak_contact_force":80.95531,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":430.0,"raw_peak_contact_force":240.28708,"subtask_id":"center_at_channel","tcp_end":[0.50034,0.01961,0.09732],"tcp_start":[0.48672,0.06612,0.10673],"tcp_to_object_dist_end":0.06937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.49406,-0.00519,0.02409],"object_pos_start":[0.49698,0.05057,0.03534],"object_to_goal_dist_end":0.07671,"object_to_goal_dist_start":0.13069,"object_z_max":0.04056,"peak_contact_force":503.23414,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1508.0,"raw_peak_contact_force":522.81292,"subtask_id":"traverse_channel","tcp_end":[0.51012,-0.07327,0.09665],"tcp_start":[0.50034,0.01961,0.09732],"tcp_to_object_dist_end":0.10078,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.49615,-0.00506,0.02415],"object_pos_start":[0.49406,-0.00519,0.02409],"object_to_goal_dist_end":0.07669,"object_to_goal_dist_start":0.07671,"object_z_max":0.02433,"peak_contact_force":0.56826,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":583.0,"raw_peak_contact_force":134.0266,"tcp_end":[0.50796,-0.07351,0.18607],"tcp_start":[0.51012,-0.07327,0.09665],"tcp_to_object_dist_end":0.17619,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93798,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.17176,"center_at_channel.align_height":0.09537,"descend_to_peg.descend_force":17.83337,"push_through_channel.push_distance":0.14018},"optimized_scores":{"best_composite_score":0.1138,"best_fitness_score":0.2038,"best_task_score":0.14246},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":85.0,"contact_point_centroid":[0.47499,0.11408,0.05998],"force_p95":155.93686,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.53539,"mean_force":114.34449,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.48868,0.04364,0.1074]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.47499,0.03331,0.05999],"force_p95":137.87194,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.95838,"mean_force":119.87685,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49909,-0.05007,0.09877]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47499,-0.00788,0.05999],"force_p95":130.69545,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.32615,"mean_force":83.26204,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49957,-0.09171,0.09837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":193.0,"contact_point_centroid":[0.4957,0.00623,0.00864],"force_p95":92.88096,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.07642,"mean_force":26.3721,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49902,-0.03519,0.09918]},{"body_a":"peg","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.49545,0.05025,0.06289],"force_p95":97.57662,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.69951,"mean_force":72.14535,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49855,0.00378,0.1]},{"body_a":"peg","body_b":"channel_base_body","contact_count":148.0,"contact_point_centroid":[0.49551,0.05517,0.00941],"force_p95":85.3245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.43715,"mean_force":14.34477,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.48954,0.0414,0.10672]},{"body_a":"peg","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.49449,0.07308,0.05881],"force_p95":91.39324,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.33677,"mean_force":70.62917,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49604,0.02314,0.1011]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47496,0.11999,0.05995],"force_p95":63.43536,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.43536,"mean_force":63.43536,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4809,0.06162,0.11333]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49345,-0.00699,0.00806],"force_p95":0.71699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.76755,"mean_force":0.62191,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4974,-0.09168,0.14246]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,-0.03186,0.02416],"force_p95":8.40701,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.29454,"mean_force":3.36041,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49711,-0.09162,0.1235]},{"body_a":"peg","body_b":"channel_base_body","contact_count":597.0,"contact_point_centroid":[0.49441,0.05902,0.00936],"force_p95":0.56412,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57071,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48055,0.14238,0.24858]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50221,0.22049,0.28755]},{"body_a":"peg","body_b":"channel_base_body","contact_count":537.0,"contact_point_centroid":[0.49416,0.05894,0.00939],"force_p95":0.55011,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54589,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47337,0.06464,0.16272]}],"total_contact_groups":13},"final_pose_error":0.01109,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49311,-0.00704,0.02412],"final_tcp_position":[0.49748,-0.09151,0.18745],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":199.53539,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05904,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1393,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54246,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":632.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46762,0.06842,0.21403],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.49401,0.05913,0.03395],"object_pos_start":[0.49402,0.05904,0.03388],"object_to_goal_dist_end":0.13939,"object_to_goal_dist_start":0.1393,"object_z_max":0.03395,"peak_contact_force":63.43536,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":538.0,"raw_peak_contact_force":63.43536,"subtask_id":"reach_peg","tcp_end":[0.48093,0.06162,0.11315],"tcp_start":[0.46762,0.06842,0.21403],"tcp_to_object_dist_end":0.08031,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":148.0,"n_steps_budget":600.0,"object_pos_end":[0.49582,0.05208,0.03442],"object_pos_start":[0.49401,0.05913,0.03395],"object_to_goal_dist_end":0.13226,"object_to_goal_dist_start":0.13939,"object_z_max":0.0344,"peak_contact_force":74.10492,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":262.0,"raw_peak_contact_force":199.53539,"subtask_id":"center_at_channel","tcp_end":[0.49745,0.01914,0.09988],"tcp_start":[0.48093,0.06162,0.11315],"tcp_to_object_dist_end":0.0733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":209.0,"n_steps_budget":900.0,"object_pos_end":[0.49503,-0.00692,0.02416],"object_pos_start":[0.49582,0.05208,0.03442],"object_to_goal_dist_end":0.07494,"object_to_goal_dist_start":0.13226,"object_z_max":0.04012,"peak_contact_force":1.41393,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":324.0,"raw_peak_contact_force":139.95838,"subtask_id":"traverse_channel","tcp_end":[0.49962,-0.09132,0.09834],"tcp_start":[0.49745,0.01914,0.09988],"tcp_to_object_dist_end":0.11246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49311,-0.00704,0.02412],"object_pos_start":[0.49503,-0.00692,0.02416],"object_to_goal_dist_end":0.07498,"object_to_goal_dist_start":0.07494,"object_z_max":0.02441,"peak_contact_force":0.65776,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":549.0,"raw_peak_contact_force":137.32615,"tcp_end":[0.49748,-0.09151,0.18745],"tcp_start":[0.49962,-0.09132,0.09834],"tcp_to_object_dist_end":0.18393,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95139,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.1579,"center_at_channel.align_height":0.13194,"descend_to_peg.descend_force":8.14644,"push_through_channel.push_distance":0.18338},"optimized_scores":{"best_composite_score":0.15831,"best_fitness_score":0.24831,"best_task_score":0.11209},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":157.0,"contact_point_centroid":[0.52504,-0.02032,0.05994],"force_p95":502.20186,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":502.86519,"mean_force":383.49967,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51544,-0.08341,0.07807]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":361.0,"contact_point_centroid":[0.47497,0.11995,0.05997],"force_p95":148.03051,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.00036,"mean_force":73.97022,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50982,0.07568,0.07031]},{"body_a":"peg","body_b":"link7","contact_count":174.0,"contact_point_centroid":[0.50453,0.06007,0.06167],"force_p95":147.0717,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.48337,"mean_force":115.80127,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51439,0.00161,0.08543]},{"body_a":"peg","body_b":"channel_base_body","contact_count":396.0,"contact_point_centroid":[0.50269,0.01754,0.00864],"force_p95":131.35038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":138.82526,"mean_force":47.21156,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51458,-0.0374,0.08227]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":418.0,"contact_point_centroid":[0.52501,0.11991,0.05965],"force_p95":123.18853,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.14883,"mean_force":67.59123,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.5108,0.07387,0.07089]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52504,-0.02141,0.05993],"force_p95":90.56165,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.84696,"mean_force":30.94796,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51799,-0.08614,0.07309]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":167.0,"contact_point_centroid":[0.52512,0.05046,0.04649],"force_p95":44.70583,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.22916,"mean_force":28.6213,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51423,0.00517,0.08538]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.51061,0.07642,0.00954],"force_p95":33.04855,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.90342,"mean_force":17.40194,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51069,0.07356,0.07121]},{"body_a":"attachment","body_b":"peg","contact_count":439.0,"contact_point_centroid":[0.50985,0.0786,0.0588],"force_p95":32.49595,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.53184,"mean_force":19.90077,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51011,0.07551,0.0702]},{"body_a":"peg","body_b":"channel_base_body","contact_count":558.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.5746,"mean_force":0.58445,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5181,0.08459,0.13524]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50664,0.0988,0.05878],"force_p95":21.14671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.14671,"mean_force":21.14671,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50665,0.08071,0.07095]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":274.0,"contact_point_centroid":[0.52506,0.07959,0.04311],"force_p95":6.46473,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.73177,"mean_force":2.26479,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51265,0.07245,0.07046]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50226,-0.00536,0.00803],"force_p95":0.72554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.53369,"mean_force":0.63281,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51548,-0.08618,0.11698]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47487,-0.02826,0.02494],"force_p95":8.39912,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.40149,"mean_force":2.33535,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51258,-0.0778,0.08185]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52504,0.01801,0.02441],"force_p95":8.02576,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.18819,"mean_force":2.28206,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51602,-0.08627,0.08079]},{"body_a":"peg","body_b":"channel_base_body","contact_count":578.0,"contact_point_centroid":[0.50575,0.0809,0.00936],"force_p95":0.55714,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57316,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5095,0.15231,0.24235]}],"total_contact_groups":17},"final_pose_error":0.0114,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49908,-0.00514,0.02409],"final_tcp_position":[0.51551,-0.08615,0.16198],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":502.86519,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54612,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":614.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.53067,0.0892,0.20045],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":558.0,"n_steps_budget":930.0,"object_pos_end":[0.50598,0.08085,0.03377],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16108,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":21.5746,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":559.0,"raw_peak_contact_force":21.5746,"subtask_id":"reach_peg","tcp_end":[0.50661,0.0807,0.07072],"tcp_start":[0.53067,0.0892,0.20045],"tcp_to_object_dist_end":0.03695,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":660.0,"object_pos_end":[0.50699,0.0794,0.03397],"object_pos_start":[0.50598,0.08085,0.03377],"object_to_goal_dist_end":0.15967,"object_to_goal_dist_start":0.16108,"object_z_max":0.03477,"peak_contact_force":0.54044,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2007.0,"raw_peak_contact_force":199.00036,"subtask_id":"center_at_channel","tcp_end":[0.51265,0.05101,0.08448],"tcp_start":[0.50661,0.0807,0.07072],"tcp_to_object_dist_end":0.05822,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.50269,-0.00551,0.02409],"object_pos_start":[0.50699,0.0794,0.03397],"object_to_goal_dist_end":0.07622,"object_to_goal_dist_start":0.15967,"object_z_max":0.0381,"peak_contact_force":497.18083,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":910.0,"raw_peak_contact_force":502.86519,"subtask_id":"traverse_channel","tcp_end":[0.51803,-0.08608,0.0731],"tcp_start":[0.51265,0.05101,0.08448],"tcp_to_object_dist_end":0.09554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49908,-0.00514,0.02409],"object_pos_start":[0.50269,-0.00551,0.02409],"object_to_goal_dist_end":0.07654,"object_to_goal_dist_start":0.07622,"object_z_max":0.02471,"peak_contact_force":0.72552,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":555.0,"raw_peak_contact_force":102.84696,"tcp_end":[0.51551,-0.08615,0.16198],"tcp_start":[0.51803,-0.08608,0.0731],"tcp_to_object_dist_end":0.16077,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```