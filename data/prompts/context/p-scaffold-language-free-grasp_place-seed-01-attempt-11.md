## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3717 | 0.72 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4772 | 0.84 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5606 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5609 | 1.00 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5571 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.372) — your mutation base

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
  - 0.1
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
    - 0.01
    tolerance: 0.008
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.01
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.03
      - 0.05
      default: 0.0
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01], tolerance=0.008
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.372
- **task_score** (E): 0.723
- **fitness_score**: 0.842  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0843 |
| descend_1 | 1.00 | 1.00 | 0.1954 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |
| lift_1 | 1.00 | 1.00 | 0.1998 |
| approach_goal | 1.00 | 1.00 | 0.2681 |
| descend_goal | 1.00 | 1.00 | 0.0885 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.482, -0.002, 0.231) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.124 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.482, -0.002, 0.231)→(0.474, -0.001, 0.036) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.036)→(0.467, -0.001, 0.028) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.148 | 0.225 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.001, 0.028)→(0.475, -0.001, 0.228) | (0.479, -0.001, 0.026)→(0.487, -0.001, 0.219) | 0.278→0.264 | 1.00 / 35.000 | 0.087 | 0.591 |
| approach_goal | approach | 1.00 / step_budget | (0.475, -0.001, 0.228)→(0.598, 0.190, 0.256) | (0.487, -0.001, 0.219)→(0.567, 0.143, 0.124) | 0.264→0.122 | 1.00 / 20.333 | 0.127 | 0.908 |
| descend_goal | descend | 1.00 / step_budget | (0.598, 0.190, 0.256)→(0.603, 0.199, 0.169) | (0.567, 0.143, 0.124)→(0.569, 0.148, 0.098) | 0.122→0.097 | 1.00 / 19.000 | 0.129 | 0.307 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.575
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.493
- phase_breakdown.subtask_approach_score: 0.144
- phase_breakdown.subtask_lift_score: 0.135
- phase_breakdown.subtask_place_score: 0.848
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.509
- **K-run variance**: 0.0385
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.494


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26556,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24564,"approach_goal.approach_goal_offset_z":0.05001,"approach_goal.arc_height":0.19676,"descend_1.depth":0.0046,"descend_goal.place_offset_z":0.02155,"lift_1.lift_height":0.15603,"lift_1.lift_speed":0.03006},"optimized_scores":{"best_composite_score":0.50927,"best_fitness_score":0.97927,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.4975,0.04224,-0.00165],"force_p95":0.50042,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51299,"mean_force":0.21388,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48743,0.04294,0.0292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":593.0,"contact_point_centroid":[0.56094,0.24982,0.18822],"force_p95":0.19505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45146,"mean_force":0.11603,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55659,0.23166,0.19124]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":443.0,"contact_point_centroid":[0.56108,0.21328,0.18915],"force_p95":0.20423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44876,"mean_force":0.13561,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55651,0.2314,0.19201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8230.0,"contact_point_centroid":[0.51898,0.08886,0.20717],"force_p95":0.12101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28289,"mean_force":0.07593,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51574,0.10765,0.20567]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8990.0,"contact_point_centroid":[0.52282,0.13653,0.2106],"force_p95":0.10375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27503,"mean_force":0.07147,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51917,0.11779,0.20931]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9751.0,"contact_point_centroid":[0.49003,0.02349,0.0927],"force_p95":0.0765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27328,"mean_force":0.05168,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49029,0.0427,0.09053]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10541.0,"contact_point_centroid":[0.49006,0.06184,0.09482],"force_p95":0.07563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26416,"mean_force":0.04932,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49053,0.0427,0.09334]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.04465,-0.00219],"force_p95":0.17794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25661,"mean_force":0.137,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48963,0.04317,0.02947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3627.0,"contact_point_centroid":[0.48978,0.0238,0.03143],"force_p95":0.0909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16094,"mean_force":0.05759,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48847,0.04306,0.02825]},{"body_a":"world","body_b":"grasp_target","contact_count":308.0,"contact_point_centroid":[0.50118,0.04505,-0.00159],"force_p95":0.13829,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12441,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49916,0.01174,0.29148]},{"body_a":"world","body_b":"grasp_target","contact_count":3496.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4965,0.03502,0.15655]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5482.0,"contact_point_centroid":[0.48828,0.06218,0.03083],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08201,"mean_force":0.04132,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48848,0.04306,0.02826]}],"total_contact_groups":12},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57111,0.23652,0.159],"final_tcp_position":[0.55807,0.23602,0.1786],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.51299,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":78.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02595],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24192,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12225,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":308.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.49879,0.02624,0.28149],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02595],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24192,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3496.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.49649,0.04377,0.03676],"tcp_start":[0.49879,0.02624,0.28149],"tcp_to_object_dist_end":0.01179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50111,0.04303,0.02539],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24389,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16531,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10909.0,"raw_peak_contact_force":0.25661,"tcp_end":[0.48844,0.04306,0.02822],"tcp_start":[0.49649,0.04377,0.03676],"tcp_to_object_dist_end":0.01298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.50717,0.04255,0.15593],"object_pos_start":[0.50111,0.04303,0.02539],"object_to_goal_dist_end":0.21046,"object_to_goal_dist_start":0.24389,"object_z_max":0.15567,"peak_contact_force":0.08129,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20394.0,"raw_peak_contact_force":0.51299,"subtask_id":"subtask_lift","tcp_end":[0.49635,0.0427,0.16202],"tcp_start":[0.48844,0.04306,0.02822],"tcp_to_object_dist_end":0.01242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":634.0,"n_steps_budget":1000.0,"object_pos_end":[0.57049,0.22808,0.18586],"object_pos_start":[0.50717,0.04255,0.15593],"object_to_goal_dist_end":0.04297,"object_to_goal_dist_start":0.21046,"object_z_max":0.2193,"peak_contact_force":0.17207,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17220.0,"raw_peak_contact_force":0.28289,"tcp_end":[0.5563,0.22793,0.20271],"tcp_start":[0.49635,0.0427,0.16202],"tcp_to_object_dist_end":0.02203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.57111,0.23652,0.159],"object_pos_start":[0.57049,0.22808,0.18586],"object_to_goal_dist_end":0.01624,"object_to_goal_dist_start":0.04297,"object_z_max":0.18586,"peak_contact_force":0.17778,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1036.0,"raw_peak_contact_force":0.45146,"subtask_id":"subtask_place","tcp_end":[0.55807,0.23602,0.1786],"tcp_start":[0.5563,0.22793,0.20271],"tcp_to_object_dist_end":0.02354,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69262,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29095,"approach_goal.approach_goal_offset_z":0.19949,"approach_goal.arc_height":0.06742,"descend_1.depth":0.00521,"descend_goal.place_offset_z":-0.01153,"lift_1.lift_height":0.1846,"lift_1.lift_speed":0.06155},"optimized_scores":{"best_composite_score":0.09435,"best_fitness_score":0.56435,"best_task_score":0.16834},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2355.0,"contact_point_centroid":[0.50201,0.00298,-0.00255],"force_p95":0.15847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.26112,"mean_force":0.15044,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55124,0.07084,0.3547]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.47342,-0.01926,-0.00142],"force_p95":0.50124,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59863,"mean_force":0.15744,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46354,-0.01944,0.03137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2686.0,"contact_point_centroid":[0.48097,0.00579,0.2291],"force_p95":0.16482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3027,"mean_force":0.10079,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4753,-0.01272,0.2289]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9245.0,"contact_point_centroid":[0.46709,-0.00033,0.10579],"force_p95":0.09885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28247,"mean_force":0.06042,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46589,-0.01939,0.10361]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2852.0,"contact_point_centroid":[0.48083,-0.03138,0.22793],"force_p95":0.15755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28103,"mean_force":0.09666,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47514,-0.01293,0.22793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9783.0,"contact_point_centroid":[0.46701,-0.0384,0.10385],"force_p95":0.09723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27836,"mean_force":0.05787,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46578,-0.01939,0.10214]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02001,-0.00206],"force_p95":0.1403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19233,"mean_force":0.12747,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46558,-0.01949,0.03124]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.47616,-0.02015,-0.0014],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12481,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49349,-0.00428,0.30287]},{"body_a":"world","body_b":"grasp_target","contact_count":3836.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12566,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4782,-0.01484,0.17024]},{"body_a":"world","body_b":"grasp_target","contact_count":1548.0,"contact_point_centroid":[0.50187,0.00307,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.6227,0.15065,0.28842]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4819.0,"contact_point_centroid":[0.46444,-0.00025,0.03242],"force_p95":0.06787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09819,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46446,-0.01946,0.03013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5170.0,"contact_point_centroid":[0.46431,-0.03869,0.03196],"force_p95":0.06661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07995,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46446,-0.01946,0.03014]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2366.0,"contact_point_centroid":[0.55441,0.07404,0.35993],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01591,"mean_force":0.01054,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55416,0.07404,0.35768]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1659.0,"contact_point_centroid":[0.62305,0.15065,0.29102],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.6227,0.15064,0.28863]}],"total_contact_groups":14},"final_pose_error":0.01465,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50187,0.00307,0.01602],"final_tcp_position":[0.62686,0.15667,0.19217],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":2.26112,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02586],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28847,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12598,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":216.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.4863,-0.01005,0.30705],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":959.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02586],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28847,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3836.0,"raw_peak_contact_force":0.12566,"subtask_id":"subtask_approach","tcp_end":[0.47217,-0.01963,0.03781],"tcp_start":[0.4863,-0.01005,0.30705],"tcp_to_object_dist_end":0.01246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01952,0.02578],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28819,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13779,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11789.0,"raw_peak_contact_force":0.19233,"tcp_end":[0.46443,-0.01946,0.0301],"tcp_start":[0.47217,-0.01963,0.03781],"tcp_to_object_dist_end":0.01239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.4888,-0.01942,0.18068],"object_pos_start":[0.47604,-0.01952,0.02578],"object_to_goal_dist_end":0.22876,"object_to_goal_dist_start":0.28819,"object_z_max":0.18042,"peak_contact_force":0.10844,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19106.0,"raw_peak_contact_force":0.59863,"subtask_id":"subtask_lift","tcp_end":[0.47168,-0.01941,0.19089],"tcp_start":[0.46443,-0.01946,0.0301],"tcp_to_object_dist_end":0.01993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.50187,0.00307,0.01602],"object_pos_start":[0.4888,-0.01942,0.18068],"object_to_goal_dist_end":0.26727,"object_to_goal_dist_start":0.22876,"object_z_max":0.24932,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10259.0,"raw_peak_contact_force":2.26112,"tcp_end":[0.61896,0.1451,0.38307],"tcp_start":[0.47168,-0.01941,0.19089],"tcp_to_object_dist_end":0.41062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.50187,0.00307,0.01602],"object_pos_start":[0.50187,0.00307,0.01602],"object_to_goal_dist_end":0.26727,"object_to_goal_dist_start":0.26727,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3207.0,"raw_peak_contact_force":0.12263,"subtask_id":"subtask_place","tcp_end":[0.62686,0.15667,0.19217],"tcp_start":[0.61896,0.1451,0.38307],"tcp_to_object_dist_end":0.26503,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47794,"average_solve_count":272.0,"average_success_count":272.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05437,"approach_goal.approach_goal_offset_z":0.05732,"approach_goal.arc_height":0.05004,"descend_1.depth":0.00038,"descend_goal.place_offset_z":0.00938,"lift_1.lift_height":0.3312,"lift_1.lift_speed":0.04308},"optimized_scores":{"best_composite_score":0.5115,"best_fitness_score":0.9815,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.45595,-0.02504,-0.00142],"force_p95":0.57976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66201,"mean_force":0.18673,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44602,-0.02542,0.02717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1590.0,"contact_point_centroid":[0.6235,0.18066,0.16069],"force_p95":0.09987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34678,"mean_force":0.0681,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62024,0.19967,0.15931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20889.0,"contact_point_centroid":[0.44919,-0.00615,0.18129],"force_p95":0.07125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27845,"mean_force":0.0493,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44943,-0.02533,0.17957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21201.0,"contact_point_centroid":[0.44894,-0.04449,0.17739],"force_p95":0.07138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27831,"mean_force":0.04903,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44928,-0.02533,0.17604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1830.0,"contact_point_centroid":[0.62287,0.21855,0.16003],"force_p95":0.09473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26206,"mean_force":0.06142,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62022,0.19963,0.15963]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02612,-0.00207],"force_p95":0.14517,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22461,"mean_force":0.12879,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44802,-0.0255,0.02695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11768.0,"contact_point_centroid":[0.53917,0.06665,0.28787],"force_p95":0.09466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18098,"mean_force":0.06465,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53717,0.0858,0.28615]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14567.0,"contact_point_centroid":[0.54012,0.10758,0.28545],"force_p95":0.08095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15135,"mean_force":0.05319,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53933,0.08874,0.28503]},{"body_a":"world","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47991,-0.01127,0.20319]},{"body_a":"world","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45595,-0.02442,0.06768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4806.0,"contact_point_centroid":[0.44693,-0.00622,0.02821],"force_p95":0.06868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10233,"mean_force":0.04493,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44693,-0.02546,0.02593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5438.0,"contact_point_centroid":[0.44639,-0.0447,0.02761],"force_p95":0.06575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08352,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44694,-0.02546,0.02593]}],"total_contact_groups":12},"final_pose_error":0.01469,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63323,0.2031,0.12014],"final_tcp_position":[0.62292,0.20315,0.13525],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.66201,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.45996,-0.02322,0.10376],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1084.0,"raw_peak_contact_force":0.12263,"subtask_id":"subtask_approach","tcp_end":[0.45444,-0.02572,0.03303],"tcp_start":[0.45996,-0.02322,0.10376],"tcp_to_object_dist_end":0.00816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02547,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30315,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14121,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12044.0,"raw_peak_contact_force":0.22461,"tcp_end":[0.44691,-0.02545,0.0259],"tcp_start":[0.45444,-0.02572,0.03303],"tcp_to_object_dist_end":0.01154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46644,-0.02533,0.3214],"object_pos_start":[0.45844,-0.02547,0.02573],"object_to_goal_dist_end":0.35257,"object_to_goal_dist_start":0.30315,"object_z_max":0.3211,"peak_contact_force":0.07247,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42169.0,"raw_peak_contact_force":0.66201,"subtask_id":"subtask_lift","tcp_end":[0.45569,-0.02539,0.33012],"tcp_start":[0.44691,-0.02545,0.0259],"tcp_to_object_dist_end":0.01384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.62915,0.19655,0.16868],"object_pos_start":[0.46644,-0.02533,0.3214],"object_to_goal_dist_end":0.0558,"object_to_goal_dist_start":0.35257,"object_z_max":0.32179,"peak_contact_force":0.08725,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26335.0,"raw_peak_contact_force":0.18098,"tcp_end":[0.61928,0.19672,0.18314],"tcp_start":[0.45569,-0.02539,0.33012],"tcp_to_object_dist_end":0.01751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.63323,0.2031,0.12014],"object_pos_start":[0.62915,0.19655,0.16868],"object_to_goal_dist_end":0.00849,"object_to_goal_dist_start":0.0558,"object_z_max":0.16868,"peak_contact_force":0.08677,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3420.0,"raw_peak_contact_force":0.34678,"subtask_id":"subtask_place","tcp_end":[0.62292,0.20315,0.13525],"tcp_start":[0.61928,0.19672,0.18314],"tcp_to_object_dist_end":0.01829,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```