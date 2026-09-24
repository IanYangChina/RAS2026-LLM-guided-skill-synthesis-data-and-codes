## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0894 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0782 | 0.29 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0744 | 0.30 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0508 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0020 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.089) — your mutation base

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

- **Composite score**: -0.089
- **task_score** (E): 0.278
- **fitness_score**: 0.611  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1553 |
| descend_1 | 1.00 | 1.00 | 0.1050 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 0.00 | 1.00 | 0.1165 |
| transport_1 | 0.00 | 1.00 | 0.1104 |
| descend_to_place_1 | 0.00 | 1.00 | 0.1867 |
| release_1 | 1.00 | 1.00 | 0.0256 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.150) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.021, 0.150)→(0.494, 0.024, 0.046) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.046)→(0.486, 0.023, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.333 | 0.150 | 0.200 |
| lift_1 | lift | 0.00 / step_budget | (0.486, 0.023, 0.036)→(0.489, 0.023, 0.153) | (0.500, 0.024, 0.026)→(0.497, 0.024, 0.135) | 0.272→0.217 | 1.00 / 37.333 | 0.081 | 0.542 |
| transport_1 | approach | 0.00 / step_budget | (0.489, 0.023, 0.153)→(0.539, 0.104, 0.202) | (0.497, 0.024, 0.135)→(0.544, 0.106, 0.178) | 0.217→0.111 | 1.00 / 28.667 | 0.129 | 0.168 |
| descend_to_place_1 | descend | 0.00 / step_budget | (0.539, 0.104, 0.202)→(0.670, 0.143, 0.239) | (0.544, 0.106, 0.178)→(0.547, 0.212, 0.019) | 0.111→0.202 | 1.00 / 9.333 | 274.714 | 1804.035 |
| release_1 | release | 1.00 / step_budget | (0.670, 0.143, 0.239)→(0.669, 0.143, 0.265) | (0.547, 0.212, 0.019)→(0.547, 0.212, 0.019) | 0.202→0.202 | 1.00 / 4.000 | 0.123 | 148.570 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.428
- phase_score: 0.200
- phase_breakdown.approach_object_score: 0.224
- phase_breakdown.transport_to_goal_score: 0.152
- phase_breakdown.lift_object_score: 0.532
- phase_breakdown.place_at_goal_score: 0.012
- grasp_place_fitness: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.676
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.428
- **Median Q (composite search score)**: -0.122
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2375,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08083,"approach_1.approach_z_offset":0.06103,"descend_1.descend_speed":0.06191,"descend_1.descend_z_offset":0.00694,"descend_to_place_1.descend_place_speed":0.15196,"descend_to_place_1.descend_place_z_offset":-0.01818,"descend_to_place_1.descend_tolerance":0.04923,"lift_1.lift_height":0.24211,"lift_1.lift_speed":0.0797,"transport_1.transport_height":0.09866,"transport_1.transport_speed":0.09268},"optimized_scores":{"best_composite_score":-0.12222,"best_fitness_score":0.57778,"best_task_score":0.20415},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":19.0,"contact_point_centroid":[0.6301,0.20502,-0.0061],"force_p95":1789.90746,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2075.65806,"mean_force":518.92894,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53906,0.16538,0.00914]},{"body_a":"world","body_b":"link6","contact_count":617.0,"contact_point_centroid":[0.61845,0.03726,-0.00032],"force_p95":434.40305,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":892.83715,"mean_force":333.46992,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.59845,0.08798,0.2787]},{"body_a":"world","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.62749,0.08766,-0.00057],"force_p95":698.17188,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":739.23032,"mean_force":327.809,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.54257,0.18488,0.03138]},{"body_a":"world","body_b":"right_finger","contact_count":161.0,"contact_point_centroid":[0.55252,0.17164,-0.00309],"force_p95":21.04496,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.41306,"mean_force":15.38615,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.54008,0.15991,0.00499]},{"body_a":"world","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.62535,0.06515,-0.00015],"force_p95":78.49871,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.9476,"mean_force":58.34021,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61533,0.09359,0.29264]},{"body_a":"world","body_b":"left_finger","contact_count":31.0,"contact_point_centroid":[0.52537,0.14376,-0.00087],"force_p95":30.95574,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.28344,"mean_force":26.52998,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53916,0.15965,0.00318]},{"body_a":"world","body_b":"grasp_target","contact_count":2560.0,"contact_point_centroid":[0.55527,0.14332,-0.00296],"force_p95":0.41172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.73521,"mean_force":0.19111,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.59628,0.08748,0.27337]},{"body_a":"grasp_target","body_b":"hand","contact_count":30.0,"contact_point_centroid":[0.58116,0.13303,0.01848],"force_p95":1.46476,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.09919,"mean_force":0.99532,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.54318,0.1723,0.02054]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1145.0,"contact_point_centroid":[0.59988,0.07843,0.19186],"force_p95":0.36795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.40688,"mean_force":0.17399,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.59248,0.06118,0.19277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1190.0,"contact_point_centroid":[0.59043,0.0431,0.19285],"force_p95":0.67344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.01655,"mean_force":0.19306,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.59132,0.06211,0.19179]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.50019,-0.01543,-0.00116],"force_p95":0.38567,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61359,"mean_force":0.0962,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48804,-0.01535,0.03332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20570.0,"contact_point_centroid":[0.49065,0.00359,0.09487],"force_p95":0.07426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3151,"mean_force":0.04988,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48927,-0.01542,0.09308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17766.0,"contact_point_centroid":[0.48994,-0.0346,0.09657],"force_p95":0.08016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31487,"mean_force":0.05631,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48931,-0.01542,0.09392]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01575,-0.00203],"force_p95":0.13322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16134,"mean_force":0.12527,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4908,-0.01537,0.03312]},{"body_a":"world","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4985,-0.00716,0.1998]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49748,-0.01498,0.07014]}],"total_contact_groups":23},"final_pose_error":0.11594,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55309,0.14512,0.01602],"final_tcp_position":[0.61527,0.0939,0.29228],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2075.65806,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2500.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49922,-0.01457,0.0997],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":792.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49811,-0.01542,0.04093],"tcp_start":[0.49922,-0.01457,0.0997],"tcp_to_object_dist_end":0.01597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01574,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13326,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.16134,"subtask_id":"lift_object","tcp_end":[0.48954,-0.01536,0.03179],"tcp_start":[0.49811,-0.01542,0.04093],"tcp_to_object_dist_end":0.01534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50329,-0.0159,0.14669],"object_pos_start":[0.50368,-0.01574,0.02588],"object_to_goal_dist_end":0.24214,"object_to_goal_dist_start":0.31241,"object_z_max":0.14655,"peak_contact_force":0.08048,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38498.0,"raw_peak_contact_force":0.61359,"subtask_id":"lift_object","tcp_end":[0.49363,-0.01553,0.16035],"tcp_start":[0.48954,-0.01536,0.03179],"tcp_to_object_dist_end":0.01674,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53161,0.06105,0.20428],"object_pos_start":[0.50329,-0.0159,0.14669],"object_to_goal_dist_end":0.14476,"object_to_goal_dist_start":0.24214,"object_z_max":0.2042,"peak_contact_force":0.08647,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34556.0,"raw_peak_contact_force":0.11491,"subtask_id":"transport_to_goal","tcp_end":[0.5252,0.06008,0.22388],"tcp_start":[0.49363,-0.01553,0.16035],"tcp_to_object_dist_end":0.02065,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":787.0,"n_steps_budget":1000.0,"object_pos_end":[0.55309,0.14512,0.01602],"object_pos_start":[0.53161,0.06105,0.20428],"object_to_goal_dist_end":0.23834,"object_to_goal_dist_start":0.14476,"object_z_max":0.20439,"peak_contact_force":340.22866,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8420.0,"raw_peak_contact_force":2075.65806,"subtask_id":"place_at_goal","tcp_end":[0.61527,0.0939,0.29228],"tcp_start":[0.5252,0.06008,0.22388],"tcp_to_object_dist_end":0.28777,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55309,0.14512,0.01602],"object_pos_start":[0.55309,0.14512,0.01602],"object_to_goal_dist_end":0.23834,"object_to_goal_dist_start":0.23834,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1107.0,"raw_peak_contact_force":89.9476,"subtask_id":"place_at_goal","tcp_end":[0.61552,0.09352,0.31935],"tcp_start":[0.61527,0.0939,0.29228],"tcp_to_object_dist_end":0.31396,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.00559,"average_mean_iterations":4.56425,"average_solve_count":179.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0559,"approach_1.approach_z_offset":0.12663,"descend_1.descend_speed":0.0587,"descend_1.descend_z_offset":0.02115,"descend_to_place_1.descend_place_speed":0.14292,"descend_to_place_1.descend_place_z_offset":-0.0509,"descend_to_place_1.descend_tolerance":0.01126,"lift_1.lift_height":0.21313,"lift_1.lift_speed":0.06393,"transport_1.transport_height":0.04293,"transport_1.transport_speed":0.08763},"optimized_scores":{"best_composite_score":-0.02405,"best_fitness_score":0.67595,"best_task_score":0.4275},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":28.0,"contact_point_centroid":[0.56901,0.13272,-0.00522],"force_p95":1773.14276,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1913.39822,"mean_force":551.49718,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.57196,0.22072,0.05941]},{"body_a":"world","body_b":"link6","contact_count":750.0,"contact_point_centroid":[0.70301,-0.02144,-0.00025],"force_p95":469.64695,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1152.07342,"mean_force":322.73164,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.65283,0.02779,0.28074]},{"body_a":"world","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.6054,0.08879,-0.0003],"force_p95":713.73254,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":736.83029,"mean_force":509.85729,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.59408,0.20125,0.11195]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.73466,0.01314,-0.00013],"force_p95":81.9551,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":267.09815,"mean_force":58.3234,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6827,0.035,0.28778]},{"body_a":"world","body_b":"grasp_target","contact_count":3270.0,"contact_point_centroid":[0.59237,0.20239,-0.00241],"force_p95":0.23623,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.27886,"mean_force":0.14766,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.64923,0.03541,0.2707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":401.0,"contact_point_centroid":[0.58243,0.1242,0.13258],"force_p95":0.85218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.99883,"mean_force":0.27586,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.58038,0.14023,0.14104]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.57122,0.13711,0.15786],"force_p95":0.41754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.81831,"mean_force":0.23024,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.57315,0.11914,0.16133]},{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.5091,0.03741,-0.00122],"force_p95":0.25552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41272,"mean_force":0.07405,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49726,0.03807,0.04776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19356.0,"contact_point_centroid":[0.49865,0.05725,0.09895],"force_p95":0.07645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28145,"mean_force":0.05199,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49852,0.03809,0.09693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20083.0,"contact_point_centroid":[0.49993,0.01903,0.09685],"force_p95":0.07997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25717,"mean_force":0.05052,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49844,0.03809,0.09601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14065.0,"contact_point_centroid":[0.53002,0.09112,0.15344],"force_p95":0.13321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24491,"mean_force":0.06989,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53093,0.07231,0.15392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14808.0,"contact_point_centroid":[0.53451,0.05525,0.15232],"force_p95":0.10734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23488,"mean_force":0.06601,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53219,0.07366,0.15425]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03973,-0.00212],"force_p95":0.15668,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20777,"mean_force":0.13176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49999,0.0383,0.04729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4664.0,"contact_point_centroid":[0.50066,0.01914,0.04668],"force_p95":0.07555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15339,"mean_force":0.04679,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49878,0.0382,0.04595]},{"body_a":"world","body_b":"grasp_target","contact_count":1920.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.1331,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50261,0.01741,0.23203]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50595,0.03721,0.10939]}],"total_contact_groups":20},"final_pose_error":0.24369,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59228,0.20152,0.02602],"final_tcp_position":[0.68291,0.03525,0.28772],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1913.39822,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1920.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50757,0.03579,0.16415],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50715,0.03887,0.05538],"tcp_start":[0.50757,0.03579,0.16415],"tcp_to_object_dist_end":0.02986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51253,0.039,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21292,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11176.0,"raw_peak_contact_force":0.20777,"subtask_id":"lift_object","tcp_end":[0.49875,0.0382,0.04591],"tcp_start":[0.50715,0.03887,0.05538],"tcp_to_object_dist_end":0.02459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5081,0.03909,0.12312],"object_pos_start":[0.51253,0.039,0.02556],"object_to_goal_dist_end":0.18043,"object_to_goal_dist_start":0.21292,"object_z_max":0.12299,"peak_contact_force":0.083,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39624.0,"raw_peak_contact_force":0.41272,"subtask_id":"lift_object","tcp_end":[0.50254,0.03833,0.1501],"tcp_start":[0.49875,0.0382,0.04591],"tcp_to_object_dist_end":0.02756,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5676,0.11112,0.12868],"object_pos_start":[0.5081,0.03909,0.12312],"object_to_goal_dist_end":0.08737,"object_to_goal_dist_start":0.18043,"object_z_max":0.12868,"peak_contact_force":0.15957,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28873.0,"raw_peak_contact_force":0.24491,"subtask_id":"transport_to_goal","tcp_end":[0.5655,0.10942,0.16328],"tcp_start":[0.50254,0.03833,0.1501],"tcp_to_object_dist_end":0.0347,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.59228,0.20152,0.02602],"object_pos_start":[0.5676,0.11112,0.12868],"object_to_goal_dist_end":0.12747,"object_to_goal_dist_start":0.08737,"object_z_max":0.12868,"peak_contact_force":252.13559,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7900.0,"raw_peak_contact_force":1913.39822,"subtask_id":"place_at_goal","tcp_end":[0.68291,0.03525,0.28772],"tcp_start":[0.5655,0.10942,0.16328],"tcp_to_object_dist_end":0.32302,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59228,0.20152,0.02602],"object_pos_start":[0.59228,0.20152,0.02602],"object_to_goal_dist_end":0.12747,"object_to_goal_dist_start":0.12747,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1112.0,"raw_peak_contact_force":267.09815,"subtask_id":"place_at_goal","tcp_end":[0.68313,0.036,0.31257],"tcp_start":[0.68291,0.03525,0.28772],"tcp_to_object_dist_end":0.34316,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44712,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04078,"approach_1.approach_z_offset":0.14978,"descend_1.descend_speed":0.05184,"descend_1.descend_z_offset":0.00556,"descend_to_place_1.descend_place_speed":0.07586,"descend_to_place_1.descend_place_z_offset":0.01287,"descend_to_place_1.descend_tolerance":0.01246,"lift_1.lift_height":0.28049,"lift_1.lift_speed":0.07093,"transport_1.transport_height":0.06431,"transport_1.transport_speed":0.15742},"optimized_scores":{"best_composite_score":-0.12192,"best_fitness_score":0.57808,"best_task_score":0.20275},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.47133,0.1505,-0.00251],"force_p95":1368.23745,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1423.0494,"mean_force":545.82795,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.46013,0.28716,0.07218]},{"body_a":"world","body_b":"link6","contact_count":905.0,"contact_point_centroid":[0.58775,0.08061,-0.00041],"force_p95":276.91025,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1091.53988,"mean_force":253.04843,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.67737,0.28023,0.16222]},{"body_a":"world","body_b":"link6","contact_count":91.0,"contact_point_centroid":[0.58396,0.09453,-0.00015],"force_p95":86.15751,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.66459,"mean_force":61.56968,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.71156,0.29895,0.13736]},{"body_a":"world","body_b":"grasp_target","contact_count":3579.0,"contact_point_centroid":[0.49319,0.28813,-0.00242],"force_p95":0.16875,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.94111,"mean_force":0.14659,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.67559,0.27974,0.15985]},{"body_a":"grasp_target","body_b":"hand","contact_count":15.0,"contact_point_centroid":[0.46652,0.23411,0.03688],"force_p95":0.90601,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97392,"mean_force":0.62141,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.46092,0.28735,0.07335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1105.0,"contact_point_centroid":[0.53437,0.14665,0.1815],"force_p95":0.38345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60806,"mean_force":0.16628,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53139,0.16469,0.18568]},{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.47804,0.04577,-0.00126],"force_p95":0.39687,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6009,"mean_force":0.1025,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46798,0.0468,0.03339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17015.0,"contact_point_centroid":[0.46801,0.06591,0.09219],"force_p95":0.08422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31678,"mean_force":0.05833,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46827,0.04671,0.08951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21036.0,"contact_point_centroid":[0.47017,0.02779,0.09032],"force_p95":0.07741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29004,"mean_force":0.04852,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46824,0.04671,0.08883]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":442.0,"contact_point_centroid":[0.53366,0.1672,0.21935],"force_p95":0.17381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25789,"mean_force":0.10137,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53574,0.14859,0.21567]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04865,-0.00216],"force_p95":0.16635,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23123,"mean_force":0.13425,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47066,0.04708,0.03287]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.47129,0.02797,0.03292],"force_p95":0.07253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19525,"mean_force":0.04273,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46946,0.04697,0.03165]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19827.0,"contact_point_centroid":[0.50283,0.07822,0.18421],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14564,"mean_force":0.04985,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49863,0.09676,0.18325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16766.0,"contact_point_centroid":[0.49679,0.11556,0.18602],"force_p95":0.08079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14064,"mean_force":0.05818,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49849,0.09654,0.18308]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48984,0.02072,0.24415]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47804,0.0453,0.1133]}],"total_contact_groups":21},"final_pose_error":0.18165,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.49528,0.29054,0.01602],"final_tcp_position":[0.71154,0.29866,0.137],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1423.0494,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48109,0.04311,0.18763],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.4778,0.04777,0.04019],"tcp_start":[0.48109,0.04311,0.18763],"tcp_to_object_dist_end":0.01503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48272,0.04765,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29103,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16291,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11101.0,"raw_peak_contact_force":0.23123,"subtask_id":"lift_object","tcp_end":[0.46943,0.04696,0.03162],"tcp_start":[0.4778,0.04777,0.04019],"tcp_to_object_dist_end":0.01467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4805,0.04781,0.13466],"object_pos_start":[0.48272,0.04765,0.02546],"object_to_goal_dist_end":0.22855,"object_to_goal_dist_start":0.29103,"object_z_max":0.13457,"peak_contact_force":0.07996,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38210.0,"raw_peak_contact_force":0.6009,"subtask_id":"lift_object","tcp_end":[0.47141,0.04689,0.14809],"tcp_start":[0.46943,0.04696,0.03162],"tcp_to_object_dist_end":0.01625,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53355,0.14528,0.20094],"object_pos_start":[0.4805,0.04781,0.13466],"object_to_goal_dist_end":0.10096,"object_to_goal_dist_start":0.22855,"object_z_max":0.20088,"peak_contact_force":0.14213,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36593.0,"raw_peak_contact_force":0.14564,"subtask_id":"transport_to_goal","tcp_end":[0.5268,0.14276,0.21955],"tcp_start":[0.47141,0.04689,0.14809],"tcp_to_object_dist_end":0.01995,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49528,0.29054,0.01602],"object_pos_start":[0.53355,0.14528,0.20094],"object_to_goal_dist_end":0.23937,"object_to_goal_dist_start":0.10096,"object_z_max":0.20102,"peak_contact_force":231.77872,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9483.0,"raw_peak_contact_force":1423.0494,"subtask_id":"place_at_goal","tcp_end":[0.71154,0.29866,0.137],"tcp_start":[0.5268,0.14276,0.21955],"tcp_to_object_dist_end":0.24793,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49528,0.29054,0.01602],"object_pos_start":[0.49528,0.29054,0.01602],"object_to_goal_dist_end":0.23937,"object_to_goal_dist_start":0.23937,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1118.0,"raw_peak_contact_force":88.66459,"subtask_id":"place_at_goal","tcp_end":[0.70948,0.2983,0.16167],"tcp_start":[0.71154,0.29866,0.137],"tcp_to_object_dist_end":0.25914,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```