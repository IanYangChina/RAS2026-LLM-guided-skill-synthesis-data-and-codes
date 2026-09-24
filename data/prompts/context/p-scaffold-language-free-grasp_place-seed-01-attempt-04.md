## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.1764 | 0.43 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4387 | 0.79 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2393 | 0.40 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3429 | 0.34 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3438 | 0.34 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=0.176) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: subtask_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: subtask_lift
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: subtask_place
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_1
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
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_approach
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: lift_1
  type: lift
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_success
    when: after_phase
    predicate: object_lifted
    args:
      z_threshold: 0.08
    threshold: 0.08
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: subtask_lift
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_goal
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.05
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_place

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_success, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.08, args={'z_threshold': 0.08}
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.176
- **task_score** (E): 0.428
- **fitness_score**: 0.681  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0749 |
| descend_1 | 1.00 | 1.00 | 0.1951 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 1.00 | 0.1877 |
| approach_goal | 1.00 | 1.00 | 0.2387 |
| descend_goal | 1.00 | 1.00 | 0.0050 |
| release_1 | 1.00 | 1.00 | 0.0204 |
| retract_1 | 1.00 | 1.00 | 0.0215 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.482, -0.003, 0.245) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.482, -0.003, 0.245)→(0.475, -0.001, 0.051) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.475, -0.001, 0.051)→(0.467, -0.001, 0.043) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 42.333 | 0.152 | 0.206 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.001, 0.043)→(0.475, -0.001, 0.230) | (0.479, -0.001, 0.026)→(0.483, -0.000, 0.208) | 0.278→0.257 | 1.00 / 31.667 | 75.618 | 0.444 |
| approach_goal | approach | 1.00 / step_budget | (0.475, -0.001, 0.230)→(0.598, 0.191, 0.251) | (0.483, -0.000, 0.208)→(0.605, 0.184, 0.154) | 0.257→0.093 | 1.00 / 31.000 | 91004.791 | 0.767 |
| descend_goal | descend | 1.00 / force_exceeded | (0.598, 0.191, 0.251)→(0.600, 0.193, 0.247) | (0.605, 0.184, 0.154)→(0.605, 0.186, 0.149) | 0.093→0.088 | 1.00 / 31.667 | 59318.487 | 0.165 |
| release_1 | release | 1.00 / step_budget | (0.600, 0.193, 0.247)→(0.595, 0.192, 0.267) | (0.605, 0.186, 0.149)→(0.600, 0.183, 0.016) | 0.088→0.137 | 1.00 / 3.000 | 0.248 | 1.256 |
| retract_1 | retract | 1.00 / step_budget | (0.595, 0.192, 0.267)→(0.600, 0.198, 0.264) | (0.600, 0.183, 0.016)→(0.601, 0.180, 0.024) | 0.137→0.130 | 1.00 / 2.333 | 0.241 | 0.261 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.539
- phase_score: 0.124
- phase_breakdown.subtask_approach_score: 0.126
- phase_breakdown.subtask_lift_score: 0.302
- phase_breakdown.subtask_place_score: 0.018
- grasp_place_fitness: 0.742

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.742
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.539
- **Median Q (composite search score)**: 0.155
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.426


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57377,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25237,"approach_goal.approach_goal_offset_z":0.13044,"descend_1.depth":0.02502,"descend_goal.place_force_threshold":2.51584,"descend_goal.place_offset_z":0.01511,"lift_1.lift_height":0.17561,"lift_1.lift_speed":0.06978,"release_1.release_duration":0.49412,"retract_1.retract_z":0.18227},"optimized_scores":{"best_composite_score":0.15512,"best_fitness_score":0.66012,"best_task_score":0.40635},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":361.0,"contact_point_centroid":[0.56833,0.21082,-0.00521],"force_p95":1.16521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96345,"mean_force":0.27378,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55357,0.21952,0.2582]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.4989,0.04166,-0.00156],"force_p95":0.30376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37994,"mean_force":0.08036,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48783,0.04273,0.05237]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.49272,0.0239,0.10724],"force_p95":0.13954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35487,"mean_force":0.09567,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4905,0.04272,0.1098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7330.0,"contact_point_centroid":[0.49153,0.06105,0.10732],"force_p95":0.12625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27751,"mean_force":0.06776,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4903,0.04271,0.10774]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04492,-0.00219],"force_p95":0.17618,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22591,"mean_force":0.13594,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48996,0.04295,0.05207]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3936.0,"contact_point_centroid":[0.52314,0.09662,0.2069],"force_p95":0.13632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22558,"mean_force":0.10555,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51813,0.11471,0.21034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3952.0,"contact_point_centroid":[0.52247,0.131,0.20603],"force_p95":0.13928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20179,"mean_force":0.10718,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51755,0.11289,0.20957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3380.0,"contact_point_centroid":[0.49126,0.0237,0.05024],"force_p95":0.10961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15636,"mean_force":0.06252,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48884,0.04285,0.05084]},{"body_a":"world","body_b":"grasp_target","contact_count":296.0,"contact_point_centroid":[0.50118,0.04505,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1245,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49915,0.01152,0.2934]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56867,0.21123,-0.00197],"force_p95":0.12997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13581,"mean_force":0.12315,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55498,0.23089,0.26515]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.56868,0.21127,-0.00165],"force_p95":0.13557,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13578,"mean_force":0.12239,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5578,0.23175,0.26382]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49672,0.03462,0.17126]},{"body_a":"world","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.56867,0.21122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55679,0.23517,0.29688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4873.0,"contact_point_centroid":[0.48937,0.06161,0.05108],"force_p95":0.07516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07908,"mean_force":0.04399,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48885,0.04285,0.05085]},{"body_a":"left_finger","body_b":"right_finger","contact_count":192.0,"contact_point_centroid":[0.55641,0.22573,0.26299],"force_p95":0.01476,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01168,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55571,0.22571,0.26105]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.5572,0.23192,0.26326],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55671,0.2319,0.26109]}],"total_contact_groups":17},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56867,0.21122,0.01602],"final_tcp_position":[0.56007,0.24021,0.31033],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273014.23406,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02593],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24193,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12241,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":296.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.4988,0.02583,0.28568],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02593],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24193,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2780.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.49671,0.04352,0.05952],"tcp_start":[0.4988,0.02583,0.28568],"tcp_to_object_dist_end":0.03384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04334,0.02529],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24367,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17556,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10053.0,"raw_peak_contact_force":0.22591,"tcp_end":[0.48882,0.04284,0.05081],"tcp_start":[0.49671,0.04352,0.05952],"tcp_to_object_dist_end":0.02835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.50452,0.04447,0.14971],"object_pos_start":[0.50116,0.04334,0.02529],"object_to_goal_dist_end":0.20917,"object_to_goal_dist_start":0.24367,"object_z_max":0.14944,"peak_contact_force":0.13306,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12228.0,"raw_peak_contact_force":0.37994,"subtask_id":"subtask_lift","tcp_end":[0.49651,0.04296,0.18165],"tcp_start":[0.48882,0.04284,0.05081],"tcp_to_object_dist_end":0.03297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.56864,0.2111,0.0167],"object_pos_start":[0.50452,0.04447,0.14971],"object_to_goal_dist_end":0.13445,"object_to_goal_dist_start":0.20917,"object_z_max":0.20224,"peak_contact_force":273014.23406,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8441.0,"raw_peak_contact_force":1.96345,"tcp_end":[0.5578,0.23175,0.26382],"tcp_start":[0.49651,0.04296,0.18165],"tcp_to_object_dist_end":0.24822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.56863,0.21108,0.01667],"object_pos_start":[0.56864,0.2111,0.0167],"object_to_goal_dist_end":0.13449,"object_to_goal_dist_start":0.13445,"object_z_max":0.0167,"peak_contact_force":9748.11863,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":0.13578,"subtask_id":"subtask_place","tcp_end":[0.55781,0.23193,0.2638],"tcp_start":[0.5578,0.23175,0.26382],"tcp_to_object_dist_end":0.24825,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56867,0.21122,0.01602],"object_pos_start":[0.56863,0.21108,0.01667],"object_to_goal_dist_end":0.13508,"object_to_goal_dist_start":0.13449,"object_z_max":0.01667,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.13581,"tcp_end":[0.55405,0.23035,0.28501],"tcp_start":[0.55781,0.23193,0.2638],"tcp_to_object_dist_end":0.27006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":120.0,"n_steps_budget":600.0,"object_pos_end":[0.56867,0.21122,0.01602],"object_pos_start":[0.56867,0.21122,0.01602],"object_to_goal_dist_end":0.13508,"object_to_goal_dist_start":0.13508,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":480.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56007,0.24021,0.31033],"tcp_start":[0.55405,0.23035,0.28501],"tcp_to_object_dist_end":0.29586,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25941,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09222,"approach_goal.approach_goal_offset_z":0.06776,"descend_1.depth":0.0108,"descend_goal.place_force_threshold":3.63728,"descend_goal.place_offset_z":0.05375,"lift_1.lift_height":0.21281,"lift_1.lift_speed":0.04323,"release_1.release_duration":0.66249,"retract_1.retract_z":0.0759},"optimized_scores":{"best_composite_score":0.13715,"best_fitness_score":0.64215,"best_task_score":0.33803},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.61794,0.15233,-0.01308],"force_p95":1.58481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64668,"mean_force":0.81638,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6189,0.15218,0.24858]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.47238,-0.01935,-0.00148],"force_p95":0.4597,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47176,"mean_force":0.18978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46334,-0.01948,0.03903]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12469.0,"contact_point_centroid":[0.46658,-0.03859,0.13052],"force_p95":0.07527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26309,"mean_force":0.0518,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46644,-0.01945,0.12859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12180.0,"contact_point_centroid":[0.46651,-0.0003,0.12886],"force_p95":0.07465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26025,"mean_force":0.05263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46633,-0.01945,0.12679]},{"body_a":"world","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.61781,0.15264,-0.00642],"force_p95":0.17105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18935,"mean_force":0.1148,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61934,0.15244,0.25611]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02006,-0.00206],"force_p95":0.13968,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18921,"mean_force":0.12726,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46532,-0.01952,0.03915]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9200.0,"contact_point_centroid":[0.62161,0.17051,0.24025],"force_p95":0.06247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15982,"mean_force":0.04304,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62113,0.15133,0.23826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8400.0,"contact_point_centroid":[0.62067,0.1321,0.24088],"force_p95":0.0674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14776,"mean_force":0.0462,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62113,0.15133,0.23826]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.47616,-0.02015,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48807,-0.0083,0.22249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12149.0,"contact_point_centroid":[0.54912,0.08812,0.23435],"force_p95":0.07832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12493,"mean_force":0.0539,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54879,0.0689,0.23213]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47294,-0.01841,0.09324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14443.0,"contact_point_centroid":[0.5458,0.04673,0.23296],"force_p95":0.06877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11675,"mean_force":0.04644,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.546,0.06577,0.23155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4831.0,"contact_point_centroid":[0.46426,-0.00028,0.04045],"force_p95":0.0681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10058,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46422,-0.01949,0.03805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5159.0,"contact_point_centroid":[0.46412,-0.03871,0.03997],"force_p95":0.0669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08061,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46422,-0.01949,0.03805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.62132,0.13394,0.2351],"force_p95":0.06698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06874,"mean_force":0.03969,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62203,0.15321,0.23281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.62219,0.17243,0.23427],"force_p95":0.0638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06758,"mean_force":0.0386,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62203,0.15321,0.2328]}],"total_contact_groups":16},"final_pose_error":0.01629,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61828,0.15096,0.02806],"final_tcp_position":[0.62027,0.153,0.25578],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":255.61251,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1200.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.47644,-0.01725,0.1419],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":305.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.12263,"subtask_id":"subtask_approach","tcp_end":[0.47195,-0.01967,0.04585],"tcp_start":[0.47644,-0.01725,0.1419],"tcp_to_object_dist_end":0.02028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01961,0.02578],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13745,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11790.0,"raw_peak_contact_force":0.18921,"tcp_end":[0.46419,-0.01949,0.03802],"tcp_start":[0.47195,-0.01967,0.04585],"tcp_to_object_dist_end":0.01705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.48051,-0.01933,0.20298],"object_pos_start":[0.47607,-0.01961,0.02578],"object_to_goal_dist_end":0.23412,"object_to_goal_dist_start":0.28823,"object_z_max":0.2027,"peak_contact_force":0.07828,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24731.0,"raw_peak_contact_force":0.47176,"subtask_id":"subtask_lift","tcp_end":[0.47218,-0.01951,0.21908],"tcp_start":[0.46419,-0.01949,0.03802],"tcp_to_object_dist_end":0.01813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":659.0,"n_steps_budget":1000.0,"object_pos_end":[0.62359,0.14747,0.22607],"object_pos_start":[0.48051,-0.01933,0.20298],"object_to_goal_dist_end":0.03871,"object_to_goal_dist_start":0.23412,"object_z_max":0.22606,"peak_contact_force":0.06667,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26592.0,"raw_peak_contact_force":0.12493,"tcp_end":[0.61923,0.14761,0.24739],"tcp_start":[0.47218,-0.01951,0.21908],"tcp_to_object_dist_end":0.02177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.62594,0.15339,0.21348],"object_pos_start":[0.62359,0.14747,0.22607],"object_to_goal_dist_end":0.02478,"object_to_goal_dist_start":0.03871,"object_z_max":0.22607,"peak_contact_force":255.61251,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17600.0,"raw_peak_contact_force":0.15982,"subtask_id":"subtask_place","tcp_end":[0.62332,0.15355,0.23634],"tcp_start":[0.61923,0.14761,0.24739],"tcp_to_object_dist_end":0.02302,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61812,0.15091,0.01737],"object_pos_start":[0.62594,0.15339,0.21348],"object_to_goal_dist_end":0.17336,"object_to_goal_dist_start":0.02478,"object_z_max":0.21348,"peak_contact_force":0.20016,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2720.0,"raw_peak_contact_force":1.64668,"tcp_end":[0.61888,0.15218,0.25593],"tcp_start":[0.62332,0.15355,0.23634],"tcp_to_object_dist_end":0.23856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.61828,0.15096,0.02806],"object_pos_start":[0.61812,0.15091,0.01737],"object_to_goal_dist_end":0.16269,"object_to_goal_dist_start":0.17336,"object_z_max":0.02774,"peak_contact_force":0.12877,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":40.0,"raw_peak_contact_force":0.18935,"tcp_end":[0.62027,0.153,0.25578],"tcp_start":[0.61888,0.15218,0.25593],"tcp_to_object_dist_end":0.22773,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39544,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28907,"approach_goal.approach_goal_offset_z":0.13412,"descend_1.depth":0.01125,"descend_goal.place_force_threshold":10.8666,"descend_goal.place_offset_z":0.03694,"lift_1.lift_height":0.28364,"lift_1.lift_speed":0.05283,"release_1.release_duration":0.61547,"retract_1.retract_z":0.09624},"optimized_scores":{"best_composite_score":0.23707,"best_fitness_score":0.74207,"best_task_score":0.53869},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.60519,0.19573,-0.01049],"force_p95":1.65994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98536,"mean_force":0.62243,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61318,0.19297,0.25284]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45609,-0.02502,-0.00144],"force_p95":0.43213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48121,"mean_force":0.12751,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4466,-0.02538,0.04036]},{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.61046,0.18845,-0.00573],"force_p95":0.45688,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4716,"mean_force":0.26139,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61596,0.19556,0.24871]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17129.0,"contact_point_centroid":[0.44951,-0.04457,0.1656],"force_p95":0.07414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27982,"mean_force":0.05081,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44968,-0.02539,0.16408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17610.0,"contact_point_centroid":[0.44942,-0.00622,0.16719],"force_p95":0.07268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27276,"mean_force":0.04933,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44975,-0.02539,0.16564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12694.0,"contact_point_centroid":[0.53938,0.06817,0.26616],"force_p95":0.08249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21153,"mean_force":0.05679,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53801,0.08732,0.2636]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02622,-0.00207],"force_p95":0.14419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20169,"mean_force":0.12843,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44866,-0.02546,0.04023]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.61874,0.17522,0.24319],"force_p95":0.13346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20011,"mean_force":0.05133,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61774,0.1943,0.24165]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.61869,0.21346,0.24279],"force_p95":0.14008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17759,"mean_force":0.07324,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61774,0.19429,0.24166]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14223.0,"contact_point_centroid":[0.53735,0.10385,0.26581],"force_p95":0.07613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14779,"mean_force":0.05142,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53616,0.08485,0.26407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.61691,0.17511,0.23805],"force_p95":0.06301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14229,"mean_force":0.03936,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61611,0.19424,0.23646]},{"body_a":"world","body_b":"grasp_target","contact_count":344.0,"contact_point_centroid":[0.45856,-0.02632,-0.00164],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12417,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48626,-0.00772,0.30331]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.61686,0.21354,0.23788],"force_p95":0.06925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13481,"mean_force":0.04123,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61606,0.19422,0.23632]},{"body_a":"world","body_b":"grasp_target","contact_count":3268.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46257,-0.02115,0.17589]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4895.0,"contact_point_centroid":[0.44762,-0.00623,0.041],"force_p95":0.06984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11903,"mean_force":0.04413,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4476,-0.02542,0.03921]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4940.0,"contact_point_centroid":[0.4478,-0.04465,0.0411],"force_p95":0.0706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07828,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4476,-0.02542,0.03921]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61478,0.17827,0.02764],"final_tcp_position":[0.62082,0.2006,0.22634],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":87.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02599],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30366,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12209,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":344.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.47191,-0.01669,0.30802],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02599],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30366,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3268.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.4551,-0.02567,0.04648],"tcp_start":[0.47191,-0.01669,0.30802],"tcp_to_object_dist_end":0.02076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02565,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30326,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14183,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11635.0,"raw_peak_contact_force":0.20169,"tcp_end":[0.44757,-0.02542,0.03918],"tcp_start":[0.4551,-0.02567,0.04648],"tcp_to_object_dist_end":0.01733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.46334,-0.02568,0.27083],"object_pos_start":[0.45848,-0.02565,0.02573],"object_to_goal_dist_end":0.32724,"object_to_goal_dist_start":0.30326,"object_z_max":0.27055,"peak_contact_force":226.64272,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34819.0,"raw_peak_contact_force":0.48121,"subtask_id":"subtask_lift","tcp_end":[0.45553,-0.02553,0.28984],"tcp_start":[0.44757,-0.02542,0.03918],"tcp_to_object_dist_end":0.02056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.62197,0.19366,0.21964],"object_pos_start":[0.46334,-0.02568,0.27083],"object_to_goal_dist_end":0.10683,"object_to_goal_dist_start":0.32724,"object_z_max":0.27099,"peak_contact_force":0.07095,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26917.0,"raw_peak_contact_force":0.21153,"tcp_end":[0.61776,0.19389,0.24226],"tcp_start":[0.45553,-0.02553,0.28984],"tcp_to_object_dist_end":0.02302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.62175,0.19472,0.21787],"object_pos_start":[0.62197,0.19366,0.21964],"object_to_goal_dist_end":0.10496,"object_to_goal_dist_start":0.10683,"object_z_max":0.21964,"peak_contact_force":167951.73011,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":298.0,"raw_peak_contact_force":0.20011,"subtask_id":"subtask_place","tcp_end":[0.61764,0.19462,0.24065],"tcp_start":[0.61776,0.19389,0.24226],"tcp_to_object_dist_end":0.02315,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61374,0.18688,0.01532],"object_pos_start":[0.62175,0.19472,0.21787],"object_to_goal_dist_end":0.1024,"object_to_goal_dist_start":0.10496,"object_z_max":0.21787,"peak_contact_force":0.42132,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2796.0,"raw_peak_contact_force":1.98536,"tcp_end":[0.61316,0.19296,0.2596],"tcp_start":[0.61764,0.19462,0.24065],"tcp_to_object_dist_end":0.24435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":73.0,"n_steps_budget":600.0,"object_pos_end":[0.61478,0.17827,0.02764],"object_pos_start":[0.61374,0.18688,0.01532],"object_to_goal_dist_end":0.09279,"object_to_goal_dist_start":0.1024,"object_z_max":0.03074,"peak_contact_force":0.4716,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":97.0,"raw_peak_contact_force":0.4716,"tcp_end":[0.62082,0.2006,0.22634],"tcp_start":[0.61316,0.19296,0.2596],"tcp_to_object_dist_end":0.20004,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```