## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.2109 | 0.24 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1002 | 0.30 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0685 | 0.36 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1071 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.2164 | 0.17 | ❌ rejected |

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

## Current Skill (Q=-0.211) — your mutation base

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
  - 0.05
  weight: 0.3
- id: reach_goal
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp_1
  type: grasp
  control: position_control
  termination: force_exceeded
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    grasp_force_threshold:
      type: scalar
      range:
      - 0.1
      - 5.0
      default: 0.5
      binds_to:
      - path: termination.force_threshold
        mode: replace
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
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    lift_z:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach2_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
      mode: keep_current
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
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
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_z: status=consumed; consumers=target.offset.z (replace)
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach2_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.211
- **task_score** (E): 0.245
- **fitness_score**: 0.519  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1880 |
| descend_1 | 1.00 | 1.00 | 0.0827 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 0.67 | 1.00 | 0.1417 |
| approach_2 | 0.00 | 0.33 | 0.0001 |
| descend_2 | 0.33 | 1.00 | 0.1321 |
| release_1 | 1.00 | 1.00 | 0.0229 |
| retract_1 | 1.00 | 1.00 | 0.1332 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.001, 0.117) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, -0.001, 0.117)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.143 | 0.211 |
| lift_1 | lift | 0.67 / step_budget | (0.466, -0.001, 0.027)→(0.472, -0.001, 0.168) | (0.479, -0.001, 0.026)→(0.494, 0.003, 0.094) | 0.278→0.241 | 1.00 / 25.333 | 91001.759 | 1.019 |
| approach_2 | approach | 0.00 / guard_failure | (0.492, 0.051, 0.207)→(0.492, 0.051, 0.207) | (0.494, 0.003, 0.094)→(0.512, 0.058, 0.118) | 0.241→0.185 | 0.33 / 2.667 | 3249.491 | 0.233 |
| descend_2 | descend | 0.33 / step_budget | (0.492, 0.051, 0.207)→(0.560, 0.147, 0.159) | (0.513, 0.059, 0.117)→(0.513, 0.071, 0.016) | 0.184→0.226 | 1.00 / 8.000 | 0.123 | 1.329 |
| release_1 | release | 1.00 / step_budget | (0.560, 0.147, 0.159)→(0.554, 0.146, 0.181) | (0.513, 0.071, 0.016)→(0.513, 0.071, 0.016) | 0.226→0.226 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.554, 0.146, 0.181)→(0.603, 0.199, 0.284) | (0.513, 0.071, 0.016)→(0.513, 0.071, 0.016) | 0.226→0.226 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.409
- phase_score: 0.702
- phase_breakdown.reach_object_score: 0.429
- phase_breakdown.reach_goal_score: 0.819
- grasp_place_fitness: 0.683

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.683
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.409
- **Median Q (composite search score)**: -0.165
- **K-run variance**: 0.0244
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.326


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80282,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.2963,"approach_1.approach_z":0.09112,"approach_2.approach2_z":0.1089,"approach_2.transport_speed":0.38467,"descend_1.descend_speed":0.09816,"descend_2.place_speed":0.09227,"grasp_1.grasp_force_threshold":0.19483,"lift_1.lift_speed":0.05727,"lift_1.lift_z":0.24277,"release_1.release_duration":0.51088,"retract_1.retract_speed":0.41124},"optimized_scores":{"best_composite_score":-0.04656,"best_fitness_score":0.68344,"best_task_score":0.40854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1259.0,"contact_point_centroid":[0.54847,0.21885,-0.00288],"force_p95":0.44198,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98552,"mean_force":0.16069,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54914,0.21568,0.16603]},{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.49701,0.04205,-0.00125],"force_p95":0.45447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66419,"mean_force":0.09926,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4864,0.04321,0.02773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19728.0,"contact_point_centroid":[0.48703,0.06211,0.075],"force_p95":0.0768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31379,"mean_force":0.05197,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4866,0.043,0.07324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19346.0,"contact_point_centroid":[0.48716,0.02388,0.07736],"force_p95":0.07803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29738,"mean_force":0.05212,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4867,0.043,0.07527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9228.0,"contact_point_centroid":[0.5099,0.08052,0.15394],"force_p95":0.14535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28571,"mean_force":0.07856,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50717,0.09948,0.15347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12112.0,"contact_point_centroid":[0.51159,0.12319,0.1568],"force_p95":0.10086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28448,"mean_force":0.06295,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5091,0.10463,0.15683]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04467,-0.00215],"force_p95":0.16707,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25111,"mean_force":0.13453,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48922,0.0435,0.02716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4045.0,"contact_point_centroid":[0.48862,0.02419,0.02875],"force_p95":0.08193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14844,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48805,0.04339,0.02594]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49765,0.02033,0.21409]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49538,0.04259,0.08159]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54825,0.21895,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55378,0.23582,0.14568]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.54825,0.21895,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55507,0.23827,0.21845]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5026.0,"contact_point_centroid":[0.4886,0.06258,0.02776],"force_p95":0.07445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08689,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48806,0.04339,0.02595]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1141.0,"contact_point_centroid":[0.55101,0.21911,0.16478],"force_p95":0.01259,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.0107,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5505,0.21908,0.16256]},{"body_a":"left_finger","body_b":"right_finger","contact_count":234.0,"contact_point_centroid":[0.55694,0.23717,0.14375],"force_p95":0.01084,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.00962,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55651,0.23714,0.14147]}],"total_contact_groups":15},"final_pose_error":0.0176,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54825,0.21895,0.01602],"final_tcp_position":[0.56132,0.24303,0.27955],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.98552,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49713,0.04129,0.12929],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49617,0.04413,0.03455],"tcp_start":[0.49713,0.04129,0.12929],"tcp_to_object_dist_end":0.00993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.04339,0.0255],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24354,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15721,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10871.0,"raw_peak_contact_force":0.25111,"tcp_end":[0.48803,0.04339,0.02591],"tcp_start":[0.49617,0.04413,0.03455],"tcp_to_object_dist_end":0.01305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49934,0.04303,0.11083],"object_pos_start":[0.50107,0.04339,0.0255],"object_to_goal_dist_end":0.21509,"object_to_goal_dist_start":0.24354,"object_z_max":0.11074,"peak_contact_force":0.06946,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39268.0,"raw_peak_contact_force":0.66419,"subtask_id":"reach_object","tcp_end":[0.48923,0.04302,0.1205],"tcp_start":[0.48803,0.04339,0.02591],"tcp_to_object_dist_end":0.01399,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.54845,0.187,0.17587],"object_pos_start":[0.49934,0.04303,0.11083],"object_to_goal_dist_end":0.06671,"object_to_goal_dist_start":0.21509,"object_z_max":0.18059,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21340.0,"raw_peak_contact_force":0.28571,"subtask_id":"reach_goal","tcp_end":[0.53777,0.18176,0.20673],"tcp_start":[0.53777,0.18166,0.20677],"tcp_to_object_dist_end":0.03307,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.54825,0.21895,0.01602],"object_pos_start":[0.54893,0.18928,0.17258],"object_to_goal_dist_end":0.13428,"object_to_goal_dist_start":0.06321,"object_z_max":0.17258,"peak_contact_force":0.12262,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2400.0,"raw_peak_contact_force":1.98552,"subtask_id":"reach_goal","tcp_end":[0.55809,0.23756,0.14436],"tcp_start":[0.53777,0.18176,0.20673],"tcp_to_object_dist_end":0.13006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54825,0.21895,0.01602],"object_pos_start":[0.54825,0.21895,0.01602],"object_to_goal_dist_end":0.13428,"object_to_goal_dist_start":0.13428,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1034.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55216,0.23505,0.1656],"tcp_start":[0.55809,0.23756,0.14436],"tcp_to_object_dist_end":0.1505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.54825,0.21895,0.01602],"object_pos_start":[0.54825,0.21895,0.01602],"object_to_goal_dist_end":0.13428,"object_to_goal_dist_start":0.13428,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56132,0.24303,0.27955],"tcp_start":[0.55216,0.23505,0.1656],"tcp_to_object_dist_end":0.26495,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.29752,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.24121,"approach_1.approach_z":0.07141,"approach_2.approach2_z":0.31632,"approach_2.transport_speed":0.23917,"descend_1.descend_speed":0.221,"descend_2.place_speed":0.07989,"grasp_1.grasp_force_threshold":0.1846,"lift_1.lift_speed":0.25059,"lift_1.lift_z":0.15487,"release_1.release_duration":0.39808,"retract_1.retract_speed":0.31401},"optimized_scores":{"best_composite_score":-0.1653,"best_fitness_score":0.5647,"best_task_score":0.16904},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3714.0,"contact_point_centroid":[0.498,0.00748,-0.00226],"force_p95":0.12518,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87372,"mean_force":0.13498,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52913,0.05079,0.18608]},{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.47386,-0.01926,-0.00112],"force_p95":0.50975,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69277,"mean_force":0.06641,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46267,-0.0196,0.02878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7978.0,"contact_point_centroid":[0.46774,-0.0006,0.08747],"force_p95":0.10944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31958,"mean_force":0.06968,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46514,-0.01954,0.08523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8588.0,"contact_point_centroid":[0.46759,-0.03841,0.08516],"force_p95":0.10664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30058,"mean_force":0.06559,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46499,-0.01954,0.08347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1646.0,"contact_point_centroid":[0.48215,0.00655,0.1748],"force_p95":0.17394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2953,"mean_force":0.10905,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47653,-0.01166,0.17718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1553.0,"contact_point_centroid":[0.48155,-0.03092,0.1735],"force_p95":0.18992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27744,"mean_force":0.11277,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47582,-0.01259,0.17561]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00204],"force_p95":0.1366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1861,"mean_force":0.1265,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46484,-0.01965,0.02806]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48627,-0.00914,0.20518]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47156,-0.01915,0.07256]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49797,0.00749,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56027,0.08845,0.18661]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.49797,0.00749,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59009,0.1203,0.26128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.46352,-0.00038,0.02988],"force_p95":0.06637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09308,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46372,-0.01963,0.02696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.46338,-0.03888,0.02937],"force_p95":0.06485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08809,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46373,-0.01963,0.02697]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3677.0,"contact_point_centroid":[0.53176,0.0534,0.18822],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.01062,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5315,0.0534,0.18594]},{"body_a":"left_finger","body_b":"right_finger","contact_count":215.0,"contact_point_centroid":[0.56335,0.08897,0.18418],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01035,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56289,0.08897,0.18192]}],"total_contact_groups":15},"final_pose_error":0.01925,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.49797,0.00749,0.01602],"final_tcp_position":[0.62507,0.15396,0.32262],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.87372,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47388,-0.01858,0.1108],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47152,-0.0198,0.0347],"tcp_start":[0.47388,-0.01858,0.1108],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01965,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13462,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.1861,"tcp_end":[0.4637,-0.01963,0.02693],"tcp_start":[0.47152,-0.0198,0.0347],"tcp_to_object_dist_end":0.01239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49139,-0.01963,0.15321],"object_pos_start":[0.47603,-0.01965,0.02583],"object_to_goal_dist_end":0.23008,"object_to_goal_dist_start":0.28825,"object_z_max":0.15303,"peak_contact_force":0.07835,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16675.0,"raw_peak_contact_force":0.69277,"subtask_id":"reach_object","tcp_end":[0.47181,-0.01955,0.16557],"tcp_start":[0.4637,-0.01963,0.02693],"tcp_to_object_dist_end":0.02316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.49646,0.00053,0.16236],"object_pos_start":[0.49139,-0.01963,0.15321],"object_to_goal_dist_end":0.21012,"object_to_goal_dist_start":0.23008,"object_z_max":0.16794,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3199.0,"raw_peak_contact_force":0.2953,"subtask_id":"reach_goal","tcp_end":[0.48398,-0.00227,0.19332],"tcp_start":[0.48399,-0.0023,0.19331],"tcp_to_object_dist_end":0.0335,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49797,0.00749,0.01602],"object_pos_start":[0.49656,0.00092,0.16115],"object_to_goal_dist_end":0.26664,"object_to_goal_dist_start":0.20993,"object_z_max":0.16115,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7391.0,"raw_peak_contact_force":1.87372,"subtask_id":"reach_goal","tcp_end":[0.56419,0.089,0.1844],"tcp_start":[0.48398,-0.00227,0.19332],"tcp_to_object_dist_end":0.19845,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49797,0.00749,0.01602],"object_pos_start":[0.49797,0.00749,0.01602],"object_to_goal_dist_end":0.26664,"object_to_goal_dist_start":0.26664,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1015.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55874,0.08816,0.20687],"tcp_start":[0.56419,0.089,0.1844],"tcp_to_object_dist_end":0.21593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49797,0.00749,0.01602],"object_pos_start":[0.49797,0.00749,0.01602],"object_to_goal_dist_end":0.26664,"object_to_goal_dist_start":0.26664,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62507,0.15396,0.32262],"tcp_start":[0.55874,0.08816,0.20687],"tcp_to_object_dist_end":0.36278,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.41441,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.30928,"approach_1.approach_z":0.07248,"approach_2.approach2_z":0.25106,"approach_2.transport_speed":0.11687,"descend_1.descend_speed":0.09685,"descend_2.place_speed":0.14964,"grasp_1.grasp_force_threshold":0.0802,"lift_1.lift_speed":0.23471,"lift_1.lift_z":0.21235,"release_1.release_duration":0.81865,"retract_1.retract_speed":0.33223},"optimized_scores":{"best_composite_score":-0.42089,"best_fitness_score":0.30911,"best_task_score":0.15644},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":384.0,"contact_point_centroid":[0.48283,-0.01633,-0.00435],"force_p95":0.9527,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70084,"mean_force":0.23673,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45174,-0.02549,0.1577]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5737.0,"contact_point_centroid":[0.44938,-0.00654,0.08255],"force_p95":0.12641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33494,"mean_force":0.07305,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44659,-0.02545,0.0804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6081.0,"contact_point_centroid":[0.44917,-0.04434,0.08001],"force_p95":0.12359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30078,"mean_force":0.06971,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44647,-0.02545,0.07842]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02615,-0.00206],"force_p95":0.14135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19436,"mean_force":0.12766,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44779,-0.02562,0.02883]},{"body_a":"world","body_b":"grasp_target","contact_count":1972.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47828,-0.01192,0.20586]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49235,-0.01275,-0.00198],"force_p95":0.12302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1287,"mean_force":0.12256,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50788,0.04912,0.18032]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45488,-0.02499,0.0734]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49235,-0.01274,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55313,0.11493,0.15097]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.49235,-0.01274,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58495,0.15679,0.20713]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.49235,-0.01277,-0.00172],"force_p95":0.11876,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.11938,"mean_force":0.10416,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.45504,-0.02549,0.21951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4814.0,"contact_point_centroid":[0.44674,-0.00636,0.03019],"force_p95":0.06828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09829,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44671,-0.02558,0.02781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5175.0,"contact_point_centroid":[0.44659,-0.04481,0.02968],"force_p95":0.06714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08216,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44672,-0.02558,0.02781]},{"body_a":"left_finger","body_b":"right_finger","contact_count":29.0,"contact_point_centroid":[0.45536,-0.02549,0.21996],"force_p95":0.01638,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01485,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45487,-0.02549,0.2182]},{"body_a":"left_finger","body_b":"right_finger","contact_count":14.0,"contact_point_centroid":[0.45635,-0.02549,0.22025],"force_p95":0.01361,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01361,"mean_force":0.01243,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.45504,-0.02549,0.21951]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4214.0,"contact_point_centroid":[0.50817,0.0491,0.18265],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01316,"mean_force":0.01059,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50787,0.0491,0.18033]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.55622,0.11564,0.14835],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01027,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55592,0.11564,0.14611]}],"total_contact_groups":16},"final_pose_error":0.01829,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.49235,-0.01274,0.01602],"final_tcp_position":[0.62237,0.20105,0.24918],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273013.08854,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1972.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45772,-0.02426,0.11203],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45428,-0.02584,0.03501],"tcp_start":[0.45772,-0.02426,0.11203],"tcp_to_object_dist_end":0.00997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02562,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30325,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13835,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11789.0,"raw_peak_contact_force":0.19436,"tcp_end":[0.44669,-0.02557,0.02778],"tcp_start":[0.45428,-0.02584,0.03501],"tcp_to_object_dist_end":0.01192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":555.0,"n_steps_budget":600.0,"object_pos_end":[0.49233,-0.01302,0.01653],"object_pos_start":[0.45844,-0.02562,0.02578],"object_to_goal_dist_end":0.27831,"object_to_goal_dist_start":0.30325,"object_z_max":0.14845,"peak_contact_force":273005.12931,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12231.0,"raw_peak_contact_force":1.70084,"subtask_id":"reach_object","tcp_end":[0.45496,-0.02549,0.21937],"tcp_start":[0.44669,-0.02557,0.02778],"tcp_to_object_dist_end":0.20663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49233,-0.01298,0.01656],"object_pos_start":[0.49233,-0.01302,0.01653],"object_to_goal_dist_end":0.27827,"object_to_goal_dist_start":0.27831,"object_z_max":0.01659,"peak_contact_force":9748.47302,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26.0,"raw_peak_contact_force":0.11938,"subtask_id":"reach_goal","tcp_end":[0.45516,-0.02549,0.21968],"tcp_start":[0.45514,-0.02549,0.21963],"tcp_to_object_dist_end":0.20687,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49235,-0.01274,0.01602],"object_pos_start":[0.49233,-0.01291,0.01661],"object_to_goal_dist_end":0.27826,"object_to_goal_dist_start":0.27819,"object_z_max":0.01664,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8214.0,"raw_peak_contact_force":0.1287,"subtask_id":"reach_goal","tcp_end":[0.55764,0.11568,0.14875],"tcp_start":[0.45516,-0.02549,0.21968],"tcp_to_object_dist_end":0.19589,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49235,-0.01274,0.01602],"object_pos_start":[0.49235,-0.01274,0.01602],"object_to_goal_dist_end":0.27826,"object_to_goal_dist_start":0.27826,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55147,0.11453,0.17132],"tcp_start":[0.55764,0.11568,0.14875],"tcp_to_object_dist_end":0.20932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49235,-0.01274,0.01602],"object_pos_start":[0.49235,-0.01274,0.01602],"object_to_goal_dist_end":0.27826,"object_to_goal_dist_start":0.27826,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62237,0.20105,0.24918],"tcp_start":[0.55147,0.11453,0.17132],"tcp_to_object_dist_end":0.34202,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```