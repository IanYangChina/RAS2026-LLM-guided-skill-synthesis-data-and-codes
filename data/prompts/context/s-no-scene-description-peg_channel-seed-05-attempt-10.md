## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → grasp → lift → rotate → approach → descend → push → retract | linear_cartesian | — | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2305 | 0.00 | ❌ rejected |
| 9 | grasp → lift → approach → descend → push → retract | — | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1643 | 0.12 | ❌ rejected |
| 8 | grasp → approach → descend → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0869 | 0.14 | ✅ accepted |
| 7 | grasp → approach → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0715 | 0.12 | ✅ accepted |
| 6 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.231) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_channel_entry
  offset:
  - 0.0
  - 0.16
  - 0.05
  weight: 0.3
- id: push_through_channel
  metric: goal_progress
  weight: 0.7
phases:
- id: grasp_0
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - 0.05
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_channel_entry
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_limit:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 35.0
      binds_to:
      - path: guards.push_guard.threshold
        mode: replace
  guards:
  - id: push_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.0
    - 0.01
  subtask_id: push_through_channel
- id: retract_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retraction_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **grasp_0** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, 0.05], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_limit: status=consumed; consumers=guards.push_guard.threshold (replace)
  - guards:
    - id=push_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.0, 0.01]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retraction_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.231
