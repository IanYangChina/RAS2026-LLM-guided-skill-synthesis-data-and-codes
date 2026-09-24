## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | -0.2030 | 0.13 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1611 | 0.13 | ❌ rejected |
| 12 | approach → align → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | -0.1833 | 0.15 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.1467 | 0.17 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.2668 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.48269722766055606, 0.048727684333792556, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.48269722766055606, 0.048727684333792556, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=-0.203) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: grasp_success
  anchor: object
  weight: 0.1
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: place_accuracy
  target_entity: object
  weight: 0.6
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
    tolerance: 0.01
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_grasp
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: grasp_success
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
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: abort
  subtask_id: lift_clearance
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: place_descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
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
  subtask_id: place_accuracy
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=1.0
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.203
- **task_score** (E): 0.127
- **fitness_score**: 0.147  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 0.00 | 1.00 | 0.1482 |
| descend_to_grasp | 1.00 | 1.00 | 0.0005 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.67 | 1.00 | 0.0569 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.433, -0.002, 0.173) | (0.522, -0.001, 0.030)→(0.485, -0.004, 0.016) | 0.287→0.311 | 1.00 / 5.000 | 91152.095 | 1495.947 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.433, -0.002, 0.173)→(0.433, -0.002, 0.173) | (0.485, -0.004, 0.016)→(0.485, -0.004, 0.016) | 0.311→0.311 | 1.00 / 5.000 | 313.626 | 261.500 |
| grasp_object | grasp | 1.00 / step_budget | (0.433, 0.001, 0.172)→(0.433, 0.001, 0.172) | (0.485, -0.004, 0.016)→(0.485, -0.004, 0.016) | 0.311→0.311 | 1.00 / 9.000 | 69.694 | 365.085 |
| lift_object | lift | 0.67 / step_budget | (0.433, 0.001, 0.172)→(0.472, -0.016, 0.194) | (0.485, -0.004, 0.016)→(0.485, -0.004, 0.016) | 0.311→0.311 | 1.00 / 9.667 | 154.959 | 703.783 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.148
- phase_score: 0.039
- phase_breakdown.reach_goal_score: 0.000
- phase_breakdown.reach_pre_grasp_score: 0.127
- phase_breakdown.lift_clearance_score: 0.224
- phase_breakdown.place_accuracy_score: 0.000
- phase_breakdown.grasp_success_score: 0.040
- grasp_place_fitness: 0.164

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.164
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.148
- **Median Q (composite search score)**: -0.196
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.438


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
{"anchors":[{"name":"object","value":[0.58187,0.22885,0.23048]},{"name":"goal","value":[0.4827,0.04873,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.56098,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.19837,"approach_above_object.arc_height_approach":0.17786,"descend_to_grasp.descend_force_threshold":10.92432,"descend_to_grasp.descend_z_offset":0.00315,"lift_object.lift_height":0.17418,"place_descend.place_force_threshold":14.91751,"place_descend.place_z_offset":0.00174,"transport_to_goal.arc_height_transport":0.16952,"transport_to_goal.transport_height":0.19929},"optimized_scores":{"best_composite_score":-0.19561,"best_fitness_score":0.15439,"best_task_score":0.12387},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62522,0.0255,-0.00046],"force_p95":230.64114,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1322.42565,"mean_force":225.40953,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38444,0.02367,0.12393]},{"body_a":"world","body_b":"link6","contact_count":12.0,"contact_point_centroid":[0.62008,0.04155,-7e-05],"force_p95":301.83411,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":315.14718,"mean_force":124.4343,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39832,0.03905,0.15925]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61875,0.04065,-0.00023],"force_p95":313.51589,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.51589,"mean_force":313.51589,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39675,0.03842,0.15861]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61934,0.0413,-0.00013],"force_p95":79.87397,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.43063,"mean_force":73.29007,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39708,0.03879,0.15842]},{"body_a":"grasp_target","body_b":"hand","contact_count":57.0,"contact_point_centroid":[0.45888,0.0395,0.04166],"force_p95":3.75225,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.89681,"mean_force":1.5093,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37538,0.01191,0.06356]},{"body_a":"grasp_target","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.48037,0.0297,0.01821],"force_p95":2.77936,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.71562,"mean_force":0.64561,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.37036,0.01199,0.06831]},{"body_a":"world","body_b":"grasp_target","contact_count":3837.0,"contact_point_centroid":[0.44696,0.04918,-0.0022],"force_p95":0.19592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.30043,"mean_force":0.14504,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39738,0.02232,0.13422]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.44094,0.04918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39675,0.03842,0.15861]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44094,0.04918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39708,0.03879,0.15842]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.44094,0.04918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41719,0.0438,0.17005]},{"body_a":"left_finger","body_b":"right_finger","contact_count":754.0,"contact_point_centroid":[0.39908,0.03879,0.15708],"force_p95":0.01323,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01092,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39714,0.03877,0.15829]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1923.0,"contact_point_centroid":[0.41918,0.04382,0.16881],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01046,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41719,0.0438,0.17006]},{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.52187,0.01559,-0.00285],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.36676,0.01167,0.0526]}],"total_contact_groups":13},"final_pose_error":0.0101,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44094,0.04918,0.01602],"final_tcp_position":[0.43505,0.04806,0.18207],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1322.42565,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44094,0.04918,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31327,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":218.33311,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4852.0,"raw_peak_contact_force":1322.42565,"subtask_id":"reach_pre_grasp","tcp_end":[0.39675,0.03842,0.15861],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14967,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.44094,0.04918,0.01602],"object_pos_start":[0.44094,0.04918,0.01602],"object_to_goal_dist_end":0.31327,"object_to_goal_dist_start":0.31327,"object_z_max":0.01602,"peak_contact_force":416.36025,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":313.51589,"subtask_id":"grasp_success","tcp_end":[0.39676,0.03842,0.1587],"tcp_start":[0.39675,0.03842,0.15861],"tcp_to_object_dist_end":0.14975,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44094,0.04918,0.01602],"object_pos_start":[0.44094,0.04918,0.01602],"object_to_goal_dist_end":0.31327,"object_to_goal_dist_start":0.31327,"object_z_max":0.01602,"peak_contact_force":69.71278,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3504.0,"raw_peak_contact_force":225.43063,"tcp_end":[0.39714,0.03876,0.15828],"tcp_start":[0.39714,0.03876,0.15828],"tcp_to_object_dist_end":0.14921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":451.0,"n_steps_budget":600.0,"object_pos_end":[0.44094,0.04918,0.01602],"object_pos_start":[0.44094,0.04918,0.01602],"object_to_goal_dist_end":0.31327,"object_to_goal_dist_start":0.31327,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3739.0,"raw_peak_contact_force":315.14718,"subtask_id":"lift_clearance","tcp_end":[0.43505,0.04806,0.18207],"tcp_start":[0.39714,0.03876,0.15828],"tcp_to_object_dist_end":0.16616,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.43902,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.18166,"approach_above_object.arc_height_approach":0.21661,"descend_to_grasp.descend_force_threshold":8.71161,"descend_to_grasp.descend_z_offset":0.01259,"lift_object.lift_height":0.18373,"place_descend.place_force_threshold":9.05782,"place_descend.place_z_offset":-0.00556,"transport_to_goal.arc_height_transport":0.20363,"transport_to_goal.transport_height":0.19283},"optimized_scores":{"best_composite_score":-0.22712,"best_fitness_score":0.12288,"best_task_score":0.10771},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.64042,0.00247,-0.00046],"force_p95":357.77038,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1459.25182,"mean_force":221.75975,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.4236,-4e-05,0.16057]},{"body_a":"world","body_b":"link6","contact_count":288.0,"contact_point_centroid":[0.68036,0.00919,-0.00017],"force_p95":463.00652,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1062.85362,"mean_force":310.53208,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47215,-0.0152,0.18205]},{"body_a":"world","body_b":"link6","contact_count":544.0,"contact_point_centroid":[0.64841,0.00034,-0.00014],"force_p95":88.50416,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":752.83119,"mean_force":75.04585,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45681,-0.00788,0.20407]},{"body_a":"world","body_b":"link5","contact_count":66.0,"contact_point_centroid":[0.62971,0.115,-0.00054],"force_p95":392.98806,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":556.56564,"mean_force":327.67953,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4886,-0.0197,0.19152]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53576,0.00681,-0.00361],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":470.79794,"mean_force":22.41895,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38216,0.00209,0.0494]},{"body_a":"link5","body_b":"hand","contact_count":351.0,"contact_point_centroid":[0.51097,0.07622,0.14146],"force_p95":154.37501,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":331.44961,"mean_force":85.51143,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47996,-0.01834,0.18348]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64753,-0.00014,-0.00024],"force_p95":248.72566,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":248.72566,"mean_force":248.72566,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45693,-0.00826,0.2048]},{"body_a":"grasp_target","body_b":"link7","contact_count":150.0,"contact_point_centroid":[0.50687,-0.02349,0.04006],"force_p95":3.34311,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.82686,"mean_force":0.91753,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39436,0.00225,0.09165]},{"body_a":"grasp_target","body_b":"hand","contact_count":131.0,"contact_point_centroid":[0.49667,-0.02902,0.05083],"force_p95":2.45127,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.24005,"mean_force":0.97715,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39331,0.00224,0.08824]},{"body_a":"world","body_b":"grasp_target","contact_count":3630.0,"contact_point_centroid":[0.50468,-0.02199,-0.0022],"force_p95":0.27128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.304,"mean_force":0.15297,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.43594,-5e-05,0.17154]},{"body_a":"grasp_target","body_b":"link6","contact_count":126.0,"contact_point_centroid":[0.54222,-0.00729,0.02562],"force_p95":0.6489,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.92976,"mean_force":0.37572,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39185,0.00225,0.09456]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49839,-0.02237,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45693,-0.00826,0.2048]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49839,-0.02237,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45681,-0.00788,0.20408]},{"body_a":"world","body_b":"grasp_target","contact_count":1440.0,"contact_point_centroid":[0.49839,-0.02237,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47364,-0.01535,0.18407]},{"body_a":"left_finger","body_b":"right_finger","contact_count":756.0,"contact_point_centroid":[0.45846,-0.00787,0.20226],"force_p95":0.01299,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01089,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45681,-0.00788,0.20398]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1563.0,"contact_point_centroid":[0.4754,-0.01523,0.18239],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.01028,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47362,-0.01537,0.18395]}],"total_contact_groups":16},"final_pose_error":0.01515,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49839,-0.02237,0.01602],"final_tcp_position":[0.48686,-0.02134,0.18999],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1459.25182,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49839,-0.02237,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33425,"object_to_goal_dist_start":0.31446,"object_z_max":0.03039,"peak_contact_force":356.93833,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4944.0,"raw_peak_contact_force":1459.25182,"subtask_id":"reach_pre_grasp","tcp_end":[0.45693,-0.00826,0.2048],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19379,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49839,-0.02237,0.01602],"object_pos_start":[0.49839,-0.02237,0.01602],"object_to_goal_dist_end":0.33425,"object_to_goal_dist_start":0.33425,"object_z_max":0.01602,"peak_contact_force":302.25722,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":248.72566,"subtask_id":"grasp_success","tcp_end":[0.45689,-0.00822,0.20489],"tcp_start":[0.45693,-0.00826,0.2048],"tcp_to_object_dist_end":0.19389,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49839,-0.02237,0.01602],"object_pos_start":[0.49839,-0.02237,0.01602],"object_to_goal_dist_end":0.33425,"object_to_goal_dist_start":0.33425,"object_z_max":0.01602,"peak_contact_force":70.88071,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3500.0,"raw_peak_contact_force":752.83119,"tcp_end":[0.45681,-0.00789,0.20398],"tcp_start":[0.45681,-0.00788,0.20398],"tcp_to_object_dist_end":0.19305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":360.0,"n_steps_budget":600.0,"object_pos_end":[0.49839,-0.02237,0.01602],"object_pos_start":[0.49839,-0.02237,0.01602],"object_to_goal_dist_end":0.33425,"object_to_goal_dist_start":0.33425,"object_z_max":0.01602,"peak_contact_force":332.56081,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3708.0,"raw_peak_contact_force":1062.85362,"subtask_id":"lift_clearance","tcp_end":[0.48686,-0.02134,0.18999],"tcp_start":[0.45681,-0.00789,0.20398],"tcp_to_object_dist_end":0.17435,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63284,0.16493,0.17692]},{"name":"goal","value":[0.5456,-0.02923,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.21951,"average_mean_iterations":52.70732,"average_solve_count":41.0,"average_success_count":32.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.16062,"approach_above_object.arc_height_approach":0.13612,"descend_to_grasp.descend_force_threshold":9.21091,"descend_to_grasp.descend_z_offset":0.00778,"lift_object.lift_height":0.16317,"place_descend.place_force_threshold":11.52315,"place_descend.place_z_offset":-0.01434,"transport_to_goal.arc_height_transport":0.16336,"transport_to_goal.transport_height":0.18494},"optimized_scores":{"best_composite_score":-0.18631,"best_fitness_score":0.16369,"best_task_score":0.14849},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":851.0,"contact_point_centroid":[0.64738,-0.01635,-0.00046],"force_p95":445.37079,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1706.1639,"mean_force":261.36899,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.43283,-0.01916,0.16611]},{"body_a":"world","body_b":"link6","contact_count":81.0,"contact_point_centroid":[0.68551,-0.0445,-6e-05],"force_p95":580.94995,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":733.34814,"mean_force":285.4242,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45671,-0.03301,0.15337]},{"body_a":"link5","body_b":"hand","contact_count":80.0,"contact_point_centroid":[0.52667,0.0453,0.12853],"force_p95":348.4879,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":717.70114,"mean_force":140.03304,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46974,-0.04989,0.15605]},{"body_a":"world","body_b":"link5","contact_count":16.0,"contact_point_centroid":[0.66242,0.0588,-0.00096],"force_p95":329.78174,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":384.73444,"mean_force":217.62089,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47363,-0.06261,0.15627]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67547,-0.04628,-3e-05],"force_p95":222.25962,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.25962,"mean_force":222.25962,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.44574,-0.03554,0.15529]},{"body_a":"world","body_b":"link6","contact_count":525.0,"contact_point_centroid":[0.67497,-0.04398,-0.00013],"force_p95":68.56791,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.99177,"mean_force":69.02538,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44363,-0.02909,0.15234]},{"body_a":"grasp_target","body_b":"link6","contact_count":119.0,"contact_point_centroid":[0.54752,-0.03314,0.03339],"force_p95":1.02744,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.52003,"mean_force":0.58897,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39596,-0.00932,0.09977]},{"body_a":"grasp_target","body_b":"link7","contact_count":150.0,"contact_point_centroid":[0.51923,-0.0311,0.03861],"force_p95":3.29427,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.32972,"mean_force":0.83195,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39908,-0.00934,0.09876]},{"body_a":"grasp_target","body_b":"hand","contact_count":103.0,"contact_point_centroid":[0.50089,-0.03428,0.04974],"force_p95":2.48345,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.44317,"mean_force":0.95343,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.39592,-0.00904,0.0878]},{"body_a":"world","body_b":"grasp_target","contact_count":3666.0,"contact_point_centroid":[0.51929,-0.03794,-0.00212],"force_p95":0.21421,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.15142,"mean_force":0.14812,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.44533,-0.01876,0.17626]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.51486,-0.0401,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.44574,-0.03554,0.15529]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.51486,-0.0401,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44358,-0.02906,0.15237]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.51486,-0.0401,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46236,-0.04149,0.15683]},{"body_a":"left_finger","body_b":"right_finger","contact_count":770.0,"contact_point_centroid":[0.44574,-0.02921,0.15116],"force_p95":0.01299,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01071,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44366,-0.02915,0.15234]},{"body_a":"left_finger","body_b":"right_finger","contact_count":826.0,"contact_point_centroid":[0.46453,-0.04175,0.15592],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01264,"mean_force":0.01035,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46259,-0.0417,0.15701]},{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.53987,-0.00559,-0.00341],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.38516,-0.0086,0.05266]}],"total_contact_groups":16},"final_pose_error":0.05051,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.51486,-0.0401,0.01602],"final_tcp_position":[0.49469,-0.07592,0.20854],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":272881.01351,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51486,-0.0401,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28609,"object_to_goal_dist_start":0.25864,"object_z_max":0.03198,"peak_contact_force":272881.01351,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4908.0,"raw_peak_contact_force":1706.1639,"subtask_id":"reach_pre_grasp","tcp_end":[0.44574,-0.03554,0.15529],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15555,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51486,-0.0401,0.01602],"object_pos_start":[0.51486,-0.0401,0.01602],"object_to_goal_dist_end":0.28609,"object_to_goal_dist_start":0.28609,"object_z_max":0.01602,"peak_contact_force":222.25962,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":222.25962,"subtask_id":"grasp_success","tcp_end":[0.44462,-0.03486,0.15526],"tcp_start":[0.44574,-0.03554,0.15529],"tcp_to_object_dist_end":0.15604,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51486,-0.0401,0.01602],"object_pos_start":[0.51486,-0.0401,0.01602],"object_to_goal_dist_end":0.28609,"object_to_goal_dist_start":0.28609,"object_z_max":0.01602,"peak_contact_force":68.48811,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3495.0,"raw_peak_contact_force":116.99177,"tcp_end":[0.44366,-0.02915,0.15234],"tcp_start":[0.44366,-0.02915,0.15234],"tcp_to_object_dist_end":0.15418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":192.0,"n_steps_budget":600.0,"object_pos_end":[0.51486,-0.0401,0.01602],"object_pos_start":[0.51486,-0.0401,0.01602],"object_to_goal_dist_end":0.28609,"object_to_goal_dist_start":0.28609,"object_z_max":0.01602,"peak_contact_force":132.19488,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1771.0,"raw_peak_contact_force":733.34814,"subtask_id":"lift_clearance","tcp_end":[0.49469,-0.07592,0.20854],"tcp_start":[0.44366,-0.02915,0.15234],"tcp_to_object_dist_end":0.19686,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```