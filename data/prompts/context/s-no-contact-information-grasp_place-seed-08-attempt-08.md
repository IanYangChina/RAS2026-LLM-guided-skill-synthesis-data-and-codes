## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3284 | 0.56 | ✅ accepted |
| 7 | approach → descend → grasp → lift → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.2248 | 0.27 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1449 | 0.46 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1348 | 0.22 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1369 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.56 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.328) — your mutation base

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
  - 0.05
  weight: 0.3
- id: place_at_goal
  target_entity: object
  metric: goal_progress
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
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
    orientation:
      mode: keep_current
  subtask_id: reach_object
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: grasp_secured
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_retained
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
  subtask_id: place_at_goal
- id: place_1
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
    - -0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.06
      - -0.01
      default: -0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=grasp_secured, when=before_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_retained, when=before_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.328
- **task_score** (E): 0.560
- **fitness_score**: 0.748  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1588 |
| descend_1 | 1.00 | 0.0974 |
| grasp_1 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 0.0995 |
| transport_1 | 1.00 | 0.2672 |
| place_1 | 1.00 | 0.1059 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.050) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.050)→(0.508, -0.001, 0.041) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.041)→(0.504, -0.001, 0.140) | (0.522, -0.001, 0.026)→(0.520, -0.001, 0.121) | 0.289→0.243 |
| transport_1 | approach | 1.00 / step_budget | (0.504, -0.001, 0.140)→(0.601, 0.196, 0.289) | (0.520, -0.001, 0.121)→(0.592, 0.169, 0.188) | 0.243→0.102 |
| place_1 | descend | 1.00 / step_budget | (0.601, 0.196, 0.289)→(0.604, 0.204, 0.183) | (0.592, 0.169, 0.188)→(0.591, 0.173, 0.115) | 0.102→0.100 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.788
- phase_score: 0.399
- phase_breakdown.reach_object_score: 0.406
- phase_breakdown.place_at_goal_score: 0.396
- grasp_place_fitness: 0.868

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.868
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.788
- **Median Q (composite search score)**: 0.353
- **K-run variance**: 0.0118
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.461


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24506,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13862,"descend_1.descend_depth":0.01001,"lift_1.lift_height":0.11613,"place_1.place_offset_z":-0.02092,"place_1.place_speed":0.03773,"transport_1.transport_speed":0.02289},"optimized_scores":{"best_composite_score":0.44787,"best_fitness_score":0.86787,"best_task_score":0.78815},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.48002,0.04618,-0.00147],"force_p95":0.52786,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5834,"mean_force":0.12003,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46925,0.04656,0.03827]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5642.0,"contact_point_centroid":[0.46825,0.06538,0.08226],"force_p95":0.09888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31238,"mean_force":0.05858,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46704,0.04634,0.08036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5076.0,"contact_point_centroid":[0.46852,0.02724,0.08315],"force_p95":0.10224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27823,"mean_force":0.06299,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46706,0.04634,0.08074]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04851,-0.00218],"force_p95":0.17207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24513,"mean_force":0.13581,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47162,0.0468,0.03784]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1673.0,"contact_point_centroid":[0.58103,0.24042,0.26988],"force_p95":0.14912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24347,"mean_force":0.10954,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5758,0.22243,0.27325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1453.0,"contact_point_centroid":[0.58058,0.20423,0.27252],"force_p95":0.18257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22738,"mean_force":0.12412,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57575,0.22232,0.27497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12268.0,"contact_point_centroid":[0.52597,0.15462,0.22591],"force_p95":0.10541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14417,"mean_force":0.07642,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52106,0.13597,0.2248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12352.0,"contact_point_centroid":[0.52368,0.11452,0.22252],"force_p95":0.1087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14057,"mean_force":0.07622,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51924,0.13311,0.22177]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49069,0.0201,0.22533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5026.0,"contact_point_centroid":[0.47026,0.02744,0.03944],"force_p95":0.07128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13525,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47051,0.0467,0.03671]},{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47884,0.04444,0.09574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5563.0,"contact_point_centroid":[0.47008,0.06605,0.03883],"force_p95":0.07151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07581,"mean_force":0.04085,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47052,0.0467,0.03671]}],"total_contact_groups":12},"final_pose_error":0.0148,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5829,0.22549,0.19495],"final_tcp_position":[0.57774,0.22577,0.22344],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.48196,0.04166,0.14835],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12254,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.47831,0.04745,0.04475],"tcp_start":[0.48196,0.04166,0.14835],"tcp_to_object_dist_end":0.01928,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48265,0.04715,0.02538],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29142,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.47048,0.04669,0.03668],"tcp_start":[0.47831,0.04745,0.04475],"tcp_to_object_dist_end":0.01661,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":299.0,"n_steps_budget":750.0,"object_pos_end":[0.48326,0.04676,0.11909],"object_pos_start":[0.48265,0.04715,0.02538],"object_to_goal_dist_end":0.23514,"object_to_goal_dist_start":0.29142,"object_z_max":0.11881,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.46682,0.04632,0.13334],"tcp_start":[0.47048,0.04669,0.03668],"tcp_to_object_dist_end":0.02176,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.58256,0.22013,0.28891],"object_pos_start":[0.48326,0.04676,0.11909],"object_to_goal_dist_end":0.05908,"object_to_goal_dist_start":0.23514,"object_z_max":0.28876,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.5751,0.22012,0.31391],"tcp_start":[0.46682,0.04632,0.13334],"tcp_to_object_dist_end":0.02608,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.5829,0.22549,0.19495],"object_pos_start":[0.58256,0.22013,0.28891],"object_to_goal_dist_end":0.03571,"object_to_goal_dist_start":0.05908,"object_z_max":0.28895,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.57774,0.22577,0.22344],"tcp_start":[0.5751,0.22012,0.31391],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44672,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10327,"descend_1.descend_depth":0.01915,"lift_1.lift_height":0.1297,"place_1.place_offset_z":-0.05143,"place_1.place_speed":0.07277,"transport_1.transport_speed":0.03446},"optimized_scores":{"best_composite_score":0.35268,"best_fitness_score":0.77268,"best_task_score":0.61465},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53448,-0.0204,-0.00137],"force_p95":0.42034,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44489,"mean_force":0.09429,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5216,-0.02065,0.04456]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5195.0,"contact_point_centroid":[0.52194,-0.00167,0.0941],"force_p95":0.11137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31634,"mean_force":0.07388,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51912,-0.02059,0.09176]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2335.0,"contact_point_centroid":[0.60888,0.23689,0.22608],"force_p95":0.17284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29079,"mean_force":0.10921,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60423,0.219,0.22889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5622.0,"contact_point_centroid":[0.52207,-0.0394,0.0919],"force_p95":0.10929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28906,"mean_force":0.06977,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51915,-0.02059,0.09024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2583.0,"contact_point_centroid":[0.60863,0.20058,0.23024],"force_p95":0.17214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2583,"mean_force":0.11143,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60414,0.2187,0.23277]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02119,-0.00206],"force_p95":0.1403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18177,"mean_force":0.12749,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52414,-0.02069,0.04464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11635.0,"contact_point_centroid":[0.56486,0.1135,0.21977],"force_p95":0.12287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16466,"mean_force":0.08002,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55874,0.09477,0.21845]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12962.0,"contact_point_centroid":[0.56578,0.07892,0.22115],"force_p95":0.09581,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15799,"mean_force":0.0722,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55977,0.09746,0.22011]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51327,-0.00882,0.22494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4106.0,"contact_point_centroid":[0.5238,-0.00146,0.04596],"force_p95":0.07773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13247,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52293,-0.02067,0.04324]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52864,-0.01952,0.09948]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4907.0,"contact_point_centroid":[0.5238,-0.03975,0.04504],"force_p95":0.0699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08405,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52294,-0.02067,0.04324]}],"total_contact_groups":12},"final_pose_error":0.01456,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60589,0.2225,0.13473],"final_tcp_position":[0.60591,0.22415,0.16938],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52867,-0.01829,0.14766],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12197,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.53129,-0.02082,0.05309],"tcp_start":[0.52867,-0.01829,0.14766],"tcp_to_object_dist_end":0.02768,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02069,0.02577],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31639,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.5229,-0.02067,0.0432],"tcp_start":[0.53129,-0.02082,0.05309],"tcp_to_object_dist_end":0.02238,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":363.0,"n_steps_budget":810.0,"object_pos_end":[0.53458,-0.02062,0.13114],"object_pos_start":[0.53694,-0.02069,0.02577],"object_to_goal_dist_end":0.27064,"object_to_goal_dist_start":0.31639,"object_z_max":0.13088,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51908,-0.02058,0.15334],"tcp_start":[0.5229,-0.02067,0.0432],"tcp_to_object_dist_end":0.02707,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60923,0.21415,0.26003],"object_pos_start":[0.53458,-0.02062,0.13114],"object_to_goal_dist_end":0.05436,"object_to_goal_dist_start":0.27064,"object_z_max":0.25993,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.60366,0.21431,0.29092],"tcp_start":[0.51908,-0.02058,0.15334],"tcp_to_object_dist_end":0.03139,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.60589,0.2225,0.13473],"object_pos_start":[0.60923,0.21415,0.26003],"object_to_goal_dist_end":0.073,"object_to_goal_dist_start":0.05436,"object_z_max":0.26003,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.60591,0.22415,0.16938],"tcp_start":[0.60366,0.21431,0.29092],"tcp_to_object_dist_end":0.03469,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93617,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.18832,"descend_1.descend_depth":0.01923,"lift_1.lift_height":0.11103,"place_1.place_offset_z":-0.03369,"place_1.place_speed":0.05579,"transport_1.transport_speed":0.18183},"optimized_scores":{"best_composite_score":0.18461,"best_fitness_score":0.60461,"best_task_score":0.2785},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1683.0,"contact_point_centroid":[0.58529,0.07192,-0.00257],"force_p95":0.26707,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69835,"mean_force":0.15185,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59637,0.10288,0.22398]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.54293,-0.02798,-0.00139],"force_p95":0.39533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44693,"mean_force":0.0974,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52982,-0.02824,0.04418]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2401.0,"contact_point_centroid":[0.54618,0.01886,0.15145],"force_p95":0.13299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33576,"mean_force":0.08478,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54003,0.00055,0.15089]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4455.0,"contact_point_centroid":[0.53002,-0.00921,0.08537],"force_p95":0.11229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31347,"mean_force":0.07367,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52729,-0.02815,0.0829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4866.0,"contact_point_centroid":[0.53017,-0.04697,0.08359],"force_p95":0.10918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29255,"mean_force":0.06942,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52732,-0.02815,0.08192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2006.0,"contact_point_centroid":[0.54435,-0.02125,0.14996],"force_p95":0.1642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23095,"mean_force":0.09705,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53848,-0.00263,0.14891]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02908,-0.00208],"force_p95":0.14661,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1992,"mean_force":0.12911,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53233,-0.02832,0.04427]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51696,-0.01218,0.22429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.53212,-0.00907,0.04554],"force_p95":0.07882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13734,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53111,-0.02828,0.04282]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53652,-0.02682,0.09891]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.58537,0.07205,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.6258,0.15811,0.21038]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4936.0,"contact_point_centroid":[0.53209,-0.04738,0.04459],"force_p95":0.07107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07466,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53111,-0.02828,0.04282]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1581.0,"contact_point_centroid":[0.60078,0.10989,0.23141],"force_p95":0.01184,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01045,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60029,0.10989,0.22908]},{"body_a":"left_finger","body_b":"right_finger","contact_count":977.0,"contact_point_centroid":[0.62614,0.1581,0.21304],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01049,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62579,0.15809,0.21069]}],"total_contact_groups":14},"final_pose_error":0.01468,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.58537,0.07205,0.01602],"final_tcp_position":[0.62774,0.16196,0.15667],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.53612,-0.0252,0.14661],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12103,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.53957,-0.02853,0.053],"tcp_start":[0.53612,-0.0252,0.14661],"tcp_to_object_dist_end":0.02765,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54553,-0.0284,0.0257],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26051,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.53108,-0.02828,0.04278],"tcp_start":[0.53957,-0.02853,0.053],"tcp_to_object_dist_end":0.02237,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":309.0,"n_steps_budget":720.0,"object_pos_end":[0.54279,-0.02823,0.11318],"object_pos_start":[0.54553,-0.0284,0.0257],"object_to_goal_dist_end":0.22245,"object_to_goal_dist_start":0.26051,"object_z_max":0.11292,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52704,-0.02814,0.13438],"tcp_start":[0.53108,-0.02828,0.04278],"tcp_to_object_dist_end":0.02641,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.58537,0.07205,0.01602],"object_pos_start":[0.54279,-0.02823,0.11318],"object_to_goal_dist_end":0.19175,"object_to_goal_dist_start":0.22245,"object_z_max":0.14194,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.62535,0.1549,0.26149],"tcp_start":[0.52704,-0.02814,0.13438],"tcp_to_object_dist_end":0.26214,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.58537,0.07205,0.01602],"object_pos_start":[0.58537,0.07205,0.01602],"object_to_goal_dist_end":0.19175,"object_to_goal_dist_start":0.19175,"object_z_max":0.01602,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.62774,0.16196,0.15667],"tcp_start":[0.62535,0.1549,0.26149],"tcp_to_object_dist_end":0.17222,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```