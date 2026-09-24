## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0744 | 0.30 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0508 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0020 | 0.39 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0199 | 0.29 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3980 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.074) — your mutation base

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

- **Composite score**: -0.074
- **task_score** (E): 0.298
- **fitness_score**: 0.626  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1429 |
| descend_1 | 1.00 | 1.00 | 0.1221 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 0.33 | 1.00 | 0.1266 |
| transport_to_goal_1 | 0.00 | 1.00 | 0.1277 |
| descend_to_place_1 | 1.00 | 1.00 | 0.2145 |
| release_1 | 1.00 | 1.00 | 0.0217 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.162) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 9.172 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.162)→(0.494, 0.024, 0.040) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.040)→(0.486, 0.023, 0.031) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.667 | 0.152 | 0.204 |
| lift_1 | lift | 0.33 / step_budget | (0.486, 0.023, 0.031)→(0.491, 0.023, 0.158) | (0.500, 0.024, 0.026)→(0.501, 0.024, 0.144) | 0.272→0.216 | 1.00 / 37.000 | 0.081 | 0.605 |
| transport_to_goal_1 | approach | 0.00 / step_budget | (0.491, 0.023, 0.158)→(0.479, 0.018, 0.277) | (0.501, 0.024, 0.144)→(0.486, 0.018, 0.255) | 0.216→0.222 | 1.00 / 25.667 | 0.119 | 0.191 |
| descend_to_place_1 | descend | 1.00 / step_budget | (0.479, 0.018, 0.277)→(0.586, 0.181, 0.201) | (0.486, 0.018, 0.255)→(0.584, 0.182, 0.175) | 0.222→0.039 | 1.00 / 36.667 | 0.083 | 0.295 |
| release_1 | release | 1.00 / step_budget | (0.586, 0.181, 0.201)→(0.580, 0.179, 0.222) | (0.584, 0.182, 0.175)→(0.582, 0.177, 0.021) | 0.039→0.189 | 1.00 / 1.667 | 0.246 | 1.642 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.434
- phase_score: 0.383
- phase_breakdown.approach_object_score: 0.167
- phase_breakdown.transport_to_goal_score: 0.003
- phase_breakdown.lift_object_score: 0.834
- phase_breakdown.place_at_goal_score: 0.608
- grasp_place_fitness: 0.693

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.693
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.434
- **Median Q (composite search score)**: -0.101
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70349,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04974,"approach_1.approach_z_offset":0.14177,"descend_1.descend_speed":0.09686,"descend_1.descend_z_offset":0.00506,"descend_to_place_1.descend_place_speed":0.13906,"descend_to_place_1.descend_place_z_offset":-0.00205,"descend_to_place_1.descend_tolerance":0.01455,"lift_1.lift_height":0.20687,"lift_1.lift_speed":0.08649,"transport_to_goal_1.transport_arc_height":0.05008,"transport_to_goal_1.transport_speed":0.15012},"optimized_scores":{"best_composite_score":-0.11508,"best_fitness_score":0.58492,"best_task_score":0.21553},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.56126,0.16964,-0.00986],"force_p95":1.58285,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70607,"mean_force":0.57114,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57474,0.17508,0.25505]},{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.50091,-0.01569,-0.00111],"force_p95":0.43028,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63726,"mean_force":0.09288,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48861,-0.0154,0.03214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.5721,0.19447,0.24151],"force_p95":0.06813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31691,"mean_force":0.04296,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57774,0.17623,0.23807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20621.0,"contact_point_centroid":[0.49192,0.00354,0.09911],"force_p95":0.07389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31621,"mean_force":0.04971,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49068,-0.01549,0.09726]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18133.0,"contact_point_centroid":[0.49117,-0.03467,0.10052],"force_p95":0.07927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31497,"mean_force":0.05528,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4907,-0.01549,0.09784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12950.0,"contact_point_centroid":[0.54797,0.08109,0.26522],"force_p95":0.08113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23272,"mean_force":0.05057,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.54417,0.09976,0.2643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1402.0,"contact_point_centroid":[0.58154,0.15724,0.23892],"force_p95":0.06422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21681,"mean_force":0.03872,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57774,0.17623,0.23806]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11270.0,"contact_point_centroid":[0.54266,0.11887,0.26686],"force_p95":0.08856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18324,"mean_force":0.0564,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.54426,0.09992,0.2643]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.1326,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15932,"mean_force":0.12514,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49129,-0.01542,0.03173]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49886,-0.00666,0.241]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16268.0,"contact_point_centroid":[0.49976,-0.02398,0.23378],"force_p95":0.08695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1371,"mean_force":0.05991,"phase_index":4.0,"phase_name":"transport_to_goal_1","phase_type":"approach","tcp_position_centroid":[0.49778,-0.005,0.23221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16695.0,"contact_point_centroid":[0.49996,0.01375,0.23255],"force_p95":0.08435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12749,"mean_force":0.05854,"phase_index":4.0,"phase_name":"transport_to_goal_1","phase_type":"approach","tcp_position_centroid":[0.4977,-0.00517,0.23149]},{"body_a":"world","body_b":"grasp_target","contact_count":1756.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49789,-0.01464,0.10952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.49082,0.00365,0.03237],"force_p95":0.06671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09455,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49006,-0.01541,0.03043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48951,-0.03468,0.03302],"force_p95":0.07899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09404,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49006,-0.01541,0.03043]}],"total_contact_groups":15},"final_pose_error":0.01439,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56989,0.17358,0.01897],"final_tcp_position":[0.57918,0.17627,0.24134],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":27.27042,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":27.27042,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1588.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49979,-0.01386,0.18074],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1756.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49865,-0.01547,0.03958],"tcp_start":[0.49979,-0.01386,0.18074],"tcp_to_object_dist_end":0.01451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01577,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31243,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13269,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.15932,"subtask_id":"lift_object","tcp_end":[0.49003,-0.01541,0.0304],"tcp_start":[0.49865,-0.01547,0.03958],"tcp_to_object_dist_end":0.01438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,-0.01598,0.15862],"object_pos_start":[0.50367,-0.01577,0.02588],"object_to_goal_dist_end":0.23651,"object_to_goal_dist_start":0.31243,"object_z_max":0.15845,"peak_contact_force":0.08267,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38912.0,"raw_peak_contact_force":0.63726,"subtask_id":"lift_object","tcp_end":[0.49603,-0.01562,0.17082],"tcp_start":[0.49003,-0.01541,0.0304],"tcp_to_object_dist_end":0.01577,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51313,0.01077,0.2761],"object_pos_start":[0.50601,-0.01598,0.15862],"object_to_goal_dist_end":0.1935,"object_to_goal_dist_start":0.23651,"object_z_max":0.27604,"peak_contact_force":0.08395,"phase_name":"transport_to_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32963.0,"raw_peak_contact_force":0.1371,"subtask_id":"transport_to_goal","tcp_end":[0.50522,0.01063,0.29579],"tcp_start":[0.49603,-0.01562,0.17082],"tcp_to_object_dist_end":0.02122,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.57486,0.17643,0.21679],"object_pos_start":[0.51313,0.01077,0.2761],"object_to_goal_dist_end":0.03533,"object_to_goal_dist_start":0.1935,"object_z_max":0.27611,"peak_contact_force":0.07322,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24220.0,"raw_peak_contact_force":0.23272,"subtask_id":"place_at_goal","tcp_end":[0.57918,0.17627,0.24134],"tcp_start":[0.50522,0.01063,0.29579],"tcp_to_object_dist_end":0.02493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56989,0.17358,0.01897],"object_pos_start":[0.57486,0.17643,0.21679],"object_to_goal_dist_end":0.2302,"object_to_goal_dist_start":0.03533,"object_z_max":0.21679,"peak_contact_force":0.20943,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2807.0,"raw_peak_contact_force":1.70607,"tcp_end":[0.57469,0.17507,0.26274],"tcp_start":[0.57918,0.17627,0.24134],"tcp_to_object_dist_end":0.24383,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22826,"average_solve_count":276.0,"average_success_count":276.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.02369,"approach_1.approach_z_offset":0.13733,"descend_1.descend_speed":0.0532,"descend_1.descend_z_offset":0.00644,"descend_to_place_1.descend_place_speed":0.17278,"descend_to_place_1.descend_place_z_offset":-0.01023,"descend_to_place_1.descend_tolerance":0.02532,"lift_1.lift_height":0.17541,"lift_1.lift_speed":0.08926,"transport_to_goal_1.transport_arc_height":0.162,"transport_to_goal_1.transport_speed":0.07277},"optimized_scores":{"best_composite_score":-0.007,"best_fitness_score":0.693,"best_task_score":0.43397},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":115.0,"contact_point_centroid":[0.6038,0.13872,-0.00823],"force_p95":1.26857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33268,"mean_force":0.55145,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60321,0.15459,0.14864]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.50917,0.0376,-0.00123],"force_p95":0.40324,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63405,"mean_force":0.09273,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49711,0.03809,0.03315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":986.0,"contact_point_centroid":[0.61444,0.13839,0.13156],"force_p95":0.21659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.61544,"mean_force":0.09673,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60691,0.15573,0.13483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":810.0,"contact_point_centroid":[0.60735,0.17461,0.13478],"force_p95":0.22938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58477,"mean_force":0.09598,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6072,0.15582,0.13516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5089.0,"contact_point_centroid":[0.54382,0.05893,0.20534],"force_p95":0.18179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42108,"mean_force":0.10987,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53772,0.07625,0.20816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4981.0,"contact_point_centroid":[0.54174,0.09681,0.20458],"force_p95":0.17202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35563,"mean_force":0.10327,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53979,0.07858,0.20608]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.50067,0.05735,0.10357],"force_p95":0.08322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33378,"mean_force":0.05861,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50047,0.03815,0.10079]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20718.0,"contact_point_centroid":[0.5022,0.01922,0.10106],"force_p95":0.07815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30557,"mean_force":0.04948,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50035,0.03815,0.09945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12310.0,"contact_point_centroid":[0.47888,0.02547,0.22078],"force_p95":0.12175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25486,"mean_force":0.07803,"phase_index":4.0,"phase_name":"transport_to_goal_1","phase_type":"approach","tcp_position_centroid":[0.47517,0.00663,0.21958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14435.0,"contact_point_centroid":[0.47909,-0.01205,0.22034],"force_p95":0.1036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23096,"mean_force":0.06757,"phase_index":4.0,"phase_name":"transport_to_goal_1","phase_type":"approach","tcp_position_centroid":[0.47509,0.00654,0.2199]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03967,-0.00213],"force_p95":0.16088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22105,"mean_force":0.13262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49977,0.03832,0.03264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5045.0,"contact_point_centroid":[0.50018,0.01922,0.03282],"force_p95":0.07244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17693,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49853,0.03822,0.0313]},{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50257,0.01714,0.23766]},{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50589,0.03707,0.10724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4226.0,"contact_point_centroid":[0.49885,0.05754,0.03407],"force_p95":0.08311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09178,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49854,0.03822,0.03131]}],"total_contact_groups":15},"final_pose_error":0.02488,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61618,0.15139,0.02213],"final_tcp_position":[0.60977,0.1559,0.13989],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.33268,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1860.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50758,0.03548,0.17492],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1808.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50713,0.03891,0.04072],"tcp_start":[0.50758,0.03548,0.17492],"tcp_to_object_dist_end":0.01568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.03883,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21306,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15814,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11071.0,"raw_peak_contact_force":0.22105,"subtask_id":"lift_object","tcp_end":[0.4985,0.03822,0.03127],"tcp_start":[0.50713,0.03891,0.04072],"tcp_to_object_dist_end":0.01513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51654,0.03927,0.15957],"object_pos_start":[0.51249,0.03883,0.02554],"object_to_goal_dist_end":0.17406,"object_to_goal_dist_start":0.21306,"object_z_max":0.1594,"peak_contact_force":0.08088,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37884.0,"raw_peak_contact_force":0.63405,"subtask_id":"lift_object","tcp_end":[0.50683,0.03844,0.173],"tcp_start":[0.4985,0.03822,0.03127],"tcp_to_object_dist_end":0.0166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46322,-0.01449,0.26484],"object_pos_start":[0.51654,0.03927,0.15957],"object_to_goal_dist_end":0.2763,"object_to_goal_dist_start":0.17406,"object_z_max":0.26472,"peak_contact_force":0.15792,"phase_name":"transport_to_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26745.0,"raw_peak_contact_force":0.25486,"subtask_id":"transport_to_goal","tcp_end":[0.45648,-0.01447,0.28939],"tcp_start":[0.50683,0.03844,0.173],"tcp_to_object_dist_end":0.02546,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.61113,0.1578,0.10928],"object_pos_start":[0.46322,-0.01449,0.26484],"object_to_goal_dist_end":0.04201,"object_to_goal_dist_start":0.2763,"object_z_max":0.2649,"peak_contact_force":0.17701,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10070.0,"raw_peak_contact_force":0.42108,"subtask_id":"place_at_goal","tcp_end":[0.60977,0.1559,0.13989],"tcp_start":[0.45648,-0.01447,0.28939],"tcp_to_object_dist_end":0.0307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61618,0.15139,0.02213],"object_pos_start":[0.61113,0.1578,0.10928],"object_to_goal_dist_end":0.12522,"object_to_goal_dist_start":0.04201,"object_z_max":0.10928,"peak_contact_force":0.34228,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1911.0,"raw_peak_contact_force":1.33268,"tcp_end":[0.60312,0.15457,0.16002],"tcp_start":[0.60977,0.1559,0.13989],"tcp_to_object_dist_end":0.13854,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51613,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07097,"approach_1.approach_z_offset":0.09221,"descend_1.descend_speed":0.05406,"descend_1.descend_z_offset":0.00575,"descend_to_place_1.descend_place_speed":0.12451,"descend_to_place_1.descend_place_z_offset":-0.00276,"descend_to_place_1.descend_tolerance":0.0249,"lift_1.lift_height":0.26731,"lift_1.lift_speed":0.05939,"transport_to_goal_1.transport_arc_height":0.06051,"transport_to_goal_1.transport_speed":0.12166},"optimized_scores":{"best_composite_score":-0.10104,"best_fitness_score":0.59896,"best_task_score":0.24519},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":181.0,"contact_point_centroid":[0.54978,0.20125,-0.00805],"force_p95":1.34823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88768,"mean_force":0.42036,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56298,0.2081,0.23592]},{"body_a":"world","body_b":"grasp_target","contact_count":186.0,"contact_point_centroid":[0.47806,0.04559,-0.00124],"force_p95":0.35787,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54337,"mean_force":0.09904,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46762,0.04672,0.03353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1270.0,"contact_point_centroid":[0.56005,0.22761,0.22286],"force_p95":0.07828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37656,"mean_force":0.04504,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56614,0.20957,0.21891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.46755,0.06582,0.08277],"force_p95":0.08426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2871,"mean_force":0.0583,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46768,0.04662,0.08008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20968.0,"contact_point_centroid":[0.46969,0.02771,0.08101],"force_p95":0.07779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25733,"mean_force":0.04858,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46766,0.04662,0.07952]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.57125,0.19086,0.21966],"force_p95":0.07157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23532,"mean_force":0.03849,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56613,0.20956,0.2189]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04864,-0.00216],"force_p95":0.16772,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23309,"mean_force":0.13462,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47045,0.04701,0.03293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7472.0,"contact_point_centroid":[0.52961,0.12178,0.2319],"force_p95":0.10655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23071,"mean_force":0.05514,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.52434,0.13999,0.23138]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5944.0,"contact_point_centroid":[0.52293,0.16033,0.23372],"force_p95":0.11535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20982,"mean_force":0.06573,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.52527,0.14149,0.23118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.47123,0.02791,0.03299],"force_p95":0.07912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19398,"mean_force":0.04318,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46925,0.04689,0.03172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14363.0,"contact_point_centroid":[0.4698,0.06851,0.1853],"force_p95":0.10801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18193,"mean_force":0.06858,"phase_index":4.0,"phase_name":"transport_to_goal_1","phase_type":"approach","tcp_position_centroid":[0.46876,0.04931,0.18382]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48915,0.02178,0.21541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17601.0,"contact_point_centroid":[0.47264,0.031,0.18515],"force_p95":0.08523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13829,"mean_force":0.0555,"phase_index":4.0,"phase_name":"transport_to_goal_1","phase_type":"approach","tcp_position_centroid":[0.4688,0.04938,0.18475]},{"body_a":"world","body_b":"grasp_target","contact_count":1260.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47743,0.04599,0.08523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4244.0,"contact_point_centroid":[0.46922,0.06623,0.03422],"force_p95":0.08626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09777,"mean_force":0.05195,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46926,0.0469,0.03172]}],"total_contact_groups":15},"final_pose_error":0.0246,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55885,0.20599,0.02213],"final_tcp_position":[0.56772,0.2095,0.22224],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.88768,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2196.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48007,0.04456,0.13088],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1260.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47758,0.0477,0.04024],"tcp_start":[0.48007,0.04456,0.13088],"tcp_to_object_dist_end":0.01515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.0476,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29107,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16412,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11049.0,"raw_peak_contact_force":0.23309,"subtask_id":"lift_object","tcp_end":[0.46922,0.04689,0.03169],"tcp_start":[0.47758,0.0477,0.04024],"tcp_to_object_dist_end":0.0149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47928,0.04768,0.11523],"object_pos_start":[0.48273,0.0476,0.02545],"object_to_goal_dist_end":0.23797,"object_to_goal_dist_start":0.29107,"object_z_max":0.11513,"peak_contact_force":0.08024,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38154.0,"raw_peak_contact_force":0.54337,"subtask_id":"lift_object","tcp_end":[0.47037,0.04677,0.12897],"tcp_start":[0.46922,0.04689,0.03169],"tcp_to_object_dist_end":0.0164,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48201,0.05853,0.22414],"object_pos_start":[0.47928,0.04768,0.11523],"object_to_goal_dist_end":0.19754,"object_to_goal_dist_start":0.23797,"object_z_max":0.22399,"peak_contact_force":0.11638,"phase_name":"transport_to_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31964.0,"raw_peak_contact_force":0.18193,"subtask_id":"transport_to_goal","tcp_end":[0.47393,0.05728,0.24599],"tcp_start":[0.47037,0.04677,0.12897],"tcp_to_object_dist_end":0.02333,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.56571,0.21046,0.19798],"object_pos_start":[0.48201,0.05853,0.22414],"object_to_goal_dist_end":0.04069,"object_to_goal_dist_start":0.19754,"object_z_max":0.22421,"peak_contact_force":0.0,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13416.0,"raw_peak_contact_force":0.23071,"subtask_id":"place_at_goal","tcp_end":[0.56772,0.2095,0.22224],"tcp_start":[0.47393,0.05728,0.24599],"tcp_to_object_dist_end":0.02436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55885,0.20599,0.02213],"object_pos_start":[0.56571,0.21046,0.19798],"object_to_goal_dist_end":0.21086,"object_to_goal_dist_start":0.04069,"object_z_max":0.19798,"peak_contact_force":0.18485,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2907.0,"raw_peak_contact_force":1.88768,"tcp_end":[0.56293,0.20809,0.24367],"tcp_start":[0.56772,0.2095,0.22224],"tcp_to_object_dist_end":0.22158,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```