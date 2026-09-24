## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → push → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.4227 | 0.00 | ❌ rejected |
| 12 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | -0.1435 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0528 | 0.09 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.1845 | 0.11 | ❌ rejected |
| 9 | approach → push → retract | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1857 | 0.02 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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

## Current Skill (Q=-0.423) — your mutation base

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
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.015
      - 0.015
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  subtask_id: approach
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.005
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
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
    - 0.02
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
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
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: push
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
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.005, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.005]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.423
- **task_score** (E): 0.000
- **fitness_score**: 0.114  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2687 |
| lateral_push_1 | 0.67 | 1.00 | 0.0000 |
| approach_1 | 1.00 | 1.00 | 0.0246 |
| contact_1 | 1.00 | 1.00 | 0.0000 |
| push_1 | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.529, 0.090, 0.059) | (0.517, 0.080, 0.040)→(0.502, 0.093, 0.027) | 0.162→0.174 | 1.00 / 1.333 | 108.289 | 324.061 |
| lateral_push_1 | push | 0.67 / step_budget | (0.529, 0.090, 0.059)→(0.529, 0.090, 0.059) | (0.502, 0.093, 0.027)→(0.502, 0.093, 0.027) | 0.174→0.174 | 1.00 / 1.333 | 108.517 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.523, 0.099, 0.056)→(0.528, 0.121, 0.046) | (0.501, 0.111, 0.024)→(0.502, 0.113, 0.024) | 0.192→0.194 | 1.00 / 2.000 | 254.228 | 308.143 |
| contact_1 | contact | 1.00 / force_exceeded | (0.528, 0.121, 0.046)→(0.528, 0.121, 0.046) | (0.502, 0.113, 0.024)→(0.502, 0.113, 0.024) | 0.194→0.194 | 1.00 / 2.000 | 90.852 | 90.852 |
| push_1 | push | 0.00 / guard_failure | (0.528, 0.121, 0.046)→(0.528, 0.121, 0.046) | (0.502, 0.113, 0.024)→(0.502, 0.113, 0.024) | 0.194→0.194 | 1.00 / 2.000 | 430.552 | 430.552 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.233
- phase_breakdown.approach_score: 0.476
- phase_breakdown.contact_score: 0.579
- phase_breakdown.push_score: 0.037

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.140
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.342
- **K-run variance**: 0.0151
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.363


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":53.0,"average_failure_rate":0.46087,"average_mean_iterations":94.38261,"average_solve_count":115.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.14383,"align_1.lateral_offset_x":-0.01125,"approach_1.approach_speed":0.07034,"contact_1.contact_force_threshold":15.5467,"contact_1.contact_speed":0.01516,"lateral_push_1.lateral_distance":0.02322,"lateral_push_1.lateral_speed":0.01967,"push_1.push_distance":0.06444,"push_1.push_speed":0.06768,"push_1.push_tolerance":0.02569,"retract_1.retract_speed":0.06673},"optimized_scores":{"best_composite_score":-0.34172,"best_fitness_score":0.12828,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":377.0,"contact_point_centroid":[0.55172,0.11999,0.05992],"force_p95":347.94597,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":382.66457,"mean_force":243.14356,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50328,0.14825,0.03255]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55496,0.11998,0.05987],"force_p95":362.38398,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":362.38398,"mean_force":362.38398,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51136,0.16398,0.02883]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55496,0.11998,0.05987],"force_p95":60.40257,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.40257,"mean_force":60.40257,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51134,0.16393,0.02885]},{"body_a":"attachment","body_b":"peg","contact_count":75.0,"contact_point_centroid":[0.50492,0.14438,0.03101],"force_p95":27.46359,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.674,"mean_force":15.03406,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49881,0.14179,0.03373]},{"body_a":"peg","body_b":"world","contact_count":562.0,"contact_point_centroid":[0.49709,0.15955,-0.00192],"force_p95":18.52702,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.82469,"mean_force":2.59635,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50149,0.14262,0.03474]},{"body_a":"peg","body_b":"world","contact_count":153.0,"contact_point_centroid":[0.49513,0.15383,-0.00151],"force_p95":1.15197,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.85269,"mean_force":0.63591,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50054,0.13015,0.07381]},{"body_a":"peg","body_b":"channel_base_body","contact_count":580.0,"contact_point_centroid":[0.49609,0.11942,0.00942],"force_p95":0.61701,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54501,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49933,0.16784,0.19526]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49963,0.19898,0.29747]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.49811,0.1878,-0.0021],"force_p95":0.69237,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69237,"mean_force":0.69237,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51134,0.16393,0.02885]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.49796,0.18782,-0.00209],"force_p95":0.6034,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6034,"mean_force":0.6034,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51136,0.16398,0.02883]}],"total_contact_groups":10},"final_pose_error":0.06858,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49871,0.1628,0.0138],"final_tcp_position":[0.51143,0.16412,0.02889],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":382.66457,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":761.0,"n_steps_budget":1000.0,"object_pos_end":[0.49528,0.16001,0.0141],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.24145,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49888,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":757.0,"raw_peak_contact_force":2.85269,"subtask_id":"approach","tcp_end":[0.50073,0.12221,0.04829],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.49528,0.16001,0.0141],"object_pos_start":[0.49528,0.16001,0.0141],"object_to_goal_dist_end":0.24145,"object_to_goal_dist_start":0.24145,"peak_contact_force":0.72533,"phase_name":"lateral_push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50073,0.12221,0.04829],"tcp_start":[0.50073,0.12221,0.04829],"tcp_to_object_dist_end":0.05126,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":562.0,"n_steps_budget":630.0,"object_pos_end":[0.49896,0.16287,0.01387],"object_pos_start":[0.49528,0.16001,0.0141],"object_to_goal_dist_end":0.24428,"object_to_goal_dist_start":0.24145,"object_z_max":0.01511,"peak_contact_force":275.32857,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1014.0,"raw_peak_contact_force":382.66457,"subtask_id":"approach","tcp_end":[0.51134,0.16393,0.02885],"tcp_start":[0.50073,0.12221,0.04829],"tcp_to_object_dist_end":0.01946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":840.0,"object_pos_end":[0.49883,0.16285,0.01384],"object_pos_start":[0.49896,0.16287,0.01387],"object_to_goal_dist_end":0.24426,"object_to_goal_dist_start":0.24428,"object_z_max":0.01387,"peak_contact_force":60.40257,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":60.40257,"subtask_id":"contact","tcp_end":[0.51136,0.16398,0.02883],"tcp_start":[0.51134,0.16393,0.02885],"tcp_to_object_dist_end":0.01957,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.49871,0.1628,0.0138],"object_pos_start":[0.49883,0.16285,0.01384],"object_to_goal_dist_end":0.24422,"object_to_goal_dist_start":0.24426,"object_z_max":0.01384,"peak_contact_force":362.38398,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":362.38398,"subtask_id":"push","tcp_end":[0.51143,0.16412,0.02889],"tcp_start":[0.51136,0.16398,0.02883],"tcp_to_object_dist_end":0.01978,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":33.0,"average_failure_rate":0.38372,"average_mean_iterations":79.30233,"average_solve_count":86.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.19967,"align_1.lateral_offset_x":-0.00655,"approach_1.approach_speed":0.06623,"contact_1.contact_force_threshold":13.59523,"contact_1.contact_speed":0.03084,"lateral_push_1.lateral_distance":0.0229,"lateral_push_1.lateral_speed":0.02862,"push_1.push_distance":0.12206,"push_1.push_speed":0.04861,"push_1.push_tolerance":0.01454,"retract_1.retract_speed":0.15344},"optimized_scores":{"best_composite_score":-0.33013,"best_fitness_score":0.13987,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.55499,0.07197,0.05992],"force_p95":498.72084,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":498.72084,"mean_force":498.72084,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5444,0.07708,0.0622]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":63.0,"contact_point_centroid":[0.55477,0.07654,0.05977],"force_p95":393.5446,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.78789,"mean_force":325.89324,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.54351,0.07708,0.06358]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":540.0,"contact_point_centroid":[0.55499,0.07204,0.05995],"force_p95":231.51092,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.62207,"mean_force":176.50971,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54435,0.07644,0.06321]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.55499,0.07186,0.05993],"force_p95":121.30147,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.30147,"mean_force":121.30147,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54444,0.07708,0.06221]},{"body_a":"peg","body_b":"channel_base_body","contact_count":799.0,"contact_point_centroid":[0.50584,0.06301,0.00937],"force_p95":0.55627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.5635,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52326,0.13168,0.16692]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50026,0.19764,0.2953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.506,0.06294,0.00938],"force_p95":0.55272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54658,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54435,0.07644,0.06321]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49862,0.04658,0.00938],"force_p95":0.54662,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54662,"mean_force":0.54662,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54444,0.07708,0.06221]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49074,0.05352,0.00938],"force_p95":0.54406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54406,"mean_force":0.54406,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5444,0.07708,0.0622]}],"total_contact_groups":9},"final_pose_error":0.14449,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50593,0.06299,0.03381],"final_tcp_position":[0.54451,0.07719,0.06231],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":498.72084,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":827.0,"n_steps_budget":930.0,"object_pos_end":[0.50601,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":896.0,"raw_peak_contact_force":496.78789,"subtask_id":"approach","tcp_end":[0.54461,0.07654,0.06399],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":0.0,"n_steps_budget":990.0,"object_pos_end":[0.50601,0.06294,0.03381],"object_pos_start":[0.50601,0.06294,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.1432,"peak_contact_force":0.54593,"phase_name":"lateral_push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.54461,0.07654,0.06399],"tcp_start":[0.54461,0.07654,0.06399],"tcp_to_object_dist_end":0.05085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.50601,0.06294,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":233.12714,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1082.0,"raw_peak_contact_force":233.62207,"subtask_id":"approach","tcp_end":[0.54444,0.07708,0.06221],"tcp_start":[0.54461,0.07654,0.06399],"tcp_to_object_dist_end":0.04987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.50594,0.06296,0.03381],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":121.30147,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":121.30147,"subtask_id":"contact","tcp_end":[0.5444,0.07708,0.0622],"tcp_start":[0.54444,0.07708,0.06221],"tcp_to_object_dist_end":0.04985,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06299,0.03381],"object_pos_start":[0.50594,0.06296,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":498.72084,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":498.72084,"subtask_id":"push","tcp_end":[0.54451,0.07719,0.06231],"tcp_start":[0.5444,0.07708,0.0622],"tcp_to_object_dist_end":0.05003,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":28.0,"average_failure_rate":0.46667,"average_mean_iterations":95.93333,"average_solve_count":60.0,"average_success_count":32.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.19951,"align_1.lateral_offset_x":-0.01489,"approach_1.approach_speed":0.03353,"contact_1.contact_force_threshold":15.73301,"contact_1.contact_speed":0.04377,"lateral_push_1.lateral_distance":0.02518,"lateral_push_1.lateral_speed":0.03576,"push_1.push_distance":0.13636,"push_1.push_speed":0.05288,"push_1.push_tolerance":0.01742,"retract_1.retract_speed":0.10115},"optimized_scores":{"best_composite_score":-0.59615,"best_fitness_score":0.07385,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":68.0,"contact_point_centroid":[0.55377,0.07122,0.05976],"force_p95":379.47302,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":472.54123,"mean_force":318.55145,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.54249,0.07154,0.0636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":814.0,"contact_point_centroid":[0.50593,0.05661,0.00936],"force_p95":0.60089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56614,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52263,0.12833,0.16648]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50025,0.19737,0.2949]}],"total_contact_groups":3},"final_pose_error":0.04656,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50615,0.05665,0.0338],"final_tcp_position":[0.543,0.07141,0.06419],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":472.54123,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":843.0,"n_steps_budget":960.0,"object_pos_end":[0.50615,0.05665,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":324.36711,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":919.0,"raw_peak_contact_force":472.54123,"subtask_id":"approach","tcp_end":[0.543,0.07141,0.06419],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":0.0,"n_steps_budget":840.0,"object_pos_end":[0.50615,0.05665,0.0338],"object_pos_start":[0.50615,0.05665,0.0338],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.13693,"peak_contact_force":324.27863,"phase_name":"lateral_push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.543,0.07141,0.06419],"tcp_start":[0.543,0.07141,0.06419],"tcp_to_object_dist_end":0.05,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```