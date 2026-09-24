## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5550 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1419 | 0.31 | ✅ accepted |
| 2 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ❌ rejected |
| 1 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ❌ rejected |
| 0 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.555) — your mutation base

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
    - 0.12
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
    - 0.1
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
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.0
      default: -0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_subtask

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_obj** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.02
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_goal_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.555
- **task_score** (E): 1.000
- **fitness_score**: 0.975  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1765 |
| descend_grasp | 1.00 | 1.00 | 0.0868 |
| grasp_phase | 1.00 | 1.00 | 0.0127 |
| lift_obj | 1.00 | 1.00 | 0.1245 |
| approach_goal | 1.00 | 1.00 | 0.2612 |
| descend_place | 1.00 | 1.00 | 0.0824 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.129) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 18.224 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.129)→(0.516, -0.001, 0.043) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_phase | grasp | 1.00 / step_budget | (0.516, -0.001, 0.043)→(0.508, -0.001, 0.033) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 43.000 | 0.142 | 0.171 |
| lift_obj | lift | 1.00 / step_budget | (0.508, -0.001, 0.033)→(0.517, -0.001, 0.158) | (0.522, -0.001, 0.026)→(0.530, -0.001, 0.147) | 0.290→0.232 | 1.00 / 37.667 | 0.081 | 0.607 |
| approach_goal | approach | 1.00 / step_budget | (0.517, -0.001, 0.158)→(0.602, 0.197, 0.302) | (0.530, -0.001, 0.147)→(0.613, 0.201, 0.286) | 0.232→0.082 | 1.00 / 35.667 | 0.086 | 0.151 |
| descend_place | descend | 1.00 / step_budget | (0.602, 0.197, 0.302)→(0.604, 0.203, 0.220) | (0.613, 0.201, 0.286)→(0.614, 0.207, 0.201) | 0.082→0.008 | 1.00 / 30.667 | 0.094 | 0.224 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.642
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.653
- phase_breakdown.place_subtask_score: 0.678
- phase_breakdown.approach_subtask_score: 0.556
- grasp_place_fitness: 0.976

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.976
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.556
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.433


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7875,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.0562,"approach_obj.pre_grasp_z_offset":0.0937,"descend_grasp.grasp_z_offset":0.02022,"descend_place.place_z_offset":-0.00228,"grasp_phase.grasp_time":0.74907,"lift_obj.lift_z_offset":0.15725},"optimized_scores":{"best_composite_score":0.55337,"best_fitness_score":0.97337,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.48033,0.04711,-0.00143],"force_p95":0.46016,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54608,"mean_force":0.10438,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.46866,0.04709,0.03772]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6936.0,"contact_point_centroid":[0.47183,0.06642,0.10176],"force_p95":0.08689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32087,"mean_force":0.06061,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.472,0.04719,0.09917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8744.0,"contact_point_centroid":[0.47386,0.02827,0.10099],"force_p95":0.08326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29163,"mean_force":0.04985,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47203,0.04719,0.09944]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":821.0,"contact_point_centroid":[0.5707,0.23886,0.26476],"force_p95":0.10234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26421,"mean_force":0.07225,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57471,0.22025,0.26166]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04871,-0.00213],"force_p95":0.15807,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21361,"mean_force":0.1321,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.47083,0.04733,0.03744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.58225,0.20298,0.2614],"force_p95":0.08629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20587,"mean_force":0.05667,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57473,0.2203,0.2614]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5259.0,"contact_point_centroid":[0.47116,0.0282,0.03748],"force_p95":0.07304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18274,"mean_force":0.04136,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46963,0.04721,0.03621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14384.0,"contact_point_centroid":[0.53059,0.11653,0.21839],"force_p95":0.08108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1664,"mean_force":0.0521,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52562,0.13485,0.21732]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12143.0,"contact_point_centroid":[0.5227,0.15338,0.22043],"force_p95":0.08852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14868,"mean_force":0.06009,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52545,0.13456,0.21712]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.49036,0.02018,0.22238]},{"body_a":"world","body_b":"grasp_target","contact_count":2260.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47803,0.04503,0.08829]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4210.0,"contact_point_centroid":[0.46944,0.06653,0.03864],"force_p95":0.08824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09235,"mean_force":0.05199,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46963,0.04721,0.03622]}],"total_contact_groups":12},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58875,0.22849,0.22832],"final_tcp_position":[0.57617,0.22287,0.24624],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.54608,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.48158,0.04185,0.14227],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2260.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47768,0.048,0.04451],"tcp_start":[0.48158,0.04185,0.14227],"tcp_to_object_dist_end":0.01917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04797,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29077,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15578,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11269.0,"raw_peak_contact_force":0.21361,"tcp_end":[0.4696,0.04721,0.03618],"tcp_start":[0.47768,0.048,0.04451],"tcp_to_object_dist_end":0.01689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":408.0,"n_steps_budget":930.0,"object_pos_end":[0.49057,0.04854,0.1503],"object_pos_start":[0.48271,0.04797,0.02556],"object_to_goal_dist_end":0.21743,"object_to_goal_dist_start":0.29077,"object_z_max":0.15003,"peak_contact_force":0.08423,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15758.0,"raw_peak_contact_force":0.54608,"tcp_end":[0.47793,0.04754,0.16361],"tcp_start":[0.4696,0.04721,0.03618],"tcp_to_object_dist_end":0.01838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.58538,0.22299,0.25531],"object_pos_start":[0.49057,0.04854,0.1503],"object_to_goal_dist_end":0.02575,"object_to_goal_dist_start":0.21743,"object_z_max":0.25519,"peak_contact_force":0.09292,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26527.0,"raw_peak_contact_force":0.1664,"tcp_end":[0.57369,0.21799,0.27219],"tcp_start":[0.47793,0.04754,0.16361],"tcp_to_object_dist_end":0.02113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.58875,0.22849,0.22832],"object_pos_start":[0.58538,0.22299,0.25531],"object_to_goal_dist_end":0.00722,"object_to_goal_dist_start":0.02575,"object_z_max":0.25534,"peak_contact_force":0.10373,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1869.0,"raw_peak_contact_force":0.26421,"subtask_id":"place_subtask","tcp_end":[0.57617,0.22287,0.24624],"tcp_start":[0.57369,0.21799,0.27219],"tcp_to_object_dist_end":0.02261,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90643,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.08807,"approach_obj.pre_grasp_z_offset":0.07406,"descend_grasp.grasp_z_offset":0.02004,"descend_place.place_z_offset":-0.00013,"grasp_phase.grasp_time":0.30393,"lift_obj.lift_z_offset":0.13321},"optimized_scores":{"best_composite_score":0.55579,"best_fitness_score":0.97579,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53431,-0.02114,-0.00133],"force_p95":0.516,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63093,"mean_force":0.12337,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52208,-0.02103,0.03354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7873.0,"contact_point_centroid":[0.5264,-0.00213,0.08611],"force_p95":0.0768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3278,"mean_force":0.05048,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52533,-0.02116,0.08417]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6596.0,"contact_point_centroid":[0.52551,-0.04035,0.08728],"force_p95":0.08143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32577,"mean_force":0.05832,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52534,-0.02116,0.08443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1599.0,"contact_point_centroid":[0.61326,0.20222,0.25518],"force_p95":0.09715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22577,"mean_force":0.06539,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60505,0.21952,0.2545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1564.0,"contact_point_centroid":[0.60123,0.23782,0.259],"force_p95":0.09683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22414,"mean_force":0.06675,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60502,0.21936,0.25603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16107.0,"contact_point_centroid":[0.57187,0.08325,0.21181],"force_p95":0.08395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15157,"mean_force":0.05802,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5676,0.10177,0.21035]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02142,-0.00203],"force_p95":0.13425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14994,"mean_force":0.12555,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52431,-0.02106,0.03371]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51327,-0.00905,0.21213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16737.0,"contact_point_centroid":[0.56391,0.114,0.20876],"force_p95":0.08589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13533,"mean_force":0.05566,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5655,0.09519,0.20634]},{"body_a":"world","body_b":"grasp_target","contact_count":3560.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5288,-0.02012,0.07312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5326.0,"contact_point_centroid":[0.52385,-0.00196,0.03432],"force_p95":0.0684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09793,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52302,-0.02104,0.03224]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4155.0,"contact_point_centroid":[0.52237,-0.0403,0.03528],"force_p95":0.08047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08837,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52303,-0.02104,0.03224]}],"total_contact_groups":12},"final_pose_error":0.01957,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61729,0.22805,0.20904],"final_tcp_position":[0.60604,0.22293,0.22575],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.63093,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1404.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.52882,-0.01868,0.12193],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":890.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3560.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53156,-0.02117,0.0421],"tcp_start":[0.52882,-0.01868,0.12193],"tcp_to_object_dist_end":0.01698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53689,-0.02144,0.02587],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31693,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13442,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11281.0,"raw_peak_contact_force":0.14994,"tcp_end":[0.52299,-0.02104,0.0322],"tcp_start":[0.53156,-0.02117,0.0421],"tcp_to_object_dist_end":0.01528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":372.0,"n_steps_budget":810.0,"object_pos_end":[0.54477,-0.02183,0.13106],"object_pos_start":[0.53689,-0.02144,0.02587],"object_to_goal_dist_end":0.26911,"object_to_goal_dist_start":0.31693,"object_z_max":0.1308,"peak_contact_force":0.07959,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14547.0,"raw_peak_contact_force":0.63093,"tcp_end":[0.53151,-0.02132,0.13999],"tcp_start":[0.52299,-0.02104,0.0322],"tcp_to_object_dist_end":0.016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.61558,0.2208,0.2655],"object_pos_start":[0.54477,-0.02183,0.13106],"object_to_goal_dist_end":0.05874,"object_to_goal_dist_start":0.26911,"object_z_max":0.26538,"peak_contact_force":0.08771,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32844.0,"raw_peak_contact_force":0.15157,"tcp_end":[0.60452,0.21617,0.28044],"tcp_start":[0.53151,-0.02132,0.13999],"tcp_to_object_dist_end":0.01916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":102.0,"n_steps_budget":1000.0,"object_pos_end":[0.61729,0.22805,0.20904],"object_pos_start":[0.61558,0.2208,0.2655],"object_to_goal_dist_end":0.00717,"object_to_goal_dist_start":0.05874,"object_z_max":0.26553,"peak_contact_force":0.09455,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3163.0,"raw_peak_contact_force":0.22577,"subtask_id":"place_subtask","tcp_end":[0.60604,0.22293,0.22575],"tcp_start":[0.60452,0.21617,0.28044],"tcp_to_object_dist_end":0.02079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92228,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.19202,"approach_obj.pre_grasp_z_offset":0.07727,"descend_grasp.grasp_z_offset":0.02013,"descend_place.place_z_offset":-0.00932,"grasp_phase.grasp_time":0.32095,"lift_obj.lift_z_offset":0.16269},"optimized_scores":{"best_composite_score":0.55576,"best_fitness_score":0.97576,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.54264,-0.02864,-0.00135],"force_p95":0.52798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64264,"mean_force":0.13117,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53042,-0.02874,0.03325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8075.0,"contact_point_centroid":[0.53434,-0.04803,0.10268],"force_p95":0.08366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34047,"mean_force":0.06037,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53407,-0.02883,0.09982]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9893.0,"contact_point_centroid":[0.53529,-0.00986,0.10002],"force_p95":0.07967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3328,"mean_force":0.05116,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53393,-0.02883,0.09823]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4525.0,"contact_point_centroid":[0.62577,0.17814,0.27501],"force_p95":0.08791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18255,"mean_force":0.06238,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62767,0.1593,0.27225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4271.0,"contact_point_centroid":[0.63425,0.14134,0.27246],"force_p95":0.09568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15502,"mean_force":0.06692,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62767,0.15931,0.27193]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5456,-0.02928,-0.00204],"force_p95":0.13596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15066,"mean_force":0.12585,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53276,-0.0288,0.03345]},{"body_a":"world","body_b":"grasp_target","contact_count":1416.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51697,-0.01244,0.21316]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15245.0,"contact_point_centroid":[0.58579,0.04572,0.26074],"force_p95":0.09054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13567,"mean_force":0.06172,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5827,0.06458,0.25888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17515.0,"contact_point_centroid":[0.58157,0.08242,0.25949],"force_p95":0.08129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12371,"mean_force":0.05409,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58222,0.06358,0.25787]},{"body_a":"world","body_b":"grasp_target","contact_count":3692.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53687,-0.02753,0.07479]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5307.0,"contact_point_centroid":[0.53244,-0.00972,0.03397],"force_p95":0.07151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10791,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53147,-0.02877,0.03194]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4159.0,"contact_point_centroid":[0.53202,-0.04805,0.03478],"force_p95":0.08314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09812,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53147,-0.02877,0.03194]}],"total_contact_groups":12},"final_pose_error":0.01953,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.6373,0.16595,0.16694],"final_tcp_position":[0.62889,0.16277,0.18661],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":54.42621,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":54.42621,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1416.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.53641,-0.02564,0.12428],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3692.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54007,-0.02899,0.04208],"tcp_start":[0.53641,-0.02564,0.12428],"tcp_to_object_dist_end":0.01698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54548,-0.02914,0.02584],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.261,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.136,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11266.0,"raw_peak_contact_force":0.15066,"tcp_end":[0.53144,-0.02876,0.0319],"tcp_start":[0.54007,-0.02899,0.04208],"tcp_to_object_dist_end":0.0153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":475.0,"n_steps_budget":990.0,"object_pos_end":[0.55368,-0.02959,0.15957],"object_pos_start":[0.54548,-0.02914,0.02584],"object_to_goal_dist_end":0.21072,"object_to_goal_dist_start":0.261,"object_z_max":0.15932,"peak_contact_force":0.08039,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18047.0,"raw_peak_contact_force":0.64264,"tcp_end":[0.54059,-0.029,0.16915],"tcp_start":[0.53144,-0.02876,0.0319],"tcp_to_object_dist_end":0.01623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.63902,0.15953,0.33692],"object_pos_start":[0.55368,-0.02959,0.15957],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.21072,"object_z_max":0.33676,"peak_contact_force":0.07587,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32760.0,"raw_peak_contact_force":0.13567,"tcp_end":[0.62731,0.15629,0.35204],"tcp_start":[0.54059,-0.029,0.16915],"tcp_to_object_dist_end":0.01941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.6373,0.16595,0.16694],"object_pos_start":[0.63902,0.15953,0.33692],"object_to_goal_dist_end":0.01097,"object_to_goal_dist_start":0.16021,"object_z_max":0.33696,"peak_contact_force":0.08356,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8796.0,"raw_peak_contact_force":0.18255,"subtask_id":"place_subtask","tcp_end":[0.62889,0.16277,0.18661],"tcp_start":[0.62731,0.15629,0.35204],"tcp_to_object_dist_end":0.02162,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```