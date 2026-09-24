## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | -0.3112 | 0.25 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1026 | 0.43 | ✅ accepted |
| 10 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.0053 | 0.35 | ❌ rejected |
| 9 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0242 | 0.34 | ❌ rejected |
| 8 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0994 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.311) — your mutation base

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

- **Composite score**: -0.311
- **task_score** (E): 0.253
- **fitness_score**: 0.203  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.056
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1770 |
| descend_to_back | 0.33 | 1.00 | 0.0813 |
| align_x | 1.00 | 1.00 | 0.0152 |
| contact_peg | 0.67 | 1.00 | 0.0251 |
| push_channel | 0.00 | 1.00 | 0.0008 |
| retract_lift | 1.00 | 1.00 | 0.1812 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.133, 0.137) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.546 | 3.242 |
| descend_to_back | descend | 0.33 / step_budget | (0.498, 0.133, 0.137)→(0.483, 0.124, 0.058) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.333 | 24.924 | 24.934 |
| align_x | align | 1.00 / step_budget | (0.483, 0.124, 0.058)→(0.496, 0.124, 0.051) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.545 | 97.260 |
| contact_peg | contact | 0.67 / step_budget | (0.496, 0.124, 0.051)→(0.499, 0.099, 0.048) | (0.505, 0.084, 0.034)→(0.506, 0.072, 0.038) | 0.165→0.152 | 1.00 / 2.667 | 2.561 | 4.813 |
| push_channel | push | 0.00 / guard_failure | (0.500, 0.098, 0.048)→(0.500, 0.098, 0.048) | (0.506, 0.072, 0.038)→(0.507, 0.071, 0.038) | 0.152→0.151 | 1.00 / 1.667 | 2.302 | 131.151 |
| retract_lift | retract | 1.00 / step_budget | (0.500, 0.098, 0.048)→(0.497, -0.065, 0.127) | (0.507, 0.070, 0.038)→(0.505, 0.019, 0.024) | 0.150→0.101 | 1.00 / 1.000 | 0.583 | 26.300 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.426
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.426
- phase_score: 0.210
- phase_breakdown.contact_score: 0.805
- phase_breakdown.push_score: 0.036
- phase_breakdown.approach_score: 0.137

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.297
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.426
- **Median Q (composite search score)**: -0.391
- **K-run variance**: 0.0212
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.322


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32759,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_x.align_speed":0.04365,"approach_above.approach_speed":0.08705,"contact_peg.contact_force":8.3849,"contact_peg.contact_speed":0.01798,"descend_to_back.descend_force":10.17647,"descend_to_back.descend_speed":0.06667,"push_channel.push_distance":0.19565,"push_channel.push_force_threshold":29.76064,"push_channel.push_speed":0.07798},"optimized_scores":{"best_composite_score":-0.43636,"best_fitness_score":0.13364,"best_task_score":0.11946},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50413,0.08076,0.04758],"force_p95":157.6941,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.8903,"mean_force":141.09387,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50144,0.09222,0.04845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50716,0.05308,0.00996],"force_p95":111.86848,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.56624,"mean_force":89.21152,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50144,0.09222,0.04845]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52506,0.06158,0.05223],"force_p95":93.21423,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.63773,"mean_force":88.1115,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50144,0.09222,0.04845]},{"body_a":"attachment","body_b":"peg","contact_count":56.0,"contact_point_centroid":[0.50322,0.06897,0.05042],"force_p95":24.12767,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.40268,"mean_force":9.53467,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49947,0.07994,0.05162]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50633,0.02426,0.00853],"force_p95":12.19311,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.31688,"mean_force":1.63083,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49794,0.01074,0.08685]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":56.0,"contact_point_centroid":[0.52523,0.06086,0.0265],"force_p95":16.49143,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.5153,"mean_force":6.0609,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49989,0.08205,0.05101]},{"body_a":"attachment","body_b":"peg","contact_count":638.0,"contact_point_centroid":[0.50285,0.08961,0.05051],"force_p95":4.44816,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.79646,"mean_force":2.63922,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49844,0.10107,0.04759]},{"body_a":"peg","body_b":"channel_base_body","contact_count":317.0,"contact_point_centroid":[0.50546,0.08086,0.00934],"force_p95":0.57698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59489,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50508,0.16279,0.21253]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":454.0,"contact_point_centroid":[0.52507,0.07022,0.04441],"force_p95":3.42108,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.04993,"mean_force":2.30212,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49921,0.09865,0.04785]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49997,0.19741,0.29399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":877.0,"contact_point_centroid":[0.50747,0.06453,0.00981],"force_p95":2.74512,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.18374,"mean_force":1.61157,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49755,0.10462,0.04747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":358.0,"contact_point_centroid":[0.50607,0.08088,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_to_back","phase_type":"descend","tcp_position_centroid":[0.49715,0.12517,0.09703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":116.0,"contact_point_centroid":[0.50571,0.08086,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54675,"phase_index":2.0,"phase_name":"align_x","phase_type":"align","tcp_position_centroid":[0.49029,0.12042,0.05367]}],"total_contact_groups":13},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50646,0.01749,0.0242],"final_tcp_position":[0.4971,-0.06517,0.12724],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":159.8903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54513,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":353.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.51078,0.12981,0.13677],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":358.0,"n_steps_budget":840.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"descend_to_back","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":358.0,"raw_peak_contact_force":0.55023,"tcp_end":[0.48509,0.12103,0.0586],"tcp_start":[0.51078,0.12981,0.13677],"tcp_to_object_dist_end":0.05162,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":116.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"align_x","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":116.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.49662,0.12008,0.05051],"tcp_start":[0.48509,0.12103,0.0586],"tcp_to_object_dist_end":0.04362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,0.06507,0.03837],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.14524,"object_to_goal_dist_start":0.16113,"object_z_max":0.03837,"peak_contact_force":3.38126,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1969.0,"raw_peak_contact_force":4.79646,"subtask_id":"contact","tcp_end":[0.50122,0.09246,0.04856],"tcp_start":[0.49662,0.12008,0.05051],"tcp_to_object_dist_end":0.0298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50707,0.06492,0.03837],"object_pos_start":[0.50702,0.06507,0.03837],"object_to_goal_dist_end":0.1451,"object_to_goal_dist_start":0.14524,"object_z_max":0.03838,"peak_contact_force":1.42411,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":159.8903,"subtask_id":"push","tcp_end":[0.50215,0.09149,0.04803],"tcp_start":[0.50171,0.09194,0.0483],"tcp_to_object_dist_end":0.02869,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.50646,0.01749,0.0242],"object_pos_start":[0.50734,0.06426,0.0384],"object_to_goal_dist_end":0.09897,"object_to_goal_dist_start":0.14446,"object_z_max":0.04077,"peak_contact_force":0.57871,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":566.0,"raw_peak_contact_force":26.40268,"tcp_end":[0.4971,-0.06517,0.12724],"tcp_start":[0.50215,0.09149,0.04803],"tcp_to_object_dist_end":0.13243,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52976,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_x.align_speed":0.07568,"approach_above.approach_speed":0.07767,"contact_peg.contact_force":10.53661,"contact_peg.contact_speed":0.0332,"descend_to_back.descend_force":8.88174,"descend_to_back.descend_speed":0.06121,"push_channel.push_distance":0.15631,"push_channel.push_force_threshold":30.74086,"push_channel.push_speed":0.06396},"optimized_scores":{"best_composite_score":-0.39057,"best_fitness_score":0.17943,"best_task_score":0.21307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50439,0.10492,0.04744],"force_p95":163.24587,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.96995,"mean_force":135.64572,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50133,0.11637,0.0484]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50803,0.07815,0.00997],"force_p95":111.57205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.92149,"mean_force":93.0668,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50133,0.11637,0.0484]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52538,0.08731,0.04484],"force_p95":103.16992,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.16902,"mean_force":83.67434,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50133,0.11637,0.0484]},{"body_a":"attachment","body_b":"peg","contact_count":56.0,"contact_point_centroid":[0.50354,0.09224,0.05007],"force_p95":27.00432,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.24753,"mean_force":12.74413,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49959,0.10316,0.05129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":504.0,"contact_point_centroid":[0.50682,0.04713,0.00848],"force_p95":13.61766,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.42325,"mean_force":1.91675,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49797,0.02261,0.08719]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":74.0,"contact_point_centroid":[0.52538,0.08182,0.02889],"force_p95":16.09931,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.86445,"mean_force":6.9235,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49982,0.10267,0.05174]},{"body_a":"attachment","body_b":"peg","contact_count":328.0,"contact_point_centroid":[0.50263,0.1134,0.04898],"force_p95":6.11026,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.901,"mean_force":3.67138,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49846,0.12478,0.04746]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":236.0,"contact_point_centroid":[0.52512,0.09512,0.0392],"force_p95":4.83065,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77686,"mean_force":2.99424,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49915,0.12252,0.04773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":472.0,"contact_point_centroid":[0.50743,0.0895,0.00978],"force_p95":4.19633,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.70696,"mean_force":2.25135,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49757,0.12895,0.04741]},{"body_a":"peg","body_b":"channel_base_body","contact_count":300.0,"contact_point_centroid":[0.50553,0.10469,0.00936],"force_p95":0.60165,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58401,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50002,0.17402,0.21378]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49969,0.1983,0.29486]},{"body_a":"peg","body_b":"channel_base_body","contact_count":386.0,"contact_point_centroid":[0.50574,0.10468,0.00939],"force_p95":0.57551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54639,"phase_index":1.0,"phase_name":"descend_to_back","phase_type":"descend","tcp_position_centroid":[0.49148,0.14725,0.09737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":127.0,"contact_point_centroid":[0.5058,0.1043,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57589,"mean_force":0.5462,"phase_index":2.0,"phase_name":"align_x","phase_type":"align","tcp_position_centroid":[0.48987,0.14373,0.05331]}],"total_contact_groups":13},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50683,0.04073,0.0241],"final_tcp_position":[0.49709,-0.06446,0.12786],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":164.96995,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54457,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":332.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.50112,0.15096,0.13824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":900.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.50592,0.10457,0.03384],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":0.54982,"phase_name":"descend_to_back","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":386.0,"raw_peak_contact_force":0.57941,"tcp_end":[0.48388,0.14422,0.05838],"tcp_start":[0.50112,0.15096,0.13824],"tcp_to_object_dist_end":0.05153,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":127.0,"n_steps_budget":600.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":0.54261,"phase_name":"align_x","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":127.0,"raw_peak_contact_force":0.57589,"tcp_end":[0.49682,0.14356,0.05018],"tcp_start":[0.48388,0.14422,0.05838],"tcp_to_object_dist_end":0.0431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50747,0.08931,0.03871],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.16948,"object_to_goal_dist_start":0.18491,"object_z_max":0.0387,"peak_contact_force":3.35835,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1036.0,"raw_peak_contact_force":6.901,"subtask_id":"contact","tcp_end":[0.50102,0.11664,0.0485],"tcp_start":[0.49682,0.14356,0.05018],"tcp_to_object_dist_end":0.02974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50763,0.08907,0.03875],"object_pos_start":[0.50747,0.08931,0.03871],"object_to_goal_dist_end":0.16925,"object_to_goal_dist_start":0.16948,"object_z_max":0.03879,"peak_contact_force":1.4237,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":164.96995,"subtask_id":"push","tcp_end":[0.50221,0.11561,0.04801],"tcp_start":[0.50169,0.11606,0.04827],"tcp_to_object_dist_end":0.02862,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,0.04073,0.0241],"object_pos_start":[0.50796,0.08829,0.03884],"object_to_goal_dist_end":0.12197,"object_to_goal_dist_start":0.16849,"object_z_max":0.0408,"peak_contact_force":0.63693,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":634.0,"raw_peak_contact_force":31.24753,"tcp_end":[0.49709,-0.06446,0.12786],"tcp_start":[0.50221,0.11561,0.04801],"tcp_to_object_dist_end":0.14808,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23636,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_x.align_speed":0.05769,"approach_above.approach_speed":0.11405,"contact_peg.contact_force":10.15725,"contact_peg.contact_speed":0.00982,"descend_to_back.descend_force":10.70296,"descend_to_back.descend_speed":0.10042,"push_channel.push_distance":0.11481,"push_channel.push_force_threshold":29.58484,"push_channel.push_speed":0.07513},"optimized_scores":{"best_composite_score":-0.10679,"best_fitness_score":0.29654,"best_task_score":0.42634},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47497,0.11657,0.05993],"force_p95":266.61905,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.65435,"mean_force":128.89277,"phase_index":2.0,"phase_name":"align_x","phase_type":"align","tcp_position_centroid":[0.48187,0.10791,0.05708]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47497,0.11894,0.05993],"force_p95":73.67373,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.67373,"mean_force":73.67373,"phase_index":1.0,"phase_name":"descend_to_back","phase_type":"descend","tcp_position_centroid":[0.47916,0.10781,0.05834]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49975,0.07583,0.04638],"force_p95":62.14506,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.59155,"mean_force":25.59205,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49587,0.08707,0.04772]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50978,0.04638,0.00998],"force_p95":68.18621,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.18621,"mean_force":68.18621,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49555,0.08739,0.04782]},{"body_a":"attachment","body_b":"peg","contact_count":76.0,"contact_point_centroid":[0.50039,0.05252,0.0568],"force_p95":20.92445,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.25101,"mean_force":10.85088,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49429,0.06297,0.05609]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":103.0,"contact_point_centroid":[0.5253,0.04105,0.04203],"force_p95":18.59773,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.173,"mean_force":7.65296,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49474,0.068,0.05376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50513,0.01066,0.00887],"force_p95":5.1483,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.95872,"mean_force":1.04967,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49517,0.00531,0.08768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50625,0.05581,0.00973],"force_p95":1.37657,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.74208,"mean_force":0.89271,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49322,0.09523,0.0473]},{"body_a":"attachment","body_b":"peg","contact_count":602.0,"contact_point_centroid":[0.50027,0.08059,0.05449],"force_p95":1.06205,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.3273,"mean_force":0.73707,"phase_index":3.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49407,0.09199,0.04738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.50304,0.06738,0.00931],"force_p95":0.64418,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57263,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49051,0.15799,0.21551]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.5031,0.06746,0.00938],"force_p95":0.55063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55314,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_back","phase_type":"descend","tcp_position_centroid":[0.47951,0.1125,0.09614]},{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.50306,0.06746,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55081,"mean_force":0.54665,"phase_index":2.0,"phase_name":"align_x","phase_type":"align","tcp_position_centroid":[0.48647,0.10765,0.05471]}],"total_contact_groups":12},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50304,-0.00075,0.02413],"final_tcp_position":[0.49662,-0.06537,0.12698],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":290.65435,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54867,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":331.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.48239,0.11782,0.13679],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":395.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14765,"object_z_max":0.0338,"peak_contact_force":73.67373,"phase_name":"descend_to_back","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":396.0,"raw_peak_contact_force":73.67373,"tcp_end":[0.47917,0.10779,0.05819],"tcp_start":[0.48239,0.11782,0.13679],"tcp_to_object_dist_end":0.05283,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":117.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54632,"phase_name":"align_x","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":146.0,"raw_peak_contact_force":290.65435,"tcp_end":[0.49352,0.10698,0.05091],"tcp_start":[0.47917,0.10779,0.05819],"tcp_to_object_dist_end":0.04411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50493,0.06016,0.03709],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14027,"object_to_goal_dist_start":0.14761,"object_z_max":0.03709,"peak_contact_force":0.94397,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1602.0,"raw_peak_contact_force":2.74208,"subtask_id":"contact","tcp_end":[0.49555,0.08739,0.04782],"tcp_start":[0.49352,0.10698,0.05091],"tcp_to_object_dist_end":0.03073,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5052,0.05984,0.03734],"object_pos_start":[0.50493,0.06016,0.03709],"object_to_goal_dist_end":0.13996,"object_to_goal_dist_start":0.14027,"object_z_max":0.03743,"peak_contact_force":4.05796,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":68.59155,"subtask_id":"push","tcp_end":[0.49698,0.0859,0.04733],"tcp_start":[0.49626,0.08666,0.04758],"tcp_to_object_dist_end":0.0291,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,-0.00075,0.02413],"object_pos_start":[0.50617,0.05838,0.03738],"object_to_goal_dist_end":0.08088,"object_to_goal_dist_start":0.13854,"object_z_max":0.04077,"peak_contact_force":0.53262,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":605.0,"raw_peak_contact_force":21.25101,"tcp_end":[0.49662,-0.06537,0.12698],"tcp_start":[0.49698,0.0859,0.04733],"tcp_to_object_dist_end":0.12163,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```