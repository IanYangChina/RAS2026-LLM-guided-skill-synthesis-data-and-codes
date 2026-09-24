## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1162 | 0.43 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1094 | 0.29 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1146 | 0.43 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 12 | -0.0171 | 0.41 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1855 | 0.56 | ✅ accepted |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.116) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_to_goal
  target_entity: object
  weight: 0.2
- id: hold_at_goal
  target_entity: object
  weight: 0.4
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_1
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
    orientation:
      mode: keep_current
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - -0.005
  subtask_id: reach_object
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.35
      binds_to:
      - path: generator.speed
        mode: replace
    transport_xy_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    transport_xy_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    transport_z_offset_delta:
      type: scalar
      range:
      - -0.03
      - 0.07
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_to_goal
- id: hold_1
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
    orientation:
      mode: keep_current
  parameters:
    hold_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: hold_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.005, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_xy_offset_x: status=consumed; consumers=target.offset.x (add)
    - transport_xy_offset_y: status=consumed; consumers=target.offset.y (add)
    - transport_z_offset_delta: status=consumed; consumers=target.offset.z (replace)
- **hold_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - hold_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.116
- **task_score** (E): 0.433
- **fitness_score**: 0.686  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0945 |
| descend_1 | 1.00 | 1.00 | 0.1711 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 1.00 | 1.00 | 0.1438 |
| transport_1 | 1.00 | 0.33 | 0.2311 |
| hold_at_goal | 1.00 | 1.00 | 0.0163 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.518, -0.001, 0.219) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / time_limit | (0.518, -0.001, 0.219)→(0.516, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.047)→(0.508, -0.001, 0.038) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 42.667 | 0.142 | 0.179 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.038)→(0.517, -0.001, 0.181) | (0.522, -0.001, 0.026)→(0.533, -0.001, 0.161) | 0.290→0.228 | 1.00 / 22.333 | 0.114 | 0.483 |
| transport_1 | approach | 1.00 / step_budget | (0.517, -0.001, 0.181)→(0.614, 0.206, 0.193) | (0.533, -0.001, 0.161)→(0.616, 0.208, 0.125) | 0.228→0.082 | 0.33 / 8.000 | 0.036 | 0.297 |
| hold_at_goal | grasp | 1.00 / step_budget | (0.614, 0.206, 0.193)→(0.607, 0.204, 0.178) | (0.616, 0.208, 0.125)→(0.613, 0.219, 0.072) | 0.082→0.134 | 1.00 / 13.333 | 0.125 | 1.111 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.639
- phase_score: 0.510
- phase_breakdown.transport_to_goal_score: 0.635
- phase_breakdown.reach_above_object_score: 0.102
- phase_breakdown.hold_at_goal_score: 0.489
- phase_breakdown.lift_object_score: 0.839
- grasp_place_fitness: 0.798

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.798
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.639
- **Median Q (composite search score)**: 0.077
- **K-run variance**: 0.0065
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.233


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0625,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15886,"descend_1.grasp_offset_z":0.01214,"grasp_1.grasp_duration":1.74265,"hold_at_goal.hold_duration":1.3827,"lift_1.lift_height":0.16631,"transport_1.transport_speed":0.55139,"transport_1.transport_xy_offset_x":0.01822,"transport_1.transport_xy_offset_y":0.01235,"transport_1.transport_z_offset_delta":-0.00944},"optimized_scores":{"best_composite_score":0.22834,"best_fitness_score":0.79834,"best_task_score":0.63933},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.48048,0.04675,-0.0014],"force_p95":0.5264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60042,"mean_force":0.12708,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46839,0.04725,0.02908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6528.0,"contact_point_centroid":[0.47348,0.06644,0.09545],"force_p95":0.11077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28268,"mean_force":0.07309,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47133,0.04721,0.09298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8488.0,"contact_point_centroid":[0.47464,0.02863,0.093],"force_p95":0.09835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27293,"mean_force":0.0587,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47122,0.0472,0.0918]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6696.0,"contact_point_centroid":[0.54204,0.12302,0.1893],"force_p95":0.12871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27099,"mean_force":0.08173,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.535,0.14108,0.19004]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5674.0,"contact_point_centroid":[0.5907,0.24626,0.19661],"force_p95":0.11677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2595,"mean_force":0.07436,"phase_index":5.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.58546,0.22703,0.19703]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6058.0,"contact_point_centroid":[0.5379,0.1577,0.19041],"force_p95":0.11691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22841,"mean_force":0.08723,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53347,0.13866,0.18949]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6061.0,"contact_point_centroid":[0.59341,0.209,0.19602],"force_p95":0.09052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22564,"mean_force":0.06859,"phase_index":5.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.58555,0.22708,0.19728]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04865,-0.00211],"force_p95":0.15646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21648,"mean_force":0.13151,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47069,0.04749,0.02875]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5105.0,"contact_point_centroid":[0.47125,0.02837,0.02878],"force_p95":0.07321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18205,"mean_force":0.04242,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46947,0.04737,0.02752]},{"body_a":"world","body_b":"grasp_target","contact_count":2216.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48913,0.02221,0.24439]},{"body_a":"world","body_b":"grasp_target","contact_count":3676.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47751,0.04668,0.10351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4214.0,"contact_point_centroid":[0.46938,0.06669,0.02997],"force_p95":0.08782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09847,"mean_force":0.05207,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46948,0.04737,0.02753]}],"total_contact_groups":12},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59059,0.22773,0.16396],"final_tcp_position":[0.59015,0.22861,0.20931],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.60042,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2216.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.48027,0.04509,0.19111],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16515,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":919.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3676.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_above_object","tcp_end":[0.47763,0.04817,0.03579],"tcp_start":[0.48027,0.04509,0.19111],"tcp_to_object_dist_end":0.01102,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48267,0.04788,0.0256],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29081,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15459,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11119.0,"raw_peak_contact_force":0.21648,"subtask_id":"lift_object","tcp_end":[0.46944,0.04736,0.02749],"tcp_start":[0.47763,0.04817,0.03579],"tcp_to_object_dist_end":0.01337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.49622,0.04848,0.16188],"object_pos_start":[0.48267,0.04788,0.0256],"object_to_goal_dist_end":0.21113,"object_to_goal_dist_start":0.29081,"object_z_max":0.16164,"peak_contact_force":0.11042,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15093.0,"raw_peak_contact_force":0.60042,"subtask_id":"lift_object","tcp_end":[0.47805,0.04748,0.17266],"tcp_start":[0.46944,0.04736,0.02749],"tcp_to_object_dist_end":0.02115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.59637,0.22988,0.18136],"object_pos_start":[0.49622,0.04848,0.16188],"object_to_goal_dist_end":0.05123,"object_to_goal_dist_start":0.21113,"object_z_max":0.18133,"peak_contact_force":0.10793,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12754.0,"raw_peak_contact_force":0.27099,"subtask_id":"transport_to_goal","tcp_end":[0.59015,0.22861,0.20931],"tcp_start":[0.47805,0.04748,0.17266],"tcp_to_object_dist_end":0.02866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59059,0.22773,0.16396],"object_pos_start":[0.59637,0.22988,0.18136],"object_to_goal_dist_end":0.0671,"object_to_goal_dist_start":0.05123,"object_z_max":0.18136,"peak_contact_force":0.13113,"phase_name":"hold_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11735.0,"raw_peak_contact_force":0.2595,"subtask_id":"hold_at_goal","tcp_end":[0.58463,0.22667,0.19485],"tcp_start":[0.59015,0.22861,0.20931],"tcp_to_object_dist_end":0.03147,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15596,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20619,"descend_1.grasp_offset_z":0.0189,"grasp_1.grasp_duration":1.36547,"hold_at_goal.hold_duration":1.4637,"lift_1.lift_height":0.17117,"transport_1.transport_speed":0.53991,"transport_1.transport_xy_offset_x":0.00746,"transport_1.transport_xy_offset_y":0.02537,"transport_1.transport_z_offset_delta":-0.00485},"optimized_scores":{"best_composite_score":0.04317,"best_fitness_score":0.61317,"best_task_score":0.29503},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1743.0,"contact_point_centroid":[0.60424,0.25193,-0.00254],"force_p95":0.26514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57067,"mean_force":0.14568,"phase_index":5.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.60509,0.23629,0.17881]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.5353,-0.02097,-0.00132],"force_p95":0.37219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42254,"mean_force":0.08702,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52215,-0.02105,0.04466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5697.0,"contact_point_centroid":[0.56796,0.06841,0.18007],"force_p95":0.1408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28846,"mean_force":0.09156,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5634,0.08705,0.18126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7899.0,"contact_point_centroid":[0.52789,-0.00241,0.10151],"force_p95":0.10355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27687,"mean_force":0.06304,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52484,-0.02119,0.09978]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6869.0,"contact_point_centroid":[0.52729,-0.04026,0.10281],"force_p95":0.10898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26419,"mean_force":0.06984,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52488,-0.02119,0.10008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5733.0,"contact_point_centroid":[0.56886,0.10568,0.17934],"force_p95":0.13415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24663,"mean_force":0.09214,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56357,0.08747,0.18135]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02146,-0.00204],"force_p95":0.1346,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15712,"mean_force":0.12598,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52448,-0.02108,0.04475]},{"body_a":"world","body_b":"grasp_target","contact_count":3932.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51685,-0.01138,0.26051]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53082,-0.02092,0.12846]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5337.0,"contact_point_centroid":[0.52399,-0.00194,0.04532],"force_p95":0.06845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10458,"mean_force":0.04136,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52323,-0.02106,0.04328]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4345.0,"contact_point_centroid":[0.5224,-0.04031,0.0467],"force_p95":0.08006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08115,"mean_force":0.04941,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52323,-0.02106,0.04329]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1555.0,"contact_point_centroid":[0.60522,0.23608,0.17962],"force_p95":0.01224,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01479,"mean_force":0.01056,"phase_index":5.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.60455,0.23604,0.17742]}],"total_contact_groups":12},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60424,0.25197,0.02602],"final_tcp_position":[0.6104,0.23793,0.19199],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.57067,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":984.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3932.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.53257,-0.02063,0.23175],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20578,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_above_object","tcp_end":[0.53165,-0.02119,0.05322],"tcp_start":[0.53257,-0.02063,0.23175],"tcp_to_object_dist_end":0.02773,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53693,-0.02153,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31701,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1346,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11482.0,"raw_peak_contact_force":0.15712,"subtask_id":"lift_object","tcp_end":[0.5232,-0.02106,0.04325],"tcp_start":[0.53165,-0.02119,0.05322],"tcp_to_object_dist_end":0.02217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":465.0,"n_steps_budget":960.0,"object_pos_end":[0.54672,-0.02211,0.15327],"object_pos_start":[0.53693,-0.02153,0.02584],"object_to_goal_dist_end":0.26345,"object_to_goal_dist_start":0.31701,"object_z_max":0.15303,"peak_contact_force":0.11292,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14847.0,"raw_peak_contact_force":0.42254,"subtask_id":"lift_object","tcp_end":[0.5321,-0.02143,0.17775],"tcp_start":[0.5232,-0.02106,0.04325],"tcp_to_object_dist_end":0.02852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.60937,0.24178,0.06774],"object_pos_start":[0.54672,-0.02211,0.15327],"object_to_goal_dist_end":0.14038,"object_to_goal_dist_start":0.26345,"object_z_max":0.15349,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11430.0,"raw_peak_contact_force":0.28846,"subtask_id":"transport_to_goal","tcp_end":[0.6104,0.23793,0.19199],"tcp_start":[0.5321,-0.02143,0.17775],"tcp_to_object_dist_end":0.12431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60424,0.25197,0.02602],"object_pos_start":[0.60937,0.24178,0.06774],"object_to_goal_dist_end":0.1831,"object_to_goal_dist_start":0.14038,"object_z_max":0.06774,"peak_contact_force":0.12263,"phase_name":"hold_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3298.0,"raw_peak_contact_force":1.57067,"subtask_id":"hold_at_goal","tcp_end":[0.60434,0.23595,0.17689],"tcp_start":[0.6104,0.23793,0.19199],"tcp_to_object_dist_end":0.15172,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06195,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2063,"descend_1.grasp_offset_z":0.01084,"grasp_1.grasp_duration":1.13979,"hold_at_goal.hold_duration":2.99798,"lift_1.lift_height":0.18735,"transport_1.transport_speed":0.50672,"transport_1.transport_xy_offset_x":0.01823,"transport_1.transport_xy_offset_y":-0.00015,"transport_1.transport_z_offset_delta":0.0085},"optimized_scores":{"best_composite_score":0.077,"best_fitness_score":0.647,"best_task_score":0.36333},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1601.0,"contact_point_centroid":[0.64566,0.17623,-0.00255],"force_p95":0.28857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50185,"mean_force":0.14618,"phase_index":5.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.63394,0.14931,0.16277]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.54342,-0.0287,-0.00135],"force_p95":0.38405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42751,"mean_force":0.0876,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53024,-0.02868,0.04449]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5134.0,"contact_point_centroid":[0.58899,0.06722,0.18214],"force_p95":0.13689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33134,"mean_force":0.08831,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58297,0.04918,0.18417]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6725.0,"contact_point_centroid":[0.53638,-0.04785,0.11073],"force_p95":0.11989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28977,"mean_force":0.07945,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53333,-0.0288,0.10824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8340.0,"contact_point_centroid":[0.5372,-0.01025,0.1095],"force_p95":0.10614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2812,"mean_force":0.06737,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53333,-0.0288,0.10832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4563.0,"contact_point_centroid":[0.59002,0.03535,0.18273],"force_p95":0.14459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2776,"mean_force":0.09741,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58568,0.05406,0.18377]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.0293,-0.00204],"force_p95":0.13664,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16251,"mean_force":0.12631,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53266,-0.02874,0.04471]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52032,-0.01485,0.26216]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53884,-0.02842,0.12885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5316.0,"contact_point_centroid":[0.53237,-0.00966,0.04526],"force_p95":0.07139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10194,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53139,-0.02871,0.04319]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4155.0,"contact_point_centroid":[0.53197,-0.04799,0.04604],"force_p95":0.08265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09294,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53139,-0.02871,0.0432]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1397.0,"contact_point_centroid":[0.63426,0.14925,0.16425],"force_p95":0.01197,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01045,"phase_index":5.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.63355,0.14922,0.16188]}],"total_contact_groups":12},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64565,0.17626,0.02602],"final_tcp_position":[0.64012,0.15043,0.17699],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.50185,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.54028,-0.02783,0.23273],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20678,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_above_object","tcp_end":[0.53984,-0.02893,0.05336],"tcp_start":[0.54028,-0.02783,0.23273],"tcp_to_object_dist_end":0.02795,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02918,0.02582],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26103,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13656,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11271.0,"raw_peak_contact_force":0.16251,"subtask_id":"lift_object","tcp_end":[0.53136,-0.02871,0.04316],"tcp_start":[0.53984,-0.02893,0.05336],"tcp_to_object_dist_end":0.02239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.55515,-0.0301,0.16831],"object_pos_start":[0.54551,-0.02918,0.02582],"object_to_goal_dist_end":0.21011,"object_to_goal_dist_start":0.26103,"object_z_max":0.16808,"peak_contact_force":0.11948,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15146.0,"raw_peak_contact_force":0.42751,"subtask_id":"lift_object","tcp_end":[0.54092,-0.02906,0.19396],"tcp_start":[0.53136,-0.02871,0.04316],"tcp_to_object_dist_end":0.02935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.64254,0.15161,0.12642],"object_pos_start":[0.55515,-0.0301,0.16831],"object_to_goal_dist_end":0.05312,"object_to_goal_dist_start":0.21011,"object_z_max":0.16855,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9697.0,"raw_peak_contact_force":0.33134,"subtask_id":"transport_to_goal","tcp_end":[0.64012,0.15043,0.17699],"tcp_start":[0.54092,-0.02906,0.19396],"tcp_to_object_dist_end":0.05063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64565,0.17626,0.02602],"object_pos_start":[0.64254,0.15161,0.12642],"object_to_goal_dist_end":0.15187,"object_to_goal_dist_start":0.05312,"object_z_max":0.12642,"peak_contact_force":0.12263,"phase_name":"hold_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2998.0,"raw_peak_contact_force":1.50185,"subtask_id":"hold_at_goal","tcp_end":[0.63345,0.14919,0.16165],"tcp_start":[0.64012,0.15043,0.17699],"tcp_to_object_dist_end":0.13884,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```