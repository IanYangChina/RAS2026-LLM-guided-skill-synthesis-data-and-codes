## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.0135 | 0.43 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11  | -0.4832 | 0.21 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13  | 0.2037 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13  | 0.2431 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12  | 0.4536 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.454) — your mutation base

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

- **Composite score**: 0.454
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1801 |
| descend_to_grasp | 1.00 | 1.00 | 0.0814 |
| grasp_object | 1.00 | 1.00 | 0.0128 |
| lift_object | 1.00 | 1.00 | 0.1030 |
| transport_to_goal | 1.00 | 1.00 | 0.2144 |
| place_at_goal | 1.00 | 1.00 | 0.0668 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.126) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 12.056 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.126)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.002, 0.044)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.142 | 0.181 |
| lift_object | lift | 1.00 / step_budget | (0.497, 0.002, 0.035)→(0.493, 0.002, 0.138) | (0.511, 0.002, 0.026)→(0.504, 0.002, 0.122) | 0.246→0.222 | 1.00 / 37.667 | 0.091 | 0.609 |
| transport_to_goal | approach | 1.00 / step_budget | (0.493, 0.002, 0.138)→(0.607, 0.160, 0.218) | (0.504, 0.002, 0.122)→(0.611, 0.161, 0.195) | 0.222→0.064 | 1.00 / 39.000 | 0.164 | 0.251 |
| place_at_goal | descend | 1.00 / step_budget | (0.607, 0.160, 0.218)→(0.623, 0.176, 0.156) | (0.611, 0.161, 0.195)→(0.625, 0.178, 0.131) | 0.064→0.013 | 1.00 / 33.667 | 0.093 | 0.297 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.311
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.690
- phase_breakdown.place_at_goal_score: 0.754
- phase_breakdown.pre_grasp_score: 0.541
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.453
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_to_grasp.grasp_offset_z
- **Final σ (mean)**: 0.305


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08527,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.05636,"descend_to_grasp.grasp_offset_z":0.01,"lift_object.lift_height":0.11731,"place_at_goal.descend_speed":0.11501,"place_at_goal.place_offset_x":0.01165,"place_at_goal.place_offset_y":-0.00192,"place_at_goal.place_offset_z":0.01765,"transport_to_goal.transport_speed":0.43171},"optimized_scores":{"best_composite_score":0.45326,"best_fitness_score":0.97326,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.45524,-0.02508,-0.00113],"force_p95":0.31337,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57393,"mean_force":0.0819,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44426,-0.02551,0.03877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3662.0,"contact_point_centroid":[0.61184,0.20717,0.16205],"force_p95":0.12716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39309,"mean_force":0.08325,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61616,0.18878,0.16269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4204.0,"contact_point_centroid":[0.62003,0.17061,0.15995],"force_p95":0.11791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32851,"mean_force":0.07667,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61574,0.18846,0.16354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18818.0,"contact_point_centroid":[0.51613,0.09107,0.16909],"force_p95":0.07834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32066,"mean_force":0.05298,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51749,0.07215,0.16704]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19163.0,"contact_point_centroid":[0.5264,0.06082,0.17044],"force_p95":0.07767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31742,"mean_force":0.05286,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52361,0.07972,0.16919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14195.0,"contact_point_centroid":[0.4432,-0.00642,0.09105],"force_p95":0.07405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28535,"mean_force":0.04874,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44169,-0.02542,0.08926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11966.0,"contact_point_centroid":[0.44149,-0.04462,0.09236],"force_p95":0.08001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28232,"mean_force":0.05619,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4417,-0.02542,0.08962]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02636,-0.00206],"force_p95":0.14228,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17745,"mean_force":0.12742,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44683,-0.02558,0.03799]},{"body_a":"world","body_b":"grasp_target","contact_count":2464.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13065,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47784,-0.012,0.19787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5128.0,"contact_point_centroid":[0.44697,-0.00646,0.03832],"force_p95":0.06858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12722,"mean_force":0.04269,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44566,-0.02555,0.03688]},{"body_a":"world","body_b":"grasp_target","contact_count":704.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45442,-0.02506,0.07032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4416.0,"contact_point_centroid":[0.44513,-0.04481,0.03967],"force_p95":0.07929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08525,"mean_force":0.04913,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44566,-0.02555,0.03688]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62666,0.20243,0.09998],"final_tcp_position":[0.63304,0.20165,0.13043],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":35.92251,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":617.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":35.92251,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2464.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.45715,-0.02442,0.09599],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":704.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45375,-0.02577,0.04468],"tcp_start":[0.45715,-0.02442,0.09599],"tcp_to_object_dist_end":0.01928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02604,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30355,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14193,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11344.0,"raw_peak_contact_force":0.17745,"tcp_end":[0.44563,-0.02555,0.03685],"tcp_start":[0.45375,-0.02577,0.04468],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.45199,-0.02607,0.12545],"object_pos_start":[0.45848,-0.02604,0.02578],"object_to_goal_dist_end":0.29454,"object_to_goal_dist_start":0.30355,"object_z_max":0.12534,"peak_contact_force":0.07905,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26290.0,"raw_peak_contact_force":0.57393,"tcp_end":[0.44183,-0.02542,0.143],"tcp_start":[0.44563,-0.02555,0.03685],"tcp_to_object_dist_end":0.02029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60016,0.17826,0.17165],"object_pos_start":[0.45199,-0.02607,0.12545],"object_to_goal_dist_end":0.07145,"object_to_goal_dist_start":0.29454,"object_z_max":0.17162,"peak_contact_force":0.32066,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37981.0,"raw_peak_contact_force":0.32066,"tcp_end":[0.60251,0.17734,0.19696],"tcp_start":[0.44183,-0.02542,0.143],"tcp_to_object_dist_end":0.02543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.62666,0.20243,0.09998],"object_pos_start":[0.60016,0.17826,0.17165],"object_to_goal_dist_end":0.01567,"object_to_goal_dist_start":0.07145,"object_z_max":0.17165,"peak_contact_force":0.11274,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7866.0,"raw_peak_contact_force":0.39309,"subtask_id":"place_at_goal","tcp_end":[0.63304,0.20165,0.13043],"tcp_start":[0.60251,0.17734,0.19696],"tcp_to_object_dist_end":0.03112,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01626,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12352,"descend_to_grasp.grasp_offset_z":0.01019,"lift_object.lift_height":0.1224,"place_at_goal.descend_speed":0.14358,"place_at_goal.place_offset_x":0.00334,"place_at_goal.place_offset_y":-0.00096,"place_at_goal.place_offset_z":0.00478,"transport_to_goal.transport_speed":0.34934},"optimized_scores":{"best_composite_score":0.45391,"best_fitness_score":0.97391,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.54042,0.00079,-0.00114],"force_p95":0.46767,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63179,"mean_force":0.09935,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.528,0.00079,0.03534]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12408.0,"contact_point_centroid":[0.52674,0.01987,0.09039],"force_p95":0.08085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35142,"mean_force":0.05716,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52529,0.00075,0.0882]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13385.0,"contact_point_centroid":[0.5267,-0.01828,0.0877],"force_p95":0.07809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3299,"mean_force":0.0536,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52532,0.00075,0.08573]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3895.0,"contact_point_centroid":[0.63323,0.16312,0.23682],"force_p95":0.08206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29957,"mean_force":0.05443,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.635,0.14414,0.2336]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.64062,0.12624,0.23172],"force_p95":0.0866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25437,"mean_force":0.05322,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63559,0.14475,0.23102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18142.0,"contact_point_centroid":[0.58104,0.05312,0.2041],"force_p95":0.0862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21614,"mean_force":0.05711,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57774,0.0718,0.20355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17190.0,"contact_point_centroid":[0.57578,0.08889,0.20361],"force_p95":0.08617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19641,"mean_force":0.05919,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5763,0.06997,0.20186]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15368,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53091,0.00086,0.03519]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.517,0.00047,0.22934]},{"body_a":"world","body_b":"grasp_target","contact_count":1400.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53619,0.00097,0.10139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53082,-0.01822,0.03537],"force_p95":0.06859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10188,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00083,0.0337]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53089,0.02005,0.03626],"force_p95":0.07522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09582,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52964,0.00083,0.03371]}],"total_contact_groups":12},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64949,0.15533,0.17773],"final_tcp_position":[0.64345,0.15255,0.2002],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.63179,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1912.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53664,0.00097,0.15977],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1400.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53848,0.00101,0.04412],"tcp_start":[0.53664,0.00097,0.15977],"tcp_to_object_dist_end":0.01902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00106,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25032,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13337,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.15368,"tcp_end":[0.52961,0.00083,0.03367],"tcp_start":[0.53848,0.00101,0.04412],"tcp_to_object_dist_end":0.01653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.53685,0.00081,0.12844],"object_pos_start":[0.54418,0.00106,0.02587],"object_to_goal_dist_end":0.20231,"object_to_goal_dist_start":0.25032,"object_z_max":0.12833,"peak_contact_force":0.08092,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25934.0,"raw_peak_contact_force":0.63179,"tcp_end":[0.52553,0.00076,0.14343],"tcp_start":[0.52961,0.00083,0.03367],"tcp_to_object_dist_end":0.01878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63588,0.13979,0.24264],"object_pos_start":[0.53685,0.00081,0.12844],"object_to_goal_dist_end":0.05594,"object_to_goal_dist_start":0.20231,"object_z_max":0.24246,"peak_contact_force":0.07563,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35332.0,"raw_peak_contact_force":0.21614,"tcp_end":[0.62945,0.13753,0.26391],"tcp_start":[0.52553,0.00076,0.14343],"tcp_to_object_dist_end":0.02233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.64949,0.15533,0.17773],"object_pos_start":[0.63588,0.13979,0.24264],"object_to_goal_dist_end":0.01378,"object_to_goal_dist_start":0.05594,"object_z_max":0.24271,"peak_contact_force":0.07534,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7957.0,"raw_peak_contact_force":0.29957,"subtask_id":"place_at_goal","tcp_end":[0.64345,0.15255,0.2002],"tcp_start":[0.62945,0.13753,0.26391],"tcp_to_object_dist_end":0.02344,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82171,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08366,"descend_to_grasp.grasp_offset_z":0.01001,"lift_object.lift_height":0.10515,"place_at_goal.descend_speed":0.05002,"place_at_goal.place_offset_x":-0.00243,"place_at_goal.place_offset_y":-0.00166,"place_at_goal.place_offset_z":0.02277,"transport_to_goal.transport_speed":0.5031},"optimized_scores":{"best_composite_score":0.4535,"best_fitness_score":0.9735,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.5268,0.02901,-0.00121],"force_p95":0.42224,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62116,"mean_force":0.09875,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51426,0.02939,0.0358]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10517.0,"contact_point_centroid":[0.51251,0.04842,0.08281],"force_p95":0.09785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34792,"mean_force":0.06252,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51161,0.02922,0.08027]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12403.0,"contact_point_centroid":[0.51344,0.01048,0.07989],"force_p95":0.08377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32315,"mean_force":0.0506,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51162,0.02923,0.07828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20438.0,"contact_point_centroid":[0.55369,0.08053,0.15968],"force_p95":0.08641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2152,"mean_force":0.04804,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55023,0.09878,0.15861]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03076,-0.00211],"force_p95":0.15412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21263,"mean_force":0.1309,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51717,0.02959,0.03545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2997.0,"contact_point_centroid":[0.58838,0.18693,0.16914],"force_p95":0.09201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19938,"mean_force":0.05964,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.59036,0.16781,0.1661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15125.0,"contact_point_centroid":[0.54961,0.11767,0.16037],"force_p95":0.1182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19054,"mean_force":0.07018,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55013,0.0986,0.15852]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4246.0,"contact_point_centroid":[0.59532,0.14957,0.16619],"force_p95":0.08835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17143,"mean_force":0.04415,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.59041,0.16796,0.1651]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5273.0,"contact_point_centroid":[0.51713,0.01048,0.03608],"force_p95":0.06704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16741,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51592,0.02951,0.03403]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51085,0.01395,0.20995]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52313,0.02913,0.08217]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4221.0,"contact_point_centroid":[0.51661,0.04884,0.03681],"force_p95":0.08127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08435,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51592,0.02951,0.03404]}],"total_contact_groups":12},"final_pose_error":0.00978,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5986,0.17488,0.11502],"final_tcp_position":[0.59297,0.17285,0.1373],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.62116,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52414,0.02835,0.12097],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":960.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52463,0.03008,0.04401],"tcp_start":[0.52414,0.02835,0.12097],"tcp_to_object_dist_end":0.01894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03009,0.02561],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18413,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15203,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11294.0,"raw_peak_contact_force":0.21263,"tcp_end":[0.51589,0.02951,0.034],"tcp_start":[0.52463,0.03008,0.04401],"tcp_to_object_dist_end":0.01681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.52407,0.02984,0.11227],"object_pos_start":[0.53044,0.03009,0.02561],"object_to_goal_dist_end":0.16775,"object_to_goal_dist_start":0.18413,"object_z_max":0.11216,"peak_contact_force":0.11249,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23068.0,"raw_peak_contact_force":0.62116,"tcp_end":[0.51171,0.02924,0.12692],"tcp_start":[0.51589,0.02951,0.034],"tcp_to_object_dist_end":0.01918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59597,0.1658,0.17196],"object_pos_start":[0.52407,0.02984,0.11227],"object_to_goal_dist_end":0.06538,"object_to_goal_dist_start":0.16775,"object_z_max":0.17191,"peak_contact_force":0.09672,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35563.0,"raw_peak_contact_force":0.2152,"tcp_end":[0.58971,0.16393,0.19286],"tcp_start":[0.51171,0.02924,0.12692],"tcp_to_object_dist_end":0.02189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.5986,0.17488,0.11502],"object_pos_start":[0.59597,0.1658,0.17196],"object_to_goal_dist_end":0.00839,"object_to_goal_dist_start":0.06538,"object_z_max":0.17196,"peak_contact_force":0.09073,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7243.0,"raw_peak_contact_force":0.19938,"subtask_id":"place_at_goal","tcp_end":[0.59297,0.17285,0.1373],"tcp_start":[0.58971,0.16393,0.19286],"tcp_to_object_dist_end":0.02307,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```