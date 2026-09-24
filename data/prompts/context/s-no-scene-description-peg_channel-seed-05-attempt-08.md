## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | grasp → approach → descend → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0869 | 0.14 | ✅ accepted |
| 7 | grasp → approach → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0715 | 0.12 | ✅ accepted |
| 6 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → insert → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.5799 | 0.00 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2994 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.087) — your mutation base

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

- **Composite score**: -0.087
- **task_score** (E): 0.137
- **fitness_score**: 0.203  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| grasp_0 | 1.00 | 1.00 | 0.0095 |
| approach_1 | 1.00 | 1.00 | 0.2244 |
| descend_1 | 1.00 | 1.00 | 0.0365 |
| push_1 | 0.00 | 1.00 | 0.0000 |
| retract_1 | 1.00 | 1.00 | 0.1429 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| grasp_0 | grasp | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.198, 0.291) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.534 | 2.488 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.198, 0.291)→(0.497, 0.086, 0.097) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.541 | 0.588 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.086, 0.097)→(0.499, 0.082, 0.061) | (0.504, 0.095, 0.034)→(0.507, 0.074, 0.028) | 0.175→0.155 | 1.00 / 3.333 | 184.868 | 232.859 |
| push_1 | push | 0.00 / guard_failure | (0.499, 0.082, 0.061)→(0.499, 0.082, 0.061) | (0.507, 0.074, 0.028)→(0.507, 0.074, 0.028) | 0.155→0.154 | 1.00 / 2.667 | 95.258 | 111.859 |
| retract_1 | retract | 1.00 / step_budget | (0.499, 0.082, 0.061)→(0.498, 0.081, 0.204) | (0.507, 0.074, 0.028)→(0.506, 0.072, 0.031) | 0.154→0.152 | 1.00 / 1.000 | 0.554 | 109.902 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.309
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.309
- phase_score: 0.247
- phase_breakdown.approach_channel_entry_score: 0.823
- phase_breakdown.push_through_channel_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.272
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.309
- **Median Q (composite search score)**: -0.109
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.418


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81452,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07997,"push_1.push_distance":0.11532,"push_1.push_force_limit":25.07724,"retract_1.retraction_height":0.19663},"optimized_scores":{"best_composite_score":-0.13413,"best_fitness_score":0.15587,"best_task_score":0.01934},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":185.0,"contact_point_centroid":[0.49949,0.11698,0.05342],"force_p95":165.4378,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.65931,"mean_force":139.81108,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49907,0.08127,0.06407]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.50336,0.11191,0.00845],"force_p95":164.56701,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":185.30549,"mean_force":94.60676,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49811,0.0821,0.07076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50142,0.11567,0.00753],"force_p95":115.92428,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.35748,"mean_force":101.65337,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49992,0.08181,0.06339]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50083,0.11653,0.05186],"force_p95":114.89962,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.28833,"mean_force":98.91967,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49992,0.08181,0.06339]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.50041,0.1161,0.05527],"force_p95":76.96586,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.89226,"mean_force":18.20849,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49944,0.08181,0.06811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":529.0,"contact_point_centroid":[0.50554,0.09901,0.00934],"force_p95":0.58028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.50972,"mean_force":1.80993,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49807,0.08105,0.15122]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":107.0,"contact_point_centroid":[0.525,0.11995,0.04291],"force_p95":96.02181,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":104.65575,"mean_force":60.65494,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49992,0.08102,0.0631]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.525,0.11998,0.04204],"force_p95":70.41817,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.41817,"mean_force":70.41817,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49991,0.08176,0.06341]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.525,0.12,0.05263],"force_p95":53.08348,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.45332,"mean_force":44.10618,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49894,0.08171,0.0727]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":151.0,"contact_point_centroid":[0.52525,0.10106,0.01303],"force_p95":17.60019,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.97567,"mean_force":8.01708,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49964,0.08109,0.0632]},{"body_a":"peg","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.50701,0.12054,0.0423],"force_p95":13.32211,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.52136,"mean_force":5.83135,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49901,0.08076,0.06434]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52509,0.09962,0.01],"force_p95":13.56387,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.58792,"mean_force":10.10376,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49997,0.08189,0.06364]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52513,0.09983,0.02505],"force_p95":7.02646,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.74867,"mean_force":2.8291,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49992,0.08181,0.06339]},{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.50547,0.1046,0.00937],"force_p95":0.57957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57306,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.497,0.19847,0.29242]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49937,0.19945,0.29908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":774.0,"contact_point_centroid":[0.50599,0.10468,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57724,"mean_force":0.54632,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49347,0.1506,0.19455]}],"total_contact_groups":16},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50629,0.09868,0.03389],"final_tcp_position":[0.49849,0.08116,0.24033],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":188.65931,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53144,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":455.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":774.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.54419,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":774.0,"raw_peak_contact_force":0.57724,"subtask_id":"approach_channel_entry","tcp_end":[0.49707,0.08574,0.09731],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.06679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":600.0,"object_pos_end":[0.50723,0.09989,0.03016],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.1803,"object_to_goal_dist_start":0.18475,"object_z_max":0.03421,"peak_contact_force":144.18034,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":730.0,"raw_peak_contact_force":188.65931,"tcp_end":[0.49991,0.08176,0.06341],"tcp_start":[0.49707,0.08574,0.09731],"tcp_to_object_dist_end":0.03858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":750.0,"object_pos_end":[0.50722,0.09988,0.03016],"object_pos_start":[0.50723,0.09989,0.03016],"object_to_goal_dist_end":0.18029,"object_to_goal_dist_start":0.1803,"object_z_max":0.03017,"peak_contact_force":103.02547,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":117.35748,"subtask_id":"push_through_channel","tcp_end":[0.49995,0.08188,0.0634],"tcp_start":[0.49994,0.08186,0.06338],"tcp_to_object_dist_end":0.03849,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50629,0.09868,0.03389],"object_pos_start":[0.50717,0.09981,0.03019],"object_to_goal_dist_end":0.17889,"object_to_goal_dist_start":0.18022,"object_z_max":0.03396,"peak_contact_force":0.54358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":576.0,"raw_peak_contact_force":109.89226,"tcp_end":[0.49849,0.08116,0.24033],"tcp_start":[0.49995,0.08188,0.0634],"tcp_to_object_dist_end":0.20733,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81301,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07401,"push_1.push_distance":0.14624,"push_1.push_force_limit":25.37329,"retract_1.retraction_height":0.1691},"optimized_scores":{"best_composite_score":-0.01786,"best_fitness_score":0.27214,"best_task_score":0.30946},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.49846,0.14184,-0.00032],"force_p95":264.84439,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.43459,"mean_force":227.72473,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49763,0.08141,0.05544]},{"body_a":"peg","body_b":"channel_base_body","contact_count":220.0,"contact_point_centroid":[0.50278,0.0609,0.00888],"force_p95":115.47321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.69366,"mean_force":28.88964,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49693,0.0823,0.07104]},{"body_a":"attachment","body_b":"peg","contact_count":68.0,"contact_point_centroid":[0.49786,0.08337,0.05523],"force_p95":117.39778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.16663,"mean_force":91.64607,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49729,0.08112,0.06571]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.52501,0.11989,0.04827],"force_p95":84.30185,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.96925,"mean_force":47.17471,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49817,0.08015,0.06383]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.4988,0.14191,-7e-05],"force_p95":81.51669,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.37542,"mean_force":68.08511,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49747,0.0826,0.05713]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49873,0.14189,-0.0001],"force_p95":77.28435,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.32234,"mean_force":67.98735,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4974,0.08258,0.05704]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.475,0.11995,0.04396],"force_p95":36.8177,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.90491,"mean_force":7.1616,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49817,0.0801,0.06386]},{"body_a":"peg","body_b":"channel_base_body","contact_count":446.0,"contact_point_centroid":[0.50608,0.02014,0.00811],"force_p95":0.82399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.28946,"mean_force":0.91873,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49547,0.08163,0.13107]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.525,-0.00493,0.0246],"force_p95":8.48091,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81261,"mean_force":4.0721,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49513,0.08149,0.11729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.50304,0.06752,0.00933],"force_p95":0.56983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56647,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49705,0.1985,0.29258]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5067,-0.00378,0.00757],"force_p95":0.90153,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91379,"mean_force":0.7976,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4974,0.08258,0.05704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":784.0,"contact_point_centroid":[0.50308,0.06745,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54664,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4935,0.15087,0.19516]}],"total_contact_groups":12},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5054,0.01795,0.02416],"final_tcp_position":[0.49573,0.08176,0.20643],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":320.43459,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54626,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":434.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54569,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":784.0,"raw_peak_contact_force":0.55115,"subtask_id":"approach_channel_entry","tcp_end":[0.49707,0.08574,0.09731],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.06637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.50589,0.02104,0.02343],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.10256,"object_to_goal_dist_start":0.14759,"object_z_max":0.04103,"peak_contact_force":230.00561,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":371.0,"raw_peak_contact_force":320.43459,"tcp_end":[0.49737,0.08255,0.05705],"tcp_start":[0.49707,0.08574,0.09731],"tcp_to_object_dist_end":0.07061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":930.0,"object_pos_end":[0.50589,0.02098,0.02343],"object_pos_start":[0.50589,0.02104,0.02343],"object_to_goal_dist_end":0.1025,"object_to_goal_dist_start":0.10256,"object_z_max":0.02344,"peak_contact_force":49.69724,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":77.32234,"subtask_id":"push_through_channel","tcp_end":[0.49745,0.08261,0.05707],"tcp_start":[0.49744,0.0826,0.05703],"tcp_to_object_dist_end":0.07072,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.5054,0.01795,0.02416],"object_pos_start":[0.50589,0.02097,0.02346],"object_to_goal_dist_end":0.09937,"object_to_goal_dist_start":0.10248,"object_z_max":0.02489,"peak_contact_force":0.5798,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":488.0,"raw_peak_contact_force":83.37542,"tcp_end":[0.49573,0.08176,0.20643],"tcp_start":[0.49745,0.08261,0.05707],"tcp_to_object_dist_end":0.19336,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78704,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08059,"push_1.push_distance":0.12622,"push_1.push_force_limit":25.12752,"retract_1.retraction_height":0.1221},"optimized_scores":{"best_composite_score":-0.10869,"best_fitness_score":0.18131,"best_task_score":0.08308},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":279.0,"contact_point_centroid":[0.50244,0.10962,0.00826],"force_p95":180.53093,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.48303,"mean_force":101.95262,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49842,0.08256,0.07094]},{"body_a":"attachment","body_b":"peg","contact_count":193.0,"contact_point_centroid":[0.49966,0.11877,0.05345],"force_p95":174.82393,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.59429,"mean_force":138.00099,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49929,0.0816,0.06416]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":94.0,"contact_point_centroid":[0.525,0.11996,0.04208],"force_p95":70.94482,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.07465,"mean_force":55.7971,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50035,0.08102,0.06265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50368,0.11619,0.00747],"force_p95":140.1133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.89794,"mean_force":135.28904,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50052,0.08171,0.06276]},{"body_a":"peg","body_b":"channel_base_body","contact_count":308.0,"contact_point_centroid":[0.50562,0.10029,0.0093],"force_p95":20.28752,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.43747,"mean_force":3.29102,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49856,0.081,0.11323]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.50097,0.1178,0.05509],"force_p95":74.91888,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.95,"mean_force":20.05053,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49998,0.08172,0.06781]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50131,0.11862,0.05144],"force_p95":128.09416,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.1813,"mean_force":126.7021,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50052,0.08171,0.06276]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.525,0.12,0.05079],"force_p95":108.39986,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.5465,"mean_force":63.23294,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49958,0.08164,0.07156]},{"body_a":"peg","body_b":"link7","contact_count":146.0,"contact_point_centroid":[0.50543,0.12262,0.03998],"force_p95":45.68678,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.11748,"mean_force":14.28941,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4985,0.08239,0.07045]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.525,0.11999,0.04103],"force_p95":64.66182,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.66182,"mean_force":64.66182,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5005,0.08168,0.06275]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":100.0,"contact_point_centroid":[0.52516,0.10098,0.01227],"force_p95":13.7472,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.19361,"mean_force":5.86194,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50034,0.08104,0.06266]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":60.0,"contact_point_centroid":[0.52506,0.09856,0.04909],"force_p95":18.01862,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.85251,"mean_force":2.50668,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49887,0.08117,0.10445]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52534,0.09895,0.01001],"force_p95":16.03414,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.5139,"mean_force":12.87691,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50052,0.08171,0.06276]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.50352,0.11166,0.00936],"force_p95":0.61517,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56336,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49702,0.19848,0.29249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":772.0,"contact_point_centroid":[0.50368,0.11171,0.00941],"force_p95":0.60011,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63444,"mean_force":0.54416,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49346,0.15053,0.19441]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49961,0.19955,0.29976]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50682,0.09848,0.03387],"final_tcp_position":[0.49852,0.08079,0.16508],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":189.48303,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,0.11179,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5238,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":444.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11172,0.03381],"object_pos_start":[0.5037,0.11179,0.0338],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19192,"object_z_max":0.034,"peak_contact_force":0.53312,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":772.0,"raw_peak_contact_force":0.63444,"subtask_id":"approach_channel_entry","tcp_end":[0.49707,0.08575,0.09733],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.06895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":600.0,"object_pos_end":[0.5074,0.10032,0.03104],"object_pos_start":[0.5037,0.11172,0.03381],"object_to_goal_dist_end":0.18069,"object_to_goal_dist_start":0.19186,"object_z_max":0.03555,"peak_contact_force":180.41802,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":812.0,"raw_peak_contact_force":189.48303,"tcp_end":[0.5005,0.08168,0.06275],"tcp_start":[0.49707,0.08575,0.09733],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":810.0,"object_pos_end":[0.50737,0.10031,0.03107],"object_pos_start":[0.5074,0.10032,0.03104],"object_to_goal_dist_end":0.18068,"object_to_goal_dist_start":0.18069,"object_z_max":0.03111,"peak_contact_force":133.05157,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":140.89794,"subtask_id":"push_through_channel","tcp_end":[0.50056,0.08177,0.06282],"tcp_start":[0.50054,0.08175,0.06278],"tcp_to_object_dist_end":0.03739,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":308.0,"n_steps_budget":780.0,"object_pos_end":[0.50682,0.09848,0.03387],"object_pos_start":[0.50731,0.10026,0.03115],"object_to_goal_dist_end":0.17872,"object_to_goal_dist_start":0.18062,"object_z_max":0.03444,"peak_contact_force":0.54004,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":413.0,"raw_peak_contact_force":136.43747,"tcp_end":[0.49852,0.08079,0.16508],"tcp_start":[0.50056,0.08177,0.06282],"tcp_to_object_dist_end":0.13266,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```