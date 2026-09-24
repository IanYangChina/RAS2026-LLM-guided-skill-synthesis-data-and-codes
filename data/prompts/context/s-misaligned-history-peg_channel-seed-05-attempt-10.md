## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7  | -0.0562 | 0.00 | ❌ rejected |
| 9 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8  | -0.1272 | 0.00 | ❌ rejected |
| 8 | approach → descend → push → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 10  | 0.1461 | 0.22 | ❌ rejected |
| 7 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7  | -0.3118 | 0.00 | ❌ rejected |
| 6 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11  | -0.1055 | 0.07 | ❌ rejected |

**Proposal policy**: task_score is 0.07 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.105) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.015
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.08
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
    approach_height:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.015
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.015
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
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
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_threshold:
      type: scalar
      range:
      - 30.0
      - 39.0
      default: 36.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_to_goal
- id: retract_tcp
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.08], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.015], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_tcp** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.105
- **task_score** (E): 0.072
- **fitness_score**: 0.221  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_peg | 1.00 | 1.00 | 0.1865 |
| descend_to_push_height | 0.00 | 1.00 | 0.0414 |
| push_along_channel | 0.33 | 1.00 | 0.0932 |
| retract_tcp | 1.00 | 1.00 | 0.0803 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.184, 0.116) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.545 | 2.488 |
| descend_to_push_height | descend | 0.00 / step_budget | (0.509, 0.184, 0.116)→(0.504, 0.175, 0.077) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.540 | 0.594 |
| push_along_channel | push | 0.33 / step_budget | (0.504, 0.175, 0.077)→(0.501, 0.082, 0.072) | (0.504, 0.095, 0.034)→(0.504, 0.076, 0.031) | 0.175→0.156 | 1.00 / 2.000 | 11.291 | 14.935 |
| retract_tcp | retract | 1.00 / step_budget | (0.501, 0.082, 0.072)→(0.499, 0.081, 0.153) | (0.504, 0.076, 0.031)→(0.505, 0.076, 0.031) | 0.156→0.156 | 1.00 / 1.000 | 0.575 | 53.710 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.064
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.064
- phase_score: 0.289
- phase_breakdown.reach_contact_pose_score: 0.841
- phase_breakdown.push_to_exit_score: 0.053

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.299
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.151
- **Median Q (composite search score)**: -0.111
- **K-run variance**: 0.0134
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.322


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53659,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_height":0.04623,"approach_behind_peg.arc_height":0.05641,"descend_to_push_height.descend_force_threshold":7.00856,"descend_to_push_height.descend_speed":0.03597,"push_along_channel.push_distance":0.11974,"push_along_channel.push_force_threshold":27.37057,"push_along_channel.push_speed":0.06156},"optimized_scores":{"best_composite_score":-0.11136,"best_fitness_score":0.29864,"best_task_score":0.15083},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.50575,0.0967,0.00958],"force_p95":3.32627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.58912,"mean_force":1.07782,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50708,0.13405,0.0705]},{"body_a":"attachment","body_b":"peg","contact_count":200.0,"contact_point_centroid":[0.50602,0.10553,0.05858],"force_p95":4.62667,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.22653,"mean_force":2.7768,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50696,0.10572,0.07053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":743.0,"contact_point_centroid":[0.50575,0.10463,0.00938],"force_p95":0.57581,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56155,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50683,0.23115,0.18951]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.5053,0.21996,0.2912]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.50557,0.05826,0.008],"force_p95":0.74957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36079,"mean_force":0.61464,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50482,0.08159,0.10962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":81.0,"contact_point_centroid":[0.50539,0.10429,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57583,"mean_force":0.54644,"phase_index":1.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.51576,0.19003,0.08203]}],"total_contact_groups":6},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50631,0.0582,0.02413],"final_tcp_position":[0.5047,0.08159,0.15078],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":11.58912,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":770.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55173,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":775.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_contact_pose","tcp_end":[0.52064,0.19358,0.08849],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":81.0,"n_steps_budget":600.0,"object_pos_end":[0.50583,0.10467,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":0.54524,"phase_name":"descend_to_push_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":81.0,"raw_peak_contact_force":0.57583,"subtask_id":"reach_contact_pose","tcp_end":[0.51002,0.18673,0.07554],"tcp_start":[0.52064,0.19358,0.08849],"tcp_to_object_dist_end":0.09215,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50513,0.0575,0.02489],"object_pos_start":[0.50583,0.10467,0.03384],"object_to_goal_dist_end":0.13842,"object_to_goal_dist_start":0.18486,"object_z_max":0.04067,"peak_contact_force":0.66357,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1191.0,"raw_peak_contact_force":11.58912,"subtask_id":"push_to_exit","tcp_end":[0.50689,0.08262,0.07057],"tcp_start":[0.51002,0.18673,0.07554],"tcp_to_object_dist_end":0.05216,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":660.0,"object_pos_end":[0.50631,0.0582,0.02413],"object_pos_start":[0.50513,0.0575,0.02489],"object_to_goal_dist_end":0.13925,"object_to_goal_dist_start":0.13842,"object_z_max":0.02489,"peak_contact_force":0.63177,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":247.0,"raw_peak_contact_force":1.36079,"tcp_end":[0.5047,0.08159,0.15078],"tcp_start":[0.50689,0.08262,0.07057],"tcp_to_object_dist_end":0.12881,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28369,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_height":0.09838,"approach_behind_peg.arc_height":0.05362,"descend_to_push_height.descend_force_threshold":12.85696,"descend_to_push_height.descend_speed":0.02936,"push_along_channel.push_distance":0.14001,"push_along_channel.push_force_threshold":30.28094,"push_along_channel.push_speed":0.0351},"optimized_scores":{"best_composite_score":-0.24408,"best_fitness_score":0.16592,"best_task_score":0.00026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":641.0,"contact_point_centroid":[0.50305,0.0675,0.00935],"force_p95":0.55497,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56007,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49692,0.21036,0.20421]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55086,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.49936,0.15157,0.10658]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50307,0.06745,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49686,0.11309,0.07275]},{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.5031,0.0674,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55058,"mean_force":0.54665,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49469,0.08274,0.11168]}],"total_contact_groups":4},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50304,0.06742,0.0338],"final_tcp_position":[0.49457,0.08272,0.15287],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":2.06903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54348,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":641.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_contact_pose","tcp_end":[0.50066,0.15692,0.1362],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54352,"phase_name":"descend_to_push_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":315.0,"raw_peak_contact_force":0.55086,"subtask_id":"reach_contact_pose","tcp_end":[0.49979,0.14701,0.07752],"tcp_start":[0.50066,0.15692,0.1362],"tcp_to_object_dist_end":0.09083,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54559,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55071,"subtask_id":"push_to_exit","tcp_end":[0.4967,0.08376,0.0727],"tcp_start":[0.49979,0.14701,0.07752],"tcp_to_object_dist_end":0.04267,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":660.0,"object_pos_end":[0.50304,0.06742,0.0338],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54778,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":244.0,"raw_peak_contact_force":0.55058,"tcp_end":[0.49457,0.08272,0.15287],"tcp_start":[0.4967,0.08376,0.0727],"tcp_to_object_dist_end":0.12035,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_height":0.08172,"approach_behind_peg.arc_height":0.05414,"descend_to_push_height.descend_force_threshold":16.33187,"descend_to_push_height.descend_speed":0.02498,"push_along_channel.push_distance":0.13476,"push_along_channel.push_force_threshold":30.39383,"push_along_channel.push_speed":0.07241},"optimized_scores":{"best_composite_score":0.03903,"best_fitness_score":0.19903,"best_task_score":0.06376},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.475,0.11989,0.05608],"force_p95":153.91396,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.21938,"mean_force":88.3766,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49809,0.07999,0.07619]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.525,0.1199,0.05827],"force_p95":26.89657,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.56938,"mean_force":6.40792,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49849,0.07984,0.07355]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11992,0.05412],"force_p95":32.43516,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.66427,"mean_force":30.37311,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49853,0.08001,0.07351]},{"body_a":"peg","body_b":"channel_base_body","contact_count":918.0,"contact_point_centroid":[0.50373,0.11013,0.00944],"force_p95":0.77687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.16395,"mean_force":0.73712,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49867,0.13572,0.07332]},{"body_a":"peg","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.50489,0.12457,0.04293],"force_p95":6.62769,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.83544,"mean_force":2.88094,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49851,0.08487,0.07344]},{"body_a":"peg","body_b":"channel_base_body","contact_count":637.0,"contact_point_centroid":[0.5036,0.11173,0.00936],"force_p95":0.63987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55744,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50005,0.23357,0.2064]},{"body_a":"peg","body_b":"channel_base_body","contact_count":221.0,"contact_point_centroid":[0.50366,0.11169,0.00942],"force_p95":0.60704,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65606,"mean_force":0.54268,"phase_index":1.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.50383,0.19609,0.10095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":245.0,"contact_point_centroid":[0.50508,0.10128,0.00944],"force_p95":0.57954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60747,"mean_force":0.54573,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.4966,0.07927,0.11252]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.5042,0.20587,0.29992]},{"body_a":"peg","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.50514,0.11955,0.05068],"force_p95":0.15975,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19468,"mean_force":0.06795,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49765,0.07986,0.08078]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.525,0.11995,0.0581],"force_p95":0.0,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49853,0.07995,0.07351]}],"total_contact_groups":11},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50538,0.10158,0.03384],"final_tcp_position":[0.49642,0.07886,0.15389],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":159.21938,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":659.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53855,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":653.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_contact_pose","tcp_end":[0.50716,0.20117,0.1234],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11174,0.03383],"object_pos_start":[0.50371,0.11177,0.03383],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19191,"object_z_max":0.03397,"peak_contact_force":0.53167,"phase_name":"descend_to_push_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":221.0,"raw_peak_contact_force":0.65606,"subtask_id":"reach_contact_pose","tcp_end":[0.50155,0.19165,0.07825],"tcp_start":[0.50716,0.20117,0.1234],"tcp_to_object_dist_end":0.09145,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.50529,0.10163,0.03508],"object_pos_start":[0.50367,0.11174,0.03383],"object_to_goal_dist_end":0.18178,"object_to_goal_dist_start":0.19187,"object_z_max":0.03517,"peak_contact_force":32.66427,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":986.0,"raw_peak_contact_force":32.66427,"subtask_id":"push_to_exit","tcp_end":[0.49853,0.07986,0.07351],"tcp_start":[0.50155,0.19165,0.07825],"tcp_to_object_dist_end":0.04468,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":630.0,"object_pos_end":[0.50538,0.10158,0.03384],"object_pos_start":[0.50529,0.10163,0.03508],"object_to_goal_dist_end":0.18176,"object_to_goal_dist_start":0.18178,"object_z_max":0.03508,"peak_contact_force":0.54426,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":269.0,"raw_peak_contact_force":159.21938,"tcp_end":[0.49642,0.07886,0.15389],"tcp_start":[0.49853,0.07986,0.07351],"tcp_to_object_dist_end":0.12251,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```