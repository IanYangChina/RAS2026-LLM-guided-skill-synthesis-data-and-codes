## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1026 | 0.43 | ✅ accepted |
| 10 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.0053 | 0.35 | ❌ rejected |
| 9 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0242 | 0.34 | ❌ rejected |
| 8 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0994 | 0.42 | ✅ accepted |
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0565 | 0.07 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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

## Current Skill (Q=0.103) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_above
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.05
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_to_height
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.008
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_detected_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: continue
  subtask_id: contact
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: progress_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: push
- id: retract_lift
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.05], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_height** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_detected_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=0.5
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=progress_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **retract_lift** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.103
- **task_score** (E): 0.429
- **fitness_score**: 0.293  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.2094 |
| descend_to_height | 1.00 | 1.00 | 0.0605 |
| contact_peg | 1.00 | 1.00 | 0.0040 |
| push_channel | 0.00 | 1.00 | 0.0406 |
| retract_lift | 0.33 | 1.00 | 0.1079 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.123, 0.107) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.542 | 3.242 |
| descend_to_height | descend | 1.00 / step_budget | (0.516, 0.123, 0.107)→(0.504, 0.117, 0.048) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.333 | 123.361 | 135.609 |
| contact_peg | contact | 1.00 / force_exceeded | (0.504, 0.117, 0.048)→(0.503, 0.115, 0.045) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 16.467 | 17.057 |
| push_channel | push | 0.00 / step_budget | (0.503, 0.115, 0.045)→(0.524, 0.092, 0.061) | (0.505, 0.084, 0.034)→(0.506, 0.000, 0.027) | 0.164→0.084 | 1.00 / 3.000 | 351.393 | 1056.908 |
| retract_lift | retract | 0.33 / step_budget | (0.524, 0.092, 0.061)→(0.509, -0.008, 0.097) | (0.506, 0.000, 0.027)→(0.505, -0.015, 0.024) | 0.084→0.069 | 1.00 / 1.333 | 76.146 | 471.948 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.847
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.847
- phase_score: 0.235
- phase_breakdown.contact_score: 0.801
- phase_breakdown.push_score: 0.037
- phase_breakdown.approach_score: 0.264

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.480
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.847
- **Median Q (composite search score)**: 0.050
- **K-run variance**: 0.0186
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.204


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36073,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.06016,"contact_peg.contact_force":6.32333,"contact_peg.contact_speed":0.02733,"descend_to_height.descend_speed":0.02917,"push_channel.push_distance":0.14258,"push_channel.push_speed":0.07628},"optimized_scores":{"best_composite_score":-0.03157,"best_fitness_score":0.15843,"best_task_score":0.12378},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":201.0,"contact_point_centroid":[0.53257,0.11982,0.05982],"force_p95":418.24444,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":930.26968,"mean_force":235.39826,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50521,0.08774,0.04447]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":819.0,"contact_point_centroid":[0.47496,0.11993,0.05986],"force_p95":603.91736,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":875.11864,"mean_force":407.89235,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51329,0.08833,0.04295]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":868.0,"contact_point_centroid":[0.52504,0.08982,0.04512],"force_p95":473.10808,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":671.70468,"mean_force":274.81575,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51335,0.08792,0.04381]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":784.0,"contact_point_centroid":[0.52512,0.082,0.04949],"force_p95":376.85709,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":654.02757,"mean_force":314.06128,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51321,0.08094,0.04926]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":614.0,"contact_point_centroid":[0.47494,0.11991,0.05508],"force_p95":573.93983,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":588.63679,"mean_force":489.49068,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51329,0.0806,0.04894]},{"body_a":"world","body_b":"link7","contact_count":838.0,"contact_point_centroid":[0.50434,0.1437,-6e-05],"force_p95":318.43243,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":450.82621,"mean_force":208.09709,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51316,0.08047,0.04919]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":138.0,"contact_point_centroid":[0.52505,0.11487,0.05998],"force_p95":394.6556,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":405.69879,"mean_force":356.80555,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.50974,0.11496,0.05185]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50373,0.14502,-3e-05],"force_p95":253.81674,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.79633,"mean_force":213.15598,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51329,0.08222,0.04692]},{"body_a":"attachment","body_b":"peg","contact_count":377.0,"contact_point_centroid":[0.5059,0.07951,0.05901],"force_p95":2.20819,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.18469,"mean_force":0.95975,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51218,0.08074,0.04963]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50496,0.0557,0.00963],"force_p95":1.24668,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.63674,"mean_force":0.77888,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51132,0.08319,0.0481]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.11527,0.06],"force_p95":36.69226,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.69226,"mean_force":36.69226,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50879,0.11538,0.04918]},{"body_a":"attachment","body_b":"peg","contact_count":92.0,"contact_point_centroid":[0.50858,0.07099,0.0595],"force_p95":3.51722,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.07507,"mean_force":2.27364,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51422,0.08011,0.05453]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52504,0.04655,0.06],"force_p95":32.67997,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.83877,"mean_force":24.92299,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51495,0.07353,0.05965]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":170.0,"contact_point_centroid":[0.52525,0.06364,0.03836],"force_p95":4.05788,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.72176,"mean_force":0.85524,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50698,0.08494,0.04553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":979.0,"contact_point_centroid":[0.50669,0.05698,0.00941],"force_p95":1.09465,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.62072,"mean_force":0.64338,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51342,0.08413,0.0458]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.50561,0.08084,0.00935],"force_p95":0.56155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58491,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51415,0.15798,0.19807]}],"total_contact_groups":19},"final_pose_error":0.06176,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50659,0.01564,0.02375],"final_tcp_position":[0.51001,-0.03339,0.10074],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":930.26968,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54639,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":436.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52861,0.11955,0.10665],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":368.99454,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":403.0,"raw_peak_contact_force":405.69879,"tcp_end":[0.50879,0.11538,0.04918],"tcp_start":[0.52861,0.11955,0.10665],"tcp_to_object_dist_end":0.03787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":36.69226,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":36.69226,"subtask_id":"contact","tcp_end":[0.50877,0.11538,0.04914],"tcp_start":[0.50879,0.11538,0.04918],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,0.06082,0.03377],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.14112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03607,"peak_contact_force":520.92983,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3968.0,"raw_peak_contact_force":930.26968,"subtask_id":"push","tcp_end":[0.5133,0.08225,0.04688],"tcp_start":[0.50877,0.11538,0.04914],"tcp_to_object_dist_end":0.02594,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50659,0.01564,0.02375],"object_pos_start":[0.50682,0.06082,0.03377],"object_to_goal_dist_end":0.09724,"object_to_goal_dist_start":0.14112,"object_z_max":0.04083,"peak_contact_force":0.25468,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2766.0,"raw_peak_contact_force":875.11864,"tcp_end":[0.51001,-0.03339,0.10074],"tcp_start":[0.5133,0.08225,0.04688],"tcp_to_object_dist_end":0.09134,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14583,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.03435,"contact_peg.contact_force":7.58958,"contact_peg.contact_speed":0.02465,"descend_to_height.descend_speed":0.07001,"push_channel.push_distance":0.11692,"push_channel.push_speed":0.05487},"optimized_scores":{"best_composite_score":0.04971,"best_fitness_score":0.23971,"best_task_score":0.31728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.55491,0.11977,0.05947],"force_p95":762.63224,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":844.98194,"mean_force":405.41213,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51057,0.12986,0.0218]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":769.0,"contact_point_centroid":[0.52502,0.11996,0.05591],"force_p95":318.23027,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":658.65574,"mean_force":131.60223,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51977,0.1207,0.04547]},{"body_a":"world","body_b":"link7","contact_count":915.0,"contact_point_centroid":[0.5044,0.18388,-7e-05],"force_p95":445.50743,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":647.4386,"mean_force":266.58804,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51919,0.12064,0.04438]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.5139,0.11937,0.00954],"force_p95":464.8652,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":480.69428,"mean_force":286.92314,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50227,0.12123,0.01036]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.46743,0.11992,0.05968],"force_p95":378.4395,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":379.13253,"mean_force":335.15074,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51411,0.07407,0.05717]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":955.0,"contact_point_centroid":[0.52502,0.11953,0.05997],"force_p95":284.23477,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.32034,"mean_force":185.4551,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.52059,0.12157,0.05136]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50465,0.18472,-3e-05],"force_p95":134.11038,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.36754,"mean_force":92.37872,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.52238,0.12042,0.04841]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50579,0.12061,0.04377],"force_p95":60.10211,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.39788,"mean_force":54.85005,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50517,0.13251,0.04334]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.50547,0.00866,0.00816],"force_p95":0.74524,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.39251,"mean_force":0.87991,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51879,0.12078,0.04368]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":50.0,"contact_point_centroid":[0.5255,0.05306,0.0246],"force_p95":9.53628,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.54108,"mean_force":2.49226,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51453,0.12302,0.03781]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50631,0.00814,0.00807],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.60897,"mean_force":0.64857,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.52034,0.12086,0.05149]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.525,0.0331,0.02422],"force_p95":9.05571,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.16108,"mean_force":2.77507,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.52009,0.12251,0.05177]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47464,0.0302,0.03579],"force_p95":8.62322,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.78734,"mean_force":2.33969,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50585,0.12605,0.01363]},{"body_a":"peg","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.50495,0.09969,0.00936],"force_p95":5.63991,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.37004,"mean_force":1.17285,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50456,0.13476,0.04619]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50572,0.12251,0.04936],"force_p95":7.74634,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.24502,"mean_force":3.09242,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5042,0.13448,0.04544]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50541,0.10464,0.00936],"force_p95":0.5824,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57566,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50893,0.1693,0.19943]}],"total_contact_groups":18},"final_pose_error":0.17353,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50668,0.00875,0.02414],"final_tcp_position":[0.51413,0.07215,0.05777],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":844.98194,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.52996,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":417.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51863,0.14106,0.10801],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":142.0,"n_steps_budget":690.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.50594,0.10472,0.03384],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.54353,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":142.0,"raw_peak_contact_force":0.57724,"tcp_end":[0.5058,0.13545,0.0485],"tcp_start":[0.51863,0.14106,0.10801],"tcp_to_object_dist_end":0.03406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":23.0,"n_steps_budget":600.0,"object_pos_end":[0.50573,0.10412,0.03401],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.18431,"object_to_goal_dist_start":0.18492,"object_z_max":0.03394,"peak_contact_force":8.37004,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":28.0,"raw_peak_contact_force":8.37004,"subtask_id":"contact","tcp_end":[0.50382,0.13386,0.04422],"tcp_start":[0.5058,0.13545,0.0485],"tcp_to_object_dist_end":0.03149,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,0.0081,0.02415],"object_pos_start":[0.50573,0.10412,0.03401],"object_to_goal_dist_end":0.08972,"object_to_goal_dist_start":0.18431,"object_z_max":0.04578,"peak_contact_force":244.7363,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2751.0,"raw_peak_contact_force":844.98194,"subtask_id":"push","tcp_end":[0.52233,0.12037,0.0484],"tcp_start":[0.50382,0.13386,0.04422],"tcp_to_object_dist_end":0.116,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50668,0.00875,0.02414],"object_pos_start":[0.50607,0.0081,0.02415],"object_to_goal_dist_end":0.09041,"object_to_goal_dist_start":0.08972,"object_z_max":0.02452,"peak_contact_force":227.577,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1983.0,"raw_peak_contact_force":379.13253,"tcp_end":[0.51413,0.07215,0.05777],"tcp_start":[0.52233,0.12037,0.0484],"tcp_to_object_dist_end":0.07215,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61828,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.071,"contact_peg.contact_force":3.01231,"contact_peg.contact_speed":0.02483,"descend_to_height.descend_speed":0.05472,"push_channel.push_distance":0.12273,"push_channel.push_speed":0.07009},"optimized_scores":{"best_composite_score":0.28967,"best_fitness_score":0.47967,"best_task_score":0.84661},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":935.0,"contact_point_centroid":[0.5265,0.11959,0.05994],"force_p95":324.06094,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1395.47145,"mean_force":294.81629,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52768,0.07228,0.08701]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52601,0.08708,0.05953],"force_p95":1271.84352,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1315.89411,"mean_force":672.15584,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50364,0.08289,0.03766]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":292.0,"contact_point_centroid":[0.52501,0.11996,0.05995],"force_p95":137.45509,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.59177,"mean_force":114.02637,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.53351,0.06552,0.08877]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50477,0.08104,0.04915],"force_p95":55.83453,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.84231,"mean_force":23.23976,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50019,0.09222,0.03962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":898.0,"contact_point_centroid":[0.50421,-0.06595,0.0081],"force_p95":0.80706,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.27946,"mean_force":0.80448,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52864,0.07214,0.08842]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":50.0,"contact_point_centroid":[0.52661,0.0072,0.03485],"force_p95":4.8197,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.14684,"mean_force":1.0249,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.505,0.08006,0.04979]},{"body_a":"peg","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.50186,0.06459,0.00937],"force_p95":1.49444,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.10861,"mean_force":0.8028,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49735,0.09796,0.04433]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.5023,0.08528,0.05395],"force_p95":5.32709,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.61108,"mean_force":2.23533,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49698,0.09709,0.04268]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.50299,0.06746,0.00932],"force_p95":0.58217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56789,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49923,0.15277,0.2004]},{"body_a":"peg","body_b":"channel_base_body","contact_count":580.0,"contact_point_centroid":[0.50334,-0.06797,0.00808],"force_p95":0.60595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60595,"mean_force":0.60595,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.52497,0.03075,0.09924]},{"body_a":"peg","body_b":"channel_base_body","contact_count":151.0,"contact_point_centroid":[0.5032,0.06729,0.00938],"force_p95":0.55054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54663,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.49843,0.10316,0.07741]}],"total_contact_groups":11},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50296,-0.068,0.02417],"final_tcp_position":[0.50257,-0.06255,0.13112],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":1395.47145,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55056,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":405.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49971,0.10729,0.10656],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":151.0,"n_steps_budget":840.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54468,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":151.0,"raw_peak_contact_force":0.55115,"tcp_end":[0.49863,0.09928,0.04764],"tcp_start":[0.49971,0.10729,0.10656],"tcp_to_object_dist_end":0.03496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":40.0,"n_steps_budget":600.0,"object_pos_end":[0.50285,0.06699,0.03416],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.14714,"object_to_goal_dist_start":0.14764,"object_z_max":0.03411,"peak_contact_force":4.33808,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":45.0,"raw_peak_contact_force":6.10861,"subtask_id":"contact","tcp_end":[0.49687,0.09649,0.04167],"tcp_start":[0.49863,0.09928,0.04764],"tcp_to_object_dist_end":0.03102,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":967.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,-0.06795,0.02417],"object_pos_start":[0.50285,0.06699,0.03416],"object_to_goal_dist_end":0.02025,"object_to_goal_dist_start":0.14714,"object_z_max":0.04697,"peak_contact_force":288.51393,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1909.0,"raw_peak_contact_force":1395.47145,"subtask_id":"push","tcp_end":[0.53513,0.07382,0.08917],"tcp_start":[0.49687,0.09649,0.04167],"tcp_to_object_dist_end":0.15909,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.50296,-0.068,0.02417],"object_pos_start":[0.50377,-0.06795,0.02417],"object_to_goal_dist_end":0.02009,"object_to_goal_dist_start":0.02025,"object_z_max":0.02417,"peak_contact_force":0.60595,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":872.0,"raw_peak_contact_force":161.59177,"tcp_end":[0.50257,-0.06255,0.13112],"tcp_start":[0.53513,0.07382,0.08917],"tcp_to_object_dist_end":0.10709,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```