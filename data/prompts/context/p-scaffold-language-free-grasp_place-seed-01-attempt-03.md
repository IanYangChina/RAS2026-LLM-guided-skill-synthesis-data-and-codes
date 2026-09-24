## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4387 | 0.79 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2393 | 0.40 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3429 | 0.34 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3438 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.791, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.439) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: subtask_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: subtask_lift
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: subtask_place
  target_entity: object
  metric: goal_progress
  weight: 0.5
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_approach
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
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
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
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_success
    when: after_phase
    predicate: object_lifted
    args:
      z_threshold: 0.08
    threshold: 0.08
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: subtask_lift
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
    approach_goal_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_goal
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
    place_offset_z:
      type: scalar
      range:
      - -0.05
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: subtask_place

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_success, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.08, args={'z_threshold': 0.08}
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.439
- **task_score** (E): 0.791
- **fitness_score**: 0.859  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0531 |
| descend_1 | 1.00 | 1.00 | 0.2038 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 1.00 | 0.1900 |
| approach_goal | 1.00 | 1.00 | 0.2323 |
| descend_goal | 1.00 | 1.00 | 0.0827 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.483, -0.002, 0.258) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.483, -0.002, 0.258)→(0.475, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.475, -0.001, 0.055)→(0.467, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.153 | 0.206 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.001, 0.047)→(0.475, -0.001, 0.236) | (0.479, -0.001, 0.026)→(0.481, -0.001, 0.211) | 0.278→0.253 | 1.00 / 36.333 | 55983.966 | 0.392 |
| approach_goal | approach | 1.00 / step_budget | (0.475, -0.001, 0.236)→(0.598, 0.191, 0.257) | (0.481, -0.001, 0.211)→(0.600, 0.190, 0.225) | 0.253→0.077 | 1.00 / 28.000 | 0.113 | 0.177 |
| descend_goal | descend | 1.00 / step_budget | (0.598, 0.191, 0.257)→(0.603, 0.199, 0.175) | (0.600, 0.190, 0.225)→(0.601, 0.205, 0.115) | 0.077→0.045 | 1.00 / 23.333 | 3249.024 | 0.794 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.291
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.567
- phase_breakdown.subtask_approach_score: 0.146
- phase_breakdown.subtask_lift_score: 0.502
- phase_breakdown.subtask_place_score: 0.774
- grasp_place_fitness: 0.964

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.964
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.475
- **K-run variance**: 0.0109
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.532


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41473,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24913,"approach_goal.approach_goal_offset_z":0.12047,"descend_1.depth":0.01649,"descend_goal.place_offset_z":-0.01334,"lift_1.lift_height":0.20907,"lift_1.lift_speed":0.03333},"optimized_scores":{"best_composite_score":0.47515,"best_fitness_score":0.89515,"best_task_score":0.85565},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.49769,0.04262,-0.00163],"force_p95":0.39536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41948,"mean_force":0.16562,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48769,0.04277,0.0433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12477.0,"contact_point_centroid":[0.49114,0.062,0.12973],"force_p95":0.07822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26456,"mean_force":0.05221,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49105,0.04284,0.12787]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04486,-0.00218],"force_p95":0.17206,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23539,"mean_force":0.13591,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48986,0.04297,0.04353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12540.0,"contact_point_centroid":[0.49082,0.02368,0.12835],"force_p95":0.0763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22473,"mean_force":0.05115,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49095,0.04283,0.12644]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3539.0,"contact_point_centroid":[0.55811,0.25337,0.21076],"force_p95":0.09244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19222,"mean_force":0.05756,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55805,0.23442,0.21007]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3604.0,"contact_point_centroid":[0.55787,0.21552,0.20693],"force_p95":0.09592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16443,"mean_force":0.0575,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55815,0.23482,0.20555]},{"body_a":"world","body_b":"grasp_target","contact_count":300.0,"contact_point_centroid":[0.50118,0.04505,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12447,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49916,0.01157,0.29252]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5036.0,"contact_point_centroid":[0.48853,0.02361,0.04525],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12416,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48873,0.04287,0.04231]},{"body_a":"world","body_b":"grasp_target","contact_count":2864.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49667,0.0347,0.16586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11151.0,"contact_point_centroid":[0.52656,0.12025,0.23702],"force_p95":0.07424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09224,"mean_force":0.05123,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52705,0.13949,0.23426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13611.0,"contact_point_centroid":[0.52648,0.15752,0.23572],"force_p95":0.06528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08458,"mean_force":0.04298,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52667,0.13841,0.23397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5564.0,"contact_point_centroid":[0.48838,0.06222,0.04466],"force_p95":0.0717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07493,"mean_force":0.0408,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48873,0.04287,0.04231]}],"total_contact_groups":12},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55378,0.23897,0.1268],"final_tcp_position":[0.55988,0.24023,0.15207],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":76.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02594],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24192,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12235,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":300.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.4988,0.02593,0.28374],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02594],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24192,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2864.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.49665,0.04356,0.05095],"tcp_start":[0.4988,0.02593,0.28374],"tcp_to_object_dist_end":0.02539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.0435,0.02537],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24349,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16515,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12400.0,"raw_peak_contact_force":0.23539,"tcp_end":[0.4887,0.04287,0.04227],"tcp_start":[0.49665,0.04356,0.05095],"tcp_to_object_dist_end":0.02101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":617.0,"n_steps_budget":1000.0,"object_pos_end":[0.50503,0.04333,0.19453],"object_pos_start":[0.50116,0.0435,0.02537],"object_to_goal_dist_end":0.21546,"object_to_goal_dist_start":0.24349,"object_z_max":0.19426,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25115.0,"raw_peak_contact_force":0.41948,"subtask_id":"subtask_lift","tcp_end":[0.49712,0.04316,0.21512],"tcp_start":[0.4887,0.04287,0.04227],"tcp_to_object_dist_end":0.02206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.56222,0.23,0.23224],"object_pos_start":[0.50503,0.04333,0.19453],"object_to_goal_dist_end":0.08678,"object_to_goal_dist_start":0.21546,"object_z_max":0.23219,"peak_contact_force":0.07071,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24762.0,"raw_peak_contact_force":0.09224,"tcp_end":[0.55738,0.23002,0.25604],"tcp_start":[0.49712,0.04316,0.21512],"tcp_to_object_dist_end":0.02428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.55378,0.23897,0.1268],"object_pos_start":[0.56222,0.23,0.23224],"object_to_goal_dist_end":0.02338,"object_to_goal_dist_start":0.08678,"object_z_max":0.23224,"peak_contact_force":0.09358,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7143.0,"raw_peak_contact_force":0.19222,"subtask_id":"subtask_place","tcp_end":[0.55988,0.24023,0.15207],"tcp_start":[0.55738,0.23002,0.25604],"tcp_to_object_dist_end":0.02602,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47303,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18602,"approach_goal.approach_goal_offset_z":0.09921,"descend_1.depth":0.01866,"descend_goal.place_offset_z":0.02278,"lift_1.lift_height":0.25811,"lift_1.lift_speed":0.04313},"optimized_scores":{"best_composite_score":0.54413,"best_fitness_score":0.96413,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.47286,-0.01928,-0.00147],"force_p95":0.39376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42175,"mean_force":0.15202,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46369,-0.01945,0.047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15310.0,"contact_point_centroid":[0.46698,-0.03846,0.15564],"force_p95":0.07685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24311,"mean_force":0.05152,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46681,-0.01944,0.15407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13120.0,"contact_point_centroid":[0.46763,-0.00026,0.15932],"force_p95":0.08304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24069,"mean_force":0.0585,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.467,-0.01945,0.15776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1499.0,"contact_point_centroid":[0.61961,0.13129,0.25686],"force_p95":0.12587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23256,"mean_force":0.07485,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62144,0.15019,0.258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.61993,0.16917,0.25594],"force_p95":0.12936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22787,"mean_force":0.07749,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62153,0.1503,0.25714]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02011,-0.00207],"force_p95":0.14229,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19134,"mean_force":0.12778,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4657,-0.01949,0.04706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13733.0,"contact_point_centroid":[0.54521,0.04549,0.27031],"force_p95":0.071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1515,"mean_force":0.04652,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54563,0.06454,0.27005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11334.0,"contact_point_centroid":[0.54624,0.08389,0.2708],"force_p95":0.07682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14732,"mean_force":0.05495,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54576,0.06469,0.27007]},{"body_a":"world","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.47616,-0.02015,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49068,-0.00676,0.26885]},{"body_a":"world","body_b":"grasp_target","contact_count":2244.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47525,-0.01707,0.1428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4837.0,"contact_point_centroid":[0.46421,-0.00016,0.04713],"force_p95":0.06982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10608,"mean_force":0.0453,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46461,-0.01946,0.04596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5886.0,"contact_point_centroid":[0.4646,-0.03866,0.04816],"force_p95":0.06203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07882,"mean_force":0.03765,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46461,-0.01946,0.04596]}],"total_contact_groups":12},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62376,0.15352,0.20051],"final_tcp_position":[0.62471,0.15399,0.23058],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.42175,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":532.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.48064,-0.01457,0.23438],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2244.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.47227,-0.01964,0.05379],"tcp_start":[0.48064,-0.01457,0.23438],"tcp_to_object_dist_end":0.02805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01962,0.02574],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14175,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12523.0,"raw_peak_contact_force":0.19134,"tcp_end":[0.46458,-0.01946,0.04593],"tcp_start":[0.47227,-0.01964,0.05379],"tcp_to_object_dist_end":0.02323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.47866,-0.01968,0.23965],"object_pos_start":[0.47609,-0.01962,0.02574],"object_to_goal_dist_end":0.24041,"object_to_goal_dist_start":0.28825,"object_z_max":0.23937,"peak_contact_force":0.07102,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28515.0,"raw_peak_contact_force":0.42175,"subtask_id":"subtask_lift","tcp_end":[0.47276,-0.01953,0.2643],"tcp_start":[0.46458,-0.01946,0.04593],"tcp_to_object_dist_end":0.02535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.62033,0.14657,0.25056],"object_pos_start":[0.47866,-0.01968,0.23965],"object_to_goal_dist_end":0.06284,"object_to_goal_dist_start":0.24041,"object_z_max":0.25081,"peak_contact_force":0.07948,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25067.0,"raw_peak_contact_force":0.1515,"tcp_end":[0.61903,0.14689,0.27968],"tcp_start":[0.47276,-0.01953,0.2643],"tcp_to_object_dist_end":0.02914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":92.0,"n_steps_budget":1000.0,"object_pos_end":[0.62376,0.15352,0.20051],"object_pos_start":[0.62033,0.14657,0.25056],"object_to_goal_dist_end":0.01418,"object_to_goal_dist_start":0.06284,"object_z_max":0.25056,"peak_contact_force":0.09817,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2891.0,"raw_peak_contact_force":0.23256,"subtask_id":"subtask_place","tcp_end":[0.62471,0.15399,0.23058],"tcp_start":[0.61903,0.14689,0.27968],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57826,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21132,"approach_goal.approach_goal_offset_z":0.12929,"descend_1.depth":0.02368,"descend_goal.place_offset_z":0.00897,"lift_1.lift_height":0.22386,"lift_1.lift_speed":0.04871},"optimized_scores":{"best_composite_score":0.2967,"best_fitness_score":0.7167,"best_task_score":0.51877},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":249.0,"contact_point_centroid":[0.62482,0.21989,-0.00663],"force_p95":1.72959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95583,"mean_force":0.39401,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62221,0.2016,0.16118]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.45638,-0.02479,-0.00148],"force_p95":0.27517,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33599,"mean_force":0.07187,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44681,-0.02532,0.05278]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7105.0,"contact_point_centroid":[0.45007,-0.00645,0.13565],"force_p95":0.11882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29983,"mean_force":0.08425,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44951,-0.02527,0.138]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9043.0,"contact_point_centroid":[0.44852,-0.04385,0.1329],"force_p95":0.10832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29106,"mean_force":0.06897,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44932,-0.02527,0.13484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9030.0,"contact_point_centroid":[0.53572,0.06568,0.22656],"force_p95":0.11715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28847,"mean_force":0.0814,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53492,0.08422,0.23026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8511.0,"contact_point_centroid":[0.53543,0.1029,0.2264],"force_p95":0.12107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25256,"mean_force":0.08525,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53499,0.08432,0.23025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.61499,0.17844,0.22831],"force_p95":0.1873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24241,"mean_force":0.05551,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61841,0.19532,0.23399]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02626,-0.0021],"force_p95":0.15231,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19088,"mean_force":0.13008,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44888,-0.0254,0.05259]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3616.0,"contact_point_centroid":[0.44976,-0.00626,0.05065],"force_p95":0.1021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13935,"mean_force":0.05921,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44783,-0.02536,0.05156]},{"body_a":"world","body_b":"grasp_target","contact_count":444.0,"contact_point_centroid":[0.45856,-0.02632,-0.00172],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12374,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48555,-0.00836,0.27885]},{"body_a":"world","body_b":"grasp_target","contact_count":2456.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46123,-0.02184,0.15578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4503.0,"contact_point_centroid":[0.4483,-0.04418,0.05121],"force_p95":0.07781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08005,"mean_force":0.04728,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44783,-0.02536,0.05156]},{"body_a":"left_finger","body_b":"right_finger","contact_count":103.0,"contact_point_centroid":[0.62347,0.20293,0.15116],"force_p95":0.0156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01293,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62322,0.20291,0.14882]}],"total_contact_groups":13},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62633,0.22346,0.01694],"final_tcp_position":[0.62383,0.20372,0.14136],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9746.87958,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12243,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":444.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.46953,-0.01815,0.25532],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2456.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.45521,-0.02562,0.05887],"tcp_start":[0.46953,-0.01815,0.25532],"tcp_to_object_dist_end":0.03302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02549,0.02556],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30318,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15294,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9919.0,"raw_peak_contact_force":0.19088,"tcp_end":[0.4478,-0.02536,0.05153],"tcp_start":[0.45521,-0.02562,0.05887],"tcp_to_object_dist_end":0.02808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.45787,-0.02561,0.1979],"object_pos_start":[0.45849,-0.02549,0.02556],"object_to_goal_dist_end":0.30227,"object_to_goal_dist_start":0.30318,"object_z_max":0.19761,"peak_contact_force":0.09551,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16234.0,"raw_peak_contact_force":0.33599,"subtask_id":"subtask_lift","tcp_end":[0.45481,-0.02534,0.22984],"tcp_start":[0.4478,-0.02536,0.05153],"tcp_to_object_dist_end":0.03209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.61701,0.19286,0.19238],"object_pos_start":[0.45787,-0.02561,0.1979],"object_to_goal_dist_end":0.08082,"object_to_goal_dist_start":0.30227,"object_z_max":0.19811,"peak_contact_force":0.1892,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17541.0,"raw_peak_contact_force":0.28847,"tcp_end":[0.61836,0.19493,0.23447],"tcp_start":[0.45481,-0.02534,0.22984],"tcp_to_object_dist_end":0.04217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.62633,0.22346,0.01694],"object_pos_start":[0.61701,0.19286,0.19238],"object_to_goal_dist_end":0.09844,"object_to_goal_dist_start":0.08082,"object_z_max":0.19238,"peak_contact_force":9746.87958,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":392.0,"raw_peak_contact_force":1.95583,"subtask_id":"subtask_place","tcp_end":[0.62383,0.20372,0.14136],"tcp_start":[0.61836,0.19493,0.23447],"tcp_to_object_dist_end":0.12601,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```