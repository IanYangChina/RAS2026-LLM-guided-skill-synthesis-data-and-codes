## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0544 | 0.24 | ✅ accepted |
| 0 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ✅ accepted |

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

## Current Skill (Q=-0.054) — your mutation base

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
  - 0.15
  weight: 0.4
- id: reach_goal
  weight: 0.6
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
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
  subtask_id: reach_object
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: move_to_goal
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
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.054
- **task_score** (E): 0.244
- **fitness_score**: 0.596  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1494 |
| descend_1 | 1.00 | 1.00 | 0.1138 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 1.00 | 0.0971 |
| move_to_goal | 0.00 | 1.00 | 0.0799 |
| place_1 | 0.00 | 1.00 | 0.0881 |
| release_1 | 1.00 | 1.00 | 0.0224 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.158) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 7.773 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.158)→(0.516, -0.001, 0.044) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.144 | 0.201 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.044)→(0.508, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 32.667 | 0.088 | 0.518 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.035)→(0.515, -0.001, 0.132) | (0.522, -0.001, 0.026)→(0.525, -0.001, 0.114) | 0.289→0.243 | 1.00 / 24.000 | 3249.615 | 0.639 |
| move_to_goal | approach | 0.00 / step_budget | (0.515, -0.001, 0.132)→(0.538, 0.058, 0.179) | (0.525, -0.001, 0.114)→(0.541, 0.059, 0.105) | 0.243→0.204 | 1.00 / 16.000 | 3249.704 | 0.130 |
| place_1 | descend | 0.00 / step_budget | (0.538, 0.058, 0.179)→(0.573, 0.137, 0.192) | (0.541, 0.059, 0.105)→(0.561, 0.110, 0.105) | 0.204→0.152 | 1.00 / 2.667 | 0.135 | 0.947 |
| release_1 | release | 1.00 / step_budget | (0.573, 0.137, 0.192)→(0.568, 0.136, 0.214) | (0.561, 0.110, 0.105)→(0.552, 0.109, 0.022) | 0.152→0.216 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.316
- phase_score: 0.288
- phase_breakdown.reach_goal_score: 0.229
- phase_breakdown.reach_object_score: 0.377
- grasp_place_fitness: 0.629

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.629
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.316
- **Median Q (composite search score)**: -0.058
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05394,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13986,"approach_1.speed":0.02022,"descend_1.descend_offset_z":0.0021,"descend_1.speed":0.08401,"lift_1.lift_height":0.11411,"lift_1.speed":0.0996,"move_to_goal.approach_goal_height":0.13377,"move_to_goal.speed":0.0529,"place_1.place_z_offset":0.01074,"place_1.speed":0.09247},"optimized_scores":{"best_composite_score":-0.08389,"best_fitness_score":0.56611,"best_task_score":0.17321},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.50409,0.09802,-0.0036],"force_p95":0.74379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69039,"mean_force":0.19839,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50085,0.09275,0.18273]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.48071,0.04601,-0.00121],"force_p95":0.43167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60952,"mean_force":0.06848,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46905,0.04688,0.03064]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10585.0,"contact_point_centroid":[0.47343,0.06571,0.07343],"force_p95":0.10395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30044,"mean_force":0.06219,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47153,0.04672,0.07173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10316.0,"contact_point_centroid":[0.47404,0.02785,0.076],"force_p95":0.09964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27173,"mean_force":0.06269,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4718,0.04672,0.07425]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04844,-0.00215],"force_p95":0.16638,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24931,"mean_force":0.13447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47133,0.04714,0.02981]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8662.0,"contact_point_centroid":[0.48964,0.0478,0.14735],"force_p95":0.13879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21603,"mean_force":0.08413,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48562,0.06618,0.14885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8622.0,"contact_point_centroid":[0.49045,0.08561,0.14873],"force_p95":0.12934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18354,"mean_force":0.08564,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48622,0.06724,0.1502]},{"body_a":"world","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48973,0.0209,0.23939]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.504,0.09808,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12326,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.52682,0.14109,0.19949]},{"body_a":"world","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47829,0.04552,0.10667]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.504,0.09808,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54565,0.17725,0.21593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5011.0,"contact_point_centroid":[0.47004,0.02779,0.0317],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11622,"mean_force":0.04302,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4702,0.04703,0.02868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5531.0,"contact_point_centroid":[0.46986,0.06637,0.03106],"force_p95":0.07051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08114,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47021,0.04703,0.02869]},{"body_a":"left_finger","body_b":"right_finger","contact_count":356.0,"contact_point_centroid":[0.50192,0.09411,0.18664],"force_p95":0.01423,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01122,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50163,0.09409,0.18446]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4280.0,"contact_point_centroid":[0.52742,0.14127,0.20182],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01042,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.52692,0.14125,0.19955]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.54884,0.17814,0.21341],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54792,0.17811,0.21135]}],"total_contact_groups":16},"final_pose_error":0.0662,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.504,0.09808,0.01602],"final_tcp_position":[0.54907,0.17831,0.21381],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.86027,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48094,0.04346,0.17791],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15905,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12342.0,"raw_peak_contact_force":0.24931,"subtask_id":"reach_object","tcp_end":[0.47808,0.04781,0.03669],"tcp_start":[0.48094,0.04346,0.17791],"tcp_to_object_dist_end":0.01167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04723,0.02547],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29133,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.10206,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":21044.0,"raw_peak_contact_force":0.60952,"subtask_id":"reach_object","tcp_end":[0.47018,0.04703,0.02865],"tcp_start":[0.47808,0.04781,0.03669],"tcp_to_object_dist_end":0.01283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.49459,0.04708,0.11645],"object_pos_start":[0.48261,0.04723,0.02547],"object_to_goal_dist_end":0.23165,"object_to_goal_dist_start":0.29133,"object_z_max":0.11635,"peak_contact_force":9748.68205,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18220.0,"raw_peak_contact_force":1.69039,"subtask_id":"reach_object","tcp_end":[0.47791,0.04683,0.12806],"tcp_start":[0.47018,0.04703,0.02865],"tcp_to_object_dist_end":0.02033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.504,0.09806,0.016],"object_pos_start":[0.49459,0.04708,0.11645],"object_to_goal_dist_end":0.26301,"object_to_goal_dist_start":0.23165,"object_z_max":0.14911,"peak_contact_force":9748.86027,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8280.0,"raw_peak_contact_force":0.12326,"subtask_id":"reach_goal","tcp_end":[0.50273,0.09596,0.18687],"tcp_start":[0.47791,0.04683,0.12806],"tcp_to_object_dist_end":0.17089,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.504,0.09808,0.01602],"object_pos_start":[0.504,0.09806,0.016],"object_to_goal_dist_end":0.26299,"object_to_goal_dist_start":0.26301,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.54907,0.17831,0.21381],"tcp_start":[0.50273,0.09596,0.18687],"tcp_to_object_dist_end":0.21815,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.504,0.09808,0.01602],"object_pos_start":[0.504,0.09808,0.01602],"object_to_goal_dist_end":0.26299,"object_to_goal_dist_start":0.26299,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1792.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.54436,0.17675,0.2361],"tcp_start":[0.54907,0.17831,0.21381],"tcp_to_object_dist_end":0.23718,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27568,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11665,"approach_1.speed":0.06528,"descend_1.descend_offset_z":0.01425,"descend_1.speed":0.06137,"lift_1.lift_height":0.15566,"lift_1.speed":0.06022,"move_to_goal.approach_goal_height":0.10065,"move_to_goal.speed":0.08662,"place_1.place_z_offset":0.01478,"place_1.speed":0.05278},"optimized_scores":{"best_composite_score":-0.05842,"best_fitness_score":0.59158,"best_task_score":0.24245},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":177.0,"contact_point_centroid":[0.55865,0.1286,-0.00751],"force_p95":1.28307,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45538,"mean_force":0.40047,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56806,0.13041,0.20611]},{"body_a":"world","body_b":"grasp_target","contact_count":207.0,"contact_point_centroid":[0.53356,-0.02058,-0.00116],"force_p95":0.26094,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46997,"mean_force":0.0738,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52138,-0.02079,0.04026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18167.0,"contact_point_centroid":[0.5249,-0.00163,0.08933],"force_p95":0.0791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29567,"mean_force":0.05523,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52385,-0.02072,0.08701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18833.0,"contact_point_centroid":[0.5248,-0.03977,0.08786],"force_p95":0.07737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2795,"mean_force":0.0537,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52375,-0.02072,0.08579]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02118,-0.00205],"force_p95":0.1366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16871,"mean_force":0.12652,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5242,-0.02086,0.04004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":650.0,"contact_point_centroid":[0.57607,0.11313,0.18763],"force_p95":0.1253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1595,"mean_force":0.07653,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57167,0.13139,0.18987]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13237,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51366,-0.00953,0.22634]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12350.0,"contact_point_centroid":[0.56437,0.11453,0.18442],"force_p95":0.12317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13501,"mean_force":0.07589,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56083,0.09575,0.18574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":540.0,"contact_point_centroid":[0.57619,0.14966,0.18595],"force_p95":0.12624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1336,"mean_force":0.08893,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57162,0.13137,0.18979]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14009.0,"contact_point_centroid":[0.56513,0.07892,0.18555],"force_p95":0.0973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12758,"mean_force":0.06638,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56142,0.09749,0.18606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.52384,-0.00163,0.04138],"force_p95":0.07715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12644,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52299,-0.02083,0.03864]},{"body_a":"world","body_b":"grasp_target","contact_count":1372.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52934,-0.02018,0.10049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17542.0,"contact_point_centroid":[0.54156,0.00246,0.16071],"force_p95":0.07825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11672,"mean_force":0.05563,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5389,0.02149,0.15906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17893.0,"contact_point_centroid":[0.54104,0.03983,0.15967],"force_p95":0.07817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10918,"mean_force":0.05422,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.53868,0.02084,0.15861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4900.0,"contact_point_centroid":[0.52384,-0.03992,0.04044],"force_p95":0.06922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08899,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52299,-0.02083,0.03865]}],"total_contact_groups":15},"final_pose_error":0.107,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.56612,0.12899,0.02447],"final_tcp_position":[0.57332,0.13167,0.19307],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.45538,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1372.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53007,-0.01945,0.15346],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13396,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10808.0,"raw_peak_contact_force":0.16871,"subtask_id":"reach_object","tcp_end":[0.53141,-0.02099,0.04849],"tcp_start":[0.53007,-0.01945,0.15346],"tcp_to_object_dist_end":0.02317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53693,-0.02077,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31643,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.08164,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":37207.0,"raw_peak_contact_force":0.46997,"subtask_id":"reach_object","tcp_end":[0.52296,-0.02083,0.03861],"tcp_start":[0.53141,-0.02099,0.04849],"tcp_to_object_dist_end":0.01893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53517,-0.02067,0.11496],"object_pos_start":[0.53693,-0.02077,0.02582],"object_to_goal_dist_end":0.27551,"object_to_goal_dist_start":0.31643,"object_z_max":0.11485,"peak_contact_force":0.08468,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35435.0,"raw_peak_contact_force":0.11672,"subtask_id":"reach_object","tcp_end":[0.52881,-0.0207,0.13574],"tcp_start":[0.52296,-0.02083,0.03861],"tcp_to_object_dist_end":0.02173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55474,0.05771,0.15781],"object_pos_start":[0.53517,-0.02067,0.11496],"object_to_goal_dist_end":0.18564,"object_to_goal_dist_start":0.27551,"object_z_max":0.15778,"peak_contact_force":0.12706,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26359.0,"raw_peak_contact_force":0.13501,"subtask_id":"reach_goal","tcp_end":[0.55085,0.05772,0.18367],"tcp_start":[0.52881,-0.0207,0.13574],"tcp_to_object_dist_end":0.02615,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57852,0.13055,0.16027],"object_pos_start":[0.55474,0.05771,0.15781],"object_to_goal_dist_end":0.11261,"object_to_goal_dist_start":0.18564,"object_z_max":0.16028,"peak_contact_force":0.14405,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1367.0,"raw_peak_contact_force":1.45538,"subtask_id":"reach_goal","tcp_end":[0.57332,0.13167,0.19307],"tcp_start":[0.55085,0.05772,0.18367],"tcp_to_object_dist_end":0.03322,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56612,0.12899,0.02447],"object_pos_start":[0.57852,0.13055,0.16027],"object_to_goal_dist_end":0.21255,"object_to_goal_dist_start":0.11261,"object_z_max":0.16027,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.568,0.1304,0.21486],"tcp_start":[0.57332,0.13167,0.19307],"tcp_to_object_dist_end":0.19041,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05505,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1068,"approach_1.speed":0.05149,"descend_1.descend_offset_z":0.01381,"descend_1.speed":0.03763,"lift_1.lift_height":0.13347,"lift_1.speed":0.05867,"move_to_goal.approach_goal_height":0.11923,"move_to_goal.speed":0.0508,"place_1.place_z_offset":0.00953,"place_1.speed":0.08062},"optimized_scores":{"best_composite_score":-0.02093,"best_fitness_score":0.62907,"best_task_score":0.3165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":191.0,"contact_point_centroid":[0.57976,0.09909,-0.00645],"force_p95":1.17577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26388,"mean_force":0.34873,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59067,0.10026,0.18241]},{"body_a":"world","body_b":"grasp_target","contact_count":229.0,"contact_point_centroid":[0.54207,-0.02807,-0.00117],"force_p95":0.26671,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47501,"mean_force":0.07481,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52956,-0.02843,0.03937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":733.0,"contact_point_centroid":[0.59898,0.11948,0.16481],"force_p95":0.12402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29652,"mean_force":0.09032,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59449,0.10106,0.1665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18043.0,"contact_point_centroid":[0.53408,-0.00926,0.08662],"force_p95":0.07966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29063,"mean_force":0.05549,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53291,-0.02835,0.08432]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.5991,0.08243,0.16462],"force_p95":0.15325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28829,"mean_force":0.08988,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59449,0.10106,0.16651]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18885.0,"contact_point_centroid":[0.53395,-0.0474,0.08508],"force_p95":0.07745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28154,"mean_force":0.05366,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53278,-0.02835,0.08309]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02907,-0.00207],"force_p95":0.14242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18525,"mean_force":0.12799,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53245,-0.02853,0.03915]},{"body_a":"world","body_b":"grasp_target","contact_count":2372.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51774,-0.01327,0.22061]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14918.0,"contact_point_centroid":[0.58137,0.04555,0.16609],"force_p95":0.09019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13232,"mean_force":0.06366,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57757,0.06441,0.16623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.53219,-0.00929,0.04042],"force_p95":0.07815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13125,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53122,-0.0285,0.0377]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5375,-0.02777,0.09505]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17169.0,"contact_point_centroid":[0.55015,-0.02021,0.14949],"force_p95":0.07924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11077,"mean_force":0.05631,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54796,-0.00129,0.14859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16843.0,"contact_point_centroid":[0.55117,0.01875,0.15114],"force_p95":0.08621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10294,"mean_force":0.05713,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54846,-0.00022,0.14945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14963.0,"contact_point_centroid":[0.58154,0.08327,0.16648],"force_p95":0.08946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10238,"mean_force":0.06281,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57758,0.06441,0.16624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4922.0,"contact_point_centroid":[0.53217,-0.04759,0.03948],"force_p95":0.07027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07961,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53122,-0.0285,0.0377]}],"total_contact_groups":15},"final_pose_error":0.07509,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.58508,0.09891,0.0248],"final_tcp_position":[0.59647,0.10128,0.17018],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":23.07482,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":23.07482,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1276.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53817,-0.02691,0.14284],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13867,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10821.0,"raw_peak_contact_force":0.18525,"subtask_id":"reach_object","tcp_end":[0.53975,-0.02875,0.04787],"tcp_start":[0.53817,-0.02691,0.14284],"tcp_to_object_dist_end":0.02262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5455,-0.0285,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26056,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.08168,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":37157.0,"raw_peak_contact_force":0.47501,"subtask_id":"reach_object","tcp_end":[0.53119,-0.02849,0.03766],"tcp_start":[0.53975,-0.02875,0.04787],"tcp_to_object_dist_end":0.01862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54537,-0.02832,0.11153],"object_pos_start":[0.5455,-0.0285,0.02576],"object_to_goal_dist_end":0.22197,"object_to_goal_dist_start":0.26056,"object_z_max":0.11142,"peak_contact_force":0.07909,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34012.0,"raw_peak_contact_force":0.11077,"subtask_id":"reach_object","tcp_end":[0.53869,-0.02836,0.13173],"tcp_start":[0.53119,-0.02849,0.03766],"tcp_to_object_dist_end":0.02128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56285,0.02167,0.14192],"object_pos_start":[0.54537,-0.02832,0.11153],"object_to_goal_dist_end":0.16324,"object_to_goal_dist_start":0.22197,"object_z_max":0.14189,"peak_contact_force":0.12439,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29881.0,"raw_peak_contact_force":0.13232,"subtask_id":"reach_goal","tcp_end":[0.55905,0.02151,0.16745],"tcp_start":[0.53869,-0.02836,0.13173],"tcp_to_object_dist_end":0.02581,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60159,0.10129,0.13907],"object_pos_start":[0.56285,0.02167,0.14192],"object_to_goal_dist_end":0.08037,"object_to_goal_dist_start":0.16324,"object_z_max":0.14192,"peak_contact_force":0.13779,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1648.0,"raw_peak_contact_force":1.26388,"subtask_id":"reach_goal","tcp_end":[0.59647,0.10128,0.17018],"tcp_start":[0.55905,0.02151,0.16745],"tcp_to_object_dist_end":0.03153,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58508,0.09891,0.0248],"object_pos_start":[0.60159,0.10129,0.13907],"object_to_goal_dist_end":0.17257,"object_to_goal_dist_start":0.08037,"object_z_max":0.13907,"peak_contact_force":0.12262,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2372.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.59061,0.10025,0.19135],"tcp_start":[0.59647,0.10128,0.17018],"tcp_to_object_dist_end":0.16665,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```