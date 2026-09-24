## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0020 | 0.39 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0199 | 0.29 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3980 | 0.29 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0208 | 0.30 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.002) — your mutation base

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

- **Composite score**: 0.002
- **task_score** (E): 0.395
- **fitness_score**: 0.672  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1454 |
| descend_1 | 1.00 | 1.00 | 0.1168 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 0.00 | 1.00 | 0.1073 |
| transport_1 | 0.00 | 1.00 | 0.1083 |
| descend_to_place_1 | 0.33 | 1.00 | 0.1601 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.160) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.160)→(0.494, 0.024, 0.043) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.043)→(0.486, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.333 | 0.151 | 0.201 |
| lift_1 | lift | 0.00 / step_budget | (0.486, 0.023, 0.034)→(0.489, 0.023, 0.141) | (0.500, 0.024, 0.026)→(0.498, 0.024, 0.126) | 0.272→0.220 | 1.00 / 37.000 | 0.080 | 0.546 |
| transport_1 | approach | 0.00 / step_budget | (0.489, 0.023, 0.141)→(0.539, 0.103, 0.191) | (0.498, 0.024, 0.126)→(0.543, 0.105, 0.171) | 0.220→0.117 | 1.00 / 36.667 | 0.082 | 0.124 |
| descend_to_place_1 | descend | 0.33 / step_budget | (0.539, 0.103, 0.191)→(0.646, 0.204, 0.202) | (0.543, 0.105, 0.171)→(0.531, 0.181, 0.058) | 0.117→0.173 | 1.00 / 11.333 | 3350.477 | 850.633 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.786
- phase_score: 0.335
- phase_breakdown.approach_object_score: 0.179
- phase_breakdown.transport_to_goal_score: 0.178
- phase_breakdown.lift_object_score: 0.408
- phase_breakdown.place_at_goal_score: 0.546
- grasp_place_fitness: 0.867

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.867
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.786
- **Median Q (composite search score)**: -0.095
- **K-run variance**: 0.0189
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27099,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03924,"approach_1.approach_z_offset":0.12524,"descend_1.descend_speed":0.02442,"descend_1.descend_z_offset":0.00975,"descend_to_place_1.descend_place_speed":0.12542,"descend_to_place_1.descend_place_z_offset":-0.00531,"descend_to_place_1.descend_tolerance":0.01447,"lift_1.lift_height":0.20551,"lift_1.lift_speed":0.07186,"transport_1.transport_height":0.06848,"transport_1.transport_speed":0.11574},"optimized_scores":{"best_composite_score":-0.09468,"best_fitness_score":0.57532,"best_task_score":0.2026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":148.0,"contact_point_centroid":[0.62613,0.13377,-0.00159],"force_p95":601.8291,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1224.71159,"mean_force":323.9354,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.55096,0.08837,0.01264]},{"body_a":"world","body_b":"link6","contact_count":666.0,"contact_point_centroid":[0.60619,0.09124,-0.00027],"force_p95":351.60639,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":479.0512,"mean_force":299.59907,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.56799,0.12251,0.2742]},{"body_a":"world","body_b":"right_finger","contact_count":865.0,"contact_point_centroid":[0.57832,0.08728,-0.01027],"force_p95":9.08241,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.30353,"mean_force":5.33638,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.56998,0.07212,-0.00902]},{"body_a":"world","body_b":"left_finger","contact_count":749.0,"contact_point_centroid":[0.56299,0.05425,-0.00965],"force_p95":8.733,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.02036,"mean_force":5.34853,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.57048,0.07087,-0.01151]},{"body_a":"world","body_b":"grasp_target","contact_count":2176.0,"contact_point_centroid":[0.55983,0.10721,-0.00644],"force_p95":1.02626,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.00285,"mean_force":0.4628,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.55897,0.12008,0.21317]},{"body_a":"grasp_target","body_b":"hand","contact_count":188.0,"contact_point_centroid":[0.62654,0.06613,0.0315],"force_p95":1.77017,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.69656,"mean_force":1.05398,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.54946,0.09159,0.0167]},{"body_a":"grasp_target","body_b":"link7","contact_count":88.0,"contact_point_centroid":[0.59665,0.10232,0.03415],"force_p95":1.65766,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.99275,"mean_force":0.84206,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.47708,0.13987,0.07995]},{"body_a":"grasp_target","body_b":"link6","contact_count":603.0,"contact_point_centroid":[0.56412,0.10455,0.04049],"force_p95":0.67922,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.27007,"mean_force":0.4995,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.57803,0.11792,0.29168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.57882,0.02492,0.19018],"force_p95":0.33298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.19986,"mean_force":0.14947,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.57745,0.04429,0.19022]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":798.0,"contact_point_centroid":[0.57511,0.06611,0.19296],"force_p95":0.39599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.74862,"mean_force":0.1627,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.57121,0.04751,0.19219]},{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.49897,-0.0153,-0.00114],"force_p95":0.34234,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53778,"mean_force":0.0926,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48861,-0.01539,0.03655]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20817.0,"contact_point_centroid":[0.49113,0.00357,0.0936],"force_p95":0.07277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29652,"mean_force":0.04904,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49004,-0.01548,0.09174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18471.0,"contact_point_centroid":[0.49029,-0.03465,0.09416],"force_p95":0.07847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29171,"mean_force":0.05411,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49001,-0.01548,0.09144]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16023,"mean_force":0.12523,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49126,-0.01541,0.03635]},{"body_a":"world","body_b":"grasp_target","contact_count":1816.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49877,-0.00679,0.23262]},{"body_a":"world","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49761,-0.01473,0.10391]}],"total_contact_groups":21},"final_pose_error":0.07536,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5487,0.13488,0.01762],"final_tcp_position":[0.59332,0.1318,0.29322],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.77147,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1816.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49968,-0.01406,0.1642],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1696.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49853,-0.01546,0.04417],"tcp_start":[0.49968,-0.01406,0.1642],"tcp_to_object_dist_end":0.01891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01579,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31244,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13261,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.16023,"subtask_id":"lift_object","tcp_end":[0.49001,-0.0154,0.03502],"tcp_start":[0.49853,-0.01546,0.04417],"tcp_to_object_dist_end":0.01646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50327,-0.01593,0.13649],"object_pos_start":[0.50369,-0.01579,0.02588],"object_to_goal_dist_end":0.24661,"object_to_goal_dist_start":0.31244,"object_z_max":0.13639,"peak_contact_force":0.07933,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39447.0,"raw_peak_contact_force":0.53778,"subtask_id":"lift_object","tcp_end":[0.49461,-0.01559,0.15253],"tcp_start":[0.49001,-0.0154,0.03502],"tcp_to_object_dist_end":0.01823,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53486,0.06875,0.19257],"object_pos_start":[0.50327,-0.01593,0.13649],"object_to_goal_dist_end":0.14101,"object_to_goal_dist_start":0.24661,"object_z_max":0.1925,"peak_contact_force":0.08859,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36603.0,"raw_peak_contact_force":0.10607,"subtask_id":"transport_to_goal","tcp_end":[0.52914,0.06751,0.2137],"tcp_start":[0.49461,-0.01559,0.15253],"tcp_to_object_dist_end":0.02193,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5487,0.13488,0.01762],"object_pos_start":[0.53486,0.06875,0.19257],"object_to_goal_dist_end":0.23948,"object_to_goal_dist_start":0.14101,"object_z_max":0.19266,"peak_contact_force":9748.77147,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10286.0,"raw_peak_contact_force":1224.71159,"subtask_id":"place_at_goal","tcp_end":[0.59332,0.1318,0.29322],"tcp_start":[0.52914,0.06751,0.2137],"tcp_to_object_dist_end":0.2792,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45198,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06418,"approach_1.approach_z_offset":0.14307,"descend_1.descend_speed":0.05268,"descend_1.descend_z_offset":0.00997,"descend_to_place_1.descend_place_speed":0.11494,"descend_to_place_1.descend_place_z_offset":0.00287,"descend_to_place_1.descend_tolerance":0.02959,"lift_1.lift_height":0.20068,"lift_1.lift_speed":0.06278,"transport_1.transport_height":0.05664,"transport_1.transport_speed":0.12654},"optimized_scores":{"best_composite_score":0.1965,"best_fitness_score":0.8665,"best_task_score":0.78562},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.5697,0.13753,0.16969],"force_p95":0.34343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.29227,"mean_force":0.1269,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.57213,0.11877,0.16645]},{"body_a":"world","body_b":"grasp_target","contact_count":187.0,"contact_point_centroid":[0.50845,0.03752,-0.00121],"force_p95":0.33558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53221,"mean_force":0.09046,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49704,0.03809,0.03652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":499.0,"contact_point_centroid":[0.58482,0.11426,0.16405],"force_p95":0.338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53195,"mean_force":0.15407,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.58064,0.13416,0.16496]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49844,0.05727,0.08794],"force_p95":0.08334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30217,"mean_force":0.0583,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49827,0.03807,0.08516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20781.0,"contact_point_centroid":[0.49998,0.01914,0.08588],"force_p95":0.07741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27271,"mean_force":0.04901,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4982,0.03807,0.08428]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03969,-0.00213],"force_p95":0.15873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21057,"mean_force":0.13205,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49985,0.03833,0.03612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5032.0,"contact_point_centroid":[0.50029,0.01923,0.03627],"force_p95":0.07387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17785,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49862,0.03823,0.03478]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18660.0,"contact_point_centroid":[0.53612,0.09899,0.15425],"force_p95":0.07705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1486,"mean_force":0.05171,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53781,0.07996,0.15079]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21713.0,"contact_point_centroid":[0.53944,0.06004,0.15194],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14813,"mean_force":0.04572,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5369,0.07898,0.15034]},{"body_a":"world","body_b":"grasp_target","contact_count":1672.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13434,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50265,0.01715,0.24021]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50594,0.03704,0.11171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4219.0,"contact_point_centroid":[0.4989,0.05754,0.03753],"force_p95":0.08362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.089,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49863,0.03823,0.03478]}],"total_contact_groups":12},"final_pose_error":0.02894,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59536,0.16659,0.12962],"final_tcp_position":[0.60142,0.17517,0.16],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":197.73772,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50761,0.03539,0.18036],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50717,0.03892,0.0442],"tcp_start":[0.50761,0.03539,0.18036],"tcp_to_object_dist_end":0.01897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.0389,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21299,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15635,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11051.0,"raw_peak_contact_force":0.21057,"subtask_id":"lift_object","tcp_end":[0.49859,0.03823,0.03474],"tcp_start":[0.50717,0.03892,0.0442],"tcp_to_object_dist_end":0.01668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51055,0.03905,0.11989],"object_pos_start":[0.5125,0.0389,0.02556],"object_to_goal_dist_end":0.17927,"object_to_goal_dist_start":0.21299,"object_z_max":0.11977,"peak_contact_force":0.08063,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37968.0,"raw_peak_contact_force":0.53221,"subtask_id":"lift_object","tcp_end":[0.5022,0.03827,0.13646],"tcp_start":[0.49859,0.03823,0.03474],"tcp_to_object_dist_end":0.01857,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57047,0.11544,0.14583],"object_pos_start":[0.51055,0.03905,0.11989],"object_to_goal_dist_end":0.08074,"object_to_goal_dist_start":0.17927,"object_z_max":0.14579,"peak_contact_force":0.06938,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40373.0,"raw_peak_contact_force":0.1486,"subtask_id":"transport_to_goal","tcp_end":[0.57025,0.1145,0.16667],"tcp_start":[0.5022,0.03827,0.13646],"tcp_to_object_dist_end":0.02086,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.59536,0.16659,0.12962],"object_pos_start":[0.57047,0.11544,0.14583],"object_to_goal_dist_end":0.03619,"object_to_goal_dist_start":0.08074,"object_z_max":0.14583,"peak_contact_force":197.73772,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":654.0,"raw_peak_contact_force":1.29227,"subtask_id":"place_at_goal","tcp_end":[0.60142,0.17517,0.16],"tcp_start":[0.57025,0.1145,0.16667],"tcp_to_object_dist_end":0.03214,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18062,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06195,"approach_1.approach_z_offset":0.09627,"descend_1.descend_speed":0.02536,"descend_1.descend_z_offset":0.00639,"descend_to_place_1.descend_place_speed":0.09375,"descend_to_place_1.descend_place_z_offset":-0.01164,"descend_to_place_1.descend_tolerance":0.03156,"lift_1.lift_height":0.23212,"lift_1.lift_speed":0.06269,"transport_1.transport_height":0.05072,"transport_1.transport_speed":0.1269},"optimized_scores":{"best_composite_score":-0.09594,"best_fitness_score":0.57406,"best_task_score":0.19593},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":901.0,"contact_point_centroid":[0.60126,0.09629,-0.00036],"force_p95":313.86856,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1325.89399,"mean_force":269.90583,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.70919,0.27343,0.17483]},{"body_a":"world","body_b":"hand","contact_count":19.0,"contact_point_centroid":[0.55797,0.26858,-0.00322],"force_p95":1138.46883,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1162.86491,"mean_force":402.97697,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.45389,0.27099,0.03977]},{"body_a":"world","body_b":"grasp_target","contact_count":3576.0,"contact_point_centroid":[0.44797,0.24219,-0.00262],"force_p95":0.20869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.9185,"mean_force":0.15825,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.7057,0.27328,0.17102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.51655,0.14125,0.1452],"force_p95":0.43634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.81545,"mean_force":0.18822,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.51794,0.15981,0.14706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":679.0,"contact_point_centroid":[0.52411,0.16512,0.16696],"force_p95":0.36011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.77587,"mean_force":0.13638,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.5221,0.14801,0.16467]},{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.47867,0.04576,-0.00123],"force_p95":0.37967,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5689,"mean_force":0.09362,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46776,0.04674,0.03412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.4682,0.06587,0.08589],"force_p95":0.08427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30441,"mean_force":0.05829,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46834,0.04667,0.0832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20961.0,"contact_point_centroid":[0.47033,0.02776,0.0841],"force_p95":0.07775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27511,"mean_force":0.04859,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4683,0.04667,0.0826]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04865,-0.00216],"force_p95":0.16727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23179,"mean_force":0.13451,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47049,0.04703,0.03343]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5006.0,"contact_point_centroid":[0.47126,0.02793,0.03349],"force_p95":0.07899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19607,"mean_force":0.0432,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46929,0.04691,0.03222]},{"body_a":"world","body_b":"grasp_target","contact_count":2220.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48917,0.02171,0.21747]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47741,0.04594,0.08771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19884.0,"contact_point_centroid":[0.49794,0.07053,0.16475],"force_p95":0.07305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11809,"mean_force":0.04943,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49396,0.08916,0.1637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16961.0,"contact_point_centroid":[0.49249,0.10831,0.16685],"force_p95":0.07864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11687,"mean_force":0.05649,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49403,0.08927,0.16379]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4241.0,"contact_point_centroid":[0.46924,0.06625,0.03471],"force_p95":0.0864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09717,"mean_force":0.05195,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46929,0.04691,0.03222]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3368.0,"contact_point_centroid":[0.72423,0.27333,0.17454],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.7254,0.27493,0.17584]}],"total_contact_groups":17},"final_pose_error":0.19119,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44841,0.24156,0.02602],"final_tcp_position":[0.744,0.30483,0.15178],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1325.89399,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":556.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48011,0.04449,0.13489],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47761,0.04771,0.04074],"tcp_start":[0.48011,0.04449,0.13489],"tcp_to_object_dist_end":0.01561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.04763,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29105,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16371,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11047.0,"raw_peak_contact_force":0.23179,"subtask_id":"lift_object","tcp_end":[0.46926,0.04691,0.03219],"tcp_start":[0.47761,0.04771,0.04074],"tcp_to_object_dist_end":0.01508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48034,0.04776,0.12027],"object_pos_start":[0.48273,0.04763,0.02545],"object_to_goal_dist_end":0.23505,"object_to_goal_dist_start":0.29105,"object_z_max":0.12015,"peak_contact_force":0.08105,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38141.0,"raw_peak_contact_force":0.5689,"subtask_id":"lift_object","tcp_end":[0.47157,0.04685,0.13453],"tcp_start":[0.46926,0.04691,0.03219],"tcp_to_object_dist_end":0.01677,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52307,0.12938,0.17451],"object_pos_start":[0.48034,0.04776,0.12027],"object_to_goal_dist_end":0.1284,"object_to_goal_dist_start":0.23505,"object_z_max":0.17447,"peak_contact_force":0.08749,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36845.0,"raw_peak_contact_force":0.11809,"subtask_id":"transport_to_goal","tcp_end":[0.51715,0.12718,0.19367],"tcp_start":[0.47157,0.04685,0.13453],"tcp_to_object_dist_end":0.02017,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44841,0.24156,0.02602],"object_pos_start":[0.52307,0.12938,0.17451],"object_to_goal_dist_end":0.2445,"object_to_goal_dist_start":0.1284,"object_z_max":0.17453,"peak_contact_force":104.92326,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9806.0,"raw_peak_contact_force":1325.89399,"subtask_id":"place_at_goal","tcp_end":[0.744,0.30483,0.15178],"tcp_start":[0.51715,0.12718,0.19367],"tcp_to_object_dist_end":0.3274,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```