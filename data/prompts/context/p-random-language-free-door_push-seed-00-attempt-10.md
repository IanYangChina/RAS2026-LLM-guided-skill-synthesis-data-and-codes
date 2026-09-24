## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 0.4501 | 0.45 | ❌ rejected |
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.3849 | 0.43 | ❌ rejected |
| 8 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.5061 | 0.50 | ❌ rejected |
| 7 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.5067 | 0.50 | ❌ rejected |
| 6 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.6355 | 0.46 | ❌ rejected |

**Proposal policy**: task_score is 0.45 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73`
- Frozen initial hinge angle: 0.048 rad
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
  frozen_initial_hinge_angle_rad: 0.0478
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73

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

## Current Skill (Q=0.450) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.5
  weight: 0.3
- id: push
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_handle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.5
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_established
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: approach
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    offset_along_axis:
      distance: 0.35
      axis: world_y
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: world_y
      tolerance: 0.15
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.35
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.5]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_established, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_door** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_y, distance=0.35, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=world_y, tolerance=0.15
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: 0.450
- **task_score** (E): 0.447
- **fitness_score**: 0.447  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2540 |
| descend_contact | 1.00 | 1.00 | 0.0231 |
| push_door | 0.00 | 0.67 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.188, 0.492) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 9.495 | 81.654 |
| descend_contact | descend | 1.00 / force_exceeded | (0.100, 0.188, 0.492)→(0.100, 0.187, 0.469) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 11.260 | 17.949 |
| push_door | push | 0.00 / guard_failure | (0.100, 0.187, 0.469)→(0.100, 0.187, 0.469) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.667 | 0.000 | 20.529 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.589
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.589
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.589
- **Median Q (composite search score)**: 0.421
- **K-run variance**: 0.0112
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.398


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `275c70960dc683bb9d0f514db4e615bd3a6644bf8e38d8dd2bfa731bf179f097`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `35996939e2e1630dea7cedb55906290b2cb0393492844f540c2c9d9496e5416e`; realized-scene SHA-256: `62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04781,"panel":{"name":"door_panel","orientation":[0.99971,0.0,0.0,0.0239],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99971,0.0,0.0,0.0239],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.59524,"average_solve_count":42.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.16204,"descend_contact.descend_speed":0.06491,"descend_contact.force_threshold":8.8389,"push_door.force_threshold":19.85545,"push_door.push_distance":0.25451,"push_door.push_speed":0.09894},"optimized_scores":{"best_composite_score":0.33708,"best_fitness_score":0.33375,"best_task_score":0.33375},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":179.0,"contact_point_centroid":[0.10306,0.15362,0.56319],"force_p95":39.2541,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.56848,"mean_force":19.57707,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09984,0.23538,0.45924]},{"body_a":"door_panel","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.16315,0.13072,0.51242],"force_p95":18.96621,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.51454,"mean_force":15.90265,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09989,0.19395,0.48775]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16287,0.1237,0.50212],"force_p95":18.21513,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.21513,"mean_force":18.21513,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09976,0.18705,0.47735]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.1629,0.1241,0.50814],"force_p95":16.07758,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.19488,"mean_force":10.46211,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09979,0.18748,0.48342]},{"body_a":"world","body_b":"door_panel","contact_count":852.0,"contact_point_centroid":[0.30162,0.17458,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09971,0.29215,0.42009]},{"body_a":"world","body_b":"door_panel","contact_count":100.0,"contact_point_centroid":[0.30709,0.14628,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.0998,0.18756,0.48451]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30714,0.1461,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09976,0.18705,0.47735]}],"total_contact_groups":7},"final_pose_error":0.27829,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09973,0.18701,0.47723],"hinge_angle":0.22269,"initial_hinge_angle":0.04781,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04781,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":58.56848,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.11531,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1071.0,"raw_peak_contact_force":58.56848,"subtask_id":"approach","tcp_end":[0.09988,0.18819,0.49175],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.40291,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":108.0,"raw_peak_contact_force":16.19488,"subtask_id":"approach","tcp_end":[0.09976,0.18705,0.47735],"tcp_start":[0.09988,0.18819,0.49175],"tcp_to_object_dist_end":0.5223,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":18.21513,"subtask_id":"push","tcp_end":[0.09973,0.18701,0.47723],"tcp_start":[0.09976,0.18705,0.47735],"tcp_to_object_dist_end":0.52217,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7a748efd829eb09daaf6b07ec36a2131763f35cca8c1f058f1a757467a8ce067`; realized-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.00413,"panel":{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.55814,"average_solve_count":43.0,"average_success_count":43.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.16148,"descend_contact.descend_speed":0.06877,"descend_contact.force_threshold":9.55723,"push_door.force_threshold":20.09205,"push_door.push_distance":0.35889,"push_door.push_speed":0.07895},"optimized_scores":{"best_composite_score":0.42116,"best_fitness_score":0.41783,"best_task_score":0.41783},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":232.0,"contact_point_centroid":[0.10241,0.16202,0.55204],"force_p95":45.22323,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.71267,"mean_force":20.89737,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0998,0.24565,0.45213]},{"body_a":"door_panel","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.16315,0.13081,0.51235],"force_p95":19.00143,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.55333,"mean_force":15.85003,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09989,0.19404,0.48769]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16302,0.12362,0.49876],"force_p95":19.44047,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.44047,"mean_force":19.44047,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09975,0.18682,0.47399]},{"body_a":"door_panel","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.16294,0.12401,0.50614],"force_p95":16.39964,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.84507,"mean_force":10.83953,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09979,0.18734,0.48141]},{"body_a":"world","body_b":"door_panel","contact_count":1020.0,"contact_point_centroid":[0.30116,0.18017,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09965,0.29817,0.41592]},{"body_a":"world","body_b":"door_panel","contact_count":120.0,"contact_point_centroid":[0.30709,0.1463,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09981,0.18758,0.48467]}],"total_contact_groups":6},"final_pose_error":0.37325,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09972,0.18679,0.47386],"hinge_angle":0.22307,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":77.71267,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1292.0,"raw_peak_contact_force":77.71267,"subtask_id":"approach","tcp_end":[0.09988,0.18819,0.49175],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.95149,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":130.0,"raw_peak_contact_force":16.84507,"subtask_id":"approach","tcp_end":[0.09975,0.18682,0.47399],"tcp_start":[0.09988,0.18819,0.49175],"tcp_to_object_dist_end":0.51915,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":19.44047,"subtask_id":"push","tcp_end":[0.09972,0.18679,0.47386],"tcp_start":[0.09975,0.18682,0.47399],"tcp_to_object_dist_end":0.51902,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `8f682501979e58f93da2583f25150788eff90e19c055477d4547c33e5c9d7ff1`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.08321,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.57778,"average_solve_count":45.0,"average_success_count":45.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.17647,"descend_contact.descend_speed":0.08082,"descend_contact.force_threshold":13.27049,"push_door.force_threshold":19.50367,"push_door.push_distance":0.38375,"push_door.push_speed":0.08248},"optimized_scores":{"best_composite_score":0.59191,"best_fitness_score":0.58858,"best_task_score":0.58858},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":317.0,"contact_point_centroid":[0.10186,0.17815,0.53437],"force_p95":38.78891,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.68015,"mean_force":22.19535,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09976,0.26448,0.43913]},{"body_a":"door_panel","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.16319,0.13107,0.51225],"force_p95":17.97637,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.19266,"mean_force":15.42,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0999,0.19427,0.48758]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16306,0.12291,0.47936],"force_p95":23.93072,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.93072,"mean_force":23.93072,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09976,0.18607,0.45456]},{"body_a":"door_panel","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.163,0.12398,0.49645],"force_p95":17.23224,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.80556,"mean_force":11.95344,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09977,0.18722,0.47169]},{"body_a":"world","body_b":"door_panel","contact_count":892.0,"contact_point_centroid":[0.30103,0.18926,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09958,0.30108,0.41383]},{"body_a":"world","body_b":"door_panel","contact_count":220.0,"contact_point_centroid":[0.30711,0.1462,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09977,0.18721,0.47156]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30727,0.14565,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09976,0.18607,0.45456]}],"total_contact_groups":7},"final_pose_error":0.39189,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09973,0.18603,0.45442],"hinge_angle":0.2252,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":108.68015,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":902.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.37018,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1244.0,"raw_peak_contact_force":108.68015,"subtask_id":"approach","tcp_end":[0.0999,0.18876,0.4914],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.5358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.42565,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":246.0,"raw_peak_contact_force":20.80556,"subtask_id":"approach","tcp_end":[0.09976,0.18607,0.45456],"tcp_start":[0.0999,0.18876,0.4914],"tcp_to_object_dist_end":0.50119,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":23.93072,"subtask_id":"push","tcp_end":[0.09973,0.18603,0.45442],"tcp_start":[0.09976,0.18607,0.45456],"tcp_to_object_dist_end":0.50105,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```