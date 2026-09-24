## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1109 | 0.54 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6757 | 0.65 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6280 | 0.69 | ✅ accepted |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

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
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=0.111) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.06
  weight: 0.3
- id: insertion_goal
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.025
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_1
  type: push
  generator: impedance_motion
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
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insertion_goal
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.111
- **task_score** (E): 0.540
- **fitness_score**: 0.301  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1791 |
| descend_1 | 1.00 | 1.00 | 0.0817 |
| contact_1 | 1.00 | 1.00 | 0.0192 |
| push_1 | 0.00 | 1.00 | 0.0025 |
| retract_1 | 1.00 | 1.00 | 0.0885 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.126, 0.140) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.545 | 2.179 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.126, 0.140)→(0.496, 0.121, 0.059) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.544 | 0.579 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.121, 0.059)→(0.494, 0.109, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.035) | 0.161→0.160 | 1.00 / 2.000 | 4.973 | 4.568 |
| push_1 | push | 0.00 / guard_failure | (0.500, 0.104, 0.041)→(0.501, 0.102, 0.040) | (0.500, 0.080, 0.035)→(0.502, 0.077, 0.037) | 0.160→0.157 | 1.00 / 1.333 | 8.675 | 118.013 |
| retract_1 | retract | 1.00 / step_budget | (0.501, 0.102, 0.040)→(0.498, 0.102, 0.129) | (0.504, 0.074, 0.038)→(0.500, -0.023, 0.024) | 0.154→0.060 | 1.00 / 1.000 | 0.549 | 11.900 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.631
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.631
- phase_score: 0.149
- phase_breakdown.insertion_goal_score: 0.017
- phase_breakdown.pre_contact_score: 0.455

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.342
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.631
- **Median Q (composite search score)**: 0.126
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.326


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90099,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08261,"contact_1.contact_force":3.04431,"descend_1.descend_height":0.01204,"push_1.insertion_depth":0.17554,"push_1.push_force_limit":41.34659,"push_1.push_speed":0.03023},"optimized_scores":{"best_composite_score":0.12625,"best_fitness_score":0.31625,"best_task_score":0.59082},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50713,0.04398,0.00952],"force_p95":87.37629,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.66347,"mean_force":26.63497,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49935,0.08977,0.04135]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.5031,0.07641,0.04487],"force_p95":89.65479,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.13636,"mean_force":38.02366,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50122,0.08794,0.04048]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52526,0.08147,0.05996],"force_p95":18.05636,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":20.1119,"mean_force":5.98922,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50944,0.07982,0.03499]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52504,0.05737,0.01331],"force_p95":11.19582,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.19582,"mean_force":11.19582,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50359,0.08564,0.03939]},{"body_a":"peg","body_b":"channel_base_body","contact_count":530.0,"contact_point_centroid":[0.4993,-0.03726,0.00825],"force_p95":0.92487,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.92923,"mean_force":0.6341,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50197,0.08309,0.08255]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47493,-0.01763,0.02441],"force_p95":5.03973,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.68421,"mean_force":1.20276,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50174,0.08329,0.07255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":129.0,"contact_point_centroid":[0.50383,0.06035,0.00938],"force_p95":0.55028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.11822,"mean_force":0.60756,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4988,0.09611,0.04737]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.5021,0.07931,0.0589],"force_p95":3.51878,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.58549,"mean_force":1.7089,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49834,0.09129,0.04232]},{"body_a":"peg","body_b":"channel_base_body","contact_count":591.0,"contact_point_centroid":[0.5036,0.06159,0.00935],"force_p95":0.58272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56019,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50284,0.15226,0.21079]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52646,0.02484,0.03406],"force_p95":1.67311,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.08466,"mean_force":0.85538,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50596,0.08045,0.03456]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49978,0.19893,0.29844]},{"body_a":"peg","body_b":"channel_base_body","contact_count":235.0,"contact_point_centroid":[0.50382,0.06164,0.00938],"force_p95":0.55133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55426,"mean_force":0.54671,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50324,0.10457,0.09257]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5071,0.07118,0.039],"force_p95":0.33001,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36667,"mean_force":0.12222,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50667,0.08269,0.03799]}],"total_contact_groups":13},"final_pose_error":0.01198,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50411,-0.0421,0.02413],"final_tcp_position":[0.5021,0.08341,0.12713],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":101.66347,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.0616,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.55392,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":610.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.50714,0.10752,0.12959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":235.0,"n_steps_budget":600.0,"object_pos_end":[0.50377,0.06157,0.03378],"object_pos_start":[0.50377,0.0616,0.03378],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14179,"object_z_max":0.03378,"peak_contact_force":0.54532,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":235.0,"raw_peak_contact_force":0.55426,"subtask_id":"pre_contact","tcp_end":[0.5008,0.10188,0.05515],"tcp_start":[0.50714,0.10752,0.12959],"tcp_to_object_dist_end":0.04572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":129.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.06125,0.03417],"object_pos_start":[0.50377,0.06157,0.03378],"object_to_goal_dist_end":0.14142,"object_to_goal_dist_start":0.14176,"object_z_max":0.03412,"peak_contact_force":3.62761,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":134.0,"raw_peak_contact_force":4.11822,"tcp_end":[0.49834,0.09082,0.04189],"tcp_start":[0.5008,0.10188,0.05515],"tcp_to_object_dist_end":0.03104,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.5051,0.05853,0.03665],"object_pos_start":[0.50376,0.06125,0.03417],"object_to_goal_dist_end":0.13867,"object_to_goal_dist_start":0.14142,"object_z_max":0.03753,"peak_contact_force":16.26467,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":101.66347,"subtask_id":"insertion_goal","tcp_end":[0.50532,0.08399,0.03866],"tcp_start":[0.50359,0.08564,0.03939],"tcp_to_object_dist_end":0.02553,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50411,-0.0421,0.02413],"object_pos_start":[0.50688,0.05538,0.03811],"object_to_goal_dist_end":0.0413,"object_to_goal_dist_start":0.13557,"object_z_max":0.04069,"peak_contact_force":0.53262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":579.0,"raw_peak_contact_force":20.1119,"tcp_end":[0.5021,0.08341,0.12713],"tcp_start":[0.50532,0.08399,0.03866],"tcp_to_object_dist_end":0.16237,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07325,"contact_1.contact_force":3.46468,"descend_1.descend_height":0.01785,"push_1.insertion_depth":0.13788,"push_1.push_force_limit":36.5333,"push_1.push_speed":0.0135},"optimized_scores":{"best_composite_score":0.15155,"best_fitness_score":0.34155,"best_task_score":0.63102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.50532,0.09845,0.00955],"force_p95":181.09399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":192.01532,"mean_force":54.85715,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49713,0.1436,0.04522]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50089,0.13041,0.04763],"force_p95":186.53767,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":191.80749,"mean_force":97.02156,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49936,0.14193,0.04428]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.5015,0.0192,0.00826],"force_p95":0.95765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.4178,"mean_force":0.66732,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50174,0.13704,0.08664]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52665,0.07328,0.02938],"force_p95":6.17807,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.19339,"mean_force":1.19472,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50561,0.13626,0.04384]},{"body_a":"peg","body_b":"channel_base_body","contact_count":110.0,"contact_point_centroid":[0.50116,0.11521,0.00942],"force_p95":0.61944,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.83606,"mean_force":0.58812,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49521,0.15051,0.05286]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49853,0.13377,0.05894],"force_p95":3.97198,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.3477,"mean_force":1.81874,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49491,0.14561,0.04655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":536.0,"contact_point_centroid":[0.50101,0.11599,0.00935],"force_p95":0.60476,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56055,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49811,0.17861,0.20869]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50723,0.12508,0.04193],"force_p95":1.05853,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.18943,"mean_force":0.41368,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50762,0.13642,0.04116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.50084,0.11628,0.00942],"force_p95":0.60188,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63151,"mean_force":0.54313,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49652,0.15673,0.0917]}],"total_contact_groups":9},"final_pose_error":0.01219,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50137,0.01507,0.02413],"final_tcp_position":[0.50185,0.13714,0.13043],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":192.01532,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11616,0.03392],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19625,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.53339,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49783,0.15839,0.12244],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":198.0,"n_steps_budget":600.0,"object_pos_end":[0.50095,0.11601,0.03393],"object_pos_start":[0.50095,0.11616,0.03392],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19625,"object_z_max":0.03394,"peak_contact_force":0.54449,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":198.0,"raw_peak_contact_force":0.63151,"subtask_id":"pre_contact","tcp_end":[0.49687,0.15554,0.06085],"tcp_start":[0.49783,0.15839,0.12244],"tcp_to_object_dist_end":0.048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":110.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11593,0.03398],"object_pos_start":[0.50095,0.11601,0.03393],"object_to_goal_dist_end":0.19602,"object_to_goal_dist_start":0.1961,"object_z_max":0.03394,"peak_contact_force":4.83606,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":113.0,"raw_peak_contact_force":4.83606,"tcp_end":[0.49491,0.14545,0.04637],"tcp_start":[0.49687,0.15554,0.06085],"tcp_to_object_dist_end":0.03259,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.50237,0.1126,0.03657],"object_pos_start":[0.50096,0.11593,0.03398],"object_to_goal_dist_end":0.19265,"object_to_goal_dist_start":0.19602,"object_z_max":0.03754,"peak_contact_force":5.20557,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":192.01532,"subtask_id":"insertion_goal","tcp_end":[0.50501,0.13804,0.04217],"tcp_start":[0.50274,0.13952,0.04292],"tcp_to_object_dist_end":0.02618,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50137,0.01507,0.02413],"object_pos_start":[0.50481,0.10993,0.03826],"object_to_goal_dist_end":0.0964,"object_to_goal_dist_start":0.19,"object_z_max":0.04342,"peak_contact_force":0.53261,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":572.0,"raw_peak_contact_force":7.4178,"tcp_end":[0.50185,0.13714,0.13043],"tcp_start":[0.50501,0.13804,0.04217],"tcp_to_object_dist_end":0.16187,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90099,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12084,"contact_1.contact_force":5.13874,"descend_1.descend_height":0.01736,"push_1.insertion_depth":0.143,"push_1.push_force_limit":37.51182,"push_1.push_speed":0.03838},"optimized_scores":{"best_composite_score":0.05485,"best_fitness_score":0.24485,"best_task_score":0.39741},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49939,0.04429,0.00991],"force_p95":55.31299,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.36021,"mean_force":22.19844,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48952,0.0898,0.04176]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49396,0.07686,0.04557],"force_p95":54.54744,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.49906,"mean_force":23.86998,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49082,0.0885,0.04109]},{"body_a":"peg","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.49682,-0.03547,0.00834],"force_p95":0.99262,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.17101,"mean_force":0.67177,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49073,0.08451,0.08481]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47498,-0.06401,0.02404],"force_p95":7.80779,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.89354,"mean_force":2.79611,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49058,0.08458,0.0701]},{"body_a":"peg","body_b":"channel_base_body","contact_count":173.0,"contact_point_centroid":[0.49576,0.06003,0.00945],"force_p95":3.61387,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.75074,"mean_force":0.82903,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48848,0.09698,0.04962]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.49221,0.08022,0.05269],"force_p95":4.42154,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.58047,"mean_force":1.86755,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48864,0.09196,0.04374]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.5261,0.02166,0.04312],"force_p95":2.09264,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.75488,"mean_force":0.64222,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49302,0.08268,0.03737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":477.0,"contact_point_centroid":[0.49557,0.06384,0.00937],"force_p95":0.59636,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56336,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48881,0.15379,0.22979]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49924,0.19815,0.29726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":361.0,"contact_point_centroid":[0.49477,0.0639,0.0094],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54551,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48377,0.10745,0.11354]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49958,0.07267,0.06029],"force_p95":0.08272,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08405,"mean_force":0.05847,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49589,0.08343,0.03831]}],"total_contact_groups":11},"final_pose_error":0.01177,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49598,-0.04123,0.02416],"final_tcp_position":[0.49092,0.0847,0.12819],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":60.36021,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.49516,0.06406,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54911,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":505.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.47978,0.1111,0.16766],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":361.0,"n_steps_budget":750.0,"object_pos_end":[0.49518,0.06363,0.034],"object_pos_start":[0.49516,0.06406,0.03394],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14427,"object_z_max":0.034,"peak_contact_force":0.5415,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":361.0,"raw_peak_contact_force":0.5516,"subtask_id":"pre_contact","tcp_end":[0.48991,0.10412,0.05977],"tcp_start":[0.47978,0.1111,0.16766],"tcp_to_object_dist_end":0.04829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":180.0,"n_steps_budget":600.0,"object_pos_end":[0.49633,0.06144,0.03545],"object_pos_start":[0.49518,0.06363,0.034],"object_to_goal_dist_end":0.14156,"object_to_goal_dist_start":0.14384,"object_z_max":0.03588,"peak_contact_force":6.45633,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":203.0,"raw_peak_contact_force":4.75074,"tcp_end":[0.48889,0.09047,0.04212],"tcp_start":[0.48991,0.10412,0.05977],"tcp_to_object_dist_end":0.0307,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.49782,0.05916,0.03668],"object_pos_start":[0.49633,0.06144,0.03545],"object_to_goal_dist_end":0.13922,"object_to_goal_dist_start":0.14156,"object_z_max":0.03725,"peak_contact_force":4.55446,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":60.36021,"subtask_id":"insertion_goal","tcp_end":[0.49407,0.08528,0.03951],"tcp_start":[0.4926,0.08672,0.0402],"tcp_to_object_dist_end":0.02653,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.49598,-0.04123,0.02416],"object_pos_start":[0.49977,0.05649,0.03766],"object_to_goal_dist_end":0.04207,"object_to_goal_dist_start":0.13651,"object_z_max":0.04326,"peak_contact_force":0.58202,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":572.0,"raw_peak_contact_force":8.17101,"tcp_end":[0.49092,0.0847,0.12819],"tcp_start":[0.49407,0.08528,0.03951],"tcp_to_object_dist_end":0.16343,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```