## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | time_limit | time_limit | grasp_success | time_limit | time_limit | time_limit | 13 | -0.0112 | 0.57 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4577 | 1.00 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4577 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4026 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4576 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=-0.011) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_at_goal
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
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
    - 0.06
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp
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
- id: lift
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
    - 0.2
    tolerance: 0.015
    orientation:
      mode: none
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.015
    orientation:
      mode: none
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.015
    orientation:
      mode: none
  parameters:
    place_height_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.06], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.02], tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - place_height_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.011
- **task_score** (E): 0.570
- **fitness_score**: 0.759  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1454 |
| descend_to_grasp | 1.00 | 1.00 | 0.1182 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1379 |
| transport_to_goal | 1.00 | 1.00 | 0.0975 |
| descend_to_place | 1.00 | 1.00 | 0.0606 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.508, -0.014, 0.161) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / time_limit | (0.508, -0.014, 0.161)→(0.509, -0.016, 0.042) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.509, -0.016, 0.042)→(0.501, -0.016, 0.033) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 43.000 | 0.138 | 0.168 |
| lift | lift | 1.00 / time_limit | (0.501, -0.016, 0.033)→(0.510, -0.017, 0.171) | (0.515, -0.017, 0.026)→(0.521, -0.017, 0.156) | 0.270→0.229 | 1.00 / 35.667 | 0.102 | 0.585 |
| transport_to_goal | approach | 1.00 / time_limit | (0.510, -0.017, 0.171)→(0.551, 0.060, 0.209) | (0.521, -0.017, 0.156)→(0.557, 0.061, 0.188) | 0.229→0.144 | 1.00 / 34.000 | 0.088 | 0.155 |
| descend_to_place | descend | 1.00 / time_limit | (0.551, 0.060, 0.209)→(0.576, 0.111, 0.194) | (0.557, 0.061, 0.188)→(0.580, 0.113, 0.167) | 0.144→0.085 | 1.00 / 24.000 | 0.124 | 0.175 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.626
- phase_score: 0.360
- phase_breakdown.place_at_goal_score: 0.207
- phase_breakdown.lift_object_score: 0.757
- phase_breakdown.reach_object_score: 0.144
- grasp_place_fitness: 0.792

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.792
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.626
- **Median Q (composite search score)**: -0.022
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.336


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93701,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10638,"approach_object.approach_speed":0.10038,"approach_object.phase_max_time_approach":2.11602,"descend_to_grasp.descend_depth":0.00612,"descend_to_grasp.phase_max_time_descend":6.81858,"descend_to_place.phase_max_time_place":12.00841,"descend_to_place.place_height_z":0.03368,"descend_to_place.place_speed":0.07755,"lift.lift_height":0.20188,"lift.lift_speed":0.09477,"lift.phase_max_time_lift":13.4904,"transport_to_goal.phase_max_time_transport":5.48686,"transport_to_goal.transport_speed":0.14191},"optimized_scores":{"best_composite_score":-0.03361,"best_fitness_score":0.73639,"best_task_score":0.535},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":237.0,"contact_point_centroid":[0.53324,-0.02042,-0.0013],"force_p95":0.25057,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53762,"mean_force":0.09107,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51977,-0.02042,0.03969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16541.0,"contact_point_centroid":[0.52486,-0.03977,0.1073],"force_p95":0.113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38989,"mean_force":0.06389,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52331,-0.02059,0.10535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20299.0,"contact_point_centroid":[0.52515,-0.002,0.10846],"force_p95":0.08522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30999,"mean_force":0.05016,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52346,-0.02059,0.10683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12577.0,"contact_point_centroid":[0.56555,0.12174,0.22735],"force_p95":0.1215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19511,"mean_force":0.07337,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56457,0.10286,0.22761]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02137,-0.00207],"force_p95":0.14485,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19361,"mean_force":0.12846,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5229,-0.02045,0.03977]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13680.0,"contact_point_centroid":[0.54689,0.0079,0.20617],"force_p95":0.11032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19267,"mean_force":0.07131,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54227,0.02673,0.20549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10728.0,"contact_point_centroid":[0.57298,0.08522,0.22692],"force_p95":0.13424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19068,"mean_force":0.08518,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56453,0.1027,0.22762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17585.0,"contact_point_centroid":[0.54372,0.04407,0.2059],"force_p95":0.08582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1491,"mean_force":0.05428,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54185,0.0254,0.20477]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51419,-0.01008,0.2173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4817.0,"contact_point_centroid":[0.52342,-0.00151,0.03973],"force_p95":0.07025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12653,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52164,-0.02043,0.03831]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.527,-0.01917,0.09288]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4174.0,"contact_point_centroid":[0.52288,-0.03967,0.04096],"force_p95":0.0897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09306,"mean_force":0.05418,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52164,-0.02043,0.03832]}],"total_contact_groups":12},"final_pose_error":0.09798,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58127,0.1395,0.19434],"final_tcp_position":[0.57609,0.13678,0.22871],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.53762,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52618,-0.01728,0.16104],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13552,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53014,-0.02055,0.04821],"tcp_start":[0.52618,-0.01728,0.16104],"tcp_to_object_dist_end":0.02325,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53708,-0.02101,0.02572],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31663,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14448,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.19361,"tcp_end":[0.52161,-0.02043,0.03828],"tcp_start":[0.53014,-0.02055,0.04821],"tcp_to_object_dist_end":0.01993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53999,-0.021,0.16375],"object_pos_start":[0.53708,-0.02101,0.02572],"object_to_goal_dist_end":0.26217,"object_to_goal_dist_start":0.31663,"object_z_max":0.16358,"peak_contact_force":0.11593,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37077.0,"raw_peak_contact_force":0.53762,"subtask_id":"lift_object","tcp_end":[0.53026,-0.02082,0.18419],"tcp_start":[0.52161,-0.02043,0.03828],"tcp_to_object_dist_end":0.02263,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5647,0.07681,0.20642],"object_pos_start":[0.53999,-0.021,0.16375],"object_to_goal_dist_end":0.15769,"object_to_goal_dist_start":0.26217,"object_z_max":0.20638,"peak_contact_force":0.10318,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31265.0,"raw_peak_contact_force":0.19267,"subtask_id":"place_at_goal","tcp_end":[0.55797,0.07499,0.23274],"tcp_start":[0.53026,-0.02082,0.18419],"tcp_to_object_dist_end":0.02722,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58127,0.1395,0.19434],"object_pos_start":[0.5647,0.07681,0.20642],"object_to_goal_dist_end":0.09382,"object_to_goal_dist_start":0.15769,"object_z_max":0.20642,"peak_contact_force":0.13612,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23305.0,"raw_peak_contact_force":0.19511,"subtask_id":"place_at_goal","tcp_end":[0.57609,0.13678,0.22871],"tcp_start":[0.55797,0.07499,0.23274],"tcp_to_object_dist_end":0.03486,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94444,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11027,"approach_object.approach_speed":0.14893,"approach_object.phase_max_time_approach":5.73545,"descend_to_grasp.descend_depth":0.01716,"descend_to_grasp.phase_max_time_descend":6.63292,"descend_to_place.phase_max_time_place":8.83353,"descend_to_place.place_height_z":0.01286,"descend_to_place.place_speed":0.07461,"lift.lift_height":0.14963,"lift.lift_speed":0.11773,"lift.phase_max_time_lift":13.41938,"transport_to_goal.phase_max_time_transport":5.93063,"transport_to_goal.transport_speed":0.08781},"optimized_scores":{"best_composite_score":-0.02215,"best_fitness_score":0.74785,"best_task_score":0.55072},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":297.0,"contact_point_centroid":[0.54262,-0.02884,-0.00157],"force_p95":0.25024,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53368,"mean_force":0.10702,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52888,-0.02851,0.03624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12555.0,"contact_point_centroid":[0.53396,-0.04785,0.09612],"force_p95":0.09523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3085,"mean_force":0.06016,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53336,-0.02865,0.09351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14875.0,"contact_point_centroid":[0.5348,-0.00977,0.09277],"force_p95":0.07978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30282,"mean_force":0.05087,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53312,-0.02864,0.0911]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11802.0,"contact_point_centroid":[0.58083,0.03553,0.18726],"force_p95":0.13605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20814,"mean_force":0.07903,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57372,0.0538,0.18695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14424.0,"contact_point_centroid":[0.57723,0.07428,0.18756],"force_p95":0.09575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19337,"mean_force":0.06448,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57452,0.05546,0.18681]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02926,-0.00205],"force_p95":0.13961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16596,"mean_force":0.12701,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53234,-0.0286,0.03713]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12912.0,"contact_point_centroid":[0.55457,-0.01848,0.17645],"force_p95":0.11135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14418,"mean_force":0.07638,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55109,0.00051,0.17555]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51845,-0.01392,0.21847]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53647,-0.0273,0.08945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5301.0,"contact_point_centroid":[0.53214,-0.00952,0.03779],"force_p95":0.07041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12093,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53106,-0.02857,0.03562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16926.0,"contact_point_centroid":[0.55343,0.01854,0.17597],"force_p95":0.0879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1102,"mean_force":0.05636,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55089,4e-05,0.17526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4172.0,"contact_point_centroid":[0.53176,-0.04786,0.03843],"force_p95":0.08121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08645,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53106,-0.02857,0.03562]}],"total_contact_groups":12},"final_pose_error":0.09109,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.59463,0.08743,0.15369],"final_tcp_position":[0.58923,0.0851,0.185],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.53368,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53568,-0.02535,0.15474],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12916,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53964,-0.02879,0.0458],"tcp_start":[0.53568,-0.02535,0.15474],"tcp_to_object_dist_end":0.02066,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02902,0.02579],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26093,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1393,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.16596,"tcp_end":[0.53103,-0.02856,0.03558],"tcp_start":[0.53964,-0.02879,0.0458],"tcp_to_object_dist_end":0.01748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":721.0,"n_steps_budget":750.0,"object_pos_end":[0.55326,-0.02958,0.14425],"object_pos_start":[0.54551,-0.02902,0.02579],"object_to_goal_dist_end":0.21268,"object_to_goal_dist_start":0.26093,"object_z_max":0.14411,"peak_contact_force":0.10971,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27727.0,"raw_peak_contact_force":0.53368,"subtask_id":"lift_object","tcp_end":[0.5408,-0.02887,0.16123],"tcp_start":[0.53103,-0.02856,0.03558],"tcp_to_object_dist_end":0.02107,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57166,0.02931,0.16989],"object_pos_start":[0.55326,-0.02958,0.14425],"object_to_goal_dist_end":0.14895,"object_to_goal_dist_start":0.21268,"object_z_max":0.16987,"peak_contact_force":0.09193,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29838.0,"raw_peak_contact_force":0.14418,"subtask_id":"place_at_goal","tcp_end":[0.56436,0.02839,0.19453],"tcp_start":[0.5408,-0.02887,0.16123],"tcp_to_object_dist_end":0.02571,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59463,0.08743,0.15369],"object_pos_start":[0.57166,0.02931,0.16989],"object_to_goal_dist_end":0.08948,"object_to_goal_dist_start":0.14895,"object_z_max":0.16989,"peak_contact_force":0.16482,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26226.0,"raw_peak_contact_force":0.20814,"subtask_id":"place_at_goal","tcp_end":[0.58923,0.0851,0.185],"tcp_start":[0.56436,0.02839,0.19453],"tcp_to_object_dist_end":0.03186,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51316,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13111,"approach_object.approach_speed":0.05402,"approach_object.phase_max_time_approach":4.31072,"descend_to_grasp.descend_depth":0.00679,"descend_to_grasp.phase_max_time_descend":10.23129,"descend_to_place.phase_max_time_place":9.91232,"descend_to_place.place_height_z":0.02428,"descend_to_place.place_speed":0.06083,"lift.lift_height":0.15264,"lift.lift_speed":0.10558,"lift.phase_max_time_lift":9.46422,"transport_to_goal.phase_max_time_transport":14.76369,"transport_to_goal.transport_speed":0.14428},"optimized_scores":{"best_composite_score":0.02215,"best_fitness_score":0.79215,"best_task_score":0.62569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":293.0,"contact_point_centroid":[0.45964,-0.00037,-0.00143],"force_p95":0.3417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68274,"mean_force":0.12326,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44771,-0.00032,0.02656]},{"body_a":"grasp_target","body_b":"hand","contact_count":130.0,"contact_point_centroid":[0.47838,0.01964,0.05992],"force_p95":0.07583,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35928,"mean_force":0.05144,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44718,-0.00034,0.02935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17937.0,"contact_point_centroid":[0.45234,0.0188,0.09139],"force_p95":0.07533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27823,"mean_force":0.05143,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45148,-0.00035,0.08924]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18294.0,"contact_point_centroid":[0.45239,-0.01948,0.09303],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27621,"mean_force":0.05039,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45161,-0.00035,0.09086]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-0.00015,-0.00202],"force_p95":0.12943,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14471,"mean_force":0.12466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45098,-0.00027,0.02682]},{"body_a":"world","body_b":"grasp_target","contact_count":2536.0,"contact_point_centroid":[0.46286,-7e-05,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48019,-6e-05,0.23289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20284.0,"contact_point_centroid":[0.49431,0.01849,0.18209],"force_p95":0.07009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1292,"mean_force":0.04856,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49279,0.03757,0.18024]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19746.0,"contact_point_centroid":[0.49213,0.05685,0.18273],"force_p95":0.0726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12274,"mean_force":0.04952,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.493,0.03777,0.18034]},{"body_a":"world","body_b":"grasp_target","contact_count":3012.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45826,-0.00015,0.09522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.54963,0.07522,0.18129],"force_p95":0.06957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12173,"mean_force":0.04872,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54663,0.09418,0.18005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.544,0.11305,0.1826],"force_p95":0.06905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1202,"mean_force":0.04805,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54663,0.09418,0.18005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.45083,-0.0195,0.02775],"force_p95":0.06674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.087,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44979,-0.00028,0.02568]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.45053,0.01893,0.02742],"force_p95":0.06491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08388,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44979,-0.00028,0.02569]},{"body_a":"grasp_target","body_b":"hand","contact_count":232.0,"contact_point_centroid":[0.48086,0.01966,0.05597],"force_p95":0.00217,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.00393,"mean_force":0.00142,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44978,-0.00028,0.02568]}],"total_contact_groups":14},"final_pose_error":0.06738,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.56267,0.11067,0.15239],"final_tcp_position":[0.56291,0.11009,0.16835],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.68274,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2536.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46172,-0.00011,0.16596],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13994,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3012.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45789,-0.00015,0.03338],"tcp_start":[0.46172,-0.00011,0.16596],"tcp_to_object_dist_end":0.00888,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-0.0003,0.0259],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12879,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12007.0,"raw_peak_contact_force":0.14471,"tcp_end":[0.44976,-0.00029,0.02566],"tcp_start":[0.45789,-0.00015,0.03338],"tcp_to_object_dist_end":0.01296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":901.0,"n_steps_budget":930.0,"object_pos_end":[0.47042,-0.00034,0.15941],"object_pos_start":[0.46271,-0.0003,0.0259],"object_to_goal_dist_end":0.21068,"object_to_goal_dist_start":0.23338,"object_z_max":0.15929,"peak_contact_force":0.08072,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36654.0,"raw_peak_contact_force":0.68274,"subtask_id":"lift_object","tcp_end":[0.45848,-0.00034,0.1668],"tcp_start":[0.44976,-0.00029,0.02566],"tcp_to_object_dist_end":0.01404,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53433,0.0775,0.18674],"object_pos_start":[0.47042,-0.00034,0.15941],"object_to_goal_dist_end":0.12488,"object_to_goal_dist_start":0.21068,"object_z_max":0.18671,"peak_contact_force":0.06942,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40030.0,"raw_peak_contact_force":0.1292,"subtask_id":"place_at_goal","tcp_end":[0.53187,0.07693,0.1987],"tcp_start":[0.45848,-0.00034,0.1668],"tcp_to_object_dist_end":0.01223,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56267,0.11067,0.15239],"object_pos_start":[0.53433,0.0775,0.18674],"object_to_goal_dist_end":0.07034,"object_to_goal_dist_start":0.12488,"object_z_max":0.18674,"peak_contact_force":0.06986,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.12173,"subtask_id":"place_at_goal","tcp_end":[0.56291,0.11009,0.16835],"tcp_start":[0.53187,0.07693,0.1987],"tcp_to_object_dist_end":0.01597,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```