## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2314 | 0.24 | ❌ rejected |
| 4 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1488 | 0.19 | ❌ rejected |
| 3 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1969 | 0.28 | ❌ rejected |
| 2 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2195 | 0.23 | ❌ rejected |
| 1 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2558 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.231) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place
  weight: 0.5
phases:
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_grasp
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
  guards:
  - id: bilateral_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_clear
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
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
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.231
- **task_score** (E): 0.242
- **fitness_score**: 0.601  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2693 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.0991 |
| transport_1 | 0.00 | 1.00 | 0.0000 |
| descend_2 | 0.00 | 0.33 | 0.1088 |
| release_1 | 1.00 | 1.00 | 0.0239 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.035) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.511, -0.001, 0.030)→(0.511, -0.001, 0.030) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 45.333 | 0.166 | 0.255 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.030)→(0.507, -0.001, 0.129) | (0.522, -0.001, 0.025)→(0.522, -0.001, 0.118) | 0.290→0.244 | 1.00 / 27.333 | 0.106 | 0.678 |
| transport_1 | approach | 0.00 / guard_failure | (0.507, -0.001, 0.129)→(0.507, -0.001, 0.129) | (0.522, -0.001, 0.118)→(0.522, -0.001, 0.118) | 0.244→0.244 | 1.00 / 28.667 | 0.137 | 0.142 |
| descend_2 | descend | 0.00 / step_budget | (0.507, -0.001, 0.129)→(0.550, 0.094, 0.155) | (0.522, -0.001, 0.118)→(0.554, 0.104, 0.079) | 0.244→0.179 | 0.33 / 2.667 | 0.041 | 0.650 |
| release_1 | release | 1.00 / step_budget | (0.550, 0.094, 0.155)→(0.544, 0.093, 0.178) | (0.554, 0.104, 0.079)→(0.562, 0.117, 0.016) | 0.179→0.215 | 1.00 / 4.000 | 0.123 | 1.001 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.301
- phase_score: 0.400
- phase_breakdown.pre_grasp_score: 0.777
- phase_breakdown.lift_clear_score: 0.657
- phase_breakdown.place_score: 0.096
- grasp_place_fitness: 0.627

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.627
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.301
- **Median Q (composite search score)**: 0.219
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.246


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86111,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.01084,"descend_2.place_z_offset":0.00586,"lift_1.lift_height":0.10281,"transport_1.approach_height":0.17386,"transport_1.transport_speed":0.01908},"optimized_scores":{"best_composite_score":0.21802,"best_fitness_score":0.58802,"best_task_score":0.20357},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":513.0,"contact_point_centroid":[0.51601,0.1465,-0.00371],"force_p95":0.87769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48868,"mean_force":0.21624,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.51377,0.1222,0.16011]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.47925,0.04353,-0.00142],"force_p95":0.60026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8144,"mean_force":0.10144,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47272,0.04536,0.02516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10931.0,"contact_point_centroid":[0.47089,0.06428,0.06798],"force_p95":0.08312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33919,"mean_force":0.05459,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47032,0.04514,0.06593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11072.0,"contact_point_centroid":[0.47092,0.02605,0.06948],"force_p95":0.08243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29991,"mean_force":0.05292,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47032,0.04514,0.06742]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48283,0.04796,-0.00239],"force_p95":0.21163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29859,"mean_force":0.15106,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47475,0.04558,0.02338]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9894.0,"contact_point_centroid":[0.49053,0.05959,0.13113],"force_p95":0.13394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27724,"mean_force":0.07928,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.48692,0.07805,0.13169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9463.0,"contact_point_centroid":[0.49159,0.09772,0.13205],"force_p95":0.13808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27261,"mean_force":0.08614,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.48758,0.07915,0.13239]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5658.0,"contact_point_centroid":[0.47449,0.02635,0.02489],"force_p95":0.08083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15717,"mean_force":0.04551,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47432,0.04553,0.02294]},{"body_a":"world","body_b":"grasp_target","contact_count":3388.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48844,0.02292,0.16226]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51598,0.14719,-0.00199],"force_p95":0.12319,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12374,"mean_force":0.12265,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51246,0.12567,0.16628]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":28.0,"contact_point_centroid":[0.47306,0.06422,0.11598],"force_p95":0.10274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12196,"mean_force":0.07462,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47032,0.04515,0.11436]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.47238,0.02633,0.11515],"force_p95":0.08742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09175,"mean_force":0.05994,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47032,0.04515,0.11436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6192.0,"contact_point_centroid":[0.47447,0.06498,0.02485],"force_p95":0.08165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08787,"mean_force":0.04537,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47433,0.04553,0.02295]},{"body_a":"left_finger","body_b":"right_finger","contact_count":287.0,"contact_point_centroid":[0.51532,0.12432,0.16364],"force_p95":0.01512,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01161,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.51506,0.1243,0.16147]},{"body_a":"left_finger","body_b":"right_finger","contact_count":215.0,"contact_point_centroid":[0.51523,0.12638,0.16316],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01106,"mean_force":0.01034,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51508,0.12636,0.16086]}],"total_contact_groups":15},"final_pose_error":0.14195,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51598,0.14719,0.01602],"final_tcp_position":[0.51639,0.12653,0.16291],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.48868,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3388.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47912,0.04596,0.02789],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48258,0.04563,0.02487],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29276,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19295,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13654.0,"raw_peak_contact_force":0.29859,"tcp_end":[0.47431,0.04552,0.02292],"tcp_start":[0.47431,0.04553,0.02292],"tcp_to_object_dist_end":0.0085,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.48612,0.04539,0.11032],"object_pos_start":[0.48257,0.04562,0.02492],"object_to_goal_dist_end":0.23931,"object_to_goal_dist_start":0.29273,"object_z_max":0.11022,"peak_contact_force":0.09626,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22152.0,"raw_peak_contact_force":0.8144,"subtask_id":"lift_clear","tcp_end":[0.4703,0.04515,0.11433],"tcp_start":[0.47431,0.04552,0.02292],"tcp_to_object_dist_end":0.01632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.48621,0.04539,0.11035],"object_pos_start":[0.48612,0.04539,0.11032],"object_to_goal_dist_end":0.23925,"object_to_goal_dist_start":0.23931,"object_z_max":0.11035,"peak_contact_force":0.12196,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":64.0,"raw_peak_contact_force":0.12196,"tcp_end":[0.47038,0.04516,0.11443],"tcp_start":[0.47035,0.04515,0.1144],"tcp_to_object_dist_end":0.01635,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51602,0.14725,0.016],"object_pos_start":[0.48624,0.0454,0.11033],"object_to_goal_dist_end":0.23874,"object_to_goal_dist_start":0.23925,"object_z_max":0.13039,"peak_contact_force":0.12375,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20157.0,"raw_peak_contact_force":1.48868,"subtask_id":"place","tcp_end":[0.51639,0.12653,0.16291],"tcp_start":[0.47038,0.04516,0.11443],"tcp_to_object_dist_end":0.14837,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51598,0.14719,0.01602],"object_pos_start":[0.51602,0.14725,0.016],"object_to_goal_dist_end":0.23876,"object_to_goal_dist_start":0.23874,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1015.0,"raw_peak_contact_force":0.12374,"tcp_end":[0.51091,0.12526,0.18704],"tcp_start":[0.51639,0.12653,0.16291],"tcp_to_object_dist_end":0.17249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86239,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00082,"descend_2.place_z_offset":-0.01396,"lift_1.lift_height":0.11514,"transport_1.approach_height":0.19999,"transport_1.transport_speed":0.04746},"optimized_scores":{"best_composite_score":0.21921,"best_fitness_score":0.58921,"best_task_score":0.22077},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":573.0,"contact_point_centroid":[0.57356,0.11135,-0.00364],"force_p95":0.90792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46976,"mean_force":0.20418,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55105,0.08764,0.1584]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.53409,-0.0195,-0.00119],"force_p95":0.43799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62554,"mean_force":0.08749,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52359,-0.02009,0.03374]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11644.0,"contact_point_centroid":[0.52256,-0.03899,0.07864],"force_p95":0.09973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30862,"mean_force":0.05927,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52099,-0.02004,0.07704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11140.0,"contact_point_centroid":[0.52263,-0.00107,0.08094],"force_p95":0.0982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30852,"mean_force":0.06101,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52099,-0.02003,0.079]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10869.0,"contact_point_centroid":[0.53978,0.01252,0.14073],"force_p95":0.15037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22634,"mean_force":0.08366,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53574,0.03108,0.14107]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53707,-0.02107,-0.00213],"force_p95":0.15375,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22617,"mean_force":0.13244,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52576,-0.02014,0.0325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11786.0,"contact_point_centroid":[0.54096,0.05134,0.14092],"force_p95":0.1287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17385,"mean_force":0.0775,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53641,0.03297,0.14147]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":27.0,"contact_point_centroid":[0.52491,-0.00144,0.13591],"force_p95":0.13257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14451,"mean_force":0.0835,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52116,-0.02003,0.13479]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":29.0,"contact_point_centroid":[0.52506,-0.03867,0.13603],"force_p95":0.12879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14265,"mean_force":0.0803,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52116,-0.02003,0.13478]},{"body_a":"world","body_b":"grasp_target","contact_count":3360.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12668,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51412,-0.01008,0.16735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5803.0,"contact_point_centroid":[0.52525,-0.00092,0.03428],"force_p95":0.06985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11004,"mean_force":0.04511,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52528,-0.02013,0.03196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6273.0,"contact_point_centroid":[0.5251,-0.03937,0.03381],"force_p95":0.06881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07646,"mean_force":0.04317,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52529,-0.02013,0.03196]}],"total_contact_groups":12},"final_pose_error":0.15462,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5738,0.11211,0.016],"final_tcp_position":[0.55636,0.08839,0.15379],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.46976,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":841.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3360.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53041,-0.0202,0.03796],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02029,0.02561],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31617,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14779,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13880.0,"raw_peak_contact_force":0.22617,"tcp_end":[0.52526,-0.02012,0.03193],"tcp_start":[0.52526,-0.02012,0.03193],"tcp_to_object_dist_end":0.01328,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53645,-0.02012,0.12116],"object_pos_start":[0.53694,-0.02027,0.02563],"object_to_goal_dist_end":0.27265,"object_to_goal_dist_start":0.31614,"object_z_max":0.12105,"peak_contact_force":0.11003,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22935.0,"raw_peak_contact_force":0.62554,"subtask_id":"lift_clear","tcp_end":[0.52113,-0.02003,0.13475],"tcp_start":[0.52526,-0.02012,0.03193],"tcp_to_object_dist_end":0.02048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.53652,-0.02012,0.12119],"object_pos_start":[0.53645,-0.02012,0.12116],"object_to_goal_dist_end":0.27262,"object_to_goal_dist_start":0.27265,"object_z_max":0.12119,"peak_contact_force":0.14265,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":56.0,"raw_peak_contact_force":0.14451,"tcp_end":[0.52117,-0.02003,0.13484],"tcp_start":[0.52119,-0.02003,0.13482],"tcp_to_object_dist_end":0.02054,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56354,0.09249,0.11177],"object_pos_start":[0.53654,-0.02012,0.12117],"object_to_goal_dist_end":0.17213,"object_to_goal_dist_start":0.27261,"object_z_max":0.12737,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22655.0,"raw_peak_contact_force":0.22634,"subtask_id":"place","tcp_end":[0.55636,0.08839,0.15379],"tcp_start":[0.52117,-0.02003,0.13484],"tcp_to_object_dist_end":0.04283,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5738,0.11211,0.016],"object_pos_start":[0.56354,0.09249,0.11177],"object_to_goal_dist_end":0.2266,"object_to_goal_dist_start":0.17213,"object_z_max":0.11177,"peak_contact_force":0.12333,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":573.0,"raw_peak_contact_force":1.46976,"tcp_end":[0.55043,0.08753,0.17676],"tcp_start":[0.55636,0.08839,0.15379],"tcp_to_object_dist_end":0.16429,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85981,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00357,"descend_2.place_z_offset":-0.00399,"lift_1.lift_height":0.11541,"transport_1.approach_height":0.14091,"transport_1.transport_speed":0.02744},"optimized_scores":{"best_composite_score":0.2569,"best_fitness_score":0.6269,"best_task_score":0.30125},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":562.0,"contact_point_centroid":[0.59637,0.0922,-0.00354],"force_p95":0.88665,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40856,"mean_force":0.20275,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57042,0.06606,0.15173]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.54259,-0.02704,-0.00126],"force_p95":0.3974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5953,"mean_force":0.0879,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53161,-0.0275,0.03593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11495.0,"contact_point_centroid":[0.5308,-0.04634,0.08054],"force_p95":0.10022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31517,"mean_force":0.06005,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52904,-0.02741,0.079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10874.0,"contact_point_centroid":[0.53086,-0.00845,0.08274],"force_p95":0.10015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30628,"mean_force":0.06227,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52904,-0.02741,0.08078]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54568,-0.02896,-0.00219],"force_p95":0.16617,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24019,"mean_force":0.13624,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53384,-0.02758,0.03469]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10361.0,"contact_point_centroid":[0.55406,-0.00072,0.13905],"force_p95":0.15078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23512,"mean_force":0.08662,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54972,0.01782,0.13934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11473.0,"contact_point_centroid":[0.55544,0.03785,0.13903],"force_p95":0.12837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17588,"mean_force":0.07858,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55062,0.01951,0.13962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":23.0,"contact_point_centroid":[0.53426,-0.00881,0.13929],"force_p95":0.13638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15838,"mean_force":0.10009,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52922,-0.02741,0.13702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":25.0,"contact_point_centroid":[0.53432,-0.04603,0.13934],"force_p95":0.13902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14706,"mean_force":0.09335,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52922,-0.02741,0.13702]},{"body_a":"world","body_b":"grasp_target","contact_count":3396.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5182,-0.01383,0.16838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6082.0,"contact_point_centroid":[0.53306,-0.00831,0.03697],"force_p95":0.06952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11804,"mean_force":0.04316,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53336,-0.02755,0.03412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6624.0,"contact_point_centroid":[0.53293,-0.04685,0.03643],"force_p95":0.06973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07622,"mean_force":0.04127,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53336,-0.02755,0.03413]}],"total_contact_groups":12},"final_pose_error":0.11634,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.59661,0.09294,0.016],"final_tcp_position":[0.57597,0.06669,0.14748],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.40856,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3396.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53852,-0.02768,0.04031],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.02787,0.02545],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26026,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15814,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14510.0,"raw_peak_contact_force":0.24019,"tcp_end":[0.53334,-0.02755,0.0341],"tcp_start":[0.53334,-0.02755,0.0341],"tcp_to_object_dist_end":0.01496,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.54382,-0.02752,0.12117],"object_pos_start":[0.54554,-0.02784,0.02548],"object_to_goal_dist_end":0.21924,"object_to_goal_dist_start":0.26022,"object_z_max":0.12107,"peak_contact_force":0.11194,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22524.0,"raw_peak_contact_force":0.5953,"subtask_id":"lift_clear","tcp_end":[0.52919,-0.02741,0.13698],"tcp_start":[0.53334,-0.02755,0.0341],"tcp_to_object_dist_end":0.02154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.54389,-0.02751,0.12121],"object_pos_start":[0.54382,-0.02752,0.12117],"object_to_goal_dist_end":0.2192,"object_to_goal_dist_start":0.21924,"object_z_max":0.12121,"peak_contact_force":0.14706,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":48.0,"raw_peak_contact_force":0.15838,"tcp_end":[0.52924,-0.02741,0.13708],"tcp_start":[0.52925,-0.02741,0.13706],"tcp_to_object_dist_end":0.0216,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58312,0.07109,0.10991],"object_pos_start":[0.54391,-0.0275,0.12119],"object_to_goal_dist_end":0.12557,"object_to_goal_dist_start":0.21919,"object_z_max":0.12119,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21834.0,"raw_peak_contact_force":0.23512,"subtask_id":"place","tcp_end":[0.57597,0.06669,0.14748],"tcp_start":[0.52924,-0.02741,0.13708],"tcp_to_object_dist_end":0.03849,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59661,0.09294,0.016],"object_pos_start":[0.58312,0.07109,0.10991],"object_to_goal_dist_end":0.17997,"object_to_goal_dist_start":0.12557,"object_z_max":0.10991,"peak_contact_force":0.1234,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":562.0,"raw_peak_contact_force":1.40856,"tcp_end":[0.56981,0.06597,0.16982],"tcp_start":[0.57597,0.06669,0.14748],"tcp_to_object_dist_end":0.15845,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```