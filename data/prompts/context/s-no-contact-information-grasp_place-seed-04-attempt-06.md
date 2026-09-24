## Search State

- **Seed**: 4
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1855 | 0.34 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4950 | 0.22 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1874 | 0.33 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1863 | 0.34 | ✅ accepted |
| 2 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

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

## Current Skill (Q=-0.186) — your mutation base

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

- **Composite score**: -0.186
- **task_score** (E): 0.336
- **fitness_score**: 0.644  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1544 |
| descend_grasp | 1.00 | 0.1089 |
| grasp_1 | 1.00 | 0.0132 |
| lift_1 | 1.00 | 0.1113 |
| approach_goal | 1.00 | 0.2317 |
| descend_place | 1.00 | 0.0688 |
| release_1 | 1.00 | 0.0200 |
| retract_1 | 1.00 | 0.0860 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.149) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 |
| descend_grasp | descend | 1.00 / step_budget | (0.519, 0.005, 0.149)→(0.521, 0.005, 0.040) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.040)→(0.512, 0.005, 0.030) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.030)→(0.509, 0.005, 0.142) | (0.526, 0.005, 0.026)→(0.528, 0.005, 0.130) | 0.249→0.205 |
| approach_goal | approach | 1.00 / step_budget | (0.509, 0.005, 0.142)→(0.604, 0.165, 0.272) | (0.528, 0.005, 0.130)→(0.585, 0.121, 0.069) | 0.205→0.169 |
| descend_place | descend | 1.00 / step_budget | (0.604, 0.165, 0.272)→(0.607, 0.171, 0.204) | (0.585, 0.121, 0.069)→(0.585, 0.124, 0.046) | 0.169→0.149 |
| release_1 | release | 1.00 / step_budget | (0.607, 0.171, 0.204)→(0.602, 0.169, 0.223) | (0.585, 0.124, 0.046)→(0.582, 0.123, 0.016) | 0.149→0.178 |
| retract_1 | retract | 1.00 / step_budget | (0.602, 0.169, 0.223)→(0.600, 0.168, 0.309) | (0.582, 0.123, 0.016)→(0.582, 0.123, 0.016) | 0.178→0.178 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.538
- phase_score: 0.463
- phase_breakdown.place_score: 0.596
- phase_breakdown.grasp_approach_score: 0.153
- grasp_place_fitness: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.747
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.538
- **Median Q (composite search score)**: -0.214
- **K-run variance**: 0.0056
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.23333,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10691,"approach_1.approach_speed":0.39287,"approach_goal.approach_goal_speed":0.62062,"approach_goal.place_approach_z":0.10824,"descend_grasp.descend_speed":0.30101,"descend_grasp.grasp_z_offset":-0.00027,"descend_place.descend_place_speed":0.26342,"descend_place.place_z_offset":-0.00097,"lift_1.lift_height":0.11267,"lift_1.lift_speed":0.37476,"release_1.release_duration":1.23945,"retract_1.retract_height":0.11587,"retract_1.retract_speed":0.55202},"optimized_scores":{"best_composite_score":-0.21383,"best_fitness_score":0.61617,"best_task_score":0.28486},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.60688,0.10189,-0.00298],"force_p95":0.49957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.10795,"mean_force":0.16382,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61738,0.12172,0.25199]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54106,0.00076,-0.00132],"force_p95":0.53739,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59599,"mean_force":0.12627,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52825,0.00084,0.03509]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4175.0,"contact_point_centroid":[0.52909,-0.01806,0.0771],"force_p95":0.11582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34966,"mean_force":0.07711,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52588,0.0008,0.07482]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2812.0,"contact_point_centroid":[0.55404,0.01508,0.15917],"force_p95":0.17754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32433,"mean_force":0.1057,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54854,0.0336,0.15821]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4377.0,"contact_point_centroid":[0.5292,0.0196,0.07575],"force_p95":0.11259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32367,"mean_force":0.07435,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52593,0.0008,0.07367]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3311.0,"contact_point_centroid":[0.55593,0.05401,0.16075],"force_p95":0.15327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3153,"mean_force":0.09358,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55016,0.03576,0.1604]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13201,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15255,"mean_force":0.12527,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53076,0.00088,0.03521]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.54431,0.00113,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51626,0.00045,0.22778]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53564,0.00096,0.09957]},{"body_a":"world","body_b":"grasp_target","contact_count":516.0,"contact_point_centroid":[0.60681,0.10186,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64122,0.15262,0.24793]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60681,0.10186,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63871,0.15393,0.20731]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.60681,0.10186,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63525,0.15284,0.27411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4117.0,"contact_point_centroid":[0.53055,-0.01834,0.03657],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10198,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52957,0.00087,0.03383]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4872.0,"contact_point_centroid":[0.53053,0.01994,0.03571],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09505,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52957,0.00087,0.03383]},{"body_a":"left_finger","body_b":"right_finger","contact_count":942.0,"contact_point_centroid":[0.6218,0.12727,0.26017],"force_p95":0.0127,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01083,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.62176,0.12726,0.25794]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.64092,0.15466,0.20608],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01011,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64102,0.15465,0.20367]}],"total_contact_groups":17},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.60681,0.10186,0.01602],"final_tcp_position":[0.63553,0.15286,0.32262],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.5347,0.00093,0.15431],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12865,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.53839,0.00102,0.04443],"tcp_start":[0.5347,0.00093,0.15431],"tcp_to_object_dist_end":0.01934,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52954,0.00086,0.0338],"tcp_start":[0.53839,0.00102,0.04443],"tcp_to_object_dist_end":0.01665,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":302.0,"n_steps_budget":600.0,"object_pos_end":[0.54406,0.0008,0.11344],"object_pos_start":[0.54418,0.00074,0.02588],"object_to_goal_dist_end":0.2037,"object_to_goal_dist_start":0.25051,"object_z_max":0.11319,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.5256,0.00081,0.12704],"tcp_start":[0.52954,0.00086,0.0338],"tcp_to_object_dist_end":0.02294,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.60681,0.10186,0.01602],"object_pos_start":[0.54406,0.0008,0.11344],"object_to_goal_dist_end":0.18836,"object_to_goal_dist_start":0.2037,"object_z_max":0.17401,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.6399,0.15035,0.28264],"tcp_start":[0.5256,0.00081,0.12704],"tcp_to_object_dist_end":0.273,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.60681,0.10186,0.01602],"object_pos_start":[0.60681,0.10186,0.01602],"object_to_goal_dist_end":0.18836,"object_to_goal_dist_start":0.18836,"object_z_max":0.01602,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.64291,0.15507,0.20891],"tcp_start":[0.6399,0.15035,0.28264],"tcp_to_object_dist_end":0.20333,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60681,0.10186,0.01602],"object_pos_start":[0.60681,0.10186,0.01602],"object_to_goal_dist_end":0.18836,"object_to_goal_dist_start":0.18836,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.63735,0.1535,0.22665],"tcp_start":[0.64291,0.15507,0.20891],"tcp_to_object_dist_end":0.21901,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":376.0,"n_steps_budget":600.0,"object_pos_end":[0.60681,0.10186,0.01602],"object_pos_start":[0.60681,0.10186,0.01602],"object_to_goal_dist_end":0.18836,"object_to_goal_dist_start":0.18836,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.63553,0.15286,0.32262],"tcp_start":[0.63735,0.1535,0.22665],"tcp_to_object_dist_end":0.31214,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.38333,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1003,"approach_1.approach_speed":0.529,"approach_goal.approach_goal_speed":0.55558,"approach_goal.place_approach_z":0.10092,"descend_grasp.descend_speed":0.25669,"descend_grasp.grasp_z_offset":-0.00871,"descend_place.descend_place_speed":0.26854,"descend_place.place_z_offset":0.00646,"lift_1.lift_height":0.14287,"lift_1.lift_speed":0.63054,"release_1.release_duration":0.74613,"retract_1.retract_height":0.10495,"retract_1.retract_speed":0.47097},"optimized_scores":{"best_composite_score":-0.08344,"best_fitness_score":0.74656,"best_task_score":0.53807},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":213.0,"contact_point_centroid":[0.58996,0.17695,-0.00557],"force_p95":1.29122,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32162,"mean_force":0.34786,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58829,0.17162,0.14355]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.5276,0.02844,-0.00147],"force_p95":0.61867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7926,"mean_force":0.15743,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.515,0.02901,0.02765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":781.0,"contact_point_centroid":[0.59607,0.19109,0.12394],"force_p95":0.15714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49652,"mean_force":0.08631,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59221,0.17295,0.12715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":403.0,"contact_point_centroid":[0.59659,0.15486,0.12399],"force_p95":0.18197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47483,"mean_force":0.11888,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59239,0.17301,0.12735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5129.0,"contact_point_centroid":[0.51601,0.01003,0.08354],"force_p95":0.11397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38532,"mean_force":0.07568,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51271,0.02886,0.08128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5305.0,"contact_point_centroid":[0.51596,0.0477,0.08044],"force_p95":0.11494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36966,"mean_force":0.07424,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51275,0.02886,0.0784]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1235.0,"contact_point_centroid":[0.59708,0.18739,0.16377],"force_p95":0.19077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34982,"mean_force":0.09907,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59298,0.16979,0.16654]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":727.0,"contact_point_centroid":[0.59723,0.15166,0.16343],"force_p95":0.21179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31992,"mean_force":0.14804,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59297,0.16976,0.16684]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03044,-0.00216],"force_p95":0.16894,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2584,"mean_force":0.1349,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51748,0.02919,0.02751]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4746.0,"contact_point_centroid":[0.55638,0.07994,0.17158],"force_p95":0.149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2417,"mean_force":0.09234,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55164,0.0985,0.1718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5189.0,"contact_point_centroid":[0.5565,0.11619,0.17186],"force_p95":0.12482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22283,"mean_force":0.08709,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5513,0.09789,0.1716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4047.0,"contact_point_centroid":[0.51712,0.00991,0.029],"force_p95":0.08142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14977,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5163,0.02911,0.02621]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.13649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51061,0.01277,0.22449]},{"body_a":"world","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.5907,0.17164,-0.00197],"force_p95":0.12747,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13278,"mean_force":0.12186,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58536,0.17066,0.19448]},{"body_a":"world","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52313,0.02793,0.09229]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5028.0,"contact_point_centroid":[0.51708,0.0483,0.02808],"force_p95":0.07466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08961,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51631,0.02911,0.02622]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5907,0.17164,0.01602],"final_tcp_position":[0.58528,0.1706,0.23762],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.52301,0.02631,0.14787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12216,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.52505,0.02967,0.03632],"tcp_start":[0.52301,0.02631,0.14787],"tcp_to_object_dist_end":0.01171,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.02913,0.02548],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18499,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51627,0.02911,0.02618],"tcp_start":[0.52505,0.02967,0.03632],"tcp_to_object_dist_end":0.01413,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":367.0,"n_steps_budget":600.0,"object_pos_end":[0.53398,0.02922,0.14034],"object_pos_start":[0.53039,0.02913,0.02548],"object_to_goal_dist_end":0.16707,"object_to_goal_dist_start":0.18499,"object_z_max":0.14008,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51274,0.02887,0.14959],"tcp_start":[0.51627,0.02911,0.02618],"tcp_to_object_dist_end":0.02317,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.5994,0.16633,0.17419],"object_pos_start":[0.53398,0.02922,0.14034],"object_to_goal_dist_end":0.06726,"object_to_goal_dist_start":0.16707,"object_z_max":0.17413,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.59163,0.16619,0.19686],"tcp_start":[0.51274,0.02887,0.14959],"tcp_to_object_dist_end":0.02396,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.59966,0.17364,0.10724],"object_pos_start":[0.5994,0.16633,0.17419],"object_to_goal_dist_end":0.00535,"object_to_goal_dist_start":0.06726,"object_z_max":0.17421,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.59516,0.17371,0.13271],"tcp_start":[0.59163,0.16619,0.19686],"tcp_to_object_dist_end":0.02586,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59107,0.17211,0.01606],"object_pos_start":[0.59966,0.17364,0.10724],"object_to_goal_dist_end":0.09285,"object_to_goal_dist_start":0.00535,"object_z_max":0.10724,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.58821,0.1716,0.15242],"tcp_start":[0.59516,0.17371,0.13271],"tcp_to_object_dist_end":0.13639,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":312.0,"n_steps_budget":600.0,"object_pos_end":[0.5907,0.17164,0.01602],"object_pos_start":[0.59107,0.17211,0.01606],"object_to_goal_dist_end":0.09297,"object_to_goal_dist_start":0.09285,"object_z_max":0.01652,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.58528,0.1706,0.23762],"tcp_start":[0.58821,0.1716,0.15242],"tcp_to_object_dist_end":0.22167,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.46667,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09655,"approach_1.approach_speed":0.41745,"approach_goal.approach_goal_speed":0.69708,"approach_goal.place_approach_z":0.10531,"descend_grasp.descend_speed":0.17935,"descend_grasp.grasp_z_offset":-0.00461,"descend_place.descend_place_speed":0.23859,"descend_place.place_z_offset":0.00244,"lift_1.lift_height":0.13667,"lift_1.lift_speed":0.2955,"release_1.release_duration":0.79841,"retract_1.retract_height":0.09676,"retract_1.retract_speed":0.51018},"optimized_scores":{"best_composite_score":-0.25929,"best_fitness_score":0.57071,"best_task_score":0.18579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1439.0,"contact_point_centroid":[0.54804,0.09612,-0.0028],"force_p95":0.37575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.2901,"mean_force":0.15648,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55698,0.13004,0.28893]},{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.50147,-0.01519,-0.0014],"force_p95":0.54668,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67806,"mean_force":0.14133,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48975,-0.01506,0.0326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4943.0,"contact_point_centroid":[0.49004,0.00394,0.08537],"force_p95":0.11207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3821,"mean_force":0.07312,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48751,-0.01502,0.08294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5402.0,"contact_point_centroid":[0.49017,-0.03385,0.08333],"force_p95":0.10806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33754,"mean_force":0.06802,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48754,-0.01502,0.08152]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2570.0,"contact_point_centroid":[0.50763,0.03648,0.17886],"force_p95":0.16051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33188,"mean_force":0.09411,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50161,0.01824,0.17816]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2077.0,"contact_point_centroid":[0.50628,-0.00232,0.17706],"force_p95":0.18875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31251,"mean_force":0.10938,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50067,0.01624,0.17626]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.0155,-0.00205],"force_p95":0.13937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18123,"mean_force":0.12715,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49204,-0.01509,0.03252]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,-0.00647,0.22366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.49123,0.00413,0.03413],"force_p95":0.07732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12351,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49092,-0.01507,0.03135]},{"body_a":"world","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49884,-0.01424,0.09335]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.54793,0.09606,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58224,0.18094,0.30518]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54793,0.09606,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58043,0.18286,0.2696]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.54793,0.09606,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57797,0.18182,0.32739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.49135,-0.03416,0.03323],"force_p95":0.06963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0843,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49092,-0.01507,0.03135]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1335.0,"contact_point_centroid":[0.56028,0.13646,0.29756],"force_p95":0.01211,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01066,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56021,0.13645,0.29534]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.58235,0.18358,0.26735],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01012,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58214,0.18357,0.26518]}],"total_contact_groups":17},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54793,0.09606,0.01602],"final_tcp_position":[0.57809,0.18179,0.3664],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"grasp_approach","tcp_end":[0.50007,-0.01336,0.14569],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11975,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_approach","tcp_end":[0.49927,-0.01517,0.04049],"tcp_start":[0.50007,-0.01336,0.14569],"tcp_to_object_dist_end":0.01517,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01499,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49089,-0.01507,0.03132],"tcp_start":[0.49927,-0.01517,0.04049],"tcp_to_object_dist_end":0.01394,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":343.0,"n_steps_budget":600.0,"object_pos_end":[0.50689,-0.01493,0.1362],"object_pos_start":[0.5037,-0.01499,0.0258],"object_to_goal_dist_end":0.24472,"object_to_goal_dist_start":0.31198,"object_z_max":0.13594,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48747,-0.015,0.14845],"tcp_start":[0.49089,-0.01507,0.03132],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":691.0,"n_steps_budget":1000.0,"object_pos_end":[0.54793,0.09606,0.01602],"object_pos_start":[0.50689,-0.01493,0.1362],"object_to_goal_dist_end":0.25247,"object_to_goal_dist_start":0.24472,"object_z_max":0.18981,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place","tcp_end":[0.5811,0.1781,0.33686],"tcp_start":[0.48747,-0.015,0.14845],"tcp_to_object_dist_end":0.33283,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.54793,0.09606,0.01602],"object_pos_start":[0.54793,0.09606,0.01602],"object_to_goal_dist_end":0.25247,"object_to_goal_dist_start":0.25247,"object_z_max":0.01602,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place","tcp_end":[0.58357,0.18396,0.26953],"tcp_start":[0.5811,0.1781,0.33686],"tcp_to_object_dist_end":0.27067,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54793,0.09606,0.01602],"object_pos_start":[0.54793,0.09606,0.01602],"object_to_goal_dist_end":0.25247,"object_to_goal_dist_start":0.25247,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.57947,0.18244,0.28952],"tcp_start":[0.58357,0.18396,0.26953],"tcp_to_object_dist_end":0.28855,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":283.0,"n_steps_budget":600.0,"object_pos_end":[0.54793,0.09606,0.01602],"object_pos_start":[0.54793,0.09606,0.01602],"object_to_goal_dist_end":0.25247,"object_to_goal_dist_start":0.25247,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.57809,0.18179,0.3664],"tcp_start":[0.57947,0.18244,0.28952],"tcp_to_object_dist_end":0.36198,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```