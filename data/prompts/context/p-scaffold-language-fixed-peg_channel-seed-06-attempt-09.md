## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → approach → contact → push → retract → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.3081 | 0.00 | ❌ rejected |
| 8 | approach → approach → contact → push → retract → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3271 | 0.67 | ❌ rejected |
| 7 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4891 | 0.74 | ✅ accepted |
| 6 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1237 | 0.01 | ❌ rejected |
| 5 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.4079 | 0.57 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.308) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
- id: push
  anchor: world
  offset:
  - 0.5
  - -0.08
  - 0.04
phases:
- id: align_1
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach
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
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
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
  subtask_id: contact
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
    - 0.02
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
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
- **align_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], offset_along_axis={axis=world_y, distance=0.04, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.308
- **task_score** (E): 0.000
- **fitness_score**: 0.145  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2005 |
| approach_1 | 1.00 | 1.00 | 0.0569 |
| contact_1 | 1.00 | 1.00 | 0.0003 |
| push_1 | 1.00 | 1.00 | 0.1072 |
| backoff_1 | 1.00 | 1.00 | 0.0325 |
| lift_1 | 1.00 | 1.00 | 0.0845 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.145, 0.108) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.560 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.145, 0.108)→(0.498, 0.116, 0.060) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.667 | 30.847 | 30.885 |
| contact_1 | contact | 1.00 / force_exceeded | (0.498, 0.116, 0.060)→(0.498, 0.115, 0.060) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 19.023 | 19.023 |
| push_1 | push | 1.00 / step_budget | (0.498, 0.115, 0.060)→(0.497, 0.222, 0.049) | (0.501, 0.099, 0.034)→(0.505, 0.142, 0.018) | 0.180→0.223 | 1.00 / 1.000 | 0.509 | 47.474 |
| backoff_1 | retract | 1.00 / step_budget | (0.497, 0.222, 0.049)→(0.495, 0.254, 0.045) | (0.505, 0.142, 0.018)→(0.516, 0.145, 0.018) | 0.223→0.228 | 1.00 / 1.000 | 0.517 | 0.731 |
| lift_1 | retract | 1.00 / step_budget | (0.495, 0.254, 0.045)→(0.493, 0.260, 0.129) | (0.516, 0.145, 0.018)→(0.519, 0.146, 0.018) | 0.228→0.229 | 1.00 / 1.000 | 0.591 | 1.881 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.247
- phase_breakdown.push_score: 0.003
- phase_breakdown.approach_score: 0.547
- phase_breakdown.contact_score: 0.678

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.148
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.309
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.366


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48113,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00537,"approach_1.lateral_offset_y":0.01,"approach_1.speed":0.07026,"backoff_1.backoff_distance":0.0315,"backoff_1.speed":0.05435,"contact_1.contact_force_threshold":7.99809,"lift_1.retract_height":0.1995,"lift_1.speed":0.07688,"push_1.push_stroke":0.15965,"push_1.speed":0.0411},"optimized_scores":{"best_composite_score":-0.30515,"best_fitness_score":0.14819,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":204.0,"contact_point_centroid":[0.5034,0.06751,0.00938],"force_p95":0.5509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.55184,"mean_force":1.97817,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50057,0.1005,0.08225]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.51458,0.08123,0.05846],"force_p95":58.02388,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.08163,"mean_force":41.82129,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50322,0.08474,0.05987]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.5002,0.10023,0.00958],"force_p95":55.74781,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.34396,"mean_force":10.84926,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50118,0.14584,0.05326]},{"body_a":"attachment","body_b":"peg","contact_count":100.0,"contact_point_centroid":[0.50848,0.09107,0.05761],"force_p95":56.82469,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.88646,"mean_force":34.10551,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50344,0.10065,0.0577]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51492,0.08099,0.05809],"force_p95":24.88651,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.88651,"mean_force":24.88651,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50348,0.08423,0.05921]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52077,0.0701,0.00932],"force_p95":24.72766,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.72766,"mean_force":24.72766,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50348,0.08423,0.05921]},{"body_a":"peg","body_b":"channel_base_body","contact_count":177.0,"contact_point_centroid":[0.49397,0.10647,0.00934],"force_p95":0.71967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.23188,"mean_force":0.61433,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49633,0.2311,0.11553]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47499,0.12,0.02676],"force_p95":3.79679,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.79756,"mean_force":3.05744,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49664,0.23581,0.1481]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50304,0.06739,0.00932],"force_p95":0.61054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56899,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49942,0.15735,0.20055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.49572,0.1083,0.00933],"force_p95":0.72868,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78273,"mean_force":0.54958,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.49868,0.21301,0.0474]}],"total_contact_groups":10},"final_pose_error":0.04913,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49347,0.11065,0.02667],"final_tcp_position":[0.49712,0.22955,0.19719],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":59.55184,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54683,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49999,0.1165,0.10729],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":204.0,"n_steps_budget":600.0,"object_pos_end":[0.5031,0.06732,0.03371],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.14749,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":59.55184,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":211.0,"raw_peak_contact_force":59.55184,"subtask_id":"contact","tcp_end":[0.50348,0.08423,0.05921],"tcp_start":[0.49999,0.1165,0.10729],"tcp_to_object_dist_end":0.0306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50303,0.06728,0.03364],"object_pos_start":[0.5031,0.06732,0.03371],"object_to_goal_dist_end":0.14744,"object_to_goal_dist_start":0.14749,"object_z_max":0.03371,"peak_contact_force":24.88651,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":24.88651,"tcp_end":[0.50345,0.08413,0.05912],"tcp_start":[0.50348,0.08423,0.05921],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11077,0.02674],"object_pos_start":[0.50303,0.06728,0.03364],"object_to_goal_dist_end":0.19128,"object_to_goal_dist_start":0.14744,"object_z_max":0.04055,"peak_contact_force":0.36396,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":430.0,"raw_peak_contact_force":58.34396,"tcp_end":[0.49967,0.20809,0.04896],"tcp_start":[0.50345,0.08413,0.05912],"tcp_to_object_dist_end":0.09989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":41.0,"n_steps_budget":600.0,"object_pos_end":[0.49531,0.1107,0.02671],"object_pos_start":[0.49605,0.11077,0.02674],"object_to_goal_dist_end":0.19122,"object_to_goal_dist_start":0.19128,"object_z_max":0.02677,"peak_contact_force":0.45562,"phase_name":"backoff_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":41.0,"raw_peak_contact_force":0.78273,"tcp_end":[0.49779,0.2201,0.04591],"tcp_start":[0.49967,0.20809,0.04896],"tcp_to_object_dist_end":0.11111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":177.0,"n_steps_budget":1000.0,"object_pos_end":[0.49347,0.11065,0.02667],"object_pos_start":[0.49531,0.1107,0.02671],"object_to_goal_dist_end":0.19123,"object_to_goal_dist_start":0.19122,"object_z_max":0.02686,"peak_contact_force":0.60785,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":182.0,"raw_peak_contact_force":4.23188,"tcp_end":[0.49712,0.22955,0.19719],"tcp_start":[0.49779,0.2201,0.04591],"tcp_to_object_dist_end":0.20791,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44099,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00585,"approach_1.lateral_offset_y":0.00979,"approach_1.speed":0.08962,"backoff_1.backoff_distance":0.0295,"backoff_1.speed":0.04055,"contact_1.contact_force_threshold":14.79318,"lift_1.retract_height":0.12195,"lift_1.speed":0.0803,"push_1.push_stroke":0.13667,"push_1.speed":0.0585},"optimized_scores":{"best_composite_score":-0.30991,"best_fitness_score":0.14342,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":107.0,"contact_point_centroid":[0.5015,0.11968,0.00964],"force_p95":37.20433,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.01463,"mean_force":13.4397,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50384,0.14562,0.05681]},{"body_a":"attachment","body_b":"peg","contact_count":72.0,"contact_point_centroid":[0.51128,0.13016,0.05725],"force_p95":38.49138,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.51322,"mean_force":19.30829,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50442,0.13885,0.05782]},{"body_a":"peg","body_b":"channel_base_body","contact_count":188.0,"contact_point_centroid":[0.50373,0.1117,0.00939],"force_p95":0.60601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.46703,"mean_force":0.71538,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50476,0.14233,0.08367]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51667,0.1244,0.05874],"force_p95":31.94339,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.94339,"mean_force":31.94339,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50532,0.12793,0.06033]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51672,0.12436,0.05863],"force_p95":23.40051,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.40051,"mean_force":23.40051,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50534,0.12779,0.06012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51925,0.12,0.00942],"force_p95":23.31576,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.31576,"mean_force":23.31576,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50534,0.12779,0.06012]},{"body_a":"peg","body_b":"world","contact_count":167.0,"contact_point_centroid":[0.50349,0.14957,-0.00192],"force_p95":1.16026,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.11809,"mean_force":0.66369,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50109,0.19916,0.05117]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50351,0.11176,0.00934],"force_p95":0.6343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56822,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.50263,0.17712,0.19971]},{"body_a":"peg","body_b":"world","contact_count":37.0,"contact_point_centroid":[0.50473,0.15047,-0.00196],"force_p95":0.68376,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68379,"mean_force":0.60415,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.49939,0.23333,0.0476]},{"body_a":"peg","body_b":"world","contact_count":92.0,"contact_point_centroid":[0.50605,0.14925,-0.00196],"force_p95":0.68371,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68371,"mean_force":0.6069,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.49663,0.24405,0.07731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.19934,0.29835]}],"total_contact_groups":11},"final_pose_error":0.04918,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50724,0.14978,0.01413],"final_tcp_position":[0.49704,0.24488,0.11926],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":42.01463,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56268,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50616,0.15629,0.10861],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":188.0,"n_steps_budget":600.0,"object_pos_end":[0.50374,0.11182,0.03387],"object_pos_start":[0.50375,0.11176,0.0338],"object_to_goal_dist_end":0.19195,"object_to_goal_dist_start":0.1919,"object_z_max":0.03387,"peak_contact_force":32.46703,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":189.0,"raw_peak_contact_force":32.46703,"subtask_id":"contact","tcp_end":[0.50534,0.12779,0.06012],"tcp_start":[0.50616,0.15629,0.10861],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50369,0.11179,0.03383],"object_pos_start":[0.50374,0.11182,0.03387],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19195,"object_z_max":0.03387,"peak_contact_force":23.40051,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":23.40051,"tcp_end":[0.50527,0.12765,0.05996],"tcp_start":[0.50534,0.12779,0.06012],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.50448,0.14981,0.01413],"object_pos_start":[0.50369,0.11179,0.03383],"object_to_goal_dist_end":0.23131,"object_to_goal_dist_start":0.19192,"object_z_max":0.03563,"peak_contact_force":0.60192,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":346.0,"raw_peak_contact_force":42.01463,"tcp_end":[0.50052,0.22935,0.0492],"tcp_start":[0.50527,0.12765,0.05996],"tcp_to_object_dist_end":0.08702,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":37.0,"n_steps_budget":600.0,"object_pos_end":[0.50513,0.14977,0.01412],"object_pos_start":[0.50448,0.14981,0.01413],"object_to_goal_dist_end":0.23128,"object_to_goal_dist_start":0.23131,"object_z_max":0.01413,"peak_contact_force":0.53278,"phase_name":"backoff_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":37.0,"raw_peak_contact_force":0.68379,"tcp_end":[0.49862,0.23948,0.04617],"tcp_start":[0.50052,0.22935,0.0492],"tcp_to_object_dist_end":0.09548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":92.0,"n_steps_budget":960.0,"object_pos_end":[0.50724,0.14978,0.01413],"object_pos_start":[0.50513,0.14977,0.01412],"object_to_goal_dist_end":0.23135,"object_to_goal_dist_start":0.23128,"object_z_max":0.01413,"peak_contact_force":0.60185,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":92.0,"raw_peak_contact_force":0.68371,"tcp_end":[0.49704,0.24488,0.11926],"tcp_start":[0.49862,0.23948,0.04617],"tcp_to_object_dist_end":0.14213,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08333,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00465,"approach_1.lateral_offset_y":0.00998,"approach_1.speed":0.0584,"backoff_1.backoff_distance":0.09256,"backoff_1.speed":0.02508,"contact_1.contact_force_threshold":2.0536,"lift_1.retract_height":0.07786,"lift_1.speed":0.038,"push_1.push_stroke":0.12831,"push_1.speed":0.08667},"optimized_scores":{"best_composite_score":-0.30922,"best_fitness_score":0.14411,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":69.0,"contact_point_centroid":[0.50089,0.11993,0.00967],"force_p95":36.48341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.06256,"mean_force":8.12659,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48624,0.14594,0.05738]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.49286,0.13917,0.05652],"force_p95":37.41731,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.48282,"mean_force":8.92276,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48635,0.14779,0.05721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50317,0.12,0.00942],"force_p95":7.96408,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.78332,"mean_force":3.30365,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48658,0.13481,0.06035]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49836,0.13366,0.05863],"force_p95":7.84707,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.25688,"mean_force":4.15875,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48653,0.13474,0.06026]},{"body_a":"peg","body_b":"world","contact_count":182.0,"contact_point_centroid":[0.50288,0.15341,-0.00138],"force_p95":1.05645,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53669,"mean_force":0.60951,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4886,0.19387,0.05203]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.49639,0.11903,0.00939],"force_p95":0.63431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56429,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49175,0.1803,0.19941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49959,0.19904,0.2964]},{"body_a":"peg","body_b":"world","contact_count":228.0,"contact_point_centroid":[0.53076,0.16966,-0.00199],"force_p95":0.72624,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72638,"mean_force":0.60617,"phase_index":4.0,"phase_name":"backoff_1","phase_type":"retract","tcp_position_centroid":[0.48861,0.26427,0.04498]},{"body_a":"peg","body_b":"world","contact_count":52.0,"contact_point_centroid":[0.55105,0.17737,-0.00199],"force_p95":0.72623,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72623,"mean_force":0.60616,"phase_index":5.0,"phase_name":"lift_1","phase_type":"retract","tcp_position_centroid":[0.48616,0.30389,0.05247]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.49591,0.11923,0.00947],"force_p95":0.58294,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6351,"mean_force":0.53923,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48485,0.14908,0.08434]}],"total_contact_groups":10},"final_pose_error":0.04965,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.55534,0.17775,0.01409],"final_tcp_position":[0.48567,0.30451,0.07186],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":42.06256,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11913,0.03403],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57183,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48515,0.16278,0.10959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":200.0,"n_steps_budget":720.0,"object_pos_end":[0.49603,0.11915,0.03386],"object_pos_start":[0.49602,0.11913,0.03403],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19926,"object_z_max":0.03408,"peak_contact_force":0.52178,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":200.0,"raw_peak_contact_force":0.6351,"subtask_id":"contact","tcp_end":[0.48666,0.13493,0.06052],"tcp_start":[0.48515,0.16278,0.10959],"tcp_to_object_dist_end":0.03237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.49608,0.11917,0.03386],"object_pos_start":[0.49603,0.11915,0.03386],"object_to_goal_dist_end":0.1993,"object_to_goal_dist_start":0.19928,"object_z_max":0.03386,"peak_contact_force":8.78332,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":8.78332,"tcp_end":[0.48641,0.13458,0.06004],"tcp_start":[0.48666,0.13493,0.06052],"tcp_to_object_dist_end":0.03188,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":251.0,"n_steps_budget":840.0,"object_pos_end":[0.51431,0.16465,0.0141],"object_pos_start":[0.49608,0.11917,0.03386],"object_to_goal_dist_end":0.24643,"object_to_goal_dist_start":0.1993,"object_z_max":0.03422,"peak_contact_force":0.56236,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":311.0,"raw_peak_contact_force":42.06256,"tcp_end":[0.49133,0.22872,0.04949],"tcp_start":[0.48641,0.13458,0.06004],"tcp_to_object_dist_end":0.07671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.54754,0.17523,0.01409],"object_pos_start":[0.51431,0.16465,0.0141],"object_to_goal_dist_end":0.26091,"object_to_goal_dist_start":0.24643,"object_z_max":0.0141,"peak_contact_force":0.56215,"phase_name":"backoff_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":228.0,"raw_peak_contact_force":0.72638,"tcp_end":[0.48798,0.30262,0.04356],"tcp_start":[0.49133,0.22872,0.04949],"tcp_to_object_dist_end":0.14368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.55534,0.17775,0.01409],"object_pos_start":[0.54754,0.17523,0.01409],"object_to_goal_dist_end":0.2649,"object_to_goal_dist_start":0.26091,"object_z_max":0.01409,"peak_contact_force":0.56239,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":52.0,"raw_peak_contact_force":0.72623,"tcp_end":[0.48567,0.30451,0.07186],"tcp_start":[0.48798,0.30262,0.04356],"tcp_to_object_dist_end":0.15575,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```