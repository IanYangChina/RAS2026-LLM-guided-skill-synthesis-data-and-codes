## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0852 | 0.25 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1283 | 0.30 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.1587 | 0.24 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.3294 | 0.20 | ✅ accepted |
| 4 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |

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

- Task name: grasp_place
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.085) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_to_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: check_object_held
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.05
  subtask_id: reach_goal
- id: release
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
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
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_object_held, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.05]
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.085
- **task_score** (E): 0.251
- **fitness_score**: 0.400  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.214
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2115 |
| descend_to_grasp | 1.00 | 1.00 | 0.0133 |
| grasp | 1.00 | 1.00 | 0.0257 |
| lift | 1.00 | 1.00 | 0.2045 |
| transport_to_goal | 1.00 | 1.00 | 0.1785 |
| release | 1.00 | 1.00 | 0.0195 |
| retract | 1.00 | 1.00 | 0.0839 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.093) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.506, 0.002, 0.093)→(0.517, -0.001, 0.087) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 405.967 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.512, -0.001, 0.081)→(0.505, -0.003, 0.056) | (0.511, 0.002, 0.026)→(0.512, -0.003, 0.025) | 0.246→0.249 | 1.00 / 19.667 | 0.170 | 0.454 |
| lift | lift | 1.00 / step_budget | (0.505, -0.003, 0.056)→(0.503, -0.003, 0.261) | (0.512, -0.003, 0.025)→(0.514, -0.002, 0.080) | 0.249→0.227 | 1.00 / 19.333 | 91001.472 | 1.164 |
| transport_to_goal | approach | 1.00 / step_budget | (0.546, -0.014, 0.180)→(0.635, 0.141, 0.181) | (0.553, -0.012, 0.187)→(0.635, 0.141, 0.174) | 0.194→0.028 | 1.00 / 40.000 | 0.074 | 0.102 |
| release | release | 1.00 / step_budget | (0.635, 0.141, 0.181)→(0.629, 0.140, 0.200) | (0.635, 0.141, 0.174)→(0.622, 0.139, 0.025) | 0.028→0.169 | 1.00 / 4.000 | 0.079 | 1.530 |
| retract | retract | 1.00 / step_budget | (0.629, 0.140, 0.200)→(0.627, 0.139, 0.283) | (0.622, 0.139, 0.025)→(0.620, 0.139, 0.026) | 0.169→0.168 | 1.00 / 4.000 | 0.123 | 0.142 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.325
- phase_score: 0.610
- phase_breakdown.reach_object_score: 0.574
- phase_breakdown.reach_goal_score: 0.626
- grasp_place_fitness: 0.640

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.640
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.325
- **Median Q (composite search score)**: -0.127
- **K-run variance**: 0.0153
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.365


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.02381,"average_solve_count":42.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05031,"approach_to_object.approach_speed":0.24191,"descend_to_grasp.descend_depth":0.22133,"descend_to_grasp.descend_force_threshold":10.78173,"descend_to_grasp.descend_speed":0.05411,"grasp.grasp_duration":0.48807,"lift.lift_height":0.18819,"lift.lift_speed":0.27505,"release.release_duration":0.42198,"retract.retract_speed":0.3269,"transport_to_goal.transport_speed":0.22232},"optimized_scores":{"best_composite_score":-0.21158,"best_fitness_score":0.23842,"best_task_score":0.13208},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2156.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13209,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.47801,-0.01202,0.19483]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45722,-0.02437,0.08973]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45081,-0.02362,0.08191]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44696,-0.02347,0.16355]},{"body_a":"left_finger","body_b":"right_finger","contact_count":751.0,"contact_point_centroid":[0.45016,-0.02361,0.08347],"force_p95":0.01278,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01095,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44997,-0.0236,0.08105]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2269.0,"contact_point_centroid":[0.44719,-0.02347,0.16612],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01063,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44696,-0.02347,0.16388]}],"total_contact_groups":6},"final_pose_error":0.01747,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45856,-0.02632,0.02602],"final_tcp_position":[0.44741,-0.02348,0.25196],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":406.52122,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2156.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45719,-0.02443,0.08992],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":406.52122,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45741,-0.02405,0.08911],"tcp_start":[0.45719,-0.02443,0.08992],"tcp_to_object_dist_end":0.06314,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2951.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.44997,-0.0236,0.08105],"tcp_start":[0.44997,-0.0236,0.08105],"tcp_to_object_dist_end":0.05577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4437.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.44741,-0.02348,0.25196],"tcp_start":[0.44997,-0.0236,0.08105],"tcp_to_object_dist_end":0.22624,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":48.0,"average_failure_rate":0.23645,"average_mean_iterations":50.53695,"average_solve_count":203.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.06638,"approach_to_object.approach_speed":0.05428,"descend_to_grasp.descend_depth":0.09373,"descend_to_grasp.descend_force_threshold":8.78637,"descend_to_grasp.descend_speed":0.0362,"grasp.grasp_duration":0.63491,"lift.lift_height":0.19534,"lift.lift_speed":0.10793,"release.release_duration":0.98641,"retract.retract_speed":0.21785,"transport_to_goal.transport_speed":0.3998},"optimized_scores":{"best_composite_score":0.08296,"best_fitness_score":0.64011,"best_task_score":0.32521},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":3.0,"contact_point_centroid":[0.5503,0.01245,-1e-05],"force_p95":3.18218,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.24791,"mean_force":2.32765,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54987,-0.01341,0.01031]},{"body_a":"world","body_b":"grasp_target","contact_count":229.0,"contact_point_centroid":[0.61967,0.13917,-0.00653],"force_p95":1.00677,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52962,"mean_force":0.31553,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62921,0.14003,0.19091]},{"body_a":"world","body_b":"right_finger","contact_count":966.0,"contact_point_centroid":[0.54879,0.02032,-0.00016],"force_p95":0.98051,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.11762,"mean_force":0.54934,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.55011,-0.01333,0.01054]},{"body_a":"world","body_b":"grasp_target","contact_count":243.0,"contact_point_centroid":[0.54488,-0.01244,-0.00178],"force_p95":0.80418,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06094,"mean_force":0.16564,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54756,-0.01351,0.0128]},{"body_a":"grasp_target","body_b":"hand","contact_count":405.0,"contact_point_centroid":[0.56212,0.01831,0.04901],"force_p95":0.36992,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68535,"mean_force":0.31982,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.55041,-0.01337,0.01095]},{"body_a":"grasp_target","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.56629,-0.00088,0.12847],"force_p95":0.26092,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41569,"mean_force":0.15995,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5455,-0.01359,0.09245]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54442,-0.00375,-0.00289],"force_p95":0.31595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34592,"mean_force":0.2367,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5535,-0.01334,0.01496]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19959.0,"contact_point_centroid":[0.55031,-0.032,0.09565],"force_p95":0.07779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26725,"mean_force":0.04929,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54549,-0.01359,0.09262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.5418,0.00532,0.09302],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26609,"mean_force":0.05188,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5455,-0.01359,0.09245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5326.0,"contact_point_centroid":[0.54287,0.01337,0.01031],"force_p95":0.10923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18335,"mean_force":0.05708,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.55006,-0.0133,0.01046]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.6197,0.13919,-0.00197],"force_p95":0.12862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14232,"mean_force":0.12147,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62668,0.13928,0.23905]},{"body_a":"world","body_b":"grasp_target","contact_count":2816.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.5173,0.00049,0.20057]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54734,-0.00298,0.09636]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1233.0,"contact_point_centroid":[0.62934,0.16019,0.17744],"force_p95":0.07374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11691,"mean_force":0.04328,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63306,0.14125,0.17691]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":358.0,"contact_point_centroid":[0.55841,-0.03095,0.0144],"force_p95":0.10134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11035,"mean_force":0.04938,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54999,-0.01336,0.01035]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.63798,0.12287,0.18],"force_p95":0.07057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10781,"mean_force":0.04109,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63308,0.14126,0.17695]}],"total_contact_groups":19},"final_pose_error":0.01626,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61969,0.13919,0.02602],"final_tcp_position":[0.62705,0.13936,0.28345],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":434.85024,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2816.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53716,0.001,0.10314],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":434.85024,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":84.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56935,-0.0092,0.08497],"tcp_start":[0.53716,0.001,0.10314],"tcp_to_object_dist_end":0.06488,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54715,-0.01258,0.02418],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25901,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.26465,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8855.0,"raw_peak_contact_force":1.11762,"tcp_end":[0.54999,-0.0134,0.01035],"tcp_start":[0.56935,-0.0092,0.08497],"tcp_to_object_dist_end":0.01414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55309,-0.01166,0.18682],"object_pos_start":[0.54715,-0.01258,0.02418],"object_to_goal_dist_end":0.19435,"object_to_goal_dist_start":0.25901,"object_z_max":0.18667,"peak_contact_force":0.07581,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41205.0,"raw_peak_contact_force":3.24791,"tcp_end":[0.54618,-0.01356,0.18019],"tcp_start":[0.54999,-0.0134,0.01035],"tcp_to_object_dist_end":0.00976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63458,0.14098,0.17358],"object_pos_start":[0.55309,-0.01166,0.18682],"object_to_goal_dist_end":0.02774,"object_to_goal_dist_start":0.19435,"object_z_max":0.18692,"peak_contact_force":0.07408,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40089.0,"raw_peak_contact_force":0.10249,"subtask_id":"reach_goal","tcp_end":[0.63475,0.14137,0.1809],"tcp_start":[0.54618,-0.01356,0.18019],"tcp_to_object_dist_end":0.00733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62208,0.13939,0.02505],"object_pos_start":[0.63458,0.14098,0.17358],"object_to_goal_dist_end":0.16904,"object_to_goal_dist_start":0.02774,"object_z_max":0.17358,"peak_contact_force":0.07928,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2682.0,"raw_peak_contact_force":1.52962,"tcp_end":[0.62918,0.14002,0.19956],"tcp_start":[0.63475,0.14137,0.1809],"tcp_to_object_dist_end":0.17465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":600.0,"object_pos_end":[0.61969,0.13919,0.02602],"object_pos_start":[0.62208,0.13939,0.02505],"object_to_goal_dist_end":0.16849,"object_to_goal_dist_start":0.16904,"object_z_max":0.02667,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.14232,"tcp_end":[0.62705,0.13936,0.28345],"tcp_start":[0.62918,0.14002,0.19956],"tcp_to_object_dist_end":0.25754,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":13.0,"average_failure_rate":0.17808,"average_mean_iterations":41.06849,"average_solve_count":73.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05007,"approach_to_object.approach_speed":0.15958,"descend_to_grasp.descend_depth":0.142,"descend_to_grasp.descend_force_threshold":12.89457,"descend_to_grasp.descend_speed":0.12569,"grasp.grasp_duration":0.93684,"lift.lift_height":0.29173,"lift.lift_speed":0.21244,"release.release_duration":0.41527,"retract.retract_speed":0.19787,"transport_to_goal.transport_speed":0.23123},"optimized_scores":{"best_composite_score":-0.12713,"best_fitness_score":0.32287,"best_task_score":0.29452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2504.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51099,0.01418,0.19291]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51745,0.02863,0.07821]},{"body_a":"world","body_b":"grasp_target","contact_count":3284.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51359,0.02837,0.20806]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52429,0.02869,0.08737]},{"body_a":"left_finger","body_b":"right_finger","contact_count":754.0,"contact_point_centroid":[0.51688,0.02857,0.0793],"force_p95":0.01292,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01091,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51651,0.02857,0.07707]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3505.0,"contact_point_centroid":[0.51406,0.02837,0.21049],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01264,"mean_force":0.01045,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5136,0.02837,0.20828]}],"total_contact_groups":6},"final_pose_error":0.01919,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5305,0.03079,0.02602],"final_tcp_position":[0.51495,0.02844,0.34967],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273004.21695,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2504.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52429,0.02869,0.08737],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":376.52868,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12262,"tcp_end":[0.52442,0.02901,0.08702],"tcp_start":[0.52429,0.02869,0.08737],"tcp_to_object_dist_end":0.06133,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2954.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51651,0.02857,0.07707],"tcp_start":[0.51651,0.02857,0.07707],"tcp_to_object_dist_end":0.05298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":821.0,"n_steps_budget":870.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":273004.21695,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6789.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51495,0.02844,0.34967],"tcp_start":[0.51651,0.02857,0.07707],"tcp_to_object_dist_end":0.32404,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```