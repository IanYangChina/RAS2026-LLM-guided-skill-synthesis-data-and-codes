## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1419 | 0.31 | ✅ accepted |
| 2 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ❌ rejected |
| 1 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ❌ rejected |
| 0 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.142) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_subtask
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: place_subtask
  target_entity: object
  weight: 0.8
phases:
- id: approach_obj
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
    - 0.0
    tolerance: 0.02
  parameters:
    pre_grasp_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_subtask
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
- id: grasp_phase
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
    tolerance: 0.02
  parameters:
    grasp_time:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_obj
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
    - 0.0
    tolerance: 0.02
  parameters:
    lift_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_goal
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
    - 0.0
    tolerance: 0.02
  parameters:
    approach_goal_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_place
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
    tolerance: 0.02
  subtask_id: place_subtask
- id: release_phase
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
    tolerance: 0.02
  parameters:
    release_time:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_arm
  type: retract
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_obj** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - pre_grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_phase** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - grasp_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_obj** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - lift_z_offset: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - approach_goal_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings: none
- **release_phase** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
- **retract_arm** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.142
- **task_score** (E): 0.306
- **fitness_score**: 0.622  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1749 |
| descend_grasp | 1.00 | 1.00 | 0.0818 |
| grasp_phase | 1.00 | 1.00 | 0.0126 |
| lift_obj | 1.00 | 1.00 | 0.1180 |
| approach_goal | 1.00 | 1.00 | 0.2686 |
| descend_place | 1.00 | 1.00 | 0.0883 |
| release_phase | 1.00 | 1.00 | 0.0199 |
| retract_arm | 1.00 | 1.00 | 0.0429 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.000, 0.131) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.515, -0.000, 0.131)→(0.516, -0.001, 0.050) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_phase | grasp | 1.00 / step_budget | (0.516, -0.001, 0.050)→(0.508, -0.001, 0.040) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 45.000 | 0.142 | 0.172 |
| lift_obj | lift | 1.00 / step_budget | (0.508, -0.001, 0.040)→(0.517, -0.001, 0.158) | (0.522, -0.001, 0.026)→(0.529, -0.001, 0.141) | 0.290→0.235 | 1.00 / 39.000 | 0.080 | 0.509 |
| approach_goal | approach | 1.00 / step_budget | (0.517, -0.001, 0.158)→(0.602, 0.197, 0.312) | (0.529, -0.001, 0.141)→(0.613, 0.201, 0.291) | 0.235→0.086 | 1.00 / 38.000 | 55983.965 | 0.159 |
| descend_place | descend | 1.00 / step_budget | (0.602, 0.197, 0.312)→(0.604, 0.204, 0.224) | (0.613, 0.201, 0.291)→(0.613, 0.208, 0.200) | 0.086→0.007 | 1.00 / 33.667 | 0.080 | 0.249 |
| release_phase | release | 1.00 / step_budget | (0.604, 0.204, 0.224)→(0.599, 0.202, 0.243) | (0.613, 0.208, 0.200)→(0.602, 0.204, 0.019) | 0.007→0.186 | 1.00 / 2.667 | 0.257 | 1.685 |
| retract_arm | retract | 1.00 / step_budget | (0.599, 0.202, 0.243)→(0.604, 0.205, 0.286) | (0.602, 0.204, 0.019)→(0.597, 0.197, 0.026) | 0.186→0.180 | 1.00 / 3.333 | 0.164 | 0.279 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.367
- phase_score: 0.680
- phase_breakdown.place_subtask_score: 0.673
- phase_breakdown.approach_subtask_score: 0.707
- grasp_place_fitness: 0.648

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.648
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.367
- **Median Q (composite search score)**: 0.139
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.340


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7602,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.1241,"approach_obj.pre_grasp_z_offset":0.05463,"descend_grasp.grasp_z_offset":0.02353,"grasp_phase.grasp_time":0.73066,"lift_obj.lift_z_offset":0.1318,"release_phase.release_time":0.80712},"optimized_scores":{"best_composite_score":0.11853,"best_fitness_score":0.59853,"best_task_score":0.25402},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.57107,0.22067,-0.01173],"force_p95":1.64332,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73971,"mean_force":0.69464,"phase_index":6.0,"phase_name":"release_phase","phase_type":"release","tcp_position_centroid":[0.57365,0.22395,0.26397]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.48037,0.04713,-0.00141],"force_p95":0.43341,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51465,"mean_force":0.09151,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.46879,0.04713,0.03974]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5491.0,"contact_point_centroid":[0.47175,0.06646,0.09009],"force_p95":0.08731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.317,"mean_force":0.06096,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47194,0.04723,0.08755]},{"body_a":"world","body_b":"grasp_target","contact_count":613.0,"contact_point_centroid":[0.56553,0.21931,-0.00242],"force_p95":0.21236,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30564,"mean_force":0.12227,"phase_index":7.0,"phase_name":"retract_arm","phase_type":"retract","tcp_position_centroid":[0.5757,0.22546,0.29118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6873.0,"contact_point_centroid":[0.47377,0.02831,0.08882],"force_p95":0.08444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2869,"mean_force":0.05052,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47193,0.04723,0.08739]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1051.0,"contact_point_centroid":[0.57311,0.24398,0.24852],"force_p95":0.08474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24955,"mean_force":0.05242,"phase_index":6.0,"phase_name":"release_phase","phase_type":"release","tcp_position_centroid":[0.57637,0.22517,0.24466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2722.0,"contact_point_centroid":[0.57316,0.24182,0.29982],"force_p95":0.0873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2299,"mean_force":0.05979,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57658,0.22304,0.296]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.58513,0.20789,0.24501],"force_p95":0.08392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22845,"mean_force":0.05102,"phase_index":6.0,"phase_name":"release_phase","phase_type":"release","tcp_position_centroid":[0.57635,0.22517,0.24463]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04871,-0.00212],"force_p95":0.15562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20504,"mean_force":0.1314,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.47092,0.04737,0.03945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3067.0,"contact_point_centroid":[0.5849,0.20567,0.29788],"force_p95":0.08493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18625,"mean_force":0.055,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57655,0.22299,0.29693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5262.0,"contact_point_centroid":[0.47124,0.02823,0.03947],"force_p95":0.0737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18133,"mean_force":0.04137,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46972,0.04725,0.03822]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18932.0,"contact_point_centroid":[0.53059,0.11688,0.23873],"force_p95":0.08041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14918,"mean_force":0.05125,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52566,0.13517,0.2375]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.48986,0.02091,0.20264]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15905.0,"contact_point_centroid":[0.52333,0.15488,0.24171],"force_p95":0.08882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13754,"mean_force":0.05986,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52616,0.13604,0.23851]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47753,0.04605,0.06621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4204.0,"contact_point_centroid":[0.46949,0.06657,0.04063],"force_p95":0.08847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09404,"mean_force":0.05202,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46972,0.04725,0.03823]}],"total_contact_groups":16},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56364,0.21804,0.02603],"final_tcp_position":[0.57827,0.22703,0.31095],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.73971,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.48081,0.04301,0.10322],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47771,0.04802,0.04648],"tcp_start":[0.48081,0.04301,0.10322],"tcp_to_object_dist_end":0.02107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04803,0.02559],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29071,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15362,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11266.0,"raw_peak_contact_force":0.20504,"tcp_end":[0.46969,0.04725,0.03819],"tcp_start":[0.47771,0.04802,0.04648],"tcp_to_object_dist_end":0.01814,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":323.0,"n_steps_budget":750.0,"object_pos_end":[0.4901,0.04855,0.1236],"object_pos_start":[0.48271,0.04803,0.02559],"object_to_goal_dist_end":0.22882,"object_to_goal_dist_start":0.29071,"object_z_max":0.12333,"peak_contact_force":0.08514,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12442.0,"raw_peak_contact_force":0.51465,"tcp_end":[0.47746,0.04756,0.13837],"tcp_start":[0.46969,0.04725,0.03819],"tcp_to_object_dist_end":0.01947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.58734,0.22536,0.31842],"object_pos_start":[0.4901,0.04855,0.1236],"object_to_goal_dist_end":0.08818,"object_to_goal_dist_start":0.22882,"object_z_max":0.31825,"peak_contact_force":0.08083,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34837.0,"raw_peak_contact_force":0.14918,"tcp_end":[0.57571,0.22054,0.33774],"tcp_start":[0.47746,0.04756,0.13837],"tcp_to_object_dist_end":0.02306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":159.0,"n_steps_budget":1000.0,"object_pos_end":[0.58792,0.23064,0.22758],"object_pos_start":[0.58734,0.22536,0.31842],"object_to_goal_dist_end":0.00695,"object_to_goal_dist_start":0.08818,"object_z_max":0.31848,"peak_contact_force":0.07986,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5789.0,"raw_peak_contact_force":0.2299,"subtask_id":"place_subtask","tcp_end":[0.5781,0.22587,0.24971],"tcp_start":[0.57571,0.22054,0.33774],"tcp_to_object_dist_end":0.02468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57476,0.22596,0.01268],"object_pos_start":[0.58792,0.23064,0.22758],"object_to_goal_dist_end":0.21794,"object_to_goal_dist_start":0.00695,"object_z_max":0.22758,"peak_contact_force":0.32283,"phase_name":"release_phase","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2289.0,"raw_peak_contact_force":1.73971,"tcp_end":[0.57362,0.22395,0.26954],"tcp_start":[0.5781,0.22587,0.24971],"tcp_to_object_dist_end":0.25686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":171.0,"n_steps_budget":600.0,"object_pos_end":[0.56364,0.21804,0.02603],"object_pos_start":[0.57476,0.22596,0.01268],"object_to_goal_dist_end":0.20555,"object_to_goal_dist_start":0.21794,"object_z_max":0.02831,"peak_contact_force":0.12971,"phase_name":"retract_arm","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":613.0,"raw_peak_contact_force":0.30564,"tcp_end":[0.57827,0.22703,0.31095],"tcp_start":[0.57362,0.22395,0.26954],"tcp_to_object_dist_end":0.28544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85354,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.11315,"approach_obj.pre_grasp_z_offset":0.07905,"descend_grasp.grasp_z_offset":0.02583,"grasp_phase.grasp_time":0.69873,"lift_obj.lift_z_offset":0.18281,"release_phase.release_time":0.72759},"optimized_scores":{"best_composite_score":0.13892,"best_fitness_score":0.61892,"best_task_score":0.29538},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.60607,0.22092,-0.01252],"force_p95":1.53773,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61075,"mean_force":0.7596,"phase_index":6.0,"phase_name":"release_phase","phase_type":"release","tcp_position_centroid":[0.60134,0.22147,0.23766]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53438,-0.02116,-0.00134],"force_p95":0.45615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54902,"mean_force":0.11412,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52212,-0.02102,0.03929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10788.0,"contact_point_centroid":[0.52678,-0.00215,0.11311],"force_p95":0.07718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3236,"mean_force":0.05101,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52564,-0.02117,0.11124]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9188.0,"contact_point_centroid":[0.5258,-0.04036,0.11382],"force_p95":0.08138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31787,"mean_force":0.058,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52561,-0.02117,0.11096]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.6015,0.24167,0.22538],"force_p95":0.08529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28553,"mean_force":0.05257,"phase_index":6.0,"phase_name":"release_phase","phase_type":"release","tcp_position_centroid":[0.60437,0.22278,0.22102]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2438.0,"contact_point_centroid":[0.60202,0.238,0.27185],"force_p95":0.09471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26853,"mean_force":0.06102,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60509,0.21922,0.26803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.61319,0.20543,0.22192],"force_p95":0.08117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25904,"mean_force":0.04877,"phase_index":6.0,"phase_name":"release_phase","phase_type":"release","tcp_position_centroid":[0.60436,0.22278,0.22102]},{"body_a":"world","body_b":"grasp_target","contact_count":608.0,"contact_point_centroid":[0.59369,0.21703,-0.00244],"force_p95":0.22423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25681,"mean_force":0.13703,"phase_index":7.0,"phase_name":"retract_arm","phase_type":"retract","tcp_position_centroid":[0.60376,0.22374,0.26911]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2583.0,"contact_point_centroid":[0.61399,0.20206,0.26888],"force_p95":0.09185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23566,"mean_force":0.05801,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60511,0.21929,0.26734]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15107.0,"contact_point_centroid":[0.5724,0.08242,0.2486],"force_p95":0.08314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17356,"mean_force":0.05759,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56814,0.1009,0.24716]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15316.0,"contact_point_centroid":[0.56452,0.11316,0.24623],"force_p95":0.08767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1552,"mean_force":0.05655,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56608,0.09434,0.24381]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02143,-0.00203],"force_p95":0.13393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15083,"mean_force":0.12563,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52442,-0.02106,0.03946]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51325,-0.00902,0.21454]},{"body_a":"world","body_b":"grasp_target","contact_count":3540.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52884,-0.02009,0.0784]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5333.0,"contact_point_centroid":[0.52394,-0.00196,0.04004],"force_p95":0.06847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10035,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52316,-0.02104,0.03799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4151.0,"contact_point_centroid":[0.52244,-0.04029,0.04099],"force_p95":0.08058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08744,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52316,-0.02104,0.03799]}],"total_contact_groups":16},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58978,0.21594,0.02603],"final_tcp_position":[0.60645,0.22569,0.28809],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.52876,-0.01862,0.12685],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":885.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3540.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5316,-0.02116,0.04785],"tcp_start":[0.52876,-0.01862,0.12685],"tcp_to_object_dist_end":0.0225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02147,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31695,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13406,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11284.0,"raw_peak_contact_force":0.15083,"tcp_end":[0.52312,-0.02104,0.03795],"tcp_start":[0.5316,-0.02116,0.04785],"tcp_to_object_dist_end":0.01834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.54458,-0.02193,0.1738],"object_pos_start":[0.53691,-0.02147,0.02586],"object_to_goal_dist_end":0.26037,"object_to_goal_dist_start":0.31695,"object_z_max":0.17355,"peak_contact_force":0.07911,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20054.0,"raw_peak_contact_force":0.54902,"tcp_end":[0.53235,-0.02136,0.18929],"tcp_start":[0.52312,-0.02104,0.03795],"tcp_to_object_dist_end":0.01974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.61466,0.21986,0.28575],"object_pos_start":[0.54458,-0.02193,0.1738],"object_to_goal_dist_end":0.07885,"object_to_goal_dist_start":0.26037,"object_z_max":0.28564,"peak_contact_force":167951.73011,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30423.0,"raw_peak_contact_force":0.17356,"tcp_end":[0.60456,0.21532,0.30607],"tcp_start":[0.53235,-0.02136,0.18929],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.61533,0.22824,0.20415],"object_pos_start":[0.61466,0.21986,0.28575],"object_to_goal_dist_end":0.006,"object_to_goal_dist_start":0.07885,"object_z_max":0.28575,"peak_contact_force":0.07558,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5021.0,"raw_peak_contact_force":0.26853,"subtask_id":"place_subtask","tcp_end":[0.60631,0.22344,0.22646],"tcp_start":[0.60456,0.21532,0.30607],"tcp_to_object_dist_end":0.02453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60395,0.22281,0.01923],"object_pos_start":[0.61533,0.22824,0.20415],"object_to_goal_dist_end":0.18835,"object_to_goal_dist_start":0.006,"object_z_max":0.20415,"peak_contact_force":0.2033,"phase_name":"release_phase","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2333.0,"raw_peak_contact_force":1.61075,"tcp_end":[0.6013,0.22146,0.24529],"tcp_start":[0.60631,0.22344,0.22646],"tcp_to_object_dist_end":0.22608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.58978,0.21594,0.02603],"object_pos_start":[0.60395,0.22281,0.01923],"object_to_goal_dist_end":0.18292,"object_to_goal_dist_start":0.18835,"object_z_max":0.03007,"peak_contact_force":0.12919,"phase_name":"retract_arm","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":608.0,"raw_peak_contact_force":0.25681,"tcp_end":[0.60645,0.22569,0.28809],"tcp_start":[0.6013,0.22146,0.24529],"tcp_to_object_dist_end":0.26277,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84699,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.13147,"approach_obj.pre_grasp_z_offset":0.11693,"descend_grasp.grasp_z_offset":0.03098,"grasp_phase.grasp_time":0.51568,"lift_obj.lift_z_offset":0.13917,"release_phase.release_time":0.56211},"optimized_scores":{"best_composite_score":0.16814,"best_fitness_score":0.64814,"best_task_score":0.36724},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.62365,0.15661,-0.00922],"force_p95":1.35417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70513,"mean_force":0.54209,"phase_index":6.0,"phase_name":"release_phase","phase_type":"release","tcp_position_centroid":[0.62255,0.16026,0.20496]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54256,-0.02883,-0.00134],"force_p95":0.40959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46409,"mean_force":0.10422,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53082,-0.0287,0.04547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":919.0,"contact_point_centroid":[0.63285,0.14343,0.18897],"force_p95":0.10014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32823,"mean_force":0.06182,"phase_index":6.0,"phase_name":"release_phase","phase_type":"release","tcp_position_centroid":[0.62607,0.16131,0.19035]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.62377,0.18021,0.19067],"force_p95":0.10051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30983,"mean_force":0.05963,"phase_index":6.0,"phase_name":"release_phase","phase_type":"release","tcp_position_centroid":[0.62608,0.16131,0.19037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8252.0,"contact_point_centroid":[0.53489,-0.00959,0.09617],"force_p95":0.07586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30222,"mean_force":0.0475,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53411,-0.02877,0.09368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7339.0,"contact_point_centroid":[0.53396,-0.048,0.09704],"force_p95":0.07362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.296,"mean_force":0.05218,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53411,-0.02877,0.0936]},{"body_a":"world","body_b":"grasp_target","contact_count":376.0,"contact_point_centroid":[0.62732,0.15648,-0.0038],"force_p95":0.27122,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27393,"mean_force":0.23082,"phase_index":7.0,"phase_name":"retract_arm","phase_type":"retract","tcp_position_centroid":[0.62484,0.16166,0.23545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2684.0,"contact_point_centroid":[0.6246,0.17719,0.24838],"force_p95":0.10861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24798,"mean_force":0.06639,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62679,0.15833,0.24773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2604.0,"contact_point_centroid":[0.63375,0.14056,0.24649],"force_p95":0.10874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24537,"mean_force":0.06804,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62681,0.15838,0.24702]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02927,-0.00205],"force_p95":0.13775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16008,"mean_force":0.12668,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53297,-0.02876,0.04564]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16249.0,"contact_point_centroid":[0.58071,0.08314,0.21895],"force_p95":0.07857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15287,"mean_force":0.0525,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58185,0.06416,0.21724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15969.0,"contact_point_centroid":[0.58485,0.04507,0.2186],"force_p95":0.07938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15156,"mean_force":0.05382,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58173,0.06393,0.21704]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51654,-0.01198,0.23267]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53674,-0.02721,0.09767]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5806.0,"contact_point_centroid":[0.5323,-0.00948,0.04684],"force_p95":0.06791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10476,"mean_force":0.03813,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.5317,-0.02872,0.04413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5132.0,"contact_point_centroid":[0.53193,-0.04802,0.04734],"force_p95":0.06998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07894,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.5317,-0.02872,0.04413]}],"total_contact_groups":16},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63684,0.15792,0.02687],"final_tcp_position":[0.62832,0.16332,0.25756],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.70513,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.53553,-0.02485,0.16338],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54014,-0.02895,0.05432],"tcp_start":[0.53553,-0.02485,0.16338],"tcp_to_object_dist_end":0.02882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54553,-0.02906,0.02579],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26095,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13754,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12738.0,"raw_peak_contact_force":0.16008,"tcp_end":[0.53167,-0.02872,0.04409],"tcp_start":[0.54014,-0.02895,0.05432],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":356.0,"n_steps_budget":780.0,"object_pos_end":[0.55238,-0.02936,0.12553],"object_pos_start":[0.54553,-0.02906,0.02579],"object_to_goal_dist_end":0.21648,"object_to_goal_dist_start":0.26095,"object_z_max":0.12527,"peak_contact_force":0.07509,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15671.0,"raw_peak_contact_force":0.46409,"tcp_end":[0.54011,-0.02891,0.14574],"tcp_start":[0.53167,-0.02872,0.04409],"tcp_to_object_dist_end":0.02366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.63651,0.15851,0.26782],"object_pos_start":[0.55238,-0.02936,0.12553],"object_to_goal_dist_end":0.0912,"object_to_goal_dist_start":0.21648,"object_z_max":0.26768,"peak_contact_force":0.08496,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32218.0,"raw_peak_contact_force":0.15287,"tcp_end":[0.62618,0.15531,0.29235],"tcp_start":[0.54011,-0.02891,0.14574],"tcp_to_object_dist_end":0.02681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.63621,0.16519,0.16888],"object_pos_start":[0.63651,0.15851,0.26782],"object_to_goal_dist_end":0.00872,"object_to_goal_dist_start":0.0912,"object_z_max":0.26786,"peak_contact_force":0.08588,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5288.0,"raw_peak_contact_force":0.24798,"subtask_id":"place_subtask","tcp_end":[0.62834,0.16186,0.19595],"tcp_start":[0.62618,0.15531,0.29235],"tcp_to_object_dist_end":0.02839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62594,0.16286,0.0251],"object_pos_start":[0.63621,0.16519,0.16888],"object_to_goal_dist_end":0.15199,"object_to_goal_dist_start":0.00872,"object_z_max":0.16888,"peak_contact_force":0.24416,"phase_name":"release_phase","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1995.0,"raw_peak_contact_force":1.70513,"tcp_end":[0.62249,0.16024,0.21455],"tcp_start":[0.62834,0.16186,0.19595],"tcp_to_object_dist_end":0.1895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":188.0,"n_steps_budget":600.0,"object_pos_end":[0.63684,0.15792,0.02687],"object_pos_start":[0.62594,0.16286,0.0251],"object_to_goal_dist_end":0.15026,"object_to_goal_dist_start":0.15199,"object_z_max":0.02974,"peak_contact_force":0.23278,"phase_name":"retract_arm","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":376.0,"raw_peak_contact_force":0.27393,"tcp_end":[0.62832,0.16332,0.25756],"tcp_start":[0.62249,0.16024,0.21455],"tcp_to_object_dist_end":0.23091,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```