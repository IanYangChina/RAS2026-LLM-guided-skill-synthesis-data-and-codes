## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1094 | 0.29 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1146 | 0.43 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 12 | -0.0171 | 0.41 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1855 | 0.56 | ✅ accepted |
| 4 | approach → descend → grasp → lift → push → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | grasp_success | pose_tolerance | pose_tolerance | time_limit | 7 | 0.2678 | 0.54 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.109) — your mutation base

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

- **Composite score**: -0.109
- **task_score** (E): 0.291
- **fitness_score**: 0.621  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0854 |
| descend_1 | 1.00 | 1.00 | 0.1844 |
| grasp_1 | 1.00 | 1.00 | 0.0135 |
| lift_1 | 1.00 | 1.00 | 0.1319 |
| transport_1 | 1.00 | 0.67 | 0.2181 |
| descend_to_goal | 1.00 | 0.67 | 0.0177 |
| release_1 | 1.00 | 1.00 | 0.0200 |
| retract_1 | 1.00 | 1.00 | 0.0599 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, -0.000, 0.224) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 10.265 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.514, -0.000, 0.224)→(0.516, -0.001, 0.040) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.040)→(0.507, -0.001, 0.030) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 43.667 | 0.157 | 0.223 |
| lift_1 | lift | 1.00 / step_budget | (0.507, -0.001, 0.030)→(0.516, -0.001, 0.161) | (0.522, -0.001, 0.025)→(0.535, -0.001, 0.148) | 0.290→0.229 | 1.00 / 23.333 | 55983.983 | 0.598 |
| transport_1 | approach | 1.00 / step_budget | (0.516, -0.001, 0.161)→(0.602, 0.195, 0.194) | (0.535, -0.001, 0.148)→(0.608, 0.186, 0.107) | 0.229→0.102 | 0.67 / 10.667 | 0.082 | 0.817 |
| descend_to_goal | descend | 1.00 / step_budget | (0.602, 0.195, 0.194)→(0.604, 0.202, 0.197) | (0.608, 0.186, 0.107)→(0.609, 0.192, 0.070) | 0.102→0.137 | 0.67 / 9.000 | 0.084 | 0.140 |
| release_1 | release | 1.00 / step_budget | (0.604, 0.202, 0.197)→(0.599, 0.201, 0.216) | (0.609, 0.192, 0.070)→(0.602, 0.191, 0.019) | 0.137→0.187 | 1.00 / 4.000 | 0.119 | 1.166 |
| retract_1 | retract | 1.00 / step_budget | (0.599, 0.201, 0.216)→(0.604, 0.204, 0.275) | (0.602, 0.191, 0.019)→(0.601, 0.191, 0.019) | 0.187→0.187 | 1.00 / 4.000 | 0.123 | 0.137 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.363
- phase_score: 0.398
- phase_breakdown.transport_to_goal_score: 0.524
- phase_breakdown.reach_above_object_score: 0.212
- phase_breakdown.reach_object_score: 0.719
- phase_breakdown.lift_object_score: 0.411
- phase_breakdown.place_at_goal_score: 0.218
- grasp_place_fitness: 0.652

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.652
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.363
- **Median Q (composite search score)**: -0.119
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8908,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17499,"descend_1.grasp_offset_z":-0.00998,"descend_to_goal.place_offset_z":-0.01123,"grasp_1.grasp_duration":1.84336,"lift_1.lift_height":0.2025,"release_1.release_duration":1.44506,"retract_1.retract_height":0.13173,"transport_1.transport_speed":0.94486,"transport_1.transport_xy_offset_x":-0.01173,"transport_1.transport_xy_offset_y":0.00863,"transport_1.transport_z_offset_delta":0.01865},"optimized_scores":{"best_composite_score":-0.13111,"best_fitness_score":0.59889,"best_task_score":0.23934},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":734.0,"contact_point_centroid":[0.58166,0.23137,-0.00368],"force_p95":0.76359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06227,"mean_force":0.19268,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56526,0.22384,0.22578]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.48023,0.04594,-0.00163],"force_p95":0.68129,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77803,"mean_force":0.16119,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46837,0.04629,0.02335]},{"body_a":"grasp_target","body_b":"hand","contact_count":140.0,"contact_point_centroid":[0.49587,0.06628,0.07449],"force_p95":0.1206,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43545,"mean_force":0.06713,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46771,0.04615,0.042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4026.0,"contact_point_centroid":[0.51823,0.14286,0.21939],"force_p95":0.15805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32362,"mean_force":0.10618,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51359,0.12391,0.21935]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48255,0.04835,-0.00241],"force_p95":0.19476,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29467,"mean_force":0.15266,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47082,0.04655,0.02255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5155.0,"contact_point_centroid":[0.52219,0.10933,0.21822],"force_p95":0.14121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28751,"mean_force":0.08712,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51509,0.12704,0.21995]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8334.0,"contact_point_centroid":[0.47327,0.06545,0.10684],"force_p95":0.11078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27746,"mean_force":0.0731,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4712,0.04626,0.10453]},{"body_a":"grasp_target","body_b":"hand","contact_count":378.0,"contact_point_centroid":[0.49922,0.0525,0.05455],"force_p95":0.16783,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25731,"mean_force":0.08231,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46998,0.04647,0.02172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10418.0,"contact_point_centroid":[0.47465,0.02767,0.10324],"force_p95":0.10394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2513,"mean_force":0.06066,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47104,0.04625,0.10225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5052.0,"contact_point_centroid":[0.47109,0.02746,0.02257],"force_p95":0.06846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1456,"mean_force":0.04137,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46961,0.04643,0.02134]},{"body_a":"world","body_b":"grasp_target","contact_count":684.0,"contact_point_centroid":[0.4827,0.04873,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49186,0.01769,0.26189]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.58142,0.23156,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12266,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57061,0.22513,0.2875]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48001,0.04229,0.12549]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4303.0,"contact_point_centroid":[0.46926,0.06586,0.02359],"force_p95":0.08679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10706,"mean_force":0.05321,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46962,0.04643,0.02136]}],"total_contact_groups":14},"final_pose_error":0.02973,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58142,0.23156,0.01602],"final_tcp_position":[0.57806,0.22738,0.33277],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":30.55107,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":30.55107,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":684.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.4839,0.03755,0.22126],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4783,0.04724,0.03013],"tcp_start":[0.4839,0.03755,0.22126],"tcp_to_object_dist_end":0.0062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48213,0.04691,0.02474],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29221,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18576,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11533.0,"raw_peak_contact_force":0.29467,"subtask_id":"reach_object","tcp_end":[0.46958,0.04642,0.02132],"tcp_start":[0.4783,0.04724,0.03013],"tcp_to_object_dist_end":0.01302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.49825,0.04787,0.19858],"object_pos_start":[0.48213,0.04691,0.02474],"object_to_goal_dist_end":0.20191,"object_to_goal_dist_start":0.29221,"object_z_max":0.19833,"peak_contact_force":0.11156,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18982.0,"raw_peak_contact_force":0.77803,"subtask_id":"lift_object","tcp_end":[0.47811,0.04654,0.20782],"tcp_start":[0.46958,0.04642,0.02132],"tcp_to_object_dist_end":0.02221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.56979,0.21799,0.18288],"object_pos_start":[0.49825,0.04787,0.19858],"object_to_goal_dist_end":0.0503,"object_to_goal_dist_start":0.20191,"object_z_max":0.20941,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9181.0,"raw_peak_contact_force":0.32362,"subtask_id":"transport_to_goal","tcp_end":[0.56137,0.22318,0.2385],"tcp_start":[0.47811,0.04654,0.20782],"tcp_to_object_dist_end":0.05649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":47.0,"n_steps_budget":1000.0,"object_pos_end":[0.58153,0.22805,0.07496],"object_pos_start":[0.56979,0.21799,0.18288],"object_to_goal_dist_end":0.15552,"object_to_goal_dist_start":0.0503,"object_z_max":0.18288,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.56883,0.22555,0.22561],"tcp_start":[0.56137,0.22318,0.2385],"tcp_to_object_dist_end":0.1512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58142,0.23156,0.01602],"object_pos_start":[0.58153,0.22805,0.07496],"object_to_goal_dist_end":0.21448,"object_to_goal_dist_start":0.15552,"object_z_max":0.07496,"peak_contact_force":0.12266,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":734.0,"raw_peak_contact_force":2.06227,"subtask_id":"place_at_goal","tcp_end":[0.56442,0.22341,0.24528],"tcp_start":[0.56883,0.22555,0.22561],"tcp_to_object_dist_end":0.23003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":750.0,"object_pos_end":[0.58142,0.23156,0.01602],"object_pos_start":[0.58142,0.23156,0.01602],"object_to_goal_dist_end":0.21448,"object_to_goal_dist_start":0.21448,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":792.0,"raw_peak_contact_force":0.12266,"subtask_id":"place_at_goal","tcp_end":[0.57806,0.22738,0.33277],"tcp_start":[0.56442,0.22341,0.24528],"tcp_to_object_dist_end":0.31679,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67797,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17942,"descend_1.grasp_offset_z":0.00266,"descend_to_goal.place_offset_z":0.01961,"grasp_1.grasp_duration":2.87626,"lift_1.lift_height":0.13403,"release_1.release_duration":1.58125,"retract_1.retract_height":0.06076,"transport_1.transport_speed":0.11486,"transport_1.transport_xy_offset_x":-0.00597,"transport_1.transport_xy_offset_y":-0.0031,"transport_1.transport_z_offset_delta":-0.00291},"optimized_scores":{"best_composite_score":-0.11926,"best_fitness_score":0.61074,"best_task_score":0.27176},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":321.0,"contact_point_centroid":[0.60234,0.18889,-0.00503],"force_p95":1.09104,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84888,"mean_force":0.27231,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59355,0.19869,0.1896]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.535,-0.02085,-0.00133],"force_p95":0.46159,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5369,"mean_force":0.10709,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52115,-0.02064,0.03314]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5278.0,"contact_point_centroid":[0.55845,0.04502,0.15717],"force_p95":0.15319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29479,"mean_force":0.1005,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55342,0.06378,0.15665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6126.0,"contact_point_centroid":[0.52771,-0.00211,0.08],"force_p95":0.106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28189,"mean_force":0.0663,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52418,-0.02075,0.07859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5116.0,"contact_point_centroid":[0.52753,-0.03979,0.08262],"force_p95":0.11012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28163,"mean_force":0.07625,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52435,-0.02075,0.08019]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6579.0,"contact_point_centroid":[0.56081,0.08523,0.15695],"force_p95":0.12231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2597,"mean_force":0.08281,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55437,0.06715,0.1574]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02132,-0.00205],"force_p95":0.13951,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17413,"mean_force":0.127,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52345,-0.02067,0.03316]},{"body_a":"world","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.53702,-0.02132,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12337,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51186,-0.00771,0.26352]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.6021,0.18913,-0.00196],"force_p95":0.12878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13144,"mean_force":0.12278,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60099,0.21815,0.2023]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52727,-0.0185,0.13318]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6021,0.18913,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60218,0.22285,0.21344]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.6021,0.18913,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60149,0.22267,0.23498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5300.0,"contact_point_centroid":[0.52321,-0.00161,0.03404],"force_p95":0.06713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10749,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52219,-0.02065,0.03173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4176.0,"contact_point_centroid":[0.52317,-0.03995,0.03443],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09013,"mean_force":0.05197,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52219,-0.02065,0.03173]},{"body_a":"left_finger","body_b":"right_finger","contact_count":84.0,"contact_point_centroid":[0.59692,0.20759,0.19399],"force_p95":0.01513,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01301,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59625,0.20757,0.19179]},{"body_a":"left_finger","body_b":"right_finger","contact_count":995.0,"contact_point_centroid":[0.60173,0.21819,0.20454],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01029,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.601,0.21816,0.20231]}],"total_contact_groups":17},"final_pose_error":0.02979,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6021,0.18913,0.01602],"final_tcp_position":[0.60281,0.2235,0.23966],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.84888,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":660.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52574,-0.01631,0.22482],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.5312,-0.02076,0.04219],"tcp_start":[0.52574,-0.01631,0.22482],"tcp_to_object_dist_end":0.01719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02103,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31665,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13896,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.17413,"subtask_id":"reach_object","tcp_end":[0.52216,-0.02065,0.0317],"tcp_start":[0.5312,-0.02076,0.04219],"tcp_to_object_dist_end":0.0159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":381.0,"n_steps_budget":810.0,"object_pos_end":[0.54923,-0.02148,0.12744],"object_pos_start":[0.53691,-0.02103,0.02579],"object_to_goal_dist_end":0.26878,"object_to_goal_dist_start":0.31665,"object_z_max":0.12721,"peak_contact_force":0.10735,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11322.0,"raw_peak_contact_force":0.5369,"subtask_id":"lift_object","tcp_end":[0.53138,-0.02094,0.14071],"tcp_start":[0.52216,-0.02065,0.0317],"tcp_to_object_dist_end":0.02225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.60209,0.18915,0.0167],"object_pos_start":[0.54923,-0.02148,0.12744],"object_to_goal_dist_end":0.19476,"object_to_goal_dist_start":0.26878,"object_z_max":0.15612,"peak_contact_force":0.12857,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12262.0,"raw_peak_contact_force":1.84888,"subtask_id":"transport_to_goal","tcp_end":[0.59717,0.21067,0.19254],"tcp_start":[0.53138,-0.02094,0.14071],"tcp_to_object_dist_end":0.17722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.6021,0.18913,0.01602],"object_pos_start":[0.60209,0.18915,0.0167],"object_to_goal_dist_end":0.19542,"object_to_goal_dist_start":0.19476,"object_z_max":0.0167,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1907.0,"raw_peak_contact_force":0.13144,"subtask_id":"place_at_goal","tcp_end":[0.60544,0.22417,0.2133],"tcp_start":[0.59717,0.21067,0.19254],"tcp_to_object_dist_end":0.2004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6021,0.18913,0.01602],"object_pos_start":[0.6021,0.18913,0.01602],"object_to_goal_dist_end":0.19542,"object_to_goal_dist_start":0.19542,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.60095,0.22227,0.23262],"tcp_start":[0.60544,0.22417,0.2133],"tcp_to_object_dist_end":0.21913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":31.0,"n_steps_budget":600.0,"object_pos_end":[0.6021,0.18913,0.01602],"object_pos_start":[0.6021,0.18913,0.01602],"object_to_goal_dist_end":0.19542,"object_to_goal_dist_start":0.19542,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":124.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.60281,0.2235,0.23966],"tcp_start":[0.60095,0.22227,0.23262],"tcp_to_object_dist_end":0.22626,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81457,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18251,"descend_1.grasp_offset_z":0.00797,"descend_to_goal.place_offset_z":-0.014,"grasp_1.grasp_duration":1.94825,"lift_1.lift_height":0.12932,"release_1.release_duration":1.38712,"retract_1.retract_height":0.10584,"transport_1.transport_speed":0.51674,"transport_1.transport_xy_offset_x":0.02578,"transport_1.transport_xy_offset_y":-0.0012,"transport_1.transport_z_offset_delta":-0.01417},"optimized_scores":{"best_composite_score":-0.07797,"best_fitness_score":0.65203,"best_task_score":0.3628},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":241.0,"contact_point_centroid":[0.6208,0.1535,-0.00502],"force_p95":1.02624,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31439,"mean_force":0.28215,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6314,0.15603,0.15972]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.54387,-0.02841,-0.00139],"force_p95":0.41524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47953,"mean_force":0.09265,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52957,-0.02821,0.03817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":637.0,"contact_point_centroid":[0.64019,0.1756,0.14336],"force_p95":0.14262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3976,"mean_force":0.09548,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63551,0.15734,0.14662]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4551.0,"contact_point_centroid":[0.53625,-0.04748,0.0835],"force_p95":0.11145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33888,"mean_force":0.07931,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53295,-0.02839,0.08102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":704.0,"contact_point_centroid":[0.63923,0.13874,0.14446],"force_p95":0.17624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30261,"mean_force":0.08609,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63552,0.15735,0.14664]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":544.0,"contact_point_centroid":[0.64716,0.13523,0.14874],"force_p95":0.14188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2871,"mean_force":0.09352,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.64317,0.15388,0.15055]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":498.0,"contact_point_centroid":[0.64823,0.17215,0.14775],"force_p95":0.15426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.284,"mean_force":0.10437,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.64316,0.15387,0.15053]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5954.0,"contact_point_centroid":[0.60114,0.04843,0.14309],"force_p95":0.13339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27826,"mean_force":0.08865,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59623,0.06731,0.14232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5705.0,"contact_point_centroid":[0.53632,-0.00985,0.08076],"force_p95":0.10739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27713,"mean_force":0.06626,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53274,-0.02838,0.07938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6562.0,"contact_point_centroid":[0.60039,0.0822,0.14189],"force_p95":0.12002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.248,"mean_force":0.08224,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59415,0.06392,0.14193]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54566,-0.02927,-0.00209],"force_p95":0.14721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19872,"mean_force":0.12937,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53188,-0.02826,0.0383]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.61884,0.15217,-0.00194],"force_p95":0.152,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16606,"mean_force":0.12168,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62975,0.15902,0.20975]},{"body_a":"world","body_b":"grasp_target","contact_count":692.0,"contact_point_centroid":[0.5456,-0.02923,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51544,-0.01077,0.26394]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5290.0,"contact_point_centroid":[0.5318,-0.0093,0.03914],"force_p95":0.06888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13646,"mean_force":0.04084,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53062,-0.02823,0.03682]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53511,-0.02549,0.13659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4204.0,"contact_point_centroid":[0.53153,-0.04755,0.03955],"force_p95":0.09237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09445,"mean_force":0.05447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53063,-0.02823,0.03683]}],"total_contact_groups":16},"final_pose_error":0.02991,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61883,0.15216,0.02602],"final_tcp_position":[0.6303,0.16255,0.25306],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.53299,-0.02263,0.22629],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1632.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53962,-0.02844,0.04759],"tcp_start":[0.53299,-0.02263,0.22629],"tcp_to_object_dist_end":0.0224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54568,-0.02887,0.02567],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26082,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14611,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11294.0,"raw_peak_contact_force":0.19872,"subtask_id":"reach_object","tcp_end":[0.53059,-0.02823,0.03679],"tcp_start":[0.53962,-0.02844,0.04759],"tcp_to_object_dist_end":0.01875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":351.0,"n_steps_budget":750.0,"object_pos_end":[0.55671,-0.02923,0.11843],"object_pos_start":[0.54568,-0.02887,0.02567],"object_to_goal_dist_end":0.2166,"object_to_goal_dist_start":0.26082,"object_z_max":0.11819,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10338.0,"raw_peak_contact_force":0.47953,"subtask_id":"lift_object","tcp_end":[0.53992,-0.02869,0.13588],"tcp_start":[0.53059,-0.02823,0.03679],"tcp_to_object_dist_end":0.02422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.65326,0.15127,0.1204],"object_pos_start":[0.55671,-0.02923,0.11843],"object_to_goal_dist_end":0.06163,"object_to_goal_dist_start":0.2166,"object_z_max":0.12041,"peak_contact_force":0.11814,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12516.0,"raw_peak_contact_force":0.27826,"subtask_id":"transport_to_goal","tcp_end":[0.64779,0.15126,0.15175],"tcp_start":[0.53992,-0.02869,0.13588],"tcp_to_object_dist_end":0.03183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.64322,0.1574,0.11875],"object_pos_start":[0.65326,0.15127,0.1204],"object_to_goal_dist_end":0.05956,"object_to_goal_dist_start":0.06163,"object_z_max":0.1204,"peak_contact_force":0.12876,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1042.0,"raw_peak_contact_force":0.2871,"subtask_id":"place_at_goal","tcp_end":[0.6376,0.15739,0.15088],"tcp_start":[0.64779,0.15126,0.15175],"tcp_to_object_dist_end":0.03262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62247,0.15267,0.02607],"object_pos_start":[0.64322,0.1574,0.11875],"object_to_goal_dist_end":0.1517,"object_to_goal_dist_start":0.05956,"object_z_max":0.11879,"peak_contact_force":0.11311,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1582.0,"raw_peak_contact_force":1.31439,"subtask_id":"place_at_goal","tcp_end":[0.63135,0.15602,0.16963],"tcp_start":[0.6376,0.15739,0.15088],"tcp_to_object_dist_end":0.14387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":720.0,"object_pos_end":[0.61883,0.15216,0.02602],"object_pos_start":[0.62247,0.15267,0.02607],"object_to_goal_dist_end":0.15209,"object_to_goal_dist_start":0.1517,"object_z_max":0.0266,"peak_contact_force":0.12287,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":780.0,"raw_peak_contact_force":0.16606,"subtask_id":"place_at_goal","tcp_end":[0.6303,0.16255,0.25306],"tcp_start":[0.63135,0.15602,0.16963],"tcp_to_object_dist_end":0.22756,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```