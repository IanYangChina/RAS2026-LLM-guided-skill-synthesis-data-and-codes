## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5316 | 0.85 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 1 | 0.4142 | 0.29 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 1 | 0.4142 | 0.29 | ❌ rejected |
| 1 | approach → contact → push → retract → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7130 | 0.83 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.4142 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.532) — your mutation base

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

- **Composite score**: 0.532
- **task_score** (E): 0.850
- **fitness_score**: 0.755  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.0864 |
| descend_to_peg | 1.00 | 1.00 | 0.1963 |
| contact_1 | 1.00 | 1.00 | 0.0266 |
| push_along_channel | 1.00 | 1.00 | 0.1888 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.135, 0.248) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.525 | 3.526 |
| descend_to_peg | approach | 1.00 / step_budget | (0.513, 0.135, 0.248)→(0.501, 0.121, 0.053) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.525 | 0.611 |
| contact_1 | contact | 1.00 / step_budget | (0.501, 0.121, 0.053)→(0.499, 0.103, 0.033) | (0.503, 0.080, 0.034)→(0.504, 0.074, 0.035) | 0.160→0.154 | 1.00 / 2.000 | 3.562 | 7.183 |
| push_along_channel | push | 1.00 / step_budget | (0.499, 0.103, 0.033)→(0.509, -0.085, 0.031) | (0.504, 0.074, 0.035)→(0.491, -0.134, 0.032) | 0.154→0.056 | 1.00 / 3.000 | 375.041 | 771.243 |
| retract_1 | retract | 1.00 / step_budget | (0.509, -0.085, 0.031)→(0.507, -0.084, 0.111) | (0.491, -0.134, 0.032)→(0.515, -0.196, 0.030) | 0.056→0.127 | 1.00 / 1.667 | 1.120 | 289.904 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.742
- phase_score: 0.644
- phase_breakdown.approach_score: 0.509
- phase_breakdown.contact_score: 0.490
- phase_breakdown.push_score: 0.740

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.803
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.513
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.305


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8323,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":11.2924,"push_along_channel.push_depth":0.21903,"push_along_channel.push_lateral_x":0.01851,"push_along_channel.push_speed":0.0954},"optimized_scores":{"best_composite_score":0.48853,"best_fitness_score":0.77853,"best_task_score":0.80853},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.53487,0.11998,0.05924],"force_p95":800.24679,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":820.45113,"mean_force":610.86358,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48129,0.14422,0.02517]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47494,0.11995,0.02847],"force_p95":219.66972,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.45247,"mean_force":178.03784,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48428,0.12697,0.02701]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":101.0,"contact_point_centroid":[0.52507,-0.07003,0.05999],"force_p95":212.17666,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.17217,"mean_force":149.67685,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50911,-0.06958,0.02967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":147.0,"contact_point_centroid":[0.50015,-0.10607,0.02736],"force_p95":143.19973,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.33507,"mean_force":84.58748,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50859,-0.06627,0.02955]},{"body_a":"peg","body_b":"channel_base_body","contact_count":202.0,"contact_point_centroid":[0.49194,-0.10332,0.05579],"force_p95":132.12168,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":186.45316,"mean_force":61.75126,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50838,-0.07146,0.06457]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":574.0,"contact_point_centroid":[0.52742,0.02878,0.05528],"force_p95":143.10377,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":170.69546,"mean_force":102.4371,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49175,0.04817,0.02698]},{"body_a":"attachment","body_b":"peg","contact_count":724.0,"contact_point_centroid":[0.50211,0.0212,0.0491],"force_p95":162.47505,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":170.20143,"mean_force":112.33934,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49464,0.02927,0.02746]},{"body_a":"attachment","body_b":"peg","contact_count":168.0,"contact_point_centroid":[0.5015,-0.07895,0.05887],"force_p95":109.1791,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":146.05709,"mean_force":66.58734,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50859,-0.07086,0.05775]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,-0.07846,0.05999],"force_p95":123.8981,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.55716,"mean_force":59.21679,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50877,-0.07785,0.02861]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":189.0,"contact_point_centroid":[0.4742,-0.08852,0.05529],"force_p95":89.87047,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.74639,"mean_force":34.78194,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50824,-0.07201,0.06501]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":42.0,"contact_point_centroid":[0.47473,-0.09626,0.05195],"force_p95":82.08122,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.62095,"mean_force":15.91994,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50902,-0.07063,0.02948]},{"body_a":"peg","body_b":"channel_base_body","contact_count":578.0,"contact_point_centroid":[0.51079,0.03412,0.00966],"force_p95":79.21148,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.34076,"mean_force":51.64548,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49017,0.0642,0.02697]},{"body_a":"peg","body_b":"link7","contact_count":470.0,"contact_point_centroid":[0.52297,0.05707,0.06291],"force_p95":51.29208,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.63297,"mean_force":36.40516,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48967,0.06281,0.02674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.49806,0.1052,0.00976],"force_p95":4.92014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.73604,"mean_force":2.49587,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4909,0.14759,0.03864]},{"body_a":"attachment","body_b":"peg","contact_count":191.0,"contact_point_centroid":[0.49484,0.13181,0.04792],"force_p95":4.73241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.41841,"mean_force":3.45238,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49125,0.14373,0.03459]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52511,-0.08052,0.05644],"force_p95":2.57354,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.58453,"mean_force":2.14174,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50699,-0.07568,0.10439]}],"total_contact_groups":19},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49541,-0.07915,0.06346],"final_tcp_position":[0.50691,-0.07621,0.10902],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":820.45113,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":109.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11901,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50659,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":108.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48922,0.17156,0.25482],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.119,0.03397],"object_pos_start":[0.49601,0.11901,0.03384],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19914,"object_z_max":0.03416,"peak_contact_force":0.50928,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":386.0,"raw_peak_contact_force":0.626,"subtask_id":"approach","tcp_end":[0.49224,0.15942,0.05347],"tcp_start":[0.48922,0.17156,0.25482],"tcp_to_object_dist_end":0.04504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.49763,0.11037,0.03525],"object_pos_start":[0.49602,0.119,0.03397],"object_to_goal_dist_end":0.19044,"object_to_goal_dist_start":0.19913,"object_z_max":0.03541,"peak_contact_force":2.89886,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":510.0,"raw_peak_contact_force":6.73604,"subtask_id":"contact","tcp_end":[0.49189,0.13994,0.03091],"tcp_start":[0.49224,0.15942,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":809.0,"n_steps_budget":1000.0,"object_pos_end":[0.49065,-0.09835,0.04112],"object_pos_start":[0.49763,0.11037,0.03525],"object_to_goal_dist_end":0.02062,"object_to_goal_dist_start":0.19044,"object_z_max":0.04099,"peak_contact_force":202.28687,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2695.0,"raw_peak_contact_force":820.45113,"subtask_id":"push","tcp_end":[0.50879,-0.07784,0.02862],"tcp_start":[0.49189,0.13994,0.03091],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":229.0,"n_steps_budget":630.0,"object_pos_end":[0.49541,-0.07915,0.06346],"object_pos_start":[0.49065,-0.09835,0.04112],"object_to_goal_dist_end":0.02392,"object_to_goal_dist_start":0.02062,"object_z_max":0.07253,"peak_contact_force":2.04219,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":587.0,"raw_peak_contact_force":186.45316,"tcp_end":[0.50691,-0.07621,0.10902],"tcp_start":[0.50879,-0.07784,0.02862],"tcp_to_object_dist_end":0.04708,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4456,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":17.91608,"push_along_channel.push_depth":0.17585,"push_along_channel.push_lateral_x":0.00387,"push_along_channel.push_speed":0.05084},"optimized_scores":{"best_composite_score":0.51323,"best_fitness_score":0.80323,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.53703,0.07553,0.05952],"force_p95":649.13136,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":659.96096,"mean_force":428.66744,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49561,0.08533,0.02559]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":32.0,"contact_point_centroid":[0.51331,-0.1009,0.06499],"force_p95":229.63169,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":230.86975,"mean_force":211.57523,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50898,-0.08941,0.032]},{"body_a":"attachment","body_b":"peg","contact_count":250.0,"contact_point_centroid":[0.50401,-0.02022,0.04064],"force_p95":147.2649,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.43486,"mean_force":46.00633,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50258,-0.00871,0.02877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":127.0,"contact_point_centroid":[0.50025,-0.10834,0.0293],"force_p95":155.17844,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":168.30909,"mean_force":66.03493,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50748,-0.0718,0.03111]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52502,-0.0825,0.06],"force_p95":129.37673,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.79268,"mean_force":97.54636,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50945,-0.0823,0.03261]},{"body_a":"peg","body_b":"channel_base_body","contact_count":187.0,"contact_point_centroid":[0.50507,-0.00197,0.00962],"force_p95":59.46494,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.50011,"mean_force":12.71258,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4995,0.03517,0.02735]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.51315,-0.10027,0.065],"force_p95":90.84795,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.64324,"mean_force":52.08174,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50877,-0.08805,0.03216]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":84.0,"contact_point_centroid":[0.52519,0.03485,0.05039],"force_p95":68.23212,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.63612,"mean_force":26.77034,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49668,0.06613,0.02625]},{"body_a":"peg","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.51832,0.03184,0.06332],"force_p95":40.18188,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.18409,"mean_force":13.42975,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49802,0.05636,0.02634]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":43.0,"contact_point_centroid":[0.47463,-0.09254,0.0593],"force_p95":14.60065,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.95988,"mean_force":3.32295,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50712,-0.06405,0.03098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.50697,0.05008,0.0097],"force_p95":4.84682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.26235,"mean_force":2.41142,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50195,0.09242,0.0386]},{"body_a":"attachment","body_b":"peg","contact_count":178.0,"contact_point_centroid":[0.50506,0.07614,0.04708],"force_p95":4.80396,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.935,"mean_force":3.59059,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50184,0.08811,0.03422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":183.0,"contact_point_centroid":[0.50525,0.06282,0.0093],"force_p95":0.79803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.62046,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51165,0.15603,0.26879]},{"body_a":"peg","body_b":"world","contact_count":11.0,"contact_point_centroid":[0.4881,-0.15769,-0.00133],"force_p95":3.32696,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.62164,"mean_force":1.73837,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.509,-0.08891,0.03196]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50082,0.19534,0.2964]},{"body_a":"peg","body_b":"world","contact_count":225.0,"contact_point_centroid":[0.50196,-0.2224,-0.00177],"force_p95":0.99376,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.91018,"mean_force":0.59956,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50686,-0.08783,0.07169]}],"total_contact_groups":18},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.52492,-0.28065,0.0141],"final_tcp_position":[0.50673,-0.08818,0.11227],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":659.96096,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":750.0,"object_pos_end":[0.50594,0.063,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54212,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":217.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.52217,0.12037,0.24581],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06303,0.0338],"object_pos_start":[0.50594,0.063,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":0.55057,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":363.0,"raw_peak_contact_force":0.55664,"subtask_id":"approach","tcp_end":[0.50472,0.10434,0.05347],"tcp_start":[0.52217,0.12037,0.24581],"tcp_to_object_dist_end":0.04577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,0.05477,0.03528],"object_pos_start":[0.50602,0.06303,0.0338],"object_to_goal_dist_end":0.13503,"object_to_goal_dist_start":0.14329,"object_z_max":0.03537,"peak_contact_force":2.23578,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":524.0,"raw_peak_contact_force":9.26235,"subtask_id":"contact","tcp_end":[0.50202,0.08446,0.03077],"tcp_start":[0.50472,0.10434,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.48953,-0.15435,0.02752],"object_pos_start":[0.50699,0.05477,0.03528],"object_to_goal_dist_end":0.07611,"object_to_goal_dist_start":0.13503,"object_z_max":0.04223,"peak_contact_force":225.66595,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":842.0,"raw_peak_contact_force":659.96096,"subtask_id":"push","tcp_end":[0.50899,-0.08843,0.03194],"tcp_start":[0.50202,0.08446,0.03077],"tcp_to_object_dist_end":0.06888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":232.0,"n_steps_budget":660.0,"object_pos_end":[0.52492,-0.28065,0.0141],"object_pos_start":[0.48953,-0.15435,0.02752],"object_to_goal_dist_end":0.20384,"object_to_goal_dist_start":0.07611,"object_z_max":0.02955,"peak_contact_force":0.56246,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":233.0,"raw_peak_contact_force":91.64324,"tcp_end":[0.50673,-0.08818,0.11227],"tcp_start":[0.50899,-0.08843,0.03194],"tcp_to_object_dist_end":0.21683,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86667,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":5.09215,"push_along_channel.push_depth":0.17625,"push_along_channel.push_lateral_x":0.00462,"push_along_channel.push_speed":0.07248},"optimized_scores":{"best_composite_score":0.59318,"best_fitness_score":0.68318,"best_task_score":0.74203},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.5472,0.06636,0.0595],"force_p95":793.47081,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":833.31818,"mean_force":586.07847,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49244,0.08908,0.02666]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.51349,-0.10096,0.06499],"force_p95":750.14353,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":793.48746,"mean_force":284.10547,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50906,-0.08949,0.03183]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52503,-0.08153,0.06],"force_p95":676.3434,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":698.14875,"mean_force":228.02572,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50937,-0.08121,0.03259]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.51284,-0.10032,0.06499],"force_p95":451.04689,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":591.61447,"mean_force":137.25042,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50867,-0.08815,0.03431]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,-0.08906,0.06],"force_p95":549.77794,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":580.4433,"mean_force":284.74436,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50914,-0.08861,0.03181]},{"body_a":"attachment","body_b":"peg","contact_count":296.0,"contact_point_centroid":[0.50436,-0.0095,0.04746],"force_p95":179.07609,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":216.41219,"mean_force":67.94653,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50006,0.00192,0.03051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":141.0,"contact_point_centroid":[0.50199,-0.10849,0.03077],"force_p95":187.32176,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":215.91206,"mean_force":76.22726,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50758,-0.07239,0.03191]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":248.0,"contact_point_centroid":[0.52562,-0.00373,0.04851],"force_p95":77.19539,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.89186,"mean_force":34.75502,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49762,0.0254,0.03006]},{"body_a":"peg","body_b":"channel_base_body","contact_count":184.0,"contact_point_centroid":[0.50677,-0.00038,0.00962],"force_p95":46.95771,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.5267,"mean_force":11.65251,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49759,0.03426,0.0301]},{"body_a":"peg","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.5234,0.05846,0.06164],"force_p95":38.35151,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.03939,"mean_force":28.11794,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49161,0.07842,0.02762]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47481,-0.10709,0.05953],"force_p95":6.56804,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.92267,"mean_force":2.90876,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50847,-0.07878,0.03219]},{"body_a":"peg","body_b":"channel_base_body","contact_count":135.0,"contact_point_centroid":[0.50604,0.05546,0.00938],"force_p95":0.58327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.55109,"mean_force":0.62552,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50277,0.09172,0.04435]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50546,0.07438,0.05704],"force_p95":5.05621,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.33914,"mean_force":2.92292,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50211,0.08642,0.03877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50547,0.05653,0.00931],"force_p95":0.75767,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.62609,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51493,0.15248,0.26826]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.48857,-0.15939,-0.00053],"force_p95":4.20459,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20459,"mean_force":4.20459,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50912,-0.0888,0.0318]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5012,0.19476,0.29613]}],"total_contact_groups":18},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.52551,-0.22929,0.01356],"final_tcp_position":[0.50685,-0.08846,0.11223],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":833.31818,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":780.0,"object_pos_end":[0.50613,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52504,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":237.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.52825,0.11375,0.24485],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05662,0.03377],"object_pos_start":[0.50613,0.0566,0.03377],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03383,"peak_contact_force":0.51533,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":360.0,"raw_peak_contact_force":0.64921,"subtask_id":"approach","tcp_end":[0.50559,0.09796,0.05344],"tcp_start":[0.52825,0.11375,0.24485],"tcp_to_object_dist_end":0.04579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":135.0,"n_steps_budget":600.0,"object_pos_end":[0.50605,0.05623,0.03426],"object_pos_start":[0.50614,0.05662,0.03377],"object_to_goal_dist_end":0.13648,"object_to_goal_dist_start":0.1369,"object_z_max":0.0342,"peak_contact_force":5.55109,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":139.0,"raw_peak_contact_force":5.55109,"subtask_id":"contact","tcp_end":[0.5021,0.08593,0.03829],"tcp_start":[0.50559,0.09796,0.05344],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.49235,-0.14824,0.02625],"object_pos_start":[0.50605,0.05623,0.03426],"object_to_goal_dist_end":0.07003,"object_to_goal_dist_start":0.13648,"object_z_max":0.04276,"peak_contact_force":697.16911,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":969.0,"raw_peak_contact_force":833.31818,"subtask_id":"push","tcp_end":[0.50912,-0.08872,0.03179],"tcp_start":[0.5021,0.08593,0.03829],"tcp_to_object_dist_end":0.06208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":233.0,"n_steps_budget":660.0,"object_pos_end":[0.52551,-0.22929,0.01356],"object_pos_start":[0.49235,-0.14824,0.02625],"object_to_goal_dist_end":0.15375,"object_to_goal_dist_start":0.07003,"object_z_max":0.03071,"peak_contact_force":0.75552,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":242.0,"raw_peak_contact_force":591.61447,"tcp_end":[0.50685,-0.08846,0.11223],"tcp_start":[0.50912,-0.08872,0.03179],"tcp_to_object_dist_end":0.17297,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```