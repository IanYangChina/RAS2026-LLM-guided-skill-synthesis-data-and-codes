## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11  | -0.4832 | 0.21 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13  | 0.2037 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 13  | 0.2431 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12  | 0.4709 | 0.88 | ❌ rejected |
| 6 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 7  | -0.0135 | 0.43 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.013) — your mutation base

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

- **Composite score**: -0.013
- **task_score** (E): 0.429
- **fitness_score**: 0.687  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1606 |
| descend_to_grasp | 1.00 | 1.00 | 0.1002 |
| grasp_object | 1.00 | 1.00 | 0.0122 |
| lift_object | 1.00 | 1.00 | 0.1092 |
| transport_to_goal | 1.00 | 1.00 | 0.2123 |
| place_at_goal | 1.00 | 0.67 | 0.0669 |
| release_object | 1.00 | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.001, 0.146) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.001, 0.146)→(0.506, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.002, 0.045)→(0.498, 0.002, 0.036) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.667 | 0.139 | 0.188 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.036)→(0.494, 0.002, 0.146) | (0.511, 0.002, 0.026)→(0.508, 0.002, 0.126) | 0.246→0.221 | 1.00 / 23.000 | 0.107 | 0.553 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.002, 0.146)→(0.608, 0.160, 0.218) | (0.508, 0.002, 0.126)→(0.591, 0.139, 0.061) | 0.221→0.125 | 1.00 / 9.000 | 3249.613 | 1.113 |
| place_at_goal | descend | 1.00 / step_budget | (0.608, 0.160, 0.218)→(0.622, 0.173, 0.155) | (0.591, 0.139, 0.061)→(0.592, 0.145, 0.037) | 0.125→0.115 | 0.67 / 5.333 | 0.082 | 0.165 |
| release_object | release | 1.00 / step_budget | (0.622, 0.173, 0.155)→(0.616, 0.171, 0.174) | (0.592, 0.145, 0.037)→(0.593, 0.147, 0.016) | 0.115→0.136 | 1.00 / 4.000 | 0.123 | 0.493 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.540
- phase_score: 0.098
- phase_breakdown.place_at_goal_score: 0.000
- phase_breakdown.pre_grasp_score: 0.328
- grasp_place_fitness: 0.740

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.740
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.025
- **K-run variance**: 0.0042
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.268


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.38462,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09844,"approach_object.approach_speed":0.3613,"descend_to_grasp.descend_speed":0.17319,"descend_to_grasp.grasp_offset_z":0.01391,"lift_object.lift_height":0.11548,"place_at_goal.descend_speed":0.1836,"place_at_goal.place_offset_x":0.00177,"place_at_goal.place_offset_y":-0.00147,"place_at_goal.place_offset_z":0.0046,"release_object.release_duration":1.08392,"transport_to_goal.transport_speed":0.38059},"optimized_scores":{"best_composite_score":0.02455,"best_fitness_score":0.72455,"best_task_score":0.51048},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.61734,0.18708,-0.00832],"force_p95":1.35599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56064,"mean_force":0.46647,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60054,0.17442,0.19623]},{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.45577,-0.02505,-0.00112],"force_p95":0.35198,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46126,"mean_force":0.06113,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44559,-0.02552,0.04346]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10595.0,"contact_point_centroid":[0.51198,0.03826,0.16502],"force_p95":0.13228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33547,"mean_force":0.07903,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50603,0.0568,0.16484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9895.0,"contact_point_centroid":[0.51168,0.07561,0.16492],"force_p95":0.1268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32056,"mean_force":0.0843,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50621,0.05701,0.1649]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10345.0,"contact_point_centroid":[0.44522,-0.00642,0.08991],"force_p95":0.10399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28434,"mean_force":0.06498,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44319,-0.02541,0.08775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11277.0,"contact_point_centroid":[0.44526,-0.0443,0.0886],"force_p95":0.09856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27265,"mean_force":0.06067,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44318,-0.02541,0.08707]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02623,-0.00206],"force_p95":0.14128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19095,"mean_force":0.1276,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44801,-0.02561,0.0427]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47869,-0.01173,0.21898]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.61845,0.18791,-0.00205],"force_p95":0.12621,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12909,"mean_force":0.11741,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61225,0.18904,0.15657]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45523,-0.02485,0.09314]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61845,0.1879,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61868,0.19974,0.11974]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4832.0,"contact_point_centroid":[0.44692,-0.00632,0.04394],"force_p95":0.06849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10404,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44694,-0.02557,0.04168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.4464,-0.0448,0.04335],"force_p95":0.06547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07816,"mean_force":0.04107,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44694,-0.02557,0.04168]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1103.0,"contact_point_centroid":[0.61349,0.18991,0.15572],"force_p95":0.01237,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01595,"mean_force":0.01072,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61296,0.1899,0.15348]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.62254,0.20092,0.11886],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.0101,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62181,0.2009,0.11642]}],"total_contact_groups":15},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61845,0.1879,0.01602],"final_tcp_position":[0.62371,0.20138,0.12012],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.56064,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.45834,-0.02398,0.1379],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45441,-0.02584,0.04893],"tcp_start":[0.45834,-0.02398,0.1379],"tcp_to_object_dist_end":0.02329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02573,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30331,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13865,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12039.0,"raw_peak_contact_force":0.19095,"tcp_end":[0.44692,-0.02557,0.04165],"tcp_start":[0.45441,-0.02584,0.04893],"tcp_to_object_dist_end":0.01965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.45586,-0.02532,0.12296],"object_pos_start":[0.45848,-0.02573,0.02577],"object_to_goal_dist_end":0.29152,"object_to_goal_dist_start":0.30331,"object_z_max":0.12285,"peak_contact_force":0.09872,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21748.0,"raw_peak_contact_force":0.46126,"tcp_end":[0.44321,-0.0254,0.14623],"tcp_start":[0.44692,-0.02557,0.04165],"tcp_to_object_dist_end":0.02649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61814,0.18519,0.00969],"object_pos_start":[0.45586,-0.02532,0.12296],"object_to_goal_dist_end":0.1076,"object_to_goal_dist_start":0.29152,"object_z_max":0.15462,"peak_contact_force":0.10387,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20644.0,"raw_peak_contact_force":1.56064,"tcp_end":[0.60304,0.17752,0.19704],"tcp_start":[0.44321,-0.0254,0.14623],"tcp_to_object_dist_end":0.18811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.61845,0.1879,0.01602],"object_pos_start":[0.61814,0.18519,0.00969],"object_to_goal_dist_end":0.10086,"object_to_goal_dist_start":0.1076,"object_z_max":0.01672,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2223.0,"raw_peak_contact_force":0.12909,"tcp_end":[0.62371,0.20138,0.12012],"tcp_start":[0.60304,0.17752,0.19704],"tcp_to_object_dist_end":0.1051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61845,0.1879,0.01602],"object_pos_start":[0.61845,0.1879,0.01602],"object_to_goal_dist_end":0.10086,"object_to_goal_dist_start":0.10086,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.6168,0.19903,0.13903],"tcp_start":[0.62371,0.20138,0.12012],"tcp_to_object_dist_end":0.12353,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.20755,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.07696,"approach_object.approach_speed":0.20415,"descend_to_grasp.descend_speed":0.154,"descend_to_grasp.grasp_offset_z":0.00457,"lift_object.lift_height":0.12096,"place_at_goal.descend_speed":0.14569,"place_at_goal.place_offset_x":0.00897,"place_at_goal.place_offset_y":-0.00681,"place_at_goal.place_offset_z":0.00838,"release_object.release_duration":1.35827,"transport_to_goal.transport_speed":0.43624},"optimized_scores":{"best_composite_score":-0.10524,"best_fitness_score":0.59476,"best_task_score":0.23653},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2784.0,"contact_point_centroid":[0.55879,0.06727,-0.00232],"force_p95":0.13193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55942,"mean_force":0.14065,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59184,0.08986,0.21705]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54134,0.0006,-0.00111],"force_p95":0.46459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69928,"mean_force":0.09216,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52791,0.00083,0.03004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9668.0,"contact_point_centroid":[0.5286,-0.01801,0.07747],"force_p95":0.10938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33555,"mean_force":0.0727,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52522,0.00079,0.07572]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10007.0,"contact_point_centroid":[0.52881,0.01954,0.07662],"force_p95":0.10721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31718,"mean_force":0.07067,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52527,0.00079,0.07495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1720.0,"contact_point_centroid":[0.53768,-0.00426,0.1425],"force_p95":0.18939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2937,"mean_force":0.11856,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53292,0.01394,0.14541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2187.0,"contact_point_centroid":[0.53837,0.03385,0.14358],"force_p95":0.1633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28774,"mean_force":0.10089,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53428,0.01592,0.14703]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15853,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53083,0.00088,0.0298]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51744,0.00049,0.2058]},{"body_a":"world","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53637,0.00099,0.07574]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.55882,0.06741,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63751,0.14204,0.2321]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55882,0.06741,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.64403,0.14661,0.20166]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.5307,-0.01834,0.03106],"force_p95":0.07613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11493,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52959,0.00086,0.02837]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53063,0.01994,0.03018],"force_p95":0.06817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09136,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52959,0.00086,0.02838]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2707.0,"contact_point_centroid":[0.59544,0.09386,0.22308],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59501,0.09386,0.22091]},{"body_a":"left_finger","body_b":"right_finger","contact_count":846.0,"contact_point_centroid":[0.63795,0.14206,0.23441],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01044,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63752,0.14204,0.23208]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.64707,0.14734,0.20092],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.64646,0.14732,0.19858]}],"total_contact_groups":16},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55882,0.06741,0.01602],"final_tcp_position":[0.64798,0.14763,0.20257],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.59826,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53707,0.00099,0.11369],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":940.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53823,0.00102,0.03844],"tcp_start":[0.53707,0.00099,0.11369],"tcp_to_object_dist_end":0.01383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13008,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15853,"tcp_end":[0.52956,0.00086,0.02834],"tcp_start":[0.53823,0.00102,0.03844],"tcp_to_object_dist_end":0.01481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.54157,0.00092,0.12267],"object_pos_start":[0.54417,0.00073,0.02588],"object_to_goal_dist_end":0.20157,"object_to_goal_dist_start":0.25052,"object_z_max":0.12257,"peak_contact_force":0.11171,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19820.0,"raw_peak_contact_force":0.69928,"tcp_end":[0.52542,0.0008,0.13681],"tcp_start":[0.52956,0.00086,0.02834],"tcp_to_object_dist_end":0.02146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55882,0.06741,0.01602],"object_pos_start":[0.54157,0.00092,0.12267],"object_to_goal_dist_end":0.21625,"object_to_goal_dist_start":0.20157,"object_z_max":0.13539,"peak_contact_force":9748.59826,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9398.0,"raw_peak_contact_force":1.55942,"tcp_end":[0.62927,0.13717,0.26249],"tcp_start":[0.52542,0.0008,0.13681],"tcp_to_object_dist_end":0.26567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.55882,0.06741,0.01602],"object_pos_start":[0.55882,0.06741,0.01602],"object_to_goal_dist_end":0.21625,"object_to_goal_dist_start":0.21625,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1638.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64798,0.14763,0.20257],"tcp_start":[0.62927,0.13717,0.26249],"tcp_to_object_dist_end":0.22179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55882,0.06741,0.01602],"object_pos_start":[0.55882,0.06741,0.01602],"object_to_goal_dist_end":0.21625,"object_to_goal_dist_start":0.21625,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.64263,0.14618,0.22076],"tcp_start":[0.64798,0.14763,0.20257],"tcp_to_object_dist_end":0.23483,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10377,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14877,"approach_object.approach_speed":0.47556,"descend_to_grasp.descend_speed":0.16788,"descend_to_grasp.grasp_offset_z":0.01451,"lift_object.lift_height":0.12672,"place_at_goal.descend_speed":0.11672,"place_at_goal.place_offset_x":-0.00027,"place_at_goal.place_offset_y":-0.00647,"place_at_goal.place_offset_z":0.02681,"release_object.release_duration":1.22275,"transport_to_goal.transport_speed":0.36484},"optimized_scores":{"best_composite_score":0.04021,"best_fitness_score":0.74021,"best_task_score":0.54048},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":687.0,"contact_point_centroid":[0.60088,0.18526,-0.00319],"force_p95":0.59955,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23364,"mean_force":0.17462,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58935,0.16745,0.1427]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52778,0.02901,-0.00119],"force_p95":0.35275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49971,"mean_force":0.07591,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5152,0.02948,0.04098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10545.0,"contact_point_centroid":[0.51555,0.01047,0.09164],"force_p95":0.10534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31788,"mean_force":0.0691,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51263,0.02932,0.0897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11030.0,"contact_point_centroid":[0.51561,0.04816,0.08939],"force_p95":0.10354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30871,"mean_force":0.0669,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51266,0.02932,0.08769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1035.0,"contact_point_centroid":[0.59683,0.14802,0.16928],"force_p95":0.16758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24382,"mean_force":0.1173,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.591,0.16594,0.17439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.5968,0.18398,0.16602],"force_p95":0.15288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22047,"mean_force":0.11244,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.59131,0.16623,0.17117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11036.0,"contact_point_centroid":[0.55429,0.11232,0.17089],"force_p95":0.13392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21938,"mean_force":0.08369,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54817,0.09401,0.17111]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.0306,-0.0021],"force_p95":0.15251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21579,"mean_force":0.13062,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51804,0.02968,0.04057]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9771.0,"contact_point_centroid":[0.5547,0.07657,0.17164],"force_p95":0.13643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20857,"mean_force":0.09365,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54883,0.09509,0.1715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4088.0,"contact_point_centroid":[0.51758,0.01039,0.04197],"force_p95":0.07966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1429,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51684,0.0296,0.0392]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.1347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51074,0.01338,0.2423]},{"body_a":"world","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52325,0.02871,0.11643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.51755,0.04873,0.041],"force_p95":0.07235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07819,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51685,0.0296,0.0392]}],"total_contact_groups":13},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.601,0.18495,0.01602],"final_tcp_position":[0.59468,0.16906,0.1417],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.23364,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52382,0.02744,0.18521],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1536.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52517,0.03015,0.04882],"tcp_start":[0.52382,0.02744,0.18521],"tcp_to_object_dist_end":0.02343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02974,0.02564],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18441,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14698,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10856.0,"raw_peak_contact_force":0.21579,"tcp_end":[0.51682,0.0296,0.03916],"tcp_start":[0.52517,0.03015,0.04882],"tcp_to_object_dist_end":0.01919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.52548,0.02954,0.13165],"object_pos_start":[0.53043,0.02974,0.02564],"object_to_goal_dist_end":0.16898,"object_to_goal_dist_start":0.18441,"object_z_max":0.13154,"peak_contact_force":0.11133,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21721.0,"raw_peak_contact_force":0.49971,"tcp_end":[0.51288,0.02934,0.15356],"tcp_start":[0.51682,0.0296,0.03916],"tcp_to_object_dist_end":0.02528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59571,0.16527,0.15843],"object_pos_start":[0.52548,0.02954,0.13165],"object_to_goal_dist_end":0.05239,"object_to_goal_dist_start":0.16898,"object_z_max":0.15841,"peak_contact_force":0.13574,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20807.0,"raw_peak_contact_force":0.21938,"tcp_end":[0.5902,0.16442,0.19534],"tcp_start":[0.51288,0.02934,0.15356],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.59868,0.17861,0.07972],"object_pos_start":[0.59571,0.16527,0.15843],"object_to_goal_dist_end":0.02852,"object_to_goal_dist_start":0.05239,"object_z_max":0.15843,"peak_contact_force":0.0,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2103.0,"raw_peak_contact_force":0.24382,"tcp_end":[0.59468,0.16906,0.1417],"tcp_start":[0.5902,0.16442,0.19534],"tcp_to_object_dist_end":0.06284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.601,0.18495,0.01602],"object_pos_start":[0.59868,0.17861,0.07972],"object_to_goal_dist_end":0.0923,"object_to_goal_dist_start":0.02852,"object_z_max":0.07972,"peak_contact_force":0.12261,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":687.0,"raw_peak_contact_force":1.23364,"subtask_id":"place_at_goal","tcp_end":[0.5882,0.16707,0.16201],"tcp_start":[0.59468,0.16906,0.1417],"tcp_to_object_dist_end":0.14764,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```