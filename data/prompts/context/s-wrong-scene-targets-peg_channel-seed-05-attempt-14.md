## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4598 | 0.76 | ❌ rejected |
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3365 | 0.75 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4803 | 0.82 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4966 | 0.85 | ✅ accepted |
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | -0.0256 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5244002338996304, -0.05536473682108051, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, -0.05536473682108051, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5244002338996304, 0.1046352631789195, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5244002338996304, 0.1046352631789195, 0.04]
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
  frozen_object_starts: {'peg': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.849, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5244002338996304, -0.05536473682108051, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=0.460) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_behind
  anchor: object
  offset:
  - 0.0
  - 0.12
  - 0.0
  weight: 0.3
- id: push_through_channel
  anchor: object
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: align_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.12
    - 0.04
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.002
      - 0.02
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_behind
- id: descend_to_push
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.12
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.002
      - 0.02
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_behind
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_during_push
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_through_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.12, 0.04], tolerance=0.005
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_push** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.12, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_during_push, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.460
- **task_score** (E): 0.762
- **fitness_score**: 0.840  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_behind | 1.00 | 1.00 | 0.2148 |
| descend_to_push | 1.00 | 1.00 | 0.0511 |
| push_channel | 1.00 | 0.67 | 0.2524 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.212, 0.087) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.541 | 2.488 |
| descend_to_push | descend | 1.00 / step_budget | (0.508, 0.212, 0.087)→(0.501, 0.213, 0.037) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.563 | 0.587 |
| push_channel | push | 1.00 / step_budget | (0.501, 0.213, 0.037)→(0.502, -0.040, 0.030) | (0.504, 0.095, 0.034)→(0.502, -0.072, 0.040) | 0.175→0.011 | 0.67 / 1.667 | 23.682 | 59.136 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.947
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.947
- phase_score: 0.944
- phase_breakdown.push_through_channel_score: 0.971
- phase_breakdown.reach_behind_score: 0.881

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.945
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.947
- **Median Q (composite search score)**: 0.526
- **K-run variance**: 0.0149
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.290


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
{"anchors":[{"name":"object","value":[0.5244,-0.05536,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,-0.05536,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88189,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.approach_speed":0.12684,"align_behind.approach_tolerance":0.01393,"descend_to_push.descend_speed":0.0719,"descend_to_push.descend_tolerance":0.01121,"push_channel.push_distance":0.18016,"push_channel.push_speed":0.08625,"push_channel.push_tolerance":0.048},"optimized_scores":{"best_composite_score":0.28851,"best_fitness_score":0.66851,"best_task_score":0.43521},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":163.0,"contact_point_centroid":[0.50354,0.06525,0.00926],"force_p95":13.53034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.44313,"mean_force":2.24203,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50346,0.1252,0.03298]},{"body_a":"attachment","body_b":"peg","contact_count":87.0,"contact_point_centroid":[0.50442,0.06078,0.04943],"force_p95":19.16586,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.19813,"mean_force":3.11872,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50382,0.07116,0.0313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.50897,0.20996,0.19142]},{"body_a":"peg","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.51383,0.00506,0.07049],"force_p95":2.28447,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.93921,"mean_force":0.5886,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50402,0.03504,0.03075]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.49969,0.19969,0.29735]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47491,0.02154,0.05999],"force_p95":1.58998,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62239,"mean_force":1.32011,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50393,0.04971,0.03092]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52509,-0.02268,0.02287],"force_p95":1.53367,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59431,"mean_force":1.09472,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50414,0.01294,0.03044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":245.0,"contact_point_centroid":[0.50578,0.10455,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57575,"mean_force":0.54634,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.51116,0.22135,0.06429]}],"total_contact_groups":8},"final_pose_error":0.04992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50276,-0.06012,0.03792],"final_tcp_position":[0.50429,-0.02573,0.02985],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":39.44313,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_behind","tcp_end":[0.51914,0.22131,0.09086],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.1047,0.03384],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.1849,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":0.5757,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":245.0,"raw_peak_contact_force":0.57575,"subtask_id":"reach_behind","tcp_end":[0.50445,0.22244,0.03804],"tcp_start":[0.51914,0.22131,0.09086],"tcp_to_object_dist_end":0.11782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.50276,-0.06012,0.03792],"object_pos_start":[0.50596,0.1047,0.03384],"object_to_goal_dist_end":0.02018,"object_to_goal_dist_start":0.1849,"object_z_max":0.04387,"peak_contact_force":39.44313,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":287.0,"raw_peak_contact_force":39.44313,"subtask_id":"push_through_channel","tcp_end":[0.50429,-0.02573,0.02985],"tcp_start":[0.50445,0.22244,0.03804],"tcp_to_object_dist_end":0.03536,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,-0.09254,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.09254,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21656,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.approach_speed":0.13601,"align_behind.approach_tolerance":0.01207,"descend_to_push.descend_speed":0.05299,"descend_to_push.descend_tolerance":0.0085,"push_channel.push_distance":0.17099,"push_channel.push_speed":0.05681,"push_channel.push_tolerance":0.04619},"optimized_scores":{"best_composite_score":0.56527,"best_fitness_score":0.94527,"best_task_score":0.94711},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":121.0,"contact_point_centroid":[0.50238,0.01237,0.04795],"force_p95":31.14252,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.27078,"mean_force":4.54554,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49963,0.02326,0.03014]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52521,0.0004,0.05946],"force_p95":60.48746,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.21433,"mean_force":34.41317,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49956,0.02937,0.03022]},{"body_a":"peg","body_b":"channel_base_body","contact_count":146.0,"contact_point_centroid":[0.50393,0.04356,0.00939],"force_p95":14.94882,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.39476,"mean_force":2.99113,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49828,0.11044,0.03181]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49588,-0.10066,0.01634],"force_p95":11.18279,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.83994,"mean_force":6.2823,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50084,-0.05228,0.02951]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47455,-0.04406,0.02382],"force_p95":5.07952,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.65859,"mean_force":2.74824,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50023,-0.01433,0.02982]},{"body_a":"peg","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.51405,-0.05015,0.0687],"force_p95":4.66896,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.57425,"mean_force":1.37041,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50035,-0.02075,0.02978]},{"body_a":"peg","body_b":"channel_base_body","contact_count":925.0,"contact_point_centroid":[0.50305,0.06743,0.00936],"force_p95":0.55244,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55595,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.49898,0.19251,0.18846]},{"body_a":"peg","body_b":"channel_base_body","contact_count":283.0,"contact_point_centroid":[0.50306,0.06764,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55074,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.49793,0.18594,0.05852]}],"total_contact_groups":8},"final_pose_error":0.04957,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5013,-0.08408,0.04038],"final_tcp_position":[0.50085,-0.0542,0.02949],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":68.27078,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":941.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54551,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":925.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_behind","tcp_end":[0.49946,0.1867,0.08373],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":283.0,"n_steps_budget":600.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54361,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":283.0,"raw_peak_contact_force":0.55074,"subtask_id":"reach_behind","tcp_end":[0.49867,0.18599,0.0357],"tcp_start":[0.49946,0.1867,0.08373],"tcp_to_object_dist_end":0.11863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5013,-0.08408,0.04038],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.00429,"object_to_goal_dist_start":0.14762,"object_z_max":0.04639,"peak_contact_force":31.60393,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":299.0,"raw_peak_contact_force":68.27078,"subtask_id":"push_through_channel","tcp_end":[0.50085,-0.0542,0.02949],"tcp_start":[0.49867,0.18599,0.0357],"tcp_to_object_dist_end":0.0318,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,-0.04822,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,-0.04822,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01695,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.approach_speed":0.19983,"align_behind.approach_tolerance":0.01292,"descend_to_push.descend_speed":0.14748,"descend_to_push.descend_tolerance":0.0166,"push_channel.push_distance":0.1998,"push_channel.push_speed":0.08727,"push_channel.push_tolerance":0.06592},"optimized_scores":{"best_composite_score":0.52576,"best_fitness_score":0.90576,"best_task_score":0.90342},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52548,0.03487,0.04874],"force_p95":45.22583,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.69336,"mean_force":13.55701,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50057,0.06436,0.03051]},{"body_a":"attachment","body_b":"peg","contact_count":86.0,"contact_point_centroid":[0.50328,0.0397,0.04332],"force_p95":47.69578,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.02285,"mean_force":10.86669,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50072,0.05078,0.03041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":152.0,"contact_point_centroid":[0.50162,0.07171,0.00907],"force_p95":27.40269,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.29268,"mean_force":3.91755,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4998,0.13627,0.03217]},{"body_a":"peg","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.5083,-0.01906,0.0703],"force_p95":6.82921,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.0372,"mean_force":1.5529,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50115,0.00658,0.02996]},{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.50356,0.11168,0.00938],"force_p95":0.61652,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55614,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.5025,0.21305,0.19184]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.50381,0.11173,0.00939],"force_p95":0.6064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63463,"mean_force":0.54577,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.50218,0.22855,0.06067]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.49972,0.19975,0.29899]}],"total_contact_groups":7},"final_pose_error":0.04942,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50298,-0.07078,0.0412],"final_tcp_position":[0.50168,-0.03886,0.02955],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":69.69336,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":683.0,"n_steps_budget":720.0,"object_pos_end":[0.5037,0.11179,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53522,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":677.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_behind","tcp_end":[0.50612,0.22853,0.08652],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":260.0,"n_steps_budget":600.0,"object_pos_end":[0.50368,0.11174,0.0338],"object_pos_start":[0.5037,0.11179,0.0338],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19193,"object_z_max":0.03385,"peak_contact_force":0.56868,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":260.0,"raw_peak_contact_force":0.63463,"subtask_id":"reach_behind","tcp_end":[0.50028,0.22959,0.03656],"tcp_start":[0.50612,0.22853,0.08652],"tcp_to_object_dist_end":0.11793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.50298,-0.07078,0.0412],"object_pos_start":[0.50368,0.11174,0.0338],"object_to_goal_dist_end":0.00977,"object_to_goal_dist_start":0.19187,"object_z_max":0.04487,"peak_contact_force":0.0,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":318.0,"raw_peak_contact_force":69.69336,"subtask_id":"push_through_channel","tcp_end":[0.50168,-0.03886,0.02955],"tcp_start":[0.50028,0.22959,0.03656],"tcp_to_object_dist_end":0.034,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```