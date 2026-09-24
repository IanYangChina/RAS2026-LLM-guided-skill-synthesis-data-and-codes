## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4950 | 0.22 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1874 | 0.33 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1863 | 0.34 | ✅ accepted |
| 2 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 1 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.495) — your mutation base

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
      - 0.1
      - 0.5
      default: 0.3
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
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
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
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace
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
    approach_goal_speed:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.5
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
  subtask_id: place
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
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
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace

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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
    - place_approach_z: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.495
- **task_score** (E): 0.220
- **fitness_score**: 0.335  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1387 |
| descend_grasp | 1.00 | 0.1338 |
| grasp_1 | 1.00 | 0.0136 |
| lift_1 | 1.00 | 0.1457 |
| approach_goal | 1.00 | 0.3440 |
| descend_place | 1.00 | 0.1148 |
| release_1 | 1.00 | 0.0197 |
| retract_1 | 1.00 | 0.0721 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.004, 0.165) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 |
| descend_grasp | descend | 1.00 / step_budget | (0.519, 0.004, 0.165)→(0.521, 0.005, 0.032) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.032)→(0.512, 0.005, 0.021) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| lift_1 | lift | 1.00 / step_budget | (0.510, 0.005, 0.458)→(0.512, 0.005, 0.604) | (0.526, 0.005, 0.026)→(0.557, 0.016, 0.016) | 0.249→0.238 |
| approach_goal | approach | 1.00 / step_budget | (0.512, 0.005, 0.604)→(0.604, 0.162, 0.316) | (0.557, 0.016, 0.016)→(0.557, 0.016, 0.016) | 0.238→0.238 |
| descend_place | descend | 1.00 / step_budget | (0.604, 0.162, 0.316)→(0.608, 0.171, 0.202) | (0.557, 0.016, 0.016)→(0.557, 0.016, 0.016) | 0.238→0.238 |
| release_1 | release | 1.00 / step_budget | (0.608, 0.171, 0.202)→(0.602, 0.169, 0.221) | (0.557, 0.016, 0.016)→(0.557, 0.016, 0.016) | 0.238→0.238 |
| retract_1 | retract | 1.00 / step_budget | (0.602, 0.169, 0.221)→(0.600, 0.169, 0.293) | (0.557, 0.016, 0.016)→(0.557, 0.016, 0.016) | 0.238→0.238 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.330
- phase_score: 0.037
- phase_breakdown.place_score: 0.000
- phase_breakdown.grasp_approach_score: 0.122
- grasp_place_fitness: 0.388

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.388
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.330
- **Median Q (composite search score)**: -0.506
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_grasp.grasp_z_offset
- **Final σ (mean)**: 0.290


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":14.0,"average_failure_rate":0.08092,"average_mean_iterations":20.52601,"average_solve_count":173.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10357,"approach_1.approach_speed":0.61549,"approach_goal.approach_goal_speed":0.2708,"approach_goal.place_approach_z":0.12507,"descend_grasp.descend_speed":0.19481,"descend_grasp.grasp_z_offset":-0.01439,"descend_place.descend_place_speed":0.11621,"descend_place.place_z_offset":0.00248,"lift_1.lift_height":0.29976,"lift_1.lift_speed":0.49681,"release_1.release_duration":1.49854,"retract_1.retract_height":0.08915,"retract_1.retract_speed":0.62816},"optimized_scores":{"best_composite_score":-0.506,"best_fitness_score":0.324,"best_task_score":0.19949},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3528.0,"contact_point_centroid":[0.57881,0.00571,-0.00223],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67975,"mean_force":0.13851,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52793,0.00074,0.39985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3241.0,"contact_point_centroid":[0.52963,-0.01802,0.07265],"force_p95":0.15691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44552,"mean_force":0.08556,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52547,0.00076,0.07075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3351.0,"contact_point_centroid":[0.52952,0.01951,0.0687],"force_p95":0.15369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43342,"mean_force":0.08252,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52549,0.00076,0.06693]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00096,-0.00203],"force_p95":0.13168,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16543,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53034,0.00086,0.02111]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.54431,0.00113,-0.00188],"force_p95":0.13649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51634,0.00045,0.22632]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53559,0.00095,0.09073]},{"body_a":"world","body_b":"grasp_target","contact_count":2224.0,"contact_point_centroid":[0.5795,0.00586,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58594,0.07127,0.47928]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.5795,0.00586,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6405,0.15041,0.27152]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5795,0.00586,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63924,0.15378,0.21061]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.5795,0.00586,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63586,0.1527,0.26381]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.53038,-0.01836,0.02238],"force_p95":0.07593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10575,"mean_force":0.05169,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52909,0.00084,0.01972]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4883.0,"contact_point_centroid":[0.53028,0.01992,0.02149],"force_p95":0.06796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09229,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52909,0.00084,0.01972]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3468.0,"contact_point_centroid":[0.52844,0.00073,0.42477],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01045,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52807,0.00073,0.42248]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2386.0,"contact_point_centroid":[0.58639,0.07124,0.48172],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.0104,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58591,0.07123,0.47937]},{"body_a":"left_finger","body_b":"right_finger","contact_count":812.0,"contact_point_centroid":[0.64111,0.15044,0.27355],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64051,0.15043,0.27129]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.64212,0.15452,0.20961],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.01,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64146,0.15449,0.20717]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.5795,0.00586,0.01602],"final_tcp_position":[0.63589,0.15265,0.29909],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.53479,0.00092,0.15067],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12502,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.53829,0.00101,0.03044],"tcp_start":[0.53479,0.00092,0.15067],"tcp_to_object_dist_end":0.00746,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54413,0.00071,0.02589],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25055,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52906,0.00083,0.01968],"tcp_start":[0.53829,0.00101,0.03044],"tcp_to_object_dist_end":0.0163,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1205.0,"n_steps_budget":600.0,"object_pos_end":[0.5795,0.00586,0.01602],"object_pos_start":[0.54413,0.00071,0.02589],"object_to_goal_dist_end":0.2418,"object_to_goal_dist_start":0.25055,"object_z_max":0.13643,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.53392,0.00064,0.62496],"tcp_start":[0.52961,0.00071,0.56881],"tcp_to_object_dist_end":0.61067,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":556.0,"n_steps_budget":1000.0,"object_pos_end":[0.5795,0.00586,0.01602],"object_pos_start":[0.5795,0.00586,0.01602],"object_to_goal_dist_end":0.2418,"object_to_goal_dist_start":0.2418,"object_z_max":0.01602,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.63843,0.14629,0.32919],"tcp_start":[0.53392,0.00064,0.62496],"tcp_to_object_dist_end":0.34824,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":192.0,"n_steps_budget":1000.0,"object_pos_end":[0.5795,0.00586,0.01602],"object_pos_start":[0.5795,0.00586,0.01602],"object_to_goal_dist_end":0.2418,"object_to_goal_dist_start":0.2418,"object_z_max":0.01602,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.6433,0.15487,0.21247],"tcp_start":[0.63843,0.14629,0.32919],"tcp_to_object_dist_end":0.2547,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5795,0.00586,0.01602],"object_pos_start":[0.5795,0.00586,0.01602],"object_to_goal_dist_end":0.2418,"object_to_goal_dist_start":0.2418,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.63793,0.15335,0.22982],"tcp_start":[0.6433,0.15487,0.21247],"tcp_to_object_dist_end":0.26623,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":287.0,"n_steps_budget":600.0,"object_pos_end":[0.5795,0.00586,0.01602],"object_pos_start":[0.5795,0.00586,0.01602],"object_to_goal_dist_end":0.2418,"object_to_goal_dist_start":0.2418,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place","tcp_end":[0.63589,0.15265,0.29909],"tcp_start":[0.63793,0.15335,0.22982],"tcp_to_object_dist_end":0.32382,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.7697,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13312,"approach_1.approach_speed":0.59989,"approach_goal.approach_goal_speed":0.34305,"approach_goal.place_approach_z":0.11726,"descend_grasp.descend_speed":0.25296,"descend_grasp.grasp_z_offset":-0.02,"descend_place.descend_place_speed":0.21194,"descend_place.place_z_offset":-0.00492,"lift_1.lift_height":0.21424,"lift_1.lift_speed":0.32989,"release_1.release_duration":0.8113,"retract_1.retract_height":0.10146,"retract_1.retract_speed":0.57902},"optimized_scores":{"best_composite_score":-0.44194,"best_fitness_score":0.38806,"best_task_score":0.33037},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4673.0,"contact_point_centroid":[0.56909,0.04366,-0.00219],"force_p95":0.12585,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51752,"mean_force":0.1346,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51206,0.0288,0.37605]},{"body_a":"grasp_target","body_b":"hand","contact_count":187.0,"contact_point_centroid":[0.53038,0.02944,0.08551],"force_p95":0.16861,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58903,"mean_force":0.09875,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51233,0.02889,0.0472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4764.0,"contact_point_centroid":[0.51601,0.04762,0.06761],"force_p95":0.14524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36324,"mean_force":0.07738,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51227,0.02888,0.06613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4158.0,"contact_point_centroid":[0.51607,0.01005,0.0689],"force_p95":0.14824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36245,"mean_force":0.08374,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51227,0.02888,0.06653]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53041,0.03001,-0.00234],"force_p95":0.17598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29195,"mean_force":0.14932,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51716,0.02923,0.01608]},{"body_a":"grasp_target","body_b":"hand","contact_count":376.0,"contact_point_centroid":[0.53386,0.04185,0.05401],"force_p95":0.16263,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23411,"mean_force":0.09009,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5163,0.02917,0.01516]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.5305,0.03079,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51033,0.01222,0.24111]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52273,0.02752,0.10274]},{"body_a":"world","body_b":"grasp_target","contact_count":2364.0,"contact_point_centroid":[0.56988,0.04397,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55433,0.0973,0.42017]},{"body_a":"world","body_b":"grasp_target","contact_count":788.0,"contact_point_centroid":[0.56988,0.04397,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59435,0.17158,0.18166]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56988,0.04397,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59094,0.17372,0.12152]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.56988,0.04397,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58615,0.17213,0.18189]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3932.0,"contact_point_centroid":[0.51691,0.01,0.01751],"force_p95":0.07844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09113,"mean_force":0.05147,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51593,0.02915,0.01475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5028.0,"contact_point_centroid":[0.51671,0.04837,0.01654],"force_p95":0.0713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08967,"mean_force":0.04595,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51594,0.02915,0.01476]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4625.0,"contact_point_centroid":[0.51248,0.0288,0.39767],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01049,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51198,0.02879,0.39533]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2546.0,"contact_point_centroid":[0.55465,0.09694,0.42341],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01036,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55412,0.09692,0.42114]}],"total_contact_groups":18},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56988,0.04397,0.01602],"final_tcp_position":[0.58606,0.17206,0.22326],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.5224,0.02545,0.18012],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15441,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.52504,0.02973,0.02502],"tcp_start":[0.5224,0.02545,0.18012],"tcp_to_object_dist_end":0.00565,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52976,0.02921,0.02497],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18539,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51591,0.02914,0.01472],"tcp_start":[0.52504,0.02973,0.02502],"tcp_to_object_dist_end":0.01723,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1566.0,"n_steps_budget":600.0,"object_pos_end":[0.56987,0.04415,0.01615],"object_pos_start":[0.52976,0.02921,0.02497],"object_to_goal_dist_end":0.16591,"object_to_goal_dist_start":0.18539,"object_z_max":0.13454,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51421,0.02884,0.59769],"tcp_start":[0.51214,0.02882,0.40309],"tcp_to_object_dist_end":0.5844,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.56988,0.04397,0.01602],"object_pos_start":[0.56988,0.04397,0.01602],"object_to_goal_dist_end":0.16613,"object_to_goal_dist_start":0.16613,"object_z_max":0.01602,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.59372,0.1683,0.24025],"tcp_start":[0.51421,0.02884,0.59769],"tcp_to_object_dist_end":0.25749,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.56988,0.04397,0.01602],"object_pos_start":[0.56988,0.04397,0.01602],"object_to_goal_dist_end":0.16613,"object_to_goal_dist_start":0.16613,"object_z_max":0.01602,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.59637,0.17536,0.12208],"tcp_start":[0.59372,0.1683,0.24025],"tcp_to_object_dist_end":0.17092,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56988,0.04397,0.01602],"object_pos_start":[0.56988,0.04397,0.01602],"object_to_goal_dist_end":0.16613,"object_to_goal_dist_start":0.16613,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.58913,0.17311,0.14135],"tcp_start":[0.59637,0.17536,0.12208],"tcp_to_object_dist_end":0.18099,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":309.0,"n_steps_budget":600.0,"object_pos_end":[0.56988,0.04397,0.01602],"object_pos_start":[0.56988,0.04397,0.01602],"object_to_goal_dist_end":0.16613,"object_to_goal_dist_start":0.16613,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place","tcp_end":[0.58606,0.17206,0.22326],"tcp_start":[0.58913,0.17311,0.14135],"tcp_to_object_dist_end":0.24417,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.675,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1157,"approach_1.approach_speed":0.59017,"approach_goal.approach_goal_speed":0.393,"approach_goal.place_approach_z":0.12293,"descend_grasp.descend_speed":0.23471,"descend_grasp.grasp_z_offset":-0.00597,"descend_place.descend_place_speed":0.36491,"descend_place.place_z_offset":0.00448,"lift_1.lift_height":0.20582,"lift_1.lift_speed":0.45501,"release_1.release_duration":1.13045,"retract_1.retract_height":0.08493,"retract_1.retract_speed":0.50588},"optimized_scores":{"best_composite_score":-0.53714,"best_fitness_score":0.29286,"best_task_score":0.1295},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4380.0,"contact_point_centroid":[0.5211,-0.0021,-0.00218],"force_p95":0.12792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67578,"mean_force":0.13371,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48673,-0.01505,0.37873]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4404.0,"contact_point_centroid":[0.49072,0.00384,0.08455],"force_p95":0.13381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39681,"mean_force":0.07983,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48722,-0.01504,0.08232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4721.0,"contact_point_centroid":[0.49067,-0.03383,0.08176],"force_p95":0.13011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36033,"mean_force":0.0757,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48724,-0.01504,0.08018]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01549,-0.00205],"force_p95":0.13903,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18062,"mean_force":0.12707,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49177,-0.0151,0.0312]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.50382,-0.01567,-0.00186],"force_p95":0.13695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49958,-0.00627,0.23396]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4988,-0.0141,0.10255]},{"body_a":"world","body_b":"grasp_target","contact_count":1916.0,"contact_point_centroid":[0.52137,-0.00189,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53359,0.0764,0.48399]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.52137,-0.00189,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58104,0.17737,0.3263]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52137,-0.00189,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58051,0.18233,0.27123]},{"body_a":"world","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.52137,-0.00189,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57817,0.18131,0.32298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.49118,0.00411,0.03276],"force_p95":0.07745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12246,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49063,-0.01509,0.03001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.49122,-0.03418,0.03185],"force_p95":0.06952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08652,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49063,-0.01509,0.03001]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4310.0,"contact_point_centroid":[0.487,-0.01505,0.39911],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01656,"mean_force":0.01054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48664,-0.01505,0.39674]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2080.0,"contact_point_centroid":[0.53407,0.07643,0.48624],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01028,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53361,0.07642,0.48396]},{"body_a":"left_finger","body_b":"right_finger","contact_count":777.0,"contact_point_centroid":[0.58154,0.17736,0.32869],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01055,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58104,0.17735,0.32646]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.58286,0.18307,0.26929],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58216,0.18305,0.26694]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52137,-0.00189,0.01602],"final_tcp_position":[0.57822,0.18124,0.35621],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.50014,-0.01307,0.16516],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13921,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.49923,-0.01518,0.03935],"tcp_start":[0.50014,-0.01307,0.16516],"tcp_to_object_dist_end":0.01411,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.015,0.02581],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.4906,-0.01509,0.02998],"tcp_start":[0.49923,-0.01518,0.03935],"tcp_to_object_dist_end":0.01374,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1493.0,"n_steps_budget":600.0,"object_pos_end":[0.52134,-0.00176,0.01654],"object_pos_start":[0.50369,-0.015,0.02581],"object_to_goal_dist_end":0.30615,"object_to_goal_dist_start":0.31198,"object_z_max":0.13765,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48833,-0.01514,0.58807],"tcp_start":[0.48687,-0.01504,0.40204],"tcp_to_object_dist_end":0.57264,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.52137,-0.00189,0.01602],"object_pos_start":[0.52137,-0.00189,0.01602],"object_to_goal_dist_end":0.30661,"object_to_goal_dist_start":0.30661,"object_z_max":0.01602,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","tcp_end":[0.57892,0.17166,0.37959],"tcp_start":[0.48833,-0.01514,0.58807],"tcp_to_object_dist_end":0.40696,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.52137,-0.00189,0.01602],"object_pos_start":[0.52137,-0.00189,0.01602],"object_to_goal_dist_end":0.30661,"object_to_goal_dist_start":0.30661,"object_z_max":0.01602,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.5835,0.18339,0.27131],"tcp_start":[0.57892,0.17166,0.37959],"tcp_to_object_dist_end":0.32149,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52137,-0.00189,0.01602],"object_pos_start":[0.52137,-0.00189,0.01602],"object_to_goal_dist_end":0.30661,"object_to_goal_dist_start":0.30661,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.5796,0.18191,0.29105],"tcp_start":[0.5835,0.18339,0.27131],"tcp_to_object_dist_end":0.33588,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":247.0,"n_steps_budget":600.0,"object_pos_end":[0.52137,-0.00189,0.01602],"object_pos_start":[0.52137,-0.00189,0.01602],"object_to_goal_dist_end":0.30661,"object_to_goal_dist_start":0.30661,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place","tcp_end":[0.57822,0.18124,0.35621],"tcp_start":[0.5796,0.18191,0.29105],"tcp_to_object_dist_end":0.39051,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```