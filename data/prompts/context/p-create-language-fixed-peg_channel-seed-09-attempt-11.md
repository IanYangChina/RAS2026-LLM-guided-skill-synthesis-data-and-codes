## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | align → approach → approach → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | 0.0368 | 0.24 | ❌ rejected |
| 10 | align → approach → descend → contact → push | joint_interpolation | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.2295 | 0.09 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.1992 | 0.00 | ❌ rejected |
| 8 | align → approach → approach → descend → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.0611 | 0.34 | ✅ accepted |
| 7 | align → approach → descend → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.1917 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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

## Current Skill (Q=0.037) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: align
  type: align
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
- id: approach_entry
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - -0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    entry_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_peg
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.018
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact
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
    - 0.018
    - 0.0
    tolerance: 0.02
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
- id: push
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.018
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 1.0
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
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
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align** (`align`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.05
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings: none
- **approach_entry** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, -0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - entry_speed: status=consumed; consumers=generator.speed (replace)
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.018, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.018, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.018, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.037
- **task_score** (E): 0.238
- **fitness_score**: 0.343  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align | 1.00 | 1.00 | 0.0041 |
| approach_entry | 1.00 | 1.00 | 0.2081 |
| approach_peg | 1.00 | 1.00 | 0.0647 |
| contact | 0.33 | 1.00 | 0.0129 |
| push | 1.00 | 1.00 | 0.1112 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.203, 0.299) | (0.512, 0.067, 0.040)→(0.507, 0.067, 0.038) | 0.150→0.148 | 1.00 / 1.000 | 0.133 | 3.257 |
| approach_entry | approach | 1.00 / step_budget | (0.498, 0.203, 0.299)→(0.503, 0.107, 0.115) | (0.507, 0.067, 0.038)→(0.502, 0.067, 0.034) | 0.148→0.147 | 1.00 / 1.000 | 0.545 | 4.034 |
| approach_peg | approach | 1.00 / step_budget | (0.503, 0.107, 0.115)→(0.502, 0.091, 0.053) | (0.502, 0.067, 0.034)→(0.503, 0.065, 0.032) | 0.147→0.145 | 1.00 / 2.000 | 10.017 | 170.493 |
| contact | contact | 0.33 / step_budget | (0.502, 0.091, 0.053)→(0.499, 0.087, 0.041) | (0.503, 0.065, 0.032)→(0.501, 0.034, 0.027) | 0.145→0.116 | 1.00 / 1.333 | 4.743 | 16.346 |
| push | push | 1.00 / time_limit | (0.499, 0.087, 0.041)→(0.497, -0.024, 0.027) | (0.501, 0.034, 0.027)→(0.504, -0.060, 0.027) | 0.116→0.025 | 1.00 / 3.000 | 18.984 | 33.780 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.790
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.212
- phase_score: 0.383
- phase_breakdown.approach_score: 0.560
- phase_breakdown.push_score: 0.242
- phase_breakdown.contact_score: 0.628

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.360
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.277
- **Median Q (composite search score)**: -0.030
- **K-run variance**: 0.0095
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.446


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57292,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.entry_speed":0.45481,"approach_peg.approach_speed":0.16553,"contact.contact_force":14.98602,"push.push_depth":0.15221,"push.push_duration":3.85849,"push.push_speed":0.06405},"optimized_scores":{"best_composite_score":-0.03457,"best_fitness_score":0.35543,"best_task_score":0.27743},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.50772,0.06471,0.00931],"force_p95":159.6095,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.22135,"mean_force":22.35741,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50806,0.0952,0.0824]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.51336,0.07894,0.05649],"force_p95":168.38269,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.7303,"mean_force":130.07455,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50611,0.08809,0.05602]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.53532,-0.01018,0.06],"force_p95":33.47136,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.48483,"mean_force":24.53039,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49932,-0.01692,0.02513]},{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.50407,0.0347,0.00904],"force_p95":2.92103,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.23285,"mean_force":1.21781,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50474,0.08469,0.04389]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50652,0.07655,0.05298],"force_p95":14.84046,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.60227,"mean_force":6.99943,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50688,0.08703,0.05186]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50458,-0.01272,0.00913],"force_p95":3.85946,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.11754,"mean_force":1.16205,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49929,0.0292,0.02768]},{"body_a":"attachment","body_b":"peg","contact_count":521.0,"contact_point_centroid":[0.50268,0.00437,0.04366],"force_p95":4.644,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.02203,"mean_force":1.51221,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49909,0.01636,0.02676]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":155.0,"contact_point_centroid":[0.52502,-0.0465,0.02731],"force_p95":4.1174,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.13307,"mean_force":1.65901,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49908,0.01395,0.02663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.50561,0.0629,0.00934],"force_p95":0.59657,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58488,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.50445,0.15354,0.20485]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.53373,0.06295,0.0362],"force_p95":1.36479,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.64647,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52714,0.06295,0.02495],"force_p95":0.76857,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85654,"mean_force":0.24853,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49761,0.20286,0.29672]}],"total_contact_groups":11},"final_pose_error":0.09515,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50442,-0.05894,0.02661],"final_tcp_position":[0.49962,-0.02202,0.0251],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":169.22135,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.5166,0.06295,0.03827],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.18909,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":2.98455,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":361.0,"n_steps_budget":600.0,"object_pos_end":[0.50594,0.063,0.03381],"object_pos_start":[0.5166,0.06295,0.03827],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14392,"object_z_max":0.03827,"peak_contact_force":0.54403,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":367.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.51194,0.10382,0.11416],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.09032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.5063,0.06159,0.03192],"object_pos_start":[0.50594,0.063,0.03381],"object_to_goal_dist_end":0.14197,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":1.68777,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":153.0,"raw_peak_contact_force":169.22135,"subtask_id":"approach","tcp_end":[0.50726,0.08724,0.05264],"tcp_start":[0.51194,0.10382,0.11416],"tcp_to_object_dist_end":0.03299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":102.0,"n_steps_budget":600.0,"object_pos_end":[0.50272,0.0171,0.02382],"object_pos_start":[0.5063,0.06159,0.03192],"object_to_goal_dist_end":0.09848,"object_to_goal_dist_start":0.14197,"object_z_max":0.04079,"peak_contact_force":0.6641,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":96.0,"raw_peak_contact_force":16.23285,"subtask_id":"contact","tcp_end":[0.50317,0.08177,0.03505],"tcp_start":[0.50726,0.08724,0.05264],"tcp_to_object_dist_end":0.06564,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50442,-0.05894,0.02661],"object_pos_start":[0.50272,0.0171,0.02382],"object_to_goal_dist_end":0.02534,"object_to_goal_dist_start":0.09848,"object_z_max":0.02773,"peak_contact_force":24.67377,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1726.0,"raw_peak_contact_force":42.48483,"subtask_id":"push","tcp_end":[0.49962,-0.02202,0.0251],"tcp_start":[0.50317,0.08177,0.03505],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61458,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.entry_speed":0.55564,"approach_peg.approach_speed":0.27752,"contact.contact_force":9.92903,"push.push_depth":0.20129,"push.push_duration":3.15662,"push.push_speed":0.0695},"optimized_scores":{"best_composite_score":-0.02981,"best_fitness_score":0.36019,"best_task_score":0.223},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":130.0,"contact_point_centroid":[0.50719,0.05746,0.00931],"force_p95":155.33826,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.67548,"mean_force":17.04777,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51028,0.08925,0.08265]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.51256,0.07208,0.05611],"force_p95":162.66332,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.22263,"mean_force":107.41595,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50721,0.08189,0.05587]},{"body_a":"attachment","body_b":"peg","contact_count":542.0,"contact_point_centroid":[0.5035,-0.00905,0.04465],"force_p95":7.33432,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.15544,"mean_force":2.43106,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49984,0.00293,0.02744]},{"body_a":"peg","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.48931,-0.10035,0.02761],"force_p95":27.00051,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.87625,"mean_force":18.21522,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5002,-0.03783,0.02545]},{"body_a":"peg","body_b":"channel_base_body","contact_count":69.0,"contact_point_centroid":[0.50538,0.01274,0.00767],"force_p95":2.57953,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.05207,"mean_force":1.03594,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50465,0.07727,0.04229]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50723,0.06949,0.0524],"force_p95":19.32746,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.32746,"mean_force":19.32746,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50775,0.081,0.05235]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5052,-0.02377,0.00919],"force_p95":4.39828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.33579,"mean_force":1.33341,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49992,0.01752,0.02836]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":158.0,"contact_point_centroid":[0.52503,-0.06063,0.02734],"force_p95":5.04985,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.37597,"mean_force":2.11883,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49987,-3e-05,0.0273]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.50574,0.05662,0.00934],"force_p95":0.60305,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.59092,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.50612,0.15044,0.20455]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.5365,0.05661,0.03623],"force_p95":1.44525,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.75988,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.03534,0.06],"force_p95":1.22643,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22643,"mean_force":1.22643,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50663,0.08046,0.05025]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52781,0.05661,0.01411],"force_p95":0.88065,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04601,"mean_force":0.25192,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49768,0.20249,0.29609]}],"total_contact_groups":12},"final_pose_error":0.13544,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50542,-0.0747,0.02788],"final_tcp_position":[0.50034,-0.03871,0.02546],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":164.67548,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.52027,0.05661,0.03869],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13812,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.14277,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":3.83578,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.50615,0.05658,0.03377],"object_pos_start":[0.52027,0.05661,0.03869],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.13812,"object_z_max":0.03869,"peak_contact_force":0.56183,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":376.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.51525,0.09798,0.11417],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.09089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":130.0,"n_steps_budget":600.0,"object_pos_end":[0.5063,0.05348,0.03285],"object_pos_start":[0.50615,0.05658,0.03377],"object_to_goal_dist_end":0.13381,"object_to_goal_dist_start":0.13686,"object_z_max":0.03377,"peak_contact_force":26.83036,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":150.0,"raw_peak_contact_force":164.67548,"subtask_id":"approach","tcp_end":[0.50775,0.081,0.05235],"tcp_start":[0.51525,0.09798,0.11417],"tcp_to_object_dist_end":0.03376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":100.0,"n_steps_budget":600.0,"object_pos_end":[0.50506,0.00924,0.02341],"object_pos_start":[0.5063,0.05348,0.03285],"object_to_goal_dist_end":0.09091,"object_to_goal_dist_start":0.13381,"object_z_max":0.04138,"peak_contact_force":0.80978,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":71.0,"raw_peak_contact_force":20.05207,"subtask_id":"contact","tcp_end":[0.5033,0.07439,0.03559],"tcp_start":[0.50775,0.081,0.05235],"tcp_to_object_dist_end":0.0663,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50542,-0.0747,0.02788],"object_pos_start":[0.50506,0.00924,0.02341],"object_to_goal_dist_end":0.0143,"object_to_goal_dist_start":0.09091,"object_z_max":0.02786,"peak_contact_force":32.15544,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1723.0,"raw_peak_contact_force":32.15544,"subtask_id":"push","tcp_end":[0.50034,-0.03871,0.02546],"tcp_start":[0.5033,0.07439,0.03559],"tcp_to_object_dist_end":0.03643,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53125,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.entry_speed":0.72757,"approach_peg.approach_speed":0.05013,"contact.contact_force":12.74365,"push.push_depth":0.12887,"push.push_duration":1.76041,"push.push_speed":0.06981},"optimized_scores":{"best_composite_score":0.17469,"best_fitness_score":0.31469,"best_task_score":0.21224},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":148.0,"contact_point_centroid":[0.49563,0.0822,0.00931],"force_p95":155.73265,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.5832,"mean_force":22.55647,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48463,0.11133,0.08335]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.49735,0.09715,0.05655],"force_p95":176.93475,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.10102,"mean_force":130.45941,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48854,0.10458,0.05619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":937.0,"contact_point_centroid":[0.50273,0.00208,0.00923],"force_p95":10.99396,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.69985,"mean_force":3.1749,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48888,0.04786,0.03961]},{"body_a":"attachment","body_b":"peg","contact_count":591.0,"contact_point_centroid":[0.49403,0.0174,0.04516],"force_p95":15.93368,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.33853,"mean_force":5.74409,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4895,0.02888,0.03678]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":336.0,"contact_point_centroid":[0.52503,-0.02669,0.02823],"force_p95":8.47794,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.18673,"mean_force":4.81842,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48954,0.02832,0.03673]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.4972,0.06112,0.00818],"force_p95":12.69015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.75403,"mean_force":9.90141,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49057,0.10374,0.05214]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49279,0.09357,0.05425],"force_p95":11.85455,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.01846,"mean_force":8.80514,"phase_index":3.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49057,0.10374,0.05214]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47489,0.05781,0.02439],"force_p95":7.80091,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.21018,"mean_force":2.07674,"phase_index":4.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48725,0.08794,0.04519]},{"body_a":"peg","body_b":"channel_base_body","contact_count":335.0,"contact_point_centroid":[0.49434,0.07989,0.00936],"force_p95":0.61343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.58461,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.48977,0.16141,0.20577]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.46621,0.07994,0.03877],"force_p95":1.38176,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.64457,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47289,0.07995,0.02378],"force_p95":0.64934,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74814,"mean_force":0.21246,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49732,0.20286,0.29645]}],"total_contact_groups":11},"final_pose_error":0.02417,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50156,-0.04638,0.02737],"final_tcp_position":[0.49108,-0.01024,0.03127],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":177.5832,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.4833,0.07995,0.03833],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16082,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.06788,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":2.95027,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":600.0,"object_pos_end":[0.49381,0.07996,0.03378],"object_pos_start":[0.4833,0.07995,0.03833],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16082,"object_z_max":0.03833,"peak_contact_force":0.52908,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":350.0,"raw_peak_contact_force":3.77147,"tcp_end":[0.48241,0.11947,0.1157],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.09166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.49567,0.07876,0.03175],"object_pos_start":[0.49381,0.07996,0.03378],"object_to_goal_dist_end":0.15903,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":1.53305,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":173.0,"raw_peak_contact_force":177.5832,"subtask_id":"approach","tcp_end":[0.49086,0.10389,0.05257],"tcp_start":[0.48241,0.11947,0.1157],"tcp_to_object_dist_end":0.03299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.49594,0.07698,0.03251],"object_pos_start":[0.49567,0.07876,0.03175],"object_to_goal_dist_end":0.15721,"object_to_goal_dist_start":0.15903,"object_z_max":0.03218,"peak_contact_force":12.75403,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":8.0,"raw_peak_contact_force":12.75403,"subtask_id":"contact","tcp_end":[0.49018,0.10356,0.05157],"tcp_start":[0.49086,0.10389,0.05257],"tcp_to_object_dist_end":0.03321,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50156,-0.04638,0.02737],"object_pos_start":[0.49594,0.07698,0.03251],"object_to_goal_dist_end":0.03595,"object_to_goal_dist_start":0.15721,"object_z_max":0.0408,"peak_contact_force":0.12217,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1880.0,"raw_peak_contact_force":26.69985,"subtask_id":"push","tcp_end":[0.49108,-0.01024,0.03127],"tcp_start":[0.49018,0.10356,0.05157],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```