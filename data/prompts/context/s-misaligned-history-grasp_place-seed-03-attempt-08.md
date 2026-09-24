## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13  | 0.2431 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12  | 0.4709 | 0.88 | ❌ rejected |
| 6 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7  | 0.4119 | 0.94 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4535 | 1.00 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.2037 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.204) — your mutation base

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

- **Composite score**: 0.204
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1695 |
| descend_to_grasp | 1.00 | 1.00 | 0.0924 |
| grasp_object | 1.00 | 1.00 | 0.0128 |
| lift_object | 1.00 | 1.00 | 0.1000 |
| transport_to_goal | 1.00 | 1.00 | 0.2160 |
| place_at_goal | 1.00 | 1.00 | 0.0583 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.137) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.137)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 11.456 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.002, 0.044)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.000 | 0.142 | 0.181 |
| lift_object | lift | 1.00 / step_budget | (0.497, 0.002, 0.035)→(0.493, 0.002, 0.135) | (0.511, 0.002, 0.026)→(0.505, 0.002, 0.119) | 0.246→0.223 | 1.00 / 37.000 | 0.091 | 0.599 |
| transport_to_goal | approach | 1.00 / step_budget | (0.493, 0.002, 0.135)→(0.607, 0.159, 0.217) | (0.505, 0.002, 0.119)→(0.611, 0.161, 0.194) | 0.223→0.063 | 1.00 / 38.000 | 0.165 | 0.254 |
| place_at_goal | descend | 1.00 / step_budget | (0.607, 0.159, 0.217)→(0.624, 0.171, 0.163) | (0.611, 0.161, 0.194)→(0.627, 0.173, 0.139) | 0.063→0.014 | 1.00 / 31.667 | 0.098 | 0.252 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.421
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.650
- phase_breakdown.place_at_goal_score: 0.788
- phase_breakdown.pre_grasp_score: 0.330
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.204
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_to_grasp.grasp_offset_z
- **Final σ (mean)**: 0.375


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00775,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.06027,"approach_object.approach_tolerance":0.02262,"descend_to_grasp.descend_tolerance":0.04429,"descend_to_grasp.grasp_offset_z":0.01,"lift_object.lift_height":0.119,"lift_object.lift_tolerance":0.02868,"place_at_goal.descend_speed":0.14261,"place_at_goal.place_offset_x":-0.00587,"place_at_goal.place_offset_y":-0.00723,"place_at_goal.place_offset_z":0.02725,"place_at_goal.place_tolerance":0.02388,"transport_to_goal.transport_speed":0.37565,"transport_to_goal.transport_tolerance":0.03326},"optimized_scores":{"best_composite_score":0.20337,"best_fitness_score":0.97337,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.45519,-0.02506,-0.00112],"force_p95":0.3193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54278,"mean_force":0.08124,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44426,-0.02553,0.03866]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2506.0,"contact_point_centroid":[0.60334,0.20383,0.16965],"force_p95":0.1331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41294,"mean_force":0.08281,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.60797,0.18551,0.17027]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19121.0,"contact_point_centroid":[0.52611,0.06042,0.17109],"force_p95":0.07834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32417,"mean_force":0.05314,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5233,0.07933,0.16989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18750.0,"contact_point_centroid":[0.51552,0.09021,0.16961],"force_p95":0.07949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32407,"mean_force":0.05325,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51683,0.07131,0.16766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2944.0,"contact_point_centroid":[0.61178,0.16762,0.16663],"force_p95":0.12797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32291,"mean_force":0.07505,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.60805,0.18562,0.16993]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13922.0,"contact_point_centroid":[0.44348,-0.0065,0.09073],"force_p95":0.0759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28619,"mean_force":0.0499,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44168,-0.02545,0.08912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11355.0,"contact_point_centroid":[0.44188,-0.04465,0.09223],"force_p95":0.08095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28528,"mean_force":0.05907,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44169,-0.02545,0.08963]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02636,-0.00206],"force_p95":0.14178,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17668,"mean_force":0.12729,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44681,-0.02561,0.03787]},{"body_a":"world","body_b":"grasp_target","contact_count":2424.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47789,-0.01199,0.19979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5115.0,"contact_point_centroid":[0.44698,-0.00649,0.0382],"force_p95":0.06883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12742,"mean_force":0.0428,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44565,-0.02557,0.03676]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4544,-0.02507,0.07204]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4415.0,"contact_point_centroid":[0.44512,-0.04483,0.03955],"force_p95":0.07924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08539,"mean_force":0.04912,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44565,-0.02557,0.03676]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61441,0.19707,0.1149],"final_tcp_position":[0.61623,0.19543,0.14317],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.54278,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2424.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.4572,-0.02441,0.09972],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":756.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45373,-0.0258,0.04454],"tcp_start":[0.4572,-0.02441,0.09972],"tcp_to_object_dist_end":0.01915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02606,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30356,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14147,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11330.0,"raw_peak_contact_force":0.17668,"tcp_end":[0.44562,-0.02557,0.03673],"tcp_start":[0.45373,-0.0258,0.04454],"tcp_to_object_dist_end":0.0169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.4525,-0.02613,0.12617],"object_pos_start":[0.45848,-0.02606,0.02579],"object_to_goal_dist_end":0.2943,"object_to_goal_dist_start":0.30356,"object_z_max":0.12606,"peak_contact_force":0.07892,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25404.0,"raw_peak_contact_force":0.54278,"tcp_end":[0.44183,-0.02544,0.14448],"tcp_start":[0.44562,-0.02557,0.03673],"tcp_to_object_dist_end":0.02121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60035,0.17839,0.1709],"object_pos_start":[0.4525,-0.02613,0.12617],"object_to_goal_dist_end":0.07072,"object_to_goal_dist_start":0.2943,"object_z_max":0.17087,"peak_contact_force":0.32417,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37871.0,"raw_peak_contact_force":0.32417,"tcp_end":[0.60252,0.17734,0.19715],"tcp_start":[0.44183,-0.02544,0.14448],"tcp_to_object_dist_end":0.02636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.61441,0.19707,0.1149],"object_pos_start":[0.60035,0.17839,0.1709],"object_to_goal_dist_end":0.01928,"object_to_goal_dist_start":0.07072,"object_z_max":0.1709,"peak_contact_force":0.10985,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5450.0,"raw_peak_contact_force":0.41294,"subtask_id":"place_at_goal","tcp_end":[0.61623,0.19543,0.14317],"tcp_start":[0.60252,0.17734,0.19715],"tcp_to_object_dist_end":0.02838,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82258,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14927,"approach_object.approach_tolerance":0.01352,"descend_to_grasp.descend_tolerance":0.04909,"descend_to_grasp.grasp_offset_z":0.01002,"lift_object.lift_height":0.10806,"lift_object.lift_tolerance":0.04197,"place_at_goal.descend_speed":0.05093,"place_at_goal.place_offset_x":0.01131,"place_at_goal.place_offset_y":-0.00704,"place_at_goal.place_offset_z":0.02186,"place_at_goal.place_tolerance":0.02529,"transport_to_goal.transport_speed":0.45921,"transport_to_goal.transport_tolerance":0.03299},"optimized_scores":{"best_composite_score":0.20414,"best_fitness_score":0.97414,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.54057,0.00093,-0.00112],"force_p95":0.46448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62965,"mean_force":0.0992,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5281,0.0008,0.03523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10692.0,"contact_point_centroid":[0.5268,0.01989,0.08313],"force_p95":0.0815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35261,"mean_force":0.05777,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52538,0.00075,0.08089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11786.0,"contact_point_centroid":[0.52672,-0.01827,0.08043],"force_p95":0.07767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33113,"mean_force":0.05321,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52542,0.00075,0.07848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17775.0,"contact_point_centroid":[0.57992,0.05183,0.19534],"force_p95":0.08913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21436,"mean_force":0.05877,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57671,0.07058,0.19444]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17559.0,"contact_point_centroid":[0.57378,0.08634,0.19293],"force_p95":0.08419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19263,"mean_force":0.05807,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57422,0.06744,0.19124]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15358,"mean_force":0.12535,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53101,0.00086,0.03505]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51684,0.00047,0.24185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2964.0,"contact_point_centroid":[0.63458,0.1602,0.24106],"force_p95":0.09483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13723,"mean_force":0.0663,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63723,0.14137,0.23853]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.64279,0.12353,0.23611],"force_p95":0.0886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13462,"mean_force":0.05465,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6381,0.14181,0.23649]},{"body_a":"world","body_b":"grasp_target","contact_count":1700.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53608,0.00097,0.11379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4997.0,"contact_point_centroid":[0.53068,-0.01822,0.03557],"force_p95":0.06743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10182,"mean_force":0.0434,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52974,0.00083,0.03357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53096,0.02007,0.03613],"force_p95":0.07573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09581,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52974,0.00083,0.03357]}],"total_contact_groups":12},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65623,0.15039,0.19199],"final_tcp_position":[0.64965,0.14743,0.21375],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.62965,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53628,0.00096,0.18491],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1700.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53859,0.00102,0.04399],"tcp_start":[0.53628,0.00096,0.18491],"tcp_to_object_dist_end":0.01886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00113,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25028,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13228,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10946.0,"raw_peak_contact_force":0.15358,"tcp_end":[0.52971,0.00083,0.03353],"tcp_start":[0.53859,0.00102,0.04399],"tcp_to_object_dist_end":0.01638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53739,0.00083,0.11484],"object_pos_start":[0.54418,0.00113,0.02587],"object_to_goal_dist_end":0.20664,"object_to_goal_dist_start":0.25028,"object_z_max":0.11472,"peak_contact_force":0.08087,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22620.0,"raw_peak_contact_force":0.62965,"tcp_end":[0.5255,0.00076,0.12895],"tcp_start":[0.52971,0.00083,0.03353],"tcp_to_object_dist_end":0.01844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63549,0.13912,0.24074],"object_pos_start":[0.53739,0.00083,0.11484],"object_to_goal_dist_end":0.05451,"object_to_goal_dist_start":0.20664,"object_z_max":0.24068,"peak_contact_force":0.07668,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35334.0,"raw_peak_contact_force":0.21436,"tcp_end":[0.62868,0.13679,0.26131],"tcp_start":[0.5255,0.00076,0.12895],"tcp_to_object_dist_end":0.02179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.65623,0.15039,0.19199],"object_pos_start":[0.63549,0.13912,0.24074],"object_to_goal_dist_end":0.01158,"object_to_goal_dist_start":0.05451,"object_z_max":0.24074,"peak_contact_force":0.092,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6740.0,"raw_peak_contact_force":0.13723,"subtask_id":"place_at_goal","tcp_end":[0.64965,0.14743,0.21375],"tcp_start":[0.62868,0.13679,0.26131],"tcp_to_object_dist_end":0.02292,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01653,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08767,"approach_object.approach_tolerance":0.04433,"descend_to_grasp.descend_tolerance":0.04966,"descend_to_grasp.grasp_offset_z":0.01001,"lift_object.lift_height":0.10916,"lift_object.lift_tolerance":0.044,"place_at_goal.descend_speed":0.15055,"place_at_goal.place_offset_x":0.01472,"place_at_goal.place_offset_y":-0.0056,"place_at_goal.place_offset_z":0.02132,"place_at_goal.place_tolerance":0.02862,"transport_to_goal.transport_speed":0.28554,"transport_to_goal.transport_tolerance":0.02551},"optimized_scores":{"best_composite_score":0.20354,"best_fitness_score":0.97354,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.52679,0.02879,-0.00121],"force_p95":0.45241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6247,"mean_force":0.09949,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51432,0.0294,0.03579]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10616.0,"contact_point_centroid":[0.51255,0.04844,0.08472],"force_p95":0.10182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34927,"mean_force":0.06098,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51166,0.02924,0.08226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12405.0,"contact_point_centroid":[0.51355,0.0105,0.08178],"force_p95":0.08414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32501,"mean_force":0.05078,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51168,0.02924,0.08017]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20345.0,"contact_point_centroid":[0.55395,0.08063,0.1617],"force_p95":0.08567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22294,"mean_force":0.04831,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55031,0.09884,0.16062]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03076,-0.00211],"force_p95":0.15388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21228,"mean_force":0.13082,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5172,0.0296,0.03544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3478.0,"contact_point_centroid":[0.59554,0.18606,0.16493],"force_p95":0.09735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20445,"mean_force":0.06278,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.59745,0.16694,0.16194]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14117.0,"contact_point_centroid":[0.55064,0.1187,0.16264],"force_p95":0.11805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19858,"mean_force":0.07479,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55071,0.09952,0.16095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5071.0,"contact_point_centroid":[0.60197,0.14842,0.16331],"force_p95":0.091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17552,"mean_force":0.0467,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.5973,0.16689,0.16233]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5274.0,"contact_point_centroid":[0.51715,0.01049,0.03606],"force_p95":0.06711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16763,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51594,0.02952,0.03402]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51085,0.01393,0.21193]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52312,0.02912,0.08408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4219.0,"contact_point_centroid":[0.51662,0.04885,0.0368],"force_p95":0.08132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08432,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51595,0.02952,0.03403]}],"total_contact_groups":12},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.61164,0.17199,0.10959],"final_tcp_position":[0.60737,0.17027,0.13277],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":34.12267,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52414,0.02831,0.1249],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":34.12267,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52466,0.03009,0.044],"tcp_start":[0.52414,0.02831,0.1249],"tcp_to_object_dist_end":0.01892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.0301,0.02562],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18412,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15184,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11293.0,"raw_peak_contact_force":0.21228,"tcp_end":[0.51591,0.02952,0.03398],"tcp_start":[0.52466,0.03009,0.044],"tcp_to_object_dist_end":0.01678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.52413,0.02992,0.11548],"object_pos_start":[0.53044,0.0301,0.02562],"object_to_goal_dist_end":0.16777,"object_to_goal_dist_start":0.18412,"object_z_max":0.11536,"peak_contact_force":0.11286,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23162.0,"raw_peak_contact_force":0.6247,"tcp_end":[0.51177,0.02925,0.13068],"tcp_start":[0.51591,0.02952,0.03398],"tcp_to_object_dist_end":0.0196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59634,0.16585,0.17181],"object_pos_start":[0.52413,0.02992,0.11548],"object_to_goal_dist_end":0.06519,"object_to_goal_dist_start":0.16777,"object_z_max":0.17176,"peak_contact_force":0.09383,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34462.0,"raw_peak_contact_force":0.22294,"tcp_end":[0.58978,0.16405,0.19326],"tcp_start":[0.51177,0.02925,0.13068],"tcp_to_object_dist_end":0.0225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.61164,0.17199,0.10959],"object_pos_start":[0.59634,0.16585,0.17181],"object_to_goal_dist_end":0.01216,"object_to_goal_dist_start":0.06519,"object_z_max":0.17181,"peak_contact_force":0.09191,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8549.0,"raw_peak_contact_force":0.20445,"subtask_id":"place_at_goal","tcp_end":[0.60737,0.17027,0.13277],"tcp_start":[0.58978,0.16405,0.19326],"tcp_to_object_dist_end":0.02363,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```