## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4528 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4537 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4536 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.0135 | 0.43 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11  | 0.3912 | 0.88 | ❌ rejected |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.391) — your mutation base

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

- **Composite score**: 0.391
- **task_score** (E): 0.883
- **fitness_score**: 0.911  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1514 |
| descend_to_grasp | 1.00 | 1.00 | 0.1064 |
| grasp_object | 1.00 | 1.00 | 0.0127 |
| lift_object | 1.00 | 1.00 | 0.1131 |
| transport_to_goal | 0.67 | 1.00 | 0.1986 |
| place_at_goal | 1.00 | 1.00 | 0.0744 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.155) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.155)→(0.506, 0.002, 0.049) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.002, 0.049)→(0.497, 0.002, 0.039) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.667 | 0.141 | 0.182 |
| lift_object | lift | 1.00 / step_budget | (0.497, 0.002, 0.039)→(0.493, 0.002, 0.152) | (0.511, 0.002, 0.026)→(0.504, 0.002, 0.132) | 0.246→0.226 | 1.00 / 36.333 | 105.147 | 0.528 |
| transport_to_goal | approach | 0.67 / step_budget | (0.493, 0.002, 0.152)→(0.601, 0.152, 0.211) | (0.504, 0.002, 0.132)→(0.602, 0.153, 0.184) | 0.226→0.066 | 1.00 / 30.667 | 0.124 | 0.285 |
| place_at_goal | descend | 1.00 / step_budget | (0.601, 0.152, 0.211)→(0.618, 0.178, 0.150) | (0.602, 0.153, 0.184)→(0.616, 0.179, 0.118) | 0.066→0.024 | 1.00 / 22.667 | 3253.535 | 0.324 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.272
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.695
- phase_breakdown.place_at_goal_score: 0.784
- phase_breakdown.pre_grasp_score: 0.490
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.378
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.383


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.168,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10946,"descend_to_grasp.grasp_offset_z":0.01064,"lift_object.lift_height":0.12897,"place_at_goal.descend_speed":0.24386,"place_at_goal.place_offset_x":0.00939,"place_at_goal.place_offset_y":-0.00494,"place_at_goal.place_offset_z":0.01184,"transport_to_goal.transport_speed":0.43727},"optimized_scores":{"best_composite_score":0.37773,"best_fitness_score":0.89773,"best_task_score":0.84982},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.45533,-0.02525,-0.00112],"force_p95":0.31239,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50605,"mean_force":0.07998,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44456,-0.02562,0.03954]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3040.0,"contact_point_centroid":[0.61152,0.20603,0.16006],"force_p95":0.14765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43872,"mean_force":0.09502,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61516,0.18749,0.1616]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18779.0,"contact_point_centroid":[0.5243,0.0581,0.17629],"force_p95":0.08331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35845,"mean_force":0.05408,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5217,0.07697,0.17531]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3538.0,"contact_point_centroid":[0.62051,0.17039,0.15571],"force_p95":0.13156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34449,"mean_force":0.0842,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61563,0.18783,0.16051]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17944.0,"contact_point_centroid":[0.51429,0.08824,0.17523],"force_p95":0.08428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31704,"mean_force":0.05546,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51555,0.06933,0.17356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12684.0,"contact_point_centroid":[0.44207,-0.04474,0.0981],"force_p95":0.08069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28539,"mean_force":0.05763,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.442,-0.02554,0.09544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15294.0,"contact_point_centroid":[0.44365,-0.00656,0.09668],"force_p95":0.07512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2832,"mean_force":0.04936,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.442,-0.02554,0.09499]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02638,-0.00205],"force_p95":0.13966,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17392,"mean_force":0.12676,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44711,-0.0257,0.03878]},{"body_a":"world","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47881,-0.01159,0.22484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.44692,-0.00656,0.03912],"force_p95":0.06841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12769,"mean_force":0.04134,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44595,-0.02566,0.03767]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45503,-0.02483,0.09683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4407.0,"contact_point_centroid":[0.44535,-0.04493,0.04045],"force_p95":0.07946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08941,"mean_force":0.04917,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44595,-0.02566,0.03768]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62473,0.19861,0.09234],"final_tcp_position":[0.63067,0.19873,0.12642],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1840.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.4585,-0.02386,0.1489],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45404,-0.02589,0.04549],"tcp_start":[0.4585,-0.02386,0.1489],"tcp_to_object_dist_end":0.01999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02615,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30363,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13955,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11516.0,"raw_peak_contact_force":0.17392,"tcp_end":[0.44592,-0.02566,0.03765],"tcp_start":[0.45404,-0.02589,0.04549],"tcp_to_object_dist_end":0.01726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.45218,-0.02619,0.13614],"object_pos_start":[0.45848,-0.02615,0.02581],"object_to_goal_dist_end":0.29512,"object_to_goal_dist_start":0.30363,"object_z_max":0.13602,"peak_contact_force":0.07884,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28104.0,"raw_peak_contact_force":0.50605,"tcp_end":[0.44221,-0.02553,0.15534],"tcp_start":[0.44592,-0.02566,0.03765],"tcp_to_object_dist_end":0.02164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60045,0.17849,0.17096],"object_pos_start":[0.45218,-0.02619,0.13614],"object_to_goal_dist_end":0.07068,"object_to_goal_dist_start":0.29512,"object_z_max":0.17092,"peak_contact_force":0.17599,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36723.0,"raw_peak_contact_force":0.35845,"tcp_end":[0.60286,0.17756,0.19862],"tcp_start":[0.44221,-0.02553,0.15534],"tcp_to_object_dist_end":0.02778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.62473,0.19861,0.09234],"object_pos_start":[0.60045,0.17849,0.17096],"object_to_goal_dist_end":0.02441,"object_to_goal_dist_start":0.07068,"object_z_max":0.17096,"peak_contact_force":9760.30694,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6578.0,"raw_peak_contact_force":0.43872,"subtask_id":"place_at_goal","tcp_end":[0.63067,0.19873,0.12642],"tcp_start":[0.60286,0.17756,0.19862],"tcp_to_object_dist_end":0.0346,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01709,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11478,"descend_to_grasp.grasp_offset_z":0.02221,"lift_object.lift_height":0.10276,"place_at_goal.descend_speed":0.19204,"place_at_goal.place_offset_x":-0.00622,"place_at_goal.place_offset_y":0.01031,"place_at_goal.place_offset_z":0.01703,"transport_to_goal.transport_speed":0.2142},"optimized_scores":{"best_composite_score":0.34218,"best_fitness_score":0.86218,"best_task_score":0.80008},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54108,0.00036,-0.00114],"force_p95":0.32153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45291,"mean_force":0.07507,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52815,0.00081,0.04751]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4180.0,"contact_point_centroid":[0.62277,0.12012,0.2121],"force_p95":0.13599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31996,"mean_force":0.09887,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62204,0.13873,0.21706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10907.0,"contact_point_centroid":[0.52649,-0.01837,0.09087],"force_p95":0.07958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31676,"mean_force":0.05469,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52553,0.00076,0.08949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11358.0,"contact_point_centroid":[0.52702,0.01986,0.08996],"force_p95":0.07698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31339,"mean_force":0.05311,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52555,0.00076,0.08831]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4887.0,"contact_point_centroid":[0.61723,0.15706,0.21336],"force_p95":0.12168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30312,"mean_force":0.08382,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6223,0.13928,0.21663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16341.0,"contact_point_centroid":[0.56578,0.0353,0.18126],"force_p95":0.09929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26078,"mean_force":0.0608,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56371,0.05401,0.18222]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16066.0,"contact_point_centroid":[0.56369,0.07295,0.18241],"force_p95":0.09838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23804,"mean_force":0.06068,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56379,0.05411,0.18232]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00116,-0.00204],"force_p95":0.13387,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16106,"mean_force":0.12578,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53104,0.00086,0.04731]},{"body_a":"world","body_b":"grasp_target","contact_count":2012.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51706,0.00047,0.22501]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53629,0.00097,0.1033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4966.0,"contact_point_centroid":[0.53107,-0.01832,0.04784],"force_p95":0.06679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08824,"mean_force":0.04379,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52979,0.00084,0.04583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4761.0,"contact_point_centroid":[0.53095,0.02006,0.04835],"force_p95":0.06885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08648,"mean_force":0.04586,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52979,0.00084,0.04583]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62976,0.1649,0.16365],"final_tcp_position":[0.6357,0.16384,0.20132],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.45291,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2012.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53674,0.00097,0.15115],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53844,0.00101,0.05626],"tcp_start":[0.53674,0.00097,0.15115],"tcp_to_object_dist_end":0.03081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00092,0.02584],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25041,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1338,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11527.0,"raw_peak_contact_force":0.16106,"tcp_end":[0.52976,0.00084,0.04579],"tcp_start":[0.53844,0.00101,0.05626],"tcp_to_object_dist_end":0.02463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.53493,0.001,0.11065],"object_pos_start":[0.54422,0.00092,0.02584],"object_to_goal_dist_end":0.2094,"object_to_goal_dist_start":0.25041,"object_z_max":0.11053,"peak_contact_force":0.07638,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22410.0,"raw_peak_contact_force":0.45291,"tcp_end":[0.52562,0.00077,0.13592],"tcp_start":[0.52976,0.00084,0.04579],"tcp_to_object_dist_end":0.02694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61174,0.11432,0.20644],"object_pos_start":[0.53493,0.001,0.11065],"object_to_goal_dist_end":0.05864,"object_to_goal_dist_start":0.2094,"object_z_max":0.20634,"peak_contact_force":0.1016,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32407.0,"raw_peak_contact_force":0.26078,"tcp_end":[0.60985,0.1128,0.23901],"tcp_start":[0.52562,0.00077,0.13592],"tcp_to_object_dist_end":0.03266,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":432.0,"n_steps_budget":1000.0,"object_pos_end":[0.62976,0.1649,0.16365],"object_pos_start":[0.61174,0.11432,0.20644],"object_to_goal_dist_end":0.03346,"object_to_goal_dist_start":0.05864,"object_z_max":0.20645,"peak_contact_force":0.20134,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9067.0,"raw_peak_contact_force":0.31996,"subtask_id":"place_at_goal","tcp_end":[0.6357,0.16384,0.20132],"tcp_start":[0.60985,0.1128,0.23901],"tcp_to_object_dist_end":0.03815,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02362,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12827,"descend_to_grasp.grasp_offset_z":0.01004,"lift_object.lift_height":0.14389,"place_at_goal.descend_speed":0.29119,"place_at_goal.place_offset_x":-0.00816,"place_at_goal.place_offset_y":-0.00424,"place_at_goal.place_offset_z":0.0063,"transport_to_goal.transport_speed":0.42892},"optimized_scores":{"best_composite_score":0.45376,"best_fitness_score":0.97376,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.52678,0.02882,-0.00121],"force_p95":0.45088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62468,"mean_force":0.09904,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51457,0.02946,0.03594]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14025.0,"contact_point_centroid":[0.51287,0.04851,0.10088],"force_p95":0.10719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34944,"mean_force":0.06174,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51196,0.0293,0.09862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16656.0,"contact_point_centroid":[0.51386,0.01059,0.09897],"force_p95":0.0832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32493,"mean_force":0.05032,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51198,0.0293,0.09738]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20924.0,"contact_point_centroid":[0.55537,0.08237,0.18077],"force_p95":0.08758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23577,"mean_force":0.04716,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55184,0.10067,0.17952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3184.0,"contact_point_centroid":[0.58586,0.18642,0.16348],"force_p95":0.09837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21458,"mean_force":0.06512,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58857,0.16749,0.16126]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.0021],"force_p95":0.1527,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21079,"mean_force":0.13054,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51744,0.02966,0.03559]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15043.0,"contact_point_centroid":[0.5524,0.12149,0.18183],"force_p95":0.11828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20221,"mean_force":0.07052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55283,0.10234,0.17995]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4387.0,"contact_point_centroid":[0.59316,0.14927,0.16034],"force_p95":0.09343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18281,"mean_force":0.05021,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58855,0.1676,0.16008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5276.0,"contact_point_centroid":[0.51733,0.01055,0.03615],"force_p95":0.06751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16882,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51619,0.02958,0.03417]},{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51076,0.0136,0.23218]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5231,0.02889,0.10402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4214.0,"contact_point_centroid":[0.51679,0.0489,0.03697],"force_p95":0.08163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08425,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51619,0.02958,0.03417]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59226,0.17306,0.09831],"final_tcp_position":[0.5886,0.17132,0.12255],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":315.2852,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1808.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52398,0.02781,0.16497],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52491,0.03015,0.04416],"tcp_start":[0.52398,0.02781,0.16497],"tcp_to_object_dist_end":0.019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03015,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18408,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15092,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11290.0,"raw_peak_contact_force":0.21079,"tcp_end":[0.51616,0.02957,0.03413],"tcp_start":[0.52491,0.03015,0.04416],"tcp_to_object_dist_end":0.01663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.52362,0.02985,0.14875],"object_pos_start":[0.53044,0.03015,0.02563],"object_to_goal_dist_end":0.17275,"object_to_goal_dist_start":0.18408,"object_z_max":0.14863,"peak_contact_force":315.2852,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30822.0,"raw_peak_contact_force":0.62468,"tcp_end":[0.51234,0.02933,0.16551],"tcp_start":[0.51616,0.02957,0.03413],"tcp_to_object_dist_end":0.02021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5952,0.16619,0.17398],"object_pos_start":[0.52362,0.02985,0.14875],"object_to_goal_dist_end":0.06734,"object_to_goal_dist_start":0.17275,"object_z_max":0.17396,"peak_contact_force":0.09345,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35967.0,"raw_peak_contact_force":0.23577,"tcp_end":[0.59019,0.16469,0.19658],"tcp_start":[0.51234,0.02933,0.16551],"tcp_to_object_dist_end":0.0232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.59226,0.17306,0.09831],"object_pos_start":[0.5952,0.16619,0.17398],"object_to_goal_dist_end":0.01457,"object_to_goal_dist_start":0.06734,"object_z_max":0.17398,"peak_contact_force":0.09764,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7571.0,"raw_peak_contact_force":0.21458,"subtask_id":"place_at_goal","tcp_end":[0.5886,0.17132,0.12255],"tcp_start":[0.59019,0.16469,0.19658],"tcp_to_object_dist_end":0.02458,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```