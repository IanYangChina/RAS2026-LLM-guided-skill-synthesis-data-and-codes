## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.1844 | 0.24 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1177 | 0.28 | ✅ accepted |
| 11 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 10 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 9 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

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
- Frozen object start: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5443056105572368, 0.0011327552814361583, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5443056105572368, 0.0011327552814361583, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=-0.184) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_clearance
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: place_goal
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
    - 0.12
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
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
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: abort
  subtask_id: grasp_object
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
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: approach_2
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    approach_goal_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.0
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.184
- **task_score** (E): 0.239
- **fitness_score**: 0.596  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1067 |
| descend_1 | 1.00 | 1.00 | 0.1572 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 1.00 | 1.00 | 0.1258 |
| approach_2 | 1.00 | 1.00 | 0.2129 |
| descend_2 | 1.00 | 1.00 | 0.0899 |
| release_1 | 1.00 | 1.00 | 0.0205 |
| retract_1 | 1.00 | 1.00 | 0.0847 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.199) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.005, 0.199)→(0.521, 0.005, 0.042) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.042)→(0.513, 0.005, 0.032) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.000 | 0.136 | 0.179 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.032)→(0.521, 0.005, 0.158) | (0.526, 0.005, 0.026)→(0.537, 0.005, 0.141) | 0.249→0.197 | 1.00 / 24.000 | 0.130 | 0.598 |
| approach_2 | approach | 1.00 / step_budget | (0.521, 0.005, 0.158)→(0.593, 0.143, 0.293) | (0.537, 0.005, 0.141)→(0.532, 0.032, 0.016) | 0.197→0.234 | 1.00 / 8.000 | 0.123 | 1.730 |
| descend_2 | descend | 1.00 / step_budget | (0.593, 0.143, 0.293)→(0.606, 0.169, 0.209) | (0.532, 0.032, 0.016)→(0.532, 0.032, 0.016) | 0.234→0.234 | 1.00 / 8.333 | 97501.689 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.606, 0.169, 0.209)→(0.601, 0.167, 0.229) | (0.532, 0.032, 0.016)→(0.532, 0.032, 0.016) | 0.234→0.234 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.601, 0.167, 0.229)→(0.599, 0.167, 0.314) | (0.532, 0.032, 0.016)→(0.532, 0.032, 0.016) | 0.234→0.234 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.414
- phase_score: 0.486
- phase_breakdown.grasp_object_score: 0.554
- phase_breakdown.reach_object_score: 0.452
- phase_breakdown.lift_clearance_score: 0.182
- phase_breakdown.place_goal_score: 0.622
- grasp_place_fitness: 0.682

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.682
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.414
- **Median Q (composite search score)**: -0.216
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.360


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
{"anchors":[{"name":"object","value":[0.64762,0.15808,0.1911]},{"name":"goal","value":[0.54431,0.00113,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.6281,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_z":0.18321,"approach_1.speed":0.35416,"approach_2.approach_goal_offset_z":0.15995,"approach_2.arc_height":0.16335,"approach_2.speed":0.36795,"descend_1.descend_offset_z":0.00591,"descend_1.speed":0.17711,"descend_2.place_offset_z":0.02072,"descend_2.speed":0.27326,"lift_1.lift_height":0.16899,"lift_1.speed":0.49272,"retract_1.speed":0.29017},"optimized_scores":{"best_composite_score":-0.21554,"best_fitness_score":0.56446,"best_task_score":0.1755},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3423.0,"contact_point_centroid":[0.53861,-0.0018,-0.0023],"force_p95":0.12511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86322,"mean_force":0.13553,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.55922,0.03179,0.31294]},{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.5422,0.00074,-0.00113],"force_p95":0.41584,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64496,"mean_force":0.06136,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52897,0.00084,0.03178]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7573.0,"contact_point_centroid":[0.53552,-0.01805,0.09363],"force_p95":0.11239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34179,"mean_force":0.07361,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53195,0.00074,0.09199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7645.0,"contact_point_centroid":[0.53519,0.01957,0.09216],"force_p95":0.11205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32304,"mean_force":0.07322,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53185,0.00075,0.09036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":388.0,"contact_point_centroid":[0.54253,-0.01959,0.17774],"force_p95":0.23112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27667,"mean_force":0.14629,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53699,-0.00139,0.18129]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":545.0,"contact_point_centroid":[0.54207,0.01601,0.17795],"force_p95":0.19625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2648,"mean_force":0.12057,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53644,-0.00183,0.18202]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13206,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15653,"mean_force":0.12537,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53138,0.00089,0.03149]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51663,0.00046,0.25826]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53596,0.00097,0.12804]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.53856,-0.00185,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63047,0.13604,0.28923]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53856,-0.00185,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63802,0.15231,0.21712]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.53856,-0.00185,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63455,0.15118,0.27576]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53105,-0.01833,0.03276],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11588,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53014,0.00087,0.03005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.531,0.01995,0.03187],"force_p95":0.06818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09552,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53014,0.00087,0.03005]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3403.0,"contact_point_centroid":[0.56198,0.03512,0.32253],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.0105,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56161,0.03512,0.32027]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1557.0,"contact_point_centroid":[0.63092,0.13612,0.29112],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63052,0.13611,0.28894]}],"total_contact_groups":17},"final_pose_error":0.01623,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.53856,-0.00185,0.01602],"final_tcp_position":[0.63494,0.15123,0.32018],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.75508,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53561,0.00094,0.21776],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53876,0.00103,0.04014],"tcp_start":[0.53561,0.00094,0.21776],"tcp_to_object_dist_end":0.01517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1301,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15653,"subtask_id":"grasp_object","tcp_end":[0.5301,0.00087,0.03002],"tcp_start":[0.53876,0.00103,0.04014],"tcp_to_object_dist_end":0.01467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55862,0.00082,0.1617],"object_pos_start":[0.54417,0.00074,0.02588],"object_to_goal_dist_end":0.18308,"object_to_goal_dist_start":0.25052,"object_z_max":0.16153,"peak_contact_force":0.1829,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15330.0,"raw_peak_contact_force":0.64496,"subtask_id":"lift_clearance","tcp_end":[0.53969,0.00069,0.17759],"tcp_start":[0.5301,0.00087,0.03002],"tcp_to_object_dist_end":0.02472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53856,-0.00185,0.01602],"object_pos_start":[0.55862,0.00082,0.1617],"object_to_goal_dist_end":0.26102,"object_to_goal_dist_start":0.18308,"object_z_max":0.16417,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7759.0,"raw_peak_contact_force":1.86322,"subtask_id":"place_goal","tcp_end":[0.62065,0.12018,0.36144],"tcp_start":[0.53969,0.00069,0.17759],"tcp_to_object_dist_end":0.37543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.53856,-0.00185,0.01602],"object_pos_start":[0.53856,-0.00185,0.01602],"object_to_goal_dist_end":0.26102,"object_to_goal_dist_start":0.26102,"object_z_max":0.01602,"peak_contact_force":9748.75508,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3025.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64178,0.15327,0.21801],"tcp_start":[0.62065,0.12018,0.36144],"tcp_to_object_dist_end":0.27481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53856,-0.00185,0.01602],"object_pos_start":[0.53856,-0.00185,0.01602],"object_to_goal_dist_end":0.26102,"object_to_goal_dist_start":0.26102,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63674,0.15188,0.23629],"tcp_start":[0.64178,0.15327,0.21801],"tcp_to_object_dist_end":0.286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":600.0,"object_pos_end":[0.53856,-0.00185,0.01602],"object_pos_start":[0.53856,-0.00185,0.01602],"object_to_goal_dist_end":0.26102,"object_to_goal_dist_start":0.26102,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63494,0.15123,0.32018],"tcp_start":[0.63674,0.15188,0.23629],"tcp_to_object_dist_end":0.35389,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.60153,0.17858,0.10809]},{"name":"goal","value":[0.5305,0.03079,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_z":0.15253,"approach_1.speed":0.2135,"approach_2.approach_goal_offset_z":0.07801,"approach_2.arc_height":0.14326,"approach_2.speed":0.26383,"descend_1.descend_offset_z":0.0091,"descend_1.speed":0.49815,"descend_2.place_offset_z":0.01603,"descend_2.speed":0.25263,"lift_1.lift_height":0.13404,"lift_1.speed":0.06995,"retract_1.speed":0.26042},"optimized_scores":{"best_composite_score":-0.09817,"best_fitness_score":0.68183,"best_task_score":0.41419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2366.0,"contact_point_centroid":[0.54931,0.09938,-0.00242],"force_p95":0.14113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65276,"mean_force":0.14095,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56722,0.11709,0.20592]},{"body_a":"world","body_b":"grasp_target","contact_count":193.0,"contact_point_centroid":[0.52777,0.02865,-0.00122],"force_p95":0.31355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54363,"mean_force":0.07544,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51519,0.02947,0.03547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16546.0,"contact_point_centroid":[0.52103,0.01055,0.08743],"force_p95":0.09395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30271,"mean_force":0.06134,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51863,0.02934,0.08607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16126.0,"contact_point_centroid":[0.52064,0.04828,0.08511],"force_p95":0.10227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30267,"mean_force":0.06381,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51838,0.02934,0.0836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3113.0,"contact_point_centroid":[0.53383,0.05955,0.16476],"force_p95":0.14321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30222,"mean_force":0.0983,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52846,0.04117,0.16641]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3201.0,"contact_point_centroid":[0.53339,0.02168,0.16331],"force_p95":0.14795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25713,"mean_force":0.09285,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5279,0.04,0.16469]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03056,-0.00211],"force_p95":0.15363,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2216,"mean_force":0.1309,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51796,0.02968,0.03527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.51752,0.01039,0.03668],"force_p95":0.0798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14456,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51675,0.0296,0.03391]},{"body_a":"world","body_b":"grasp_target","contact_count":1484.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51067,0.01328,0.24434]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5232,0.02866,0.11563]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.54926,0.09939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59243,0.16895,0.16066]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54926,0.09939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59039,0.17284,0.13104]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.54926,0.09939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5854,0.17121,0.19128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.51748,0.04873,0.03571],"force_p95":0.07239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08302,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51675,0.0296,0.03391]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2302.0,"contact_point_centroid":[0.5699,0.12149,0.2087],"force_p95":0.01125,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01519,"mean_force":0.01052,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.56948,0.12147,0.2064]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.5939,0.17386,0.12894],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59336,0.17384,0.12698]}],"total_contact_groups":17},"final_pose_error":0.01538,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.54926,0.09939,0.01602],"final_tcp_position":[0.58559,0.17123,0.23576],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273007.33934,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1484.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52375,0.02732,0.18902],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52514,0.03015,0.04353],"tcp_start":[0.52375,0.02732,0.18902],"tcp_to_object_dist_end":0.01832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02967,0.02564],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18448,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14741,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10850.0,"raw_peak_contact_force":0.2216,"subtask_id":"grasp_object","tcp_end":[0.51672,0.02959,0.03387],"tcp_start":[0.52514,0.03015,0.04353],"tcp_to_object_dist_end":0.01598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53731,0.0296,0.12618],"object_pos_start":[0.53041,0.02967,0.02564],"object_to_goal_dist_end":0.16323,"object_to_goal_dist_start":0.18448,"object_z_max":0.12608,"peak_contact_force":0.09768,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32865.0,"raw_peak_contact_force":0.54363,"subtask_id":"lift_clearance","tcp_end":[0.52533,0.02939,0.14496],"tcp_start":[0.51672,0.02959,0.03387],"tcp_to_object_dist_end":0.02228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54926,0.09939,0.01602],"object_pos_start":[0.53731,0.0296,0.12618],"object_to_goal_dist_end":0.13221,"object_to_goal_dist_start":0.16323,"object_z_max":0.16393,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10982.0,"raw_peak_contact_force":1.65276,"subtask_id":"place_goal","tcp_end":[0.5914,0.16456,0.1909],"tcp_start":[0.52533,0.02939,0.14496],"tcp_to_object_dist_end":0.19132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.54926,0.09939,0.01602],"object_pos_start":[0.54926,0.09939,0.01602],"object_to_goal_dist_end":0.13221,"object_to_goal_dist_start":0.13221,"object_z_max":0.01602,"peak_contact_force":273007.33934,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1497.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.5953,0.17429,0.13056],"tcp_start":[0.5914,0.16456,0.1909],"tcp_to_object_dist_end":0.1444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54926,0.09939,0.01602],"object_pos_start":[0.54926,0.09939,0.01602],"object_to_goal_dist_end":0.13221,"object_to_goal_dist_start":0.13221,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5886,0.17224,0.15081],"tcp_start":[0.5953,0.17429,0.13056],"tcp_to_object_dist_end":0.15819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":600.0,"object_pos_end":[0.54926,0.09939,0.01602],"object_pos_start":[0.54926,0.09939,0.01602],"object_to_goal_dist_end":0.13221,"object_to_goal_dist_start":0.13221,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58559,0.17123,0.23576],"tcp_start":[0.5886,0.17224,0.15081],"tcp_to_object_dist_end":0.23403,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.28814,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_z":0.15078,"approach_1.speed":0.24529,"approach_2.approach_goal_offset_z":0.07623,"approach_2.arc_height":0.24892,"approach_2.speed":0.45497,"descend_1.descend_offset_z":0.00668,"descend_1.speed":0.49718,"descend_2.place_offset_z":0.03136,"descend_2.speed":0.26584,"lift_1.lift_height":0.13888,"lift_1.speed":0.2481,"retract_1.speed":0.37763},"optimized_scores":{"best_composite_score":-0.23945,"best_fitness_score":0.54055,"best_task_score":0.12745},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3106.0,"contact_point_centroid":[0.50826,-0.00074,-0.0023],"force_p95":0.12665,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67257,"mean_force":0.13698,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52641,0.053,0.28624]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.50228,-0.01514,-0.00111],"force_p95":0.37691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60542,"mean_force":0.06507,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48948,-0.01532,0.03428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7675.0,"contact_point_centroid":[0.49503,0.00367,0.08398],"force_p95":0.10956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34609,"mean_force":0.07175,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49213,-0.01523,0.08178]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8328.0,"contact_point_centroid":[0.49495,-0.03404,0.08192],"force_p95":0.10599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31121,"mean_force":0.06707,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.492,-0.01524,0.08026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1349.0,"contact_point_centroid":[0.5027,0.00277,0.16072],"force_p95":0.18429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30221,"mean_force":0.10202,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49657,-0.01562,0.16178]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.5025,-0.03406,0.1605],"force_p95":0.18954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30145,"mean_force":0.10428,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49652,-0.01565,0.16164]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01554,-0.00203],"force_p95":0.133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16023,"mean_force":0.12556,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4919,-0.01536,0.03377]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49912,-0.00659,0.24537]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49819,-0.01455,0.11469]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.50819,-0.00075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57335,0.16189,0.30133]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50819,-0.00075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57834,0.17863,0.28038]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.50819,-0.00075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57597,0.17759,0.34077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49124,0.00386,0.0353],"force_p95":0.07622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1198,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01534,0.03254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.4913,-0.03442,0.03438],"force_p95":0.06853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08923,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01534,0.03254]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3071.0,"contact_point_centroid":[0.529,0.05791,0.29446],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.0105,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52861,0.05791,0.29214]},{"body_a":"left_finger","body_b":"right_finger","contact_count":955.0,"contact_point_centroid":[0.57383,0.16204,0.30336],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57341,0.16203,0.30115]}],"total_contact_groups":17},"final_pose_error":0.01492,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50819,-0.00075,0.01602],"final_tcp_position":[0.57638,0.17765,0.3853],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.97224,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49994,-0.01373,0.18962],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1680.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49888,-0.01544,0.04123],"tcp_start":[0.49994,-0.01373,0.18962],"tcp_to_object_dist_end":0.01599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01522,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13074,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.16023,"subtask_id":"grasp_object","tcp_end":[0.49071,-0.01534,0.03251],"tcp_start":[0.49888,-0.01544,0.04123],"tcp_to_object_dist_end":0.01459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.51603,-0.01514,0.13377],"object_pos_start":[0.5037,-0.01522,0.02587],"object_to_goal_dist_end":0.24319,"object_to_goal_dist_start":0.31208,"object_z_max":0.13361,"peak_contact_force":0.10914,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16148.0,"raw_peak_contact_force":0.60542,"subtask_id":"lift_clearance","tcp_end":[0.49905,-0.01517,0.15018],"tcp_start":[0.49071,-0.01534,0.03251],"tcp_to_object_dist_end":0.02361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50819,-0.00075,0.01602],"object_pos_start":[0.51603,-0.01514,0.13377],"object_to_goal_dist_end":0.30901,"object_to_goal_dist_start":0.24319,"object_z_max":0.15739,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8850.0,"raw_peak_contact_force":1.67257,"subtask_id":"place_goal","tcp_end":[0.5669,0.14517,0.32631],"tcp_start":[0.49905,-0.01517,0.15018],"tcp_to_object_dist_end":0.34788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.50819,-0.00075,0.01602],"object_pos_start":[0.50819,-0.00075,0.01602],"object_to_goal_dist_end":0.30901,"object_to_goal_dist_start":0.30901,"object_z_max":0.01602,"peak_contact_force":9748.97224,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1851.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.5811,0.17945,0.2795],"tcp_start":[0.5669,0.14517,0.32631],"tcp_to_object_dist_end":0.32743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50819,-0.00075,0.01602],"object_pos_start":[0.50819,-0.00075,0.01602],"object_to_goal_dist_end":0.30901,"object_to_goal_dist_start":0.30901,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57747,0.17822,0.30017],"tcp_start":[0.5811,0.17945,0.2795],"tcp_to_object_dist_end":0.34289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":600.0,"object_pos_end":[0.50819,-0.00075,0.01602],"object_pos_start":[0.50819,-0.00075,0.01602],"object_to_goal_dist_end":0.30901,"object_to_goal_dist_start":0.30901,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57638,0.17765,0.3853],"tcp_start":[0.57747,0.17822,0.30017],"tcp_to_object_dist_end":0.41575,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```