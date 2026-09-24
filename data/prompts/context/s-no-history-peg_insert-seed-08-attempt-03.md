## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

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

## Current Skill (Q=0.028) — your mutation base

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

- **Composite score**: 0.028
- **task_score** (E): 0.841
- **fitness_score**: 0.422  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1103 |
| align_1 | 0.00 | 0.67 | 0.0824 |
| descend_contact_1 | 0.67 | 0.67 | 0.0133 |
| insert_1 | 0.00 | 0.67 | 0.0592 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.465, -0.001, 0.199) | (0.504, -0.000, 0.340)→(0.499, 0.000, 0.178) | 0.260→0.102 | 1.00 / 1.000 | 298.152 | 968.709 |
| align_1 | align | 0.00 / step_budget | (0.465, -0.001, 0.199)→(0.508, -0.001, 0.218) | (0.499, 0.000, 0.178)→(0.545, -0.002, 0.204) | 0.102→0.139 | 0.67 / 0.667 | 319.372 | 763.150 |
| descend_contact_1 | descend | 0.67 / force_exceeded | (0.508, -0.001, 0.218)→(0.507, -0.002, 0.231) | (0.545, -0.002, 0.204)→(0.544, -0.003, 0.219) | 0.139→0.153 | 0.67 / 0.667 | 35.347 | 35.347 |
| insert_1 | insert | 0.00 / guard_failure | (0.507, -0.002, 0.231)→(0.506, -0.000, 0.172) | (0.544, -0.003, 0.219)→(0.543, -0.001, 0.160) | 0.153→0.098 | 0.67 / 0.667 | 85.605 | 86.462 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.809
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.809
- phase_score: 0.233
- phase_breakdown.approach_target_score: 0.623
- phase_breakdown.insertion_target_score: 0.066

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.463
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.858
- **Median Q (composite search score)**: 0.091
- **K-run variance**: 0.0182
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: approach_1.approach_speed
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.75325,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_lateral_x":0.00463,"align_1.align_lateral_y":0.00597,"align_1.align_speed":0.03956,"approach_1.approach_speed":0.04973,"approach_1.arc_height":0.09323,"descend_contact_1.contact_force_threshold":8.11347,"descend_contact_1.descend_offset_dist":0.00805,"descend_contact_1.descend_speed":0.01439,"insert_1.insert_depth":0.04822,"insert_1.insert_speed":0.01021},"optimized_scores":{"best_composite_score":0.15307,"best_fitness_score":0.46307,"best_task_score":0.80858},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":107.0,"contact_point_centroid":[0.54155,0.01347,0.07909],"force_p95":552.73159,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1082.95047,"mean_force":310.38811,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43279,0.01504,0.13946]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.44203,0.01103,0.07919],"force_p95":537.45773,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":895.76288,"mean_force":99.52921,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43796,0.01099,0.09282]},{"body_a":"peg_socket","body_b":"link7","contact_count":641.0,"contact_point_centroid":[0.54608,0.04224,0.07992],"force_p95":391.4969,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":647.51609,"mean_force":288.73372,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48079,0.03862,0.183]},{"body_a":"peg_socket","body_b":"link6","contact_count":306.0,"contact_point_centroid":[0.54612,0.03348,0.07992],"force_p95":257.53156,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":394.67605,"mean_force":180.42479,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46982,0.0344,0.20931]},{"body_a":"peg_socket","body_b":"link6","contact_count":746.0,"contact_point_centroid":[0.54612,0.02998,0.07992],"force_p95":317.68197,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.98763,"mean_force":293.48828,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44816,0.02864,0.19721]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54614,0.04612,0.08],"force_p95":69.77903,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.90314,"mean_force":68.63247,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48945,0.04727,0.16092]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54613,0.04604,0.08],"force_p95":46.9009,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.9009,"mean_force":46.9009,"phase_index":2.0,"phase_name":"descend_contact_1","phase_type":"descend","tcp_position_centroid":[0.48939,0.04709,0.16096]}],"total_contact_groups":7},"final_pose_error":0.12941,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48949,0.0474,0.16088],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1082.95047,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.49452,0.03383,0.18815],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11345,"object_to_goal_dist_start":0.26034,"object_z_max":0.34406,"peak_contact_force":319.49791,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":862.0,"raw_peak_contact_force":1082.95047,"subtask_id":"approach_target","tcp_end":[0.46526,0.03325,0.21542],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52419,0.04614,0.14125],"object_pos_start":[0.49452,0.03383,0.18815],"object_to_goal_dist_end":0.08041,"object_to_goal_dist_start":0.11345,"object_z_max":0.18815,"peak_contact_force":232.86513,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":947.0,"raw_peak_contact_force":647.51609,"tcp_end":[0.48939,0.04709,0.16096],"tcp_start":[0.46526,0.03325,0.21542],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52422,0.04622,0.14123],"object_pos_start":[0.52419,0.04614,0.14125],"object_to_goal_dist_end":0.08045,"object_to_goal_dist_start":0.08041,"object_z_max":0.14125,"peak_contact_force":46.9009,"phase_name":"descend_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":46.9009,"tcp_end":[0.48943,0.04719,0.16095],"tcp_start":[0.48939,0.04709,0.16096],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52424,0.0463,0.1412],"object_pos_start":[0.52422,0.04622,0.14123],"object_to_goal_dist_end":0.08048,"object_to_goal_dist_start":0.08045,"object_z_max":0.14123,"peak_contact_force":67.3322,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":69.90314,"subtask_id":"insertion_target","tcp_end":[0.48949,0.0474,0.16088],"tcp_start":[0.48948,0.04734,0.1609],"tcp_to_object_dist_end":0.03995,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":194.0,"average_failure_rate":0.59146,"average_mean_iterations":122.11585,"average_solve_count":328.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_lateral_x":-0.00424,"align_1.align_lateral_y":0.00958,"align_1.align_speed":0.04082,"approach_1.approach_speed":0.05,"approach_1.arc_height":0.16634,"descend_contact_1.contact_force_threshold":8.3677,"descend_contact_1.descend_offset_dist":0.00287,"descend_contact_1.descend_speed":0.01144,"insert_1.insert_depth":0.03575,"insert_1.insert_speed":0.01247},"optimized_scores":{"best_composite_score":-0.15908,"best_fitness_score":0.40092,"best_task_score":0.85598},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":18.0,"contact_point_centroid":[0.65809,0.09506,-0.00076],"force_p95":662.48244,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":891.25905,"mean_force":477.51964,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49913,-0.00642,0.17449]},{"body_a":"peg_socket","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.54405,0.01357,0.07819],"force_p95":755.80777,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":859.02534,"mean_force":198.41467,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4488,0.00184,0.10415]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.46973,0.00244,0.0797],"force_p95":806.21903,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":809.3274,"mean_force":399.48309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45781,0.00242,0.09111]},{"body_a":"peg_socket","body_b":"link7","contact_count":100.0,"contact_point_centroid":[0.58957,-0.00758,0.07992],"force_p95":340.73364,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":475.10742,"mean_force":271.08322,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49487,-0.00622,0.17785]},{"body_a":"peg_socket","body_b":"link5","contact_count":6.0,"contact_point_centroid":[0.58947,0.04246,0.07977],"force_p95":381.65958,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.74318,"mean_force":276.87306,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51524,-0.01112,0.21738]},{"body_a":"peg_socket","body_b":"link6","contact_count":573.0,"contact_point_centroid":[0.58958,-0.00838,0.07993],"force_p95":212.84371,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":331.61115,"mean_force":163.9551,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47864,-0.00644,0.19158]},{"body_a":"peg_socket","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.56369,0.00229,0.07876],"force_p95":223.39855,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":302.02707,"mean_force":50.36925,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44957,0.0018,0.10899]},{"body_a":"peg_socket","body_b":"link6","contact_count":789.0,"contact_point_centroid":[0.58952,-0.00135,0.07986],"force_p95":276.73052,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.25483,"mean_force":238.45049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45495,0.00063,0.1557]},{"body_a":"peg_socket","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.54456,-0.04709,0.07976],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44726,0.002,0.09565]}],"total_contact_groups":9},"final_pose_error":0.13664,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52561,-0.02559,0.18057],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":891.25905,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.49915,-0.00629,0.17328],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09349,"object_to_goal_dist_start":0.26034,"object_z_max":0.34475,"peak_contact_force":286.84059,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":875.0,"raw_peak_contact_force":859.02534,"subtask_id":"approach_target","tcp_end":[0.4633,-0.00632,0.19102],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.56969,-0.02969,0.31441],"object_pos_start":[0.49915,-0.00629,0.17328],"object_to_goal_dist_end":0.24634,"object_to_goal_dist_start":0.09349,"object_z_max":0.31119,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":697.0,"raw_peak_contact_force":891.25905,"tcp_end":[0.5299,-0.02841,0.31831],"tcp_start":[0.4633,-0.00632,0.19102],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.56887,-0.03214,0.35763],"object_pos_start":[0.56969,-0.02969,0.31441],"object_to_goal_dist_end":0.28785,"object_to_goal_dist_start":0.24634,"object_z_max":0.35703,"peak_contact_force":0.0,"phase_name":"descend_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5289,-0.03072,0.35774],"tcp_start":[0.5299,-0.02841,0.31831],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.56557,-0.02721,0.17965],"object_pos_start":[0.56887,-0.03214,0.35763],"object_to_goal_dist_end":0.12235,"object_to_goal_dist_start":0.28785,"object_z_max":0.35919,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_target","tcp_end":[0.52561,-0.02559,0.18057],"tcp_start":[0.5289,-0.03072,0.35774],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":17.0,"average_failure_rate":0.20482,"average_mean_iterations":46.53012,"average_solve_count":83.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_lateral_x":-0.0058,"align_1.align_lateral_y":0.00564,"align_1.align_speed":0.05967,"approach_1.approach_speed":0.04123,"approach_1.arc_height":0.13305,"descend_contact_1.contact_force_threshold":8.23409,"descend_contact_1.descend_offset_dist":0.00782,"descend_contact_1.descend_speed":0.01554,"insert_1.insert_depth":0.04748,"insert_1.insert_speed":0.00606},"optimized_scores":{"best_composite_score":0.09129,"best_fitness_score":0.40129,"best_task_score":0.85849},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.56681,-0.00809,0.07798],"force_p95":306.67024,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":964.15157,"mean_force":96.96725,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45125,-0.00756,0.1048]},{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.54629,0.00747,0.07761],"force_p95":652.78636,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":778.59597,"mean_force":158.20769,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45095,-0.00748,0.10067]},{"body_a":"world","body_b":"link5","contact_count":9.0,"contact_point_centroid":[0.65632,0.08774,-0.00072],"force_p95":749.65302,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":750.67556,"mean_force":672.57022,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50246,-0.02209,0.17341]},{"body_a":"peg_socket","body_b":"link6","contact_count":413.0,"contact_point_centroid":[0.59644,-0.01999,0.07993],"force_p95":231.69561,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.11231,"mean_force":173.07321,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48179,-0.02712,0.18935]},{"body_a":"peg_socket","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.59639,-0.01913,0.07984],"force_p95":325.62861,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":354.52421,"mean_force":251.37936,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49884,-0.02038,0.17767]},{"body_a":"peg_socket","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.59618,-0.01521,0.07983],"force_p95":270.65908,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.81274,"mean_force":237.57227,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45669,-0.01542,0.16099]},{"body_a":"world","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.65683,0.08562,-0.00087],"force_p95":181.63439,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":189.48425,"mean_force":122.00162,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50378,-0.02213,0.17478]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.65659,0.08579,-0.00103],"force_p95":59.14135,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.14135,"mean_force":59.14135,"phase_index":2.0,"phase_name":"descend_contact_1","phase_type":"descend","tcp_position_centroid":[0.50345,-0.02215,0.17432]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47652,-0.00713,0.07987],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45441,-0.00701,0.08894]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.54673,-0.05362,0.07865],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4503,-0.00737,0.09567]}],"total_contact_groups":10},"final_pose_error":0.14623,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.50397,-0.02215,0.17508],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":964.15157,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50314,-0.02722,0.17384],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09775,"object_to_goal_dist_start":0.26034,"object_z_max":0.34498,"peak_contact_force":288.11865,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":979.0,"raw_peak_contact_force":964.15157,"subtask_id":"approach_target","tcp_end":[0.46726,-0.02967,0.19135],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.5399,-0.02212,0.15784],"object_pos_start":[0.50314,-0.02722,0.17384],"object_to_goal_dist_end":0.09022,"object_to_goal_dist_start":0.09775,"object_z_max":0.17437,"peak_contact_force":725.2515,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":512.0,"raw_peak_contact_force":750.67556,"tcp_end":[0.50345,-0.02215,0.17432],"tcp_start":[0.46726,-0.02967,0.19135],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54011,-0.02204,0.15814],"object_pos_start":[0.5399,-0.02212,0.15784],"object_to_goal_dist_end":0.09056,"object_to_goal_dist_start":0.09022,"object_z_max":0.15784,"peak_contact_force":59.14135,"phase_name":"descend_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":59.14135,"tcp_end":[0.50364,-0.02212,0.17457],"tcp_start":[0.50345,-0.02215,0.17432],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54028,-0.022,0.1584],"object_pos_start":[0.54011,-0.02204,0.15814],"object_to_goal_dist_end":0.09085,"object_to_goal_dist_start":0.09056,"object_z_max":0.1586,"peak_contact_force":189.48425,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":189.48425,"subtask_id":"insertion_target","tcp_end":[0.50397,-0.02215,0.17508],"tcp_start":[0.50391,-0.02214,0.17497],"tcp_to_object_dist_end":0.03996,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```