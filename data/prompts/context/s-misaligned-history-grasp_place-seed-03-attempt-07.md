## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12  | 0.4709 | 0.88 | ❌ rejected |
| 6 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7  | 0.4119 | 0.94 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4535 | 1.00 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4537 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.2431 | 1.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | final destination targets |
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

## Current Skill (Q=0.243) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: place_at_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
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
  subtask_id: pre_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
- id: grasp_object
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
  retries:
    max_attempts: 1
    strategy: repeat
- id: lift_object
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
    - 0.1
    tolerance: 0.01
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_to_goal
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
    tolerance: 0.01
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.6
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
- id: place_at_goal
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
    tolerance: 0.01
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    place_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    place_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_offset_y: status=consumed; consumers=target.offset.y (replace)
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.243
- **task_score** (E): 1.000
- **fitness_score**: 0.963  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1500 |
| descend_to_grasp | 1.00 | 1.00 | 0.1008 |
| grasp_object | 1.00 | 1.00 | 0.0134 |
| lift_object | 1.00 | 1.00 | 0.0971 |
| transport_to_goal | 1.00 | 1.00 | 0.2135 |
| place_at_goal | 1.00 | 1.00 | 0.0134 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.156) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 16.498 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.156)→(0.506, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.002, 0.055)→(0.497, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 46.333 | 0.148 | 0.193 |
| lift_object | lift | 1.00 / step_budget | (0.497, 0.002, 0.045)→(0.493, 0.001, 0.142) | (0.511, 0.002, 0.026)→(0.506, 0.002, 0.120) | 0.246→0.221 | 1.00 / 41.667 | 75.090 | 0.458 |
| transport_to_goal | approach | 1.00 / step_budget | (0.493, 0.001, 0.142)→(0.615, 0.170, 0.177) | (0.506, 0.002, 0.120)→(0.618, 0.172, 0.151) | 0.221→0.019 | 1.00 / 33.333 | 0.090 | 0.302 |
| place_at_goal | descend | 1.00 / step_budget | (0.615, 0.170, 0.177)→(0.617, 0.174, 0.165) | (0.618, 0.172, 0.151)→(0.621, 0.176, 0.138) | 0.019→0.013 | 1.00 / 32.667 | 0.097 | 0.364 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.581
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.395
- phase_breakdown.place_at_goal_score: 0.405
- phase_breakdown.pre_grasp_score: 0.372
- grasp_place_fitness: 0.964

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.964
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.243
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.302


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94355,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09526,"approach_object.approach_tolerance":0.03009,"descend_to_grasp.descend_tolerance":0.03506,"descend_to_grasp.grasp_offset_z":0.01003,"lift_object.lift_height":0.10525,"lift_object.lift_tolerance":0.02761,"place_at_goal.descend_speed":0.15213,"place_at_goal.place_offset_x":-0.00145,"place_at_goal.place_offset_y":0.00378,"place_at_goal.place_offset_z":0.02681,"transport_to_goal.transport_speed":0.36011,"transport_to_goal.transport_tolerance":0.02453},"optimized_scores":{"best_composite_score":0.24253,"best_fitness_score":0.96253,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.61523,0.21933,0.14487],"force_p95":0.11396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46013,"mean_force":0.09011,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61908,0.20087,0.14559]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.4564,-0.02515,-0.00139],"force_p95":0.36426,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40686,"mean_force":0.09316,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44568,-0.02514,0.04857]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11990.0,"contact_point_centroid":[0.52712,0.0609,0.14112],"force_p95":0.10144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38798,"mean_force":0.05738,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52451,0.07958,0.1412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.62421,0.18356,0.14071],"force_p95":0.10454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35498,"mean_force":0.08161,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61913,0.20098,0.14539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10421.0,"contact_point_centroid":[0.52065,0.0953,0.1414],"force_p95":0.1046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32281,"mean_force":0.06362,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52192,0.0763,0.14087]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5476.0,"contact_point_centroid":[0.44365,-0.04433,0.09185],"force_p95":0.07588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27084,"mean_force":0.05258,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44346,-0.02507,0.08907]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6026.0,"contact_point_centroid":[0.44508,-0.00594,0.09003],"force_p95":0.07803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25838,"mean_force":0.04903,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44347,-0.02507,0.08889]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02636,-0.0021],"force_p95":0.14936,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1988,"mean_force":0.1298,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44802,-0.02521,0.04813]},{"body_a":"world","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4805,-0.01084,0.22391]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5555.0,"contact_point_centroid":[0.44835,-0.00599,0.04822],"force_p95":0.06809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12448,"mean_force":0.03987,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44689,-0.02517,0.04705]},{"body_a":"world","body_b":"grasp_target","contact_count":692.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45741,-0.02395,0.10069]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5043.0,"contact_point_centroid":[0.44689,-0.04447,0.04987],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07597,"mean_force":0.04371,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.02517,0.04705]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62043,0.20786,0.10812],"final_tcp_position":[0.62151,0.20585,0.13781],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":49.24842,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":49.24842,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.46099,-0.02257,0.14472],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":173.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":692.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45528,-0.02539,0.05547],"tcp_start":[0.46099,-0.02257,0.14472],"tcp_to_object_dist_end":0.02965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45853,-0.02587,0.02565],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30342,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14834,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12398.0,"raw_peak_contact_force":0.1988,"tcp_end":[0.44686,-0.02517,0.04702],"tcp_start":[0.45528,-0.02539,0.05547],"tcp_to_object_dist_end":0.02436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":262.0,"n_steps_budget":690.0,"object_pos_end":[0.45471,-0.02586,0.11004],"object_pos_start":[0.45853,-0.02587,0.02565],"object_to_goal_dist_end":0.29254,"object_to_goal_dist_start":0.30342,"object_z_max":0.10975,"peak_contact_force":0.0711,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11579.0,"raw_peak_contact_force":0.40686,"tcp_end":[0.44323,-0.02505,0.13273],"tcp_start":[0.44686,-0.02517,0.04702],"tcp_to_object_dist_end":0.02544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.61471,0.19734,0.12479],"object_pos_start":[0.45471,-0.02586,0.11004],"object_to_goal_dist_end":0.02167,"object_to_goal_dist_start":0.29254,"object_z_max":0.12478,"peak_contact_force":0.11042,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22411.0,"raw_peak_contact_force":0.38798,"tcp_end":[0.6177,0.19629,0.15422],"tcp_start":[0.44323,-0.02505,0.13273],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":91.0,"n_steps_budget":1000.0,"object_pos_end":[0.62043,0.20786,0.10812],"object_pos_start":[0.61471,0.19734,0.12479],"object_to_goal_dist_end":0.01141,"object_to_goal_dist_start":0.02167,"object_z_max":0.12479,"peak_contact_force":0.11355,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2048.0,"raw_peak_contact_force":0.46013,"subtask_id":"place_at_goal","tcp_end":[0.62151,0.20585,0.13781],"tcp_start":[0.6177,0.19629,0.15422],"tcp_to_object_dist_end":0.02978,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80469,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13164,"approach_object.approach_tolerance":0.02891,"descend_to_grasp.descend_tolerance":0.02488,"descend_to_grasp.grasp_offset_z":0.01029,"lift_object.lift_height":0.12591,"lift_object.lift_tolerance":0.03404,"place_at_goal.descend_speed":0.26052,"place_at_goal.place_offset_x":0.00245,"place_at_goal.place_offset_y":-0.00673,"place_at_goal.place_offset_z":0.01399,"transport_to_goal.transport_speed":0.28442,"transport_to_goal.transport_tolerance":0.02899},"optimized_scores":{"best_composite_score":0.24356,"best_fitness_score":0.96356,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54126,0.00058,-0.00134],"force_p95":0.41418,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48021,"mean_force":0.09605,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52783,0.00079,0.04535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7459.0,"contact_point_centroid":[0.52629,0.01988,0.09838],"force_p95":0.0772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32121,"mean_force":0.05306,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52524,0.00074,0.09557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7194.0,"contact_point_centroid":[0.52644,-0.01843,0.09957],"force_p95":0.07812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31417,"mean_force":0.05424,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5252,0.00074,0.09666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1340.0,"contact_point_centroid":[0.63467,0.16762,0.22131],"force_p95":0.07562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27906,"mean_force":0.051,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63909,0.14915,0.21946]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10851.0,"contact_point_centroid":[0.58318,0.05695,0.18833],"force_p95":0.07898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25589,"mean_force":0.05404,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58122,0.07606,0.18743]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11248.0,"contact_point_centroid":[0.58158,0.0978,0.19114],"force_p95":0.07464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23125,"mean_force":0.05139,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58342,0.07892,0.18896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1197.0,"contact_point_centroid":[0.64165,0.13001,0.21922],"force_p95":0.07909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22366,"mean_force":0.05487,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6391,0.14915,0.21937]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00117,-0.00204],"force_p95":0.13397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16235,"mean_force":0.12582,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53032,0.00084,0.04546]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51569,0.00043,0.24032]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53501,0.00093,0.11718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5225.0,"contact_point_centroid":[0.53005,-0.01834,0.04662],"force_p95":0.06412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09383,"mean_force":0.04174,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52908,0.00081,0.04401]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4744.0,"contact_point_centroid":[0.52996,0.02007,0.04734],"force_p95":0.06876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08718,"mean_force":0.04609,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52908,0.00081,0.04401]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64894,0.15242,0.18508],"final_tcp_position":[0.64159,0.14956,0.20995],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":225.11417,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53384,0.00089,0.17834],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":920.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53818,0.001,0.05512],"tcp_start":[0.53384,0.00089,0.17834],"tcp_to_object_dist_end":0.02973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00093,0.02584],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2504,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13474,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11769.0,"raw_peak_contact_force":0.16235,"tcp_end":[0.52905,0.00082,0.04397],"tcp_start":[0.53818,0.001,0.05512],"tcp_to_object_dist_end":0.02363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":358.0,"n_steps_budget":810.0,"object_pos_end":[0.53834,0.00078,0.1295],"object_pos_start":[0.54422,0.00093,0.02584],"object_to_goal_dist_end":0.2012,"object_to_goal_dist_start":0.2504,"object_z_max":0.12923,"peak_contact_force":225.11417,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14733.0,"raw_peak_contact_force":0.48021,"tcp_end":[0.52521,0.00075,0.15043],"tcp_start":[0.52905,0.00082,0.04397],"tcp_to_object_dist_end":0.02471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.64452,0.15095,0.20284],"object_pos_start":[0.53834,0.00078,0.1295],"object_to_goal_dist_end":0.01408,"object_to_goal_dist_start":0.2012,"object_z_max":0.20275,"peak_contact_force":0.07438,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22099.0,"raw_peak_contact_force":0.25589,"tcp_end":[0.63749,0.14835,0.22719],"tcp_start":[0.52521,0.00075,0.15043],"tcp_to_object_dist_end":0.02548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.64894,0.15242,0.18508],"object_pos_start":[0.64452,0.15095,0.20284],"object_to_goal_dist_end":0.00837,"object_to_goal_dist_start":0.01408,"object_z_max":0.20284,"peak_contact_force":0.07469,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2537.0,"raw_peak_contact_force":0.27906,"subtask_id":"place_at_goal","tcp_end":[0.64159,0.14956,0.20995],"tcp_start":[0.63749,0.14835,0.22719],"tcp_to_object_dist_end":0.0261,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.672,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09641,"approach_object.approach_tolerance":0.02532,"descend_to_grasp.descend_tolerance":0.01487,"descend_to_grasp.grasp_offset_z":0.01009,"lift_object.lift_height":0.11819,"lift_object.lift_tolerance":0.02003,"place_at_goal.descend_speed":0.1629,"place_at_goal.place_offset_x":-0.01035,"place_at_goal.place_offset_y":-0.00871,"place_at_goal.place_offset_z":0.03511,"transport_to_goal.transport_speed":0.34419,"transport_to_goal.transport_tolerance":0.04082},"optimized_scores":{"best_composite_score":0.24324,"best_fitness_score":0.96324,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.52773,0.02871,-0.00147],"force_p95":0.42857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4876,"mean_force":0.09923,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51437,0.02887,0.04559]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":387.0,"contact_point_centroid":[0.58486,0.18386,0.15038],"force_p95":0.15409,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35418,"mean_force":0.06378,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58963,0.16557,0.14787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6192.0,"contact_point_centroid":[0.51248,0.04793,0.09582],"force_p95":0.08472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32425,"mean_force":0.05896,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51186,0.02872,0.09252]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7065.0,"contact_point_centroid":[0.51379,0.00973,0.09362],"force_p95":0.08142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30406,"mean_force":0.05162,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5119,0.02872,0.09173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7516.0,"contact_point_centroid":[0.55195,0.07675,0.14431],"force_p95":0.09658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26244,"mean_force":0.05781,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54909,0.09546,0.1439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":333.0,"contact_point_centroid":[0.59408,0.14692,0.14668],"force_p95":0.11169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25627,"mean_force":0.06501,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58967,0.16554,0.14799]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7591.0,"contact_point_centroid":[0.54775,0.11529,0.14631],"force_p95":0.10273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22255,"mean_force":0.06327,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54963,0.09644,0.14391]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03079,-0.00216],"force_p95":0.16429,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21868,"mean_force":0.13394,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51687,0.02905,0.04548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5689.0,"contact_point_centroid":[0.51687,0.00984,0.04671],"force_p95":0.06378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14832,"mean_force":0.03856,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51565,0.02897,0.04409]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51037,0.01272,0.22337]},{"body_a":"world","body_b":"grasp_target","contact_count":676.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52284,0.02789,0.10003]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4746.0,"contact_point_centroid":[0.51605,0.04833,0.04771],"force_p95":0.07317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07996,"mean_force":0.0467,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51566,0.02897,0.0441]}],"total_contact_groups":12},"final_pose_error":0.00537,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59423,0.16841,0.12176],"final_tcp_position":[0.58912,0.16589,0.14617],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.4876,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52286,0.02637,0.14434],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":676.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52462,0.02953,0.05472],"tcp_start":[0.52286,0.02637,0.14434],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53053,0.0299,0.02545],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18433,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16108,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12235.0,"raw_peak_contact_force":0.21868,"tcp_end":[0.51562,0.02897,0.04406],"tcp_start":[0.52462,0.02953,0.05472],"tcp_to_object_dist_end":0.02386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":326.0,"n_steps_budget":750.0,"object_pos_end":[0.52519,0.02972,0.12174],"object_pos_start":[0.53053,0.0299,0.02545],"object_to_goal_dist_end":0.16786,"object_to_goal_dist_start":0.18433,"object_z_max":0.12147,"peak_contact_force":0.08611,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13339.0,"raw_peak_contact_force":0.4876,"tcp_end":[0.51177,0.02872,0.14281],"tcp_start":[0.51562,0.02897,0.04406],"tcp_to_object_dist_end":0.025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.59585,0.16754,0.12491],"object_pos_start":[0.52519,0.02972,0.12174],"object_to_goal_dist_end":0.02091,"object_to_goal_dist_start":0.16786,"object_z_max":0.12489,"peak_contact_force":0.08636,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15107.0,"raw_peak_contact_force":0.26244,"tcp_end":[0.59013,0.16493,0.14902],"tcp_start":[0.51177,0.02872,0.14281],"tcp_to_object_dist_end":0.02492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.59423,0.16841,0.12176],"object_pos_start":[0.59585,0.16754,0.12491],"object_to_goal_dist_end":0.01853,"object_to_goal_dist_start":0.02091,"object_z_max":0.12491,"peak_contact_force":0.10229,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":720.0,"raw_peak_contact_force":0.35418,"subtask_id":"place_at_goal","tcp_end":[0.58912,0.16589,0.14617],"tcp_start":[0.59013,0.16493,0.14902],"tcp_to_object_dist_end":0.02507,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```