## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0818 | 0.26 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0682 | 0.30 | ❌ rejected |
| 1 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0773 | 0.32 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.3457 | 0.14 | ✅ accepted |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.082) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: reach_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.4
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
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above_object
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
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
    orientation:
      mode: keep_current
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
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
  subtask_id: lift_object
- id: transport_1
  type: push
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
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    transport_xy_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    transport_xy_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    transport_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
  guards:
  - id: object_held
    when: during_phase
    predicate: object_lifted
    threshold: 0.01
    on_failure: abort
  subtask_id: approach_goal
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
  parameters:
    place_delay:
      type: scalar
      range:
      - 0.0
      - 0.5
      default: 0.1
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: place_at_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.03
      - 0.2
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - transport_xy_offset_x: status=consumed; consumers=target.offset.x (add)
    - transport_xy_offset_y: status=consumed; consumers=target.offset.y (add)
    - transport_z_offset: status=consumed; consumers=target.offset.z (add)
  - guards:
    - id=object_held, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.01
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_delay: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.082
- **task_score** (E): 0.261
- **fitness_score**: 0.598  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0910 |
| descend_1 | 1.00 | 1.00 | 0.1675 |
| grasp_1 | 1.00 | 1.00 | 0.0138 |
| lift_1 | 1.00 | 1.00 | 0.1399 |
| transport_1 | 1.00 | 0.67 | 0.2296 |
| descend_place_1 | 1.00 | 1.00 | 0.0162 |
| release_1 | 1.00 | 1.00 | 0.0197 |
| retract_1 | 1.00 | 1.00 | 0.1203 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.000, 0.218) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 17.711 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.514, 0.000, 0.218)→(0.516, -0.001, 0.051) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 17.078 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.051)→(0.507, -0.001, 0.040) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 44.000 | 0.156 | 0.209 |
| lift_1 | lift | 1.00 / step_budget | (0.507, -0.001, 0.040)→(0.517, -0.001, 0.180) | (0.522, -0.001, 0.026)→(0.532, -0.001, 0.157) | 0.290→0.229 | 1.00 / 22.667 | 22.251 | 0.450 |
| transport_1 | approach | 1.00 / step_budget | (0.517, -0.001, 0.180)→(0.609, 0.187, 0.260) | (0.532, -0.001, 0.157)→(0.611, 0.145, 0.040) | 0.229→0.181 | 0.67 / 4.000 | 0.214 | 1.316 |
| descend_place_1 | descend | 1.00 / step_budget | (0.609, 0.187, 0.260)→(0.607, 0.197, 0.256) | (0.611, 0.145, 0.040)→(0.614, 0.146, 0.016) | 0.181→0.205 | 1.00 / 8.333 | 6498.379 | 0.777 |
| release_1 | release | 1.00 / step_budget | (0.607, 0.197, 0.256)→(0.603, 0.196, 0.275) | (0.614, 0.146, 0.016)→(0.614, 0.146, 0.016) | 0.205→0.205 | 1.00 / 4.000 | 0.123 | 0.125 |
| retract_1 | retract | 1.00 / step_budget | (0.603, 0.196, 0.275)→(0.603, 0.196, 0.396) | (0.614, 0.146, 0.016)→(0.614, 0.146, 0.016) | 0.205→0.205 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.339
- phase_score: 0.468
- phase_breakdown.approach_goal_xy_score: 0.625
- phase_breakdown.reach_above_object_score: 0.147
- phase_breakdown.reach_object_score: 0.659
- phase_breakdown.lift_object_score: 0.819
- phase_breakdown.place_at_goal_score: 0.306
- grasp_place_fitness: 0.632

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.632
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.339
- **Median Q (composite search score)**: -0.090
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.285


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8427,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1453,"descend_1.grasp_offset_z":0.00016,"descend_place_1.place_z_offset":0.06372,"lift_1.lift_height":0.2139,"release_1.place_delay":0.26872,"retract_1.retract_height":0.13807,"transport_1.transport_speed":0.21084,"transport_1.transport_xy_offset_x":0.00774,"transport_1.transport_xy_offset_y":-0.00931,"transport_1.transport_z_offset":0.0237},"optimized_scores":{"best_composite_score":-0.08955,"best_fitness_score":0.59045,"best_task_score":0.23481},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":67.0,"contact_point_centroid":[0.5971,0.19617,-0.00963],"force_p95":1.75742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.97019,"mean_force":0.93881,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57949,0.20536,0.28973]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.48094,0.04574,-0.00149],"force_p95":0.43926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49915,"mean_force":0.09827,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46875,0.04607,0.03824]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.59746,0.19738,-0.00742],"force_p95":0.37826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47604,"mean_force":0.13139,"phase_index":5.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.58055,0.2109,0.28899]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5057.0,"contact_point_centroid":[0.52668,0.09446,0.24499],"force_p95":0.14056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29065,"mean_force":0.08356,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51926,0.11224,0.2466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4122.0,"contact_point_centroid":[0.52509,0.13202,0.24721],"force_p95":0.14691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29036,"mean_force":0.09845,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51972,0.11297,0.24693]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7874.0,"contact_point_centroid":[0.47399,0.06546,0.11949],"force_p95":0.11431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28615,"mean_force":0.07573,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4717,0.04625,0.11712]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10124.0,"contact_point_centroid":[0.47532,0.02772,0.11678],"force_p95":0.10186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26455,"mean_force":0.06141,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4716,0.04625,0.11577]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48283,0.04862,-0.00222],"force_p95":0.18244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24379,"mean_force":0.13875,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47108,0.0463,0.03764]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5233.0,"contact_point_centroid":[0.47137,0.02718,0.03771],"force_p95":0.06654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20927,"mean_force":0.04132,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46991,0.04619,0.03645]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.4827,0.04873,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49121,0.01883,0.24775]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59768,0.19733,-0.00194],"force_p95":0.12499,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12531,"mean_force":0.1192,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57796,0.21505,0.28794]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47985,0.04324,0.11963]},{"body_a":"world","body_b":"grasp_target","contact_count":1768.0,"contact_point_centroid":[0.59768,0.19733,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57681,0.21412,0.3653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4279.0,"contact_point_centroid":[0.46961,0.06557,0.03881],"force_p95":0.0859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09322,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46992,0.04619,0.03646]},{"body_a":"left_finger","body_b":"right_finger","contact_count":83.0,"contact_point_centroid":[0.58158,0.21317,0.28999],"force_p95":0.01607,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01348,"phase_index":5.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.58043,0.21313,0.28809]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.58,0.21594,0.28637],"force_p95":0.01145,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01297,"mean_force":0.01031,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57925,0.21592,0.28437]}],"total_contact_groups":16},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59768,0.19733,0.01602],"final_tcp_position":[0.57785,0.2144,0.4257],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9746.22384,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":884.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.48283,0.03969,0.19259],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47864,0.047,0.04564],"tcp_start":[0.48283,0.03969,0.19259],"tcp_to_object_dist_end":0.02011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48279,0.04721,0.02524],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29144,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17696,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11312.0,"raw_peak_contact_force":0.24379,"subtask_id":"reach_object","tcp_end":[0.46988,0.04619,0.03642],"tcp_start":[0.47864,0.047,0.04564],"tcp_to_object_dist_end":0.01711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.49411,0.04827,0.1984],"object_pos_start":[0.48279,0.04721,0.02524],"object_to_goal_dist_end":0.20333,"object_to_goal_dist_start":0.29144,"object_z_max":0.19814,"peak_contact_force":66.5477,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18081.0,"raw_peak_contact_force":0.49915,"subtask_id":"lift_object","tcp_end":[0.47886,0.04682,0.2198],"tcp_start":[0.46988,0.04619,0.03642],"tcp_to_object_dist_end":0.02632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.59841,0.19698,-0.0062],"object_pos_start":[0.49411,0.04827,0.1984],"object_to_goal_dist_end":0.2394,"object_to_goal_dist_start":0.20333,"object_z_max":0.23765,"peak_contact_force":0.51791,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9246.0,"raw_peak_contact_force":1.97019,"subtask_id":"approach_goal_xy","tcp_end":[0.58088,0.20768,0.29072],"tcp_start":[0.47886,0.04682,0.2198],"tcp_to_object_dist_end":0.29763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":41.0,"n_steps_budget":1000.0,"object_pos_end":[0.59777,0.19741,0.01511],"object_pos_start":[0.59841,0.19698,-0.0062],"object_to_goal_dist_end":0.21823,"object_to_goal_dist_start":0.2394,"object_z_max":0.01489,"peak_contact_force":9746.22384,"phase_name":"descend_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":247.0,"raw_peak_contact_force":0.47604,"subtask_id":"place_at_goal","tcp_end":[0.5803,0.21568,0.28749],"tcp_start":[0.58088,0.20768,0.29072],"tcp_to_object_dist_end":0.27355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59768,0.19733,0.01602],"object_pos_start":[0.59777,0.19741,0.01511],"object_to_goal_dist_end":0.21735,"object_to_goal_dist_start":0.21823,"object_z_max":0.01678,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12531,"subtask_id":"place_at_goal","tcp_end":[0.57733,0.2146,0.30743],"tcp_start":[0.5803,0.21568,0.28749],"tcp_to_object_dist_end":0.29263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":442.0,"n_steps_budget":870.0,"object_pos_end":[0.59768,0.19733,0.01602],"object_pos_start":[0.59768,0.19733,0.01602],"object_to_goal_dist_end":0.21735,"object_to_goal_dist_start":0.21735,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1768.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57785,0.2144,0.4257],"tcp_start":[0.57733,0.2146,0.30743],"tcp_to_object_dist_end":0.41051,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19266,"descend_1.grasp_offset_z":0.00661,"descend_place_1.place_z_offset":0.05509,"lift_1.lift_height":0.1246,"release_1.place_delay":0.23642,"retract_1.retract_height":0.16869,"transport_1.transport_speed":0.38281,"transport_1.transport_xy_offset_x":0.01148,"transport_1.transport_xy_offset_y":-0.02257,"transport_1.transport_z_offset":0.04285},"optimized_scores":{"best_composite_score":-0.10799,"best_fitness_score":0.57201,"best_task_score":0.20953},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.59832,0.09288,-0.00266],"force_p95":0.32882,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71394,"mean_force":0.15358,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5941,0.14129,0.24497]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.53547,-0.02063,-0.00135],"force_p95":0.36751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42739,"mean_force":0.08492,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52111,-0.02047,0.04207]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4387.0,"contact_point_centroid":[0.52733,-0.03971,0.08348],"force_p95":0.10987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27728,"mean_force":0.07548,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52433,-0.02064,0.08094]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5310.0,"contact_point_centroid":[0.52751,-0.00196,0.08141],"force_p95":0.1045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26709,"mean_force":0.06515,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5242,-0.02063,0.07985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2431.0,"contact_point_centroid":[0.5495,-0.00141,0.15646],"force_p95":0.14813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23164,"mean_force":0.09616,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54401,0.01739,0.1552]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3096.0,"contact_point_centroid":[0.55199,0.03942,0.15783],"force_p95":0.10876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20136,"mean_force":0.07833,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54549,0.02131,0.15789]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02133,-0.00207],"force_p95":0.14203,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18025,"mean_force":0.12782,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52335,-0.0205,0.04211]},{"body_a":"world","body_b":"grasp_target","contact_count":576.0,"contact_point_centroid":[0.53702,-0.02132,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12347,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51154,-0.00741,0.26961]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52708,-0.01814,0.1447]},{"body_a":"world","body_b":"grasp_target","contact_count":304.0,"contact_point_centroid":[0.59838,0.09291,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.61381,0.20298,0.2748]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59838,0.09291,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60819,0.21253,0.26404]},{"body_a":"world","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.59838,0.09291,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60667,0.21155,0.35585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5302.0,"contact_point_centroid":[0.52315,-0.00144,0.04305],"force_p95":0.06645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11047,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52211,-0.02048,0.0407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4184.0,"contact_point_centroid":[0.52312,-0.03979,0.04339],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08093,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52212,-0.02048,0.0407]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1311.0,"contact_point_centroid":[0.59847,0.15007,0.25369],"force_p95":0.01228,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59772,0.15005,0.25141]},{"body_a":"left_finger","body_b":"right_finger","contact_count":321.0,"contact_point_centroid":[0.61439,0.20306,0.27678],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01053,"phase_index":5.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.6138,0.20304,0.27474]}],"total_contact_groups":17},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59838,0.09291,0.01602],"final_tcp_position":[0.60811,0.21199,0.43197],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.7868,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":576.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52495,-0.01576,0.2371],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1384.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.53123,-0.02058,0.05158],"tcp_start":[0.52495,-0.01576,0.2371],"tcp_to_object_dist_end":0.02622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02099,0.02575],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31663,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14111,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11286.0,"raw_peak_contact_force":0.18025,"subtask_id":"reach_object","tcp_end":[0.52208,-0.02048,0.04066],"tcp_start":[0.53123,-0.02058,0.05158],"tcp_to_object_dist_end":0.02106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":320.0,"n_steps_budget":720.0,"object_pos_end":[0.54705,-0.02142,0.11104],"object_pos_start":[0.53695,-0.02099,0.02575],"object_to_goal_dist_end":0.27455,"object_to_goal_dist_start":0.31663,"object_z_max":0.1108,"peak_contact_force":0.10474,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9780.0,"raw_peak_contact_force":0.42739,"subtask_id":"lift_object","tcp_end":[0.53108,-0.02087,0.13138],"tcp_start":[0.52208,-0.02048,0.04066],"tcp_to_object_dist_end":0.02587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.59838,0.09291,0.01602],"object_pos_start":[0.54705,-0.02142,0.11104],"object_to_goal_dist_end":0.23443,"object_to_goal_dist_start":0.27455,"object_z_max":0.15619,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8286.0,"raw_peak_contact_force":1.71394,"subtask_id":"approach_goal_xy","tcp_end":[0.6162,0.19484,0.28416],"tcp_start":[0.53108,-0.02087,0.13138],"tcp_to_object_dist_end":0.28742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":76.0,"n_steps_budget":1000.0,"object_pos_end":[0.59838,0.09291,0.01602],"object_pos_start":[0.59838,0.09291,0.01602],"object_to_goal_dist_end":0.23443,"object_to_goal_dist_start":0.23443,"object_z_max":0.01602,"peak_contact_force":9748.7868,"phase_name":"descend_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":625.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.61108,0.21313,0.26457],"tcp_start":[0.6162,0.19484,0.28416],"tcp_to_object_dist_end":0.27639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59838,0.09291,0.01602],"object_pos_start":[0.59838,0.09291,0.01602],"object_to_goal_dist_end":0.23443,"object_to_goal_dist_start":0.23443,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.60736,0.21204,0.28325],"tcp_start":[0.61108,0.21313,0.26457],"tcp_to_object_dist_end":0.29272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.59838,0.09291,0.01602],"object_pos_start":[0.59838,0.09291,0.01602],"object_to_goal_dist_end":0.23443,"object_to_goal_dist_start":0.23443,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60811,0.21199,0.43197],"tcp_start":[0.60736,0.21204,0.28325],"tcp_to_object_dist_end":0.43277,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84277,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18102,"descend_1.grasp_offset_z":0.01062,"descend_place_1.place_z_offset":0.05381,"lift_1.lift_height":0.18254,"release_1.place_delay":0.29463,"retract_1.retract_height":0.11378,"transport_1.transport_speed":0.33516,"transport_1.transport_xy_offset_x":0.00768,"transport_1.transport_xy_offset_y":0.00714,"transport_1.transport_z_offset":-0.01178},"optimized_scores":{"best_composite_score":-0.04781,"best_fitness_score":0.63219,"best_task_score":0.33868},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":396.0,"contact_point_centroid":[0.64502,0.14682,-0.00461],"force_p95":0.89539,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73336,"mean_force":0.23223,"phase_index":5.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.62929,0.16118,0.21115]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.54395,-0.02805,-0.00137],"force_p95":0.3318,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42208,"mean_force":0.07536,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52939,-0.02803,0.0459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7019.0,"contact_point_centroid":[0.53708,-0.04727,0.11413],"force_p95":0.10993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31475,"mean_force":0.07412,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53335,-0.02829,0.11135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7601.0,"contact_point_centroid":[0.53721,-0.00964,0.10698],"force_p95":0.11274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27158,"mean_force":0.07038,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53282,-0.02826,0.10584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4971.0,"contact_point_centroid":[0.58434,0.03479,0.19145],"force_p95":0.13286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26435,"mean_force":0.08862,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57925,0.05341,0.19328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4794.0,"contact_point_centroid":[0.58273,0.06584,0.19007],"force_p95":0.13776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23379,"mean_force":0.09231,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5764,0.04764,0.19267]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54566,-0.0293,-0.00211],"force_p95":0.15154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20186,"mean_force":0.13055,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53174,-0.02809,0.04583]},{"body_a":"world","body_b":"grasp_target","contact_count":700.0,"contact_point_centroid":[0.5456,-0.02923,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51549,-0.01081,0.26324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5303.0,"contact_point_centroid":[0.53219,-0.009,0.04651],"force_p95":0.06706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13724,"mean_force":0.04127,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5305,-0.02806,0.04437]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64484,0.14643,-0.00198],"force_p95":0.1246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12655,"mean_force":0.12292,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62608,0.16161,0.21638]},{"body_a":"world","body_b":"grasp_target","contact_count":1260.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53533,-0.02544,0.14065]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.64484,0.14643,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62298,0.16054,0.28185]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4718.0,"contact_point_centroid":[0.53108,-0.04735,0.04793],"force_p95":0.08208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08572,"mean_force":0.04867,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53051,-0.02806,0.04438]},{"body_a":"left_finger","body_b":"right_finger","contact_count":168.0,"contact_point_centroid":[0.63017,0.1621,0.21658],"force_p95":0.01511,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01155,"phase_index":5.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.62932,0.16208,0.21443]},{"body_a":"left_finger","body_b":"right_finger","contact_count":234.0,"contact_point_centroid":[0.62935,0.1624,0.21591],"force_p95":0.01074,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01078,"mean_force":0.00957,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62839,0.16237,0.21348]}],"total_contact_groups":15},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64484,0.14643,0.01602],"final_tcp_position":[0.62338,0.16059,0.32934],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":52.88783,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":52.88783,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.5331,-0.02272,0.22484],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":50.98995,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1260.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53962,-0.02826,0.05556],"tcp_start":[0.5331,-0.02272,0.22484],"tcp_to_object_dist_end":0.03016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54568,-0.02881,0.02561],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26082,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15085,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11821.0,"raw_peak_contact_force":0.20186,"subtask_id":"reach_object","tcp_end":[0.53047,-0.02806,0.04434],"tcp_start":[0.53962,-0.02826,0.05556],"tcp_to_object_dist_end":0.02413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.55568,-0.02955,0.16201],"object_pos_start":[0.54568,-0.02881,0.02561],"object_to_goal_dist_end":0.20976,"object_to_goal_dist_start":0.26082,"object_z_max":0.16177,"peak_contact_force":0.10198,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14704.0,"raw_peak_contact_force":0.42208,"subtask_id":"lift_object","tcp_end":[0.54091,-0.02866,0.18881],"tcp_start":[0.53047,-0.02806,0.04434],"tcp_to_object_dist_end":0.03062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.63515,0.14544,0.11028],"object_pos_start":[0.55568,-0.02955,0.16201],"object_to_goal_dist_end":0.06947,"object_to_goal_dist_start":0.20976,"object_z_max":0.16314,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9765.0,"raw_peak_contact_force":0.26435,"subtask_id":"approach_goal_xy","tcp_end":[0.63101,0.15803,0.20453],"tcp_start":[0.54091,-0.02866,0.18881],"tcp_to_object_dist_end":0.09518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":134.0,"n_steps_budget":1000.0,"object_pos_end":[0.64495,0.14639,0.01631],"object_pos_start":[0.63515,0.14544,0.11028],"object_to_goal_dist_end":0.16213,"object_to_goal_dist_start":0.06947,"object_z_max":0.11028,"peak_contact_force":0.12656,"phase_name":"descend_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":564.0,"raw_peak_contact_force":1.73336,"subtask_id":"place_at_goal","tcp_end":[0.62942,0.16259,0.21633],"tcp_start":[0.63101,0.15803,0.20453],"tcp_to_object_dist_end":0.20128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64484,0.14643,0.01602],"object_pos_start":[0.64495,0.14639,0.01631],"object_to_goal_dist_end":0.16241,"object_to_goal_dist_start":0.16213,"object_z_max":0.01631,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1034.0,"raw_peak_contact_force":0.12655,"subtask_id":"place_at_goal","tcp_end":[0.62481,0.16118,0.23549],"tcp_start":[0.62942,0.16259,0.21633],"tcp_to_object_dist_end":0.22088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":720.0,"object_pos_end":[0.64484,0.14643,0.01602],"object_pos_start":[0.64484,0.14643,0.01602],"object_to_goal_dist_end":0.16241,"object_to_goal_dist_start":0.16241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62338,0.16059,0.32934],"tcp_start":[0.62481,0.16118,0.23549],"tcp_to_object_dist_end":0.31437,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```