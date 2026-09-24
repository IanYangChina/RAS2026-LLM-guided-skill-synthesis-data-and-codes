## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.7956 | 1.00 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.7678 | 1.00 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.7956 | 1.00 | ❌ rejected |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.8233 | 1.00 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.7122 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen initial hinge angle: 0.129 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
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
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.796) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_handle
  anchor: fixture
  offset:
  - -0.394
  - -0.072
  - 0.35
  weight: 0.3
- id: push_goal
  anchor: fixture
  offset:
  - -0.3364
  - -0.2173
  - 0.35
  weight: 0.7
phases:
- id: approach
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_offset:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_made
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
- id: push
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    max_time:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
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
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_goal
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - -0.1
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.05, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset: status=consumed; consumers=target.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_made, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=reduce_speed
- **push** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=1, strategy=reduce_speed
- **retract** (`retract`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, -0.1, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.796
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.306
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 0.67 | 0.1613 |
| contact | 1.00 | 1.00 | 0.0078 |
| push | 0.67 | 1.00 | 0.0656 |
| retract | 1.00 | 0.67 | 0.2037 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.104, 0.238, 0.355) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 5.710 | 27.237 |
| contact | contact | 1.00 / force_exceeded | (0.104, 0.238, 0.355)→(0.104, 0.230, 0.354) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.667 | 65.761 | 9.190 |
| push | push | 0.67 / time_limit | (0.104, 0.230, 0.353)→(0.105, 0.171, 0.381) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 13.515 | 34.027 |
| retract | retract | 1.00 / step_budget | (0.105, 0.171, 0.381)→(0.128, -0.007, 0.473) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 9.465 | 37.301 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.823
- **K-run variance**: 0.0015
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 3.0
- **Final σ (mean)**: 0.273


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
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14386,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset":0.06202,"approach.speed":0.02851,"contact.contact_speed":0.02184,"contact.force_threshold":14.92554,"push.max_time":4.60486,"push.push_distance":0.17275,"push.push_speed":0.03803,"retract.retract_height":0.14101,"retract.speed":0.04069},"optimized_scores":{"best_composite_score":0.82333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":346.0,"contact_point_centroid":[0.18861,-0.0155,0.45888],"force_p95":25.06444,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.62676,"mean_force":17.32506,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.11998,0.03752,0.43139]},{"body_a":"door_panel","body_b":"link7","contact_count":687.0,"contact_point_centroid":[0.17073,0.10277,0.38688],"force_p95":18.80322,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.92599,"mean_force":13.09863,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.10558,0.16011,0.36242]},{"body_a":"door_panel","body_b":"link6","contact_count":21.0,"contact_point_centroid":[0.10378,0.1459,0.46328],"force_p95":21.27198,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.87936,"mean_force":17.98769,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.10518,0.2155,0.35719]},{"body_a":"door_panel","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.10471,0.13906,0.4601],"force_p95":18.363,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.34426,"mean_force":8.0367,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.10518,0.20674,0.35449]},{"body_a":"door_panel","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.10466,0.13937,0.46029],"force_p95":9.12054,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.35166,"mean_force":8.24291,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.10519,0.20716,0.35467]},{"body_a":"world","body_b":"door_panel","contact_count":508.0,"contact_point_centroid":[0.30293,0.16448,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.10242,0.3112,0.36181]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30377,0.16007,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.10521,0.20868,0.35514]},{"body_a":"world","body_b":"door_panel","contact_count":952.0,"contact_point_centroid":[0.31139,0.13398,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.10559,0.15984,0.36183]},{"body_a":"world","body_b":"door_panel","contact_count":408.0,"contact_point_centroid":[0.33906,0.08335,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.1184,0.04722,0.42619]}],"total_contact_groups":9},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13461,-0.05308,0.48076],"hinge_angle":0.7828,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":92.49873,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":529.0,"raw_peak_contact_force":22.87936,"subtask_id":"reach_handle","tcp_end":[0.10532,0.20961,0.35551],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":92.49873,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":33.0,"raw_peak_contact_force":9.35166,"tcp_end":[0.10519,0.2068,0.35458],"tcp_start":[0.10532,0.20961,0.35551],"tcp_to_object_dist_end":0.42374,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.50772,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1643.0,"raw_peak_contact_force":25.92599,"subtask_id":"push_goal","tcp_end":[0.10589,0.12283,0.38673],"tcp_start":[0.10519,0.2068,0.35458],"tcp_to_object_dist_end":0.41936,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.98323,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":754.0,"raw_peak_contact_force":29.62676,"tcp_end":[0.13461,-0.05308,0.48076],"tcp_start":[0.10589,0.12283,0.38673],"tcp_to_object_dist_end":0.50206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1fec9e8e5c1fdb9e52be404e6e4e2b90974542a257bfa7ba08d11c8aa9beb00c`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30612,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset":0.0658,"approach.speed":0.02339,"contact.contact_speed":0.03195,"contact.force_threshold":18.19854,"push.max_time":7.03941,"push.push_distance":0.25455,"push.push_speed":0.04337,"retract.retract_height":0.11836,"retract.speed":0.05892},"optimized_scores":{"best_composite_score":0.82333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":350.0,"contact_point_centroid":[0.19807,-0.04146,0.45968],"force_p95":23.3804,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.51526,"mean_force":14.99049,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.12818,0.00783,0.43128]},{"body_a":"door_panel","body_b":"link7","contact_count":629.0,"contact_point_centroid":[0.17383,0.08137,0.39832],"force_p95":21.55748,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.94828,"mean_force":13.48277,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.10848,0.13858,0.37243]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.17258,0.14642,0.38017],"force_p95":24.48682,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.80128,"mean_force":20.28367,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.10742,0.20382,0.3562]},{"body_a":"door_panel","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.1052,0.13648,0.46241],"force_p95":19.3412,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.02837,"mean_force":6.74041,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.10738,0.20506,0.35654]},{"body_a":"door_panel","body_b":"link7","contact_count":113.0,"contact_point_centroid":[0.17262,0.13486,0.378],"force_p95":16.49344,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.21798,"mean_force":12.89859,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.10743,0.19226,0.35386]},{"body_a":"world","body_b":"door_panel","contact_count":548.0,"contact_point_centroid":[0.30405,0.15873,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.1034,0.30797,0.36254]},{"body_a":"world","body_b":"door_panel","contact_count":124.0,"contact_point_centroid":[0.30561,0.152,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.10741,0.19379,0.35412]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.31602,0.1221,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.10851,0.13741,0.37302]},{"body_a":"world","body_b":"door_panel","contact_count":444.0,"contact_point_centroid":[0.34928,0.06995,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.12712,0.01236,0.42979]}],"total_contact_groups":9},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1489,-0.08163,0.46139],"hinge_angle":0.84613,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":38.51526,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.13134,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":568.0,"raw_peak_contact_force":24.80128,"subtask_id":"reach_handle","tcp_end":[0.10749,0.20178,0.35564],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.21798,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":237.0,"raw_peak_contact_force":18.21798,"tcp_end":[0.10755,0.18432,0.35302],"tcp_start":[0.10749,0.20178,0.35564],"tcp_to_object_dist_end":0.41251,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.79745,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1549.0,"raw_peak_contact_force":28.94828,"subtask_id":"push_goal","tcp_end":[0.10856,0.09075,0.40471],"tcp_start":[0.10755,0.18432,0.35302],"tcp_to_object_dist_end":0.42873,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":794.0,"raw_peak_contact_force":38.51526,"tcp_end":[0.1489,-0.08163,0.46139],"tcp_start":[0.10856,0.09075,0.40471],"tcp_to_object_dist_end":0.49165,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3715cb43c8f8f3084ca346701c1c33fec8eb1e50d1b8785cdad3bdd48e46f29f`; realized-scene SHA-256: `a85e6d1e7f42d6b7853e30231dc3bdf8d0b19eb5c068167ff162abd11c92b77d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.12965,"panel":{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13433,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset":0.05152,"approach.speed":0.05483,"contact.contact_speed":0.02942,"contact.force_threshold":15.97279,"push.max_time":5.0162,"push.push_distance":0.17131,"push.push_speed":0.06004,"retract.retract_height":0.13913,"retract.speed":0.06205},"optimized_scores":{"best_composite_score":0.74,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.10046,0.21891,0.46256],"force_p95":44.72367,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.20557,"mean_force":29.27687,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.09996,0.30024,0.35285]},{"body_a":"door_panel","body_b":"link6","contact_count":129.0,"contact_point_centroid":[0.10082,0.18467,0.48694],"force_p95":37.13892,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.76123,"mean_force":23.20426,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.09976,0.2579,0.37892]},{"body_a":"door_panel","body_b":"link6","contact_count":43.0,"contact_point_centroid":[0.1014,0.23105,0.46608],"force_p95":29.06182,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.03028,"mean_force":19.65438,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.1002,0.31394,0.3558]},{"body_a":"door_panel","body_b":"link7","contact_count":195.0,"contact_point_centroid":[0.16502,0.10589,0.46767],"force_p95":30.35678,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.63227,"mean_force":19.6218,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.09965,0.16303,0.44334]},{"body_a":"world","body_b":"door_panel","contact_count":208.0,"contact_point_centroid":[0.30001,0.21001,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.10011,0.35774,0.35535]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.29975,0.19967,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.10007,0.3018,0.3534]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.29975,0.19948,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.09997,0.30025,0.35285]},{"body_a":"world","body_b":"door_panel","contact_count":496.0,"contact_point_centroid":[0.30756,0.15188,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.09968,0.19481,0.4218]}],"total_contact_groups":8},"final_pose_error":0.01966,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09952,0.1142,0.47678],"hinge_angle":0.40304,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":86.56507,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":251.0,"raw_peak_contact_force":34.03028,"subtask_id":"reach_handle","tcp_end":[0.10015,0.30292,0.35377],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":86.56507,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":16.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09998,0.30028,0.35292],"tcp_start":[0.10015,0.30292,0.35377],"tcp_to_object_dist_end":0.47404,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.23846,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":47.20557,"subtask_id":"push_goal","tcp_end":[0.09992,0.30017,0.35272],"tcp_start":[0.09993,0.30019,0.35277],"tcp_to_object_dist_end":0.47381,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.41326,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":820.0,"raw_peak_contact_force":43.76123,"tcp_end":[0.09952,0.1142,0.47678],"tcp_start":[0.09992,0.30017,0.35272],"tcp_to_object_dist_end":0.50027,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```