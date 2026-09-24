## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 14 | -0.4413 | 0.37 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0579 | 0.34 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 13 | -0.3933 | 0.36 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0537 | 0.34 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 13 | -0.3922 | 0.36 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.441) — your mutation base

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

- **Composite score**: -0.441
- **task_score** (E): 0.367
- **fitness_score**: 0.409  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.850

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1468 |
| descend_grasp | 1.00 | 0.1174 |
| grasp_1 | 1.00 | 0.0135 |
| lift_1 | 0.00 | 0.0001 |
| approach_place | 0.00 | 0.0001 |
| descend_place | 0.67 | 0.2087 |
| release_1 | 1.00 | 0.0219 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.157) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 |
| descend_grasp | descend | 1.00 / step_budget | (0.519, 0.005, 0.157)→(0.521, 0.005, 0.039) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.039)→(0.512, 0.005, 0.029) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| lift_1 | lift | 0.00 / guard_failure | (0.512, 0.005, 0.029)→(0.512, 0.005, 0.029) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| approach_place | approach | 0.00 / guard_failure | (0.512, 0.005, 0.029)→(0.512, 0.005, 0.029) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| descend_place | descend | 0.67 / step_budget | (0.512, 0.005, 0.029)→(0.597, 0.153, 0.145) | (0.526, 0.005, 0.025)→(0.598, 0.164, 0.038) | 0.249→0.146 |
| release_1 | release | 1.00 / step_budget | (0.597, 0.153, 0.145)→(0.591, 0.151, 0.166) | (0.598, 0.164, 0.038)→(0.595, 0.165, 0.020) | 0.146→0.164 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.584
- phase_score: 0.306
- phase_breakdown.place_goal_score: 0.816
- phase_breakdown.grasp_approach_score: 0.193
- phase_breakdown.transport_score: 0.008
- grasp_place_fitness: 0.512

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.512
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.584
- **Median Q (composite search score)**: -0.468
- **K-run variance**: 0.0058
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.320


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44776,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11468,"approach_1.approach_speed":0.28409,"approach_place.approach_goal_speed":0.69752,"approach_place.place_approach_z":0.15147,"approach_place.transport_arc_height":0.14685,"approach_place.transport_guard_threshold":0.04868,"descend_grasp.descend_speed":0.32106,"descend_grasp.grasp_z_offset":-0.00684,"descend_place.descend_place_speed":0.25312,"descend_place.place_z_offset":-0.0187,"lift_1.lift_guard_threshold":0.00727,"lift_1.lift_height":0.16734,"lift_1.lift_speed":0.39922,"release_1.release_duration":0.24856},"optimized_scores":{"best_composite_score":-0.46834,"best_fitness_score":0.38166,"best_task_score":0.31083},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.60217,0.09488,-0.00303],"force_p95":0.69852,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37436,"mean_force":0.28994,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59024,0.08573,0.09966]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9740.0,"contact_point_centroid":[0.57291,0.04042,0.07488],"force_p95":0.15903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39136,"mean_force":0.09312,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56922,0.05928,0.07484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10610.0,"contact_point_centroid":[0.57703,0.08276,0.07977],"force_p95":0.13582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37465,"mean_force":0.07879,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57304,0.06438,0.07939]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.54425,0.00075,-0.00217],"force_p95":0.27887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27898,"mean_force":0.253,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.52906,0.00084,0.02674]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.54429,0.00075,-0.00208],"force_p95":0.27302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2757,"mean_force":0.23836,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5292,0.00084,0.02692]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.13217,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16007,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53048,0.00086,0.02838]},{"body_a":"world","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5162,0.00044,0.23175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.5302,0.01983,0.02851],"force_p95":0.11541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1326,"mean_force":0.08236,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.52906,0.00084,0.02674]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.53034,0.01983,0.0287],"force_p95":0.11352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13245,"mean_force":0.07612,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5292,0.00084,0.02692]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63974,0.16033,-0.00198],"force_p95":0.12714,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12958,"mean_force":0.12287,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63474,0.15006,0.15781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.53043,-0.01831,0.02959],"force_p95":0.11745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12475,"mean_force":0.08235,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5292,0.00084,0.02692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.5303,-0.01831,0.0294],"force_p95":0.12279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12439,"mean_force":0.08798,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.52906,0.00084,0.02674]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53547,0.00095,0.09988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53049,-0.01836,0.02966],"force_p95":0.07611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11336,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52926,0.00084,0.02699]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53039,0.01992,0.02878],"force_p95":0.06817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09663,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52926,0.00084,0.02699]},{"body_a":"left_finger","body_b":"right_finger","contact_count":71.0,"contact_point_centroid":[0.63827,0.14985,0.15922],"force_p95":0.01568,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01588,"mean_force":0.0131,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63832,0.14984,0.15674]}],"total_contact_groups":17},"final_pose_error":0.01835,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63975,0.16034,0.01602],"final_tcp_position":[0.63914,0.151,0.15776],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.53451,0.00092,0.16162],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13596,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.53836,0.00101,0.03776],"tcp_start":[0.53451,0.00092,0.16162],"tcp_to_object_dist_end":0.01316,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25054,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52923,0.00084,0.02695],"tcp_start":[0.53836,0.00101,0.03776],"tcp_to_object_dist_end":0.01497,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.54415,0.00072,0.02585],"object_pos_start":[0.54416,0.00072,0.02588],"object_to_goal_dist_end":0.25056,"object_to_goal_dist_start":0.25054,"object_z_max":0.02588,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52912,0.00084,0.02682],"tcp_start":[0.52917,0.00084,0.02688],"tcp_to_object_dist_end":0.01506,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54403,0.00071,0.02566],"object_pos_start":[0.54408,0.00071,0.02573],"object_to_goal_dist_end":0.25074,"object_to_goal_dist_start":0.25067,"object_z_max":0.02573,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport","tcp_end":[0.52892,0.00084,0.02656],"tcp_start":[0.52899,0.00084,0.02666],"tcp_to_object_dist_end":0.01514,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63979,0.16048,0.01646],"object_pos_start":[0.54389,0.00071,0.0255],"object_to_goal_dist_end":0.17484,"object_to_goal_dist_start":0.2509,"object_z_max":0.11453,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.63914,0.151,0.15776],"tcp_start":[0.52892,0.00084,0.02656],"tcp_to_object_dist_end":0.14162,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63975,0.16034,0.01602],"object_pos_start":[0.63979,0.16048,0.01646],"object_to_goal_dist_end":0.17528,"object_to_goal_dist_start":0.17484,"object_z_max":0.01646,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.63302,0.14955,0.177],"tcp_start":[0.63914,0.151,0.15776],"tcp_to_object_dist_end":0.16148,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19118,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07567,"approach_1.approach_speed":0.54847,"approach_place.approach_goal_speed":0.43735,"approach_place.place_approach_z":0.1165,"approach_place.transport_arc_height":0.13008,"approach_place.transport_guard_threshold":0.02917,"descend_grasp.descend_speed":0.2058,"descend_grasp.grasp_z_offset":0.00298,"descend_place.descend_place_speed":0.19034,"descend_place.place_z_offset":0.01217,"lift_1.lift_guard_threshold":0.03722,"lift_1.lift_height":0.18121,"lift_1.lift_speed":0.3774,"release_1.release_duration":0.78866},"optimized_scores":{"best_composite_score":-0.33777,"best_fitness_score":0.51223,"best_task_score":0.58378},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":183.0,"contact_point_centroid":[0.59069,0.1819,-0.006],"force_p95":0.91128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.03609,"mean_force":0.37114,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58738,0.16998,0.11705]},{"body_a":"world","body_b":"grasp_target","contact_count":514.0,"contact_point_centroid":[0.53892,0.04519,-0.00228],"force_p95":0.62736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84187,"mean_force":0.38237,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52224,0.04561,0.04277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9553.0,"contact_point_centroid":[0.55319,0.07548,0.06867],"force_p95":0.17128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38803,"mean_force":0.10118,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54959,0.09464,0.06805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9322.0,"contact_point_centroid":[0.56086,0.12418,0.07568],"force_p95":0.14805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3849,"mean_force":0.08097,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55592,0.10566,0.07393]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.53071,0.02999,-0.00237],"force_p95":0.27049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27058,"mean_force":0.23217,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.51576,0.02894,0.0374]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.53073,0.03,-0.00228],"force_p95":0.26955,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27032,"mean_force":0.2312,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5159,0.02895,0.03758]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03054,-0.00216],"force_p95":0.16851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23871,"mean_force":0.13457,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51714,0.02903,0.03898]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":761.0,"contact_point_centroid":[0.59824,0.15289,0.10695],"force_p95":0.09959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22802,"mean_force":0.0642,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59209,0.17154,0.10604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.59705,0.19041,0.10566],"force_p95":0.10231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22153,"mean_force":0.06609,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59193,0.17148,0.10581]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4019.0,"contact_point_centroid":[0.5171,0.00974,0.04036],"force_p95":0.08259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15711,"mean_force":0.05252,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51595,0.02895,0.03765]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51072,0.01302,0.21262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.51686,0.04797,0.03936],"force_p95":0.1099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12872,"mean_force":0.0753,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5159,0.02895,0.03758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.51672,0.04797,0.03918],"force_p95":0.1143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12797,"mean_force":0.07995,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.51576,0.02894,0.0374]},{"body_a":"world","body_b":"grasp_target","contact_count":576.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52322,0.02809,0.08626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.51697,0.0098,0.04029],"force_p95":0.11009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11563,"mean_force":0.07932,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5159,0.02895,0.03758]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.51683,0.00979,0.04011],"force_p95":0.11068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1143,"mean_force":0.08267,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.51576,0.02894,0.0374]}],"total_contact_groups":17},"final_pose_error":0.01494,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59341,0.17396,0.0279],"final_tcp_position":[0.59398,0.17185,0.10927],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.5232,0.02678,0.1236],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09793,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.5247,0.0295,0.04792],"tcp_start":[0.5232,0.02678,0.1236],"tcp_to_object_dist_end":0.02269,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02925,0.02546],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51592,0.02895,0.03761],"tcp_start":[0.5247,0.0295,0.04792],"tcp_to_object_dist_end":0.01894,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.53044,0.02925,0.02543],"object_pos_start":[0.53045,0.02925,0.02546],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18487,"object_z_max":0.02546,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51582,0.02894,0.03748],"tcp_start":[0.51587,0.02894,0.03754],"tcp_to_object_dist_end":0.01895,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53034,0.02925,0.02525],"object_pos_start":[0.53039,0.02925,0.02532],"object_to_goal_dist_end":0.18501,"object_to_goal_dist_start":0.18496,"object_z_max":0.02532,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport","tcp_end":[0.51562,0.02893,0.03724],"tcp_start":[0.5157,0.02893,0.03732],"tcp_to_object_dist_end":0.01899,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.60068,0.17164,0.08257],"object_pos_start":[0.53023,0.02924,0.02509],"object_to_goal_dist_end":0.02646,"object_to_goal_dist_start":0.18513,"object_z_max":0.08252,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.59398,0.17185,0.10927],"tcp_start":[0.51562,0.02893,0.03724],"tcp_to_object_dist_end":0.02753,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59341,0.17396,0.0279],"object_pos_start":[0.60068,0.17164,0.08257],"object_to_goal_dist_end":0.08074,"object_to_goal_dist_start":0.02646,"object_z_max":0.08257,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.58721,0.16993,0.13025],"tcp_start":[0.59398,0.17185,0.10927],"tcp_to_object_dist_end":0.10262,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21519,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13614,"approach_1.approach_speed":0.64761,"approach_place.approach_goal_speed":0.42991,"approach_place.place_approach_z":0.14071,"approach_place.transport_arc_height":0.20872,"approach_place.transport_guard_threshold":0.0424,"descend_grasp.descend_speed":0.32247,"descend_grasp.grasp_z_offset":-0.01247,"descend_place.descend_place_speed":0.15127,"descend_place.place_z_offset":-0.01961,"lift_1.lift_guard_threshold":0.02463,"lift_1.lift_height":0.17716,"lift_1.lift_speed":0.21743,"release_1.release_duration":0.90757},"optimized_scores":{"best_composite_score":-0.51768,"best_fitness_score":0.33232,"best_task_score":0.20728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":406.0,"contact_point_centroid":[0.5331,0.08821,-0.0038],"force_p95":0.93376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45139,"mean_force":0.32798,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52833,0.07042,0.10564]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11526.0,"contact_point_centroid":[0.51902,0.06515,0.08122],"force_p95":0.14431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32456,"mean_force":0.0794,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51565,0.0465,0.08052]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50376,-0.01513,-0.00219],"force_p95":0.29203,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29313,"mean_force":0.26982,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.49036,-0.01511,0.0232]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50382,-0.01513,-0.00211],"force_p95":0.29009,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29171,"mean_force":0.25454,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49049,-0.01511,0.02336]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11405.0,"contact_point_centroid":[0.51678,0.02342,0.07702],"force_p95":0.14164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28547,"mean_force":0.08004,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51359,0.04215,0.07621]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01546,-0.00205],"force_p95":0.13815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18285,"mean_force":0.12695,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49171,-0.01513,0.02462]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.50382,-0.01567,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49969,-0.00606,0.24415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.49111,-0.0341,0.0252],"force_p95":0.11409,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13199,"mean_force":0.07685,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49049,-0.01511,0.02336]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.49097,-0.0341,0.02503],"force_p95":0.11607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13089,"mean_force":0.0812,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.49036,-0.01511,0.0232]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55234,0.16183,-0.00194],"force_p95":0.12853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13049,"mean_force":0.12102,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5545,0.13408,0.17145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.49095,0.00404,0.02594],"force_p95":0.12044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12351,"mean_force":0.08695,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.49036,-0.01511,0.0232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.49109,0.00404,0.0261],"force_p95":0.1181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12327,"mean_force":0.08334,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49049,-0.01511,0.02336]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49882,-0.01393,0.10918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.49113,0.00409,0.02618],"force_p95":0.07729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1184,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49055,-0.01511,0.02343]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.49117,-0.03421,0.02526],"force_p95":0.06922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08803,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49055,-0.01511,0.02343]},{"body_a":"left_finger","body_b":"right_finger","contact_count":9.0,"contact_point_centroid":[0.55964,0.13461,0.17168],"force_p95":0.01597,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01597,"mean_force":0.01516,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55834,0.13461,0.16878]}],"total_contact_groups":17},"final_pose_error":0.08437,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55234,0.16184,0.01602],"final_tcp_position":[0.55845,0.13484,0.16901],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.50023,-0.01273,0.1853],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15934,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.49924,-0.0152,0.03275],"tcp_start":[0.50023,-0.01273,0.1853],"tcp_to_object_dist_end":0.00815,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01499,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31197,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49052,-0.01511,0.0234],"tcp_start":[0.49924,-0.0152,0.03275],"tcp_to_object_dist_end":0.01337,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.50365,-0.01499,0.02579],"object_pos_start":[0.50367,-0.01499,0.02582],"object_to_goal_dist_end":0.31199,"object_to_goal_dist_start":0.31197,"object_z_max":0.02582,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49042,-0.01511,0.02327],"tcp_start":[0.49047,-0.01511,0.02333],"tcp_to_object_dist_end":0.01347,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50352,-0.01499,0.02562],"object_pos_start":[0.50358,-0.01499,0.02569],"object_to_goal_dist_end":0.31215,"object_to_goal_dist_start":0.31209,"object_z_max":0.02569,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport","tcp_end":[0.49022,-0.01511,0.02305],"tcp_start":[0.49029,-0.01511,0.02313],"tcp_to_object_dist_end":0.01355,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5522,0.16087,0.01598],"object_pos_start":[0.50338,-0.01499,0.02547],"object_to_goal_dist_end":0.23622,"object_to_goal_dist_start":0.31229,"object_z_max":0.1255,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55845,0.13484,0.16901],"tcp_start":[0.49022,-0.01511,0.02305],"tcp_to_object_dist_end":0.15536,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55234,0.16184,0.01602],"object_pos_start":[0.5522,0.16087,0.01598],"object_to_goal_dist_end":0.23605,"object_to_goal_dist_start":0.23622,"object_z_max":0.01662,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.55291,0.13364,0.19168],"tcp_start":[0.55845,0.13484,0.16901],"tcp_to_object_dist_end":0.17791,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```