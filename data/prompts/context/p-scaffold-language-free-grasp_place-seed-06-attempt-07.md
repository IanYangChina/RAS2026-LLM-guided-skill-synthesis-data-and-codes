## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0508 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0020 | 0.39 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0199 | 0.29 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3980 | 0.29 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0208 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=0.051) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_to_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: place_at_goal
  weight: 0.3
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
    - 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_object
- id: descend_1
  type: descend
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
    - 0.02
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_object
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: lift_object
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
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_1
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
    - 0.05
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_to_goal
- id: descend_to_place_1
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    descend_place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
    - descend_place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.051
- **task_score** (E): 0.190
- **fitness_score**: 0.571  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1275 |
| descend_1 | 1.00 | 1.00 | 0.1370 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 0.00 | 1.00 | 0.0996 |
| transport_1 | 0.00 | 1.00 | 0.2075 |
| release_1 | 1.00 | 0.67 | 0.0265 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.178) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.178)→(0.495, 0.024, 0.041) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.041)→(0.486, 0.023, 0.032) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.333 | 0.151 | 0.204 |
| lift_1 | lift | 0.00 / step_budget | (0.486, 0.023, 0.032)→(0.488, 0.023, 0.132) | (0.500, 0.024, 0.026)→(0.497, 0.024, 0.118) | 0.272→0.224 | 1.00 / 37.000 | 0.080 | 0.545 |
| transport_1 | approach | 0.00 / step_budget | (0.488, 0.023, 0.132)→(0.607, 0.046, 0.291) | (0.497, 0.024, 0.118)→(0.525, 0.101, -5.449) | 0.224→5.675 | 1.00 / 8.000 | 91094.586 | 1502.274 |
| release_1 | release | 1.00 / step_budget | (0.607, 0.046, 0.291)→(0.607, 0.046, 0.318) | (0.525, 0.101, -5.449)→(0.512, 0.103, -8.098) | 5.675→8.324 | 0.67 / 2.667 | 0.082 | 123.862 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.419
- phase_score: 0.158
- phase_breakdown.approach_object_score: 0.167
- phase_breakdown.lift_object_score: 0.376
- phase_breakdown.place_at_goal_score: 0.023
- grasp_place_fitness: 0.686

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.686
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.419
- **Median Q (composite search score)**: 0.030
- **K-run variance**: 0.0075
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: approach_1.approach_speed
- **Final σ (mean)**: 0.367


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78912,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1,"approach_1.approach_z_offset":0.13834,"descend_1.descend_speed":0.0488,"descend_1.descend_z_offset":0.00946,"lift_1.lift_height":0.24064,"lift_1.lift_speed":0.06104,"transport_1.transport_speed":0.19291,"transport_1.transport_tolerance":0.02981},"optimized_scores":{"best_composite_score":0.03002,"best_fitness_score":0.55002,"best_task_score":0.15122},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":150.0,"contact_point_centroid":[0.668,0.01017,-0.00148],"force_p95":708.89721,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1753.00722,"mean_force":326.15152,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57881,0.0165,0.04783]},{"body_a":"world","body_b":"link6","contact_count":725.0,"contact_point_centroid":[0.59345,-0.09418,-0.00035],"force_p95":328.08061,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1057.97033,"mean_force":284.91366,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57017,-0.04731,0.28442]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.59745,-0.07495,-0.00015],"force_p95":81.03693,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.95004,"mean_force":60.28235,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58387,-0.04884,0.29272]},{"body_a":"world","body_b":"right_finger","contact_count":193.0,"contact_point_centroid":[0.57922,-0.02538,-0.00413],"force_p95":6.67862,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.1333,"mean_force":2.34493,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56498,-0.03547,0.00637]},{"body_a":"world","body_b":"grasp_target","contact_count":3346.0,"contact_point_centroid":[0.60091,0.01869,-0.00283],"force_p95":0.46929,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.29332,"mean_force":0.18272,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57191,-0.04109,0.25942]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1646.0,"contact_point_centroid":[0.55821,-0.01845,0.07664],"force_p95":0.41322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.36358,"mean_force":0.17084,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54733,-0.02799,0.08063]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1643.0,"contact_point_centroid":[0.5432,-0.05101,0.08353],"force_p95":0.56606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.79452,"mean_force":0.2252,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54837,-0.03374,0.077]},{"body_a":"grasp_target","body_b":"hand","contact_count":53.0,"contact_point_centroid":[0.59105,-0.03173,0.06746],"force_p95":0.53484,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57133,"mean_force":0.29939,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57274,0.00629,0.04604]},{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.49939,-0.01534,-0.0011],"force_p95":0.3292,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49956,"mean_force":0.09212,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48856,-0.01539,0.03621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20848.0,"contact_point_centroid":[0.48993,0.0036,0.08476],"force_p95":0.07273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.269,"mean_force":0.04888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48883,-0.01545,0.08292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18423.0,"contact_point_centroid":[0.4891,-0.03462,0.08533],"force_p95":0.07845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26396,"mean_force":0.05414,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4888,-0.01545,0.0826]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16009,"mean_force":0.12522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49131,-0.01541,0.03594]},{"body_a":"world","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49892,-0.00671,0.23913]},{"body_a":"world","body_b":"grasp_target","contact_count":1812.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49776,-0.01466,0.11002]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6042,0.02583,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58386,-0.04899,0.2993]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5329.0,"contact_point_centroid":[0.49084,0.00366,0.03658],"force_p95":0.06674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09513,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49008,-0.0154,0.03465]}],"total_contact_groups":19},"final_pose_error":0.24046,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.6042,0.02583,0.01602],"final_tcp_position":[0.58394,-0.04888,0.29239],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":272998.75278,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49982,-0.01391,0.17731],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1812.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49859,-0.01546,0.04377],"tcp_start":[0.49982,-0.01391,0.17731],"tcp_to_object_dist_end":0.01851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01579,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31244,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1326,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.16009,"subtask_id":"lift_object","tcp_end":[0.49005,-0.0154,0.03461],"tcp_start":[0.49859,-0.01546,0.04377],"tcp_to_object_dist_end":0.0162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5004,-0.0159,0.11829],"object_pos_start":[0.50369,-0.01579,0.02588],"object_to_goal_dist_end":0.2563,"object_to_goal_dist_start":0.31244,"object_z_max":0.11817,"peak_contact_force":0.08033,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39440.0,"raw_peak_contact_force":0.49956,"subtask_id":"lift_object","tcp_end":[0.49202,-0.01553,0.1341],"tcp_start":[0.49005,-0.0154,0.03461],"tcp_to_object_dist_end":0.0179,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6042,0.02583,0.01602],"object_pos_start":[0.5004,-0.0159,0.11829],"object_to_goal_dist_end":0.28335,"object_to_goal_dist_start":0.2563,"object_z_max":0.11841,"peak_contact_force":272998.75278,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10896.0,"raw_peak_contact_force":1753.00722,"subtask_id":"place_at_goal","tcp_end":[0.58394,-0.04888,0.29239],"tcp_start":[0.49202,-0.01553,0.1341],"tcp_to_object_dist_end":0.287,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6042,0.02583,0.01602],"object_pos_start":[0.6042,0.02583,0.01602],"object_to_goal_dist_end":0.28335,"object_to_goal_dist_start":0.28335,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1107.0,"raw_peak_contact_force":85.95004,"tcp_end":[0.58397,-0.04916,0.3197],"tcp_start":[0.58394,-0.04888,0.29239],"tcp_to_object_dist_end":0.31345,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48408,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06212,"approach_1.approach_z_offset":0.14763,"descend_1.descend_speed":0.0556,"descend_1.descend_z_offset":0.00623,"lift_1.lift_height":0.21785,"lift_1.lift_speed":0.06216,"transport_1.transport_speed":0.23447,"transport_1.transport_tolerance":0.02442},"optimized_scores":{"best_composite_score":0.16564,"best_fitness_score":0.68564,"best_task_score":0.41908},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":22.0,"contact_point_centroid":[0.5953,0.15559,-0.00506],"force_p95":1464.84997,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1523.88927,"mean_force":450.13957,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49493,0.14909,0.01458]},{"body_a":"world","body_b":"link6","contact_count":751.0,"contact_point_centroid":[0.66998,-0.00853,-0.00024],"force_p95":589.78901,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1198.42166,"mean_force":354.96757,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.62402,0.03361,0.28043]},{"body_a":"world","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.56494,0.0452,-0.00051],"force_p95":584.10417,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":624.5304,"mean_force":289.07851,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50246,0.15785,0.03397]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.71299,0.04433,-0.00012],"force_p95":82.75585,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.60708,"mean_force":56.39176,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.66901,0.06098,0.29046]},{"body_a":"world","body_b":"right_finger","contact_count":156.0,"contact_point_centroid":[0.50943,0.15017,-0.00302],"force_p95":24.03289,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.6517,"mean_force":9.63449,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49234,0.14181,0.0045]},{"body_a":"world","body_b":"left_finger","contact_count":48.0,"contact_point_centroid":[0.47428,0.12662,-0.00133],"force_p95":22.01531,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.01688,"mean_force":18.41953,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49232,0.13977,0.00276]},{"body_a":"world","body_b":"grasp_target","contact_count":2966.0,"contact_point_centroid":[0.60623,0.1802,-0.00282],"force_p95":0.46829,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.75936,"mean_force":0.20864,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.62237,0.03301,0.27545]},{"body_a":"grasp_target","body_b":"hand","contact_count":27.0,"contact_point_centroid":[0.52601,0.11944,0.01775],"force_p95":3.27885,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.531,"mean_force":1.74956,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49688,0.14869,0.018]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1369.0,"contact_point_centroid":[0.50992,0.05591,0.08711],"force_p95":1.4356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.76244,"mean_force":0.35463,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5143,0.07482,0.08662]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":558.0,"contact_point_centroid":[0.51538,0.0762,0.10925],"force_p95":0.81331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.94244,"mean_force":0.20335,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5111,0.06032,0.10754]},{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.50793,0.03722,-0.00119],"force_p95":0.35713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58591,"mean_force":0.09565,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4969,0.03808,0.03303]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49798,0.05722,0.08404],"force_p95":0.08321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30672,"mean_force":0.0584,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49777,0.03803,0.08127]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20767.0,"contact_point_centroid":[0.49951,0.01909,0.08197],"force_p95":0.07768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27807,"mean_force":0.04915,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49771,0.03802,0.08037]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03967,-0.00213],"force_p95":0.16086,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22113,"mean_force":0.13262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4998,0.03833,0.03255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5024.0,"contact_point_centroid":[0.50023,0.01923,0.03271],"force_p95":0.07324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17664,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49856,0.03823,0.0312]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50265,0.01705,0.24252]}],"total_contact_groups":21},"final_pose_error":0.18773,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61194,0.18401,0.01602],"final_tcp_position":[0.66926,0.0612,0.29033],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1523.88927,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50759,0.03524,0.18494],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50716,0.03892,0.04063],"tcp_start":[0.50759,0.03524,0.18494],"tcp_to_object_dist_end":0.01558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.03882,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21306,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15824,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11050.0,"raw_peak_contact_force":0.22113,"subtask_id":"lift_object","tcp_end":[0.49853,0.03822,0.03117],"tcp_start":[0.50716,0.03892,0.04063],"tcp_to_object_dist_end":0.01507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5106,0.03899,0.11898],"object_pos_start":[0.51249,0.03882,0.02554],"object_to_goal_dist_end":0.17942,"object_to_goal_dist_start":0.21306,"object_z_max":0.11886,"peak_contact_force":0.08033,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37961.0,"raw_peak_contact_force":0.58591,"subtask_id":"lift_object","tcp_end":[0.50135,0.03819,0.13247],"tcp_start":[0.49853,0.03822,0.03117],"tcp_to_object_dist_end":0.01638,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.61194,0.18401,0.01602],"object_pos_start":[0.5106,0.03899,0.11898],"object_to_goal_dist_end":0.13046,"object_to_goal_dist_start":0.17942,"object_z_max":0.11906,"peak_contact_force":285.00406,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9045.0,"raw_peak_contact_force":1523.88927,"subtask_id":"place_at_goal","tcp_end":[0.66926,0.0612,0.29033],"tcp_start":[0.50135,0.03819,0.13247],"tcp_to_object_dist_end":0.30596,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61194,0.18401,0.01602],"object_pos_start":[0.61194,0.18401,0.01602],"object_to_goal_dist_end":0.13046,"object_to_goal_dist_start":0.13046,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1117.0,"raw_peak_contact_force":199.60708,"tcp_end":[0.66932,0.06144,0.31522],"tcp_start":[0.66926,0.0612,0.29033],"tcp_to_object_dist_end":0.32839,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43367,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03977,"approach_1.approach_z_offset":0.13455,"descend_1.descend_speed":0.04582,"descend_1.descend_z_offset":0.00524,"lift_1.lift_height":0.2597,"lift_1.lift_speed":0.05974,"transport_1.transport_speed":0.16834,"transport_1.transport_tolerance":0.02139},"optimized_scores":{"best_composite_score":-0.04314,"best_fitness_score":0.47686,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":130.0,"contact_point_centroid":[0.56327,0.16207,-0.00215],"force_p95":811.75885,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1229.92455,"mean_force":218.43123,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49029,0.11774,0.03003]},{"body_a":"world","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.62177,0.07658,-0.00033],"force_p95":425.84601,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.73601,"mean_force":238.05791,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49713,0.09046,0.00942]},{"body_a":"world","body_b":"link6","contact_count":726.0,"contact_point_centroid":[0.62891,0.08986,-0.00022],"force_p95":322.80732,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":407.00553,"mean_force":269.82813,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5243,0.13011,0.21735]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.59947,0.10453,-0.00014],"force_p95":76.99858,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.029,"mean_force":57.91983,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56681,0.12637,0.29158]},{"body_a":"world","body_b":"left_finger","contact_count":1087.0,"contact_point_centroid":[0.51789,0.05226,-0.00874],"force_p95":10.83554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.52796,"mean_force":5.91121,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51757,0.07483,-0.00811]},{"body_a":"world","body_b":"right_finger","contact_count":1134.0,"contact_point_centroid":[0.52187,0.09692,-0.00861],"force_p95":11.57029,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.1998,"mean_force":5.79599,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51678,0.07525,-0.00742]},{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.53382,0.07211,-0.02757],"force_p95":3.71859,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.8222,"mean_force":0.90679,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52247,0.07325,-0.00774]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.51859,0.03587,0.0918],"force_p95":0.81705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.81775,"mean_force":0.19198,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51685,0.055,0.09187]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1403.0,"contact_point_centroid":[0.52221,0.07704,0.0759],"force_p95":0.77564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.65946,"mean_force":0.2183,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51868,0.05786,0.07473]},{"body_a":"grasp_target","body_b":"hand","contact_count":6.0,"contact_point_centroid":[0.56679,0.0614,-0.00907],"force_p95":0.89669,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.90617,"mean_force":0.70443,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52562,0.07293,-0.02012]},{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.47813,0.0457,-0.00124],"force_p95":0.36203,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54942,"mean_force":0.09975,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46779,0.04679,0.03311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.46771,0.06588,0.0826],"force_p95":0.08424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28757,"mean_force":0.05828,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4679,0.04669,0.07992]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21006.0,"contact_point_centroid":[0.46985,0.02777,0.08084],"force_p95":0.07758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25848,"mean_force":0.04849,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46787,0.04668,0.07935]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04864,-0.00216],"force_p95":0.16643,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23172,"mean_force":0.13426,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47061,0.04708,0.03253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.47132,0.02797,0.03258],"force_p95":0.07737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19426,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46941,0.04696,0.03131]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48963,0.02104,0.23667]}],"total_contact_groups":20},"final_pose_error":0.12011,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.31975,0.09841,-24.32597],"final_tcp_position":[0.56688,0.12638,0.29131],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1229.92455,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1804.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48079,0.04358,0.17271],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1840.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47776,0.04777,0.03985],"tcp_start":[0.48079,0.04358,0.17271],"tcp_to_object_dist_end":0.01472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48272,0.04764,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29104,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16298,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11064.0,"raw_peak_contact_force":0.23172,"subtask_id":"lift_object","tcp_end":[0.46938,0.04696,0.03128],"tcp_start":[0.47776,0.04777,0.03985],"tcp_to_object_dist_end":0.01457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47957,0.04774,0.11583],"object_pos_start":[0.48272,0.04764,0.02546],"object_to_goal_dist_end":0.23752,"object_to_goal_dist_start":0.29104,"object_z_max":0.11572,"peak_contact_force":0.0802,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38191.0,"raw_peak_contact_force":0.54942,"subtask_id":"lift_object","tcp_end":[0.47064,0.04683,0.1291],"tcp_start":[0.46938,0.04696,0.03128],"tcp_to_object_dist_end":0.01603,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.35752,0.09375,-16.37876],"object_pos_start":[0.47957,0.04774,0.11583],"object_to_goal_dist_end":16.61131,"object_to_goal_dist_start":0.23752,"object_z_max":0.11592,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9158.0,"raw_peak_contact_force":1229.92455,"subtask_id":"place_at_goal","tcp_end":[0.56688,0.12638,0.29131],"tcp_start":[0.47064,0.04683,0.1291],"tcp_to_object_dist_end":16.67142,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.31975,0.09841,-24.32597],"object_pos_start":[0.35752,0.09375,-16.37876],"object_to_goal_dist_end":24.5582,"object_to_goal_dist_start":16.61131,"object_z_max":-16.37876,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":302.0,"raw_peak_contact_force":86.029,"tcp_end":[0.56698,0.12613,0.31855],"tcp_start":[0.56688,0.12638,0.29131],"tcp_to_object_dist_end":24.64577,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```