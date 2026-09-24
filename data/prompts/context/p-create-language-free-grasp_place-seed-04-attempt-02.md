## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 1 | 0.3623 | 0.24 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.3139 | 0.21 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.3139 | 0.21 | ✅ accepted |

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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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
| `object` | offset from object initial position (0.5443056105572368, 0.0011327552814361583, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | final destination targets |
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

## Current Skill (Q=0.362) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: lift_clearance
  anchor: object
  target_entity: object
  metric: goal_progress
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_pre_place
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: place_goal
  target_entity: object
  weight: 0.4
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
    - 0.08
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_pre_grasp
- id: descend_1
  type: descend
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
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
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
    orientation:
      mode: none
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.001
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
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
    - 0.15
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    lift_z:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: lift_clearance
- id: approach_2
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
      mode: keep_current
  subtask_id: reach_pre_place
- id: descend_2
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: place_goal
- id: release_1
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
    orientation:
      mode: none
- id: retract_1
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
    - 0.15
    tolerance: 0.005
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.001
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.362
- **task_score** (E): 0.242
- **fitness_score**: 0.592  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1678 |
| descend_1 | 1.00 | 1.00 | 0.1005 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.1099 |
| approach_2 | 0.00 | 1.00 | 0.0799 |
| descend_2 | 0.67 | 1.00 | 0.0825 |
| release_1 | 1.00 | 1.00 | 0.0221 |
| retract_1 | 1.00 | 1.00 | 0.1351 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.004, 0.135) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.004, 0.135)→(0.520, 0.005, 0.035) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.520, 0.005, 0.035)→(0.511, 0.005, 0.026) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.025) | 0.249→0.249 | 1.00 / 40.333 | 0.150 | 0.198 |
| lift_1 | lift | 1.00 / step_budget | (0.511, 0.005, 0.026)→(0.521, 0.005, 0.135) | (0.526, 0.005, 0.025)→(0.539, 0.005, 0.122) | 0.249→0.201 | 1.00 / 20.667 | 524.442 | 0.667 |
| approach_2 | approach | 0.00 / step_budget | (0.521, 0.005, 0.135)→(0.551, 0.067, 0.173) | (0.539, 0.005, 0.122)→(0.537, 0.045, 0.016) | 0.201→0.225 | 1.00 / 8.000 | 3249.723 | 1.346 |
| descend_2 | descend | 0.67 / step_budget | (0.551, 0.067, 0.173)→(0.587, 0.135, 0.165) | (0.537, 0.045, 0.016)→(0.537, 0.045, 0.016) | 0.225→0.225 | 1.00 / 9.000 | 273006.076 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.587, 0.135, 0.165)→(0.581, 0.134, 0.186) | (0.537, 0.045, 0.016)→(0.537, 0.045, 0.016) | 0.225→0.225 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.581, 0.134, 0.186)→(0.607, 0.170, 0.312) | (0.537, 0.045, 0.016)→(0.537, 0.045, 0.016) | 0.225→0.225 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.377
- phase_score: 0.454
- phase_breakdown.reach_pre_grasp_score: 0.560
- phase_breakdown.lift_clearance_score: 0.136
- phase_breakdown.place_goal_score: 0.718
- phase_breakdown.reach_pre_place_score: 0.139
- grasp_place_fitness: 0.665

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.665
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.377
- **Median Q (composite search score)**: 0.336
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 12.0
- **Final σ (mean)**: 0.376


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87755,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_z":0.13518},"optimized_scores":{"best_composite_score":0.33644,"best_fitness_score":0.56644,"best_task_score":0.20663},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3661.0,"contact_point_centroid":[0.55836,0.02642,-0.00221],"force_p95":0.12692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37774,"mean_force":0.13355,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55781,0.033,0.16669]},{"body_a":"world","body_b":"grasp_target","contact_count":350.0,"contact_point_centroid":[0.54274,0.00067,-0.00158],"force_p95":0.18428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37329,"mean_force":0.09128,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52498,0.00077,0.04288]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8342.0,"contact_point_centroid":[0.53494,-0.01784,0.08718],"force_p95":0.1297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34571,"mean_force":0.08526,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53002,0.00073,0.08558]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8480.0,"contact_point_centroid":[0.53504,0.01928,0.08705],"force_p95":0.11875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32901,"mean_force":0.08439,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53003,0.00073,0.08566]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":61.0,"contact_point_centroid":[0.54619,-0.01665,0.14168],"force_p95":0.21445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23267,"mean_force":0.1753,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53957,0.00113,0.14801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.54561,0.01783,0.14291],"force_p95":0.15469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17182,"mean_force":0.07699,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53959,0.00166,0.14789]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54428,0.00104,-0.00205],"force_p95":0.1371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15539,"mean_force":0.12678,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52839,0.00084,0.04371]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.54431,0.00113,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5152,0.00044,0.21539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3983.0,"contact_point_centroid":[0.5294,-0.01809,0.04542],"force_p95":0.09713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12395,"mean_force":0.0546,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52717,0.00082,0.04227]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53079,0.00086,0.09454]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5584,0.02644,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59757,0.09329,0.18076]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5584,0.02644,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61736,0.12548,0.18168]},{"body_a":"world","body_b":"grasp_target","contact_count":3488.0,"contact_point_centroid":[0.5584,0.02644,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62828,0.13995,0.25887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4138.0,"contact_point_centroid":[0.52982,0.01966,0.04477],"force_p95":0.0903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09489,"mean_force":0.05329,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52717,0.00082,0.04228]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3565.0,"contact_point_centroid":[0.55949,0.03502,0.17051],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.0106,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55919,0.03502,0.1682]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4263.0,"contact_point_centroid":[0.59798,0.0933,0.18304],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59757,0.09329,0.18076]}],"total_contact_groups":17},"final_pose_error":0.01602,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.5584,0.02644,0.01602],"final_tcp_position":[0.64453,0.15602,0.32553],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273006.34168,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52806,0.00077,0.15679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53533,0.00096,0.05194],"tcp_start":[0.52806,0.00077,0.15679],"tcp_to_object_dist_end":0.02743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54446,0.00077,0.02572],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13902,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9921.0,"raw_peak_contact_force":0.15539,"tcp_end":[0.52714,0.00082,0.04224],"tcp_start":[0.53533,0.00096,0.05194],"tcp_to_object_dist_end":0.02394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":721.0,"n_steps_budget":750.0,"object_pos_end":[0.54862,0.00037,0.12062],"object_pos_start":[0.54446,0.00077,0.02572],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.25048,"object_z_max":0.12053,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17172.0,"raw_peak_contact_force":0.37329,"subtask_id":"lift_clearance","tcp_end":[0.53941,0.00071,0.14794],"tcp_start":[0.52714,0.00082,0.04224],"tcp_to_object_dist_end":0.02883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5584,0.02644,0.01602],"object_pos_start":[0.54862,0.00037,0.12062],"object_to_goal_dist_end":0.23653,"object_to_goal_dist_start":0.19911,"object_z_max":0.12063,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7445.0,"raw_peak_contact_force":1.37774,"subtask_id":"reach_pre_place","tcp_end":[0.57603,0.05911,0.18672],"tcp_start":[0.53941,0.00071,0.14794],"tcp_to_object_dist_end":0.17469,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5584,0.02644,0.01602],"object_pos_start":[0.5584,0.02644,0.01602],"object_to_goal_dist_end":0.23653,"object_to_goal_dist_start":0.23653,"object_z_max":0.01602,"peak_contact_force":273006.34168,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8263.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62144,0.12633,0.18114],"tcp_start":[0.57603,0.05911,0.18672],"tcp_to_object_dist_end":0.20302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5584,0.02644,0.01602],"object_pos_start":[0.5584,0.02644,0.01602],"object_to_goal_dist_end":0.23653,"object_to_goal_dist_start":0.23653,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61579,0.12507,0.20115],"tcp_start":[0.62144,0.12633,0.18114],"tcp_to_object_dist_end":0.21748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.5584,0.02644,0.01602],"object_pos_start":[0.5584,0.02644,0.01602],"object_to_goal_dist_end":0.23653,"object_to_goal_dist_start":0.23653,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3488.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64453,0.15602,0.32553],"tcp_start":[0.61579,0.12507,0.20115],"tcp_to_object_dist_end":0.34641,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87919,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_z":0.11254},"optimized_scores":{"best_composite_score":0.43483,"best_fitness_score":0.66483,"best_task_score":0.37735},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2467.0,"contact_point_centroid":[0.54161,0.08211,-0.00227],"force_p95":0.13836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25427,"mean_force":0.13846,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5465,0.07832,0.13983]},{"body_a":"world","body_b":"grasp_target","contact_count":342.0,"contact_point_centroid":[0.52732,0.02904,-0.00164],"force_p95":0.36138,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73714,"mean_force":0.12445,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51404,0.02924,0.021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11503.0,"contact_point_centroid":[0.5202,0.04795,0.06307],"force_p95":0.10627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30085,"mean_force":0.06621,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51747,0.02909,0.06156]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11052.0,"contact_point_centroid":[0.5203,0.01021,0.06587],"force_p95":0.10948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2867,"mean_force":0.06769,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51777,0.02909,0.06427]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.0304,-0.00212],"force_p95":0.15988,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25215,"mean_force":0.13286,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51756,0.02952,0.02166]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3442.0,"contact_point_centroid":[0.53126,0.0598,0.1226],"force_p95":0.16112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24283,"mean_force":0.10418,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52837,0.04174,0.12589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3142.0,"contact_point_centroid":[0.53097,0.02218,0.12235],"force_p95":0.17112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24116,"mean_force":0.10308,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52783,0.04042,0.12554]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5305,0.03079,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51066,0.01403,0.20762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4041.0,"contact_point_centroid":[0.51727,0.01024,0.02303],"force_p95":0.08062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13595,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51632,0.02943,0.02028]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52164,0.02792,0.07295]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54149,0.0822,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57272,0.1334,0.1237]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54149,0.0822,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5858,0.16483,0.10696]},{"body_a":"world","body_b":"grasp_target","contact_count":3128.0,"contact_point_centroid":[0.54149,0.0822,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58869,0.16987,0.18085]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4997.0,"contact_point_centroid":[0.51718,0.0486,0.02208],"force_p95":0.0728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09225,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51633,0.02943,0.02029]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2297.0,"contact_point_centroid":[0.54826,0.08089,0.14306],"force_p95":0.01127,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01692,"mean_force":0.01063,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.54782,0.08088,0.14087]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.58951,0.16588,0.10508],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.00996,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58905,0.16585,0.10291]}],"total_contact_groups":17},"final_pose_error":0.01543,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.54149,0.0822,0.01602],"final_tcp_position":[0.59773,0.17687,0.24323],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273006.70932,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52109,0.02528,0.1369],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52468,0.02999,0.02959],"tcp_start":[0.52109,0.02528,0.1369],"tcp_to_object_dist_end":0.00688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53034,0.02932,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.151,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10838.0,"raw_peak_contact_force":0.25215,"tcp_end":[0.51629,0.02943,0.02025],"tcp_start":[0.52468,0.02999,0.02959],"tcp_to_object_dist_end":0.01504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":721.0,"n_steps_budget":750.0,"object_pos_end":[0.54593,0.02916,0.11769],"object_pos_start":[0.53034,0.02932,0.0256],"object_to_goal_dist_end":0.15971,"object_to_goal_dist_start":0.1848,"object_z_max":0.11759,"peak_contact_force":0.11312,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22897.0,"raw_peak_contact_force":0.73714,"subtask_id":"lift_clearance","tcp_end":[0.52534,0.02905,0.12556],"tcp_start":[0.51629,0.02943,0.02025],"tcp_to_object_dist_end":0.02205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54149,0.0822,0.01602],"object_pos_start":[0.54593,0.02916,0.11769],"object_to_goal_dist_end":0.14619,"object_to_goal_dist_start":0.15971,"object_z_max":0.11772,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11348.0,"raw_peak_contact_force":1.25427,"subtask_id":"reach_pre_place","tcp_end":[0.55755,0.09973,0.14852],"tcp_start":[0.52534,0.02905,0.12556],"tcp_to_object_dist_end":0.13461,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54149,0.0822,0.01602],"object_pos_start":[0.54149,0.0822,0.01602],"object_to_goal_dist_end":0.14619,"object_to_goal_dist_start":0.14619,"object_z_max":0.01602,"peak_contact_force":273006.70932,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8256.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.59074,0.1662,0.10576],"tcp_start":[0.55755,0.09973,0.14852],"tcp_to_object_dist_end":0.13242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54149,0.0822,0.01602],"object_pos_start":[0.54149,0.0822,0.01602],"object_to_goal_dist_end":0.14619,"object_to_goal_dist_start":0.14619,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58385,0.16421,0.12678],"tcp_start":[0.59074,0.1662,0.10576],"tcp_to_object_dist_end":0.14418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.54149,0.0822,0.01602],"object_pos_start":[0.54149,0.0822,0.01602],"object_to_goal_dist_end":0.14619,"object_to_goal_dist_start":0.14619,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59773,0.17687,0.24323],"tcp_start":[0.58385,0.16421,0.12678],"tcp_to_object_dist_end":0.25249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8882,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_z":0.11924},"optimized_scores":{"best_composite_score":0.31553,"best_fitness_score":0.54553,"best_task_score":0.14151},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2528.0,"contact_point_centroid":[0.50996,0.02536,-0.00233],"force_p95":0.13019,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40517,"mean_force":0.14018,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51189,0.02471,0.16525]},{"body_a":"world","body_b":"grasp_target","contact_count":353.0,"contact_point_centroid":[0.50035,-0.0153,-0.00175],"force_p95":0.41516,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88955,"mean_force":0.13977,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48838,-0.01544,0.01616]},{"body_a":"grasp_target","body_b":"hand","contact_count":484.0,"contact_point_centroid":[0.50361,-0.0127,0.08375],"force_p95":0.11877,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37934,"mean_force":0.06515,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48972,-0.01537,0.04526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12134.0,"contact_point_centroid":[0.49382,0.00363,0.06669],"force_p95":0.10618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27713,"mean_force":0.06659,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49157,-0.01534,0.06474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3155.0,"contact_point_centroid":[0.50162,-0.02454,0.13391],"force_p95":0.18287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25216,"mean_force":0.10214,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49892,-0.00624,0.13663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13383.0,"contact_point_centroid":[0.49322,-0.03419,0.06301],"force_p95":0.10789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24878,"mean_force":0.06116,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49131,-0.01535,0.06169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3297.0,"contact_point_centroid":[0.50216,0.01285,0.13469],"force_p95":0.16117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2476,"mean_force":0.10475,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49919,-0.00528,0.13735]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50364,-0.01548,-0.00228],"force_p95":0.16148,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18723,"mean_force":0.14209,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49188,-0.0155,0.01623]},{"body_a":"world","body_b":"grasp_target","contact_count":3584.0,"contact_point_centroid":[0.50382,-0.01567,-0.00196],"force_p95":0.12593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49856,-0.00759,0.20286]},{"body_a":"world","body_b":"grasp_target","contact_count":2656.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49767,-0.01532,0.05844]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50994,0.02547,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53326,0.07844,0.19281]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50994,0.02547,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54566,0.11232,0.21027]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50994,0.02547,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.56032,0.14369,0.29548]},{"body_a":"grasp_target","body_b":"hand","contact_count":377.0,"contact_point_centroid":[0.50847,-0.01746,0.05424],"force_p95":0.08627,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11867,"mean_force":0.07812,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49103,-0.01549,0.01536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.49101,0.00379,0.01744],"force_p95":0.07709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09093,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49068,-0.01549,0.015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5376.0,"contact_point_centroid":[0.49036,-0.03455,0.01735],"force_p95":0.0637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08406,"mean_force":0.04102,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49068,-0.01549,0.015]}],"total_contact_groups":19},"final_pose_error":0.03274,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50994,0.02547,0.01602],"final_tcp_position":[0.57987,0.17683,0.36796],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273005.17673,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49945,-0.01498,0.11224],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2656.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49872,-0.01559,0.02332],"tcp_start":[0.49945,-0.01498,0.11224],"tcp_to_object_dist_end":0.00577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50294,-0.01529,0.02514],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31285,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15944,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11672.0,"raw_peak_contact_force":0.18723,"tcp_end":[0.49065,-0.01548,0.01496],"tcp_start":[0.49872,-0.01559,0.02332],"tcp_to_object_dist_end":0.01595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":781.0,"n_steps_budget":810.0,"object_pos_end":[0.52119,-0.01539,0.12794],"object_pos_start":[0.50294,-0.01529,0.02514],"object_to_goal_dist_end":0.24475,"object_to_goal_dist_start":0.31285,"object_z_max":0.12785,"peak_contact_force":0.11963,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26354.0,"raw_peak_contact_force":0.88955,"subtask_id":"lift_clearance","tcp_end":[0.49826,-0.01523,0.13227],"tcp_start":[0.49065,-0.01548,0.01496],"tcp_to_object_dist_end":0.02333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50994,0.02547,0.01602],"object_pos_start":[0.52119,-0.01539,0.12794],"object_to_goal_dist_end":0.29331,"object_to_goal_dist_start":0.24475,"object_z_max":0.12797,"peak_contact_force":9748.92409,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11374.0,"raw_peak_contact_force":1.40517,"subtask_id":"reach_pre_place","tcp_end":[0.51989,0.04255,0.18239],"tcp_start":[0.49826,-0.01523,0.13227],"tcp_to_object_dist_end":0.16754,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50994,0.02547,0.01602],"object_pos_start":[0.50994,0.02547,0.01602],"object_to_goal_dist_end":0.29331,"object_to_goal_dist_start":0.29331,"object_z_max":0.01602,"peak_contact_force":273005.17673,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8266.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.54927,0.11302,0.2078],"tcp_start":[0.51989,0.04255,0.18239],"tcp_to_object_dist_end":0.21446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50994,0.02547,0.01602],"object_pos_start":[0.50994,0.02547,0.01602],"object_to_goal_dist_end":0.29331,"object_to_goal_dist_start":0.29331,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54429,0.11199,0.23061],"tcp_start":[0.54927,0.11302,0.2078],"tcp_to_object_dist_end":0.23391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50994,0.02547,0.01602],"object_pos_start":[0.50994,0.02547,0.01602],"object_to_goal_dist_end":0.29331,"object_to_goal_dist_start":0.29331,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57987,0.17683,0.36796],"tcp_start":[0.54429,0.11199,0.23061],"tcp_to_object_dist_end":0.38944,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```