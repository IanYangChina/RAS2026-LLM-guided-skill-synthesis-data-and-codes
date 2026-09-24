## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0242 | 0.34 | ❌ rejected |
| 8 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0994 | 0.42 | ✅ accepted |
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0565 | 0.07 | ❌ rejected |
| 6 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0422 | 0.29 | ❌ rejected |
| 5 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0424 | 0.33 | ❌ rejected |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.024) — your mutation base

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

- **Composite score**: 0.024
- **task_score** (E): 0.341
- **fitness_score**: 0.264  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.2094 |
| descend_to_height | 1.00 | 1.00 | 0.0594 |
| contact_peg | 1.00 | 1.00 | 0.0089 |
| push_channel | 0.00 | 0.67 | 0.0003 |
| retract_lift | 1.00 | 1.00 | 0.1669 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.123, 0.107) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.542 | 3.242 |
| descend_to_height | descend | 1.00 / step_budget | (0.516, 0.123, 0.107)→(0.505, 0.117, 0.049) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 1.333 | 121.592 | 132.962 |
| contact_peg | contact | 1.00 / force_exceeded | (0.505, 0.117, 0.049)→(0.502, 0.113, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.035) | 0.164→0.164 | 1.00 / 2.000 | 10.051 | 18.085 |
| push_channel | push | 0.00 / guard_failure | (0.495, 0.074, 0.035)→(0.495, 0.074, 0.035) | (0.505, 0.084, 0.035)→(0.500, 0.041, 0.038) | 0.164→0.121 | 0.67 / 1.000 | 0.955 | 330.477 |
| retract_lift | retract | 1.00 / step_budget | (0.495, 0.074, 0.035)→(0.497, -0.066, 0.126) | (0.499, 0.039, 0.038)→(0.502, -0.018, 0.024) | 0.120→0.064 | 1.00 / 1.000 | 0.662 | 59.257 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.584
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.584
- phase_score: 0.235
- phase_breakdown.contact_score: 0.815
- phase_breakdown.push_score: 0.032
- phase_breakdown.approach_score: 0.263

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.374
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.584
- **Median Q (composite search score)**: 0.002
- **K-run variance**: 0.0068
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4717,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.11655,"contact_peg.contact_force":10.21949,"contact_peg.contact_speed":0.0324,"descend_to_height.descend_speed":0.04897,"push_channel.push_distance":0.13688,"push_channel.push_lateral_offset":-0.02112,"push_channel.push_speed":0.05257},"optimized_scores":{"best_composite_score":-0.06379,"best_fitness_score":0.17621,"best_task_score":0.14872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.555,0.05294,0.05998],"force_p95":472.79083,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":518.21343,"mean_force":205.21477,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49591,0.06238,0.03441]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":158.0,"contact_point_centroid":[0.52504,0.11585,0.05999],"force_p95":387.00961,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":397.75721,"mean_force":353.74689,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.51097,0.11592,0.05553]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.555,0.05207,0.05999],"force_p95":56.00744,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.79142,"mean_force":48.95161,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49605,0.05971,0.03443]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.50457,0.07444,0.05244],"force_p95":27.81382,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.97697,"mean_force":6.38813,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49862,0.08576,0.03582]},{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.50686,0.05005,0.00957],"force_p95":23.44136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.73967,"mean_force":4.27005,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49961,0.08926,0.03688]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.11632,0.06],"force_p95":34.23273,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.23273,"mean_force":34.23273,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50982,0.11641,0.05225]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52528,0.06897,0.04544],"force_p95":4.73526,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.62107,"mean_force":1.61062,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49991,0.09874,0.03646]},{"body_a":"peg","body_b":"channel_base_body","contact_count":69.0,"contact_point_centroid":[0.5061,0.08021,0.00938],"force_p95":0.83378,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.6793,"mean_force":0.91885,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50752,0.11379,0.04723]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50617,0.09871,0.04443],"force_p95":12.50568,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.14059,"mean_force":6.69243,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50555,0.11066,0.04229]},{"body_a":"peg","body_b":"channel_base_body","contact_count":420.0,"contact_point_centroid":[0.50018,-0.0084,0.00848],"force_p95":3.02806,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.51876,"mean_force":0.89405,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49505,-0.00492,0.07978]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52506,0.01007,0.02439],"force_p95":9.06753,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.15946,"mean_force":2.30111,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49553,-0.0323,0.09988]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49588,0.03414,0.04237],"force_p95":7.73564,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.91134,"mean_force":3.70017,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49442,0.04584,0.0428]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50555,0.08091,0.00935],"force_p95":0.56235,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58714,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51435,0.15765,0.19726]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50048,0.19741,0.29374]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.4746,0.0078,0.0592],"force_p95":1.23701,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31903,"mean_force":0.32321,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49516,0.0541,0.03761]},{"body_a":"peg","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.50598,0.08081,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.51505,0.11622,0.06759]}],"total_contact_groups":16},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50271,-0.01432,0.02423],"final_tcp_position":[0.49668,-0.06677,0.12564],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":518.21343,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55009,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":414.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52866,0.1195,0.10653],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":269.0,"n_steps_budget":990.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":363.68377,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":427.0,"raw_peak_contact_force":397.75721,"tcp_end":[0.50982,0.11641,0.05225],"tcp_start":[0.52866,0.1195,0.10653],"tcp_to_object_dist_end":0.04022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":69.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08046,0.03391],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16069,"object_to_goal_dist_start":0.16113,"object_z_max":0.03383,"peak_contact_force":13.6793,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":74.0,"raw_peak_contact_force":34.23273,"subtask_id":"contact","tcp_end":[0.50545,0.11043,0.04195],"tcp_start":[0.50982,0.11641,0.05225],"tcp_to_object_dist_end":0.03103,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":93.0,"n_steps_budget":1000.0,"object_pos_end":[0.49726,0.02666,0.03619],"object_pos_start":[0.50596,0.08046,0.03391],"object_to_goal_dist_end":0.10676,"object_to_goal_dist_start":0.16069,"object_z_max":0.03972,"peak_contact_force":0.97789,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":105.0,"raw_peak_contact_force":518.21343,"subtask_id":"push","tcp_end":[0.49606,0.06107,0.03455],"tcp_start":[0.49595,0.06136,0.03451],"tcp_to_object_dist_end":0.03447,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.50271,-0.01432,0.02423],"object_pos_start":[0.49659,0.02542,0.03638],"object_to_goal_dist_end":0.0676,"object_to_goal_dist_start":0.10554,"object_z_max":0.04078,"peak_contact_force":0.57212,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":483.0,"raw_peak_contact_force":56.79142,"tcp_end":[0.49668,-0.06677,0.12564],"tcp_start":[0.49606,0.06107,0.03455],"tcp_to_object_dist_end":0.11433,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47879,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.09222,"contact_peg.contact_force":7.69168,"contact_peg.contact_speed":0.02299,"descend_to_height.descend_speed":0.05196,"push_channel.push_distance":0.15556,"push_channel.push_lateral_offset":-0.01394,"push_channel.push_speed":0.05768},"optimized_scores":{"best_composite_score":0.00192,"best_fitness_score":0.24192,"best_task_score":0.2916},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.555,0.06724,0.06],"force_p95":409.4416,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":427.63767,"mean_force":245.67694,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49622,0.0694,0.03547]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.555,0.06632,0.06],"force_p95":61.69204,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.0904,"mean_force":58.10685,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49628,0.06771,0.03548]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52552,0.08284,0.05197],"force_p95":28.3124,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.41665,"mean_force":4.95321,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49841,0.11379,0.03741]},{"body_a":"attachment","body_b":"peg","contact_count":44.0,"contact_point_centroid":[0.50355,0.09256,0.04945],"force_p95":30.26281,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.97295,"mean_force":7.80472,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49808,0.10382,0.03722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":47.0,"contact_point_centroid":[0.50643,0.07405,0.00958],"force_p95":24.42667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.03661,"mean_force":5.28332,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49942,0.11745,0.03885]},{"body_a":"peg","body_b":"channel_base_body","contact_count":27.0,"contact_point_centroid":[0.50645,0.09565,0.00943],"force_p95":10.7148,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.29797,"mean_force":2.17916,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50449,0.13452,0.04579]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50544,0.12208,0.04742],"force_p95":11.87167,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.03486,"mean_force":9.24929,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50404,0.13406,0.04471]},{"body_a":"peg","body_b":"channel_base_body","contact_count":427.0,"contact_point_centroid":[0.49816,-0.01093,0.00829],"force_p95":0.99501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.34112,"mean_force":0.67604,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49513,-0.00199,0.08094]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47497,0.00834,0.0241],"force_p95":7.63348,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.06148,"mean_force":2.14806,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49415,0.02695,0.06036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50553,0.10474,0.00936],"force_p95":0.58322,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57749,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50911,0.169,0.19841]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50014,0.19829,0.29479]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47418,0.04333,0.02283],"force_p95":1.56098,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76181,"mean_force":0.57261,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49663,0.0783,0.03575]},{"body_a":"peg","body_b":"channel_base_body","contact_count":145.0,"contact_point_centroid":[0.50608,0.10448,0.00939],"force_p95":0.57515,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54628,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.51193,0.13798,0.07861]}],"total_contact_groups":13},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50074,-0.01395,0.02415],"final_tcp_position":[0.49671,-0.06631,0.12588],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":427.63767,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10461,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53281,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":395.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.5187,0.141,0.1078],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":145.0,"n_steps_budget":900.0,"object_pos_end":[0.50591,0.10456,0.03383],"object_pos_start":[0.50599,0.10461,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18481,"object_z_max":0.03384,"peak_contact_force":0.54297,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":145.0,"raw_peak_contact_force":0.57865,"tcp_end":[0.50584,0.13535,0.04842],"tcp_start":[0.5187,0.141,0.1078],"tcp_to_object_dist_end":0.03407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":27.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.10371,0.03471],"object_pos_start":[0.50591,0.10456,0.03383],"object_to_goal_dist_end":0.18388,"object_to_goal_dist_start":0.18476,"object_z_max":0.03462,"peak_contact_force":8.74826,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":32.0,"raw_peak_contact_force":12.29797,"subtask_id":"contact","tcp_end":[0.50371,0.13346,0.04355],"tcp_start":[0.50584,0.13535,0.04842],"tcp_to_object_dist_end":0.03112,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":118.0,"n_steps_budget":1000.0,"object_pos_end":[0.49941,0.03222,0.0414],"object_pos_start":[0.50593,0.10371,0.03471],"object_to_goal_dist_end":0.11223,"object_to_goal_dist_start":0.18388,"object_z_max":0.04297,"peak_contact_force":0.0,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":142.0,"raw_peak_contact_force":427.63767,"subtask_id":"push","tcp_end":[0.49627,0.06838,0.03555],"tcp_start":[0.49621,0.06869,0.03554],"tcp_to_object_dist_end":0.03676,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.50074,-0.01395,0.02415],"object_pos_start":[0.49985,0.03052,0.04065],"object_to_goal_dist_end":0.06793,"object_to_goal_dist_start":0.11052,"object_z_max":0.04065,"peak_contact_force":0.6436,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":441.0,"raw_peak_contact_force":62.0904,"tcp_end":[0.49671,-0.06631,0.12588],"tcp_start":[0.49627,0.06838,0.03555],"tcp_to_object_dist_end":0.11448,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7483,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.0868,"contact_peg.contact_force":7.4458,"contact_peg.contact_speed":0.01899,"descend_to_height.descend_speed":0.07614,"push_channel.push_distance":0.13424,"push_channel.push_lateral_offset":-0.02507,"push_channel.push_speed":0.04929},"optimized_scores":{"best_composite_score":0.13448,"best_fitness_score":0.37448,"best_task_score":0.58374},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":452.0,"contact_point_centroid":[0.50342,-0.01855,0.00836],"force_p95":0.97051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.88819,"mean_force":0.75961,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49319,0.00535,0.08328]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.4977,0.0787,0.03934],"force_p95":50.22957,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.5007,"mean_force":16.28973,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49268,0.09022,0.03554]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53999,0.0851,0.05993],"force_p95":50.66825,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.84528,"mean_force":32.06826,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.4926,0.08742,0.03524]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.5068,0.05178,0.00968],"force_p95":27.25955,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.5807,"mean_force":4.38328,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49453,0.09576,0.03804]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.5003,0.08281,0.04743],"force_p95":39.29738,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.11267,"mean_force":12.34357,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4939,0.09446,0.0374]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52503,-0.04972,0.02394],"force_p95":7.22697,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.40084,"mean_force":1.99597,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49174,0.03361,0.06599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":54.0,"contact_point_centroid":[0.50231,0.05921,0.00944],"force_p95":6.36597,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.72544,"mean_force":1.21697,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49725,0.09746,0.04354]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.5018,0.08475,0.05119],"force_p95":7.24308,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.43013,"mean_force":4.9727,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49694,0.09657,0.04192]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.50309,0.06752,0.00932],"force_p95":0.58794,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5682,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49925,0.15281,0.20049]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47466,-0.01409,0.05841],"force_p95":1.13861,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24952,"mean_force":0.53634,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49104,0.06389,0.04763]},{"body_a":"peg","body_b":"channel_base_body","contact_count":145.0,"contact_point_centroid":[0.50314,0.06736,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54666,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.49853,0.10321,0.07756]}],"total_contact_groups":11},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50212,-0.02594,0.02404],"final_tcp_position":[0.49632,-0.06584,0.12662],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":58.88819,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54454,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":399.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49972,0.10739,0.10677],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":145.0,"n_steps_budget":630.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54804,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":145.0,"raw_peak_contact_force":0.55115,"tcp_end":[0.4987,0.09926,0.04776],"tcp_start":[0.49972,0.10739,0.10677],"tcp_to_object_dist_end":0.03504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":54.0,"n_steps_budget":630.0,"object_pos_end":[0.50319,0.06637,0.03505],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14649,"object_to_goal_dist_start":0.14758,"object_z_max":0.03503,"peak_contact_force":7.72544,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":62.0,"raw_peak_contact_force":7.72544,"subtask_id":"contact","tcp_end":[0.49684,0.09558,0.04031],"tcp_start":[0.4987,0.09926,0.04776],"tcp_to_object_dist_end":0.03035,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.50199,0.06327,0.03661],"object_pos_start":[0.50319,0.06637,0.03505],"object_to_goal_dist_end":0.14332,"object_to_goal_dist_start":0.14649,"object_z_max":0.03703,"peak_contact_force":1.88596,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":29.0,"raw_peak_contact_force":45.5807,"subtask_id":"push","tcp_end":[0.49269,0.09125,0.03583],"tcp_start":[0.49275,0.0915,0.03604],"tcp_to_object_dist_end":0.0295,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.50212,-0.02594,0.02404],"object_pos_start":[0.50195,0.06242,0.03742],"object_to_goal_dist_end":0.05641,"object_to_goal_dist_start":0.14246,"object_z_max":0.04174,"peak_contact_force":0.7703,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":478.0,"raw_peak_contact_force":58.88819,"tcp_end":[0.49632,-0.06584,0.12662],"tcp_start":[0.49269,0.09125,0.03583],"tcp_to_object_dist_end":0.11022,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```