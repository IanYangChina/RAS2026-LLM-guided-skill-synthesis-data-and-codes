## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → rotate → contact → push → retract | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.2657 | 0.56 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.3290 | 0.30 | ✅ accepted |
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2253 | 0.23 | ❌ rejected |
| 1 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2268 | 0.23 | ✅ accepted |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.56 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=0.266) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: push_through
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_above
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: rotate_to_align
  type: rotate
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  subtask_id: approach_peg
- id: descend_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 4.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: approach_peg
- id: push_through
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
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
      mode: keep_current
  parameters:
    push_duration:
      type: scalar
      range:
      - 2.0
      - 4.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_through
- id: retract_away
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
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_through

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **rotate_to_align** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings: none
- **descend_contact** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_away** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.266
- **task_score** (E): 0.560
- **fitness_score**: 0.356  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1839 |
| rotate_to_align | 1.00 | 0.0239 |
| descend_contact | 1.00 | 0.0920 |
| push_through | 1.00 | 0.1339 |
| retract_away | 1.00 | 0.0906 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.101, 0.146) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 |
| rotate_to_align | rotate | 1.00 / step_budget | (0.509, 0.101, 0.146)→(0.500, 0.123, 0.141) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 |
| descend_contact | contact | 1.00 / force_exceeded | (0.500, 0.123, 0.141)→(0.497, 0.122, 0.049) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 |
| push_through | push | 1.00 / time_limit | (0.497, 0.122, 0.049)→(0.494, -0.012, 0.046) | (0.504, 0.095, 0.034)→(0.502, 0.003, 0.039) | 0.175→0.084 |
| retract_away | retract | 1.00 / step_budget | (0.494, -0.012, 0.046)→(0.491, -0.012, 0.136) | (0.502, 0.003, 0.039)→(0.503, -0.015, 0.027) | 0.084→0.067 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.880
- alignment_error: None
- terminal_score: 0.880
- phase_score: 0.268
- phase_breakdown.approach_peg_score: 0.099
- phase_breakdown.push_through_score: 0.310

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.513
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.880
- **Median Q (composite search score)**: 0.230
- **K-run variance**: 0.0135
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63566,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.18943,"descend_contact.contact_force_threshold":6.95991,"push_through.push_duration":2.10551,"push_through.push_speed":0.07968,"retract_away.retract_speed":0.03828},"optimized_scores":{"best_composite_score":0.14473,"best_fitness_score":0.23473,"best_task_score":0.29076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.51083,0.06105,0.0093],"force_p95":53.0759,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.72654,"mean_force":43.84214,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50673,0.06987,0.05834]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.51433,0.07129,0.05794],"force_p95":52.60019,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.27372,"mean_force":43.37541,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50673,0.06987,0.05834]},{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50596,0.10458,0.00939],"force_p95":0.57572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.38725,"mean_force":0.58673,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.50802,0.13228,0.09935]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51245,0.12129,0.05879],"force_p95":15.91106,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.91106,"mean_force":15.91106,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.50719,0.13203,0.05951]},{"body_a":"peg","body_b":"channel_base_body","contact_count":908.0,"contact_point_centroid":[0.50094,0.01465,0.00835],"force_p95":0.68345,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.37628,"mean_force":0.60004,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50108,0.00294,0.10094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":480.0,"contact_point_centroid":[0.50562,0.10472,0.00937],"force_p95":0.57765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56989,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50948,0.15328,0.2182]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.5049,0.01461,0.05531],"force_p95":2.56931,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.20874,"mean_force":0.78909,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50397,0.00266,0.0555]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50005,0.19766,0.29593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":286.0,"contact_point_centroid":[0.5059,0.10464,0.00939],"force_p95":0.57563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57647,"mean_force":0.54633,"phase_index":1.0,"phase_name":"rotate_to_align","phase_type":"rotate","tcp_position_centroid":[0.5141,0.12237,0.14187]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.01328,0.0242],"force_p95":0.41121,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41121,"mean_force":0.41121,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50111,0.00298,0.13125]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":26.0,"contact_point_centroid":[0.4748,0.01852,0.05957],"force_p95":0.31463,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3652,"mean_force":0.08657,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50195,0.00277,0.05987]}],"total_contact_groups":11},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50537,0.01083,0.02415],"final_tcp_position":[0.50122,0.00298,0.14621],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":507.0,"n_steps_budget":630.0,"object_pos_end":[0.50599,0.10461,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.51964,0.11078,0.14627],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11343,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":286.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50599,0.10461,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18481,"object_z_max":0.03384,"phase_name":"rotate_to_align","phase_peak_obstacle_force":0.0,"phase_type":"rotate","subtask_id":"approach_peg","tcp_end":[0.51098,0.13301,0.14109],"tcp_start":[0.51964,0.11078,0.14627],"tcp_to_object_dist_end":0.11107,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":392.0,"n_steps_budget":930.0,"object_pos_end":[0.50592,0.10455,0.03384],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_peg","tcp_end":[0.50719,0.13204,0.05935],"tcp_start":[0.51098,0.13301,0.14109],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49743,0.03582,0.04065],"object_pos_start":[0.50592,0.10455,0.03384],"object_to_goal_dist_end":0.11585,"object_to_goal_dist_start":0.18475,"object_z_max":0.04065,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.50437,0.00303,0.05563],"tcp_start":[0.50719,0.13204,0.05935],"tcp_to_object_dist_end":0.03671,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.50537,0.01083,0.02415],"object_pos_start":[0.49743,0.03582,0.04065],"object_to_goal_dist_end":0.09236,"object_to_goal_dist_start":0.11585,"object_z_max":0.04071,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"push_through","tcp_end":[0.50122,0.00298,0.14621],"tcp_start":[0.50437,0.00303,0.05563],"tcp_to_object_dist_end":0.12238,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11429,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.15301,"descend_contact.contact_force_threshold":2.01873,"push_through.push_duration":3.20287,"push_through.push_speed":0.1464,"retract_away.retract_speed":0.07279},"optimized_scores":{"best_composite_score":0.42277,"best_fitness_score":0.51277,"best_task_score":0.87994},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":204.0,"contact_point_centroid":[0.47497,-0.04659,0.04378],"force_p95":255.49448,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.74959,"mean_force":154.19715,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48677,-0.04658,0.04179]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":165.0,"contact_point_centroid":[0.475,0.02376,0.02778],"force_p95":64.45594,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.92996,"mean_force":44.9267,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48683,0.02376,0.02582]},{"body_a":"attachment","body_b":"peg","contact_count":629.0,"contact_point_centroid":[0.4964,0.01552,0.04429],"force_p95":49.91064,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.58719,"mean_force":26.27565,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48686,0.02504,0.02584]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54788,-0.1,0.065],"force_p95":49.58023,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.39335,"mean_force":43.16686,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48685,-0.04763,0.02553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":659.0,"contact_point_centroid":[0.51021,-0.01027,0.00984],"force_p95":44.90728,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.58181,"mean_force":26.31704,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4869,0.02821,0.0259]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":367.0,"contact_point_centroid":[0.52511,-0.02916,0.06],"force_p95":34.89955,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.44317,"mean_force":23.75999,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48684,-0.00445,0.02577]},{"body_a":"peg","body_b":"link7","contact_count":622.0,"contact_point_centroid":[0.51957,0.01089,0.06158],"force_p95":33.70888,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.25826,"mean_force":20.84353,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48684,0.02425,0.02582]},{"body_a":"attachment","body_b":"peg","contact_count":96.0,"contact_point_centroid":[0.49542,-0.0574,0.05855],"force_p95":16.72448,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.27998,"mean_force":3.48965,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48679,-0.04677,0.0372]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52508,-0.07237,0.06],"force_p95":22.70943,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.17793,"mean_force":10.71908,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.4868,-0.04757,0.02671]},{"body_a":"peg","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.52053,-0.06005,0.06153],"force_p95":18.65491,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.44215,"mean_force":5.23932,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.4868,-0.04773,0.026]},{"body_a":"peg","body_b":"channel_base_body","contact_count":679.0,"contact_point_centroid":[0.5029,-0.07602,0.00947],"force_p95":0.60886,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.69574,"mean_force":0.61372,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48466,-0.04694,0.07368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":568.0,"contact_point_centroid":[0.50311,0.06702,0.00938],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.4281,"mean_force":0.56316,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.48977,0.09602,0.08319]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.49739,0.08455,0.05872],"force_p95":4.91476,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.96366,"mean_force":1.52549,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.4891,0.09586,0.03078]},{"body_a":"peg","body_b":"channel_base_body","contact_count":593.0,"contact_point_centroid":[0.50302,0.06743,0.00934],"force_p95":0.55519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56115,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49918,0.13629,0.21943]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.50318,0.06761,0.00938],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55089,"mean_force":0.54665,"phase_index":1.0,"phase_name":"rotate_to_align","phase_type":"rotate","tcp_position_centroid":[0.49534,0.08628,0.14128]}],"total_contact_groups":15},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50155,-0.07333,0.03381],"final_tcp_position":[0.48355,-0.04725,0.11612],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"phases":[{"n_steps":609.0,"n_steps_budget":870.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.49989,0.07524,0.14521],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11173,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":265.0,"n_steps_budget":600.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"phase_name":"rotate_to_align","phase_peak_obstacle_force":0.0,"phase_type":"rotate","subtask_id":"approach_peg","tcp_end":[0.49293,0.09662,0.14051],"tcp_start":[0.49989,0.07524,0.14521],"tcp_to_object_dist_end":0.1111,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":568.0,"n_steps_budget":930.0,"object_pos_end":[0.50304,0.06742,0.0339],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.03387,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_peg","tcp_end":[0.48901,0.09586,0.02863],"tcp_start":[0.49293,0.09662,0.14051],"tcp_to_object_dist_end":0.03214,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":661.0,"n_steps_budget":690.0,"object_pos_end":[0.50687,-0.0692,0.03611],"object_pos_start":[0.50304,0.06742,0.0339],"object_to_goal_dist_end":0.01338,"object_to_goal_dist_start":0.14758,"object_z_max":0.03673,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.48685,-0.04753,0.02553],"tcp_start":[0.48901,0.09586,0.02863],"tcp_to_object_dist_end":0.03134,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":706.0,"n_steps_budget":870.0,"object_pos_end":[0.50155,-0.07333,0.03381],"object_pos_start":[0.50687,-0.0692,0.03611],"object_to_goal_dist_end":0.00923,"object_to_goal_dist_start":0.01338,"object_z_max":0.03803,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"push_through","tcp_end":[0.48355,-0.04725,0.11612],"tcp_start":[0.48685,-0.04753,0.02553],"tcp_to_object_dist_end":0.08819,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.875,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.12886,"descend_contact.contact_force_threshold":2.9143,"push_through.push_duration":3.06482,"push_through.push_speed":0.07988,"retract_away.retract_speed":0.07749},"optimized_scores":{"best_composite_score":0.22959,"best_fitness_score":0.31959,"best_task_score":0.51005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50291,0.068,0.00916],"force_p95":53.48776,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.42597,"mean_force":42.04685,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49282,0.07633,0.0584]},{"body_a":"attachment","body_b":"peg","contact_count":990.0,"contact_point_centroid":[0.50288,0.07874,0.05758],"force_p95":53.01064,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.92337,"mean_force":41.99618,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49284,0.07699,0.05843]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.50363,0.11166,0.00941],"force_p95":0.60998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.90126,"mean_force":0.6193,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49434,0.13891,0.09994]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50118,0.12947,0.05876],"force_p95":30.52327,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.52327,"mean_force":30.52327,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49359,0.13867,0.05986]},{"body_a":"peg","body_b":"channel_base_body","contact_count":703.0,"contact_point_centroid":[0.50056,0.02216,0.0084],"force_p95":0.7276,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.51239,"mean_force":0.59231,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48739,0.00959,0.1012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.5035,0.11167,0.00937],"force_p95":0.61743,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55994,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50247,0.15759,0.21995]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.4908,0.02095,0.06371],"force_p95":0.63638,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.73189,"mean_force":0.28034,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48779,0.00949,0.06421]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.5038,0.11175,0.00939],"force_p95":0.60355,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63444,"mean_force":0.54516,"phase_index":1.0,"phase_name":"rotate_to_align","phase_type":"rotate","tcp_position_centroid":[0.50041,0.12949,0.14262]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49977,0.19914,0.29894]}],"total_contact_groups":9},"final_pose_error":0.01012,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50216,0.01768,0.02413],"final_tcp_position":[0.4875,0.00963,0.14631],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"phases":[{"n_steps":535.0,"n_steps_budget":900.0,"object_pos_end":[0.50369,0.11181,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.50627,0.11762,0.14691],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11328,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":318.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.11177,0.03384],"object_pos_start":[0.50369,0.11181,0.0338],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19194,"object_z_max":0.03391,"phase_name":"rotate_to_align","phase_peak_obstacle_force":0.0,"phase_type":"rotate","subtask_id":"approach_peg","tcp_end":[0.49725,0.13968,0.14194],"tcp_start":[0.50627,0.11762,0.14691],"tcp_to_object_dist_end":0.11184,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":402.0,"n_steps_budget":930.0,"object_pos_end":[0.50364,0.1117,0.03381],"object_pos_start":[0.50371,0.11177,0.03384],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.19191,"object_z_max":0.03402,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_peg","tcp_end":[0.49362,0.13869,0.05968],"tcp_start":[0.49725,0.13968,0.14194],"tcp_to_object_dist_end":0.03871,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50131,0.04314,0.04073],"object_pos_start":[0.50364,0.1117,0.03381],"object_to_goal_dist_end":0.12315,"object_to_goal_dist_start":0.19183,"object_z_max":0.04073,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.49061,0.00971,0.05594],"tcp_start":[0.49362,0.13869,0.05968],"tcp_to_object_dist_end":0.03825,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":710.0,"n_steps_budget":810.0,"object_pos_end":[0.50216,0.01768,0.02413],"object_pos_start":[0.50131,0.04314,0.04073],"object_to_goal_dist_end":0.09898,"object_to_goal_dist_start":0.12315,"object_z_max":0.04073,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"push_through","tcp_end":[0.4875,0.00963,0.14631],"tcp_start":[0.49061,0.00971,0.05594],"tcp_to_object_dist_end":0.12332,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```