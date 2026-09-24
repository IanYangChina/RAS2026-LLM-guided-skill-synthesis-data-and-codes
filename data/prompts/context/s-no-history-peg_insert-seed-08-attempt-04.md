## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.48615778212844424, 0.03898214746703404, 0.08]
- Frozen socket pose: [0.48615778212844424, 0.03898214746703404, 0.025] (static fixture for this episode)
- Goal object position: (0.48615778212844424, 0.03898214746703404, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.4862, 0.039, 0.08]
  frozen_socket_position: [0.4862, 0.039, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.48615778212844424, 0.03898214746703404, 0.08]}
  frozen_fixtures: {'peg_socket': [0.48615778212844424, 0.03898214746703404, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.851, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844424, 0.03898214746703404, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.48615778212844424, 0.03898214746703404, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.161) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_target
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: insertion_target
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: ''
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_target
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: ''
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    align_lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    align_lateral_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insertion_target
- id: descend_contact_1
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    offset_along_axis:
      distance: 0.01
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 25.0
      default: 12.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_offset_dist:
      type: scalar
      range:
      - 0.002
      - 0.025
      default: 0.01
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    offset_along_axis:
      distance: 0.045
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.008
    orientation:
      mode: keep_current
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.02
      - 0.055
      default: 0.045
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.003
      - 0.03
      default: 0.008
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insertion_target

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, entity=, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_lateral_x: status=consumed; consumers=target.offset.x (add)
    - align_lateral_y: status=consumed; consumers=target.offset.y (add)
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_contact_1** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.01, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_offset_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.045, mode=add_to_offset, sign=positive}, tolerance=0.008
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.161
- **task_score** (E): 0.850
- **fitness_score**: 0.421  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1125 |
| align_1 | 0.00 | 0.33 | 0.0431 |
| descend_contact_1 | 1.00 | 1.00 | 0.0009 |
| insert_1 | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.466, -0.001, 0.195) | (0.504, -0.000, 0.340)→(0.500, -0.001, 0.175) | 0.260→0.096 | 1.00 / 1.000 | 282.596 | 1749.082 |
| align_1 | align | 0.00 / step_budget | (0.466, -0.001, 0.195)→(0.495, -0.006, 0.168) | (0.500, -0.001, 0.175)→(0.531, -0.006, 0.151) | 0.096→0.082 | 0.33 / 0.333 | 85.005 | 431.123 |
| descend_contact_1 | descend | 1.00 / force_exceeded | (0.495, -0.006, 0.168)→(0.496, -0.007, 0.168) | (0.531, -0.006, 0.151)→(0.532, -0.007, 0.152) | 0.082→0.083 | 1.00 / 1.000 | 220.624 | 220.624 |
| insert_1 | insert | 0.00 / guard_failure | (0.496, -0.007, 0.168)→(0.496, -0.007, 0.168) | (0.532, -0.007, 0.152)→(0.532, -0.007, 0.151) | 0.083→0.083 | 1.00 / 1.000 | 157.701 | 196.207 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.831
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.831
- phase_score: 0.211
- phase_breakdown.approach_target_score: 0.553
- phase_breakdown.insertion_target_score: 0.065

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.459
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.862
- **Median Q (composite search score)**: 0.144
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.322


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6af64227b04102c511381eb024ec48290b429fbc7fcb6f0c4b42c66d0a974e9f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5cd76595591baa0f9f71873dced18f865534f529ba8f9daf4a3973579a78fb36`; realized-scene SHA-256: `586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.74684,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_lateral_x":0.00756,"align_1.align_lateral_y":0.00092,"align_1.align_speed":0.03359,"approach_1.approach_speed":0.04821,"descend_contact_1.contact_force_threshold":14.02473,"descend_contact_1.descend_offset_dist":0.02038,"descend_contact_1.descend_speed":0.01432,"insert_1.insert_depth":0.04705,"insert_1.insert_speed":0.01775},"optimized_scores":{"best_composite_score":0.19909,"best_fitness_score":0.45909,"best_task_score":0.83067},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.44842,0.00536,0.07851],"force_p95":1509.28844,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3018.57689,"mean_force":274.41608,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44429,0.00468,0.09127]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.45655,0.00467,0.07921],"force_p95":1867.19168,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2477.52637,"mean_force":381.024,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44589,0.00468,0.09087]},{"body_a":"peg_socket","body_b":"link7","contact_count":273.0,"contact_point_centroid":[0.54527,0.01217,0.07956],"force_p95":395.95507,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":942.02388,"mean_force":291.85052,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44269,0.00835,0.16038]},{"body_a":"peg_socket","body_b":"link7","contact_count":705.0,"contact_point_centroid":[0.54609,0.02944,0.07992],"force_p95":313.65126,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":506.09445,"mean_force":270.94001,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48057,0.02774,0.1851]},{"body_a":"peg_socket","body_b":"link6","contact_count":607.0,"contact_point_centroid":[0.54611,0.01786,0.07992],"force_p95":328.13613,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.83869,"mean_force":305.99906,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4561,0.01792,0.19921]},{"body_a":"peg_socket","body_b":"link6","contact_count":246.0,"contact_point_centroid":[0.54611,0.03391,0.07994],"force_p95":197.7286,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.95665,"mean_force":142.87921,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47033,0.02411,0.20649]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54601,0.03964,0.07998],"force_p95":232.73421,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.73421,"mean_force":232.73421,"phase_index":2.0,"phase_name":"descend_contact_1","phase_type":"descend","tcp_position_centroid":[0.48881,0.02711,0.16108]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54604,0.0394,0.07998],"force_p95":179.30781,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":186.52693,"mean_force":137.19995,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48889,0.02682,0.16103]}],"total_contact_groups":8},"final_pose_error":0.10385,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48896,0.02647,0.16101],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":3018.57689,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.02377,0.18332],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10609,"object_to_goal_dist_start":0.26034,"object_z_max":0.34434,"peak_contact_force":329.15901,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":900.0,"raw_peak_contact_force":3018.57689,"subtask_id":"approach_target","tcp_end":[0.46625,0.02293,0.21],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52366,0.03009,0.14166],"object_pos_start":[0.49604,0.02377,0.18332],"object_to_goal_dist_end":0.07258,"object_to_goal_dist_start":0.10609,"object_z_max":0.18332,"peak_contact_force":255.01644,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":951.0,"raw_peak_contact_force":506.09445,"tcp_end":[0.48881,0.02711,0.16108],"tcp_start":[0.46625,0.02293,0.21],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52369,0.03001,0.14163],"object_pos_start":[0.52366,0.03009,0.14166],"object_to_goal_dist_end":0.07253,"object_to_goal_dist_start":0.07258,"object_z_max":0.14166,"peak_contact_force":232.73421,"phase_name":"descend_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":232.73421,"tcp_end":[0.48884,0.02702,0.16105],"tcp_start":[0.48881,0.02711,0.16108],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52373,0.02982,0.14162],"object_pos_start":[0.52369,0.03001,0.14163],"object_to_goal_dist_end":0.07245,"object_to_goal_dist_start":0.07253,"object_z_max":0.14163,"peak_contact_force":114.33568,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":186.52693,"subtask_id":"insertion_target","tcp_end":[0.48896,0.02647,0.16101],"tcp_start":[0.48893,0.02663,0.16102],"tcp_to_object_dist_end":0.03995,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`; realized-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":27.0,"average_failure_rate":0.36,"average_mean_iterations":76.69333,"average_solve_count":75.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_lateral_x":0.00732,"align_1.align_lateral_y":0.00518,"align_1.align_speed":0.04456,"approach_1.approach_speed":0.09081,"descend_contact_1.contact_force_threshold":11.10446,"descend_contact_1.descend_offset_dist":0.02099,"descend_contact_1.descend_speed":0.02368,"insert_1.insert_depth":0.03935,"insert_1.insert_speed":0.0137},"optimized_scores":{"best_composite_score":0.14373,"best_fitness_score":0.40373,"best_task_score":0.86184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.47035,-0.00339,0.07942],"force_p95":1045.88293,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1073.62441,"mean_force":391.30361,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46094,-0.0034,0.09147]},{"body_a":"peg_socket","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.56712,-0.0039,0.07927],"force_p95":722.54719,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":862.87866,"mean_force":222.13739,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45065,-0.00414,0.11284]},{"body_a":"peg_socket","body_b":"link6","contact_count":389.0,"contact_point_centroid":[0.58952,-0.00874,0.07985],"force_p95":273.56591,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":473.19513,"mean_force":243.65165,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45508,-0.00632,0.15986]},{"body_a":"peg_socket","body_b":"link7","contact_count":114.0,"contact_point_centroid":[0.58955,-0.00864,0.07986],"force_p95":292.91914,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":409.85578,"mean_force":220.9885,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49252,-0.01066,0.1747]},{"body_a":"peg_socket","body_b":"link6","contact_count":428.0,"contact_point_centroid":[0.58959,-0.01164,0.07993],"force_p95":163.97991,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.27176,"mean_force":143.83998,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47582,-0.00992,0.18211]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.58957,-0.02332,0.07989],"force_p95":271.07148,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":273.6048,"mean_force":256.12742,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49584,-0.01898,0.16656]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5896,-0.02339,0.07996],"force_p95":221.88183,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.88183,"mean_force":221.88183,"phase_index":2.0,"phase_name":"descend_contact_1","phase_type":"descend","tcp_position_centroid":[0.49583,-0.01857,0.16675]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.55022,0.01318,0.07936],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45333,-0.00374,0.09736]}],"total_contact_groups":8},"final_pose_error":0.10641,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.49589,-0.01948,0.16654],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1073.62441,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49893,-0.00957,0.16634],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08688,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":256.74969,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":452.0,"raw_peak_contact_force":1073.62441,"subtask_id":"approach_target","tcp_end":[0.46215,-0.00971,0.18209],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.53267,-0.02074,0.15152],"object_pos_start":[0.49893,-0.00957,0.16634],"object_to_goal_dist_end":0.08132,"object_to_goal_dist_start":0.08688,"object_z_max":0.16656,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":542.0,"raw_peak_contact_force":409.85578,"tcp_end":[0.49583,-0.01843,0.16693],"tcp_start":[0.46215,-0.00971,0.18209],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.53267,-0.02104,0.15124],"object_pos_start":[0.53267,-0.02074,0.15152],"object_to_goal_dist_end":0.08115,"object_to_goal_dist_start":0.08132,"object_z_max":0.15152,"peak_contact_force":221.88183,"phase_name":"descend_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":221.88183,"tcp_end":[0.49582,-0.01874,0.16663],"tcp_start":[0.49583,-0.01843,0.16693],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53268,-0.02126,0.15115],"object_pos_start":[0.53267,-0.02104,0.15124],"object_to_goal_dist_end":0.08114,"object_to_goal_dist_start":0.08115,"object_z_max":0.15124,"peak_contact_force":246.50591,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":273.6048,"subtask_id":"insertion_target","tcp_end":[0.49589,-0.01948,0.16654],"tcp_start":[0.49585,-0.01923,0.16651],"tcp_to_object_dist_end":0.03992,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`; realized-scene SHA-256: `77fea26f11e91c54ae4a9c1f03cd5e6af1b4f6cac3191aa4cbd28ae81b548c93`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.16667,"average_mean_iterations":39.06061,"average_solve_count":66.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_lateral_x":-0.01995,"align_1.align_lateral_y":-0.00687,"align_1.align_speed":0.0771,"approach_1.approach_speed":0.06241,"descend_contact_1.contact_force_threshold":16.81489,"descend_contact_1.descend_offset_dist":0.02967,"descend_contact_1.descend_speed":0.02099,"insert_1.insert_depth":0.03849,"insert_1.insert_speed":0.01483},"optimized_scores":{"best_composite_score":0.14109,"best_fitness_score":0.40109,"best_task_score":0.85727},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.54437,0.00758,0.07732],"force_p95":898.29386,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1155.04478,"mean_force":215.9794,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44885,-0.00453,0.10102]},{"body_a":"peg_socket","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.56681,-0.00441,0.07815],"force_p95":358.21826,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":406.25506,"mean_force":79.60211,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4488,-0.00461,0.10412]},{"body_a":"peg_socket","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.59636,-0.01605,0.07988],"force_p95":364.34415,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":377.41904,"mean_force":290.95762,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49674,-0.01634,0.17891]},{"body_a":"peg_socket","body_b":"link6","contact_count":338.0,"contact_point_centroid":[0.59644,-0.01684,0.07992],"force_p95":266.25094,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.17912,"mean_force":194.82879,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48243,-0.01817,0.18853]},{"body_a":"peg_socket","body_b":"link6","contact_count":644.0,"contact_point_centroid":[0.59599,-0.01131,0.07982],"force_p95":276.37553,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.14371,"mean_force":237.54721,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4558,-0.00892,0.15768]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.66227,0.06649,-0.00018],"force_p95":207.25507,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.25507,"mean_force":207.25507,"phase_index":2.0,"phase_name":"descend_contact_1","phase_type":"descend","tcp_position_centroid":[0.5018,-0.02817,0.17719]},{"body_a":"world","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.66211,0.06562,-0.00042],"force_p95":126.86597,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.48861,"mean_force":106.51145,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50186,-0.02826,0.17732]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.47656,-0.00402,0.07974],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45183,-0.00392,0.08782]},{"body_a":"peg_socket","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.54473,-0.05361,0.07871],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44798,-0.00433,0.09425]}],"total_contact_groups":9},"final_pose_error":0.1162,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.50185,-0.02843,0.17731],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1155.04478,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":754.0,"n_steps_budget":870.0,"object_pos_end":[0.50441,-0.01612,0.17462],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09608,"object_to_goal_dist_start":0.26034,"object_z_max":0.34478,"peak_contact_force":261.87985,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":733.0,"raw_peak_contact_force":1155.04478,"subtask_id":"approach_target","tcp_end":[0.46862,-0.01677,0.19247],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":452.0,"n_steps_budget":840.0,"object_pos_end":[0.53761,-0.02836,0.1604],"object_pos_start":[0.50441,-0.01612,0.17462],"object_to_goal_dist_end":0.09318,"object_to_goal_dist_start":0.09608,"object_z_max":0.17471,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":378.0,"raw_peak_contact_force":377.41904,"tcp_end":[0.50094,-0.02651,0.17626],"tcp_start":[0.46862,-0.01677,0.19247],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.53863,-0.03015,0.16166],"object_pos_start":[0.53761,-0.02836,0.1604],"object_to_goal_dist_end":0.09524,"object_to_goal_dist_start":0.09318,"object_z_max":0.16155,"peak_contact_force":207.25507,"phase_name":"descend_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":207.25507,"tcp_end":[0.50186,-0.0282,0.17729],"tcp_start":[0.50094,-0.02651,0.17626],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53864,-0.03021,0.1617],"object_pos_start":[0.53863,-0.03015,0.16166],"object_to_goal_dist_end":0.09529,"object_to_goal_dist_start":0.09524,"object_z_max":0.1617,"peak_contact_force":112.26224,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":128.48861,"subtask_id":"insertion_target","tcp_end":[0.50185,-0.02843,0.17731],"tcp_start":[0.50186,-0.02833,0.17732],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```