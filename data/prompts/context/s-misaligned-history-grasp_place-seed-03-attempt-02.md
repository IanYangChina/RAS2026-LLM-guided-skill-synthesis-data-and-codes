## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.2658 | 0.45 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5  | 0.0374 | 0.17 | ✅ accepted |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3  | 0.4737 | 0.94 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.941, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.474) — your mutation base

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
      - 0.05
      - 0.2
      default: 0.1
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
    - place_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_offset_y: status=consumed; consumers=target.offset.y (replace)
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.474
- **task_score** (E): 0.941
- **fitness_score**: 0.944  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1757 |
| descend_to_grasp | 1.00 | 1.00 | 0.0859 |
| grasp_object | 1.00 | 1.00 | 0.0128 |
| lift_object | 1.00 | 1.00 | 0.1160 |
| transport_to_goal | 0.00 | 1.00 | 0.1386 |
| place_at_goal | 1.00 | 1.00 | 0.0978 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.130) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.130)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.002, 0.044)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.000 | 0.142 | 0.182 |
| lift_object | lift | 1.00 / step_budget | (0.497, 0.002, 0.035)→(0.493, 0.002, 0.151) | (0.511, 0.002, 0.026)→(0.504, 0.002, 0.134) | 0.246→0.222 | 1.00 / 36.000 | 0.091 | 0.604 |
| transport_to_goal | approach | 0.00 / step_budget | (0.493, 0.002, 0.151)→(0.567, 0.107, 0.194) | (0.504, 0.002, 0.134)→(0.572, 0.108, 0.172) | 0.222→0.100 | 1.00 / 35.667 | 0.066 | 0.189 |
| place_at_goal | descend | 1.00 / step_budget | (0.567, 0.107, 0.194)→(0.620, 0.176, 0.154) | (0.572, 0.108, 0.172)→(0.618, 0.177, 0.125) | 0.100→0.017 | 1.00 / 31.333 | 0.105 | 0.252 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.204
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.672
- phase_breakdown.place_at_goal_score: 0.820
- phase_breakdown.pre_grasp_score: 0.324
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.503
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.398


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8951,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.05023,"descend_to_grasp.grasp_offset_z":0.01016,"lift_object.lift_height":0.13586,"place_at_goal.place_offset_x":0.00165,"place_at_goal.place_offset_y":0.00408,"place_at_goal.place_offset_z":0.01174,"transport_to_goal.transport_speed":0.19968},"optimized_scores":{"best_composite_score":0.41399,"best_fitness_score":0.88399,"best_task_score":0.82194},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.45522,-0.02507,-0.00112],"force_p95":0.30937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56531,"mean_force":0.08293,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44422,-0.02548,0.03893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16647.0,"contact_point_centroid":[0.44323,-0.00639,0.10005],"force_p95":0.07385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28469,"mean_force":0.04885,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44168,-0.02539,0.09829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14096.0,"contact_point_centroid":[0.44155,-0.04459,0.10143],"force_p95":0.07983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28063,"mean_force":0.0561,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44169,-0.02539,0.0987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17421.0,"contact_point_centroid":[0.58288,0.13334,0.15055],"force_p95":0.09702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25251,"mean_force":0.05712,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.57905,0.15169,0.15177]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14539.0,"contact_point_centroid":[0.57558,0.17042,0.15266],"force_p95":0.10493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23956,"mean_force":0.06617,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.57909,0.15174,0.15174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19764.0,"contact_point_centroid":[0.4986,0.02741,0.17445],"force_p95":0.07653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21219,"mean_force":0.04989,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49659,0.04648,0.1725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20042.0,"contact_point_centroid":[0.49312,0.0622,0.17409],"force_p95":0.07131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18775,"mean_force":0.04896,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49395,0.04318,0.17184]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02636,-0.00206],"force_p95":0.14268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17817,"mean_force":0.12752,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4468,-0.02555,0.0382]},{"body_a":"world","body_b":"grasp_target","contact_count":2544.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13046,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47774,-0.01204,0.1947]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.447,-0.00644,0.03853],"force_p95":0.06862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12555,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44564,-0.02552,0.03709]},{"body_a":"world","body_b":"grasp_target","contact_count":632.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4544,-0.02508,0.06731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4416.0,"contact_point_centroid":[0.44511,-0.04477,0.03988],"force_p95":0.07926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08534,"mean_force":0.04914,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44564,-0.02552,0.03709]}],"total_contact_groups":12},"final_pose_error":0.02586,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61022,0.19528,0.09675],"final_tcp_position":[0.6135,0.19404,0.12675],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.56531,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2544.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.45699,-0.02449,0.08973],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":632.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45371,-0.02574,0.04488],"tcp_start":[0.45699,-0.02449,0.08973],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02602,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30354,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14228,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11312.0,"raw_peak_contact_force":0.17817,"tcp_end":[0.44561,-0.02552,0.03706],"tcp_start":[0.45371,-0.02574,0.04488],"tcp_to_object_dist_end":0.01713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45145,-0.02605,0.14358],"object_pos_start":[0.45849,-0.02602,0.02577],"object_to_goal_dist_end":0.2961,"object_to_goal_dist_start":0.30354,"object_z_max":0.14347,"peak_contact_force":0.07851,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30872.0,"raw_peak_contact_force":0.56531,"tcp_end":[0.44195,-0.02539,0.16178],"tcp_start":[0.44561,-0.02552,0.03706],"tcp_to_object_dist_end":0.02054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54628,0.10697,0.16311],"object_pos_start":[0.45145,-0.02605,0.14358],"object_to_goal_dist_end":0.1403,"object_to_goal_dist_start":0.2961,"object_z_max":0.16311,"peak_contact_force":0.06734,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39806.0,"raw_peak_contact_force":0.21219,"tcp_end":[0.54451,0.10597,0.18468],"tcp_start":[0.44195,-0.02539,0.16178],"tcp_to_object_dist_end":0.02166,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61022,0.19528,0.09675],"object_pos_start":[0.54628,0.10697,0.16311],"object_to_goal_dist_end":0.02941,"object_to_goal_dist_start":0.1403,"object_z_max":0.16311,"peak_contact_force":0.12431,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":31960.0,"raw_peak_contact_force":0.25251,"subtask_id":"place_at_goal","tcp_end":[0.6135,0.19404,0.12675],"tcp_start":[0.54451,0.10597,0.18468],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01587,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14992,"descend_to_grasp.grasp_offset_z":0.01016,"lift_object.lift_height":0.13123,"place_at_goal.place_offset_x":0.00244,"place_at_goal.place_offset_y":0.00164,"place_at_goal.place_offset_z":0.02215,"transport_to_goal.transport_speed":0.15608},"optimized_scores":{"best_composite_score":0.50401,"best_fitness_score":0.97401,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.54061,0.00095,-0.00112],"force_p95":0.45269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62575,"mean_force":0.09835,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52809,0.00079,0.03542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13488.0,"contact_point_centroid":[0.52682,0.01987,0.0949],"force_p95":0.0807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3519,"mean_force":0.05695,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52541,0.00075,0.0927]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14539.0,"contact_point_centroid":[0.52678,-0.01828,0.09208],"force_p95":0.07779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33051,"mean_force":0.05344,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52544,0.00075,0.0901]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20184.0,"contact_point_centroid":[0.62271,0.10688,0.20841],"force_p95":0.07342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22479,"mean_force":0.04982,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61875,0.12541,0.20857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17278.0,"contact_point_centroid":[0.61665,0.14412,0.21086],"force_p95":0.08786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2212,"mean_force":0.05816,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61856,0.12515,0.20866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15938.0,"contact_point_centroid":[0.55968,0.02541,0.18536],"force_p95":0.08636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16603,"mean_force":0.06099,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55601,0.0441,0.18441]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15687.0,"contact_point_centroid":[0.55718,0.06327,0.18589],"force_p95":0.08762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15681,"mean_force":0.06155,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55614,0.04427,0.18455]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15362,"mean_force":0.12534,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53101,0.00086,0.03524]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51681,0.00047,0.24225]},{"body_a":"world","body_b":"grasp_target","contact_count":1708.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53605,0.00097,0.11436]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4905.0,"contact_point_centroid":[0.53081,-0.01822,0.03557],"force_p95":0.06847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1019,"mean_force":0.04418,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52974,0.00083,0.03376]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53096,0.02005,0.03632],"force_p95":0.07529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09578,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52974,0.00083,0.03376]}],"total_contact_groups":12},"final_pose_error":0.01067,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64353,0.15771,0.17572],"final_tcp_position":[0.64475,0.15679,0.20448],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.62575,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53621,0.00096,0.18574],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1708.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53859,0.00102,0.04418],"tcp_start":[0.53621,0.00096,0.18574],"tcp_to_object_dist_end":0.01904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00111,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25029,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13264,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10854.0,"raw_peak_contact_force":0.15362,"tcp_end":[0.52971,0.00083,0.03372],"tcp_start":[0.53859,0.00102,0.04418],"tcp_to_object_dist_end":0.01647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.53658,0.00083,0.13707],"object_pos_start":[0.54418,0.00111,0.02587],"object_to_goal_dist_end":0.19995,"object_to_goal_dist_start":0.25029,"object_z_max":0.13696,"peak_contact_force":0.08009,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28171.0,"raw_peak_contact_force":0.62575,"tcp_end":[0.52572,0.00076,0.15235],"tcp_start":[0.52971,0.00083,0.03372],"tcp_to_object_dist_end":0.01874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59492,0.08722,0.19866],"object_pos_start":[0.53658,0.00083,0.13707],"object_to_goal_dist_end":0.08864,"object_to_goal_dist_start":0.19995,"object_z_max":0.19862,"peak_contact_force":0.13192,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31625.0,"raw_peak_contact_force":0.16603,"tcp_end":[0.58868,0.08593,0.22039],"tcp_start":[0.52572,0.00076,0.15235],"tcp_to_object_dist_end":0.02265,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":998.0,"n_steps_budget":1000.0,"object_pos_end":[0.64353,0.15771,0.17572],"object_pos_start":[0.59492,0.08722,0.19866],"object_to_goal_dist_end":0.01592,"object_to_goal_dist_start":0.08864,"object_z_max":0.19866,"peak_contact_force":0.09651,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":37462.0,"raw_peak_contact_force":0.22479,"subtask_id":"place_at_goal","tcp_end":[0.64475,0.15679,0.20448],"tcp_start":[0.58868,0.08593,0.22039],"tcp_to_object_dist_end":0.0288,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95238,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.07787,"descend_to_grasp.grasp_offset_z":0.01021,"lift_object.lift_height":0.1167,"place_at_goal.place_offset_x":0.00868,"place_at_goal.place_offset_y":0.00227,"place_at_goal.place_offset_z":0.02722,"transport_to_goal.transport_speed":0.14716},"optimized_scores":{"best_composite_score":0.50313,"best_fitness_score":0.97313,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52687,0.02884,-0.00121],"force_p95":0.41084,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62223,"mean_force":0.09514,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51413,0.02938,0.03584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11431.0,"contact_point_centroid":[0.51265,0.04844,0.08805],"force_p95":0.11039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41598,"mean_force":0.06127,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51149,0.02921,0.08576]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13572.0,"contact_point_centroid":[0.51344,0.01061,0.08559],"force_p95":0.08636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32278,"mean_force":0.05089,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51152,0.02921,0.08403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7420.0,"contact_point_centroid":[0.58395,0.17414,0.1511],"force_p95":0.1025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28014,"mean_force":0.06367,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58672,0.15524,0.14894]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03078,-0.00211],"force_p95":0.15431,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21293,"mean_force":0.13108,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51704,0.02958,0.03546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9730.0,"contact_point_centroid":[0.59046,0.1363,0.14966],"force_p95":0.0869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21207,"mean_force":0.04883,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58633,0.15475,0.14938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12632.0,"contact_point_centroid":[0.54015,0.09985,0.15795],"force_p95":0.11476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18878,"mean_force":0.07932,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53915,0.08059,0.15642]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18609.0,"contact_point_centroid":[0.54322,0.06254,0.15698],"force_p95":0.0897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18324,"mean_force":0.05349,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53918,0.08063,0.15645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5273.0,"contact_point_centroid":[0.51703,0.01056,0.03613],"force_p95":0.06762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16686,"mean_force":0.04092,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51579,0.02949,0.03404]},{"body_a":"world","body_b":"grasp_target","contact_count":2400.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13069,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51087,0.014,0.20698]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52307,0.02916,0.07928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4181.0,"contact_point_centroid":[0.51662,0.04884,0.03685],"force_p95":0.09173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09624,"mean_force":0.0549,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51579,0.0295,0.03405]}],"total_contact_groups":12},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60059,0.17674,0.10344],"final_tcp_position":[0.60315,0.17628,0.12995],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.62223,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2400.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52416,0.02843,0.11507],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":896.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5245,0.03006,0.04402],"tcp_start":[0.52416,0.02843,0.11507],"tcp_to_object_dist_end":0.01899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53058,0.03018,0.0256],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18401,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15214,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11254.0,"raw_peak_contact_force":0.21293,"tcp_end":[0.51576,0.02949,0.03401],"tcp_start":[0.5245,0.03006,0.04402],"tcp_to_object_dist_end":0.01705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.5235,0.02982,0.12259],"object_pos_start":[0.53058,0.03018,0.0256],"object_to_goal_dist_end":0.1686,"object_to_goal_dist_start":0.18401,"object_z_max":0.12248,"peak_contact_force":0.11528,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25149.0,"raw_peak_contact_force":0.62223,"tcp_end":[0.51169,0.02923,0.13837],"tcp_start":[0.51576,0.02949,0.03401],"tcp_to_object_dist_end":0.01972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57478,0.13127,0.15539],"object_pos_start":[0.5235,0.02982,0.12259],"object_to_goal_dist_end":0.07205,"object_to_goal_dist_start":0.1686,"object_z_max":0.15535,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31241.0,"raw_peak_contact_force":0.18878,"tcp_end":[0.56851,0.12915,0.17818],"tcp_start":[0.51169,0.02923,0.13837],"tcp_to_object_dist_end":0.02373,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.60059,0.17674,0.10344],"object_pos_start":[0.57478,0.13127,0.15539],"object_to_goal_dist_end":0.00509,"object_to_goal_dist_start":0.07205,"object_z_max":0.15539,"peak_contact_force":0.09463,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17150.0,"raw_peak_contact_force":0.28014,"subtask_id":"place_at_goal","tcp_end":[0.60315,0.17628,0.12995],"tcp_start":[0.56851,0.12915,0.17818],"tcp_to_object_dist_end":0.02664,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```