## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.4071 | 0.67 | ❌ rejected |
| 13 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5148 | 0.93 | ❌ rejected |
| 12 | approach → approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1213 | 0.08 | ❌ rejected |
| 11 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.4770 | 0.69 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.2244 | 0.02 | ❌ rejected |

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

## Current Skill (Q=0.407) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_high
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  guards:
  - id: wall_contact_high
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - -0.02
    - 0.0
    - 0.0
- id: descend_to_peg
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  guards:
  - id: wall_contact_descend
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - -0.02
    - 0.0
    - 0.0
  subtask_id: approach
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
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: contact
- id: push_along_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
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
      - 1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.12
      - 0.22
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
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
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=wall_contact_high, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[-0.02, 0.0, 0.0]
- **descend_to_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=wall_contact_descend, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[-0.02, 0.0, 0.0]
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_lateral_x: status=consumed; consumers=target.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.407
- **task_score** (E): 0.673
- **fitness_score**: 0.697  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.0864 |
| descend_to_peg | 1.00 | 1.00 | 0.1963 |
| contact_1 | 1.00 | 1.00 | 0.0301 |
| push_along_channel | 1.00 | 1.00 | 0.1833 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.135, 0.248) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.525 | 3.526 |
| descend_to_peg | approach | 1.00 / step_budget | (0.513, 0.135, 0.248)→(0.501, 0.121, 0.053) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.525 | 0.611 |
| contact_1 | contact | 1.00 / step_budget | (0.501, 0.121, 0.053)→(0.499, 0.101, 0.031) | (0.503, 0.080, 0.034)→(0.504, 0.071, 0.035) | 0.160→0.151 | 1.00 / 2.333 | 2.758 | 7.486 |
| push_along_channel | push | 1.00 / step_budget | (0.499, 0.101, 0.031)→(0.507, -0.082, 0.031) | (0.504, 0.071, 0.035)→(0.499, -0.134, 0.032) | 0.151→0.055 | 1.00 / 2.000 | 112.792 | 710.681 |
| retract_1 | retract | 1.00 / step_budget | (0.507, -0.082, 0.031)→(0.505, -0.082, 0.112) | (0.499, -0.134, 0.032)→(0.514, -0.153, 0.021) | 0.055→0.080 | 1.00 / 1.333 | 0.645 | 94.833 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.773
- phase_score: 0.773
- phase_breakdown.approach_score: 0.744
- phase_breakdown.contact_score: 0.806
- phase_breakdown.push_score: 0.772

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.773
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.903
- **Median Q (composite search score)**: 0.468
- **K-run variance**: 0.0094
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.419


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64835,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":15.09377,"push_along_channel.push_depth":0.21755,"push_along_channel.push_lateral_x":0.01401,"push_along_channel.push_speed":0.06745},"optimized_scores":{"best_composite_score":0.48305,"best_fitness_score":0.77305,"best_task_score":0.77287},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.53549,0.11998,0.05921],"force_p95":810.12777,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":832.95665,"mean_force":615.84445,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48135,0.14513,0.0251]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47491,0.11992,0.02814],"force_p95":206.89749,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.42843,"mean_force":177.23387,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48418,0.12707,0.02667]},{"body_a":"attachment","body_b":"peg","contact_count":822.0,"contact_point_centroid":[0.50242,0.01205,0.05354],"force_p95":171.41281,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.14328,"mean_force":128.77466,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49342,0.01949,0.02741]},{"body_a":"peg","body_b":"channel_base_body","contact_count":174.0,"contact_point_centroid":[0.50718,-0.1039,0.05274],"force_p95":169.68467,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.11885,"mean_force":131.62794,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50484,-0.06435,0.02911]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":762.0,"contact_point_centroid":[0.52748,-0.00124,0.05552],"force_p95":144.93115,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.99,"mean_force":96.54745,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49331,0.01782,0.02732]},{"body_a":"peg","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.49129,-0.10435,0.0577],"force_p95":137.01488,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.75952,"mean_force":62.98958,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50849,-0.07102,0.06225]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52505,-0.07689,0.05999],"force_p95":127.10125,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.17558,"mean_force":107.51632,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50957,-0.07648,0.03152]},{"body_a":"attachment","body_b":"peg","contact_count":164.0,"contact_point_centroid":[0.50193,-0.0795,0.06037],"force_p95":108.06791,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":115.53636,"mean_force":64.46248,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50853,-0.07073,0.05942]},{"body_a":"peg","body_b":"channel_base_body","contact_count":713.0,"contact_point_centroid":[0.5118,0.01447,0.00965],"force_p95":84.18735,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.05262,"mean_force":53.10523,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49058,0.04428,0.02706]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":147.0,"contact_point_centroid":[0.47459,-0.09086,0.05477],"force_p95":64.64251,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.88077,"mean_force":29.75359,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50826,-0.07153,0.06332]},{"body_a":"peg","body_b":"link7","contact_count":573.0,"contact_point_centroid":[0.52318,0.03983,0.06316],"force_p95":55.70163,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.58289,"mean_force":39.46869,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48991,0.04479,0.02689]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47411,-0.09821,0.05974],"force_p95":11.07119,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.83556,"mean_force":5.03351,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50827,-0.07312,0.03046]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52503,-0.0779,0.0531],"force_p95":8.87194,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.00063,"mean_force":8.13228,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50892,-0.06865,0.0794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.49806,0.1052,0.00976],"force_p95":4.92014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.73604,"mean_force":2.49587,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4909,0.14759,0.03864]},{"body_a":"attachment","body_b":"peg","contact_count":191.0,"contact_point_centroid":[0.49484,0.13181,0.04792],"force_p95":4.73241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.41841,"mean_force":3.45238,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49125,0.14373,0.03459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50658,-0.07208,0.00762],"force_p95":4.77588,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.06253,"mean_force":2.67784,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5074,-0.07593,0.10914]}],"total_contact_groups":19},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49631,-0.07814,0.03394],"final_tcp_position":[0.50741,-0.07619,0.11181],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":832.95665,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":109.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11901,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50659,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":108.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48922,0.17156,0.25482],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.119,0.03397],"object_pos_start":[0.49601,0.11901,0.03384],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19914,"object_z_max":0.03416,"peak_contact_force":0.50928,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":386.0,"raw_peak_contact_force":0.626,"subtask_id":"approach","tcp_end":[0.49224,0.15942,0.05347],"tcp_start":[0.48922,0.17156,0.25482],"tcp_to_object_dist_end":0.04504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.49763,0.11037,0.03525],"object_pos_start":[0.49602,0.119,0.03397],"object_to_goal_dist_end":0.19044,"object_to_goal_dist_start":0.19913,"object_z_max":0.03541,"peak_contact_force":2.89886,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":510.0,"raw_peak_contact_force":6.73604,"subtask_id":"contact","tcp_end":[0.49189,0.13994,0.03091],"tcp_start":[0.49224,0.15942,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.49589,-0.10402,0.04224],"object_pos_start":[0.49763,0.11037,0.03525],"object_to_goal_dist_end":0.02447,"object_to_goal_dist_start":0.19044,"object_z_max":0.04212,"peak_contact_force":117.49732,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3107.0,"raw_peak_contact_force":832.95665,"subtask_id":"push","tcp_end":[0.50939,-0.07761,0.03143],"tcp_start":[0.49189,0.13994,0.03091],"tcp_to_object_dist_end":0.03157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":235.0,"n_steps_budget":630.0,"object_pos_end":[0.49631,-0.07814,0.03394],"object_pos_start":[0.49589,-0.10402,0.04224],"object_to_goal_dist_end":0.00733,"object_to_goal_dist_start":0.02447,"object_z_max":0.06811,"peak_contact_force":0.67676,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":514.0,"raw_peak_contact_force":142.75952,"tcp_end":[0.50741,-0.07619,0.11181],"tcp_start":[0.50939,-0.07761,0.03143],"tcp_to_object_dist_end":0.07867,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57627,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":9.60896,"push_along_channel.push_depth":0.16574,"push_along_channel.push_lateral_x":0.00231,"push_along_channel.push_speed":0.06104},"optimized_scores":{"best_composite_score":0.27004,"best_fitness_score":0.56004,"best_task_score":0.34184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.5367,0.07594,0.05952],"force_p95":641.86631,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":654.68106,"mean_force":420.81705,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49553,0.08514,0.02559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.50206,-0.10727,0.03455],"force_p95":155.32234,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.78577,"mean_force":61.31432,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50491,-0.06682,0.02995]},{"body_a":"attachment","body_b":"peg","contact_count":272.0,"contact_point_centroid":[0.50438,-0.00367,0.04726],"force_p95":128.97056,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":182.77607,"mean_force":46.05566,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49983,0.00799,0.02771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.49636,-0.11304,0.04109],"force_p95":74.02756,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.19405,"mean_force":10.88422,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50608,-0.08151,0.03708]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50397,-0.09301,0.03213],"force_p95":94.55215,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.41879,"mean_force":52.96521,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50692,-0.08182,0.03181]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":233.0,"contact_point_centroid":[0.52557,0.00209,0.04921],"force_p95":69.04569,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.44245,"mean_force":29.12225,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4983,0.032,0.02695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":160.0,"contact_point_centroid":[0.50936,0.00724,0.00965],"force_p95":64.03273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.78424,"mean_force":16.91951,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49808,0.04425,0.02692]},{"body_a":"peg","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.52196,0.05926,0.0604],"force_p95":45.82876,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.96216,"mean_force":21.83643,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49571,0.08266,0.02521]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47469,-0.10214,0.05969],"force_p95":16.00181,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.57519,"mean_force":5.38847,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50539,-0.0739,0.03021]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.4749,-0.10982,0.05998],"force_p95":10.93009,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.60238,"mean_force":7.35888,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50676,-0.08189,0.03206]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.50697,0.05008,0.0097],"force_p95":4.84682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.26235,"mean_force":2.41142,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50195,0.09242,0.0386]},{"body_a":"attachment","body_b":"peg","contact_count":178.0,"contact_point_centroid":[0.50506,0.07614,0.04708],"force_p95":4.80396,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.935,"mean_force":3.59059,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50184,0.08811,0.03422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":183.0,"contact_point_centroid":[0.50525,0.06282,0.0093],"force_p95":0.79803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.62046,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51165,0.15603,0.26879]},{"body_a":"peg","body_b":"world","contact_count":171.0,"contact_point_centroid":[0.50097,-0.17818,-0.00163],"force_p95":1.61811,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.12332,"mean_force":0.68306,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50479,-0.08112,0.07979]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50082,0.19534,0.2964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49134,-0.11992,0.00976],"force_p95":1.57167,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83126,"mean_force":0.76959,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5055,-0.0813,0.04278]}],"total_contact_groups":18},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50315,-0.18343,0.01409],"final_tcp_position":[0.50481,-0.08122,0.11165],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":654.68106,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":750.0,"object_pos_end":[0.50594,0.063,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54212,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":217.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.52217,0.12037,0.24581],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06303,0.0338],"object_pos_start":[0.50594,0.063,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":0.55057,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":363.0,"raw_peak_contact_force":0.55664,"subtask_id":"approach","tcp_end":[0.50472,0.10434,0.05347],"tcp_start":[0.52217,0.12037,0.24581],"tcp_to_object_dist_end":0.04577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,0.05477,0.03528],"object_pos_start":[0.50602,0.06303,0.0338],"object_to_goal_dist_end":0.13503,"object_to_goal_dist_start":0.14329,"object_z_max":0.03537,"peak_contact_force":2.23578,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":524.0,"raw_peak_contact_force":9.26235,"subtask_id":"contact","tcp_end":[0.50202,0.08446,0.03077],"tcp_start":[0.50472,0.10434,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.49751,-0.10976,0.04166],"object_pos_start":[0.50699,0.05477,0.03528],"object_to_goal_dist_end":0.02992,"object_to_goal_dist_start":0.13503,"object_z_max":0.0415,"peak_contact_force":8.86994,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":827.0,"raw_peak_contact_force":654.68106,"subtask_id":"push","tcp_end":[0.50704,-0.08144,0.03152],"tcp_start":[0.50202,0.08446,0.03077],"tcp_to_object_dist_end":0.03156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":660.0,"object_pos_end":[0.50315,-0.18343,0.01409],"object_pos_start":[0.49751,-0.10976,0.04166],"object_to_goal_dist_end":0.10667,"object_to_goal_dist_start":0.02992,"object_z_max":0.04188,"peak_contact_force":0.72621,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":232.0,"raw_peak_contact_force":105.19405,"tcp_end":[0.50481,-0.08122,0.11165],"tcp_start":[0.50704,-0.08144,0.03152],"tcp_to_object_dist_end":0.1413,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5989,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":11.22006,"push_along_channel.push_depth":0.18471,"push_along_channel.push_lateral_x":-0.00205,"push_along_channel.push_speed":0.06207},"optimized_scores":{"best_composite_score":0.46835,"best_fitness_score":0.75835,"best_task_score":0.90333},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.53754,0.06863,0.05956],"force_p95":636.97153,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":644.40566,"mean_force":406.3833,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49541,0.07795,0.02565]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":106.0,"contact_point_centroid":[0.51033,-0.10041,0.06499],"force_p95":223.8927,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.63385,"mean_force":205.13826,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50572,-0.08829,0.03101]},{"body_a":"attachment","body_b":"peg","contact_count":591.0,"contact_point_centroid":[0.50556,-0.04537,0.05628],"force_p95":181.77493,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":214.03886,"mean_force":116.60047,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50011,-0.03527,0.0283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.50674,-0.10425,0.05521],"force_p95":176.51302,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":213.82309,"mean_force":144.91666,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50186,-0.06691,0.02904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.50876,-0.06577,0.00978],"force_p95":41.83613,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.21692,"mean_force":10.97675,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49946,-0.02743,0.02806]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":595.0,"contact_point_centroid":[0.52553,-0.05525,0.05296],"force_p95":57.45271,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.30859,"mean_force":26.28388,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4998,-0.02896,0.02818]},{"body_a":"peg","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.52046,0.05339,0.0607],"force_p95":56.99039,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.89896,"mean_force":19.52392,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4955,0.07731,0.02522]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51038,-0.10004,0.065],"force_p95":36.28912,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.54514,"mean_force":29.47466,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50566,-0.08752,0.03089]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.4748,-0.11459,0.03445],"force_p95":14.1462,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.8981,"mean_force":4.85839,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50569,-0.08683,0.03063]},{"body_a":"attachment","body_b":"peg","contact_count":146.0,"contact_point_centroid":[0.50534,0.06945,0.04659],"force_p95":6.0052,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.46095,"mean_force":4.06073,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50212,0.08142,0.03385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":292.0,"contact_point_centroid":[0.50664,0.04426,0.00969],"force_p95":5.2799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.3841,"mean_force":2.25508,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50242,0.08629,0.03881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50547,0.05653,0.00931],"force_p95":0.75767,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.62609,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51493,0.15248,0.26826]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":127.0,"contact_point_centroid":[0.5251,0.05151,0.03147],"force_p95":2.53861,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.99659,"mean_force":1.40552,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50212,0.08108,0.03351]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5012,0.19476,0.29613]},{"body_a":"peg","body_b":"world","contact_count":66.0,"contact_point_centroid":[0.49958,-0.17626,-0.00154],"force_p95":2.58912,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.4877,"mean_force":0.82951,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50571,-0.08779,0.03102]},{"body_a":"peg","body_b":"world","contact_count":230.0,"contact_point_centroid":[0.52347,-0.19191,-0.002],"force_p95":0.6852,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89109,"mean_force":0.60439,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50359,-0.08716,0.07007]}],"total_contact_groups":17},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.54351,-0.19654,0.01411],"final_tcp_position":[0.50334,-0.08734,0.11137],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":644.40566,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":780.0,"object_pos_end":[0.50613,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52504,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":237.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.52825,0.11375,0.24485],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05662,0.03377],"object_pos_start":[0.50613,0.0566,0.03377],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03383,"peak_contact_force":0.51533,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":360.0,"raw_peak_contact_force":0.64921,"subtask_id":"approach","tcp_end":[0.50559,0.09796,0.05344],"tcp_start":[0.52825,0.11375,0.24485],"tcp_to_object_dist_end":0.04579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":302.0,"n_steps_budget":600.0,"object_pos_end":[0.50706,0.04848,0.03534],"object_pos_start":[0.50614,0.05662,0.03377],"object_to_goal_dist_end":0.12876,"object_to_goal_dist_start":0.1369,"object_z_max":0.03544,"peak_contact_force":3.13935,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":565.0,"raw_peak_contact_force":6.46095,"subtask_id":"contact","tcp_end":[0.50218,0.07816,0.03076],"tcp_start":[0.50559,0.09796,0.05344],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.50447,-0.18725,0.01347],"object_pos_start":[0.50706,0.04848,0.03534],"object_to_goal_dist_end":0.11057,"object_to_goal_dist_start":0.12876,"object_z_max":0.04085,"peak_contact_force":212.01023,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2307.0,"raw_peak_contact_force":644.40566,"subtask_id":"push","tcp_end":[0.50568,-0.08755,0.03091],"tcp_start":[0.50218,0.07816,0.03076],"tcp_to_object_dist_end":0.10122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":230.0,"n_steps_budget":630.0,"object_pos_end":[0.54351,-0.19654,0.01411],"object_pos_start":[0.50447,-0.18725,0.01347],"object_to_goal_dist_end":0.12707,"object_to_goal_dist_start":0.11057,"object_z_max":0.01413,"peak_contact_force":0.53294,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":233.0,"raw_peak_contact_force":36.54514,"tcp_end":[0.50334,-0.08734,0.11137],"tcp_start":[0.50568,-0.08755,0.03091],"tcp_to_object_dist_end":0.15166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```