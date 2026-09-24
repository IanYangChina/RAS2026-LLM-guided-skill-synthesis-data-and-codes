## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → rotate → contact → push → retract | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.2382 | 0.57 | ✅ accepted |
| 6 | approach → rotate → contact → push → retract | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.0195 | 0.34 | ❌ rejected |
| 5 | approach → rotate → contact → push → retract | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.1302 | 0.31 | ❌ rejected |
| 4 | approach → rotate → contact → push → retract | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.2657 | 0.56 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.3290 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.238) — your mutation base

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

- **Composite score**: 0.238
- **task_score** (E): 0.565
- **fitness_score**: 0.328  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1839 |
| rotate_to_align | 1.00 | 0.0240 |
| descend_contact | 1.00 | 0.0924 |
| push_through | 1.00 | 0.1353 |
| retract_away | 1.00 | 0.0899 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.101, 0.146) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 |
| rotate_to_align | rotate | 1.00 / step_budget | (0.509, 0.101, 0.146)→(0.500, 0.123, 0.141) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 |
| descend_contact | contact | 1.00 / force_exceeded | (0.500, 0.123, 0.141)→(0.497, 0.122, 0.049) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 |
| push_through | push | 1.00 / time_limit | (0.497, 0.122, 0.049)→(0.494, -0.013, 0.045) | (0.504, 0.095, 0.034)→(0.502, 0.002, 0.039) | 0.175→0.083 |
| retract_away | retract | 1.00 / step_budget | (0.494, -0.013, 0.045)→(0.491, -0.013, 0.135) | (0.502, 0.002, 0.039)→(0.504, -0.015, 0.027) | 0.083→0.067 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.857
- alignment_error: None
- terminal_score: 0.857
- phase_score: 0.127
- phase_breakdown.approach_peg_score: 0.096
- phase_breakdown.push_through_score: 0.134

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.419
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.857
- **Median Q (composite search score)**: 0.232
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.273


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69466,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.06817,"descend_contact.contact_force_threshold":5.7336,"push_through.push_duration":3.30552,"push_through.push_speed":0.0833,"retract_away.retract_speed":0.10873},"optimized_scores":{"best_composite_score":0.15382,"best_fitness_score":0.24382,"best_task_score":0.31648},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.51057,0.05926,0.00933],"force_p95":53.52612,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.06048,"mean_force":42.61012,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50647,0.06705,0.05827]},{"body_a":"attachment","body_b":"peg","contact_count":968.0,"contact_point_centroid":[0.5142,0.07066,0.05796],"force_p95":53.06081,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.61619,"mean_force":43.53767,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50655,0.06929,0.05837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.50592,0.10467,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.27955,"mean_force":0.60959,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.50783,0.13271,0.09931]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51219,0.12168,0.05876],"force_p95":24.71064,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.71064,"mean_force":24.71064,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.50701,0.13247,0.05953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.50124,0.0148,0.00851],"force_p95":0.90621,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.49672,"mean_force":0.83711,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50055,-0.00301,0.09844]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.52501,-0.01615,0.02463],"force_p95":8.64521,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.06373,"mean_force":3.89878,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50037,-0.00296,0.12096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.50564,0.1047,0.00937],"force_p95":0.57645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56575,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5092,0.15365,0.21882]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49985,0.19821,0.29688]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.03375,0.02503],"force_p95":0.74939,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76236,"mean_force":0.64045,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50037,-0.00301,0.075]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.50178,0.00874,0.06105],"force_p95":0.60151,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.74991,"mean_force":0.33371,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50137,-0.00321,0.06114]},{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.50581,0.10458,0.00939],"force_p95":0.57568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57608,"mean_force":0.54634,"phase_index":1.0,"phase_name":"rotate_to_align","phase_type":"rotate","tcp_position_centroid":[0.51387,0.12284,0.14164]}],"total_contact_groups":11},"final_pose_error":0.01214,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50627,0.00702,0.02412],"final_tcp_position":[0.50059,-0.00295,0.1434],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.51959,0.11072,0.14614],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11328,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":323.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.1047,0.03384],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.1849,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"phase_name":"rotate_to_align","phase_peak_obstacle_force":0.0,"phase_type":"rotate","subtask_id":"approach_peg","tcp_end":[0.51079,0.13346,0.14095],"tcp_start":[0.51959,0.11072,0.14614],"tcp_to_object_dist_end":0.11101,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":391.0,"n_steps_budget":930.0,"object_pos_end":[0.50599,0.10469,0.03384],"object_pos_start":[0.50597,0.1047,0.03384],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.1849,"object_z_max":0.03384,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_peg","tcp_end":[0.50701,0.13247,0.05938],"tcp_start":[0.51079,0.13346,0.14095],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49759,0.03087,0.04043],"object_pos_start":[0.50599,0.10469,0.03384],"object_to_goal_dist_end":0.1109,"object_to_goal_dist_start":0.18489,"object_z_max":0.04067,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.5037,-0.00294,0.05514],"tcp_start":[0.50701,0.13247,0.05938],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.50627,0.00702,0.02412],"object_pos_start":[0.49759,0.03087,0.04043],"object_to_goal_dist_end":0.08868,"object_to_goal_dist_start":0.1109,"object_z_max":0.04043,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"push_through","tcp_end":[0.50059,-0.00295,0.1434],"tcp_start":[0.5037,-0.00294,0.05514],"tcp_to_object_dist_end":0.11983,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7623,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.11028,"descend_contact.contact_force_threshold":5.09178,"push_through.push_duration":2.84589,"push_through.push_speed":0.13681,"retract_away.retract_speed":0.06423},"optimized_scores":{"best_composite_score":0.32874,"best_fitness_score":0.41874,"best_task_score":0.85677},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":210.0,"contact_point_centroid":[0.47497,-0.0446,0.04405],"force_p95":219.42056,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.93352,"mean_force":132.24682,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48678,-0.04459,0.04206]},{"body_a":"channel_base_body","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.55113,-0.1,0.06499],"force_p95":118.69069,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.60656,"mean_force":106.72468,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48726,-0.04342,0.02499]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.525,-0.00435,0.06],"force_p95":108.52171,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.85556,"mean_force":71.7214,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48688,-0.00721,0.02476]},{"body_a":"attachment","body_b":"peg","contact_count":686.0,"contact_point_centroid":[0.49668,0.01492,0.04692],"force_p95":54.2486,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.47961,"mean_force":29.42055,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4869,0.02458,0.0248]},{"body_a":"peg","body_b":"channel_base_body","contact_count":717.0,"contact_point_centroid":[0.51321,-0.00991,0.00974],"force_p95":52.0964,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.64975,"mean_force":32.30149,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48693,0.02756,0.02485]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":52.0,"contact_point_centroid":[0.475,0.02904,0.02673],"force_p95":50.41292,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.28954,"mean_force":34.75068,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48684,0.02905,0.02477]},{"body_a":"peg","body_b":"link7","contact_count":686.0,"contact_point_centroid":[0.51962,0.01119,0.06066],"force_p95":39.60192,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.82554,"mean_force":26.13027,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48689,0.02454,0.02479]},{"body_a":"channel_base_body","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.55028,-0.1,0.065],"force_p95":46.11103,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.5268,"mean_force":42.36911,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48752,-0.04543,0.02519]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":390.0,"contact_point_centroid":[0.52515,-0.03072,0.05998],"force_p95":36.14985,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.61276,"mean_force":23.5984,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48689,-0.00617,0.02479]},{"body_a":"attachment","body_b":"peg","contact_count":149.0,"contact_point_centroid":[0.49568,-0.05508,0.0589],"force_p95":0.82378,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.43086,"mean_force":0.80978,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48682,-0.04466,0.04092]},{"body_a":"peg","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.52058,-0.05813,0.06108],"force_p95":22.67814,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.89569,"mean_force":6.7871,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.4872,-0.04555,0.02551]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52527,-0.06987,0.05999],"force_p95":14.08963,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.51015,"mean_force":3.84933,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48741,-0.04552,0.02528]},{"body_a":"peg","body_b":"channel_base_body","contact_count":749.0,"contact_point_centroid":[0.50624,-0.07441,0.00958],"force_p95":0.60017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.14535,"mean_force":0.59479,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48513,-0.04489,0.07228]},{"body_a":"peg","body_b":"channel_base_body","contact_count":574.0,"contact_point_centroid":[0.50305,0.06676,0.00938],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.20918,"mean_force":0.57576,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.48975,0.09596,0.08254]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.4974,0.0845,0.05877],"force_p95":5.43575,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.76584,"mean_force":2.12302,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.48908,0.0958,0.03053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":630.0,"contact_point_centroid":[0.50301,0.06746,0.00935],"force_p95":0.55503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5603,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49911,0.13627,0.21939]}],"total_contact_groups":17},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5033,-0.06962,0.03379],"final_tcp_position":[0.48424,-0.04513,0.11582],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"phases":[{"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.49987,0.07518,0.14514],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11165,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":265.0,"n_steps_budget":600.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50307,0.0675,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"phase_name":"rotate_to_align","phase_peak_obstacle_force":0.0,"phase_type":"rotate","subtask_id":"approach_peg","tcp_end":[0.49291,0.09656,0.14044],"tcp_start":[0.49987,0.07518,0.14514],"tcp_to_object_dist_end":0.11101,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":574.0,"n_steps_budget":930.0,"object_pos_end":[0.50312,0.06734,0.0342],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14749,"object_to_goal_dist_start":0.14758,"object_z_max":0.03417,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_peg","tcp_end":[0.48909,0.09583,0.02742],"tcp_start":[0.49291,0.09656,0.14044],"tcp_to_object_dist_end":0.03247,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":717.0,"n_steps_budget":750.0,"object_pos_end":[0.50669,-0.06778,0.03605],"object_pos_start":[0.50312,0.06734,0.0342],"object_to_goal_dist_end":0.01448,"object_to_goal_dist_start":0.14749,"object_z_max":0.03607,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.48751,-0.0454,0.02519],"tcp_start":[0.48909,0.09583,0.02742],"tcp_to_object_dist_end":0.03142,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":759.0,"n_steps_budget":990.0,"object_pos_end":[0.5033,-0.06962,0.03379],"object_pos_start":[0.50669,-0.06778,0.03605],"object_to_goal_dist_end":0.01254,"object_to_goal_dist_start":0.01448,"object_z_max":0.03676,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"push_through","tcp_end":[0.48424,-0.04513,0.11582],"tcp_start":[0.48751,-0.0454,0.02519],"tcp_to_object_dist_end":0.0877,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60656,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.12362,"descend_contact.contact_force_threshold":6.29781,"push_through.push_duration":2.64233,"push_through.push_speed":0.07942,"retract_away.retract_speed":0.05717},"optimized_scores":{"best_composite_score":0.23198,"best_fitness_score":0.32198,"best_task_score":0.52272},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50285,0.06825,0.00919],"force_p95":52.47339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.42995,"mean_force":40.64322,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49275,0.07625,0.05849]},{"body_a":"attachment","body_b":"peg","contact_count":975.0,"contact_point_centroid":[0.50287,0.0797,0.05768],"force_p95":51.97992,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.92988,"mean_force":41.20237,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4928,0.07791,0.05855]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.50375,0.1116,0.0094],"force_p95":0.60586,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.15616,"mean_force":0.64822,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49437,0.13886,0.10008]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50149,0.12965,0.05884],"force_p95":41.76026,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.76026,"mean_force":41.76026,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49363,0.13863,0.06006]},{"body_a":"peg","body_b":"channel_base_body","contact_count":840.0,"contact_point_centroid":[0.50151,0.02254,0.00837],"force_p95":0.70629,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.61932,"mean_force":0.60807,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48728,0.00959,0.10129]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.525,0.04046,0.02419],"force_p95":6.38994,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.39144,"mean_force":3.40053,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.48725,0.00963,0.12509]},{"body_a":"peg","body_b":"channel_base_body","contact_count":514.0,"contact_point_centroid":[0.50353,0.11164,0.00938],"force_p95":0.6124,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50244,0.15761,0.21998]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.49088,0.02099,0.06268],"force_p95":0.53046,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.64561,"mean_force":0.27321,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.4877,0.00949,0.06326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":308.0,"contact_point_centroid":[0.50368,0.11171,0.00942],"force_p95":0.59502,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62584,"mean_force":0.54276,"phase_index":1.0,"phase_name":"rotate_to_align","phase_type":"rotate","tcp_position_centroid":[0.50046,0.12944,0.14283]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49977,0.19915,0.29895]}],"total_contact_groups":10},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50289,0.01878,0.02413],"final_tcp_position":[0.4874,0.00963,0.14649],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"phases":[{"n_steps":536.0,"n_steps_budget":930.0,"object_pos_end":[0.50375,0.11177,0.03388],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.50626,0.11773,0.1471],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1134,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":308.0,"n_steps_budget":600.0,"object_pos_end":[0.50372,0.11172,0.0339],"object_pos_start":[0.50375,0.11177,0.03388],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.1919,"object_z_max":0.03401,"phase_name":"rotate_to_align","phase_peak_obstacle_force":0.0,"phase_type":"rotate","subtask_id":"approach_peg","tcp_end":[0.49728,0.13964,0.14214],"tcp_start":[0.50626,0.11773,0.1471],"tcp_to_object_dist_end":0.11197,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":402.0,"n_steps_budget":930.0,"object_pos_end":[0.50373,0.11176,0.03386],"object_pos_start":[0.50372,0.11172,0.0339],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19185,"object_z_max":0.03393,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_peg","tcp_end":[0.49363,0.13864,0.05987],"tcp_start":[0.49728,0.13964,0.14214],"tcp_to_object_dist_end":0.03874,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50116,0.04364,0.04073],"object_pos_start":[0.50373,0.11176,0.03386],"object_to_goal_dist_end":0.12365,"object_to_goal_dist_start":0.1919,"object_z_max":0.04073,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.49048,0.00971,0.05598],"tcp_start":[0.49363,0.13864,0.05987],"tcp_to_object_dist_end":0.0387,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.50289,0.01878,0.02413],"object_pos_start":[0.50116,0.04364,0.04073],"object_to_goal_dist_end":0.10009,"object_to_goal_dist_start":0.12365,"object_z_max":0.04073,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"push_through","tcp_end":[0.4874,0.00963,0.14649],"tcp_start":[0.49048,0.00971,0.05598],"tcp_to_object_dist_end":0.12368,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```