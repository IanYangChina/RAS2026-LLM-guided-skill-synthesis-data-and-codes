## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0579 | 0.34 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 13 | -0.3933 | 0.36 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0537 | 0.34 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 13 | -0.3922 | 0.36 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0947 | 0.48 | ❌ rejected |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.058) — your mutation base

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

- **Composite score**: -0.058
- **task_score** (E): 0.336
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1417 |
| descend_grasp | 1.00 | 0.1187 |
| grasp_1 | 1.00 | 0.0135 |
| lift_1 | 1.00 | 0.0953 |
| approach_place | 1.00 | 0.2462 |
| descend_place | 1.00 | 0.0886 |
| release_1 | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.004, 0.162) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 |
| descend_grasp | descend | 1.00 / step_budget | (0.519, 0.004, 0.162)→(0.521, 0.005, 0.044) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.044)→(0.512, 0.005, 0.033) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.033)→(0.508, 0.005, 0.129) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.115) | 0.249→0.209 |
| approach_place | approach | 1.00 / step_budget | (0.508, 0.005, 0.129)→(0.605, 0.166, 0.281) | (0.526, 0.005, 0.115)→(0.571, 0.109, 0.066) | 0.209→0.175 |
| descend_place | descend | 1.00 / step_budget | (0.605, 0.166, 0.281)→(0.607, 0.172, 0.192) | (0.571, 0.109, 0.066)→(0.570, 0.112, 0.042) | 0.175→0.160 |
| release_1 | release | 1.00 / step_budget | (0.607, 0.172, 0.192)→(0.602, 0.170, 0.212) | (0.570, 0.112, 0.042)→(0.566, 0.116, 0.020) | 0.160→0.182 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.574
- phase_score: 0.544
- phase_breakdown.place_score: 0.692
- phase_breakdown.grasp_approach_score: 0.197
- grasp_place_fitness: 0.757

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.757
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.574
- **Median Q (composite search score)**: -0.097
- **K-run variance**: 0.0068
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.241


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09573,"approach_1.approach_speed":0.46392,"approach_place.approach_goal_speed":0.44022,"approach_place.place_approach_z":0.12356,"descend_grasp.descend_speed":0.283,"descend_grasp.grasp_z_offset":-0.00244,"descend_place.descend_place_speed":0.12781,"descend_place.place_z_offset":-0.00623,"lift_1.lift_height":0.10994,"lift_1.lift_speed":0.21539,"release_1.release_duration":0.66739},"optimized_scores":{"best_composite_score":-0.0973,"best_fitness_score":0.6027,"best_task_score":0.25594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.59133,0.0689,-0.00254],"force_p95":0.26149,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82069,"mean_force":0.15095,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.60694,0.1085,0.24655]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.5413,0.00049,-0.00132],"force_p95":0.58195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62228,"mean_force":0.13367,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52788,0.00082,0.0327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4038.0,"contact_point_centroid":[0.52889,-0.01807,0.07356],"force_p95":0.11267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33999,"mean_force":0.07741,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52544,0.00077,0.07133]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1927.0,"contact_point_centroid":[0.54486,0.00286,0.14383],"force_p95":0.19073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33067,"mean_force":0.10464,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.53904,0.02142,0.14321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2319.0,"contact_point_centroid":[0.54685,0.04231,0.14603],"force_p95":0.14978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32691,"mean_force":0.09189,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.54093,0.02405,0.1461]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4241.0,"contact_point_centroid":[0.52891,0.01956,0.0718],"force_p95":0.11211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32198,"mean_force":0.0747,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52549,0.00078,0.06986]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15751,"mean_force":0.1254,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53043,0.00087,0.03283]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51649,0.00045,0.22216]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53566,0.00096,0.09296]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.59124,0.0689,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64159,0.15313,0.24964]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59124,0.0689,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6391,0.15459,0.19726]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53045,-0.01836,0.0341],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1173,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52921,0.00084,0.03143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53036,0.01992,0.03322],"force_p95":0.06827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0959,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52921,0.00084,0.03143]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1555.0,"contact_point_centroid":[0.61221,0.11456,0.25615],"force_p95":0.01205,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01652,"mean_force":0.01059,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.61176,0.11455,0.25384]},{"body_a":"left_finger","body_b":"right_finger","contact_count":848.0,"contact_point_centroid":[0.64196,0.15314,0.25179],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64159,0.15313,0.2496]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.64216,0.15534,0.19629],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64149,0.15532,0.19392]}],"total_contact_groups":16},"final_pose_error":0.01458,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.59124,0.0689,0.01602],"final_tcp_position":[0.64331,0.15575,0.19861],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.53495,0.00093,0.14298],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11734,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.53823,0.00101,0.04217],"tcp_start":[0.53495,0.00093,0.14298],"tcp_to_object_dist_end":0.01726,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52918,0.00084,0.03139],"tcp_start":[0.53823,0.00101,0.04217],"tcp_to_object_dist_end":0.01598,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":296.0,"n_steps_budget":600.0,"object_pos_end":[0.54371,0.00081,0.11065],"object_pos_start":[0.54418,0.00072,0.02588],"object_to_goal_dist_end":0.20495,"object_to_goal_dist_start":0.25053,"object_z_max":0.1104,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52512,0.00078,0.12192],"tcp_start":[0.52918,0.00084,0.03139],"tcp_to_object_dist_end":0.02174,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.59124,0.0689,0.01602],"object_pos_start":[0.54371,0.00081,0.11065],"object_to_goal_dist_end":0.20442,"object_to_goal_dist_start":0.20495,"object_z_max":0.15053,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.6407,0.15089,0.29751],"tcp_start":[0.52512,0.00078,0.12192],"tcp_to_object_dist_end":0.29733,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.59124,0.0689,0.01602],"object_pos_start":[0.59124,0.0689,0.01602],"object_to_goal_dist_end":0.20442,"object_to_goal_dist_start":0.20442,"object_z_max":0.01602,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.64331,0.15575,0.19861],"tcp_start":[0.6407,0.15089,0.29751],"tcp_to_object_dist_end":0.20879,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59124,0.0689,0.01602],"object_pos_start":[0.59124,0.0689,0.01602],"object_to_goal_dist_end":0.20442,"object_to_goal_dist_start":0.20442,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.6377,0.15414,0.21645],"tcp_start":[0.64331,0.15575,0.19861],"tcp_to_object_dist_end":0.22271,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.4,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13353,"approach_1.approach_speed":0.53711,"approach_place.approach_goal_speed":0.43109,"approach_place.place_approach_z":0.10166,"descend_grasp.descend_speed":0.455,"descend_grasp.grasp_z_offset":0.00368,"descend_place.descend_place_speed":0.17771,"descend_place.place_z_offset":0.00417,"lift_1.lift_height":0.12195,"lift_1.lift_speed":0.30694,"release_1.release_duration":0.46149},"optimized_scores":{"best_composite_score":0.0569,"best_fitness_score":0.7569,"best_task_score":0.57405},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":206.0,"contact_point_centroid":[0.58411,0.18899,-0.00532],"force_p95":1.01888,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14977,"mean_force":0.31848,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58841,0.17238,0.13182]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.52701,0.02841,-0.00145],"force_p95":0.51644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52606,"mean_force":0.11355,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51492,0.02897,0.04002]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":705.0,"contact_point_centroid":[0.59565,0.19245,0.11649],"force_p95":0.1569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42867,"mean_force":0.08832,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59253,0.17376,0.11993]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.59701,0.1555,0.11678],"force_p95":0.13004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40538,"mean_force":0.09077,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5927,0.17381,0.12015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4584.0,"contact_point_centroid":[0.51572,0.00993,0.08639],"force_p95":0.11311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32889,"mean_force":0.0748,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51264,0.02881,0.08406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4872.0,"contact_point_centroid":[0.51567,0.04767,0.08368],"force_p95":0.11344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32361,"mean_force":0.07218,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51268,0.02882,0.08178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1816.0,"contact_point_centroid":[0.59767,0.18842,0.16197],"force_p95":0.15383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29042,"mean_force":0.09262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59279,0.1702,0.1633]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1661.0,"contact_point_centroid":[0.59782,0.15161,0.16166],"force_p95":0.16704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26887,"mean_force":0.10213,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59283,0.17027,0.16271]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03055,-0.00215],"force_p95":0.16486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22994,"mean_force":0.13374,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51747,0.02914,0.03989]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5246.0,"contact_point_centroid":[0.55872,0.08218,0.16974],"force_p95":0.12773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19208,"mean_force":0.08599,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.55284,0.10081,0.16845]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5555.0,"contact_point_centroid":[0.55875,0.11942,0.16936],"force_p95":0.11833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19185,"mean_force":0.08278,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.55283,0.10087,0.16841]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.51723,0.00985,0.04131],"force_p95":0.08152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15453,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51629,0.02906,0.03856]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.5305,0.03079,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5103,0.01218,0.24147]},{"body_a":"world","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5228,0.02744,0.11522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5023.0,"contact_point_centroid":[0.51716,0.04823,0.04035],"force_p95":0.07442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07821,"mean_force":0.04446,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5163,0.02907,0.03856]}],"total_contact_groups":15},"final_pose_error":0.01467,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58639,0.18521,0.02649],"final_tcp_position":[0.59528,0.17449,0.12488],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.52237,0.02541,0.18064],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15493,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.52509,0.02962,0.04889],"tcp_start":[0.52237,0.02541,0.18064],"tcp_to_object_dist_end":0.02354,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02935,0.0255],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51626,0.02906,0.03852],"tcp_start":[0.52509,0.02962,0.04889],"tcp_to_object_dist_end":0.01926,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":323.0,"n_steps_budget":600.0,"object_pos_end":[0.52953,0.02915,0.12168],"object_pos_start":[0.53045,0.02935,0.0255],"object_to_goal_dist_end":0.16643,"object_to_goal_dist_start":0.18478,"object_z_max":0.12143,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.5125,0.02881,0.14092],"tcp_start":[0.51626,0.02906,0.03852],"tcp_to_object_dist_end":0.0257,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.59927,0.16698,0.1667],"object_pos_start":[0.52953,0.02915,0.12168],"object_to_goal_dist_end":0.05979,"object_to_goal_dist_start":0.16643,"object_z_max":0.16662,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.59186,0.16671,0.19691],"tcp_start":[0.5125,0.02881,0.14092],"tcp_to_object_dist_end":0.03111,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.59797,0.17458,0.09273],"object_pos_start":[0.59927,0.16698,0.1667],"object_to_goal_dist_end":0.01627,"object_to_goal_dist_start":0.05979,"object_z_max":0.16672,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.59528,0.17449,0.12488],"tcp_start":[0.59186,0.16671,0.19691],"tcp_to_object_dist_end":0.03227,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58639,0.18521,0.02649],"object_pos_start":[0.59797,0.17458,0.09273],"object_to_goal_dist_end":0.08325,"object_to_goal_dist_start":0.01627,"object_z_max":0.09273,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.58828,0.17234,0.14474],"tcp_start":[0.59528,0.17449,0.12488],"tcp_to_object_dist_end":0.11896,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.6,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1137,"approach_1.approach_speed":0.56912,"approach_place.approach_goal_speed":0.49935,"approach_place.place_approach_z":0.11647,"descend_grasp.descend_speed":0.28202,"descend_grasp.grasp_z_offset":-0.0054,"descend_place.descend_place_speed":0.21103,"descend_place.place_z_offset":-0.00904,"lift_1.lift_height":0.11215,"lift_1.lift_speed":0.369,"release_1.release_duration":0.47445},"optimized_scores":{"best_composite_score":-0.13326,"best_fitness_score":0.56674,"best_task_score":0.17752},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1631.0,"contact_point_centroid":[0.52237,0.09055,-0.00268],"force_p95":0.33349,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78422,"mean_force":0.16884,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.55554,0.1274,0.28654]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.50069,-0.01493,-0.00134],"force_p95":0.61103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64366,"mean_force":0.14921,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48937,-0.01508,0.0316]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2014.0,"contact_point_centroid":[0.50386,0.03032,0.15186],"force_p95":0.17564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4743,"mean_force":0.10378,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.49791,0.01186,0.15128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4311.0,"contact_point_centroid":[0.48939,0.00397,0.07306],"force_p95":0.10934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34634,"mean_force":0.07014,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48713,-0.01504,0.07054]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2017.0,"contact_point_centroid":[0.50261,-0.00926,0.14906],"force_p95":0.16492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31974,"mean_force":0.09726,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.49668,0.0092,0.14831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4721.0,"contact_point_centroid":[0.48947,-0.03392,0.07139],"force_p95":0.1054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31562,"mean_force":0.06537,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48714,-0.01504,0.06959]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.0155,-0.00205],"force_p95":0.13898,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18047,"mean_force":0.12705,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49178,-0.01511,0.03148]},{"body_a":"world","body_b":"grasp_target","contact_count":972.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49956,-0.00629,0.23297]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.49118,0.00411,0.03304],"force_p95":0.07745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12278,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49063,-0.0151,0.03029]},{"body_a":"world","body_b":"grasp_target","contact_count":888.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4988,-0.01412,0.10165]},{"body_a":"world","body_b":"grasp_target","contact_count":788.0,"contact_point_centroid":[0.52102,0.09244,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58246,0.18178,0.30182]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52102,0.09244,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5804,0.18371,0.25351]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.49122,-0.03419,0.03213],"force_p95":0.06951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08819,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49063,-0.0151,0.03029]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1759.0,"contact_point_centroid":[0.55624,0.12816,0.28975],"force_p95":0.01171,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01688,"mean_force":0.01056,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.55592,0.12816,0.28744]},{"body_a":"left_finger","body_b":"right_finger","contact_count":829.0,"contact_point_centroid":[0.58293,0.18179,0.30403],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58246,0.18178,0.30186]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.58249,0.18447,0.25145],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01104,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58223,0.18445,0.24928]}],"total_contact_groups":16},"final_pose_error":0.01478,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52102,0.09244,0.01602],"final_tcp_position":[0.58366,0.18488,0.25327],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.50012,-0.01311,0.16311],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13716,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.49921,-0.01518,0.0396],"tcp_start":[0.50012,-0.01311,0.16311],"tcp_to_object_dist_end":0.01435,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01501,0.02581],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.4906,-0.01509,0.03025],"tcp_start":[0.49921,-0.01518,0.0396],"tcp_to_object_dist_end":0.01383,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":286.0,"n_steps_budget":600.0,"object_pos_end":[0.50525,-0.01502,0.11324],"object_pos_start":[0.50369,-0.01501,0.02581],"object_to_goal_dist_end":0.25662,"object_to_goal_dist_start":0.31198,"object_z_max":0.11298,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48682,-0.01503,0.12293],"tcp_start":[0.4906,-0.01509,0.03025],"tcp_to_object_dist_end":0.02082,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.52102,0.09244,0.01602],"object_pos_start":[0.50525,-0.01502,0.11324],"object_to_goal_dist_end":0.2593,"object_to_goal_dist_start":0.25662,"object_z_max":0.16193,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.58178,0.17906,0.34733],"tcp_start":[0.48682,-0.01503,0.12293],"tcp_to_object_dist_end":0.3478,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.52102,0.09244,0.01602],"object_pos_start":[0.52102,0.09244,0.01602],"object_to_goal_dist_end":0.2593,"object_to_goal_dist_start":0.2593,"object_z_max":0.01602,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.58366,0.18488,0.25327],"tcp_start":[0.58178,0.17906,0.34733],"tcp_to_object_dist_end":0.26222,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52102,0.09244,0.01602],"object_pos_start":[0.52102,0.09244,0.01602],"object_to_goal_dist_end":0.2593,"object_to_goal_dist_start":0.2593,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.57937,0.18327,0.27332],"tcp_start":[0.58366,0.18488,0.25327],"tcp_to_object_dist_end":0.27903,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```