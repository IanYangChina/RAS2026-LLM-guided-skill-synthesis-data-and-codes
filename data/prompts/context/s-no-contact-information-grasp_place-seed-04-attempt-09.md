## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 13 | -0.3922 | 0.36 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0947 | 0.48 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2160 | 0.56 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1855 | 0.34 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4950 | 0.22 | ❌ rejected |

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

## Current Skill (Q=-0.392) — your mutation base

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

- **Composite score**: -0.392
- **task_score** (E): 0.364
- **fitness_score**: 0.408  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.800

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1541 |
| descend_grasp | 1.00 | 0.1101 |
| grasp_1 | 1.00 | 0.0135 |
| lift_1 | 0.00 | 0.0001 |
| approach_goal | 0.00 | 0.0001 |
| descend_place | 0.67 | 0.2138 |
| release_1 | 1.00 | 0.0218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.150) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 |
| descend_grasp | descend | 1.00 / step_budget | (0.519, 0.005, 0.150)→(0.521, 0.005, 0.040) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.040)→(0.512, 0.005, 0.029) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| lift_1 | lift | 0.00 / guard_failure | (0.512, 0.005, 0.029)→(0.512, 0.005, 0.029) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| approach_goal | approach | 0.00 / guard_failure | (0.512, 0.005, 0.029)→(0.512, 0.005, 0.029) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| descend_place | descend | 0.67 / step_budget | (0.512, 0.005, 0.029)→(0.598, 0.154, 0.149) | (0.526, 0.005, 0.025)→(0.596, 0.156, 0.035) | 0.249→0.151 |
| release_1 | release | 1.00 / step_budget | (0.598, 0.154, 0.149)→(0.592, 0.153, 0.170) | (0.596, 0.156, 0.035)→(0.596, 0.157, 0.020) | 0.151→0.165 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.574
- phase_score: 0.539
- phase_breakdown.place_score: 0.691
- phase_breakdown.grasp_approach_score: 0.184
- grasp_place_fitness: 0.509

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.509
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.574
- **Median Q (composite search score)**: -0.419
- **K-run variance**: 0.0055
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.310


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30303,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13798,"approach_1.approach_speed":0.53681,"approach_goal.approach_goal_speed":0.27615,"approach_goal.place_approach_z":0.2491,"approach_goal.transport_guard_threshold":0.04365,"descend_grasp.descend_speed":0.35577,"descend_grasp.grasp_z_offset":-0.00624,"descend_place.descend_place_speed":0.28719,"descend_place.place_z_offset":-0.00673,"lift_1.lift_guard_threshold":0.04605,"lift_1.lift_height":0.38987,"lift_1.lift_speed":0.28329,"release_1.release_duration":0.40714},"optimized_scores":{"best_composite_score":-0.41854,"best_fitness_score":0.38146,"best_task_score":0.31051},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":450.0,"contact_point_centroid":[0.59574,0.08106,-0.00371],"force_p95":0.97841,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52699,"mean_force":0.32932,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58499,0.07838,0.0996]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11204.0,"contact_point_centroid":[0.57775,0.0837,0.08607],"force_p95":0.13504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31455,"mean_force":0.07619,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57381,0.06526,0.08558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10157.0,"contact_point_centroid":[0.57425,0.04193,0.08161],"force_p95":0.15557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29797,"mean_force":0.08945,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57043,0.06076,0.08124]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.54425,0.00075,-0.00217],"force_p95":0.27611,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27624,"mean_force":0.25021,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52912,0.00084,0.02753]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.54429,0.00075,-0.00208],"force_p95":0.27054,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27309,"mean_force":0.23666,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52926,0.00084,0.02771]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.1322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15952,"mean_force":0.12537,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53054,0.00087,0.02918]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.54431,0.00113,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51582,0.00043,0.24323]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.53024,0.01983,0.02931],"force_p95":0.11484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13201,"mean_force":0.08221,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52912,0.00084,0.02753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.53038,0.01983,0.02949],"force_p95":0.113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13191,"mean_force":0.07602,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52926,0.00084,0.02771]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63943,0.1507,-0.00194],"force_p95":0.12781,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12976,"mean_force":0.12057,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63558,0.15083,0.16996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.53047,-0.01831,0.03038],"force_p95":0.11738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12437,"mean_force":0.08223,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52926,0.00084,0.02771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.53033,-0.01831,0.0302],"force_p95":0.12224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12398,"mean_force":0.08782,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52912,0.00084,0.02753]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53509,0.00094,0.112]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53052,-0.01835,0.03045],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1141,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52931,0.00084,0.02778]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53043,0.01992,0.02958],"force_p95":0.06819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09648,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52931,0.00084,0.02778]},{"body_a":"left_finger","body_b":"right_finger","contact_count":199.0,"contact_point_centroid":[0.63861,0.15168,0.1689],"force_p95":0.01493,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01136,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63826,0.15167,0.16661]}],"total_contact_groups":16},"final_pose_error":0.01755,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63943,0.15069,0.01602],"final_tcp_position":[0.63981,0.15178,0.16998],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.53372,0.00089,0.18458],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15891,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.53842,0.00101,0.03857],"tcp_start":[0.53372,0.00089,0.18458],"tcp_to_object_dist_end":0.01387,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52928,0.00084,0.02775],"tcp_start":[0.53842,0.00101,0.03857],"tcp_to_object_dist_end":0.015,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":870.0,"object_pos_end":[0.54415,0.00072,0.02585],"object_pos_start":[0.54416,0.00072,0.02588],"object_to_goal_dist_end":0.25056,"object_to_goal_dist_start":0.25053,"object_z_max":0.02588,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52918,0.00084,0.02761],"tcp_start":[0.52923,0.00084,0.02767],"tcp_to_object_dist_end":0.01508,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54403,0.00072,0.02566],"object_pos_start":[0.54408,0.00072,0.02573],"object_to_goal_dist_end":0.25073,"object_to_goal_dist_start":0.25066,"object_z_max":0.02573,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.52897,0.00084,0.02736],"tcp_start":[0.52905,0.00084,0.02745],"tcp_to_object_dist_end":0.01515,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63979,0.15162,0.01573],"object_pos_start":[0.5439,0.00072,0.0255],"object_to_goal_dist_end":0.17567,"object_to_goal_dist_start":0.2509,"object_z_max":0.12698,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.63981,0.15178,0.16998],"tcp_start":[0.52897,0.00084,0.02736],"tcp_to_object_dist_end":0.15425,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63943,0.15069,0.01602],"object_pos_start":[0.63979,0.15162,0.01573],"object_to_goal_dist_end":0.17543,"object_to_goal_dist_start":0.17567,"object_z_max":0.01664,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place","tcp_end":[0.63394,0.15035,0.18914],"tcp_start":[0.63981,0.15178,0.16998],"tcp_to_object_dist_end":0.17321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1791,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05685,"approach_1.approach_speed":0.39991,"approach_goal.approach_goal_speed":0.28587,"approach_goal.place_approach_z":0.11047,"approach_goal.transport_guard_threshold":0.021,"descend_grasp.descend_speed":0.25333,"descend_grasp.grasp_z_offset":0.001,"descend_place.descend_place_speed":0.1938,"descend_place.place_z_offset":-0.00445,"lift_1.lift_guard_threshold":0.02079,"lift_1.lift_height":0.4093,"lift_1.lift_speed":0.25654,"release_1.release_duration":0.6524},"optimized_scores":{"best_composite_score":-0.29085,"best_fitness_score":0.50915,"best_task_score":0.57418},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.54074,0.05015,-0.00277],"force_p95":0.7148,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98492,"mean_force":0.43632,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52557,0.0522,0.04145]},{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.58942,0.1524,-0.00525],"force_p95":0.79896,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8735,"mean_force":0.34146,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58679,0.16961,0.10009]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10073.0,"contact_point_centroid":[0.55384,0.07758,0.06104],"force_p95":0.19537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43281,"mean_force":0.10512,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55085,0.09712,0.06051]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9390.0,"contact_point_centroid":[0.56353,0.13035,0.06845],"force_p95":0.16361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40629,"mean_force":0.07737,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55921,0.11166,0.06687]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.53072,0.0299,-0.00238],"force_p95":0.27444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27446,"mean_force":0.23577,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51548,0.02886,0.03507]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.53075,0.0299,-0.00229],"force_p95":0.27293,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27412,"mean_force":0.23331,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51562,0.02887,0.03525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":730.0,"contact_point_centroid":[0.59502,0.15187,0.08867],"force_p95":0.15198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2615,"mean_force":0.08086,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59145,0.17114,0.08957]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53058,0.0305,-0.00217],"force_p95":0.17142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24397,"mean_force":0.13525,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51686,0.02895,0.03665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.59538,0.18948,0.08912],"force_p95":0.10516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18266,"mean_force":0.05626,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59169,0.17122,0.08989]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3855.0,"contact_point_centroid":[0.51719,0.00967,0.03819],"force_p95":0.08559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15495,"mean_force":0.0545,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51567,0.02887,0.03532]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51079,0.01321,0.20316]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.51666,0.04789,0.03702],"force_p95":0.11162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13059,"mean_force":0.07592,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51562,0.02887,0.03525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.51652,0.04789,0.03684],"force_p95":0.11638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1299,"mean_force":0.08082,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51548,0.02886,0.03507]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5232,0.02823,0.07565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.5168,0.00972,0.03794],"force_p95":0.11162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11608,"mean_force":0.07994,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51562,0.02887,0.03525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.51667,0.00971,0.03777],"force_p95":0.11191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11479,"mean_force":0.08337,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51548,0.02886,0.03507]}],"total_contact_groups":17},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59215,0.16114,0.02726],"final_tcp_position":[0.59363,0.17152,0.09306],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.52338,0.02712,0.10471],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0791,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.52443,0.02942,0.04554],"tcp_start":[0.52338,0.02712,0.10471],"tcp_to_object_dist_end":0.02049,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02914,0.02544],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18497,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51565,0.02887,0.03528],"tcp_start":[0.52443,0.02942,0.04554],"tcp_to_object_dist_end":0.01778,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":990.0,"object_pos_end":[0.53044,0.02914,0.02541],"object_pos_start":[0.53045,0.02914,0.02544],"object_to_goal_dist_end":0.18499,"object_to_goal_dist_start":0.18497,"object_z_max":0.02544,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51554,0.02886,0.03515],"tcp_start":[0.51559,0.02887,0.03521],"tcp_to_object_dist_end":0.01779,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53033,0.02914,0.02523],"object_pos_start":[0.53038,0.02914,0.0253],"object_to_goal_dist_end":0.18512,"object_to_goal_dist_start":0.18507,"object_z_max":0.0253,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.51534,0.02885,0.03491],"tcp_start":[0.51542,0.02886,0.035],"tcp_to_object_dist_end":0.01784,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.60009,0.16924,0.06775],"object_pos_start":[0.53022,0.02913,0.02508],"object_to_goal_dist_end":0.04143,"object_to_goal_dist_start":0.18523,"object_z_max":0.06772,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.59363,0.17152,0.09306],"tcp_start":[0.51534,0.02885,0.03491],"tcp_to_object_dist_end":0.02622,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59215,0.16114,0.02726],"object_pos_start":[0.60009,0.16924,0.06775],"object_to_goal_dist_end":0.08322,"object_to_goal_dist_start":0.04143,"object_z_max":0.06775,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place","tcp_end":[0.58657,0.16954,0.11409],"tcp_start":[0.59363,0.17152,0.09306],"tcp_to_object_dist_end":0.08742,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.51316,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11064,"approach_1.approach_speed":0.46601,"approach_goal.approach_goal_speed":0.29973,"approach_goal.place_approach_z":0.21055,"approach_goal.transport_guard_threshold":0.0286,"descend_grasp.descend_speed":0.2536,"descend_grasp.grasp_z_offset":-0.01025,"descend_place.descend_place_speed":0.17745,"descend_place.place_z_offset":-0.00793,"lift_1.lift_guard_threshold":0.01466,"lift_1.lift_height":0.29134,"lift_1.lift_speed":0.2843,"release_1.release_duration":0.62461},"optimized_scores":{"best_composite_score":-0.46715,"best_fitness_score":0.33285,"best_task_score":0.20778},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":436.0,"contact_point_centroid":[0.53275,0.08812,-0.00442],"force_p95":1.12819,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5111,"mean_force":0.35785,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53216,0.07852,0.12007]},{"body_a":"world","body_b":"grasp_target","contact_count":700.0,"contact_point_centroid":[0.5555,0.15721,-0.00234],"force_p95":0.24769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34645,"mean_force":0.14294,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.557,0.13926,0.18668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10526.0,"contact_point_centroid":[0.51741,0.0613,0.08253],"force_p95":0.14598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2952,"mean_force":0.07858,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51387,0.04267,0.08146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10200.0,"contact_point_centroid":[0.51466,0.01859,0.07716],"force_p95":0.14435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29044,"mean_force":0.08049,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51136,0.03736,0.07594]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50377,-0.01515,-0.00219],"force_p95":0.28284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28381,"mean_force":0.26034,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49034,-0.01511,0.0252]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50382,-0.01515,-0.00211],"force_p95":0.2815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28269,"mean_force":0.24781,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49048,-0.01511,0.02536]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01547,-0.00205],"force_p95":0.13831,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18087,"mean_force":0.12694,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49168,-0.01513,0.02662]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49955,-0.00634,0.23113]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.4911,-0.03411,0.02719],"force_p95":0.1139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13141,"mean_force":0.07693,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49048,-0.01511,0.02536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.49096,-0.03411,0.02703],"force_p95":0.11527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13019,"mean_force":0.08117,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49034,-0.01511,0.0252]},{"body_a":"world","body_b":"grasp_target","contact_count":900.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49875,-0.01417,0.09746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.49107,0.00404,0.0281],"force_p95":0.11754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12247,"mean_force":0.0833,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49048,-0.01511,0.02536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.49094,0.00404,0.02794],"force_p95":0.11959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12247,"mean_force":0.0868,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49034,-0.01511,0.0252]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.49111,0.00408,0.02818],"force_p95":0.07732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11622,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49053,-0.01512,0.02543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.49115,-0.03421,0.02726],"force_p95":0.06931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08765,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49053,-0.01512,0.02543]},{"body_a":"left_finger","body_b":"right_finger","contact_count":316.0,"contact_point_centroid":[0.55883,0.13461,0.18021],"force_p95":0.01492,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01142,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55844,0.1346,0.17793]}],"total_contact_groups":17},"final_pose_error":0.07802,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55683,0.15958,0.01602],"final_tcp_position":[0.56117,0.14014,0.18374],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.50009,-0.01319,0.15964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1337,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.49918,-0.0152,0.03473],"tcp_start":[0.50009,-0.01319,0.15964],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.015,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.4905,-0.01511,0.02539],"tcp_start":[0.49918,-0.0152,0.03473],"tcp_to_object_dist_end":0.01318,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":660.0,"object_pos_end":[0.50366,-0.015,0.02579],"object_pos_start":[0.50367,-0.015,0.02582],"object_to_goal_dist_end":0.312,"object_to_goal_dist_start":0.31198,"object_z_max":0.02582,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.4904,-0.01511,0.02527],"tcp_start":[0.49045,-0.01511,0.02532],"tcp_to_object_dist_end":0.01327,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50353,-0.015,0.02562],"object_pos_start":[0.50359,-0.015,0.02568],"object_to_goal_dist_end":0.31216,"object_to_goal_dist_start":0.3121,"object_z_max":0.02568,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.4902,-0.01511,0.02505],"tcp_start":[0.49027,-0.01511,0.02513],"tcp_to_object_dist_end":0.01335,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54932,0.1468,0.02012],"object_pos_start":[0.50339,-0.015,0.02547],"object_to_goal_dist_end":0.23463,"object_to_goal_dist_start":0.3123,"object_z_max":0.12829,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.56117,0.14014,0.18374],"tcp_start":[0.4902,-0.01511,0.02505],"tcp_to_object_dist_end":0.16419,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55683,0.15958,0.01602],"object_pos_start":[0.54932,0.1468,0.02012],"object_to_goal_dist_end":0.23569,"object_to_goal_dist_start":0.23463,"object_z_max":0.02012,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place","tcp_end":[0.55587,0.13894,0.20622],"tcp_start":[0.56117,0.14014,0.18374],"tcp_to_object_dist_end":0.19132,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```