## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4533 | 0.62 | ❌ rejected |
| 11 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1528 | 0.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5969 | 0.75 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5839 | 0.64 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2627 | 0.59 | ❌ rejected |

**Proposal policy**: task_score is 0.62 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.453) — your mutation base

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

- **Composite score**: 0.453
- **task_score** (E): 0.622
- **fitness_score**: 0.513  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2581 |
| contact_side | 1.00 | 1.00 | 0.0195 |
| push_channel | 0.67 | 1.00 | 0.1053 |
| retract | 1.00 | 1.00 | 0.0889 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.134, 0.052) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 142.442 | 164.836 |
| contact_side | contact | 1.00 / force_exceeded | (0.495, 0.134, 0.052)→(0.493, 0.116, 0.046) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.035) | 0.161→0.160 | 1.00 / 2.000 | 20.274 | 20.078 |
| push_channel | push | 0.67 / step_budget | (0.493, 0.116, 0.046)→(0.490, 0.010, 0.043) | (0.500, 0.080, 0.035)→(0.503, -0.024, 0.036) | 0.160→0.058 | 1.00 / 1.667 | 17.865 | 38.112 |
| retract | retract | 1.00 / step_budget | (0.490, 0.010, 0.043)→(0.487, 0.010, 0.131) | (0.503, -0.024, 0.036)→(0.502, -0.027, 0.034) | 0.058→0.057 | 1.00 / 1.000 | 0.544 | 24.383 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.410
- terminal_score: 0.983
- phase_score: 0.541
- phase_breakdown.insertion_goal_score: 0.421
- phase_breakdown.pre_contact_score: 0.821

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.718
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.983
- **Median Q (composite search score)**: 0.630
- **K-run variance**: 0.0730
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48718,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_y_offset":0.05727,"contact_side.contact_force":3.39065,"push_channel.force_limit_threshold":35.45124,"push_channel.insertion_depth":0.15388,"push_channel.push_speed":0.0455},"optimized_scores":{"best_composite_score":0.6302,"best_fitness_score":0.6902,"best_task_score":0.88274},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":216.0,"contact_point_centroid":[0.5253,0.00689,0.03414],"force_p95":29.37094,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.35062,"mean_force":6.30158,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49829,0.03557,0.03385]},{"body_a":"attachment","body_b":"peg","contact_count":284.0,"contact_point_centroid":[0.50306,0.01315,0.04803],"force_p95":28.08339,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.31507,"mean_force":6.2511,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49833,0.02468,0.03384]},{"body_a":"peg","body_b":"channel_base_body","contact_count":122.0,"contact_point_centroid":[0.50541,-0.01708,0.0098],"force_p95":16.72318,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.68714,"mean_force":5.20432,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49863,0.02656,0.03419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":224.0,"contact_point_centroid":[0.50391,0.06164,0.00938],"force_p95":0.55168,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.13672,"mean_force":0.58403,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.50303,0.10689,0.04165]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50407,0.07941,0.0552],"force_p95":6.45003,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.68646,"mean_force":4.3222,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.50173,0.09145,0.03806]},{"body_a":"peg","body_b":"channel_base_body","contact_count":791.0,"contact_point_centroid":[0.50365,0.06156,0.00935],"force_p95":0.58219,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55687,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5026,0.15983,0.16969]},{"body_a":"peg","body_b":"channel_base_body","contact_count":532.0,"contact_point_centroid":[0.50593,-0.0803,0.0094],"force_p95":0.61637,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31844,"mean_force":0.55157,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49481,-0.04364,0.07802]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49978,0.19919,0.29833]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52508,-0.07726,0.03201],"force_p95":0.35019,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36099,"mean_force":0.20055,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49648,-0.04428,0.03824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.50661,-0.10021,0.05808],"force_p95":0.30099,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34893,"mean_force":0.07959,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49619,-0.04438,0.03724]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50369,-0.05622,0.06086],"force_p95":0.13554,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16116,"mean_force":0.03385,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49786,-0.04435,0.03341]}],"total_contact_groups":11},"final_pose_error":0.01174,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50593,-0.07986,0.03397],"final_tcp_position":[0.49491,-0.04355,0.12209],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":33.35062,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.06161,0.0338],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.55118,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":810.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.50669,0.12206,0.04821],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":224.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.06137,0.03389],"object_pos_start":[0.50372,0.06161,0.0338],"object_to_goal_dist_end":0.14155,"object_to_goal_dist_start":0.1418,"object_z_max":0.03382,"peak_contact_force":7.13672,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":226.0,"raw_peak_contact_force":7.13672,"tcp_end":[0.50172,0.09122,0.03802],"tcp_start":[0.50669,0.12206,0.04821],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.50629,-0.07264,0.03612],"object_pos_start":[0.50371,0.06137,0.03389],"object_to_goal_dist_end":0.01043,"object_to_goal_dist_start":0.14155,"object_z_max":0.03843,"peak_contact_force":0.26165,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":622.0,"raw_peak_contact_force":33.35062,"subtask_id":"insertion_goal","tcp_end":[0.49814,-0.0438,0.03338],"tcp_start":[0.50172,0.09122,0.03802],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50593,-0.07986,0.03397],"object_pos_start":[0.50629,-0.07264,0.03612],"object_to_goal_dist_end":0.00845,"object_to_goal_dist_start":0.01043,"object_z_max":0.03649,"peak_contact_force":0.54486,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":565.0,"raw_peak_contact_force":1.31844,"tcp_end":[0.49491,-0.04355,0.12209],"tcp_start":[0.49814,-0.0438,0.03338],"tcp_to_object_dist_end":0.09594,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34804,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_y_offset":0.04935,"contact_side.contact_force":5.46038,"push_channel.force_limit_threshold":48.64388,"push_channel.insertion_depth":0.1995,"push_channel.push_speed":0.01112},"optimized_scores":{"best_composite_score":0.65812,"best_fitness_score":0.71812,"best_task_score":0.98343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":330.0,"contact_point_centroid":[0.49812,0.04253,0.03987],"force_p95":22.63669,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.47895,"mean_force":5.41006,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49151,0.05283,0.03533]},{"body_a":"peg","body_b":"channel_base_body","contact_count":192.0,"contact_point_centroid":[0.50591,0.01286,0.00989],"force_p95":19.04866,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.46849,"mean_force":7.25905,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49167,0.05427,0.03554]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":336.0,"contact_point_centroid":[0.52515,0.01932,0.03115],"force_p95":11.77347,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.77179,"mean_force":2.86924,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49137,0.04454,0.03516]},{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.50113,0.11397,0.00945],"force_p95":0.62269,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.24181,"mean_force":0.68721,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49495,0.15469,0.04306]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.49851,0.13229,0.05434],"force_p95":4.70387,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.94572,"mean_force":2.00028,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49469,0.14404,0.03979]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52507,-0.06328,0.04073],"force_p95":2.41537,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57025,"mean_force":0.45366,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4897,-0.03837,0.039]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.49751,-0.04873,0.05515],"force_p95":2.21907,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.35806,"mean_force":0.41866,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48919,-0.0383,0.04039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":752.0,"contact_point_centroid":[0.50093,0.116,0.0094],"force_p95":0.61777,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55355,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49784,0.18242,0.17151]},{"body_a":"peg","body_b":"channel_base_body","contact_count":537.0,"contact_point_centroid":[0.50619,-0.06525,0.00944],"force_p95":0.57757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.18221,"mean_force":0.5485,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48797,-0.03786,0.07935]}],"total_contact_groups":9},"final_pose_error":0.01159,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50628,-0.06407,0.03378],"final_tcp_position":[0.48804,-0.03776,0.12383],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":29.47895,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":768.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11605,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.53704,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":752.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49733,0.16609,0.04918],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":187.0,"n_steps_budget":600.0,"object_pos_end":[0.50168,0.11373,0.03564],"object_pos_start":[0.50096,0.11605,0.03387],"object_to_goal_dist_end":0.19378,"object_to_goal_dist_start":0.19615,"object_z_max":0.03581,"peak_contact_force":5.82916,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":195.0,"raw_peak_contact_force":5.24181,"tcp_end":[0.49475,0.14254,0.03945],"tcp_start":[0.49733,0.16609,0.04918],"tcp_to_object_dist_end":0.02988,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.50712,-0.06325,0.03714],"object_pos_start":[0.50168,0.11373,0.03564],"object_to_goal_dist_end":0.01843,"object_to_goal_dist_start":0.19378,"object_z_max":0.03748,"peak_contact_force":1.82781,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":858.0,"raw_peak_contact_force":29.47895,"subtask_id":"insertion_goal","tcp_end":[0.49121,-0.03799,0.03497],"tcp_start":[0.49475,0.14254,0.03945],"tcp_to_object_dist_end":0.02993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50628,-0.06407,0.03378],"object_pos_start":[0.50712,-0.06325,0.03714],"object_to_goal_dist_end":0.01822,"object_to_goal_dist_start":0.01843,"object_z_max":0.03724,"peak_contact_force":0.54715,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":573.0,"raw_peak_contact_force":2.57025,"tcp_end":[0.48804,-0.03776,0.12383],"tcp_start":[0.49121,-0.03799,0.03497],"tcp_to_object_dist_end":0.09557,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78049,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_y_offset":0.04147,"contact_side.contact_force":9.82241,"push_channel.force_limit_threshold":45.62518,"push_channel.insertion_depth":0.15892,"push_channel.push_speed":0.03765},"optimized_scores":{"best_composite_score":0.07162,"best_fitness_score":0.13162,"best_task_score":0.00104},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":68.0,"contact_point_centroid":[0.47496,0.10214,0.05973],"force_p95":472.674,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":490.41412,"mean_force":411.73503,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48025,0.1128,0.05883]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.10261,0.05996],"force_p95":68.47227,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.26152,"mean_force":61.3364,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48117,0.11277,0.05917]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.10257,0.05995],"force_p95":51.32477,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.50494,"mean_force":49.81474,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48111,0.11277,0.05916]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.10253,0.05995],"force_p95":47.85609,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.85609,"mean_force":47.85609,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.48105,0.11278,0.05916]},{"body_a":"peg","body_b":"channel_base_body","contact_count":824.0,"contact_point_centroid":[0.49538,0.06385,0.00938],"force_p95":0.56226,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55586,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48784,0.15154,0.16499]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4994,0.1987,0.29695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49487,0.06374,0.0094],"force_p95":0.55079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54519,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47824,0.11211,0.10305]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49103,0.08101,0.0094],"force_p95":0.54987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55067,"mean_force":0.54533,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48111,0.11277,0.05916]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50137,0.08071,0.0094],"force_p95":0.5394,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5394,"mean_force":0.5394,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.48105,0.11278,0.05916]}],"total_contact_groups":9},"final_pose_error":0.01154,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49525,0.06361,0.03403],"final_tcp_position":[0.47823,0.11212,0.14801],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":490.41412,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.49518,0.06412,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14433,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":426.23707,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":920.0,"raw_peak_contact_force":490.41412,"subtask_id":"pre_contact","tcp_end":[0.48105,0.11278,0.05916],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49511,0.06413,0.03399],"object_pos_start":[0.49518,0.06412,0.03399],"object_to_goal_dist_end":0.14434,"object_to_goal_dist_start":0.14433,"object_z_max":0.03399,"peak_contact_force":47.85609,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":47.85609,"tcp_end":[0.48108,0.11278,0.05916],"tcp_start":[0.48105,0.11278,0.05916],"tcp_to_object_dist_end":0.05653,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49504,0.06413,0.03399],"object_pos_start":[0.49511,0.06413,0.03399],"object_to_goal_dist_end":0.14434,"object_to_goal_dist_start":0.14434,"object_z_max":0.034,"peak_contact_force":51.50494,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":51.50494,"subtask_id":"insertion_goal","tcp_end":[0.48116,0.11277,0.05916],"tcp_start":[0.48113,0.11277,0.05916],"tcp_to_object_dist_end":0.0565,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49525,0.06361,0.03403],"object_pos_start":[0.49492,0.06406,0.034],"object_to_goal_dist_end":0.14382,"object_to_goal_dist_start":0.14427,"object_z_max":0.03403,"peak_contact_force":0.54052,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":546.0,"raw_peak_contact_force":69.26152,"tcp_end":[0.47823,0.11212,0.14801],"tcp_start":[0.48116,0.11277,0.05916],"tcp_to_object_dist_end":0.12504,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```