## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | time_limit | 6  | -0.2055 | 0.17 | ❌ rejected |
| 6 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | 7  | 0.7483 | 0.58 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | time_limit | 6  | 0.2819 | 0.66 | ✅ accepted |
| 4 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | 7  | 0.2314 | 0.61 | ✅ accepted |
| 3 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 7  | 0.7811 | 0.67 | ✅ accepted |

**Proposal policy**: task_score is 0.67 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.781) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_push_point
  anchor: fixture
  offset:
  - 0.2
  - -0.01
  - 0.2
  weight: 0.3
- id: push_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_push_point
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - 0.2
    - -0.01
    - 0.25
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_push_point
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - 0.2
    - -0.01
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
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
  subtask_id: reach_push_point
- id: push_door_open
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - 0.2
    - -0.01
    - 0.2
    offset_along_axis:
      distance: 0.4
      axis: world_y
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.2
      - 0.6
      default: 0.4
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: hinge_movement
    when: during_phase
    predicate: hinge_delta_reached
    threshold: 0.4
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_push_point** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[0.2, -0.01, 0.25], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[0.2, -0.01, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_door_open** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[0.2, -0.01, 0.2], offset_along_axis={axis=world_y, distance=0.4, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=hinge_movement, when=during_phase, predicate=hinge_delta_reached, on_failure=retry, threshold=0.4
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.781
- **task_score** (E): 0.667
- **fitness_score**: 0.667  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.444
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_push_point | 0.00 | 0.67 | 0.3722 |
| descend_contact | 1.00 | 1.00 | 0.0006 |
| push_door_open | 0.67 | 0.67 | 0.0622 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_push_point | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.457, 0.335, 0.313) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 259.989 | 745.274 |
| descend_contact | descend | 1.00 / force_exceeded | (0.457, 0.335, 0.313)→(0.457, 0.335, 0.313) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.667 | 108.862 | 250.388 |
| push_door_open | push | 0.67 / time_limit | (0.457, 0.335, 0.313)→(0.485, 0.387, 0.295) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 92.310 | 174.724 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.170
- **K-run variance**: 0.3025
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.294


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15534,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_push_point.approach_speed":0.16929,"approach_push_point.approach_tolerance":0.03587,"descend_contact.contact_force_threshold":10.61442,"descend_contact.descend_speed":0.03481,"push_door_open.push_distance":0.33024,"push_door_open.push_speed":0.04182},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":550.0,"contact_point_centroid":[0.14631,0.06335,0.64536],"force_p95":607.51106,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":752.10364,"mean_force":302.36934,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.34753,0.32152,0.35057]},{"body_a":"door_frame","body_b":"link6","contact_count":233.0,"contact_point_centroid":[0.47544,0.22488,0.38849],"force_p95":496.92964,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":628.2897,"mean_force":303.06652,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.50406,0.30224,0.27331]},{"body_a":"door_panel","body_b":"link5","contact_count":14.0,"contact_point_centroid":[0.10383,0.146,0.6048],"force_p95":366.52907,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":389.54711,"mean_force":212.67668,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.20886,0.36252,0.33078]},{"body_a":"door_frame","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.51429,0.22487,0.31837],"force_p95":261.13133,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.86361,"mean_force":228.87259,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.45258,0.28161,0.29533]},{"body_a":"door_frame","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.48278,0.22492,0.39247],"force_p95":84.85641,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.19273,"mean_force":28.21605,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.54066,0.30907,0.26383]},{"body_a":"door_frame","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.48251,0.22498,0.39299],"force_p95":55.63063,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.63063,"mean_force":55.63063,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.54046,0.30929,0.26445]},{"body_a":"door_panel","body_b":"link4","contact_count":170.0,"contact_point_centroid":[0.28963,0.00869,0.54465],"force_p95":24.85064,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.189,"mean_force":14.58139,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.55786,0.33286,0.24968]},{"body_a":"world","body_b":"door_panel","contact_count":876.0,"contact_point_centroid":[0.32543,0.11262,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.35167,0.32514,0.33554]},{"body_a":"world","body_b":"door_panel","contact_count":792.0,"contact_point_centroid":[0.3588,0.058,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.5619,0.3382,0.24787]}],"total_contact_groups":9},"final_pose_error":0.19543,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.58402,0.3675,0.23753],"hinge_angle":0.73476,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":752.10364,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_push_point","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1698.0,"raw_peak_contact_force":752.10364,"subtask_id":"reach_push_point","tcp_end":[0.54033,0.30941,0.26458],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.67653,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":55.63063,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":55.63063,"subtask_id":"reach_push_point","tcp_end":[0.54053,0.30916,0.26431],"tcp_start":[0.54033,0.30941,0.26458],"tcp_to_object_dist_end":0.67647,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":970.0,"raw_peak_contact_force":110.19273,"subtask_id":"push_door","tcp_end":[0.58402,0.3675,0.23753],"tcp_start":[0.54053,0.30916,0.26431],"tcp_to_object_dist_end":0.72976,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31068,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_push_point.approach_speed":0.17732,"approach_push_point.approach_tolerance":0.03148,"descend_contact.contact_force_threshold":13.98176,"descend_contact.descend_speed":0.043,"push_door_open.push_distance":0.45197,"push_door_open.push_speed":0.06636},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":518.0,"contact_point_centroid":[0.15611,0.05383,0.63922],"force_p95":600.30454,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":886.2095,"mean_force":280.92432,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.36256,0.32016,0.34149]},{"body_a":"door_frame","body_b":"link6","contact_count":263.0,"contact_point_centroid":[0.4781,0.22485,0.38866],"force_p95":526.84387,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":654.77396,"mean_force":302.46234,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.51191,0.30319,0.27086]},{"body_a":"door_frame","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.49725,0.225,0.38926],"force_p95":442.38679,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":463.61579,"mean_force":251.32583,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.55683,0.30826,0.26077]},{"body_a":"door_frame","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.51458,0.2249,0.3176],"force_p95":263.51005,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.30187,"mean_force":234.00116,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.45268,0.28167,0.29465]},{"body_a":"door_frame","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.49747,0.22498,0.38857],"force_p95":125.96237,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.04892,"mean_force":54.41078,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.55694,0.30818,0.26001]},{"body_a":"door_panel","body_b":"link4","contact_count":34.0,"contact_point_centroid":[0.28737,0.00257,0.54889],"force_p95":27.72552,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.45397,"mean_force":17.15834,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.56146,0.32084,0.25153]},{"body_a":"door_panel","body_b":"link4","contact_count":3.0,"contact_point_centroid":[0.27802,-0.00537,0.56103],"force_p95":18.02595,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.05395,"mean_force":17.64887,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.55689,0.3083,0.26042]},{"body_a":"world","body_b":"door_panel","contact_count":968.0,"contact_point_centroid":[0.32735,0.10828,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.35888,0.32354,0.33016]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.35995,0.05687,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.55684,0.30839,0.26077]},{"body_a":"world","body_b":"door_panel","contact_count":772.0,"contact_point_centroid":[0.35894,0.05788,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.57603,0.35505,0.24358]}],"total_contact_groups":10},"final_pose_error":0.25965,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.59779,0.4056,0.23312],"hinge_angle":0.72276,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":886.2095,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":205.2368,"phase_name":"approach_push_point","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1775.0,"raw_peak_contact_force":886.2095,"subtask_id":"reach_push_point","tcp_end":[0.55675,0.30828,0.26127],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.68794,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":39.03588,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13.0,"raw_peak_contact_force":463.61579,"subtask_id":"reach_push_point","tcp_end":[0.55694,0.30819,0.26014],"tcp_start":[0.55675,0.30828,0.26127],"tcp_to_object_dist_end":0.68763,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":809.0,"raw_peak_contact_force":137.04892,"subtask_id":"push_door","tcp_end":[0.59779,0.4056,0.23312],"tcp_start":[0.55694,0.30819,0.26014],"tcp_to_object_dist_end":0.75908,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.62963,"average_solve_count":54.0,"average_success_count":54.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_push_point.approach_speed":0.16548,"approach_push_point.approach_tolerance":0.07089,"descend_contact.contact_force_threshold":11.9006,"descend_contact.descend_speed":0.03433,"push_door_open.push_distance":0.44347,"push_door_open.push_speed":0.05596},"optimized_scores":{"best_composite_score":0.00333,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":907.0,"contact_point_centroid":[0.10164,0.23933,0.61354],"force_p95":583.78761,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":597.50826,"mean_force":539.67991,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.23245,0.38479,0.36443]},{"body_a":"door_panel","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.10181,0.24164,0.628],"force_p95":276.58371,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":276.93146,"mean_force":270.95197,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.27356,0.38816,0.41424]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10181,0.24177,0.62786],"force_p95":231.9185,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":231.9185,"mean_force":231.9185,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.27348,0.38822,0.41406]},{"body_a":"world","body_b":"door_panel","contact_count":1044.0,"contact_point_centroid":[0.30067,0.21879,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_push_point","phase_type":"approach","tcp_position_centroid":[0.22465,0.38478,0.36299]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30084,0.22083,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.27348,0.38822,0.41406]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30083,0.2208,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.27352,0.3882,0.41416]}],"total_contact_groups":6},"final_pose_error":0.53663,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.27363,0.38806,0.41437],"hinge_angle":-0.15341,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":597.50826,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":574.73132,"phase_name":"approach_push_point","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1951.0,"raw_peak_contact_force":597.50826,"subtask_id":"reach_push_point","tcp_end":[0.27348,0.38822,0.41406],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.63004,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":231.9185,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":231.9185,"subtask_id":"reach_push_point","tcp_end":[0.27352,0.3882,0.41416],"tcp_start":[0.27348,0.38822,0.41406],"tcp_to_object_dist_end":0.63011,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":276.93146,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":276.93146,"subtask_id":"push_door","tcp_end":[0.27363,0.38806,0.41437],"tcp_start":[0.2736,0.38812,0.41431],"tcp_to_object_dist_end":0.63021,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```