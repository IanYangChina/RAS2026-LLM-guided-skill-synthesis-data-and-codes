## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0782 | 0.29 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0744 | 0.30 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0508 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0020 | 0.39 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0199 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.078) — your mutation base

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

- **Composite score**: -0.078
- **task_score** (E): 0.291
- **fitness_score**: 0.622  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1399 |
| descend_1 | 1.00 | 1.00 | 0.1245 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 0.00 | 1.00 | 0.1540 |
| transport_1 | 0.33 | 1.00 | 0.1675 |
| descend_to_place_1 | 0.67 | 1.00 | 0.0236 |
| release_1 | 1.00 | 1.00 | 0.0306 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.165) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.165)→(0.494, 0.024, 0.041) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 4.437 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.041)→(0.486, 0.023, 0.032) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.667 | 0.152 | 0.205 |
| lift_1 | lift | 0.00 / step_budget | (0.486, 0.023, 0.032)→(0.491, 0.023, 0.186) | (0.500, 0.024, 0.026)→(0.501, 0.024, 0.171) | 0.272→0.211 | 1.00 / 36.000 | 0.094 | 0.617 |
| transport_1 | approach | 0.33 / step_budget | (0.491, 0.023, 0.186)→(0.569, 0.146, 0.251) | (0.501, 0.024, 0.171)→(0.572, 0.147, 0.229) | 0.211→0.065 | 1.00 / 39.667 | 0.081 | 0.230 |
| descend_to_place_1 | descend | 0.67 / step_budget | (0.569, 0.146, 0.251)→(0.577, 0.166, 0.246) | (0.572, 0.147, 0.229)→(0.581, 0.165, 0.222) | 0.065→0.046 | 1.00 / 25.333 | 0.423 | 0.525 |
| release_1 | release | 1.00 / step_budget | (0.577, 0.166, 0.246)→(0.568, 0.171, 0.241) | (0.581, 0.165, 0.222)→(0.569, 0.164, 0.019) | 0.046→0.195 | 1.00 / 3.333 | 0.119 | 1.906 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.404
- phase_breakdown.approach_object_score: 0.163
- phase_breakdown.transport_to_goal_score: 0.774
- phase_breakdown.lift_object_score: 0.694
- phase_breakdown.place_at_goal_score: 0.000
- grasp_place_fitness: 0.699

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.699
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.446
- **Median Q (composite search score)**: -0.111
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32941,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04998,"approach_1.approach_z_offset":0.16234,"descend_1.descend_speed":0.08094,"descend_1.descend_z_offset":0.00713,"descend_to_place_1.descend_place_speed":0.05979,"descend_to_place_1.descend_place_z_offset":0.03068,"descend_to_place_1.descend_tolerance":0.04324,"lift_1.lift_height":0.27868,"lift_1.lift_speed":0.07326,"transport_1.transport_arc_height":0.03472,"transport_1.transport_speed":0.23604},"optimized_scores":{"best_composite_score":-0.12286,"best_fitness_score":0.57714,"best_task_score":0.20222},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":383.0,"contact_point_centroid":[0.54049,0.14846,-0.00475],"force_p95":0.93947,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07619,"mean_force":0.24667,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54018,0.16738,0.19688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.56307,0.15875,0.21201],"force_p95":0.60382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.8613,"mean_force":0.29028,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55139,0.17221,0.21669]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.55103,0.19401,0.21958],"force_p95":0.5296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72846,"mean_force":0.22725,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55167,0.17549,0.21859]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.49878,-0.01527,-0.00115],"force_p95":0.3871,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58889,"mean_force":0.0999,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48861,-0.01539,0.03392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":477.0,"contact_point_centroid":[0.56526,0.11124,0.27221],"force_p95":0.24255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38058,"mean_force":0.13155,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.55946,0.12969,0.27297]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20793.0,"contact_point_centroid":[0.48999,0.00361,0.09189],"force_p95":0.07293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30638,"mean_force":0.04918,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48891,-0.01544,0.09003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18487.0,"contact_point_centroid":[0.48916,-0.03462,0.09259],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30352,"mean_force":0.05416,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48889,-0.01544,0.08988]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":304.0,"contact_point_centroid":[0.55513,0.14351,0.27748],"force_p95":0.18083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26256,"mean_force":0.08412,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.55812,0.1247,0.27496]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18442.0,"contact_point_centroid":[0.52105,0.02779,0.2232],"force_p95":0.07973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20887,"mean_force":0.05528,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51835,0.04657,0.22199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17532.0,"contact_point_centroid":[0.51695,0.06285,0.2214],"force_p95":0.08689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17609,"mean_force":0.05764,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51705,0.04383,0.2194]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15991,"mean_force":0.1252,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49131,-0.01541,0.03375]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49898,-0.00647,0.25118]},{"body_a":"world","body_b":"grasp_target","contact_count":2020.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49791,-0.01448,0.12052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.49084,0.00366,0.03439],"force_p95":0.06669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09503,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49008,-0.0154,0.03245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48953,-0.03467,0.03504],"force_p95":0.07897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09393,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49008,-0.0154,0.03246]}],"total_contact_groups":15},"final_pose_error":0.04189,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53953,0.14839,0.01635],"final_tcp_position":[0.56281,0.1586,0.2603],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.07619,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.4999,-0.01355,0.20111],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2020.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49864,-0.01546,0.0416],"tcp_start":[0.4999,-0.01355,0.20111],"tcp_to_object_dist_end":0.01642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01578,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31243,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13275,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.15991,"subtask_id":"lift_object","tcp_end":[0.49005,-0.0154,0.03242],"tcp_start":[0.49864,-0.01546,0.0416],"tcp_to_object_dist_end":0.01512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50153,-0.01584,0.13818],"object_pos_start":[0.50368,-0.01578,0.02588],"object_to_goal_dist_end":0.24638,"object_to_goal_dist_start":0.31243,"object_z_max":0.13808,"peak_contact_force":0.07971,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39435.0,"raw_peak_contact_force":0.58889,"subtask_id":"lift_object","tcp_end":[0.49234,-0.01552,0.15187],"tcp_start":[0.49005,-0.0154,0.03242],"tcp_to_object_dist_end":0.01649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55991,0.12268,0.25592],"object_pos_start":[0.50153,-0.01584,0.13818],"object_to_goal_dist_end":0.0706,"object_to_goal_dist_start":0.24638,"object_z_max":0.25584,"peak_contact_force":0.08479,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35974.0,"raw_peak_contact_force":0.20887,"subtask_id":"transport_to_goal","tcp_end":[0.55351,0.12067,0.27566],"tcp_start":[0.49234,-0.01552,0.15187],"tcp_to_object_dist_end":0.02085,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.57082,0.15675,0.23556],"object_pos_start":[0.55991,0.12268,0.25592],"object_to_goal_dist_end":0.03686,"object_to_goal_dist_start":0.0706,"object_z_max":0.25623,"peak_contact_force":0.33489,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":781.0,"raw_peak_contact_force":0.38058,"subtask_id":"place_at_goal","tcp_end":[0.56281,0.1586,0.2603],"tcp_start":[0.55351,0.12067,0.27566],"tcp_to_object_dist_end":0.02606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53953,0.14839,0.01635],"object_pos_start":[0.57082,0.15675,0.23556],"object_to_goal_dist_end":0.23976,"object_to_goal_dist_start":0.03686,"object_z_max":0.23556,"peak_contact_force":0.12539,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":2.07619,"subtask_id":"place_at_goal","tcp_end":[0.54011,0.16741,0.21085],"tcp_start":[0.56281,0.1586,0.2603],"tcp_to_object_dist_end":0.19543,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":17.0,"average_failure_rate":0.09827,"average_mean_iterations":23.20231,"average_solve_count":173.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07608,"approach_1.approach_z_offset":0.11813,"descend_1.descend_speed":0.04836,"descend_1.descend_z_offset":0.00528,"descend_to_place_1.descend_place_speed":0.09886,"descend_to_place_1.descend_place_z_offset":0.03733,"descend_to_place_1.descend_tolerance":0.03235,"lift_1.lift_height":0.25006,"lift_1.lift_speed":0.10383,"transport_1.transport_arc_height":0.05036,"transport_1.transport_speed":0.20142},"optimized_scores":{"best_composite_score":-0.00069,"best_fitness_score":0.69931,"best_task_score":0.44561},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":186.0,"contact_point_centroid":[0.6011,0.1608,-0.0075],"force_p95":1.34914,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45259,"mean_force":0.39974,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61337,0.16392,0.20805]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.50829,0.03735,-0.00127],"force_p95":0.43082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67396,"mean_force":0.10351,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49699,0.03808,0.03183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1454.0,"contact_point_centroid":[0.62105,0.14602,0.19488],"force_p95":0.06472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45222,"mean_force":0.03912,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61701,0.16509,0.19349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.62216,0.14616,0.19956],"force_p95":0.29988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37936,"mean_force":0.13306,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.61821,0.16514,0.19814]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49974,0.05729,0.11436],"force_p95":0.08342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34179,"mean_force":0.05913,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49932,0.03809,0.11165]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20510.0,"contact_point_centroid":[0.50135,0.01918,0.11178],"force_p95":0.07932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31662,"mean_force":0.05038,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49924,0.03809,0.11026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.61428,0.18377,0.20248],"force_p95":0.2349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27692,"mean_force":0.15759,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.61821,0.16514,0.19814]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20453.0,"contact_point_centroid":[0.56417,0.08339,0.22541],"force_p95":0.08193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27521,"mean_force":0.05135,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56056,0.10205,0.22454]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17385.0,"contact_point_centroid":[0.55887,0.12115,0.22725],"force_p95":0.08915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24678,"mean_force":0.05824,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5607,0.10221,0.2243]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03966,-0.00213],"force_p95":0.16128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22258,"mean_force":0.13271,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49968,0.03831,0.03145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1270.0,"contact_point_centroid":[0.61304,0.18389,0.19788],"force_p95":0.06715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22054,"mean_force":0.04063,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61701,0.16509,0.1935]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5173.0,"contact_point_centroid":[0.49992,0.0192,0.03174],"force_p95":0.06948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17434,"mean_force":0.04182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49844,0.03821,0.03011]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50262,0.01748,0.22798]},{"body_a":"world","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50582,0.03728,0.09726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4229.0,"contact_point_centroid":[0.4988,0.05754,0.0329],"force_p95":0.08306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09271,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49844,0.03821,0.03011]}],"total_contact_groups":15},"final_pose_error":0.01904,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6096,0.16217,0.02556],"final_tcp_position":[0.61878,0.1653,0.19763],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.45259,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1912.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50756,0.03591,0.15592],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1580.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50705,0.0389,0.03952],"tcp_start":[0.50756,0.03591,0.15592],"tcp_to_object_dist_end":0.01459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.0388,0.02553],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21308,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15858,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11202.0,"raw_peak_contact_force":0.22258,"subtask_id":"lift_object","tcp_end":[0.49841,0.03821,0.03007],"tcp_start":[0.50705,0.0389,0.03952],"tcp_to_object_dist_end":0.0148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51535,0.03926,0.18273],"object_pos_start":[0.51248,0.0388,0.02553],"object_to_goal_dist_end":0.17825,"object_to_goal_dist_start":0.21308,"object_z_max":0.18261,"peak_contact_force":0.08761,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37660.0,"raw_peak_contact_force":0.67396,"subtask_id":"lift_object","tcp_end":[0.50478,0.03835,0.19647],"tcp_start":[0.49841,0.03821,0.03007],"tcp_to_object_dist_end":0.01736,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61673,0.16587,0.17696],"object_pos_start":[0.51535,0.03926,0.18273],"object_to_goal_dist_end":0.03437,"object_to_goal_dist_start":0.17825,"object_z_max":0.22118,"peak_contact_force":0.06888,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37838.0,"raw_peak_contact_force":0.27521,"subtask_id":"transport_to_goal","tcp_end":[0.61796,0.16478,0.19839],"tcp_start":[0.50478,0.03835,0.19647],"tcp_to_object_dist_end":0.0215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.61741,0.1664,0.17609],"object_pos_start":[0.61673,0.16587,0.17696],"object_to_goal_dist_end":0.03326,"object_to_goal_dist_start":0.03437,"object_z_max":0.17696,"peak_contact_force":0.27844,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":135.0,"raw_peak_contact_force":0.37936,"subtask_id":"place_at_goal","tcp_end":[0.61878,0.1653,0.19763],"tcp_start":[0.61796,0.16478,0.19839],"tcp_to_object_dist_end":0.02161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6096,0.16217,0.02556],"object_pos_start":[0.61741,0.1664,0.17609],"object_to_goal_dist_end":0.12125,"object_to_goal_dist_start":0.03326,"object_z_max":0.17609,"peak_contact_force":0.14116,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2910.0,"raw_peak_contact_force":1.45259,"subtask_id":"place_at_goal","tcp_end":[0.61331,0.16391,0.21745],"tcp_start":[0.61878,0.1653,0.19763],"tcp_to_object_dist_end":0.19193,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.04089,"average_mean_iterations":11.63197,"average_solve_count":269.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04895,"approach_1.approach_z_offset":0.1,"descend_1.descend_speed":0.01041,"descend_1.descend_z_offset":0.00636,"descend_to_place_1.descend_place_speed":0.16353,"descend_to_place_1.descend_place_z_offset":0.05293,"descend_to_place_1.descend_tolerance":0.01479,"lift_1.lift_height":0.2666,"lift_1.lift_speed":0.1106,"transport_1.transport_arc_height":0.03568,"transport_1.transport_speed":0.16017},"optimized_scores":{"best_composite_score":-0.11091,"best_fitness_score":0.58909,"best_task_score":0.22614},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":208.0,"contact_point_centroid":[0.5573,0.1852,-0.00819],"force_p95":1.47409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18899,"mean_force":0.42968,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54918,0.18183,0.28636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":308.0,"contact_point_centroid":[0.56494,0.16898,0.27171],"force_p95":0.66553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.1076,"mean_force":0.20668,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55527,0.18664,0.2745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":447.0,"contact_point_centroid":[0.55404,0.20923,0.27109],"force_p95":0.66111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.08535,"mean_force":0.18187,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55535,0.18919,0.26919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.53541,0.17439,0.28226],"force_p95":0.32755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.81399,"mean_force":0.15136,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53691,0.15536,0.27888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":250.0,"contact_point_centroid":[0.54521,0.13949,0.27941],"force_p95":0.54207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.74274,"mean_force":0.30169,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53862,0.15794,0.27906]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.47962,0.04582,-0.00135],"force_p95":0.33779,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58777,"mean_force":0.08753,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46784,0.04676,0.0341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17050.0,"contact_point_centroid":[0.47044,0.06601,0.11997],"force_p95":0.10583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31401,"mean_force":0.06064,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47006,0.04678,0.11777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20595.0,"contact_point_centroid":[0.47251,0.02812,0.11843],"force_p95":0.08418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29136,"mean_force":0.04982,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47002,0.04678,0.11701]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04865,-0.00216],"force_p95":0.16701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23138,"mean_force":0.13443,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4705,0.04704,0.03356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18392.0,"contact_point_centroid":[0.50707,0.07911,0.25121],"force_p95":0.08966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20683,"mean_force":0.05371,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5021,0.09698,0.25059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12772.0,"contact_point_centroid":[0.50244,0.11638,0.25223],"force_p95":0.11573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20127,"mean_force":0.07909,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50215,0.09709,0.25062]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5006.0,"contact_point_centroid":[0.47127,0.02794,0.03362],"force_p95":0.07898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19664,"mean_force":0.04321,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4693,0.04692,0.03235]},{"body_a":"world","body_b":"grasp_target","contact_count":2220.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48919,0.02167,0.21929]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4774,0.04593,0.0897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4239.0,"contact_point_centroid":[0.46924,0.06625,0.03483],"force_p95":0.08646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09689,"mean_force":0.05196,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04692,0.03235]}],"total_contact_groups":15},"final_pose_error":0.06356,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55797,0.18062,0.01409],"final_tcp_position":[0.54932,0.17436,0.28019],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":13.06587,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":556.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48015,0.04447,0.13839],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":13.06587,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47761,0.04772,0.04086],"tcp_start":[0.48015,0.04447,0.13839],"tcp_to_object_dist_end":0.01572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.04764,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29104,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16348,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11045.0,"raw_peak_contact_force":0.23138,"subtask_id":"lift_object","tcp_end":[0.46927,0.04692,0.03232],"tcp_start":[0.47761,0.04772,0.04086],"tcp_to_object_dist_end":0.01512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48616,0.048,0.19124],"object_pos_start":[0.48273,0.04764,0.02545],"object_to_goal_dist_end":0.20835,"object_to_goal_dist_start":0.29104,"object_z_max":0.19109,"peak_contact_force":0.11477,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37797.0,"raw_peak_contact_force":0.58777,"subtask_id":"lift_object","tcp_end":[0.47533,0.04709,0.20829],"tcp_start":[0.46927,0.04692,0.03232],"tcp_to_object_dist_end":0.02022,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54066,0.15335,0.25503],"object_pos_start":[0.48616,0.048,0.19124],"object_to_goal_dist_end":0.08945,"object_to_goal_dist_start":0.20835,"object_z_max":0.25502,"peak_contact_force":0.08838,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31164.0,"raw_peak_contact_force":0.20683,"subtask_id":"transport_to_goal","tcp_end":[0.5342,0.15149,0.27858],"tcp_start":[0.47533,0.04709,0.20829],"tcp_to_object_dist_end":0.02449,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.55368,0.17262,0.25527],"object_pos_start":[0.54066,0.15335,0.25503],"object_to_goal_dist_end":0.06761,"object_to_goal_dist_start":0.08945,"object_z_max":0.25535,"peak_contact_force":0.65636,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":410.0,"raw_peak_contact_force":0.81399,"subtask_id":"place_at_goal","tcp_end":[0.54932,0.17436,0.28019],"tcp_start":[0.5342,0.15149,0.27858],"tcp_to_object_dist_end":0.02535,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55797,0.18062,0.01409],"object_pos_start":[0.55368,0.17262,0.25527],"object_to_goal_dist_end":0.22299,"object_to_goal_dist_start":0.06761,"object_z_max":0.25527,"peak_contact_force":0.09145,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":963.0,"raw_peak_contact_force":2.18899,"subtask_id":"place_at_goal","tcp_end":[0.54913,0.18184,0.29432],"tcp_start":[0.54932,0.17436,0.28019],"tcp_to_object_dist_end":0.28037,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```