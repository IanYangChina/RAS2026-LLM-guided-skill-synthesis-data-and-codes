## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1107 | 0.04 | ❌ rejected |
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1482 | 0.18 | ✅ accepted |
| 5 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0612 | 0.00 | ❌ rejected |
| 4 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1447 | 0.17 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1936 | 0.13 | ❌ rejected |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.111) — your mutation base

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

- **Composite score**: -0.111
- **task_score** (E): 0.037
- **fitness_score**: 0.029  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 0.00 | 1.00 | 0.1196 |
| descend_to_peg | 1.00 | 1.00 | 0.0000 |
| center_at_channel | 0.00 | 1.00 | 0.0364 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |
| retract_up | 1.00 | 1.00 | 0.0893 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.479, 0.084, 0.282) | (0.494, 0.068, 0.040)→(0.501, 0.063, 0.035) | 0.151→0.143 | 1.00 / 3.667 | 343.201 | 735.543 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.479, 0.084, 0.282)→(0.479, 0.084, 0.282) | (0.501, 0.063, 0.035)→(0.501, 0.063, 0.035) | 0.143→0.143 | 1.00 / 3.667 | 60.585 | 60.585 |
| center_at_channel | align | 0.00 / step_budget | (0.479, 0.084, 0.282)→(0.460, 0.069, 0.274) | (0.501, 0.063, 0.035)→(0.507, 0.047, 0.034) | 0.143→0.127 | 1.00 / 4.667 | 564.149 | 703.173 |
| push_through_channel | push | 0.00 / guard_failure | (0.460, 0.069, 0.274)→(0.460, 0.069, 0.274) | (0.507, 0.047, 0.034)→(0.507, 0.047, 0.034) | 0.127→0.127 | 1.00 / 3.333 | 56.765 | 221.206 |
| retract_up | retract | 1.00 / step_budget | (0.460, 0.069, 0.274)→(0.460, 0.068, 0.363) | (0.507, 0.047, 0.034)→(0.507, 0.046, 0.034) | 0.127→0.127 | 1.00 / 1.333 | 1.120 | 99.539 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.215
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.077
- phase_score: 0.026
- phase_breakdown.center_at_channel_score: 0.000
- phase_breakdown.reach_peg_score: 0.156
- phase_breakdown.traverse_channel_score: 0.004

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.047
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.077
- **Median Q (composite search score)**: -0.112
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.229


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.23469,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.16964,"center_at_channel.align_height":0.07672,"descend_to_peg.descend_force":12.30124,"push_through_channel.push_distance":0.17612,"push_through_channel.push_speed":0.0643},"optimized_scores":{"best_composite_score":-0.09344,"best_fitness_score":0.04656,"best_task_score":0.07731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link6","contact_count":603.0,"contact_point_centroid":[0.47491,0.0942,0.05981],"force_p95":380.40793,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":757.61905,"mean_force":292.60182,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49515,0.1391,0.26509]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":398.0,"contact_point_centroid":[0.52503,0.09702,0.05991],"force_p95":628.17763,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":682.83345,"mean_force":326.52093,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52616,0.16299,0.26515]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":997.0,"contact_point_centroid":[0.52505,0.07106,0.05989],"force_p95":655.32592,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":674.331,"mean_force":610.84319,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.44694,0.07062,0.27535]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":456.0,"contact_point_centroid":[0.475,0.0881,0.06],"force_p95":191.5861,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":514.37996,"mean_force":95.77798,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.44146,0.0706,0.2737]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.52506,0.06865,0.05989],"force_p95":215.57369,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.6515,"mean_force":156.29757,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.43477,0.05897,0.27111]},{"body_a":"peg","body_b":"link6","contact_count":426.0,"contact_point_centroid":[0.49818,0.08269,0.05719],"force_p95":100.61343,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.9949,"mean_force":56.1562,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48314,0.09101,0.28367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":885.0,"contact_point_centroid":[0.49819,0.07,0.00932],"force_p95":66.26894,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":168.74255,"mean_force":27.55615,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4973,0.15157,0.25678]},{"body_a":"peg","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.50202,0.057,0.05833],"force_p95":59.94486,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.28557,"mean_force":28.50503,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.44699,0.07063,0.27536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50799,0.04677,0.00949],"force_p95":60.42347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.10039,"mean_force":28.4227,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.44699,0.07063,0.27536]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.52503,0.06886,0.05994],"force_p95":128.29621,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.52112,"mean_force":110.12311,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.43479,0.05921,0.27125]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.475,0.08874,0.06],"force_p95":88.80288,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.80288,"mean_force":88.80288,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.43476,0.05893,0.27108]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50539,0.0685,0.00917],"force_p95":51.20798,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.20798,"mean_force":51.20798,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47344,0.06827,0.28262]},{"body_a":"peg","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.50576,0.07846,0.05609],"force_p95":50.68357,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.68357,"mean_force":50.68357,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47344,0.06827,0.28262]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52503,0.07293,0.0599],"force_p95":41.8664,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.8664,"mean_force":41.8664,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47344,0.06827,0.28262]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.475,0.06809,0.05999],"force_p95":32.85605,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.85605,"mean_force":32.85605,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47344,0.06827,0.28262]},{"body_a":"peg","body_b":"channel_base_body","contact_count":572.0,"contact_point_centroid":[0.50603,0.02889,0.00942],"force_p95":0.57624,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.89332,"mean_force":0.68287,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.43463,0.06292,0.31436]}],"total_contact_groups":23},"final_pose_error":0.01009,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50643,0.0294,0.03389],"final_tcp_position":[0.43463,0.05891,0.36108],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":3920.03648,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":912.0,"n_steps_budget":1000.0,"object_pos_end":[0.50195,0.0568,0.03663],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":247.83959,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2340.0,"raw_peak_contact_force":757.61905,"subtask_id":"reach_peg","tcp_end":[0.47344,0.06827,0.28262],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2479,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50195,0.05678,0.03665],"object_pos_start":[0.50195,0.0568,0.03663],"object_to_goal_dist_end":0.13683,"object_to_goal_dist_start":0.13686,"object_z_max":0.03663,"peak_contact_force":51.20798,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":51.20798,"subtask_id":"reach_peg","tcp_end":[0.47345,0.06826,0.28264],"tcp_start":[0.47344,0.06827,0.28262],"tcp_to_object_dist_end":0.2479,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50752,0.03012,0.03436],"object_pos_start":[0.50195,0.05678,0.03665],"object_to_goal_dist_end":0.11052,"object_to_goal_dist_start":0.13683,"object_z_max":0.0371,"peak_contact_force":650.88577,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4143.0,"raw_peak_contact_force":674.331,"subtask_id":"center_at_channel","tcp_end":[0.43476,0.05893,0.27108],"tcp_start":[0.47345,0.06826,0.28264],"tcp_to_object_dist_end":0.24932,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50751,0.0301,0.03436],"object_pos_start":[0.50752,0.03012,0.03436],"object_to_goal_dist_end":0.1105,"object_to_goal_dist_start":0.11052,"object_z_max":0.03436,"peak_contact_force":118.36781,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":13.0,"raw_peak_contact_force":225.6515,"subtask_id":"traverse_channel","tcp_end":[0.43479,0.05909,0.27117],"tcp_start":[0.43477,0.05902,0.27113],"tcp_to_object_dist_end":0.24942,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50643,0.0294,0.03389],"object_pos_start":[0.50749,0.03008,0.03436],"object_to_goal_dist_end":0.10976,"object_to_goal_dist_start":0.11048,"object_z_max":0.03532,"peak_contact_force":0.54398,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":590.0,"raw_peak_contact_force":131.52112,"tcp_end":[0.43463,0.05891,0.36108],"tcp_start":[0.43479,0.05909,0.27117],"tcp_to_object_dist_end":0.33627,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.1494,"center_at_channel.align_height":0.07316,"descend_to_peg.descend_force":11.30359,"push_through_channel.push_distance":0.17652,"push_through_channel.push_speed":0.05368},"optimized_scores":{"best_composite_score":-0.11212,"best_fitness_score":0.02788,"best_task_score":0.03119},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link6","contact_count":757.0,"contact_point_centroid":[0.47491,0.09568,0.05983],"force_p95":386.02987,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":764.1278,"mean_force":317.1852,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49315,0.13918,0.26625]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":998.0,"contact_point_centroid":[0.52505,0.07197,0.0599],"force_p95":686.92292,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":723.65406,"mean_force":627.74113,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.44472,0.07464,0.27465]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":287.0,"contact_point_centroid":[0.52503,0.10131,0.05991],"force_p95":640.55436,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":680.00789,"mean_force":346.61329,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.53566,0.18264,0.25747]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":333.0,"contact_point_centroid":[0.475,0.08755,0.06],"force_p95":246.13631,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":298.78767,"mean_force":143.36217,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.44223,0.07712,0.27394]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.52504,0.06726,0.05992],"force_p95":218.95645,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.90584,"mean_force":179.00326,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.43592,0.06223,0.27205]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.51047,0.03695,0.00976],"force_p95":29.46006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.00828,"mean_force":10.60868,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.44475,0.07465,0.27466]},{"body_a":"peg","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.50081,0.05267,0.05933],"force_p95":28.99714,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.45336,"mean_force":10.42972,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.44475,0.07465,0.27466]},{"body_a":"peg","body_b":"link6","contact_count":203.0,"contact_point_centroid":[0.49773,0.07252,0.05825],"force_p95":42.00215,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":158.14308,"mean_force":30.90204,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.46982,0.07793,0.28309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49558,0.05864,0.00937],"force_p95":34.98964,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.74939,"mean_force":7.00127,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49423,0.15026,0.25798]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.52502,0.06749,0.05996],"force_p95":139.57309,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.35719,"mean_force":134.56432,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4359,0.06243,0.27215]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.47499,0.07749,0.05997],"force_p95":51.94641,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.94641,"mean_force":51.94641,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47132,0.07433,0.28223]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52503,0.07833,0.05991],"force_p95":48.8391,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.8391,"mean_force":48.8391,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47132,0.07433,0.28223]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50766,0.0627,0.00925],"force_p95":31.0106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.0106,"mean_force":31.0106,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47132,0.07433,0.28223]},{"body_a":"peg","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.50005,0.06757,0.05777],"force_p95":30.4852,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.4852,"mean_force":30.4852,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47132,0.07433,0.28223]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":658.0,"contact_point_centroid":[0.52514,0.03146,0.04008],"force_p95":3.12035,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.93643,"mean_force":1.60849,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.43692,0.07224,0.27216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4976,0.19305,0.27739]}],"total_contact_groups":21},"final_pose_error":0.01046,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,0.03003,0.03378],"final_tcp_position":[0.43574,0.0622,0.36166],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":764.1278,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49651,0.05011,0.0335],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13032,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":271.48836,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2253.0,"raw_peak_contact_force":764.1278,"subtask_id":"reach_peg","tcp_end":[0.47132,0.07433,0.28223],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25117,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49651,0.05009,0.03351],"object_pos_start":[0.49651,0.05011,0.0335],"object_to_goal_dist_end":0.1303,"object_to_goal_dist_start":0.13032,"object_z_max":0.0335,"peak_contact_force":51.94641,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":51.94641,"subtask_id":"reach_peg","tcp_end":[0.47134,0.07432,0.28224],"tcp_start":[0.47132,0.07433,0.28223],"tcp_to_object_dist_end":0.25117,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50706,0.03002,0.03485],"object_pos_start":[0.49651,0.05009,0.03351],"object_to_goal_dist_end":0.11037,"object_to_goal_dist_start":0.1303,"object_z_max":0.03485,"peak_contact_force":653.05971,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3989.0,"raw_peak_contact_force":723.65406,"subtask_id":"center_at_channel","tcp_end":[0.43592,0.06218,0.27203],"tcp_start":[0.47134,0.07432,0.28224],"tcp_to_object_dist_end":0.2497,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50706,0.03002,0.03484],"object_pos_start":[0.50706,0.03002,0.03485],"object_to_goal_dist_end":0.11037,"object_to_goal_dist_start":0.11037,"object_z_max":0.03485,"peak_contact_force":10.68889,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":224.90584,"subtask_id":"traverse_channel","tcp_end":[0.4359,0.06236,0.27211],"tcp_start":[0.43591,0.06229,0.27208],"tcp_to_object_dist_end":0.24981,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50699,0.03003,0.03378],"object_pos_start":[0.50706,0.03001,0.03484],"object_to_goal_dist_end":0.11043,"object_to_goal_dist_start":0.11036,"object_z_max":0.03484,"peak_contact_force":2.277,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":708.0,"raw_peak_contact_force":140.35719,"tcp_end":[0.43574,0.0622,0.36166],"tcp_start":[0.4359,0.06236,0.27211],"tcp_to_object_dist_end":0.33707,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05051,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.15118,"center_at_channel.align_height":0.07058,"descend_to_peg.descend_force":15.13481,"push_through_channel.push_distance":0.17075,"push_through_channel.push_speed":0.06366},"optimized_scores":{"best_composite_score":-0.12654,"best_fitness_score":0.01346,"best_task_score":0.00204},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":988.0,"contact_point_centroid":[0.52527,0.11855,0.05994],"force_p95":671.14659,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":711.53431,"mean_force":597.32103,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49691,0.10022,0.27924]},{"body_a":"channel_left_wall","body_b":"link5","contact_count":207.0,"contact_point_centroid":[0.55128,0.03823,0.05994],"force_p95":431.89087,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":708.85348,"mean_force":305.57339,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.5017,0.09418,0.27839]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":298.0,"contact_point_centroid":[0.47486,0.11752,0.05982],"force_p95":449.76816,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":684.88285,"mean_force":241.51639,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48058,0.13265,0.26801]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":740.0,"contact_point_centroid":[0.52503,0.11994,0.05989],"force_p95":596.99583,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":653.87061,"mean_force":462.85014,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49678,0.13537,0.27713]},{"body_a":"channel_left_wall","body_b":"link5","contact_count":158.0,"contact_point_centroid":[0.54583,0.01973,0.05998],"force_p95":297.24569,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.60959,"mean_force":196.54586,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48964,0.10761,0.27974]},{"body_a":"channel_left_wall","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.52829,0.06495,0.05997],"force_p95":213.05959,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.05959,"mean_force":213.05959,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51002,0.08457,0.27766]},{"body_a":"peg","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.49044,0.08334,0.0588],"force_p95":22.26199,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":187.52505,"mean_force":19.40068,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50781,0.08704,0.27769]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.525,0.06515,0.05995],"force_p95":166.23355,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.98268,"mean_force":87.49134,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51004,0.08455,0.27771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50635,0.08053,0.00939],"force_p95":12.73043,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.25744,"mean_force":1.93272,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49697,0.10015,0.27923]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":51.0,"contact_point_centroid":[0.52534,0.08018,0.03879],"force_p95":36.71009,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.29467,"mean_force":8.8596,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50861,0.08608,0.27767]},{"body_a":"channel_left_wall","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.54621,0.02029,0.06],"force_p95":78.5999,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.5999,"mean_force":78.5999,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49305,0.10803,0.28043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52561,0.08178,0.00937],"force_p95":38.42866,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.23871,"mean_force":18.3484,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51005,0.08454,0.27775]},{"body_a":"peg","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.49373,0.08217,0.05871],"force_p95":38.05416,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.94103,"mean_force":17.6822,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51005,0.08454,0.27775]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52502,0.11997,0.05993],"force_p95":33.0158,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.0158,"mean_force":33.0158,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49305,0.10803,0.28043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50547,0.08005,0.00943],"force_p95":0.59194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.73756,"mean_force":0.62486,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50987,0.08399,0.32126]},{"body_a":"peg","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.49379,0.08209,0.05869],"force_p95":23.86036,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.31706,"mean_force":9.14175,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51009,0.08448,0.2779]}],"total_contact_groups":21},"final_pose_error":0.01146,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,0.07985,0.03378],"final_tcp_position":[0.51021,0.08377,0.36644],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":6272.10721,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":915.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":510.27452,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2118.0,"raw_peak_contact_force":684.88285,"subtask_id":"reach_peg","tcp_end":[0.49305,0.10803,0.28043],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24848,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":78.5999,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":78.5999,"subtask_id":"reach_peg","tcp_end":[0.49302,0.10801,0.28045],"tcp_start":[0.49305,0.10803,0.28043],"tcp_to_object_dist_end":0.2485,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50788,0.08002,0.03388],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16033,"object_to_goal_dist_start":0.16113,"object_z_max":0.03436,"peak_contact_force":388.50214,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2328.0,"raw_peak_contact_force":711.53431,"subtask_id":"center_at_channel","tcp_end":[0.51002,0.08457,0.27766],"tcp_start":[0.49302,0.10801,0.28045],"tcp_to_object_dist_end":0.24382,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5079,0.08002,0.03387],"object_pos_start":[0.50788,0.08002,0.03388],"object_to_goal_dist_end":0.16033,"object_to_goal_dist_start":0.16033,"object_z_max":0.03388,"peak_contact_force":41.23871,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":213.05959,"subtask_id":"traverse_channel","tcp_end":[0.51008,0.08449,0.27788],"tcp_start":[0.51007,0.08451,0.27784],"tcp_to_object_dist_end":0.24406,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50699,0.07985,0.03378],"object_pos_start":[0.50791,0.08001,0.03383],"object_to_goal_dist_end":0.16013,"object_to_goal_dist_start":0.16032,"object_z_max":0.03437,"peak_contact_force":0.5395,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":785.0,"raw_peak_contact_force":26.73756,"tcp_end":[0.51021,0.08377,0.36644],"tcp_start":[0.51008,0.08449,0.27788],"tcp_to_object_dist_end":0.3327,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```