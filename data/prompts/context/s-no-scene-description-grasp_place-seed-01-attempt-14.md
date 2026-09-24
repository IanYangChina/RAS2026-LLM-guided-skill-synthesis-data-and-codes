## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2334 | 0.36 | ✅ accepted |
| 13 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 12 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 11 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 10 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.233) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: lift_object
  anchor: object
  metric: goal_progress
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_goal
  weight: 0.5
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp_object
  type: grasp
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.003
    orientation:
      mode: keep_current
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: grasp_contact_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: lift_object
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
    - 0.12
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: lifted
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: lift_object
- id: approach_goal
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
    - 0.08
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_place
  type: descend
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
    tolerance: 0.003
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
- id: release_object
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
    max_release_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.003
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=grasp_contact_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lifted, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.003
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_release_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.233
- **task_score** (E): 0.355
- **fitness_score**: 0.653  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1879 |
| grasp_object | 1.00 | 1.00 | 0.0819 |
| lift_object | 1.00 | 1.00 | 0.1070 |
| approach_goal | 0.00 | 1.00 | 0.1022 |
| descend_place | 0.00 | 1.00 | 0.0782 |
| release_object | 1.00 | 1.00 | 0.0234 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.001, 0.118) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_object | grasp | 1.00 / step_budget | (0.476, -0.001, 0.118)→(0.469, -0.001, 0.036) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.137 | 0.177 |
| lift_object | lift | 1.00 / step_budget | (0.469, -0.001, 0.036)→(0.466, -0.001, 0.143) | (0.479, -0.001, 0.026)→(0.480, -0.001, 0.126) | 0.278→0.250 | 1.00 / 26.333 | 0.106 | 0.563 |
| approach_goal | approach | 0.00 / step_budget | (0.466, -0.001, 0.143)→(0.519, 0.078, 0.172) | (0.480, -0.001, 0.126)→(0.520, 0.085, 0.099) | 0.250→0.180 | 1.00 / 21.000 | 0.107 | 0.642 |
| descend_place | descend | 0.00 / step_budget | (0.519, 0.078, 0.172)→(0.559, 0.141, 0.157) | (0.520, 0.085, 0.099)→(0.545, 0.136, 0.039) | 0.180→0.159 | 1.00 / 9.667 | 0.277 | 0.636 |
| release_object | release | 1.00 / step_budget | (0.559, 0.141, 0.157)→(0.553, 0.139, 0.180) | (0.545, 0.136, 0.039)→(0.548, 0.144, 0.018) | 0.159→0.161 | 1.00 / 3.333 | 0.244 | 0.646 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.435
- phase_score: 0.290
- phase_breakdown.place_goal_score: 0.110
- phase_breakdown.lift_object_score: 0.043
- phase_breakdown.reach_object_score: 0.755
- grasp_place_fitness: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.690
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.435
- **Median Q (composite search score)**: 0.251
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.241


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45509,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09367,"approach_object.approach_speed":0.04526,"descend_place.place_offset_z":0.0061,"grasp_object.grasp_offset_z":0.02111,"lift_object.lift_height":0.12612,"release_object.max_release_time":1.38139},"optimized_scores":{"best_composite_score":0.251,"best_fitness_score":0.671,"best_task_score":0.40229},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":52.0,"contact_point_centroid":[0.5463,0.207,-0.00612],"force_p95":1.21486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58307,"mean_force":0.74829,"phase_index":4.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53682,0.18508,0.15615]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54866,0.20877,-0.00279],"force_p95":0.21358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54746,"mean_force":0.12737,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53297,0.18424,0.15864]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.49785,0.04329,-0.00128],"force_p95":0.23944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48263,"mean_force":0.07546,"phase_index":2.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48974,0.04365,0.04408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13001.0,"contact_point_centroid":[0.48878,0.06256,0.09369],"force_p95":0.09495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30774,"mean_force":0.05949,"phase_index":2.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48766,0.04347,0.09173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13674.0,"contact_point_centroid":[0.48873,0.0245,0.09497],"force_p95":0.0908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28617,"mean_force":0.05646,"phase_index":2.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48765,0.04347,0.09313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8064.0,"contact_point_centroid":[0.52526,0.12454,0.1622],"force_p95":0.13542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24567,"mean_force":0.10169,"phase_index":4.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51985,0.14286,0.16444]},{"body_a":"world","body_b":"grasp_target","contact_count":3796.0,"contact_point_centroid":[0.50119,0.045,-0.00205],"force_p95":0.15008,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21156,"mean_force":0.12645,"phase_index":1.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49382,0.04277,0.06726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9106.0,"contact_point_centroid":[0.52398,0.15979,0.16218],"force_p95":0.12986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18997,"mean_force":0.0908,"phase_index":4.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51936,0.14161,0.1647]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14369.0,"contact_point_centroid":[0.50127,0.05892,0.1642],"force_p95":0.1005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18145,"mean_force":0.06958,"phase_index":3.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49753,0.07782,0.16365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15729.0,"contact_point_centroid":[0.50084,0.09696,0.16408],"force_p95":0.08762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16676,"mean_force":0.0606,"phase_index":3.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49767,0.07827,0.16376]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49726,0.02036,0.20873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4814.0,"contact_point_centroid":[0.49174,0.02465,0.04437],"force_p95":0.07222,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12874,"mean_force":0.04479,"phase_index":1.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49165,0.04384,0.04241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.49172,0.06308,0.04427],"force_p95":0.07281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0738,"mean_force":0.04455,"phase_index":1.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49166,0.04384,0.04242]}],"total_contact_groups":13},"final_pose_error":0.06539,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54859,0.20868,0.01602],"final_tcp_position":[0.537,0.18558,0.15606],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.58307,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49708,0.04002,0.12467],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":549.0,"n_steps_budget":600.0,"object_pos_end":[0.50111,0.04419,0.02561],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24281,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14823,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13578.0,"raw_peak_contact_force":0.21156,"subtask_id":"reach_object","tcp_end":[0.49163,0.04383,0.04238],"tcp_start":[0.49708,0.04002,0.12467],"tcp_to_object_dist_end":0.01927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.50045,0.04374,0.13436],"object_pos_start":[0.50111,0.04419,0.02561],"object_to_goal_dist_end":0.21142,"object_to_goal_dist_start":0.24281,"object_z_max":0.13425,"peak_contact_force":0.10247,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26891.0,"raw_peak_contact_force":0.48263,"subtask_id":"lift_object","tcp_end":[0.48786,0.0435,0.15676],"tcp_start":[0.49163,0.04383,0.04238],"tcp_to_object_dist_end":0.02569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51641,0.11348,0.14616],"object_pos_start":[0.50045,0.04374,0.13436],"object_to_goal_dist_end":0.13988,"object_to_goal_dist_start":0.21142,"object_z_max":0.14615,"peak_contact_force":0.10209,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30098.0,"raw_peak_contact_force":0.18145,"subtask_id":"place_goal","tcp_end":[0.51102,0.1134,0.17542],"tcp_start":[0.48786,0.0435,0.15676],"tcp_to_object_dist_end":0.02976,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54634,0.2062,0.00186],"object_pos_start":[0.51641,0.11348,0.14616],"object_to_goal_dist_end":0.15107,"object_to_goal_dist_start":0.13988,"object_z_max":0.14616,"peak_contact_force":0.58358,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17222.0,"raw_peak_contact_force":1.58307,"subtask_id":"place_goal","tcp_end":[0.537,0.18558,0.15606],"tcp_start":[0.51102,0.1134,0.17542],"tcp_to_object_dist_end":0.15585,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54859,0.20868,0.01602],"object_pos_start":[0.54634,0.2062,0.00186],"object_to_goal_dist_end":0.13659,"object_to_goal_dist_start":0.15107,"object_z_max":0.01654,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.54746,"tcp_end":[0.53142,0.18365,0.17908],"tcp_start":[0.537,0.18558,0.15606],"tcp_to_object_dist_end":0.16586,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99099,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.14997,"approach_object.approach_speed":0.12135,"descend_place.place_offset_z":0.0051,"grasp_object.grasp_offset_z":0.00164,"lift_object.lift_height":0.10306,"release_object.max_release_time":1.07489},"optimized_scores":{"best_composite_score":0.17928,"best_fitness_score":0.59928,"best_task_score":0.22838},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":699.0,"contact_point_centroid":[0.52102,0.07127,-0.00343],"force_p95":0.77943,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53521,"mean_force":0.20813,"phase_index":3.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52256,0.04722,0.16836]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.47277,-0.01974,-0.00119],"force_p95":0.46911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72918,"mean_force":0.09881,"phase_index":2.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46521,-0.01981,0.0262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10833.0,"contact_point_centroid":[0.46394,-0.00071,0.06737],"force_p95":0.08979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30237,"mean_force":0.05717,"phase_index":2.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.463,-0.01974,0.06542]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11005.0,"contact_point_centroid":[0.46397,-0.03879,0.06669],"force_p95":0.08912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29883,"mean_force":0.05667,"phase_index":2.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46299,-0.01974,0.06493]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8975.0,"contact_point_centroid":[0.48542,0.02197,0.13202],"force_p95":0.14297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.296,"mean_force":0.08272,"phase_index":3.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48128,0.00356,0.13186]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8430.0,"contact_point_centroid":[0.48406,-0.01584,0.13134],"force_p95":0.14998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25606,"mean_force":0.08463,"phase_index":3.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48053,0.00277,0.13119]},{"body_a":"world","body_b":"grasp_target","contact_count":3804.0,"contact_point_centroid":[0.47615,-0.02011,-0.00201],"force_p95":0.13091,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1551,"mean_force":0.1238,"phase_index":1.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46932,-0.01964,0.05161]},{"body_a":"world","body_b":"grasp_target","contact_count":3224.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48541,-0.00957,0.20482]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52331,0.07489,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12277,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5525,0.08131,0.1735]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52331,0.07489,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57667,0.10949,0.18014]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4838.0,"contact_point_centroid":[0.46698,-0.00067,0.02658],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09886,"mean_force":0.04468,"phase_index":1.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46692,-0.01985,0.02466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.467,-0.03906,0.02654],"force_p95":0.06859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09166,"mean_force":0.04485,"phase_index":1.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46692,-0.01985,0.02466]},{"body_a":"left_finger","body_b":"right_finger","contact_count":639.0,"contact_point_centroid":[0.52381,0.04859,0.17185],"force_p95":0.01395,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.01096,"phase_index":3.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52387,0.04859,0.16952]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4213.0,"contact_point_centroid":[0.55257,0.08133,0.17577],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01057,"phase_index":4.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55252,0.08133,0.17351]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.57942,0.11011,0.17796],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01003,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57935,0.11009,0.1757]}],"total_contact_groups":15},"final_pose_error":0.07248,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52331,0.07489,0.01602],"final_tcp_position":[0.58069,0.11026,0.17823],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.53521,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3224.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47322,-0.01911,0.11383],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":551.0,"n_steps_budget":600.0,"object_pos_end":[0.47603,-0.01987,0.02588],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28835,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13059,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13526.0,"raw_peak_contact_force":0.1551,"subtask_id":"reach_object","tcp_end":[0.46689,-0.01985,0.02463],"tcp_start":[0.47322,-0.01911,0.11383],"tcp_to_object_dist_end":0.00923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.48024,-0.01976,0.11081],"object_pos_start":[0.47603,-0.01987,0.02588],"object_to_goal_dist_end":0.24729,"object_to_goal_dist_start":0.28835,"object_z_max":0.11071,"peak_contact_force":0.10511,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22026.0,"raw_peak_contact_force":0.72918,"subtask_id":"lift_object","tcp_end":[0.46297,-0.01973,0.11647],"tcp_start":[0.46689,-0.01985,0.02463],"tcp_to_object_dist_end":0.01817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5233,0.07487,0.01602],"object_pos_start":[0.48024,-0.01976,0.11081],"object_to_goal_dist_end":0.22153,"object_to_goal_dist_start":0.24729,"object_z_max":0.13406,"peak_contact_force":0.12277,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18743.0,"raw_peak_contact_force":1.53521,"subtask_id":"place_goal","tcp_end":[0.52937,0.0544,0.17439],"tcp_start":[0.46297,-0.01973,0.11647],"tcp_to_object_dist_end":0.1598,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52331,0.07489,0.01602],"object_pos_start":[0.5233,0.07487,0.01602],"object_to_goal_dist_end":0.22151,"object_to_goal_dist_start":0.22153,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8213.0,"raw_peak_contact_force":0.12277,"subtask_id":"place_goal","tcp_end":[0.58069,0.11026,0.17823],"tcp_start":[0.52937,0.0544,0.17439],"tcp_to_object_dist_end":0.17566,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52331,0.07489,0.01602],"object_pos_start":[0.52331,0.07489,0.01602],"object_to_goal_dist_end":0.22151,"object_to_goal_dist_start":0.22151,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57512,0.10914,0.20025],"tcp_start":[0.58069,0.11026,0.17823],"tcp_to_object_dist_end":0.19442,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76871,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.14955,"approach_object.approach_speed":0.06332,"descend_place.place_offset_z":0.00173,"grasp_object.grasp_offset_z":0.01849,"lift_object.lift_height":0.12538,"release_object.max_release_time":1.38691},"optimized_scores":{"best_composite_score":0.27005,"best_fitness_score":0.69005,"best_task_score":0.43483},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.55405,0.12798,-0.00706],"force_p95":1.16816,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26738,"mean_force":0.44766,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55406,0.12463,0.14416]},{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.45563,-0.02571,-0.00118],"force_p95":0.24731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47633,"mean_force":0.06935,"phase_index":2.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44814,-0.02582,0.04254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13485.0,"contact_point_centroid":[0.44731,-0.0447,0.09297],"force_p95":0.0935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29217,"mean_force":0.05741,"phase_index":2.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44603,-0.02572,0.09135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12961.0,"contact_point_centroid":[0.44721,-0.0067,0.09301],"force_p95":0.09828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29185,"mean_force":0.05908,"phase_index":2.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44604,-0.02572,0.09104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15353.0,"contact_point_centroid":[0.48117,-0.00088,0.159],"force_p95":0.09363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20906,"mean_force":0.06465,"phase_index":3.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47693,0.01785,0.15779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10145.0,"contact_point_centroid":[0.53937,0.07496,0.14761],"force_p95":0.11855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20182,"mean_force":0.08948,"phase_index":4.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53362,0.09324,0.14949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9660.0,"contact_point_centroid":[0.53863,0.11088,0.14771],"force_p95":0.12532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19774,"mean_force":0.09392,"phase_index":4.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53302,0.09247,0.14982]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13744.0,"contact_point_centroid":[0.48162,0.03677,0.15925],"force_p95":0.0961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18036,"mean_force":0.07127,"phase_index":3.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47702,0.01794,0.15782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.56448,0.1439,0.12906],"force_p95":0.17018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17471,"mean_force":0.1041,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55818,0.12568,0.13412]},{"body_a":"world","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.45856,-0.02629,-0.00201],"force_p95":0.1334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16518,"mean_force":0.1241,"phase_index":1.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45229,-0.02562,0.06281]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":494.0,"contact_point_centroid":[0.56461,0.10768,0.12959],"force_p95":0.12543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16105,"mean_force":0.08968,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55822,0.12569,0.13417]},{"body_a":"world","body_b":"grasp_target","contact_count":3548.0,"contact_point_centroid":[0.45856,-0.02632,-0.00196],"force_p95":0.12598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47705,-0.01246,0.20515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4837.0,"contact_point_centroid":[0.44984,-0.00669,0.04285],"force_p95":0.06907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10921,"mean_force":0.04475,"phase_index":1.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44979,-0.02588,0.04093]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4892.0,"contact_point_centroid":[0.44986,-0.04509,0.0428],"force_p95":0.06932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08664,"mean_force":0.04477,"phase_index":1.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44979,-0.02588,0.04093]}],"total_contact_groups":14},"final_pose_error":0.11013,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.57345,0.14703,0.02112],"final_tcp_position":[0.55999,0.12599,0.13703],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.26738,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3548.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45662,-0.02494,0.11425],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":544.0,"n_steps_budget":600.0,"object_pos_end":[0.45847,-0.02599,0.02585],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30349,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13291,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13505.0,"raw_peak_contact_force":0.16518,"subtask_id":"reach_object","tcp_end":[0.44976,-0.02588,0.0409],"tcp_start":[0.45662,-0.02494,0.11425],"tcp_to_object_dist_end":0.01739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.45929,-0.02569,0.13366],"object_pos_start":[0.45847,-0.02599,0.02585],"object_to_goal_dist_end":0.29031,"object_to_goal_dist_start":0.30349,"object_z_max":0.13355,"peak_contact_force":0.11054,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26636.0,"raw_peak_contact_force":0.47633,"subtask_id":"lift_object","tcp_end":[0.44615,-0.0257,0.15535],"tcp_start":[0.44976,-0.02588,0.0409],"tcp_to_object_dist_end":0.02536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52178,0.06636,0.13608],"object_pos_start":[0.45929,-0.02569,0.13366],"object_to_goal_dist_end":0.17985,"object_to_goal_dist_start":0.29031,"object_z_max":0.13608,"peak_contact_force":0.097,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29097.0,"raw_peak_contact_force":0.20906,"subtask_id":"place_goal","tcp_end":[0.51517,0.06648,0.1649],"tcp_start":[0.44615,-0.0257,0.15535],"tcp_to_object_dist_end":0.02956,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56633,0.12563,0.09937],"object_pos_start":[0.52178,0.06636,0.13608],"object_to_goal_dist_end":0.10539,"object_to_goal_dist_start":0.17985,"object_z_max":0.13608,"peak_contact_force":0.1237,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19805.0,"raw_peak_contact_force":0.20182,"subtask_id":"place_goal","tcp_end":[0.55999,0.12599,0.13703],"tcp_start":[0.51517,0.06648,0.1649],"tcp_to_object_dist_end":0.03819,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57345,0.14703,0.02112],"object_pos_start":[0.56633,0.12563,0.09937],"object_to_goal_dist_end":0.12492,"object_to_goal_dist_start":0.10539,"object_z_max":0.09937,"peak_contact_force":0.48767,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1159.0,"raw_peak_contact_force":1.26738,"tcp_end":[0.55386,0.12459,0.15979],"tcp_start":[0.55999,0.12599,0.13703],"tcp_to_object_dist_end":0.14184,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```