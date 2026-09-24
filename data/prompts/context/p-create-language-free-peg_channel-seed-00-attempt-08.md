## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2627 | 0.59 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1421 | 0.06 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6127 | 0.72 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5229 | 0.40 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6309 | 0.78 | ✅ accepted |

**Proposal policy**: task_score is 0.59 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.263) — your mutation base

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

- **Composite score**: 0.263
- **task_score** (E): 0.590
- **fitness_score**: 0.406  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2172 |
| descend_1 | 1.00 | 1.00 | 0.0538 |
| push_1 | 0.67 | 1.00 | 0.0956 |
| retract_1 | 1.00 | 1.00 | 0.0889 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.124, 0.098) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.548 | 2.179 |
| descend_1 | descend | 1.00 / force_exceeded | (0.495, 0.124, 0.098)→(0.493, 0.111, 0.046) | (0.500, 0.081, 0.034)→(0.500, 0.079, 0.035) | 0.161→0.159 | 1.00 / 2.000 | 22.281 | 22.799 |
| push_1 | push | 0.67 / step_budget | (0.493, 0.111, 0.046)→(0.491, 0.015, 0.043) | (0.500, 0.079, 0.035)→(0.500, -0.016, 0.037) | 0.159→0.065 | 1.00 / 1.667 | 17.121 | 43.079 |
| retract_1 | retract | 1.00 / step_budget | (0.491, 0.015, 0.043)→(0.487, 0.015, 0.132) | (0.500, -0.016, 0.037)→(0.498, -0.021, 0.034) | 0.065→0.063 | 1.00 / 1.000 | 0.537 | 25.316 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.897
- alignment_error: None
- force_efficiency: 0.331
- terminal_score: 0.876
- phase_score: 0.463
- phase_breakdown.insertion_goal_score: 0.531
- phase_breakdown.pre_contact_score: 0.302

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.628
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.892
- **Median Q (composite search score)**: 0.190
- **K-run variance**: 0.0508
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.271


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37017,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04706,"descend_1.contact_force":6.82837,"push_1.insertion_depth":0.15794,"push_1.push_force_limit":35.5162,"push_1.push_speed":0.03452},"optimized_scores":{"best_composite_score":0.56789,"best_fitness_score":0.62789,"best_task_score":0.87596},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":245.0,"contact_point_centroid":[0.5253,-0.01873,0.03545],"force_p95":31.19169,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.45969,"mean_force":6.72574,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.497,0.00935,0.03758]},{"body_a":"attachment","body_b":"peg","contact_count":273.0,"contact_point_centroid":[0.50177,0.00834,0.0445],"force_p95":30.72436,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.34129,"mean_force":8.57516,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49729,0.01962,0.03793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":145.0,"contact_point_centroid":[0.50526,-0.01376,0.00984],"force_p95":21.59021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.50891,"mean_force":7.73096,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49757,0.02781,0.03825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":283.0,"contact_point_centroid":[0.50396,0.06009,0.0094],"force_p95":0.55233,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.13194,"mean_force":0.64869,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50273,0.09844,0.06764]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50276,0.07897,0.05254],"force_p95":6.73278,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.83789,"mean_force":5.3531,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50081,0.09096,0.04437]},{"body_a":"peg","body_b":"channel_base_body","contact_count":682.0,"contact_point_centroid":[0.50365,0.06162,0.00935],"force_p95":0.58237,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55851,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50274,0.15185,0.19302]},{"body_a":"peg","body_b":"channel_base_body","contact_count":531.0,"contact_point_centroid":[0.50537,-0.08215,0.00939],"force_p95":0.59149,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5203,"mean_force":0.55526,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4938,-0.04842,0.08221]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49978,0.19902,0.29838]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.5252,-0.07719,0.01246],"force_p95":0.30457,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31282,"mean_force":0.28263,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49664,-0.04927,0.03764]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.5025,-0.06068,0.0566],"force_p95":0.12677,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14914,"mean_force":0.03729,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.497,-0.04896,0.03747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":128.0,"contact_point_centroid":[0.50543,-0.10004,0.05884],"force_p95":0.04102,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13591,"mean_force":0.00694,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49398,-0.04853,0.07174]}],"total_contact_groups":11},"final_pose_error":0.01173,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50548,-0.08196,0.03377],"final_tcp_position":[0.49391,-0.04833,0.1262],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":33.45969,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06157,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54536,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":701.0,"raw_peak_contact_force":2.17216,"subtask_id":"pre_contact","tcp_end":[0.507,0.10664,0.09465],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":283.0,"n_steps_budget":600.0,"object_pos_end":[0.50402,0.06073,0.03514],"object_pos_start":[0.50378,0.06157,0.03378],"object_to_goal_dist_end":0.14087,"object_to_goal_dist_start":0.14176,"object_z_max":0.03507,"peak_contact_force":7.13194,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":289.0,"raw_peak_contact_force":7.13194,"subtask_id":"pre_contact","tcp_end":[0.5007,0.09026,0.04214],"tcp_start":[0.507,0.10664,0.09465],"tcp_to_object_dist_end":0.03052,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50671,-0.07674,0.03675],"object_pos_start":[0.50402,0.06073,0.03514],"object_to_goal_dist_end":0.00814,"object_to_goal_dist_start":0.14087,"object_z_max":0.041,"peak_contact_force":0.54321,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":663.0,"raw_peak_contact_force":33.45969,"subtask_id":"insertion_goal","tcp_end":[0.4971,-0.04861,0.03749],"tcp_start":[0.5007,0.09026,0.04214],"tcp_to_object_dist_end":0.02974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50548,-0.08196,0.03377],"object_pos_start":[0.50671,-0.07674,0.03675],"object_to_goal_dist_end":0.00852,"object_to_goal_dist_start":0.00814,"object_z_max":0.03694,"peak_contact_force":0.52386,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":673.0,"raw_peak_contact_force":1.5203,"tcp_end":[0.49391,-0.04833,0.1262],"tcp_start":[0.4971,-0.04861,0.03749],"tcp_to_object_dist_end":0.09904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4142,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07016,"descend_1.contact_force":7.20308,"push_1.insertion_depth":0.16656,"push_1.push_force_limit":35.80833,"push_1.push_speed":0.03911},"optimized_scores":{"best_composite_score":0.18975,"best_fitness_score":0.49975,"best_task_score":0.89184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_right_wall","contact_count":71.0,"contact_point_centroid":[0.4745,0.02963,0.04364],"force_p95":17.2227,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.29412,"mean_force":2.2883,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49332,0.06055,0.03207]},{"body_a":"attachment","body_b":"peg","contact_count":216.0,"contact_point_centroid":[0.49733,0.06093,0.04678],"force_p95":8.57101,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.86958,"mean_force":2.11701,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49375,0.07246,0.03268]},{"body_a":"peg","body_b":"channel_base_body","contact_count":187.0,"contact_point_centroid":[0.50178,0.03101,0.00949],"force_p95":8.29353,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.4243,"mean_force":2.36226,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49372,0.06847,0.03263]},{"body_a":"peg","body_b":"channel_base_body","contact_count":413.0,"contact_point_centroid":[0.50173,0.11187,0.00949],"force_p95":3.05388,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.51381,"mean_force":0.74666,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49603,0.1498,0.0773]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.49912,0.13154,0.05139],"force_p95":5.44512,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.1457,"mean_force":2.95403,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49656,0.14334,0.04529]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.50093,0.11607,0.00938],"force_p95":0.62924,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55821,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4981,0.17855,0.207]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.49441,-0.04527,0.00938],"force_p95":0.69925,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53676,"mean_force":0.56109,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48995,-0.00602,0.07727]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.4746,-0.04691,0.05879],"force_p95":0.8848,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.224,"mean_force":0.2121,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49045,-0.0063,0.04249]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52527,0.08868,0.0185],"force_p95":0.76087,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80833,"mean_force":0.48207,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49393,0.11578,0.03287]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49577,-0.01776,0.03162],"force_p95":0.04122,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0458,"mean_force":0.01527,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49322,-0.00622,0.03206]}],"total_contact_groups":10},"final_pose_error":0.0116,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49366,-0.04509,0.03383],"final_tcp_position":[0.49006,-0.00592,0.12093],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":19.29412,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.50089,0.11605,0.03392],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55071,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":546.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.4978,0.1583,0.11924],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":422.0,"n_steps_budget":600.0,"object_pos_end":[0.50103,0.11204,0.03497],"object_pos_start":[0.50089,0.11605,0.03392],"object_to_goal_dist_end":0.19211,"object_to_goal_dist_start":0.19614,"object_z_max":0.03573,"peak_contact_force":4.95925,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":446.0,"raw_peak_contact_force":6.51381,"subtask_id":"pre_contact","tcp_end":[0.49677,0.14158,0.03658],"tcp_start":[0.4978,0.1583,0.11924],"tcp_to_object_dist_end":0.02989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.49811,-0.03643,0.03948],"object_pos_start":[0.50103,0.11204,0.03497],"object_to_goal_dist_end":0.04362,"object_to_goal_dist_start":0.19211,"object_z_max":0.04239,"peak_contact_force":0.24573,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":488.0,"raw_peak_contact_force":19.29412,"subtask_id":"insertion_goal","tcp_end":[0.49326,-0.00595,0.03209],"tcp_start":[0.49677,0.14158,0.03658],"tcp_to_object_dist_end":0.03173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.49366,-0.04509,0.03383],"object_pos_start":[0.49811,-0.03643,0.03948],"object_to_goal_dist_end":0.03601,"object_to_goal_dist_start":0.04362,"object_z_max":0.04008,"peak_contact_force":0.53972,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":558.0,"raw_peak_contact_force":1.53676,"tcp_end":[0.49006,-0.00592,0.12093],"tcp_start":[0.49326,-0.00595,0.03209],"tcp_to_object_dist_end":0.09558,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68235,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.03086,"descend_1.contact_force":3.64109,"push_1.insertion_depth":0.12768,"push_1.push_force_limit":33.95174,"push_1.push_speed":0.02292},"optimized_scores":{"best_composite_score":0.03046,"best_fitness_score":0.09046,"best_task_score":0.00111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.09075,0.05992],"force_p95":74.80532,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.48295,"mean_force":62.255,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48112,0.10091,0.059]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,0.0907,0.05993],"force_p95":72.16061,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.8897,"mean_force":61.68384,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48124,0.10081,0.059]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.09077,0.05997],"force_p95":54.75212,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.75212,"mean_force":54.75212,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48104,0.10098,0.05912]},{"body_a":"peg","body_b":"channel_base_body","contact_count":707.0,"contact_point_centroid":[0.49537,0.0638,0.00938],"force_p95":0.56532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55759,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48825,0.15264,0.18475]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49937,0.19858,0.29698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49488,0.06388,0.0094],"force_p95":0.55088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54519,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47829,0.10024,0.10288]},{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.49536,0.06411,0.0094],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55124,"mean_force":0.54534,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47914,0.10438,0.0678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49353,0.08131,0.0094],"force_p95":0.54567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54577,"mean_force":0.54503,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48112,0.10091,0.059]}],"total_contact_groups":8},"final_pose_error":0.01152,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49497,0.0636,0.03403],"final_tcp_position":[0.47825,0.10027,0.14783],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":76.48295,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.49531,0.06398,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14419,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54737,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":735.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_contact","tcp_end":[0.47873,0.10853,0.07931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":164.0,"n_steps_budget":600.0,"object_pos_end":[0.49514,0.06413,0.034],"object_pos_start":[0.49531,0.06398,0.03398],"object_to_goal_dist_end":0.14434,"object_to_goal_dist_start":0.14419,"object_z_max":0.034,"peak_contact_force":54.75212,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":165.0,"raw_peak_contact_force":54.75212,"subtask_id":"pre_contact","tcp_end":[0.48108,0.10095,0.05903],"tcp_start":[0.47873,0.10853,0.07931],"tcp_to_object_dist_end":0.04669,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49507,0.06414,0.034],"object_pos_start":[0.49514,0.06413,0.034],"object_to_goal_dist_end":0.14435,"object_to_goal_dist_start":0.14434,"object_z_max":0.034,"peak_contact_force":50.57538,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":76.48295,"subtask_id":"insertion_goal","tcp_end":[0.4812,0.10085,0.05896],"tcp_start":[0.48116,0.10088,0.05897],"tcp_to_object_dist_end":0.04651,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49497,0.0636,0.03403],"object_pos_start":[0.49494,0.06409,0.034],"object_to_goal_dist_end":0.14381,"object_to_goal_dist_start":0.1443,"object_z_max":0.03403,"peak_contact_force":0.54742,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":547.0,"raw_peak_contact_force":72.8897,"tcp_end":[0.47825,0.10027,0.14783],"tcp_start":[0.4812,0.10085,0.05896],"tcp_to_object_dist_end":0.12073,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```