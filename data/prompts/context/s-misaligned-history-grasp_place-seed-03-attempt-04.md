## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4537 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4737 | 0.94 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.2658 | 0.45 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5  | 0.0374 | 0.17 | ✅ accepted |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3  | 0.4535 | 1.00 | ❌ rejected |

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
| approach_object | 1.00 | 1.00 | 0.1610 |
| descend_to_grasp | 1.00 | 1.00 | 0.1008 |
| grasp_object | 1.00 | 1.00 | 0.0128 |
| lift_object | 1.00 | 1.00 | 0.1186 |
| transport_to_goal | 0.67 | 1.00 | 0.1702 |
| place_at_goal | 1.00 | 1.00 | 0.1035 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.145) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.507, 0.002, 0.145)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.002, 0.044)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.667 | 0.141 | 0.180 |
| lift_object | lift | 1.00 / step_budget | (0.497, 0.002, 0.035)→(0.493, 0.002, 0.154) | (0.511, 0.002, 0.026)→(0.504, 0.002, 0.137) | 0.246→0.221 | 1.00 / 35.333 | 0.093 | 0.592 |
| transport_to_goal | approach | 0.67 / step_budget | (0.493, 0.002, 0.154)→(0.583, 0.130, 0.214) | (0.504, 0.002, 0.137)→(0.587, 0.131, 0.192) | 0.221→0.096 | 1.00 / 39.667 | 0.084 | 0.205 |
| place_at_goal | descend | 1.00 / step_budget | (0.583, 0.130, 0.214)→(0.631, 0.188, 0.157) | (0.587, 0.131, 0.192)→(0.631, 0.190, 0.131) | 0.096→0.014 | 1.00 / 33.667 | 0.097 | 0.289 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.185
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.717
- phase_breakdown.place_at_goal_score: 0.716
- phase_breakdown.pre_grasp_score: 0.720
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.454
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: place_at_goal.place_offset_z
- **Final σ (mean)**: 0.486


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10156,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11503,"descend_to_grasp.grasp_offset_z":0.01012,"lift_object.lift_height":0.13339,"place_at_goal.descend_speed":0.26952,"place_at_goal.place_offset_x":0.01422,"place_at_goal.place_offset_y":0.01148,"place_at_goal.place_offset_z":0.03,"transport_to_goal.transport_speed":0.14556},"optimized_scores":{"best_composite_score":0.45335,"best_fitness_score":0.97335,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.45532,-0.02525,-0.00113],"force_p95":0.31563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52224,"mean_force":0.08119,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44457,-0.02563,0.03902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18433.0,"contact_point_centroid":[0.58092,0.12704,0.15539],"force_p95":0.09193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36097,"mean_force":0.05524,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.57712,0.14545,0.15627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15242.0,"contact_point_centroid":[0.57312,0.16336,0.15762],"force_p95":0.10444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31496,"mean_force":0.0645,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.57639,0.1446,0.15652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13767.0,"contact_point_centroid":[0.44182,-0.04474,0.10039],"force_p95":0.07939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28513,"mean_force":0.05536,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44201,-0.02554,0.09763]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16096.0,"contact_point_centroid":[0.44347,-0.00652,0.09901],"force_p95":0.07392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28361,"mean_force":0.04866,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44202,-0.02554,0.09723]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02638,-0.00205],"force_p95":0.13964,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17383,"mean_force":0.12674,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44712,-0.0257,0.03827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19686.0,"contact_point_centroid":[0.49046,0.01734,0.17054],"force_p95":0.07664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16443,"mean_force":0.04974,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4887,0.03641,0.16857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19538.0,"contact_point_centroid":[0.48556,0.05199,0.16993],"force_p95":0.0735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16264,"mean_force":0.0501,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48592,0.03293,0.16785]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47896,-0.01152,0.22773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.44692,-0.00657,0.03861],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12713,"mean_force":0.04133,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44595,-0.02567,0.03716]},{"body_a":"world","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45512,-0.02479,0.09941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4407.0,"contact_point_centroid":[0.44536,-0.04494,0.03994],"force_p95":0.07945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08954,"mean_force":0.04917,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44596,-0.02567,0.03716]}],"total_contact_groups":12},"final_pose_error":0.01904,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62719,0.20866,0.10842],"final_tcp_position":[0.63086,0.20769,0.13807],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.52224,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1776.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.4587,-0.02377,0.15451],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1408.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45405,-0.0259,0.04498],"tcp_start":[0.4587,-0.02377,0.15451],"tcp_to_object_dist_end":0.01949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02615,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30363,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13953,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11516.0,"raw_peak_contact_force":0.17383,"tcp_end":[0.44593,-0.02567,0.03713],"tcp_start":[0.45405,-0.0259,0.04498],"tcp_to_object_dist_end":0.01691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.45185,-0.02619,0.14098],"object_pos_start":[0.45847,-0.02615,0.02581],"object_to_goal_dist_end":0.29572,"object_to_goal_dist_start":0.30363,"object_z_max":0.14086,"peak_contact_force":0.07865,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29989.0,"raw_peak_contact_force":0.52224,"tcp_end":[0.44225,-0.02554,0.15926],"tcp_start":[0.44593,-0.02567,0.03713],"tcp_to_object_dist_end":0.02066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52879,0.08656,0.15755],"object_pos_start":[0.45185,-0.02619,0.14098],"object_to_goal_dist_end":0.16418,"object_to_goal_dist_start":0.29572,"object_z_max":0.15754,"peak_contact_force":0.0799,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39224.0,"raw_peak_contact_force":0.16443,"tcp_end":[0.52853,0.0859,0.17924],"tcp_start":[0.44225,-0.02554,0.15926],"tcp_to_object_dist_end":0.0217,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62719,0.20866,0.10842],"object_pos_start":[0.52879,0.08656,0.15755],"object_to_goal_dist_end":0.00643,"object_to_goal_dist_start":0.16418,"object_z_max":0.15755,"peak_contact_force":0.1169,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33675.0,"raw_peak_contact_force":0.36097,"subtask_id":"place_at_goal","tcp_end":[0.63086,0.20769,0.13807],"tcp_start":[0.52853,0.0859,0.17924],"tcp_to_object_dist_end":0.02989,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01587,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10809,"descend_to_grasp.grasp_offset_z":0.01018,"lift_object.lift_height":0.13927,"place_at_goal.descend_speed":0.2452,"place_at_goal.place_offset_x":0.01513,"place_at_goal.place_offset_y":0.01571,"place_at_goal.place_offset_z":0.02417,"transport_to_goal.transport_speed":0.55308},"optimized_scores":{"best_composite_score":0.45371,"best_fitness_score":0.97371,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.54035,0.00078,-0.00114],"force_p95":0.47047,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63065,"mean_force":0.10026,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52793,0.00079,0.03543]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13865.0,"contact_point_centroid":[0.52679,0.01986,0.0982],"force_p95":0.08326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35168,"mean_force":0.05808,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52524,0.00075,0.09601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15066.0,"contact_point_centroid":[0.52677,-0.01825,0.09605],"force_p95":0.08026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33028,"mean_force":0.05416,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52527,0.00075,0.09428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4605.0,"contact_point_centroid":[0.6402,0.17264,0.24107],"force_p95":0.09047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29638,"mean_force":0.05812,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6423,0.15368,0.23735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5626.0,"contact_point_centroid":[0.64682,0.135,0.23801],"force_p95":0.08949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23427,"mean_force":0.05076,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.64213,0.15347,0.23774]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18851.0,"contact_point_centroid":[0.58244,0.0547,0.21423],"force_p95":0.08476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22676,"mean_force":0.05442,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57889,0.07314,0.2138]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14817.0,"contact_point_centroid":[0.57904,0.09185,0.21556],"force_p95":0.10606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21237,"mean_force":0.06944,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57866,0.07282,0.21357]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15375,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53081,0.00085,0.03528]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51709,0.00047,0.2217]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53622,0.00097,0.09395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53076,-0.01822,0.03546],"force_p95":0.0686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10192,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52954,0.00083,0.0338]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53083,0.02004,0.03635],"force_p95":0.07522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09584,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52954,0.00083,0.03381]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65798,0.17046,0.18873],"final_tcp_position":[0.65488,0.16802,0.21334],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.63065,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53678,0.00097,0.14464],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53838,0.00101,0.04422],"tcp_start":[0.53678,0.00097,0.14464],"tcp_to_object_dist_end":0.01914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00106,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25032,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13338,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.15375,"tcp_end":[0.52951,0.00083,0.03377],"tcp_start":[0.53838,0.00101,0.04422],"tcp_to_object_dist_end":0.01666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.53649,0.00097,0.144],"object_pos_start":[0.54418,0.00106,0.02587],"object_to_goal_dist_end":0.19813,"object_to_goal_dist_start":0.25032,"object_z_max":0.14389,"peak_contact_force":0.08773,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29068.0,"raw_peak_contact_force":0.63065,"tcp_end":[0.5256,0.00076,0.16028],"tcp_start":[0.52951,0.00083,0.03377],"tcp_to_object_dist_end":0.01958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63769,0.14126,0.24507],"object_pos_start":[0.53649,0.00097,0.144],"object_to_goal_dist_end":0.05739,"object_to_goal_dist_start":0.19813,"object_z_max":0.24491,"peak_contact_force":0.07786,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33668.0,"raw_peak_contact_force":0.22676,"tcp_end":[0.63064,0.13887,0.26716],"tcp_start":[0.5256,0.00076,0.16028],"tcp_to_object_dist_end":0.02331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.65798,0.17046,0.18873],"object_pos_start":[0.63769,0.14126,0.24507],"object_to_goal_dist_end":0.01631,"object_to_goal_dist_start":0.05739,"object_z_max":0.24511,"peak_contact_force":0.08209,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10231.0,"raw_peak_contact_force":0.29638,"subtask_id":"place_at_goal","tcp_end":[0.65488,0.16802,0.21334],"tcp_start":[0.63064,0.13887,0.26716],"tcp_to_object_dist_end":0.02492,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02439,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09915,"descend_to_grasp.grasp_offset_z":0.01002,"lift_object.lift_height":0.11938,"place_at_goal.descend_speed":0.23428,"place_at_goal.place_offset_x":0.01277,"place_at_goal.place_offset_y":0.01546,"place_at_goal.place_offset_z":0.00897,"transport_to_goal.transport_speed":0.339},"optimized_scores":{"best_composite_score":0.45353,"best_fitness_score":0.97353,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.52679,0.0288,-0.0012],"force_p95":0.45122,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62289,"mean_force":0.09881,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51441,0.02942,0.03597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11624.0,"contact_point_centroid":[0.51266,0.04846,0.0897],"force_p95":0.10413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34926,"mean_force":0.06085,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51176,0.02926,0.08732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13617.0,"contact_point_centroid":[0.51366,0.01053,0.08696],"force_p95":0.08384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32487,"mean_force":0.05066,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51178,0.02926,0.08537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20769.0,"contact_point_centroid":[0.55446,0.0814,0.16765],"force_p95":0.08668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2228,"mean_force":0.04735,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55095,0.09969,0.16646]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03076,-0.00211],"force_p95":0.15345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21154,"mean_force":0.13069,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51728,0.02962,0.03561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4558.0,"contact_point_centroid":[0.59322,0.19436,0.15883],"force_p95":0.10162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21113,"mean_force":0.06393,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.59682,0.17561,0.15601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5966.0,"contact_point_centroid":[0.60123,0.1572,0.15625],"force_p95":0.09376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19982,"mean_force":0.05066,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.59689,0.17571,0.1557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15309.0,"contact_point_centroid":[0.55112,0.11994,0.16887],"force_p95":0.11806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19448,"mean_force":0.06969,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55164,0.10085,0.16694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5274.0,"contact_point_centroid":[0.51721,0.01051,0.03621],"force_p95":0.06724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16843,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51603,0.02954,0.03419]},{"body_a":"world","body_b":"grasp_target","contact_count":2148.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51081,0.01383,0.21781]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52311,0.02905,0.08988]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4216.0,"contact_point_centroid":[0.51668,0.04886,0.03698],"force_p95":0.08142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08431,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51603,0.02954,0.0342]}],"total_contact_groups":12},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60689,0.18973,0.09518],"final_tcp_position":[0.60651,0.18856,0.11959],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.62289,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2148.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.5241,0.02817,0.13637],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52475,0.03011,0.04419],"tcp_start":[0.5241,0.02817,0.13637],"tcp_to_object_dist_end":0.01907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03012,0.02562],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18411,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1515,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11290.0,"raw_peak_contact_force":0.21154,"tcp_end":[0.516,0.02953,0.03416],"tcp_start":[0.52475,0.03011,0.04419],"tcp_to_object_dist_end":0.01679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.52393,0.02992,0.12511],"object_pos_start":[0.53044,0.03012,0.02562],"object_to_goal_dist_end":0.16855,"object_to_goal_dist_start":0.18411,"object_z_max":0.12499,"peak_contact_force":0.11358,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25382.0,"raw_peak_contact_force":0.62289,"tcp_end":[0.51195,0.02928,0.14104],"tcp_start":[0.516,0.02953,0.03416],"tcp_to_object_dist_end":0.01994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59547,0.16572,0.17235],"object_pos_start":[0.52393,0.02992,0.12511],"object_to_goal_dist_end":0.06582,"object_to_goal_dist_start":0.16855,"object_z_max":0.17231,"peak_contact_force":0.09349,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36078.0,"raw_peak_contact_force":0.2228,"tcp_end":[0.5898,0.16405,0.1942],"tcp_start":[0.51195,0.02928,0.14104],"tcp_to_object_dist_end":0.02263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.60689,0.18973,0.09518],"object_pos_start":[0.59547,0.16572,0.17235],"object_to_goal_dist_end":0.01788,"object_to_goal_dist_start":0.06582,"object_z_max":0.17235,"peak_contact_force":0.09275,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10524.0,"raw_peak_contact_force":0.21113,"subtask_id":"place_at_goal","tcp_end":[0.60651,0.18856,0.11959],"tcp_start":[0.5898,0.16405,0.1942],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```