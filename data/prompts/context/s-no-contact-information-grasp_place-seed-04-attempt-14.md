## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2084 | 0.57 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 14 | -0.4413 | 0.37 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0579 | 0.34 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 13 | -0.3933 | 0.36 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0537 | 0.34 | ❌ rejected |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.208) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: grasp_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: place
  weight: 0.7
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_approach
- id: descend_grasp
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.08
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: grasp_approach
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_guard_threshold:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.015
      binds_to:
      - path: guards.lift_guard.threshold
        mode: replace
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_guard
    when: during_phase
    predicate: object_lifted
    threshold: 0.015
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
- id: approach_goal
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_speed:
      type: scalar
      range:
      - 0.15
      - 0.7
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace
    place_approach_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_guard_threshold:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: guards.transport_guard.threshold
        mode: replace
  guards:
  - id: transport_guard
    when: during_phase
    predicate: object_lifted
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: place
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_guard_threshold: status=consumed; consumers=guards.lift_guard.threshold (replace)
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_guard, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.015
  - retries: max_attempts=2, strategy=reduce_speed
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
    - place_approach_z: status=consumed; consumers=target.offset.z (replace)
    - transport_guard_threshold: status=consumed; consumers=guards.transport_guard.threshold (replace)
  - guards:
    - id=transport_guard, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=reduce_speed
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.208
- **task_score** (E): 0.572
- **fitness_score**: 0.512  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1493 |
| descend_grasp | 1.00 | 0.1140 |
| grasp_1 | 1.00 | 0.0135 |
| lift_1 | 0.00 | 0.0001 |
| approach_goal | 0.00 | 0.0001 |
| descend_place | 0.67 | 0.2170 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.154) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 |
| descend_grasp | descend | 1.00 / step_budget | (0.519, 0.005, 0.154)→(0.521, 0.005, 0.040) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.040)→(0.512, 0.005, 0.030) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| lift_1 | lift | 0.00 / guard_failure | (0.512, 0.005, 0.030)→(0.512, 0.005, 0.030) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| approach_goal | approach | 0.00 / guard_failure | (0.512, 0.005, 0.030)→(0.512, 0.005, 0.030) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| descend_place | descend | 0.67 / step_budget | (0.512, 0.005, 0.030)→(0.600, 0.157, 0.155) | (0.526, 0.005, 0.025)→(0.602, 0.159, 0.067) | 0.249→0.119 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.063
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 1.000
- phase_score: 0.611
- phase_breakdown.place_score: 0.803
- phase_breakdown.grasp_approach_score: 0.162
- grasp_place_fitness: 0.727

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.727
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.244
- **K-run variance**: 0.0265
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.265


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.16667,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08527,"approach_1.approach_speed":0.74294,"approach_goal.approach_goal_speed":0.56577,"approach_goal.place_approach_z":0.09735,"approach_goal.transport_guard_threshold":0.02107,"descend_grasp.descend_speed":0.23011,"descend_grasp.grasp_z_offset":0.00206,"descend_place.descend_place_speed":0.26051,"descend_place.place_z_offset":-0.01219,"lift_1.lift_guard_threshold":0.03927,"lift_1.lift_height":0.133,"lift_1.lift_speed":0.49466},"optimized_scores":{"best_composite_score":-0.24418,"best_fitness_score":0.47582,"best_task_score":0.50831},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":254.0,"contact_point_centroid":[0.55099,0.00984,-0.00151],"force_p95":0.50748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64026,"mean_force":0.31569,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53223,0.00805,0.03947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10826.0,"contact_point_centroid":[0.58022,0.04934,0.09153],"force_p95":0.149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3379,"mean_force":0.09168,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57607,0.0682,0.09077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11998.0,"contact_point_centroid":[0.58311,0.09019,0.09492],"force_p95":0.12678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33714,"mean_force":0.07569,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57872,0.07174,0.09386]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.54429,0.00079,-0.00218],"force_p95":0.25306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25325,"mean_force":0.22691,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52901,0.00084,0.03565]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.54431,0.00079,-0.00208],"force_p95":0.24992,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25112,"mean_force":0.2228,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52915,0.00084,0.03583]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13252,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15506,"mean_force":0.12545,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53042,0.00087,0.0373]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51658,0.00046,0.217]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.53031,0.01983,0.03761],"force_p95":0.10902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12516,"mean_force":0.07419,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52915,0.00084,0.03583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.53017,0.01983,0.03743],"force_p95":0.1103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12486,"mean_force":0.07961,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52901,0.00084,0.03565]},{"body_a":"world","body_b":"grasp_target","contact_count":640.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53581,0.00096,0.08998]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53045,-0.01836,0.03857],"force_p95":0.07626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12057,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52921,0.00085,0.03591]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.5304,-0.01831,0.0385],"force_p95":0.11497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11916,"mean_force":0.08012,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52915,0.00084,0.03583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.53026,-0.01831,0.03832],"force_p95":0.1156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11847,"mean_force":0.08492,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52901,0.00084,0.03565]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53035,0.01992,0.0377],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0952,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52921,0.00085,0.03591]}],"total_contact_groups":14},"final_pose_error":0.01529,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65336,0.16326,0.0899],"final_tcp_position":[0.64072,0.15316,0.16619],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.53517,0.00093,0.13257],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10694,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.53815,0.00101,0.04666],"tcp_start":[0.53517,0.00093,0.13257],"tcp_to_object_dist_end":0.02154,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00074,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52917,0.00084,0.03587],"tcp_start":[0.53815,0.00101,0.04666],"tcp_to_object_dist_end":0.01804,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.54418,0.00074,0.02584],"object_pos_start":[0.54419,0.00074,0.02587],"object_to_goal_dist_end":0.25054,"object_to_goal_dist_start":0.25052,"object_z_max":0.02587,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52907,0.00084,0.03573],"tcp_start":[0.52912,0.00084,0.03579],"tcp_to_object_dist_end":0.01806,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54408,0.00073,0.02565],"object_pos_start":[0.54412,0.00074,0.02572],"object_to_goal_dist_end":0.25071,"object_to_goal_dist_start":0.25064,"object_z_max":0.02572,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.52887,0.00084,0.03548],"tcp_start":[0.52894,0.00084,0.03557],"tcp_to_object_dist_end":0.01811,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.65336,0.16326,0.0899],"object_pos_start":[0.54396,0.00073,0.02549],"object_to_goal_dist_end":0.1015,"object_to_goal_dist_start":0.25086,"object_z_max":0.13157,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.64072,0.15316,0.16619],"tcp_start":[0.52887,0.00084,0.03548],"tcp_to_object_dist_end":0.07799,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30303,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11113,"approach_1.approach_speed":0.61758,"approach_goal.approach_goal_speed":0.43505,"approach_goal.place_approach_z":0.11677,"approach_goal.transport_guard_threshold":0.03204,"descend_grasp.descend_speed":0.21774,"descend_grasp.grasp_z_offset":-0.00605,"descend_place.descend_place_speed":0.22156,"descend_place.place_z_offset":0.01626,"lift_1.lift_guard_threshold":0.02799,"lift_1.lift_height":0.11962,"lift_1.lift_speed":0.26272},"optimized_scores":{"best_composite_score":0.00665,"best_fitness_score":0.72665,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":421.0,"contact_point_centroid":[0.53864,0.04372,-0.00206],"force_p95":0.62363,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93807,"mean_force":0.40109,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52065,0.04238,0.03358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9601.0,"contact_point_centroid":[0.55142,0.07297,0.06325],"force_p95":0.16147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41648,"mean_force":0.09831,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54813,0.09208,0.06329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9450.0,"contact_point_centroid":[0.55743,0.11965,0.06965],"force_p95":0.14056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32836,"mean_force":0.08046,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55331,0.10119,0.06889]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.53068,0.02985,-0.00236],"force_p95":0.28827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2884,"mean_force":0.25416,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51589,0.02908,0.02851]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.53072,0.02986,-0.00227],"force_p95":0.28368,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.287,"mean_force":0.2443,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51603,0.02909,0.02869]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03046,-0.00216],"force_p95":0.16826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24913,"mean_force":0.13468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51728,0.02917,0.03008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4052.0,"contact_point_centroid":[0.51712,0.00989,0.0315],"force_p95":0.08187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1535,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51608,0.0291,0.02876]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51051,0.01258,0.23023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.51695,0.04811,0.03047],"force_p95":0.11565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13494,"mean_force":0.07754,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51603,0.02909,0.02869]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.51681,0.04811,0.03029],"force_p95":0.12071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13454,"mean_force":0.08332,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51589,0.02908,0.02851]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52297,0.02781,0.09893]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.51694,0.00993,0.03123],"force_p95":0.1155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11855,"mean_force":0.0859,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51589,0.02908,0.02851]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.51707,0.00994,0.0314],"force_p95":0.11581,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1177,"mean_force":0.08178,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51603,0.02909,0.02869]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5029.0,"contact_point_centroid":[0.51701,0.04828,0.03054],"force_p95":0.07457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08637,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51609,0.0291,0.02877]}],"total_contact_groups":14},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60291,0.17271,0.09035],"final_tcp_position":[0.59417,0.17216,0.11303],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.5228,0.02607,0.15846],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13275,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.52498,0.02966,0.03903],"tcp_start":[0.5228,0.02607,0.15846],"tcp_to_object_dist_end":0.01418,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02917,0.02548],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18495,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51606,0.02909,0.02872],"tcp_start":[0.52498,0.02966,0.03903],"tcp_to_object_dist_end":0.01471,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.53039,0.02917,0.02545],"object_pos_start":[0.5304,0.02917,0.02548],"object_to_goal_dist_end":0.18496,"object_to_goal_dist_start":0.18495,"object_z_max":0.02548,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51596,0.02909,0.02859],"tcp_start":[0.516,0.02909,0.02865],"tcp_to_object_dist_end":0.01477,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53027,0.02917,0.02527],"object_pos_start":[0.53033,0.02917,0.02534],"object_to_goal_dist_end":0.18509,"object_to_goal_dist_start":0.18504,"object_z_max":0.02534,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.51575,0.02907,0.02835],"tcp_start":[0.51583,0.02908,0.02844],"tcp_to_object_dist_end":0.01484,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":792.0,"n_steps_budget":1000.0,"object_pos_end":[0.60291,0.17271,0.09035],"object_pos_start":[0.53014,0.02916,0.02512],"object_to_goal_dist_end":0.01873,"object_to_goal_dist_start":0.18522,"object_z_max":0.09031,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.59417,0.17216,0.11303],"tcp_start":[0.51575,0.02907,0.02835],"tcp_to_object_dist_end":0.02431,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.50667,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12265,"approach_1.approach_speed":0.56625,"approach_goal.approach_goal_speed":0.40869,"approach_goal.place_approach_z":0.12284,"approach_goal.transport_guard_threshold":0.03881,"descend_grasp.descend_speed":0.29586,"descend_grasp.grasp_z_offset":-0.00953,"descend_place.descend_place_speed":0.18602,"descend_place.place_z_offset":-0.0144,"lift_1.lift_guard_threshold":0.02502,"lift_1.lift_height":0.17887,"lift_1.lift_speed":0.3989},"optimized_scores":{"best_composite_score":-0.38761,"best_fitness_score":0.33239,"best_task_score":0.20672},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":442.0,"contact_point_centroid":[0.53539,0.08874,-0.00446],"force_p95":1.12083,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56539,"mean_force":0.35947,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53345,0.08097,0.12007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10516.0,"contact_point_centroid":[0.51856,0.06349,0.08345],"force_p95":0.13821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33738,"mean_force":0.07798,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51497,0.04486,0.08242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10156.0,"contact_point_centroid":[0.51603,0.02105,0.07856],"force_p95":0.14199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29564,"mean_force":0.08131,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5126,0.03983,0.07737]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50378,-0.01515,-0.00219],"force_p95":0.27959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28051,"mean_force":0.25708,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49038,-0.0151,0.02601]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50382,-0.01515,-0.00211],"force_p95":0.27855,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2795,"mean_force":0.24557,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49052,-0.0151,0.02618]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01548,-0.00205],"force_p95":0.13855,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18063,"mean_force":0.127,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49173,-0.01512,0.02743]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.50382,-0.01567,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49962,-0.0062,0.23752]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.49113,-0.0341,0.02801],"force_p95":0.11379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13109,"mean_force":0.07693,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49052,-0.0151,0.02618]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.49099,-0.0341,0.02785],"force_p95":0.11489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12982,"mean_force":0.08112,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49038,-0.0151,0.02601]},{"body_a":"world","body_b":"grasp_target","contact_count":972.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4988,-0.01405,0.10412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.4911,0.00405,0.02892],"force_p95":0.11722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1222,"mean_force":0.08326,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49052,-0.0151,0.02618]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.49097,0.00405,0.02876],"force_p95":0.11916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12196,"mean_force":0.08671,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49038,-0.0151,0.02601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.49114,0.00409,0.02899],"force_p95":0.07736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1174,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49058,-0.01511,0.02624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.49118,-0.0342,0.02808],"force_p95":0.06936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08615,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49058,-0.01511,0.02624]},{"body_a":"left_finger","body_b":"right_finger","contact_count":321.0,"contact_point_centroid":[0.56149,0.13998,0.18129],"force_p95":0.0139,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01121,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56117,0.13998,0.17892]}],"total_contact_groups":15},"final_pose_error":0.06874,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54943,0.14077,0.01936],"final_tcp_position":[0.56385,0.1454,0.18446],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.50018,-0.01295,0.17211],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14616,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.49922,-0.01519,0.03556],"tcp_start":[0.50018,-0.01295,0.17211],"tcp_to_object_dist_end":0.0106,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01499,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49055,-0.0151,0.02621],"tcp_start":[0.49922,-0.01519,0.03556],"tcp_to_object_dist_end":0.01314,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.50366,-0.01499,0.02579],"object_pos_start":[0.50368,-0.01499,0.02582],"object_to_goal_dist_end":0.312,"object_to_goal_dist_start":0.31198,"object_z_max":0.02582,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49044,-0.0151,0.02608],"tcp_start":[0.49049,-0.0151,0.02614],"tcp_to_object_dist_end":0.01322,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50354,-0.01499,0.02561],"object_pos_start":[0.50359,-0.01499,0.02568],"object_to_goal_dist_end":0.31216,"object_to_goal_dist_start":0.31209,"object_z_max":0.02568,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.49024,-0.0151,0.02586],"tcp_start":[0.49032,-0.0151,0.02594],"tcp_to_object_dist_end":0.0133,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54943,0.14077,0.01936],"object_pos_start":[0.5034,-0.01499,0.02547],"object_to_goal_dist_end":0.23646,"object_to_goal_dist_start":0.3123,"object_z_max":0.1292,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.56385,0.1454,0.18446],"tcp_start":[0.49024,-0.0151,0.02586],"tcp_to_object_dist_end":0.1658,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```