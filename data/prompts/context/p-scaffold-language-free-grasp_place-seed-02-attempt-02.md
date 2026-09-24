## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1736 | 0.39 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1339 | 0.31 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3008 | 0.15 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=0.174) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: lift_height
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.21
  weight: 0.3
- id: place_target
  target_entity: object
  weight: 0.7
phases:
- id: approach_1
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
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp_1
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
    orientation:
      mode: keep_current
- id: lift_1
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
    - 0.0
    offset_along_axis:
      distance: 0.21
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.21
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_height
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_2
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_target
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.21, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.174
- **task_score** (E): 0.388
- **fitness_score**: 0.674  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1581 |
| descend_1 | 1.00 | 1.00 | 0.1135 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1450 |
| transport_1 | 1.00 | 1.00 | 0.2362 |
| descend_2 | 1.00 | 1.00 | 0.0353 |
| release_1 | 1.00 | 1.00 | 0.0198 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.148) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.490, -0.014, 0.148)→(0.488, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.333 | 0.134 | 0.180 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.477, -0.015, 0.171) | (0.493, -0.015, 0.026)→(0.491, -0.015, 0.165) | 0.281→0.241 | 1.00 / 34.000 | 0.087 | 0.680 |
| transport_1 | approach | 1.00 / step_budget | (0.477, -0.015, 0.171)→(0.625, 0.164, 0.204) | (0.491, -0.015, 0.165)→(0.631, 0.164, 0.186) | 0.241→0.025 | 1.00 / 29.667 | 0.222 | 0.169 |
| descend_2 | descend | 1.00 / step_budget | (0.625, 0.164, 0.204)→(0.629, 0.170, 0.170) | (0.631, 0.164, 0.186)→(0.636, 0.171, 0.150) | 0.025→0.017 | 1.00 / 25.333 | 59237.372 | 0.226 |
| release_1 | release | 1.00 / step_budget | (0.629, 0.170, 0.170)→(0.623, 0.169, 0.189) | (0.636, 0.171, 0.150)→(0.640, 0.173, 0.018) | 0.017→0.148 | 1.00 / 3.333 | 0.111 | 1.565 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.546
- phase_score: 0.631
- phase_breakdown.place_target_score: 0.821
- phase_breakdown.lift_height_score: 0.189
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.546
- **Median Q (composite search score)**: 0.134
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.435


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00373,"average_solve_count":268.0,"average_success_count":268.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07214,"approach_1.speed":0.08533,"descend_1.speed":0.01953,"descend_2.speed":0.13511,"lift_1.lift_distance":0.16231,"lift_1.speed":0.05896,"transport_1.speed":0.09909},"optimized_scores":{"best_composite_score":0.13419,"best_fitness_score":0.63419,"best_task_score":0.30828},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":199.0,"contact_point_centroid":[0.63136,0.1512,-0.00709],"force_p95":1.27242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77448,"mean_force":0.38269,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61878,0.1533,0.20662]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.47321,-0.01931,-0.00139],"force_p95":0.56775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65678,"mean_force":0.18872,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46261,-0.0196,0.02805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8955.0,"contact_point_centroid":[0.46036,-0.00038,0.09812],"force_p95":0.07801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29528,"mean_force":0.05447,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46016,-0.01953,0.09558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9378.0,"contact_point_centroid":[0.46031,-0.03864,0.0969],"force_p95":0.07632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29316,"mean_force":0.05256,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46016,-0.01953,0.09475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":830.0,"contact_point_centroid":[0.62466,0.13536,0.19173],"force_p95":0.09886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2553,"mean_force":0.06328,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6224,0.15445,0.19079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.62535,0.17326,0.19127],"force_p95":0.08261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24617,"mean_force":0.05173,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62243,0.15446,0.19085]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00204],"force_p95":0.13672,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18616,"mean_force":0.12651,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46475,-0.01965,0.02796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1391.0,"contact_point_centroid":[0.62342,0.1327,0.21281],"force_p95":0.09923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18607,"mean_force":0.07417,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62126,0.15164,0.2121]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1807.0,"contact_point_centroid":[0.6242,0.17044,0.21273],"force_p95":0.08393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17824,"mean_force":0.05982,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62124,0.15163,0.21216]},{"body_a":"world","body_b":"grasp_target","contact_count":2304.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48628,-0.00911,0.2058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12778.0,"contact_point_centroid":[0.53981,0.04543,0.19835],"force_p95":0.0879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13403,"mean_force":0.05957,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53806,0.06442,0.19681]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12725.0,"contact_point_centroid":[0.53875,0.08236,0.19801],"force_p95":0.0875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12645,"mean_force":0.0595,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53704,0.06338,0.19639]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47135,-0.01913,0.07325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.46345,-0.00038,0.02987],"force_p95":0.06657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09293,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46363,-0.01962,0.02686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.46332,-0.03888,0.02935],"force_p95":0.0649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.088,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46363,-0.01962,0.02687]}],"total_contact_groups":15},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63356,0.15191,0.01367],"final_tcp_position":[0.62428,0.15484,0.19521],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2304.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47409,-0.01858,0.11164],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47139,-0.0198,0.03456],"tcp_start":[0.47409,-0.01858,0.11164],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01965,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1347,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12265.0,"raw_peak_contact_force":0.18616,"tcp_end":[0.4636,-0.01962,0.02684],"tcp_start":[0.47139,-0.0198,0.03456],"tcp_to_object_dist_end":0.01247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.47222,-0.01949,0.16431],"object_pos_start":[0.47603,-0.01965,0.02583],"object_to_goal_dist_end":0.24069,"object_to_goal_dist_start":0.28825,"object_z_max":0.16403,"peak_contact_force":0.07992,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18411.0,"raw_peak_contact_force":0.65678,"subtask_id":"lift_height","tcp_end":[0.46017,-0.01951,0.1695],"tcp_start":[0.4636,-0.01962,0.02684],"tcp_to_object_dist_end":0.01312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":741.0,"n_steps_budget":1000.0,"object_pos_end":[0.62927,0.14886,0.2135],"object_pos_start":[0.47222,-0.01949,0.16431],"object_to_goal_dist_end":0.02575,"object_to_goal_dist_start":0.24069,"object_z_max":0.21346,"peak_contact_force":0.43157,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25503.0,"raw_peak_contact_force":0.13403,"tcp_end":[0.61946,0.14882,0.22812],"tcp_start":[0.46017,-0.01951,0.1695],"tcp_to_object_dist_end":0.01761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.63467,0.15462,0.17947],"object_pos_start":[0.62927,0.14886,0.2135],"object_to_goal_dist_end":0.01194,"object_to_goal_dist_start":0.02575,"object_z_max":0.2135,"peak_contact_force":167951.73011,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3198.0,"raw_peak_contact_force":0.18607,"subtask_id":"place_target","tcp_end":[0.62428,0.15484,0.19521],"tcp_start":[0.61946,0.14882,0.22812],"tcp_to_object_dist_end":0.01885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63356,0.15191,0.01367],"object_pos_start":[0.63467,0.15462,0.17947],"object_to_goal_dist_end":0.17651,"object_to_goal_dist_start":0.01194,"object_z_max":0.17947,"peak_contact_force":0.07968,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2093.0,"raw_peak_contact_force":1.77448,"tcp_end":[0.61874,0.15329,0.2143],"tcp_start":[0.62428,0.15484,0.19521],"tcp_to_object_dist_end":0.20118,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05965,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12625,"approach_1.speed":0.08248,"descend_1.speed":0.01613,"descend_2.speed":0.10585,"lift_1.lift_distance":0.15008,"lift_1.speed":0.0552,"transport_1.speed":0.12327},"optimized_scores":{"best_composite_score":0.25422,"best_fitness_score":0.75422,"best_task_score":0.54648},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.61223,0.20035,-0.00652],"force_p95":0.93193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98198,"mean_force":0.37969,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61555,0.20083,0.12399]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.45564,-0.02539,-0.0014],"force_p95":0.55186,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63471,"mean_force":0.18422,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44579,-0.02559,0.02896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9038.0,"contact_point_centroid":[0.44303,-0.04464,0.09256],"force_p95":0.07211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28644,"mean_force":0.04931,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44341,-0.02548,0.09096]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8596.0,"contact_point_centroid":[0.4431,-0.00628,0.09118],"force_p95":0.07511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28431,"mean_force":0.05116,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44342,-0.02548,0.08916]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1342.0,"contact_point_centroid":[0.61993,0.22166,0.11563],"force_p95":0.07067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27776,"mean_force":0.04074,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62021,0.20256,0.11345]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1110.0,"contact_point_centroid":[0.61906,0.18325,0.11544],"force_p95":0.07936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23802,"mean_force":0.04766,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62019,0.20256,0.11342]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00206],"force_p95":0.14003,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19267,"mean_force":0.12738,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44785,-0.02566,0.02881]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2794.0,"contact_point_centroid":[0.61883,0.21819,0.13873],"force_p95":0.07059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17383,"mean_force":0.04656,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61916,0.19913,0.13649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2286.0,"contact_point_centroid":[0.61832,0.17991,0.13845],"force_p95":0.07894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15961,"mean_force":0.05503,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61916,0.19913,0.13649]},{"body_a":"world","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47935,-0.01139,0.23337]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45543,-0.02465,0.10011]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13824.0,"contact_point_centroid":[0.53305,0.07016,0.15764],"force_p95":0.08123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12168,"mean_force":0.05716,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5325,0.08939,0.15525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16812.0,"contact_point_centroid":[0.53285,0.10864,0.1569],"force_p95":0.07438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1153,"mean_force":0.04785,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53272,0.08968,0.15524]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.44678,-0.00641,0.03014],"force_p95":0.06807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09781,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44677,-0.02562,0.02779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44663,-0.04486,0.02964],"force_p95":0.06687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08234,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44677,-0.02562,0.02779]}],"total_contact_groups":15},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63175,0.19992,0.02388],"final_tcp_position":[0.62241,0.20318,0.11772],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.98198,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1688.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.45936,-0.02358,0.16575],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45434,-0.02589,0.03499],"tcp_start":[0.45936,-0.02358,0.16575],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02566,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13729,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11788.0,"raw_peak_contact_force":0.19267,"tcp_end":[0.44674,-0.02562,0.02776],"tcp_start":[0.45434,-0.02589,0.03499],"tcp_to_object_dist_end":0.01187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.45454,-0.02538,0.153],"object_pos_start":[0.45844,-0.02566,0.02579],"object_to_goal_dist_end":0.29481,"object_to_goal_dist_start":0.30328,"object_z_max":0.15271,"peak_contact_force":0.07868,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17712.0,"raw_peak_contact_force":0.63471,"subtask_id":"lift_height","tcp_end":[0.44339,-0.02546,0.15814],"tcp_start":[0.44674,-0.02562,0.02776],"tcp_to_object_dist_end":0.01228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":792.0,"n_steps_budget":1000.0,"object_pos_end":[0.61903,0.1954,0.13952],"object_pos_start":[0.45454,-0.02538,0.153],"object_to_goal_dist_end":0.03054,"object_to_goal_dist_start":0.29481,"object_z_max":0.15333,"peak_contact_force":0.07756,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30636.0,"raw_peak_contact_force":0.12168,"tcp_end":[0.61755,0.19557,0.1556],"tcp_start":[0.44339,-0.02546,0.15814],"tcp_to_object_dist_end":0.01615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.62474,0.20315,0.10112],"object_pos_start":[0.61903,0.1954,0.13952],"object_to_goal_dist_end":0.01496,"object_to_goal_dist_start":0.03054,"object_z_max":0.13952,"peak_contact_force":0.07869,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5080.0,"raw_peak_contact_force":0.17383,"subtask_id":"place_target","tcp_end":[0.62241,0.20318,0.11772],"tcp_start":[0.61755,0.19557,0.1556],"tcp_to_object_dist_end":0.01677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63175,0.19992,0.02388],"object_pos_start":[0.62474,0.20315,0.10112],"object_to_goal_dist_end":0.09064,"object_to_goal_dist_start":0.01496,"object_z_max":0.10112,"peak_contact_force":0.12962,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2626.0,"raw_peak_contact_force":0.98198,"tcp_end":[0.61541,0.20077,0.13657],"tcp_start":[0.62241,0.20318,0.11772],"tcp_to_object_dist_end":0.11387,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8354,"average_solve_count":322.0,"average_success_count":322.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13013,"approach_1.speed":0.01261,"descend_1.speed":0.02753,"descend_2.speed":0.14092,"lift_1.lift_distance":0.18144,"lift_1.speed":0.06609,"transport_1.speed":0.19939},"optimized_scores":{"best_composite_score":0.13232,"best_fitness_score":0.63232,"best_task_score":0.3105},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":505.0,"contact_point_centroid":[0.65337,0.16756,-0.00415],"force_p95":0.841,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93958,"mean_force":0.21288,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63555,0.15195,0.19817]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.54086,0.00071,-0.00139],"force_p95":0.60396,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74998,"mean_force":0.19429,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52869,0.00084,0.02503]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9248.0,"contact_point_centroid":[0.52807,-0.01812,0.10066],"force_p95":0.10415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33357,"mean_force":0.06483,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52586,0.0008,0.09911]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9449.0,"contact_point_centroid":[0.528,0.01973,0.0977],"force_p95":0.10466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3217,"mean_force":0.06381,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52589,0.0008,0.09599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":762.0,"contact_point_centroid":[0.64313,0.16759,0.2104],"force_p95":0.17635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31661,"mean_force":0.1155,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63814,0.14983,0.2139]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":47.0,"contact_point_centroid":[0.64586,0.16787,0.19028],"force_p95":0.17358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31364,"mean_force":0.06143,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64045,0.15338,0.19551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.64255,0.13166,0.21077],"force_p95":0.2091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27906,"mean_force":0.14671,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63795,0.14959,0.2151]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5819.0,"contact_point_centroid":[0.58279,0.05297,0.2043],"force_p95":0.14123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25063,"mean_force":0.0881,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5788,0.07169,0.20458]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6650.0,"contact_point_centroid":[0.58507,0.09192,0.20563],"force_p95":0.1109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23959,"mean_force":0.07743,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58016,0.0735,0.20511]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.1317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16001,"mean_force":0.12529,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53114,0.00089,0.02536]},{"body_a":"world","body_b":"grasp_target","contact_count":2092.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51676,0.00047,0.23284]},{"body_a":"world","body_b":"grasp_target","contact_count":1824.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53601,0.00098,0.09971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53089,-0.01833,0.02662],"force_p95":0.07603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11026,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52989,0.00087,0.02393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53083,0.01994,0.02574],"force_p95":0.06803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09655,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52989,0.00087,0.02393]}],"total_contact_groups":14},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65375,0.16734,0.01602],"final_tcp_position":[0.64079,0.15334,0.19644],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53656,0.00098,0.16645],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53858,0.00103,0.03397],"tcp_start":[0.53656,0.00098,0.16645],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12961,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16001,"tcp_end":[0.52986,0.00086,0.02389],"tcp_start":[0.53858,0.00103,0.03397],"tcp_to_object_dist_end":0.01443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.54491,0.00075,0.1788],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.1883,"object_to_goal_dist_start":0.25053,"object_z_max":0.17855,"peak_contact_force":0.10306,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18779.0,"raw_peak_contact_force":0.74998,"subtask_id":"lift_height","tcp_end":[0.52626,0.00081,0.1858],"tcp_start":[0.52986,0.00086,0.02389],"tcp_to_object_dist_end":0.01992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.64437,0.14718,0.20582],"object_pos_start":[0.54491,0.00075,0.1788],"object_to_goal_dist_end":0.0186,"object_to_goal_dist_start":0.1883,"object_z_max":0.20578,"peak_contact_force":0.15728,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12469.0,"raw_peak_contact_force":0.25063,"tcp_end":[0.63682,0.14693,0.22867],"tcp_start":[0.52626,0.00081,0.1858],"tcp_to_object_dist_end":0.02407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":102.0,"n_steps_budget":1000.0,"object_pos_end":[0.64849,0.15654,0.16808],"object_pos_start":[0.64437,0.14718,0.20582],"object_to_goal_dist_end":0.02309,"object_to_goal_dist_start":0.0186,"object_z_max":0.20582,"peak_contact_force":9760.30694,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1318.0,"raw_peak_contact_force":0.31661,"subtask_id":"place_target","tcp_end":[0.64079,0.15334,0.19644],"tcp_start":[0.63682,0.14693,0.22867],"tcp_to_object_dist_end":0.02956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.65375,0.16734,0.01602],"object_pos_start":[0.64849,0.15654,0.16808],"object_to_goal_dist_end":0.17543,"object_to_goal_dist_start":0.02309,"object_z_max":0.16808,"peak_contact_force":0.12406,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":552.0,"raw_peak_contact_force":1.93958,"tcp_end":[0.63527,0.15185,0.21484],"tcp_start":[0.64079,0.15334,0.19644],"tcp_to_object_dist_end":0.20027,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```