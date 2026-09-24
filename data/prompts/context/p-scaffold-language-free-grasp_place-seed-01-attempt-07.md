## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5571 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5571 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5604 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.1764 | 0.43 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4387 | 0.79 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.557) — your mutation base

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
  guards:
  - id: lift_success
    when: after_phase
    predicate: object_lifted
    args:
      z_threshold: 0.1
    threshold: 0.1
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
  - guards:
    - id=lift_success, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.1, args={'z_threshold': 0.1}
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
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

- **Composite score**: 0.557
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0497 |
| descend_1 | 1.00 | 1.00 | 0.2223 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |
| lift_1 | 1.00 | 1.00 | 0.2242 |
| approach_goal | 1.00 | 1.00 | 0.2331 |
| descend_goal | 1.00 | 1.00 | 0.0644 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.487, 0.004, 0.261) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.125 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.487, 0.004, 0.261)→(0.475, -0.000, 0.039) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.125 |
| grasp_1 | grasp | 1.00 / step_budget | (0.475, -0.000, 0.039)→(0.467, -0.001, 0.032) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 47.000 | 0.147 | 0.221 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.001, 0.032)→(0.475, -0.000, 0.256) | (0.479, -0.000, 0.026)→(0.487, -0.000, 0.243) | 0.278→0.265 | 1.00 / 35.667 | 0.082 | 0.609 |
| approach_goal | approach | 1.00 / step_budget | (0.475, -0.000, 0.256)→(0.598, 0.190, 0.236) | (0.487, -0.000, 0.243)→(0.605, 0.190, 0.217) | 0.265→0.070 | 1.00 / 33.000 | 0.100 | 0.144 |
| descend_goal | descend | 1.00 / step_budget | (0.598, 0.190, 0.236)→(0.602, 0.198, 0.172) | (0.605, 0.190, 0.217)→(0.605, 0.199, 0.152) | 0.070→0.014 | 1.00 / 31.667 | 0.129 | 0.207 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.238
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.546
- phase_breakdown.subtask_approach_score: 0.144
- phase_breakdown.subtask_lift_score: 0.352
- phase_breakdown.subtask_place_score: 0.823
- grasp_place_fitness: 0.982

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.561
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.482


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72483,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16616,"approach_goal.approach_goal_offset_z":0.0588,"descend_1.depth":0.01834,"descend_goal.place_offset_z":0.02728,"lift_1.lift_height":0.1654,"lift_1.lift_speed":0.1246},"optimized_scores":{"best_composite_score":0.54766,"best_fitness_score":0.96766,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.49882,0.04286,-0.00144],"force_p95":0.4498,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49724,"mean_force":0.09768,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48757,0.04315,0.04356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":326.0,"contact_point_centroid":[0.56328,0.24971,0.18842],"force_p95":0.18192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31786,"mean_force":0.11817,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.557,0.23206,0.19085]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6501.0,"contact_point_centroid":[0.49246,0.06206,0.09876],"force_p95":0.10906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31696,"mean_force":0.06735,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49012,0.04313,0.09679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6095.0,"contact_point_centroid":[0.49305,0.02423,0.1016],"force_p95":0.10846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29398,"mean_force":0.07042,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49035,0.04314,0.09945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":205.0,"contact_point_centroid":[0.56296,0.21358,0.18834],"force_p95":0.2349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26008,"mean_force":0.15361,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55685,0.23161,0.19193]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04488,-0.00215],"force_p95":0.16312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22763,"mean_force":0.13356,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48977,0.04337,0.0433]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6211.0,"contact_point_centroid":[0.53071,0.11635,0.18312],"force_p95":0.12645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18919,"mean_force":0.08582,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52474,0.13503,0.1814]},{"body_a":"world","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.50118,0.04505,-0.00182],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1233,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49885,0.01665,0.25778]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7110.0,"contact_point_centroid":[0.53209,0.15666,0.18308],"force_p95":0.10024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13031,"mean_force":0.07539,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52581,0.13816,0.18189]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49611,0.03951,0.1301]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5040.0,"contact_point_centroid":[0.48847,0.02402,0.04509],"force_p95":0.07011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1176,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48863,0.04326,0.04207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5526.0,"contact_point_centroid":[0.4883,0.06259,0.04451],"force_p95":0.07037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07293,"mean_force":0.04087,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48864,0.04327,0.04208]}],"total_contact_groups":12},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5679,0.23765,0.15216],"final_tcp_position":[0.55802,0.23516,0.18346],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.49724,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":728.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.4984,0.03522,0.21293],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.12263,"subtask_id":"subtask_approach","tcp_end":[0.4965,0.04397,0.05062],"tcp_start":[0.4984,0.03522,0.21293],"tcp_to_object_dist_end":0.02507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04376,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24322,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15745,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12366.0,"raw_peak_contact_force":0.22763,"tcp_end":[0.4886,0.04326,0.04204],"tcp_start":[0.4965,0.04397,0.05062],"tcp_to_object_dist_end":0.02078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":408.0,"n_steps_budget":750.0,"object_pos_end":[0.51229,0.04377,0.14936],"object_pos_start":[0.50114,0.04376,0.02548],"object_to_goal_dist_end":0.20775,"object_to_goal_dist_start":0.24322,"object_z_max":0.1491,"peak_contact_force":0.10143,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12674.0,"raw_peak_contact_force":0.49724,"subtask_id":"subtask_lift","tcp_end":[0.49655,0.04339,0.17167],"tcp_start":[0.4886,0.04326,0.04204],"tcp_to_object_dist_end":0.0273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.56407,0.22973,0.16695],"object_pos_start":[0.51229,0.04377,0.14936],"object_to_goal_dist_end":0.02522,"object_to_goal_dist_start":0.20775,"object_z_max":0.16693,"peak_contact_force":0.15536,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13321.0,"raw_peak_contact_force":0.18919,"tcp_end":[0.55661,0.22967,0.19563],"tcp_start":[0.49655,0.04339,0.17167],"tcp_to_object_dist_end":0.02963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":41.0,"n_steps_budget":1000.0,"object_pos_end":[0.5679,0.23765,0.15216],"object_pos_start":[0.56407,0.22973,0.16695],"object_to_goal_dist_end":0.00966,"object_to_goal_dist_start":0.02522,"object_z_max":0.16695,"peak_contact_force":0.25367,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":531.0,"raw_peak_contact_force":0.31786,"subtask_id":"subtask_place","tcp_end":[0.55802,0.23516,0.18346],"tcp_start":[0.55661,0.22967,0.19563],"tcp_to_object_dist_end":0.03291,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42045,"average_solve_count":264.0,"average_success_count":264.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24823,"approach_goal.approach_goal_offset_z":0.11834,"descend_1.depth":0.00158,"descend_goal.place_offset_z":0.01662,"lift_1.lift_height":0.3069,"lift_1.lift_speed":0.04949},"optimized_scores":{"best_composite_score":0.56147,"best_fitness_score":0.98147,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.47345,-0.01919,-0.00141],"force_p95":0.55685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64952,"mean_force":0.16025,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4635,-0.01934,0.02796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19612.0,"contact_point_centroid":[0.46705,-0.00011,0.17564],"force_p95":0.07305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28155,"mean_force":0.05041,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46711,-0.01928,0.17376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19903.0,"contact_point_centroid":[0.4669,-0.03842,0.17113],"force_p95":0.07255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27834,"mean_force":0.05007,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46692,-0.01928,0.16956]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.01996,-0.00207],"force_p95":0.14349,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20863,"mean_force":0.12837,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46568,-0.01938,0.02793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3356.0,"contact_point_centroid":[0.62232,0.16952,0.2618],"force_p95":0.07908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15266,"mean_force":0.05316,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62175,0.15051,0.26031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3520.0,"contact_point_centroid":[0.62222,0.13131,0.26175],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15033,"mean_force":0.05222,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62172,0.15047,0.2605]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.47616,-0.02015,-0.00123],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12402,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49508,-0.00327,0.29539]},{"body_a":"world","body_b":"grasp_target","contact_count":3596.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13005,"mean_force":0.12269,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47931,-0.01395,0.15872]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4809.0,"contact_point_centroid":[0.46451,-0.00012,0.02909],"force_p95":0.06813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12797,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46456,-0.01936,0.02683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11706.0,"contact_point_centroid":[0.54707,0.04584,0.30545],"force_p95":0.07811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12716,"mean_force":0.05201,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54634,0.0647,0.30483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9665.0,"contact_point_centroid":[0.5475,0.0835,0.30655],"force_p95":0.08984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12281,"mean_force":0.06128,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54607,0.06437,0.30489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5429.0,"contact_point_centroid":[0.46401,-0.0386,0.02851],"force_p95":0.06515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08091,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46456,-0.01936,0.02684]}],"total_contact_groups":12},"final_pose_error":0.01467,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62334,0.15481,0.20344],"final_tcp_position":[0.62586,0.15534,0.21965],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.64952,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":44.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02595],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28842,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.13053,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":172.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.48866,-0.00831,0.28834],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02595],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28842,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3596.0,"raw_peak_contact_force":0.13005,"subtask_id":"subtask_approach","tcp_end":[0.4723,-0.01952,0.03451],"tcp_start":[0.48866,-0.00831,0.28834],"tcp_to_object_dist_end":0.00935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01938,0.02575],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28812,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14009,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12038.0,"raw_peak_contact_force":0.20863,"tcp_end":[0.46453,-0.01936,0.0268],"tcp_start":[0.4723,-0.01952,0.03451],"tcp_to_object_dist_end":0.01155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.48412,-0.01932,0.30394],"object_pos_start":[0.47603,-0.01938,0.02575],"object_to_goal_dist_end":0.25795,"object_to_goal_dist_start":0.28812,"object_z_max":0.30367,"peak_contact_force":0.07541,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39597.0,"raw_peak_contact_force":0.64952,"subtask_id":"subtask_lift","tcp_end":[0.47333,-0.01932,0.3131],"tcp_start":[0.46453,-0.01936,0.0268],"tcp_to_object_dist_end":0.01416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.6264,0.14582,0.28604],"object_pos_start":[0.48412,-0.01932,0.30394],"object_to_goal_dist_end":0.09708,"object_to_goal_dist_start":0.25795,"object_z_max":0.30412,"peak_contact_force":0.07606,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21371.0,"raw_peak_contact_force":0.12716,"tcp_end":[0.61863,0.14596,0.30078],"tcp_start":[0.47333,-0.01932,0.3131],"tcp_to_object_dist_end":0.01666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.62334,0.15481,0.20344],"object_pos_start":[0.6264,0.14582,0.28604],"object_to_goal_dist_end":0.01627,"object_to_goal_dist_start":0.09708,"object_z_max":0.28604,"peak_contact_force":0.06713,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6876.0,"raw_peak_contact_force":0.15266,"subtask_id":"subtask_place","tcp_end":[0.62586,0.15534,0.21965],"tcp_start":[0.61863,0.14596,0.30078],"tcp_to_object_dist_end":0.01641,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44964,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24543,"approach_goal.approach_goal_offset_z":0.10127,"descend_1.depth":0.00031,"descend_goal.place_offset_z":-0.01313,"lift_1.lift_height":0.27588,"lift_1.lift_speed":0.03493},"optimized_scores":{"best_composite_score":0.56224,"best_fitness_score":0.98224,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.45534,-0.0251,-0.00146],"force_p95":0.61568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67913,"mean_force":0.21157,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44647,-0.02539,0.02715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17226.0,"contact_point_centroid":[0.44963,-0.04445,0.15656],"force_p95":0.07315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26562,"mean_force":0.0505,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44956,-0.02532,0.15465]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16819.0,"contact_point_centroid":[0.44964,-0.00616,0.15615],"force_p95":0.07394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25298,"mean_force":0.05127,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44954,-0.02532,0.15405]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02613,-0.00208],"force_p95":0.14561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22582,"mean_force":0.12905,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44851,-0.02547,0.02708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4310.0,"contact_point_centroid":[0.61978,0.1794,0.16404],"force_p95":0.0771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14936,"mean_force":0.04976,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61952,0.19861,0.16213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4271.0,"contact_point_centroid":[0.61972,0.21778,0.16345],"force_p95":0.07613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14194,"mean_force":0.05055,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61955,0.19866,0.16163]},{"body_a":"world","body_b":"grasp_target","contact_count":304.0,"contact_point_centroid":[0.45856,-0.02632,-0.00159],"force_p95":0.13831,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12444,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48778,-0.0069,0.29162]},{"body_a":"world","body_b":"grasp_target","contact_count":3592.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46323,-0.02058,0.1552]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14643.0,"contact_point_centroid":[0.53902,0.07005,0.24464],"force_p95":0.0771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11571,"mean_force":0.05005,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53913,0.08921,0.24312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14729.0,"contact_point_centroid":[0.53443,0.10176,0.24675],"force_p95":0.07466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11466,"mean_force":0.04969,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53422,0.08265,0.24513]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5279.0,"contact_point_centroid":[0.44678,-0.00618,0.02748],"force_p95":0.0656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10334,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44742,-0.02543,0.02605]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5441.0,"contact_point_centroid":[0.44679,-0.04473,0.02734],"force_p95":0.06557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08333,"mean_force":0.04121,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44742,-0.02543,0.02606]}],"total_contact_groups":12},"final_pose_error":0.01488,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62474,0.20353,0.10065],"final_tcp_position":[0.62348,0.20393,0.1136],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.67913,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":77.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02594],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30367,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.1223,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":304.0,"raw_peak_contact_force":0.13845,"subtask_id":"subtask_approach","tcp_end":[0.47389,-0.01548,0.28192],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":898.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02594],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30367,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3592.0,"raw_peak_contact_force":0.12264,"subtask_id":"subtask_approach","tcp_end":[0.45493,-0.02568,0.03318],"tcp_start":[0.47389,-0.01548,0.28192],"tcp_to_object_dist_end":0.00805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02549,0.02572],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30317,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14255,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12520.0,"raw_peak_contact_force":0.22582,"tcp_end":[0.44739,-0.02543,0.02602],"tcp_start":[0.45493,-0.02568,0.03318],"tcp_to_object_dist_end":0.01105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.46567,-0.0254,0.27545],"object_pos_start":[0.45844,-0.02549,0.02572],"object_to_goal_dist_end":0.3281,"object_to_goal_dist_start":0.30317,"object_z_max":0.27518,"peak_contact_force":0.06971,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34126.0,"raw_peak_contact_force":0.67913,"subtask_id":"subtask_lift","tcp_end":[0.45542,-0.02538,0.28209],"tcp_start":[0.44739,-0.02543,0.02602],"tcp_to_object_dist_end":0.01221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.62558,0.19397,0.19906],"object_pos_start":[0.46567,-0.0254,0.27545],"object_to_goal_dist_end":0.08625,"object_to_goal_dist_start":0.3281,"object_z_max":0.27562,"peak_contact_force":0.06973,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29372.0,"raw_peak_contact_force":0.11571,"tcp_end":[0.61733,0.19393,0.21062],"tcp_start":[0.45542,-0.02538,0.28209],"tcp_to_object_dist_end":0.01419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.62474,0.20353,0.10065],"object_pos_start":[0.62558,0.19397,0.19906],"object_to_goal_dist_end":0.01525,"object_to_goal_dist_start":0.08625,"object_z_max":0.19906,"peak_contact_force":0.06742,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8581.0,"raw_peak_contact_force":0.14936,"subtask_id":"subtask_place","tcp_end":[0.62348,0.20393,0.1136],"tcp_start":[0.61733,0.19393,0.21062],"tcp_to_object_dist_end":0.01302,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```