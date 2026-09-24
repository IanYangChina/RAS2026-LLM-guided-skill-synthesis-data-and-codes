## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.2415 | 0.29 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.4488 | 0.40 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2977 | 0.48 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.5850 | 0.48 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3291 | 0.51 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: door_push
- Frozen realised-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`
- Frozen initial hinge angle: 0.524 rad
- target_hinge_angle: 0.129 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: 0.1292
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.129
  realized_scene_sha256: 8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

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

## Current Skill (Q=0.242) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_handle
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: open_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_handle
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: approach_handle
- id: contact_handle
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  guards:
  - id: contact_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: approach_handle
- id: push_door_open
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.0
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.y
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat
- **contact_handle** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=contact_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **push_door_open** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset.y (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: 0.242
- **task_score** (E): 0.288
- **fitness_score**: 0.288  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 0.67 | 0.67 | 0.2515 |
| descend_to_door | 1.00 | 1.00 | 0.0058 |
| push_door_open | 1.00 | 0.00 | 0.1001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 0.67 / step_budget | (0.100, 0.399, 0.350)→(0.105, 0.195, 0.485) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 3.333 | 11.615 | 34.629 |
| descend_to_door | contact | 1.00 / force_exceeded | (0.107, 0.142, 0.478)→(0.107, 0.139, 0.474) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 18.300 | 23.427 |
| push_door_open | push | 1.00 / time_limit | (0.107, 0.139, 0.474)→(0.168, 0.206, 0.432) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 14.427 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.358
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.358
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.358
- **Median Q (composite search score)**: 0.478
- **K-run variance**: 0.1117
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_door_open.max_push_time
- **Final σ (mean)**: 0.328


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d324a70682be50916187e25da5a0a59a7678607fbe49b53fdc39aa246f41ddf9`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d82b7d31aa43f8d3a4479d5f34069ef44e70dc4ca62021414a1e013fa43805ad`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.12924},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55446,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_height":0.10842,"approach_handle.arc_height":0.03589,"descend_to_door.contact_force_threshold":14.99905,"push_door_open.max_push_time":2.23756,"push_door_open.push_offset_x":0.24903,"push_door_open.push_offset_y":0.1862,"push_door_open.push_speed":0.03344},"optimized_scores":{"best_composite_score":0.47758,"best_fitness_score":0.35758,"best_task_score":0.35758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":109.0,"contact_point_centroid":[0.17022,0.12227,0.48058],"force_p95":27.67374,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.84173,"mean_force":18.57454,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10495,0.17967,0.45668]},{"body_a":"door_panel","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.17117,0.08898,0.47932],"force_p95":19.19022,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.067,"mean_force":14.15172,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.10589,0.14637,0.45542]},{"body_a":"door_panel","body_b":"link6","contact_count":21.0,"contact_point_centroid":[0.10377,0.14595,0.55844],"force_p95":22.94033,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.0739,"mean_force":14.7532,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10422,0.21391,0.45286]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.1715,0.08725,0.47705],"force_p95":13.42263,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.12908,"mean_force":7.06454,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10621,0.14467,0.45312]},{"body_a":"world","body_b":"door_panel","contact_count":716.0,"contact_point_centroid":[0.30397,0.16028,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10259,0.28766,0.41807]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.31368,0.12662,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.10585,0.14666,0.45579]},{"body_a":"world","body_b":"door_panel","contact_count":964.0,"contact_point_centroid":[0.3136,0.12682,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.14031,0.17544,0.43638]}],"total_contact_groups":7},"final_pose_error":0.2478,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.17397,0.20616,0.42172],"hinge_angle":0.31661,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":29.84173,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":656.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.7162,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":846.0,"raw_peak_contact_force":29.84173,"subtask_id":"approach_handle","tcp_end":[0.10566,0.14848,0.45781],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":38.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.81229,"phase_name":"descend_to_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":39.0,"raw_peak_contact_force":29.067,"subtask_id":"approach_handle","tcp_end":[0.10621,0.14467,0.45315],"tcp_start":[0.10566,0.14848,0.45781],"tcp_to_object_dist_end":0.48739,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":966.0,"raw_peak_contact_force":14.12908,"subtask_id":"open_door","tcp_end":[0.17397,0.20616,0.42172],"tcp_start":[0.10621,0.14467,0.45315],"tcp_to_object_dist_end":0.50061,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1fec9e8e5c1fdb9e52be404e6e4e2b90974542a257bfa7ba08d11c8aa9beb00c`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.15917},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53982,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_height":0.14995,"approach_handle.arc_height":0.0462,"descend_to_door.contact_force_threshold":14.89686,"push_door_open.max_push_time":1.62729,"push_door_open.push_offset_x":0.16768,"push_door_open.push_offset_y":0.17039,"push_door_open.push_speed":0.04919},"optimized_scores":{"best_composite_score":0.4782,"best_fitness_score":0.3582,"best_task_score":0.3582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":132.0,"contact_point_centroid":[0.17208,0.11499,0.5196],"force_p95":28.76206,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.95203,"mean_force":18.68755,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10672,0.17227,0.4958]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.17338,0.07698,0.51891],"force_p95":16.39727,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.78738,"mean_force":14.36328,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.10801,0.13436,0.49513]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17349,0.0763,0.51769],"force_p95":14.17656,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.72567,"mean_force":9.23452,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10811,0.13368,0.49391]},{"body_a":"door_panel","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.105,0.1373,0.59628],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10586,0.20412,0.49105]},{"body_a":"world","body_b":"door_panel","contact_count":772.0,"contact_point_centroid":[0.30482,0.15602,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10312,0.29694,0.43701]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.31632,0.12023,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.10794,0.13467,0.49574]},{"body_a":"world","body_b":"door_panel","contact_count":896.0,"contact_point_centroid":[0.31596,0.12107,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.13508,0.1702,0.46725]}],"total_contact_groups":7},"final_pose_error":0.20175,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.16155,0.20615,0.44292],"hinge_angle":0.34687,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":29.95203,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":910.0,"raw_peak_contact_force":29.95203,"subtask_id":"approach_handle","tcp_end":[0.1077,0.13652,0.49862],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.52807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":35.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.78738,"phase_name":"descend_to_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":29.0,"raw_peak_contact_force":17.78738,"subtask_id":"approach_handle","tcp_end":[0.10814,0.13371,0.49394],"tcp_start":[0.1077,0.13652,0.49862],"tcp_to_object_dist_end":0.52302,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":898.0,"raw_peak_contact_force":14.72567,"subtask_id":"open_door","tcp_end":[0.16155,0.20615,0.44292],"tcp_start":[0.10814,0.13371,0.49394],"tcp_to_object_dist_end":0.51456,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3715cb43c8f8f3084ca346701c1c33fec8eb1e50d1b8785cdad3bdd48e46f29f`; realized-scene SHA-256: `a85e6d1e7f42d6b7853e30231dc3bdf8d0b19eb5c068167ff162abd11c92b77d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]},"target_hinge_angle":-0.12965},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91892,"average_solve_count":37.0,"average_success_count":37.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_height":0.13165,"approach_handle.arc_height":0.08273,"descend_to_door.contact_force_threshold":14.43233,"push_door_open.max_push_time":2.99992,"push_door_open.push_offset_x":0.25757,"push_door_open.push_offset_y":0.05077,"push_door_open.push_speed":0.06912},"optimized_scores":{"best_composite_score":-0.23123,"best_fitness_score":0.14877,"best_task_score":0.14877},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":46.0,"contact_point_centroid":[0.10126,0.23029,0.60813],"force_p95":26.02305,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.0943,"mean_force":19.87504,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10028,0.31067,0.49888]},{"body_a":"world","body_b":"door_panel","contact_count":520.0,"contact_point_centroid":[0.29999,0.20969,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10012,0.37457,0.44058]}],"total_contact_groups":2},"final_pose_error":0.07032,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10016,0.29984,0.49972],"hinge_angle":-0.0517,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":44.0943,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":28.1286,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":566.0,"raw_peak_contact_force":44.0943,"subtask_id":"approach_handle","tcp_end":[0.10016,0.29984,0.49972],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.59131,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```