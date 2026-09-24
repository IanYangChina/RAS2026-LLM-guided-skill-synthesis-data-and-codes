## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 9 | 0.0687 | 0.41 | ❌ rejected |
| 12 | approach → align → grasp → lift → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0623 | 0.61 | ❌ rejected |
| 11 | approach → align → grasp → lift → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3276 | 0.77 | ❌ rejected |
| 10 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4359 | 0.83 | ❌ rejected |
| 9 | approach → align → grasp → lift → lift | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7 | 0.4185 | 0.79 | ❌ rejected |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.900, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.069) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.15
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.25
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_goal
  weight: 0.4
phases:
- id: approach_object
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
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.003
  subtask_id: grasp_object
- id: lift_to_clear
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_to_goal
  type: lift
  generator: linear_cartesian
  control: position_control
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
      mode: none
  parameters:
    place_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    place_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.003]
- **lift_to_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`lift`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_offset_y: status=consumed; consumers=target.offset.y (replace)
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.069
- **task_score** (E): 0.413
- **fitness_score**: 0.669  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1863 |
| descend_grasp | 1.00 | 1.00 | 0.0644 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift_to_clear | 0.67 | 1.00 | 0.1231 |
| transport_to_goal | 1.00 | 1.00 | 0.2467 |
| release_object | 1.00 | 1.00 | 0.0215 |
| retract_after_release | 1.00 | 1.00 | 0.0853 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | align | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.667 | 0.146 | 0.197 |
| lift_to_clear | lift | 0.67 / step_budget | (0.466, -0.001, 0.047)→(0.463, -0.001, 0.170) | (0.479, -0.001, 0.026)→(0.471, -0.000, 0.141) | 0.278→0.255 | 1.00 / 30.333 | 0.101 | 0.428 |
| transport_to_goal | push | 1.00 / step_budget | (0.463, -0.001, 0.170)→(0.589, 0.197, 0.213) | (0.471, -0.000, 0.141)→(0.591, 0.187, 0.128) | 0.255→0.057 | 1.00 / 7.000 | 55984.034 | 0.850 |
| release_object | release | 1.00 / step_budget | (0.589, 0.197, 0.213)→(0.584, 0.196, 0.234) | (0.591, 0.187, 0.128)→(0.603, 0.180, 0.019) | 0.057→0.136 | 1.00 / 4.000 | 0.148 | 1.201 |
| retract_after_release | retract | 1.00 / step_budget | (0.584, 0.196, 0.234)→(0.582, 0.195, 0.320) | (0.603, 0.180, 0.019)→(0.602, 0.180, 0.019) | 0.136→0.135 | 1.00 / 4.000 | 0.123 | 0.148 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.489
- phase_score: 0.475
- phase_breakdown.lift_object_score: 0.717
- phase_breakdown.reach_object_score: 0.819
- phase_breakdown.grasp_object_score: 0.788
- phase_breakdown.reach_goal_score: 0.028
- grasp_place_fitness: 0.706

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.706
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.489
- **Median Q (composite search score)**: 0.081
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85034,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.10183,"descend_grasp.descend_speed":0.05972,"lift_to_clear.lift_speed":0.17439,"retract_after_release.retract_speed":0.17179,"transport_to_goal.arc_height":0.05278,"transport_to_goal.place_offset_x":-0.00816,"transport_to_goal.place_offset_y":0.00744,"transport_to_goal.place_offset_z":0.04929,"transport_to_goal.transport_speed":0.11272},"optimized_scores":{"best_composite_score":0.08079,"best_fitness_score":0.68079,"best_task_score":0.43579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":364.0,"contact_point_centroid":[0.56056,0.22027,-0.00506],"force_p95":1.06272,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4484,"mean_force":0.27268,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5432,0.23359,0.20778]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.55346,0.21981,0.19409],"force_p95":0.34776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49846,"mean_force":0.13174,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54714,0.23555,0.20059]},{"body_a":"world","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.49877,0.04217,-0.00123],"force_p95":0.25743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49286,"mean_force":0.06276,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48677,0.04314,0.04782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":50.0,"contact_point_centroid":[0.54398,0.25345,0.19706],"force_p95":0.31404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33555,"mean_force":0.18753,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54727,0.23558,0.20085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7991.0,"contact_point_centroid":[0.48718,0.02402,0.10392],"force_p95":0.10932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31476,"mean_force":0.06983,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48456,0.04294,0.10314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8810.0,"contact_point_centroid":[0.48745,0.06183,0.10159],"force_p95":0.10553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31255,"mean_force":0.06549,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.48459,0.04294,0.10039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6089.0,"contact_point_centroid":[0.5183,0.10649,0.21307],"force_p95":0.13367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3084,"mean_force":0.09335,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.51015,0.12385,0.21562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5876.0,"contact_point_centroid":[0.51283,0.14012,0.21413],"force_p95":0.13556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28824,"mean_force":0.09585,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.50923,0.12116,0.2157]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22282,"mean_force":0.13351,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48934,0.04338,0.04702]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.56157,0.21433,-0.002],"force_p95":0.12877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19308,"mean_force":0.12268,"phase_index":6.0,"phase_name":"retract_after_release","phase_type":"retract","tcp_position_centroid":[0.54059,0.23247,0.26525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4331.0,"contact_point_centroid":[0.48846,0.02402,0.04756],"force_p95":0.0781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14015,"mean_force":0.04967,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48821,0.04328,0.04579]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49758,0.02042,0.20861]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.49547,0.04263,0.08616]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5517.0,"contact_point_centroid":[0.48905,0.06245,0.04823],"force_p95":0.07068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07276,"mean_force":0.04035,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48821,0.04328,0.0458]}],"total_contact_groups":14},"final_pose_error":0.01443,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56157,0.21432,0.02602],"final_tcp_position":[0.54078,0.23251,0.30981],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.4484,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49717,0.0415,0.11821],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":780.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":880.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49607,0.04398,0.05442],"tcp_start":[0.49717,0.0415,0.11821],"tcp_to_object_dist_end":0.02888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04378,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24322,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16083,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11648.0,"raw_peak_contact_force":0.22282,"subtask_id":"grasp_object","tcp_end":[0.48818,0.04327,0.04576],"tcp_start":[0.49607,0.04398,0.05442],"tcp_to_object_dist_end":0.0241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49742,0.04364,0.15144],"object_pos_start":[0.50115,0.04378,0.02547],"object_to_goal_dist_end":0.21214,"object_to_goal_dist_start":0.24322,"object_z_max":0.15125,"peak_contact_force":0.10057,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16928.0,"raw_peak_contact_force":0.49286,"subtask_id":"lift_object","tcp_end":[0.48483,0.04296,0.1806],"tcp_start":[0.48818,0.04327,0.04576],"tcp_to_object_dist_end":0.03177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.55052,0.2385,0.16485],"object_pos_start":[0.49742,0.04364,0.15144],"object_to_goal_dist_end":0.02367,"object_to_goal_dist_start":0.21214,"object_z_max":0.2011,"peak_contact_force":0.24392,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11965.0,"raw_peak_contact_force":0.3084,"subtask_id":"reach_goal","tcp_end":[0.54811,0.23533,0.20235],"tcp_start":[0.48483,0.04296,0.1806],"tcp_to_object_dist_end":0.03771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56177,0.21286,0.02554],"object_pos_start":[0.55052,0.2385,0.16485],"object_to_goal_dist_end":0.12542,"object_to_goal_dist_start":0.02367,"object_z_max":0.16485,"peak_contact_force":0.19459,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":522.0,"raw_peak_contact_force":1.4484,"subtask_id":"reach_goal","tcp_end":[0.54297,0.23348,0.22404],"tcp_start":[0.54811,0.23533,0.20235],"tcp_to_object_dist_end":0.20045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":600.0,"object_pos_end":[0.56157,0.21432,0.02602],"object_pos_start":[0.56177,0.21286,0.02554],"object_to_goal_dist_end":0.12459,"object_to_goal_dist_start":0.12542,"object_z_max":0.02604,"peak_contact_force":0.12263,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.19308,"subtask_id":"reach_goal","tcp_end":[0.54078,0.23251,0.30981],"tcp_start":[0.54297,0.23348,0.22404],"tcp_to_object_dist_end":0.28513,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85165,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.073,"descend_grasp.descend_speed":0.15556,"lift_to_clear.lift_speed":0.04354,"retract_after_release.retract_speed":0.14926,"transport_to_goal.arc_height":0.06197,"transport_to_goal.place_offset_x":-0.0009,"transport_to_goal.place_offset_y":0.01022,"transport_to_goal.place_offset_z":0.06655,"transport_to_goal.transport_speed":0.15006},"optimized_scores":{"best_composite_score":0.01912,"best_fitness_score":0.61912,"best_task_score":0.3134},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":445.0,"contact_point_centroid":[0.63439,0.15735,-0.00463],"force_p95":1.12102,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02871,"mean_force":0.2539,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61221,0.15496,0.25946]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12437.0,"contact_point_centroid":[0.51486,0.02401,0.21981],"force_p95":0.10733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46102,"mean_force":0.0645,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.51378,0.04273,0.22153]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11225.0,"contact_point_centroid":[0.50659,0.05668,0.21654],"force_p95":0.12896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45295,"mean_force":0.0688,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.50953,0.03806,0.21831]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.47143,-0.01918,-0.00119],"force_p95":0.32821,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38845,"mean_force":0.08867,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.46234,-0.01953,0.04843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21641.0,"contact_point_centroid":[0.45943,-0.03855,0.09581],"force_p95":0.07069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25918,"mean_force":0.04755,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45987,-0.01945,0.09504]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18893.0,"contact_point_centroid":[0.45967,-0.00026,0.096],"force_p95":0.07685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25917,"mean_force":0.05396,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.45987,-0.01945,0.095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22.0,"contact_point_centroid":[0.61531,0.14127,0.24693],"force_p95":0.23225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24987,"mean_force":0.06855,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61627,0.15599,0.25398]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13753,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17744,"mean_force":0.12661,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46495,-0.01959,0.04808]},{"body_a":"world","body_b":"grasp_target","contact_count":2228.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13187,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48619,-0.00906,0.20978]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.63454,0.15675,-0.00199],"force_p95":0.12334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12739,"mean_force":0.12271,"phase_index":6.0,"phase_name":"retract_after_release","phase_type":"retract","tcp_position_centroid":[0.61009,0.15437,0.31524]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.47173,-0.01909,0.08701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.4634,-0.00032,0.04913],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0991,"mean_force":0.04499,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46386,-0.01956,0.04698]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5390.0,"contact_point_centroid":[0.46344,-0.03878,0.04883],"force_p95":0.06506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0819,"mean_force":0.04101,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46387,-0.01956,0.04698]}],"total_contact_groups":13},"final_pose_error":0.01517,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63454,0.15675,0.01602],"final_tcp_position":[0.61038,0.15441,0.35982],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2228.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47401,-0.01852,0.11934],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":852.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47149,-0.01974,0.05479],"tcp_start":[0.47401,-0.01852,0.11934],"tcp_to_object_dist_end":0.02915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13638,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12030.0,"raw_peak_contact_force":0.17744,"subtask_id":"grasp_object","tcp_end":[0.46384,-0.01956,0.04695],"tcp_start":[0.47149,-0.01974,0.05479],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46343,-0.0196,0.11451],"object_pos_start":[0.47609,-0.01971,0.02581],"object_to_goal_dist_end":0.25669,"object_to_goal_dist_start":0.28827,"object_z_max":0.11443,"peak_contact_force":0.07686,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40696.0,"raw_peak_contact_force":0.38845,"subtask_id":"lift_object","tcp_end":[0.45997,-0.01945,0.14199],"tcp_start":[0.46384,-0.01956,0.04695],"tcp_to_object_dist_end":0.0277,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.61235,0.15175,0.2125],"object_pos_start":[0.46343,-0.0196,0.11451],"object_to_goal_dist_end":0.03041,"object_to_goal_dist_start":0.25669,"object_z_max":0.23094,"peak_contact_force":167951.73011,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":23662.0,"raw_peak_contact_force":0.46102,"subtask_id":"reach_goal","tcp_end":[0.61639,0.15582,0.25435],"tcp_start":[0.45997,-0.01945,0.14199],"tcp_to_object_dist_end":0.04224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63469,0.15684,0.01613],"object_pos_start":[0.61235,0.15175,0.2125],"object_to_goal_dist_end":0.17393,"object_to_goal_dist_start":0.03041,"object_z_max":0.2125,"peak_contact_force":0.12762,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":467.0,"raw_peak_contact_force":2.02871,"subtask_id":"reach_goal","tcp_end":[0.61208,0.15492,0.27488],"tcp_start":[0.61639,0.15582,0.25435],"tcp_to_object_dist_end":0.25974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.63454,0.15675,0.01602],"object_pos_start":[0.63469,0.15684,0.01613],"object_to_goal_dist_end":0.17404,"object_to_goal_dist_start":0.17393,"object_z_max":0.01613,"peak_contact_force":0.12263,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.12739,"subtask_id":"reach_goal","tcp_end":[0.61038,0.15441,0.35982],"tcp_start":[0.61208,0.15492,0.27488],"tcp_to_object_dist_end":0.34465,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11765,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.09006,"descend_grasp.descend_speed":0.10781,"lift_to_clear.lift_speed":0.09429,"retract_after_release.retract_speed":0.11764,"transport_to_goal.arc_height":0.0548,"transport_to_goal.place_offset_x":-0.01448,"transport_to_goal.place_offset_y":0.00592,"transport_to_goal.place_offset_z":0.06478,"transport_to_goal.transport_speed":0.17583},"optimized_scores":{"best_composite_score":0.10631,"best_fitness_score":0.70631,"best_task_score":0.48898},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.61123,0.17022,-0.009],"force_p95":1.25718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78038,"mean_force":0.52584,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.59936,0.19455,0.18837]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.45599,-0.02486,-0.00113],"force_p95":0.27903,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4024,"mean_force":0.05465,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44556,-0.02545,0.04959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5740.0,"contact_point_centroid":[0.51172,0.04382,0.21468],"force_p95":0.14262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38794,"mean_force":0.09874,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.50311,0.06058,0.21702]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4746.0,"contact_point_centroid":[0.5086,0.08277,0.21593],"force_p95":0.15944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36478,"mean_force":0.1155,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.50547,0.06385,0.21799]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13303.0,"contact_point_centroid":[0.44598,-0.00641,0.10931],"force_p95":0.10302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28603,"mean_force":0.06812,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44319,-0.02534,0.10883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14693.0,"contact_point_centroid":[0.44573,-0.04419,0.10878],"force_p95":0.09791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26289,"mean_force":0.06267,"phase_index":3.0,"phase_name":"lift_to_clear","phase_type":"lift","tcp_position_centroid":[0.44319,-0.02534,0.10832]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00207],"force_p95":0.14292,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19124,"mean_force":0.12788,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44799,-0.02554,0.04879]},{"body_a":"world","body_b":"grasp_target","contact_count":2216.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47847,-0.01182,0.21002]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61113,0.16907,-0.00224],"force_p95":0.12535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1263,"mean_force":0.11336,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59886,0.19876,0.18401]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.61111,0.16909,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_after_release","phase_type":"retract","tcp_position_centroid":[0.5948,0.19733,0.24444]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"align","tcp_position_centroid":[0.45523,-0.02492,0.0874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44711,-0.00626,0.04887],"force_p95":0.07269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10432,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44694,-0.0255,0.04777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5408.0,"contact_point_centroid":[0.44633,-0.04465,0.04881],"force_p95":0.0653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07668,"mean_force":0.0408,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44694,-0.0255,0.04777]},{"body_a":"left_finger","body_b":"right_finger","contact_count":101.0,"contact_point_centroid":[0.60039,0.19922,0.18074],"force_p95":0.01427,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01439,"mean_force":0.01156,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6006,0.19943,0.1784]}],"total_contact_groups":14},"final_pose_error":0.0152,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61111,0.16909,0.01602],"final_tcp_position":[0.59499,0.19736,0.28893],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.78038,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2216.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45802,-0.02418,0.11972],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45434,-0.02576,0.05504],"tcp_start":[0.45802,-0.02418,0.11972],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02569,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14115,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11562.0,"raw_peak_contact_force":0.19124,"subtask_id":"grasp_object","tcp_end":[0.44691,-0.0255,0.04774],"tcp_start":[0.45434,-0.02576,0.05504],"tcp_to_object_dist_end":0.02486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.45285,-0.02541,0.15671],"object_pos_start":[0.4585,-0.02569,0.02575],"object_to_goal_dist_end":0.29635,"object_to_goal_dist_start":0.30328,"object_z_max":0.15661,"peak_contact_force":0.12541,"phase_name":"lift_to_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28128.0,"raw_peak_contact_force":0.4024,"subtask_id":"lift_object","tcp_end":[0.44347,-0.02534,0.18686],"tcp_start":[0.44691,-0.0255,0.04774],"tcp_to_object_dist_end":0.03158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.60953,0.17018,0.00563],"object_pos_start":[0.45285,-0.02541,0.15671],"object_to_goal_dist_end":0.11679,"object_to_goal_dist_start":0.29635,"object_z_max":0.19656,"peak_contact_force":0.12853,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10618.0,"raw_peak_contact_force":1.78038,"subtask_id":"reach_goal","tcp_end":[0.60301,0.19982,0.18348],"tcp_start":[0.44347,-0.02534,0.18686],"tcp_to_object_dist_end":0.18042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61111,0.16909,0.01602],"object_pos_start":[0.60953,0.17018,0.00563],"object_to_goal_dist_end":0.10731,"object_to_goal_dist_start":0.11679,"object_z_max":0.01668,"peak_contact_force":0.12264,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":901.0,"raw_peak_contact_force":0.1263,"subtask_id":"reach_goal","tcp_end":[0.59743,0.19822,0.2039],"tcp_start":[0.60301,0.19982,0.18348],"tcp_to_object_dist_end":0.19062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":600.0,"object_pos_end":[0.61111,0.16909,0.01602],"object_pos_start":[0.61111,0.16909,0.01602],"object_to_goal_dist_end":0.10731,"object_to_goal_dist_start":0.10731,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_goal","tcp_end":[0.59499,0.19736,0.28893],"tcp_start":[0.59743,0.19822,0.2039],"tcp_to_object_dist_end":0.27484,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```