- **task_score** (E): 0.002
- **fitness_score**: 0.249  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1840 |
| grasp_peg_action | 1.00 | 1.00 | 0.0100 |
| lift_peg | 1.00 | 1.00 | 0.1458 |
| align_peg | 1.00 | 1.00 | 0.0230 |
| approach_channel | 1.00 | 1.00 | 0.1850 |
| descend_into_channel | 1.00 | 1.00 | 0.0492 |
| push_through | 0.67 | 1.00 | 0.0947 |
| retract | 1.00 | 1.00 | 0.1438 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.101, 0.146) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.547 | 2.488 |
| grasp_peg_action | grasp | 1.00 / step_budget | (0.509, 0.101, 0.146)→(0.503, 0.100, 0.138) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.552 | 0.588 |
| lift_peg | lift | 1.00 / step_budget | (0.503, 0.100, 0.138)→(0.501, 0.100, 0.284) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.554 | 0.591 |
| align_peg | rotate | 1.00 / step_budget | (0.501, 0.100, 0.284)→(0.494, 0.121, 0.279) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.545 | 0.579 |
| approach_channel | approach | 1.00 / step_budget | (0.494, 0.121, 0.279)→(0.496, 0.082, 0.099) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.543 | 0.587 |
| descend_into_channel | descend | 1.00 / step_budget | (0.496, 0.082, 0.099)→(0.499, 0.080, 0.050) | (0.504, 0.095, 0.034)→(0.506, 0.097, 0.033) | 0.175→0.177 | 1.00 / 2.000 | 59.608 | 110.748 |
| push_through | push | 0.67 / step_budget | (0.499, 0.080, 0.050)→(0.499, -0.014, 0.041) | (0.506, 0.097, 0.033)→(0.506, 0.095, 0.033) | 0.177→0.176 | 1.00 / 1.667 | 40.115 | 40.386 |
| retract | retract | 1.00 / step_budget | (0.499, -0.014, 0.041)→(0.496, -0.014, 0.185) | (0.506, 0.095, 0.033)→(0.505, 0.095, 0.034) | 0.176→0.175 | 1.00 / 1.000 | 0.570 | 44.333 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.420
- phase_breakdown.grasp_peg_score: 0.820
- phase_breakdown.push_through_channel_score: 0.020
- phase_breakdown.approach_channel_entry_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.252
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.006
- **Median Q (composite search score)**: -0.231
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.266


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86667,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel.approach_speed":0.08281,"approach_peg.approach_speed":0.09324,"lift_peg.lift_height":0.15763,"push_through.push_distance":0.16016,"push_through.push_force_limit":30.80363,"retract.retraction_height":0.15237},"optimized_scores":{"best_composite_score":-0.22772,"best_fitness_score":0.25228,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.5058,0.08764,0.05678],"force_p95":140.38238,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.77544,"mean_force":87.36045,"phase_index":5.0,"phase_name":"descend_into_channel","phase_type":"descend","tcp_position_centroid":[0.49715,0.08053,0.0568]},{"body_a":"peg","body_b":"channel_base_body","contact_count":182.0,"contact_point_centroid":[0.50717,0.10317,0.00922],"force_p95":115.66775,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.46556,"mean_force":20.59286,"phase_index":5.0,"phase_name":"descend_into_channel","phase_type":"descend","tcp_position_centroid":[0.49609,0.08143,0.07296]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":29.0,"contact_point_centroid":[0.52515,0.10676,0.04203],"force_p95":24.97152,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.30797,"mean_force":7.81023,"phase_index":5.0,"phase_name":"descend_into_channel","phase_type":"descend","tcp_position_centroid":[0.49839,0.08035,0.05361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":556.0,"contact_point_centroid":[0.50559,0.10469,0.00937],"force_p95":0.57689,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5667,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50932,0.15363,0.21879]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49991,0.19811,0.29671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50653,0.10817,0.00945],"force_p95":0.65448,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24546,"mean_force":0.53429,"phase_index":6.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49589,0.00994,0.04131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.50687,0.10686,0.00939],"force_p95":0.58302,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60004,"mean_force":0.54599,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4933,-0.06083,0.10171]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50594,0.1045,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57624,"mean_force":0.54631,"phase_index":1.0,"phase_name":"grasp_peg_action","phase_type":"grasp","tcp_position_centroid":[0.51497,0.10954,0.13872]},{"body_a":"peg","body_b":"channel_base_body","contact_count":903.0,"contact_point_centroid":[0.50589,0.10471,0.00939],"force_p95":0.57567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57574,"mean_force":0.54633,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.51164,0.10883,0.20933]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.50582,0.1046,0.00939],"force_p95":0.57563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57565,"mean_force":0.54635,"phase_index":3.0,"phase_name":"align_peg","phase_type":"rotate","tcp_position_centroid":[0.50764,0.12048,0.279]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.50584,0.10458,0.00939],"force_p95":0.57559,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57562,"mean_force":0.54628,"phase_index":4.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.50016,0.10731,0.18822]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52502,0.10958,0.05926],"force_p95":0.31837,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39186,"mean_force":0.09334,"phase_index":6.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49611,0.04364,0.04411]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":46.0,"contact_point_centroid":[0.52501,0.1069,0.05877],"force_p95":0.03153,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.03405,"mean_force":0.00398,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49309,-0.06072,0.10018]}],"total_contact_groups":13},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50684,0.10689,0.0338],"final_tcp_position":[0.49349,-0.06069,0.16913],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":153.77544,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55068,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":588.0,"raw_peak_contact_force":3.33087,"subtask_id":"grasp_peg","tcp_end":[0.51959,0.11072,0.14614],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50583,0.10466,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":0.54307,"phase_name":"grasp_peg_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":0.57624,"tcp_end":[0.51416,0.10938,0.13743],"tcp_start":[0.51959,0.11072,0.14614],"tcp_to_object_dist_end":0.10404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.50598,0.10463,0.03384],"object_pos_start":[0.50583,0.10466,0.03384],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18486,"object_z_max":0.03384,"peak_contact_force":0.54104,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":903.0,"raw_peak_contact_force":0.57574,"tcp_end":[0.51211,0.10892,0.28322],"tcp_start":[0.51416,0.10938,0.13743],"tcp_to_object_dist_end":0.24949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":272.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.10466,0.03384],"object_pos_start":[0.50598,0.10463,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18483,"object_z_max":0.03384,"peak_contact_force":0.54954,"phase_name":"align_peg","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":272.0,"raw_peak_contact_force":0.57565,"tcp_end":[0.50466,0.13086,0.27799],"tcp_start":[0.51211,0.10892,0.28322],"tcp_to_object_dist_end":0.24556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.1047,0.03383],"object_pos_start":[0.50598,0.10466,0.03384],"object_to_goal_dist_end":0.1849,"object_to_goal_dist_start":0.18486,"object_z_max":0.03384,"peak_contact_force":0.52979,"phase_name":"approach_channel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":583.0,"raw_peak_contact_force":0.57562,"subtask_id":"approach_channel_entry","tcp_end":[0.49696,0.0831,0.09881],"tcp_start":[0.50466,0.13086,0.27799],"tcp_to_object_dist_end":0.06906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":182.0,"n_steps_budget":600.0,"object_pos_end":[0.50706,0.1107,0.03465],"object_pos_start":[0.50591,0.1047,0.03383],"object_to_goal_dist_end":0.19091,"object_to_goal_dist_start":0.1849,"object_z_max":0.03448,"peak_contact_force":0.37061,"phase_name":"descend_into_channel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":254.0,"raw_peak_contact_force":153.77544,"tcp_end":[0.49822,0.07997,0.04959],"tcp_start":[0.49696,0.0831,0.09881],"tcp_to_object_dist_end":0.03529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.50686,0.1069,0.03384],"object_pos_start":[0.50706,0.1107,0.03465],"object_to_goal_dist_end":0.18713,"object_to_goal_dist_start":0.19091,"object_z_max":0.0366,"peak_contact_force":0.54204,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":359.0,"raw_peak_contact_force":1.24546,"subtask_id":"push_through_channel","tcp_end":[0.49622,-0.06094,0.03643],"tcp_start":[0.49822,0.07997,0.04959],"tcp_to_object_dist_end":0.1682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":402.0,"n_steps_budget":960.0,"object_pos_end":[0.50684,0.10689,0.0338],"object_pos_start":[0.50686,0.1069,0.03384],"object_to_goal_dist_end":0.18712,"object_to_goal_dist_start":0.18713,"object_z_max":0.03384,"peak_contact_force":0.55613,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":448.0,"raw_peak_contact_force":0.60004,"tcp_end":[0.49349,-0.06069,0.16913],"tcp_start":[0.49622,-0.06094,0.03643],"tcp_to_object_dist_end":0.21581,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81633,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel.approach_speed":0.07568,"approach_peg.approach_speed":0.07097,"lift_peg.lift_height":0.1626,"push_through.push_distance":0.152,"push_through.push_force_limit":30.15799,"retract.retraction_height":0.12468},"optimized_scores":{"best_composite_score":-0.23115,"best_fitness_score":0.24885,"best_task_score":0.00599},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.50776,0.07246,0.00897],"force_p95":172.13285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.84459,"mean_force":53.74161,"phase_index":5.0,"phase_name":"descend_into_channel","phase_type":"descend","tcp_position_centroid":[0.49642,0.08003,0.07003]},{"body_a":"attachment","body_b":"peg","contact_count":86.0,"contact_point_centroid":[0.51092,0.08015,0.05466],"force_p95":175.18163,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.35863,"mean_force":133.10592,"phase_index":5.0,"phase_name":"descend_into_channel","phase_type":"descend","tcp_position_centroid":[0.49913,0.08011,0.05484]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.50589,0.06811,0.00926],"force_p95":14.16484,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":131.77306,"mean_force":2.42757,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50115,0.08018,0.10285]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.51455,0.07796,0.05481],"force_p95":76.05087,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.31495,"mean_force":17.75724,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50301,0.08044,0.05526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50341,0.07185,0.00754],"force_p95":116.53662,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.29151,"mean_force":91.00735,"phase_index":6.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50373,0.08064,0.05078]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51554,0.08045,0.0519],"force_p95":111.52925,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.78518,"mean_force":88.96932,"phase_index":6.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50373,0.08064,0.05078]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52529,0.06891,0.05468],"force_p95":13.95359,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.13965,"mean_force":3.9513,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50371,0.08064,0.0511]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52513,0.06803,0.02499],"force_p95":9.10278,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.09059,"mean_force":3.43437,"phase_index":6.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50373,0.08064,0.05078]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52505,0.06797,0.05524],"force_p95":8.05208,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.30939,"mean_force":4.76243,"phase_index":5.0,"phase_name":"descend_into_channel","phase_type":"descend","tcp_position_centroid":[0.50332,0.0806,0.05098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":658.0,"contact_point_centroid":[0.50303,0.06748,0.00935],"force_p95":0.55495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55972,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49903,0.13638,0.21951]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50306,0.06746,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55083,"mean_force":0.54665,"phase_index":1.0,"phase_name":"grasp_peg_action","phase_type":"grasp","tcp_position_centroid":[0.49528,0.07437,0.13849]},{"body_a":"peg","body_b":"channel_base_body","contact_count":933.0,"contact_point_centroid":[0.50307,0.06741,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55068,"mean_force":0.54664,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.492,0.07389,0.21213]},{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.50299,0.06749,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55057,"mean_force":0.54664,"phase_index":3.0,"phase_name":"align_peg","phase_type":"rotate","tcp_position_centroid":[0.48892,0.08491,0.28472]},{"body_a":"peg","body_b":"channel_base_body","contact_count":608.0,"contact_point_centroid":[0.50312,0.0675,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55056,"mean_force":0.54665,"phase_index":4.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49033,0.08771,0.1912]}],"total_contact_groups":14},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50572,0.0665,0.0339],"final_tcp_position":[0.50098,0.08017,0.15583],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":177.84459,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":674.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54749,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":658.0,"raw_peak_contact_force":2.06903,"subtask_id":"grasp_peg","tcp_end":[0.49982,0.07525,0.14521],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50308,0.06748,0.0338],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54361,"phase_name":"grasp_peg_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":0.55083,"tcp_end":[0.49448,0.07427,0.13733],"tcp_start":[0.49982,0.07525,0.14521],"tcp_to_object_dist_end":0.10411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50308,0.06748,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54518,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":933.0,"raw_peak_contact_force":0.55068,"tcp_end":[0.49246,0.07396,0.28849],"tcp_start":[0.49448,0.07427,0.13733],"tcp_to_object_dist_end":0.25499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":600.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54564,"phase_name":"align_peg","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":244.0,"raw_peak_contact_force":0.55057,"tcp_end":[0.48665,0.09491,0.28369],"tcp_start":[0.49246,0.07396,0.28849],"tcp_to_object_dist_end":0.25193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.06742,0.0338],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54779,"phase_name":"approach_channel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":608.0,"raw_peak_contact_force":0.55056,"subtask_id":"approach_channel_entry","tcp_end":[0.4957,0.08048,0.09877],"tcp_start":[0.48665,0.09491,0.28369],"tcp_to_object_dist_end":0.06667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":215.0,"n_steps_budget":600.0,"object_pos_end":[0.50717,0.06792,0.03021],"object_pos_start":[0.50304,0.06742,0.0338],"object_to_goal_dist_end":0.14841,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":177.84459,"phase_name":"descend_into_channel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":308.0,"raw_peak_contact_force":177.84459,"tcp_end":[0.50367,0.08063,0.05079],"tcp_start":[0.4957,0.08048,0.09877],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":960.0,"object_pos_end":[0.50716,0.06792,0.03021],"object_pos_start":[0.50717,0.06792,0.03021],"object_to_goal_dist_end":0.14841,"object_to_goal_dist_start":0.14841,"object_z_max":0.03021,"peak_contact_force":119.29151,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":119.29151,"subtask_id":"push_through_channel","tcp_end":[0.5038,0.08066,0.0508],"tcp_start":[0.50377,0.08065,0.05078],"tcp_to_object_dist_end":0.02445,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":318.0,"n_steps_budget":780.0,"object_pos_end":[0.50572,0.0665,0.0339],"object_pos_start":[0.50712,0.06795,0.03018],"object_to_goal_dist_end":0.14674,"object_to_goal_dist_start":0.14845,"object_z_max":0.03403,"peak_contact_force":0.54811,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":358.0,"raw_peak_contact_force":131.77306,"tcp_end":[0.50098,0.08017,0.15583],"tcp_start":[0.5038,0.08066,0.0508],"tcp_to_object_dist_end":0.12279,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56855,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel.approach_speed":0.09805,"approach_peg.approach_speed":0.0484,"lift_peg.lift_height":0.15196,"push_through.push_distance":0.16077,"push_through.push_force_limit":29.58116,"retract.retraction_height":0.21326},"optimized_scores":{"best_composite_score":-0.23276,"best_fitness_score":0.24724,"best_task_score":0.00093},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":577.0,"contact_point_centroid":[0.50356,0.11156,0.00939],"force_p95":0.6126,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55627,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50233,0.15765,0.22005]},{"body_a":"peg","body_b":"channel_base_body","contact_count":873.0,"contact_point_centroid":[0.50367,0.11165,0.00941],"force_p95":0.59907,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64581,"mean_force":0.54405,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.49842,0.11567,0.20784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50375,0.11166,0.00942],"force_p95":0.59187,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63673,"mean_force":0.543,"phase_index":1.0,"phase_name":"grasp_peg_action","phase_type":"grasp","tcp_position_centroid":[0.50172,0.11642,0.13979]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.50362,0.11156,0.00942],"force_p95":0.59359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63611,"mean_force":0.54309,"phase_index":4.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49275,0.11052,0.18579]},{"body_a":"peg","body_b":"channel_base_body","contact_count":586.0,"contact_point_centroid":[0.50367,0.11155,0.0094],"force_p95":0.59999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62546,"mean_force":0.54452,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4931,-0.06168,0.13235]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.50341,0.11162,0.00941],"force_p95":0.59686,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62341,"mean_force":0.54453,"phase_index":5.0,"phase_name":"descend_into_channel","phase_type":"descend","tcp_position_centroid":[0.49499,0.08171,0.07366]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.50372,0.11136,0.00944],"force_p95":0.58846,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62239,"mean_force":0.54112,"phase_index":6.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49439,0.00945,0.04084]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50373,0.11157,0.00939],"force_p95":0.59284,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60989,"mean_force":0.54536,"phase_index":3.0,"phase_name":"align_peg","phase_type":"rotate","tcp_position_centroid":[0.49426,0.12685,0.27495]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49973,0.19925,0.29915]}],"total_contact_groups":9},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50372,0.11162,0.03381],"final_tcp_position":[0.49362,-0.06163,0.23],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":2.06328,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11177,0.03389],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54409,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":593.0,"raw_peak_contact_force":2.06328,"subtask_id":"grasp_peg","tcp_end":[0.50626,0.11762,0.1469],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,0.11172,0.03382],"object_pos_start":[0.50373,0.11177,0.03389],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.1919,"object_z_max":0.03404,"peak_contact_force":0.57014,"phase_name":"grasp_peg_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":0.63673,"tcp_end":[0.50091,0.11625,0.13856],"tcp_start":[0.50626,0.11762,0.1469],"tcp_to_object_dist_end":0.10488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.50366,0.11171,0.03385],"object_pos_start":[0.5037,0.11172,0.03382],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19185,"object_z_max":0.03393,"peak_contact_force":0.57518,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":873.0,"raw_peak_contact_force":0.64581,"tcp_end":[0.49885,0.11576,0.27892],"tcp_start":[0.50091,0.11625,0.13856],"tcp_to_object_dist_end":0.24514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.11175,0.03385],"object_pos_start":[0.50366,0.11171,0.03385],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19184,"object_z_max":0.03385,"peak_contact_force":0.5406,"phase_name":"align_peg","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":252.0,"raw_peak_contact_force":0.60989,"tcp_end":[0.49112,0.13693,0.27391],"tcp_start":[0.49885,0.11576,0.27892],"tcp_to_object_dist_end":0.24171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11168,0.03391],"object_pos_start":[0.50371,0.11175,0.03385],"object_to_goal_dist_end":0.19181,"object_to_goal_dist_start":0.19189,"object_z_max":0.03394,"peak_contact_force":0.55264,"phase_name":"approach_channel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":583.0,"raw_peak_contact_force":0.63611,"subtask_id":"approach_channel_entry","tcp_end":[0.49609,0.08345,0.09826],"tcp_start":[0.49112,0.13693,0.27391],"tcp_to_object_dist_end":0.07068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":171.0,"n_steps_budget":600.0,"object_pos_end":[0.50375,0.11171,0.03381],"object_pos_start":[0.50371,0.11168,0.03391],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19181,"object_z_max":0.03391,"peak_contact_force":0.60874,"phase_name":"descend_into_channel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":171.0,"raw_peak_contact_force":0.62341,"tcp_end":[0.49552,0.08018,0.04874],"tcp_start":[0.49609,0.08345,0.09826],"tcp_to_object_dist_end":0.03584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11162,0.03397],"object_pos_start":[0.50375,0.11171,0.03381],"object_to_goal_dist_end":0.19175,"object_to_goal_dist_start":0.19185,"object_z_max":0.03403,"peak_contact_force":0.51081,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":343.0,"raw_peak_contact_force":0.62239,"subtask_id":"push_through_channel","tcp_end":[0.49591,-0.06184,0.03632],"tcp_start":[0.49552,0.08018,0.04874],"tcp_to_object_dist_end":0.17365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11162,0.03381],"object_pos_start":[0.50368,0.11162,0.03397],"object_to_goal_dist_end":0.19175,"object_to_goal_dist_start":0.19175,"object_z_max":0.03397,"peak_contact_force":0.6049,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":586.0,"raw_peak_contact_force":0.62546,"tcp_end":[0.49362,-0.06163,0.23],"tcp_start":[0.49591,-0.06184,0.03632],"tcp_to_object_dist_end":0.26193,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```