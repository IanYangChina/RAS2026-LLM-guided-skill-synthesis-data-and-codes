## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0994 | 0.42 | ✅ accepted |
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0565 | 0.07 | ❌ rejected |
| 6 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0422 | 0.29 | ❌ rejected |
| 5 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0424 | 0.33 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.1451 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.099) — your mutation base

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

- **Composite score**: 0.099
- **task_score** (E): 0.422
- **fitness_score**: 0.289  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.2093 |
| descend_to_height | 1.00 | 1.00 | 0.0591 |
| contact_peg | 1.00 | 1.00 | 0.0037 |
| push_channel | 0.00 | 1.00 | 0.0419 |
| retract_lift | 0.67 | 1.00 | 0.1474 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.123, 0.107) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.542 | 3.242 |
| descend_to_height | descend | 1.00 / step_budget | (0.516, 0.123, 0.107)→(0.505, 0.117, 0.050) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.333 | 120.645 | 134.846 |
| contact_peg | contact | 1.00 / force_exceeded | (0.505, 0.117, 0.050)→(0.504, 0.116, 0.047) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 20.991 | 21.606 |
| push_channel | push | 0.00 / step_budget | (0.504, 0.116, 0.047)→(0.523, 0.091, 0.059) | (0.505, 0.084, 0.034)→(0.505, -0.007, 0.027) | 0.164→0.077 | 1.00 / 3.000 | 370.143 | 1033.553 |
| retract_lift | retract | 0.67 / step_budget | (0.523, 0.091, 0.059)→(0.506, -0.044, 0.115) | (0.505, -0.007, 0.027)→(0.503, -0.022, 0.026) | 0.077→0.062 | 1.00 / 1.000 | 0.444 | 448.718 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.857
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.857
- phase_score: 0.233
- phase_breakdown.contact_score: 0.801
- phase_breakdown.push_score: 0.034
- phase_breakdown.approach_score: 0.262

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.482
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.857
- **Median Q (composite search score)**: 0.038
- **K-run variance**: 0.0195
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.302


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36364,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.05498,"contact_peg.contact_force":8.55113,"contact_peg.contact_speed":0.02184,"descend_to_height.descend_speed":0.07603,"push_channel.push_distance":0.11343,"push_channel.push_speed":0.06225},"optimized_scores":{"best_composite_score":-0.03281,"best_fitness_score":0.15719,"best_task_score":0.12227},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":113.0,"contact_point_centroid":[0.53626,0.11974,0.05973],"force_p95":462.64619,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":884.97776,"mean_force":284.33572,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49849,0.09444,0.03964]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":842.0,"contact_point_centroid":[0.47496,0.11993,0.05972],"force_p95":608.25696,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":848.83048,"mean_force":403.25711,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51328,0.08802,0.0435]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":891.0,"contact_point_centroid":[0.52504,0.08947,0.04554],"force_p95":486.97974,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":664.04214,"mean_force":271.47563,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51335,0.08758,0.04426]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":753.0,"contact_point_centroid":[0.5251,0.08214,0.05031],"force_p95":357.65889,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":637.11778,"mean_force":295.25609,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5132,0.08108,0.05015]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":525.0,"contact_point_centroid":[0.47494,0.1199,0.05533],"force_p95":562.22755,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":585.35836,"mean_force":481.09907,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51328,0.08069,0.04979]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":109.0,"contact_point_centroid":[0.52507,0.11554,0.05998],"force_p95":397.45585,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":403.40898,"mean_force":356.17872,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.51124,0.11561,0.05619]},{"body_a":"world","body_b":"link7","contact_count":837.0,"contact_point_centroid":[0.50398,0.14417,-6e-05],"force_p95":302.71671,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.49746,"mean_force":214.03832,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51301,0.08072,0.04991]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.50279,0.14346,-3e-05],"force_p95":286.19784,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.71672,"mean_force":218.07378,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51332,0.08195,0.04839]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50585,0.06012,0.00944],"force_p95":0.63726,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.76432,"mean_force":0.86763,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51112,0.08352,0.04879]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.50242,0.09036,0.0468],"force_p95":54.36643,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.15714,"mean_force":14.28302,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49763,0.09515,0.04013]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52504,0.11623,0.05999],"force_p95":48.54434,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.54434,"mean_force":48.54434,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51011,0.11632,0.0529]},{"body_a":"attachment","body_b":"peg","contact_count":71.0,"contact_point_centroid":[0.50865,0.06879,0.05976],"force_p95":4.70378,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.95395,"mean_force":2.00701,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51425,0.07807,0.05495]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":310.0,"contact_point_centroid":[0.52501,0.05842,0.05867],"force_p95":0.24297,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.80873,"mean_force":0.19677,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51334,0.08752,0.04426]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":321.0,"contact_point_centroid":[0.52529,0.0598,0.04941],"force_p95":1.1156,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.64987,"mean_force":0.81512,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50947,0.08337,0.04723]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.5069,0.05685,0.00944],"force_p95":0.7049,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.27204,"mean_force":0.61914,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51342,0.08633,0.04503]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.50565,0.08091,0.00935],"force_p95":0.56141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58453,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51418,0.15789,0.19785]}],"total_contact_groups":19},"final_pose_error":0.0946,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50637,0.0157,0.0291],"final_tcp_position":[0.51438,-0.00522,0.08387],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":884.97776,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54605,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":440.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52863,0.11946,0.10644],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":216.0,"n_steps_budget":660.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":360.83913,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":325.0,"raw_peak_contact_force":403.40898,"tcp_end":[0.51011,0.11632,0.0529],"tcp_start":[0.52863,0.11946,0.10644],"tcp_to_object_dist_end":0.0405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":48.54434,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":48.54434,"subtask_id":"contact","tcp_end":[0.51008,0.11632,0.05287],"tcp_start":[0.51011,0.11632,0.0529],"tcp_to_object_dist_end":0.04048,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":989.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,0.05882,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1611,"object_z_max":0.03742,"peak_contact_force":464.09592,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3549.0,"raw_peak_contact_force":884.97776,"subtask_id":"push","tcp_end":[0.51333,0.08195,0.04836],"tcp_start":[0.51008,0.11632,0.05287],"tcp_to_object_dist_end":0.02807,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50637,0.0157,0.0291],"object_pos_start":[0.50696,0.05882,0.03378],"object_to_goal_dist_end":0.09653,"object_to_goal_dist_start":0.13914,"object_z_max":0.04084,"peak_contact_force":0.15108,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3095.0,"raw_peak_contact_force":848.83048,"tcp_end":[0.51438,-0.00522,0.08387],"tcp_start":[0.51333,0.08195,0.04836],"tcp_to_object_dist_end":0.05917,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77647,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.09495,"contact_peg.contact_force":9.42622,"contact_peg.contact_speed":0.0273,"descend_to_height.descend_speed":0.06994,"push_channel.push_distance":0.14535,"push_channel.push_speed":0.07341},"optimized_scores":{"best_composite_score":0.03849,"best_fitness_score":0.22849,"best_task_score":0.28623},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.55494,0.11985,0.05968],"force_p95":755.16963,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":810.52613,"mean_force":426.69786,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51057,0.13007,0.02135]},{"body_a":"world","body_b":"link7","contact_count":915.0,"contact_point_centroid":[0.50073,0.18415,-5e-05],"force_p95":362.31289,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":759.65513,"mean_force":294.55156,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51297,0.11663,0.03866]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.51515,0.11941,0.00957],"force_p95":565.1935,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":601.23744,"mean_force":301.45385,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50348,0.12109,0.01048]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":875.0,"contact_point_centroid":[0.52505,0.11746,0.03995],"force_p95":199.86413,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":564.21144,"mean_force":183.32483,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51315,0.11656,0.03946]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":572.0,"contact_point_centroid":[0.47269,0.11993,0.05997],"force_p95":310.04951,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.64912,"mean_force":171.34828,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51306,0.09036,0.05031]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":368.0,"contact_point_centroid":[0.52502,0.09613,0.05176],"force_p95":212.26078,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.83525,"mean_force":133.95579,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51378,0.09278,0.04943]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.49552,0.17864,-2e-05],"force_p95":174.83411,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.53721,"mean_force":123.67472,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.5133,0.11334,0.04073]},{"body_a":"peg","body_b":"channel_base_body","contact_count":948.0,"contact_point_centroid":[0.49938,-0.00868,0.00814],"force_p95":0.80682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.49383,"mean_force":0.87331,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51265,0.11694,0.03786]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50602,0.12089,0.04453],"force_p95":100.18909,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.44854,"mean_force":79.87415,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50542,0.13279,0.04401]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52506,0.068,0.0438],"force_p95":23.75471,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.63762,"mean_force":5.4303,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50986,0.12715,0.03766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.50644,0.09961,0.00936],"force_p95":2.40629,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.29155,"mean_force":1.15028,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50477,0.13482,0.04658]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50587,0.12256,0.04976],"force_p95":8.74424,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.07476,"mean_force":3.03981,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50437,0.13453,0.04576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":948.0,"contact_point_centroid":[0.50306,-0.01057,0.00803],"force_p95":0.72553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.17741,"mean_force":0.61361,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51141,0.06664,0.06198]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47493,0.01181,0.02437],"force_p95":8.26389,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.57456,"mean_force":2.28567,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51316,0.11937,0.03875]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.525,-0.03404,0.02432],"force_p95":7.4005,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.17875,"mean_force":2.97221,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51041,0.08791,0.05154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50553,0.10474,0.00936],"force_p95":0.58322,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57749,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50911,0.169,0.19842]}],"total_contact_groups":18},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50093,-0.01071,0.0241],"final_tcp_position":[0.49977,-0.06377,0.12838],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":810.52613,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10461,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53281,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":395.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.5187,0.14101,0.10784],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":141.0,"n_steps_budget":690.0,"object_pos_end":[0.506,0.10468,0.03384],"object_pos_start":[0.50599,0.10461,0.03384],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18481,"object_z_max":0.03384,"peak_contact_force":0.55138,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":141.0,"raw_peak_contact_force":0.57865,"tcp_end":[0.50588,0.13537,0.04856],"tcp_start":[0.5187,0.14101,0.10784],"tcp_to_object_dist_end":0.03404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":19.0,"n_steps_budget":600.0,"object_pos_end":[0.50583,0.1043,0.03382],"object_pos_start":[0.506,0.10468,0.03384],"object_to_goal_dist_end":0.18449,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":10.29155,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":23.0,"raw_peak_contact_force":10.29155,"subtask_id":"contact","tcp_end":[0.50408,0.1341,0.04488],"tcp_start":[0.50588,0.13537,0.04856],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,-0.01064,0.02414],"object_pos_start":[0.50583,0.1043,0.03382],"object_to_goal_dist_end":0.07124,"object_to_goal_dist_start":0.18449,"object_z_max":0.04566,"peak_contact_force":292.10455,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2807.0,"raw_peak_contact_force":810.52613,"subtask_id":"push","tcp_end":[0.51328,0.11335,0.04072],"tcp_start":[0.50408,0.1341,0.04488],"tcp_to_object_dist_end":0.12546,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,-0.01071,0.0241],"object_pos_start":[0.50369,-0.01064,0.02414],"object_to_goal_dist_end":0.07109,"object_to_goal_dist_start":0.07124,"object_z_max":0.02471,"peak_contact_force":0.56202,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1895.0,"raw_peak_contact_force":337.64912,"tcp_end":[0.49977,-0.06377,0.12838],"tcp_start":[0.51328,0.11335,0.04072],"tcp_to_object_dist_end":0.11701,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35185,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.04238,"contact_peg.contact_force":3.40516,"contact_peg.contact_speed":0.02463,"descend_to_height.descend_speed":0.07586,"push_channel.push_distance":0.18447,"push_channel.push_speed":0.11942},"optimized_scores":{"best_composite_score":0.29241,"best_fitness_score":0.48241,"best_task_score":0.85659},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":851.0,"contact_point_centroid":[0.52655,0.11951,0.05994],"force_p95":352.12888,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1405.15435,"mean_force":308.78074,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52954,0.071,0.088]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52588,0.08664,0.05959],"force_p95":1226.8252,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1284.57994,"mean_force":659.83775,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50335,0.08242,0.03758]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":211.0,"contact_point_centroid":[0.52502,0.11997,0.05996],"force_p95":143.0718,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.67412,"mean_force":117.89358,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.53686,0.0681,0.09091]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50468,0.08105,0.04942],"force_p95":56.47076,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.49397,"mean_force":23.27787,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50005,0.09222,0.03971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":815.0,"contact_point_centroid":[0.50153,-0.06756,0.00812],"force_p95":0.84024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.88679,"mean_force":0.83941,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5307,0.0708,0.08964]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47491,-0.0468,0.02445],"force_p95":7.99814,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.45764,"mean_force":1.9966,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52506,0.06696,0.09185]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":47.0,"contact_point_centroid":[0.52661,0.01349,0.03748],"force_p95":2.92344,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.78902,"mean_force":0.94369,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50494,0.08054,0.04765]},{"body_a":"peg","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.50187,0.06458,0.00937],"force_p95":1.46495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.98073,"mean_force":0.79409,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49733,0.09798,0.04444]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50232,0.08529,0.0542],"force_p95":5.18317,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.4833,"mean_force":2.16344,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49696,0.09712,0.04278]},{"body_a":"peg","body_b":"channel_base_body","contact_count":420.0,"contact_point_centroid":[0.50308,0.06741,0.00933],"force_p95":0.57264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56713,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49918,0.15314,0.20117]},{"body_a":"peg","body_b":"channel_base_body","contact_count":523.0,"contact_point_centroid":[0.50268,-0.06953,0.00805],"force_p95":0.6971,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6971,"mean_force":0.60592,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.52629,0.02723,0.10251]},{"body_a":"peg","body_b":"channel_base_body","contact_count":145.0,"contact_point_centroid":[0.50294,0.06743,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_height","phase_type":"descend","tcp_position_centroid":[0.49849,0.10329,0.0777]}],"total_contact_groups":12},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50136,-0.06959,0.02414],"final_tcp_position":[0.50328,-0.06244,0.13136],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":1405.15435,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54706,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":420.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49969,0.10749,0.10697],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":145.0,"n_steps_budget":630.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.5451,"phase_name":"descend_to_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":145.0,"raw_peak_contact_force":0.55115,"tcp_end":[0.49865,0.0993,0.04781],"tcp_start":[0.49969,0.10749,0.10697],"tcp_to_object_dist_end":0.03505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":40.0,"n_steps_budget":600.0,"object_pos_end":[0.50286,0.067,0.03416],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.14714,"object_to_goal_dist_start":0.14764,"object_z_max":0.03411,"peak_contact_force":4.13854,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":45.0,"raw_peak_contact_force":5.98073,"subtask_id":"contact","tcp_end":[0.49686,0.09651,0.04178],"tcp_start":[0.49865,0.0993,0.04781],"tcp_to_object_dist_end":0.03107,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.50392,-0.06943,0.02414],"object_pos_start":[0.50286,0.067,0.03416],"object_to_goal_dist_end":0.01946,"object_to_goal_dist_start":0.14714,"object_z_max":0.04723,"peak_contact_force":354.2289,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1753.0,"raw_peak_contact_force":1405.15435,"subtask_id":"push","tcp_end":[0.54099,0.07626,0.089],"tcp_start":[0.49686,0.09651,0.04178],"tcp_to_object_dist_end":0.16372,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.50136,-0.06959,0.02414],"object_pos_start":[0.50392,-0.06943,0.02414],"object_to_goal_dist_end":0.01902,"object_to_goal_dist_start":0.01946,"object_z_max":0.02414,"peak_contact_force":0.61749,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":734.0,"raw_peak_contact_force":159.67412,"tcp_end":[0.50328,-0.06244,0.13136],"tcp_start":[0.54099,0.07626,0.089],"tcp_to_object_dist_end":0.10747,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```