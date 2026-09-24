## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | -0.1435 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0528 | 0.09 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.1845 | 0.11 | ❌ rejected |
| 9 | approach → push → retract | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1857 | 0.02 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1139 | 0.01 | ❌ rejected |

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

## Current Skill (Q=-0.144) — your mutation base

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

- **Composite score**: -0.144
- **task_score** (E): 0.001
- **fitness_score**: 0.130  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.267
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2213 |
| approach_1 | 1.00 | 1.00 | 0.0380 |
| contact_1 | 1.00 | 1.00 | 0.0302 |
| push_1 | 0.33 | 1.00 | 0.0010 |
| retract_1 | 0.67 | 1.00 | 0.1243 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.523, 0.123, 0.097) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.565 | 3.526 |
| approach_1 | approach | 1.00 / step_budget | (0.523, 0.123, 0.097)→(0.503, 0.102, 0.081) | (0.503, 0.080, 0.034)→(0.503, 0.085, 0.033) | 0.160→0.165 | 1.00 / 1.000 | 0.564 | 0.732 |
| contact_1 | contact | 1.00 / force_exceeded | (0.503, 0.102, 0.081)→(0.500, 0.097, 0.051) | (0.503, 0.085, 0.033)→(0.504, 0.093, 0.027) | 0.165→0.174 | 1.00 / 2.000 | 63.417 | 14.700 |
| push_1 | push | 0.33 / guard_failure | (0.499, 0.100, 0.050)→(0.499, 0.101, 0.050) | (0.504, 0.093, 0.027)→(0.504, 0.094, 0.027) | 0.174→0.174 | 1.00 / 2.000 | 119.982 | 119.982 |
| retract_1 | retract | 0.67 / step_budget | (0.499, 0.101, 0.050)→(0.496, 0.107, 0.174) | (0.504, 0.095, 0.026)→(0.500, 0.094, 0.027) | 0.175→0.175 | 1.00 / 1.000 | 0.559 | 70.456 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.298
- terminal_score: 0.000
- phase_score: 0.202
- phase_breakdown.approach_score: 0.374
- phase_breakdown.contact_score: 0.516
- phase_breakdown.push_score: 0.040

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.154
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.002
- **Median Q (composite search score)**: -0.186
- **K-run variance**: 0.0080
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56557,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.1149,"align_1.lateral_offset_x":0.00104,"approach_1.approach_speed":0.069,"contact_1.contact_force_threshold":10.3578,"contact_1.contact_speed":0.03249,"push_1.push_distance":0.11925,"push_1.push_force_threshold":26.98835,"push_1.push_speed":0.05035,"retract_1.retract_speed":0.12927},"optimized_scores":{"best_composite_score":-0.18571,"best_fitness_score":0.15429,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50151,0.14365,0.03051],"force_p95":146.68534,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.74121,"mean_force":61.04419,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49062,0.14219,0.03215]},{"body_a":"peg","body_b":"world","contact_count":7.0,"contact_point_centroid":[0.49923,0.14316,-0.0027],"force_p95":133.38308,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":166.70128,"mean_force":42.37008,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49079,0.14181,0.03231]},{"body_a":"peg","body_b":"world","contact_count":692.0,"contact_point_centroid":[0.4907,0.16296,-0.00213],"force_p95":8.99929,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.40456,"mean_force":2.59836,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48601,0.15607,0.09522]},{"body_a":"attachment","body_b":"peg","contact_count":54.0,"contact_point_centroid":[0.49675,0.14709,0.0269],"force_p95":67.13287,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.16622,"mean_force":25.32859,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48522,0.14922,0.02886]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.52965,0.11999,0.05986],"force_p95":7.25282,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10.36117,"mean_force":1.48017,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48436,0.14832,0.02497]},{"body_a":"peg","body_b":"world","contact_count":288.0,"contact_point_centroid":[0.49738,0.15752,-0.00178],"force_p95":0.84136,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.87009,"mean_force":0.61747,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49034,0.13978,0.05528]},{"body_a":"peg","body_b":"channel_base_body","contact_count":582.0,"contact_point_centroid":[0.49625,0.11921,0.0094],"force_p95":0.61758,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55533,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49156,0.17949,0.19556]},{"body_a":"peg","body_b":"world","contact_count":7.0,"contact_point_centroid":[0.49605,0.13371,-0.00026],"force_p95":1.04309,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07815,"mean_force":0.80792,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49145,0.1408,0.08044]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49952,0.19921,0.29757]},{"body_a":"peg","body_b":"channel_base_body","contact_count":430.0,"contact_point_centroid":[0.49615,0.11965,0.00943],"force_p95":0.59706,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63725,"mean_force":0.53012,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48746,0.14913,0.08714]}],"total_contact_groups":10},"final_pose_error":0.01303,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.48975,0.16388,0.01414],"final_tcp_position":[0.48661,0.14883,0.16751],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":168.74121,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11989,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.20002,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.59778,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":606.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48489,0.16071,0.09945],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":431.0,"n_steps_budget":600.0,"object_pos_end":[0.49608,0.1356,0.03004],"object_pos_start":[0.49599,0.11989,0.03384],"object_to_goal_dist_end":0.21587,"object_to_goal_dist_start":0.20002,"object_z_max":0.03392,"peak_contact_force":0.60493,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":437.0,"raw_peak_contact_force":1.07815,"subtask_id":"approach","tcp_end":[0.49151,0.14067,0.08034],"tcp_start":[0.48489,0.16071,0.09945],"tcp_to_object_dist_end":0.05076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":297.0,"n_steps_budget":990.0,"object_pos_end":[0.49968,0.15988,0.01409],"object_pos_start":[0.49608,0.1356,0.03004],"object_to_goal_dist_end":0.24128,"object_to_goal_dist_start":0.21587,"object_z_max":0.03004,"peak_contact_force":149.02164,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":288.0,"raw_peak_contact_force":2.87009,"subtask_id":"contact","tcp_end":[0.4915,0.13956,0.03346],"tcp_start":[0.49151,0.14067,0.08034],"tcp_to_object_dist_end":0.02924,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.49931,0.16125,0.01244],"object_pos_start":[0.49968,0.15988,0.01409],"object_to_goal_dist_end":0.24282,"object_to_goal_dist_start":0.24128,"object_z_max":0.01409,"peak_contact_force":168.74121,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":168.74121,"subtask_id":"push","tcp_end":[0.48923,0.14677,0.0301],"tcp_start":[0.48959,0.1453,0.03074],"tcp_to_object_dist_end":0.02497,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.48975,0.16388,0.01414],"object_pos_start":[0.49897,0.16263,0.01049],"object_to_goal_dist_end":0.24546,"object_to_goal_dist_start":0.24442,"object_z_max":0.015,"peak_contact_force":0.59413,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":753.0,"raw_peak_contact_force":103.40456,"tcp_end":[0.48661,0.14883,0.16751],"tcp_start":[0.48923,0.14677,0.0301],"tcp_to_object_dist_end":0.15414,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5042,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.09588,"align_1.lateral_offset_x":0.01469,"approach_1.approach_speed":0.07299,"contact_1.contact_force_threshold":18.0737,"contact_1.contact_speed":0.01998,"push_1.push_distance":0.19786,"push_1.push_force_threshold":32.86749,"push_1.push_speed":0.05509,"retract_1.retract_speed":0.16719},"optimized_scores":{"best_composite_score":-0.01892,"best_fitness_score":0.12108,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50571,0.06313,0.00939],"force_p95":0.58974,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.11938,"mean_force":0.72601,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5011,0.08935,0.12493]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.51488,0.07829,0.05864],"force_p95":34.16571,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.63243,"mean_force":7.06448,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50316,0.08,0.06026]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52395,0.06394,0.00938],"force_p95":34.55379,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.55379,"mean_force":34.55379,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50376,0.07963,0.0604]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51553,0.07832,0.05865],"force_p95":33.0133,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.0133,"mean_force":33.0133,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50376,0.07963,0.0604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.50598,0.063,0.00938],"force_p95":0.55117,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.52525,"mean_force":0.74643,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50524,0.08324,0.07064]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51553,0.07833,0.05871],"force_p95":25.9769,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.9769,"mean_force":25.9769,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50376,0.07968,0.06053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":710.0,"contact_point_centroid":[0.50583,0.063,0.00936],"force_p95":0.55941,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56562,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51888,0.15206,0.19317]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50014,0.19827,0.29627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":238.0,"contact_point_centroid":[0.50587,0.06305,0.00938],"force_p95":0.55269,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55422,"mean_force":0.54657,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52237,0.09706,0.08694]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.06293,0.05868],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50194,0.08175,0.06389]}],"total_contact_groups":10},"final_pose_error":0.01474,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.06296,0.03381],"final_tcp_position":[0.50145,0.08272,0.19593],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":35.11938,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54919,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":744.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.53829,0.10759,0.09616],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":238.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06297,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54451,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":238.0,"raw_peak_contact_force":0.55422,"subtask_id":"approach","tcp_end":[0.50787,0.08648,0.08092],"tcp_start":[0.53829,0.10759,0.09616],"tcp_to_object_dist_end":0.05269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":130.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,0.06298,0.03381],"object_pos_start":[0.50603,0.06297,0.03381],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":26.52525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":131.0,"raw_peak_contact_force":26.52525,"subtask_id":"contact","tcp_end":[0.50376,0.07963,0.0604],"tcp_start":[0.50787,0.08648,0.08092],"tcp_to_object_dist_end":0.03145,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.06313,0.03387],"object_pos_start":[0.50605,0.06298,0.03381],"object_to_goal_dist_end":0.14339,"object_to_goal_dist_start":0.14325,"object_z_max":0.03381,"peak_contact_force":34.55379,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":34.55379,"subtask_id":"push","tcp_end":[0.5039,0.07991,0.06019],"tcp_start":[0.50376,0.07963,0.0604],"tcp_to_object_dist_end":0.03129,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.06296,0.03381],"object_pos_start":[0.50613,0.06313,0.03387],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14339,"object_z_max":0.03424,"peak_contact_force":0.54398,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":560.0,"raw_peak_contact_force":35.11938,"tcp_end":[0.50145,0.08272,0.19593],"tcp_start":[0.5039,0.07991,0.06019],"tcp_to_object_dist_end":0.16339,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29688,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.1297,"align_1.lateral_offset_x":0.01495,"approach_1.approach_speed":0.04215,"contact_1.contact_force_threshold":7.27302,"contact_1.contact_speed":0.02559,"push_1.push_distance":0.13851,"push_1.push_force_threshold":30.83616,"push_1.push_speed":0.01901,"retract_1.retract_speed":0.0551},"optimized_scores":{"best_composite_score":-0.2259,"best_fitness_score":0.1141,"best_task_score":0.00162},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50512,0.06894,0.00928],"force_p95":153.06981,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":156.65153,"mean_force":103.63011,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50426,0.07378,0.06004]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.51587,0.0716,0.05838],"force_p95":151.50571,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.10565,"mean_force":102.42601,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50426,0.07378,0.06004]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.51322,0.07092,0.05884],"force_p95":51.57014,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.84532,"mean_force":10.60417,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50308,0.077,0.06005]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50537,0.0572,0.00944],"force_p95":0.63317,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.08718,"mean_force":0.95053,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50116,0.08663,0.10747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":121.0,"contact_point_centroid":[0.50604,0.05636,0.00938],"force_p95":0.55246,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.70436,"mean_force":0.66369,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50569,0.07661,0.07051]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51589,0.07167,0.05874],"force_p95":14.27241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.27241,"mean_force":14.27241,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50413,0.07318,0.06057]},{"body_a":"peg","body_b":"channel_base_body","contact_count":705.0,"contact_point_centroid":[0.50593,0.0566,0.00936],"force_p95":0.60098,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56918,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52244,0.1488,0.19269]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50027,0.19802,0.29585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.50621,0.05671,0.00938],"force_p95":0.55277,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56254,"mean_force":0.54662,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52582,0.09052,0.0863]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.0572,0.05889],"force_p95":0.09987,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.10359,"mean_force":0.06799,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50119,0.08006,0.06793]}],"total_contact_groups":10},"final_pose_error":0.05278,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50571,0.05568,0.03443],"final_tcp_position":[0.50136,0.08803,0.15809],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":156.65153,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.5471,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":742.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.54512,0.10147,0.0957],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":720.0,"object_pos_end":[0.50614,0.05659,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":0.54255,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":281.0,"raw_peak_contact_force":0.56254,"subtask_id":"approach","tcp_end":[0.50828,0.07972,0.08057],"tcp_start":[0.54512,0.10147,0.0957],"tcp_to_object_dist_end":0.05224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03379],"object_pos_start":[0.50614,0.05659,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":14.70436,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":122.0,"raw_peak_contact_force":14.70436,"subtask_id":"contact","tcp_end":[0.50413,0.07313,0.06042],"tcp_start":[0.50828,0.07972,0.08057],"tcp_to_object_dist_end":0.03141,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05697,0.03383],"object_pos_start":[0.50611,0.0566,0.03379],"object_to_goal_dist_end":0.13724,"object_to_goal_dist_start":0.13687,"object_z_max":0.034,"peak_contact_force":156.65153,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":156.65153,"subtask_id":"push","tcp_end":[0.50436,0.07578,0.05934],"tcp_start":[0.50433,0.07471,0.05963],"tcp_to_object_dist_end":0.03174,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50571,0.05568,0.03443],"object_pos_start":[0.50616,0.05791,0.03426],"object_to_goal_dist_end":0.13591,"object_to_goal_dist_start":0.13816,"object_z_max":0.03623,"peak_contact_force":0.53844,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1042.0,"raw_peak_contact_force":72.84532,"tcp_end":[0.50136,0.08803,0.15809],"tcp_start":[0.50436,0.07578,0.05934],"tcp_to_object_dist_end":0.1279,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```