## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1611 | 0.13 | ❌ rejected |
| 12 | approach → align → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | -0.1833 | 0.15 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.1467 | 0.17 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.2668 | 0.15 | ❌ rejected |
| 9 | retract → approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.2039 | 0.15 | ❌ rejected |

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

## Current Skill (Q=-0.161) — your mutation base

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

- **Composite score**: -0.161
- **task_score** (E): 0.133
- **fitness_score**: 0.139  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.0415 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.67 | 1.00 | 0.0739 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.454, -0.031, 0.188)→(0.457, -0.060, 0.180) | (0.522, -0.001, 0.030)→(0.483, -0.003, 0.016) | 0.287→0.311 | 1.00 / 6.000 | 338.315 | 1518.076 |
| descend_1 | descend | 1.00 / force_exceeded | (0.457, -0.060, 0.180)→(0.457, -0.060, 0.180) | (0.483, -0.003, 0.016)→(0.483, -0.003, 0.016) | 0.311→0.311 | 1.00 / 6.000 | 199.385 | 199.385 |
| grasp_1 | grasp | 1.00 / step_budget | (0.457, -0.060, 0.179)→(0.457, -0.060, 0.179) | (0.483, -0.003, 0.016)→(0.483, -0.003, 0.016) | 0.311→0.311 | 1.00 / 9.667 | 91047.954 | 125.335 |
| lift_1 | lift | 0.67 / step_budget | (0.457, -0.060, 0.179)→(0.487, -0.018, 0.183) | (0.483, -0.003, 0.016)→(0.484, 0.004, 0.017) | 0.311→0.305 | 1.00 / 8.000 | 26.798 | 320.546 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.169
- phase_score: 0.048
- phase_breakdown.reach_goal_score: 0.000
- phase_breakdown.reach_pre_grasp_score: 0.053
- phase_breakdown.lift_clearance_score: 0.402
- phase_breakdown.place_accuracy_score: 0.000
- phase_breakdown.grasp_success_score: 0.025
- grasp_place_fitness: 0.160

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.160
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.169
- **Median Q (composite search score)**: -0.172
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.56098,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08334,"approach_1.approach_speed":0.05081,"descend_1.descend_force_threshold":10.05707,"descend_1.descend_z_offset":0.02051,"lift_1.lift_height":0.2346,"place_descend_1.place_force_threshold":10.62093,"place_descend_1.place_z_offset":0.00698,"transport_1.transport_height":0.24196},"optimized_scores":{"best_composite_score":-0.17212,"best_fitness_score":0.12788,"best_task_score":0.12467},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":2623.0,"contact_point_centroid":[0.61031,0.02811,-0.00032],"force_p95":450.491,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1704.95583,"mean_force":265.8202,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40876,0.02817,0.18148]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62647,0.06194,-0.00027],"force_p95":157.24682,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":157.24682,"mean_force":157.24682,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44714,0.0632,0.21727]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.62792,0.0619,-0.0001],"force_p95":121.16305,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.47098,"mean_force":99.81569,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44704,0.06326,0.21633]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62779,0.06195,-0.00013],"force_p95":76.95979,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.09832,"mean_force":73.12056,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44705,0.06329,0.21639]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.46245,0.03729,0.03959],"force_p95":3.70157,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.94044,"mean_force":1.89492,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3812,0.0022,0.05522]},{"body_a":"grasp_target","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.48319,0.02933,0.01427],"force_p95":1.87418,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.91454,"mean_force":0.71914,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37098,0.00213,0.0552]},{"body_a":"world","body_b":"grasp_target","contact_count":10949.0,"contact_point_centroid":[0.44447,0.04945,-0.00204],"force_p95":0.12278,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.34959,"mean_force":0.12897,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41253,0.02727,0.18298]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.44271,0.04948,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44714,0.0632,0.21727]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44271,0.04948,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44705,0.06329,0.21639]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.44271,0.04948,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44365,0.05647,0.22829]},{"body_a":"left_finger","body_b":"right_finger","contact_count":743.0,"contact_point_centroid":[0.4486,0.06332,0.21493],"force_p95":0.01359,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01107,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44706,0.06329,0.2163]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1195.0,"contact_point_centroid":[0.44513,0.05651,0.22654],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01055,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44366,0.05648,0.22827]},{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.52462,0.00724,-0.00341],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36998,0.00211,0.05274]}],"total_contact_groups":13},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44271,0.04948,0.01602],"final_tcp_position":[0.4417,0.05099,0.24082],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1704.95583,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":2755.0,"n_steps_budget":1000.0,"object_pos_end":[0.44271,0.04948,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31231,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":372.79819,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13655.0,"raw_peak_contact_force":1704.95583,"subtask_id":"reach_pre_grasp","tcp_end":[0.44714,0.0632,0.21727],"tcp_start":[0.44794,0.04699,0.2167],"tcp_to_object_dist_end":0.20177,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.44271,0.04948,0.01602],"object_pos_start":[0.44271,0.04948,0.01602],"object_to_goal_dist_end":0.31231,"object_to_goal_dist_start":0.31231,"object_z_max":0.01602,"peak_contact_force":157.24682,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":157.24682,"subtask_id":"grasp_success","tcp_end":[0.44715,0.06319,0.21724],"tcp_start":[0.44714,0.0632,0.21727],"tcp_to_object_dist_end":0.20174,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44271,0.04948,0.01602],"object_pos_start":[0.44271,0.04948,0.01602],"object_to_goal_dist_end":0.31231,"object_to_goal_dist_start":0.31231,"object_z_max":0.01602,"peak_contact_force":71.78207,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3493.0,"raw_peak_contact_force":117.09832,"tcp_end":[0.44706,0.06328,0.2163],"tcp_start":[0.44706,0.06328,0.2163],"tcp_to_object_dist_end":0.2008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":283.0,"n_steps_budget":600.0,"object_pos_end":[0.44271,0.04948,0.01602],"object_pos_start":[0.44271,0.04948,0.01602],"object_to_goal_dist_end":0.31231,"object_to_goal_dist_start":0.31231,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2333.0,"raw_peak_contact_force":121.47098,"subtask_id":"lift_clearance","tcp_end":[0.4417,0.05099,0.24082],"tcp_start":[0.44706,0.06328,0.2163],"tcp_to_object_dist_end":0.22481,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.2716,"average_solve_count":81.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13187,"approach_1.approach_speed":0.09883,"descend_1.descend_force_threshold":8.37319,"descend_1.descend_z_offset":0.03103,"lift_1.lift_height":0.17964,"place_descend_1.place_force_threshold":5.94793,"place_descend_1.place_z_offset":0.00308,"transport_1.transport_height":0.14577},"optimized_scores":{"best_composite_score":-0.17154,"best_fitness_score":0.12846,"best_task_score":0.10614},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":2564.0,"contact_point_centroid":[0.62792,-0.01607,-0.00031],"force_p95":444.84084,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1442.28095,"mean_force":269.48137,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43067,-0.02897,0.1887]},{"body_a":"world","body_b":"link6","contact_count":117.0,"contact_point_centroid":[0.67249,-0.00919,-2e-05],"force_p95":338.25359,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":537.85498,"mean_force":121.82405,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46893,-0.08766,0.17006]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53308,0.00146,-0.0034],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":468.5725,"mean_force":22.31298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37964,-0.00239,0.0503]},{"body_a":"link5","body_b":"hand","contact_count":690.0,"contact_point_centroid":[0.51586,0.03237,0.16063],"force_p95":133.32059,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.96903,"mean_force":84.69128,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47903,-0.07849,0.16194]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.65964,-0.03365,-0.00015],"force_p95":188.417,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":188.417,"mean_force":188.417,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46215,-0.09858,0.17682]},{"body_a":"link5","body_b":"hand","contact_count":558.0,"contact_point_centroid":[0.50477,0.01136,0.19099],"force_p95":139.81255,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":162.24377,"mean_force":70.26024,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45755,-0.08241,0.20021]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.66051,-0.03418,-0.00013],"force_p95":75.54566,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.86895,"mean_force":71.32802,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46214,-0.09906,0.1759]},{"body_a":"link5","body_b":"hand","contact_count":558.0,"contact_point_centroid":[0.50193,0.00175,0.18174],"force_p95":30.67185,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.87594,"mean_force":5.96552,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46214,-0.09905,0.17591]},{"body_a":"grasp_target","body_b":"link7","contact_count":228.0,"contact_point_centroid":[0.51841,-0.01804,0.03397],"force_p95":3.22457,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.88503,"mean_force":0.56226,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3943,-0.00264,0.10184]},{"body_a":"grasp_target","body_b":"link6","contact_count":98.0,"contact_point_centroid":[0.5409,-0.02491,0.02796],"force_p95":0.89112,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.88851,"mean_force":0.4741,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38696,-0.00246,0.08724]},{"body_a":"grasp_target","body_b":"hand","contact_count":103.0,"contact_point_centroid":[0.49427,-0.0282,0.04638],"force_p95":2.34816,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.29416,"mean_force":0.95284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38926,-0.00243,0.08084]},{"body_a":"world","body_b":"grasp_target","contact_count":10565.0,"contact_point_centroid":[0.50384,-0.0265,-0.00207],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.64164,"mean_force":0.13295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43476,-0.02864,0.19157]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50199,-0.02686,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46215,-0.09858,0.17682]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50199,-0.02686,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46214,-0.09906,0.1759]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.50199,-0.02686,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4836,-0.07623,0.15809]},{"body_a":"left_finger","body_b":"right_finger","contact_count":756.0,"contact_point_centroid":[0.4639,-0.09841,0.17439],"force_p95":0.01316,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01089,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46214,-0.09908,0.17581]}],"total_contact_groups":18},"final_pose_error":0.07432,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50199,-0.02686,0.01602],"final_tcp_position":[0.51772,-0.06804,0.13582],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273004.12084,"phases":[{"contact_detected":true,"contact_event_count":7.0,"n_steps":2706.0,"n_steps_budget":1000.0,"object_pos_end":[0.50199,-0.02686,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33644,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":380.36316,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14137.0,"raw_peak_contact_force":1442.28095,"subtask_id":"reach_pre_grasp","tcp_end":[0.46215,-0.09858,0.17682],"tcp_start":[0.46012,-0.03533,0.1959],"tcp_to_object_dist_end":0.18052,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50199,-0.02686,0.01602],"object_pos_start":[0.50199,-0.02686,0.01602],"object_to_goal_dist_end":0.33644,"object_to_goal_dist_start":0.33644,"object_z_max":0.01602,"peak_contact_force":188.417,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7.0,"raw_peak_contact_force":188.417,"subtask_id":"grasp_success","tcp_end":[0.46218,-0.09861,0.17682],"tcp_start":[0.46215,-0.09858,0.17682],"tcp_to_object_dist_end":0.18052,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50199,-0.02686,0.01602],"object_pos_start":[0.50199,-0.02686,0.01602],"object_to_goal_dist_end":0.33644,"object_to_goal_dist_start":0.33644,"object_z_max":0.01602,"peak_contact_force":273004.12084,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4064.0,"raw_peak_contact_force":93.86895,"tcp_end":[0.46214,-0.09909,0.17581],"tcp_start":[0.46214,-0.09909,0.17581],"tcp_to_object_dist_end":0.17982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50199,-0.02686,0.01602],"object_pos_start":[0.50199,-0.02686,0.01602],"object_to_goal_dist_end":0.33644,"object_to_goal_dist_start":0.33644,"object_z_max":0.01602,"peak_contact_force":80.01292,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5103.0,"raw_peak_contact_force":537.85498,"subtask_id":"lift_clearance","tcp_end":[0.51772,-0.06804,0.13582],"tcp_start":[0.46214,-0.09909,0.17581],"tcp_to_object_dist_end":0.12765,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.25287,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16471,"approach_1.approach_speed":0.25852,"descend_1.descend_force_threshold":7.21218,"descend_1.descend_z_offset":0.02157,"lift_1.lift_height":0.16518,"place_descend_1.place_force_threshold":6.44365,"place_descend_1.place_z_offset":-0.01046,"transport_1.transport_height":0.15472},"optimized_scores":{"best_composite_score":-0.13956,"best_fitness_score":0.16044,"best_task_score":0.16858},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":2466.0,"contact_point_centroid":[0.65232,-0.01614,-0.00029],"force_p95":403.04076,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1406.98989,"mean_force":252.54984,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44158,-0.07854,0.1542]},{"body_a":"link5","body_b":"hand","contact_count":608.0,"contact_point_centroid":[0.49513,-0.04631,0.19827],"force_p95":279.70142,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":585.33899,"mean_force":128.61126,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45411,-0.1327,0.1486]},{"body_a":"world","body_b":"link7","contact_count":73.0,"contact_point_centroid":[0.54221,-0.09552,-0.00114],"force_p95":430.96039,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":523.9615,"mean_force":187.33955,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43004,-0.11853,0.10277]},{"body_a":"world","body_b":"link6","contact_count":54.0,"contact_point_centroid":[0.67276,-0.02741,-2e-05],"force_p95":223.80324,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":302.31204,"mean_force":85.61798,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46362,-0.13764,0.14563]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.66937,-0.03455,-0.00016],"force_p95":252.49246,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.49246,"mean_force":252.49246,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46091,-0.1443,0.14668]},{"body_a":"link5","body_b":"hand","contact_count":124.0,"contact_point_centroid":[0.51114,-0.08252,0.20891],"force_p95":31.69143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.03802,"mean_force":11.39313,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46111,-0.14447,0.14618]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.67012,-0.03441,-0.00013],"force_p95":74.90473,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.28842,"mean_force":69.63084,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46119,-0.14449,0.14583]},{"body_a":"link5","body_b":"hand","contact_count":508.0,"contact_point_centroid":[0.52442,-0.045,0.21135],"force_p95":110.97249,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.12609,"mean_force":76.28536,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47571,-0.10621,0.14696]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.51116,-0.08232,0.20913],"force_p95":89.78879,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.78879,"mean_force":89.78879,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46091,-0.1443,0.14668]},{"body_a":"grasp_target","body_b":"link6","contact_count":136.0,"contact_point_centroid":[0.54434,-0.01575,0.02719],"force_p95":0.82644,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.42201,"mean_force":0.47617,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39187,-0.004,0.09618]},{"body_a":"grasp_target","body_b":"link7","contact_count":180.0,"contact_point_centroid":[0.51238,-0.03038,0.04095],"force_p95":2.92916,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.09238,"mean_force":0.70092,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39571,-0.00414,0.09905]},{"body_a":"world","body_b":"grasp_target","contact_count":10251.0,"contact_point_centroid":[0.50747,-0.0301,-0.00206],"force_p95":0.12631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.26048,"mean_force":0.13276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4462,-0.07814,0.1581]},{"body_a":"grasp_target","body_b":"hand","contact_count":127.0,"contact_point_centroid":[0.49881,-0.03389,0.05032],"force_p95":2.33595,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.20271,"mean_force":0.96842,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39226,-0.0039,0.08869]},{"body_a":"grasp_target","body_b":"hand","contact_count":353.0,"contact_point_centroid":[0.53644,-0.03352,0.04],"force_p95":0.20803,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39209,"mean_force":0.11866,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49054,-0.06665,0.15928]},{"body_a":"world","body_b":"grasp_target","contact_count":2311.0,"contact_point_centroid":[0.50578,-0.02492,-0.00241],"force_p95":0.26035,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39051,"mean_force":0.15403,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47834,-0.09876,0.15011]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50519,-0.03025,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46091,-0.1443,0.14668]}],"total_contact_groups":19},"final_pose_error":0.01105,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.50744,-0.01128,0.02027],"final_tcp_position":[0.50109,-0.03621,0.17285],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273004.12132,"phases":[{"contact_detected":true,"contact_event_count":6.0,"n_steps":2657.0,"n_steps_budget":1000.0,"object_pos_end":[0.50519,-0.03025,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28333,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":261.78353,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13841.0,"raw_peak_contact_force":1406.98989,"subtask_id":"reach_pre_grasp","tcp_end":[0.46091,-0.1443,0.14668],"tcp_start":[0.45261,-0.10331,0.15198],"tcp_to_object_dist_end":0.179,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50519,-0.03025,0.01602],"object_pos_start":[0.50519,-0.03025,0.01602],"object_to_goal_dist_end":0.28333,"object_to_goal_dist_start":0.28333,"object_z_max":0.01602,"peak_contact_force":252.49246,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":252.49246,"subtask_id":"grasp_success","tcp_end":[0.461,-0.14436,0.14668],"tcp_start":[0.46091,-0.1443,0.14668],"tcp_to_object_dist_end":0.17902,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50519,-0.03025,0.01602],"object_pos_start":[0.50519,-0.03025,0.01602],"object_to_goal_dist_end":0.28333,"object_to_goal_dist_start":0.28333,"object_z_max":0.01602,"peak_contact_force":67.96033,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3627.0,"raw_peak_contact_force":165.03802,"tcp_end":[0.46122,-0.14448,0.14569],"tcp_start":[0.46122,-0.14449,0.14569],"tcp_to_object_dist_end":0.17832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":722.0,"n_steps_budget":810.0,"object_pos_end":[0.50744,-0.01128,0.02027],"object_pos_start":[0.50519,-0.03025,0.01602],"object_to_goal_dist_end":0.26705,"object_to_goal_dist_start":0.28333,"object_z_max":0.02027,"peak_contact_force":0.25939,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6374.0,"raw_peak_contact_force":302.31204,"subtask_id":"lift_clearance","tcp_end":[0.50109,-0.03621,0.17285],"tcp_start":[0.46122,-0.14448,0.14569],"tcp_to_object_dist_end":0.15474,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```