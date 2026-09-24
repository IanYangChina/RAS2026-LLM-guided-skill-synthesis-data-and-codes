## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 6 | 0.1229 | 0.20 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 5 | 0.3416 | 0.23 | ✅ accepted |
| 0 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.123) — your mutation base

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

- **Composite score**: 0.123
- **task_score** (E): 0.203
- **fitness_score**: 0.478  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.095
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1469 |
| descend_1 | 1.00 | 1.00 | 0.1166 |
| grasp_1 | 1.00 | 1.00 | 0.0041 |
| lift_1 | 1.00 | 1.00 | 0.1054 |
| transport_1 | 0.00 | 1.00 | 0.0892 |
| place_descend_1 | 1.00 | 1.00 | 0.0705 |
| release_1 | 1.00 | 1.00 | 0.0220 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.003, 0.161) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / condition_met | (0.517, 0.003, 0.161)→(0.512, 0.025, 0.047) | (0.522, -0.001, 0.026)→(0.515, 0.010, 0.029) | 0.289→0.281 | 1.00 / 11.000 | 7.578 | 705.692 |
| grasp_1 | grasp | 1.00 / step_budget | (0.509, 0.025, 0.043)→(0.508, 0.028, 0.045) | (0.515, 0.010, 0.029)→(0.514, 0.025, 0.022) | 0.281→0.276 | 1.00 / 23.000 | 49.607 | 153.309 |
| lift_1 | lift | 1.00 / step_budget | (0.508, 0.028, 0.045)→(0.510, 0.025, 0.150) | (0.514, 0.025, 0.022)→(0.514, 0.023, 0.104) | 0.276→0.232 | 1.00 / 29.000 | 0.105 | 68.433 |
| transport_1 | approach | 0.00 / step_budget | (0.510, 0.025, 0.150)→(0.529, 0.065, 0.227) | (0.514, 0.023, 0.104)→(0.527, 0.048, 0.150) | 0.232→0.195 | 1.00 / 26.000 | 91001.998 | 0.156 |
| place_descend_1 | descend | 1.00 / step_budget | (0.529, 0.065, 0.227)→(0.557, 0.125, 0.208) | (0.527, 0.048, 0.150)→(0.542, 0.091, 0.071) | 0.195→0.203 | 1.00 / 17.333 | 0.129 | 0.732 |
| release_1 | release | 1.00 / step_budget | (0.557, 0.125, 0.208)→(0.553, 0.124, 0.229) | (0.542, 0.091, 0.071)→(0.537, 0.092, 0.016) | 0.203→0.240 | 1.00 / 3.667 | 0.147 | 0.733 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.223
- phase_score: 0.196
- phase_breakdown.reach_goal_score: 0.008
- phase_breakdown.reach_pre_grasp_score: 0.631
- phase_breakdown.lift_clearance_score: 0.160
- phase_breakdown.place_accuracy_score: 0.146
- phase_breakdown.grasp_success_score: 0.291
- grasp_place_fitness: 0.600

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.600
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.223
- **Median Q (composite search score)**: 0.291
- **K-run variance**: 0.0571
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.283


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":22.0,"average_failure_rate":0.1746,"average_mean_iterations":38.84921,"average_solve_count":126.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12755,"descend_1.descend_z_offset":0.0314,"lift_1.lift_guard_threshold":0.13458,"lift_1.lift_height":0.18028,"place_descend_1.place_z_offset":-0.0005,"transport_1.transport_height":0.1496},"optimized_scores":{"best_composite_score":0.29087,"best_fitness_score":0.59801,"best_task_score":0.20986},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.54788,0.09622,-0.00503],"force_p95":1072.97829,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1189.6466,"mean_force":281.73933,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50115,0.06097,-0.01077]},{"body_a":"world","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.61901,0.05421,-0.0007],"force_p95":371.56961,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":416.5269,"mean_force":288.8311,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49643,0.06203,-0.00261]},{"body_a":"world","body_b":"link7","contact_count":444.0,"contact_point_centroid":[0.60538,0.05735,-0.00018],"force_p95":109.8028,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.67766,"mean_force":80.97125,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48372,0.06807,0.0175]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.60534,0.0573,-0.00012],"force_p95":146.62952,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.22621,"mean_force":100.57929,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48369,0.06802,0.01766]},{"body_a":"world","body_b":"left_finger","contact_count":635.0,"contact_point_centroid":[0.50014,0.01925,-0.00841],"force_p95":13.59193,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.12522,"mean_force":4.13426,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50088,0.061,-0.00933]},{"body_a":"world","body_b":"right_finger","contact_count":669.0,"contact_point_centroid":[0.50561,0.10244,-0.00897],"force_p95":10.97162,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.93347,"mean_force":4.3789,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50034,0.06104,-0.00874]},{"body_a":"world","body_b":"grasp_target","contact_count":118.0,"contact_point_centroid":[0.51317,0.16087,-0.00977],"force_p95":1.60976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96281,"mean_force":0.65816,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.51772,0.14239,0.23787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5.0,"contact_point_centroid":[0.4782,0.02897,0.01511],"force_p95":0.87217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97002,"mean_force":0.52339,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48714,0.06687,0.0151]},{"body_a":"world","body_b":"grasp_target","contact_count":256.0,"contact_point_centroid":[0.47976,0.07099,-0.00253],"force_p95":0.44863,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80835,"mean_force":0.14951,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48177,0.06772,0.02254]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48224,0.05495,-0.00317],"force_p95":0.48875,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.695,"mean_force":0.24345,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48373,0.06807,0.0175]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5872.0,"contact_point_centroid":[0.48318,0.04181,0.01577],"force_p95":0.14364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62192,"mean_force":0.06422,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48373,0.06805,0.01752]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3371.0,"contact_point_centroid":[0.51053,0.09859,0.24592],"force_p95":0.14285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33563,"mean_force":0.08462,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.50908,0.11743,0.25023]},{"body_a":"world","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32276,"mean_force":0.1242,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50973,0.05739,0.06227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19431.0,"contact_point_centroid":[0.4803,0.04838,0.09947],"force_p95":0.09205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31688,"mean_force":0.05307,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47969,0.06772,0.09931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19494.0,"contact_point_centroid":[0.48278,0.08687,0.09976],"force_p95":0.09059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2799,"mean_force":0.04931,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47967,0.06772,0.0992]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3746.0,"contact_point_centroid":[0.51386,0.13701,0.24475],"force_p95":0.10105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25999,"mean_force":0.07382,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.50992,0.11883,0.24958]}],"total_contact_groups":22},"final_pose_error":0.10744,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.514,0.16368,0.01602],"final_tcp_position":[0.51828,0.14265,0.23825],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1189.6466,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1772.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48086,0.04818,0.1672],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":131.0,"n_steps_budget":1000.0,"object_pos_end":[0.48256,0.04885,0.02613],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28987,"object_to_goal_dist_start":0.28998,"object_z_max":0.02607,"peak_contact_force":13.07479,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1909.0,"raw_peak_contact_force":1189.6466,"subtask_id":"grasp_success","tcp_end":[0.48615,0.0675,0.01593],"tcp_start":[0.48086,0.04818,0.1672],"tcp_to_object_dist_end":0.02156,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48299,0.06839,0.02169],"object_pos_start":[0.48256,0.04885,0.02613],"object_to_goal_dist_end":0.28128,"object_to_goal_dist_start":0.28987,"object_z_max":0.02646,"peak_contact_force":78.63745,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10537.0,"raw_peak_contact_force":251.67766,"tcp_end":[0.48368,0.06803,0.01756],"tcp_start":[0.48615,0.0675,0.01593],"tcp_to_object_dist_end":0.00421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48429,0.06754,0.17281],"object_pos_start":[0.48299,0.06839,0.02169],"object_to_goal_dist_end":0.19716,"object_to_goal_dist_start":0.28128,"object_z_max":0.17265,"peak_contact_force":0.07887,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39186.0,"raw_peak_contact_force":153.22621,"subtask_id":"lift_clearance","tcp_end":[0.48008,0.06802,0.18031],"tcp_start":[0.48368,0.06803,0.01756],"tcp_to_object_dist_end":0.00862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5088,0.10685,0.23066],"object_pos_start":[0.48429,0.06754,0.17281],"object_to_goal_dist_end":0.14222,"object_to_goal_dist_start":0.19716,"object_z_max":0.23063,"peak_contact_force":0.0993,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38966.0,"raw_peak_contact_force":0.20882,"subtask_id":"reach_goal","tcp_end":[0.50357,0.10732,0.25827],"tcp_start":[0.48008,0.06802,0.18031],"tcp_to_object_dist_end":0.0281,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.51582,0.16155,0.0033],"object_pos_start":[0.5088,0.10685,0.23066],"object_to_goal_dist_end":0.24598,"object_to_goal_dist_start":0.14222,"object_z_max":0.23066,"peak_contact_force":0.18647,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7235.0,"raw_peak_contact_force":1.96281,"subtask_id":"place_accuracy","tcp_end":[0.51828,0.14265,0.23825],"tcp_start":[0.50357,0.10732,0.25827],"tcp_to_object_dist_end":0.23572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.514,0.16368,0.01602],"object_pos_start":[0.51582,0.16155,0.0033],"object_to_goal_dist_end":0.2342,"object_to_goal_dist_start":0.24598,"object_z_max":0.01673,"peak_contact_force":0.12264,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":944.0,"raw_peak_contact_force":0.18647,"tcp_end":[0.5164,0.14217,0.25999],"tcp_start":[0.51828,0.14265,0.23825],"tcp_to_object_dist_end":0.24493,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17895,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16748,"descend_1.descend_z_offset":0.02285,"lift_1.lift_guard_threshold":0.11547,"lift_1.lift_height":0.10894,"place_descend_1.place_z_offset":-0.00038,"transport_1.transport_height":0.17006},"optimized_scores":{"best_composite_score":0.29282,"best_fitness_score":0.59996,"best_task_score":0.2229},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":119.0,"contact_point_centroid":[0.62198,0.02399,-0.00206],"force_p95":498.13161,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":927.42979,"mean_force":213.91865,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56084,0.00365,-0.01072]},{"body_a":"world","body_b":"hand","contact_count":420.0,"contact_point_centroid":[0.60648,0.06322,-0.00017],"force_p95":87.46436,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":208.12568,"mean_force":72.43983,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5105,0.03906,0.01308]},{"body_a":"world","body_b":"hand","contact_count":6.0,"contact_point_centroid":[0.60646,0.06387,-0.00011],"force_p95":51.7551,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.94908,"mean_force":38.48368,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51049,0.03968,0.01317]},{"body_a":"world","body_b":"left_finger","contact_count":1406.0,"contact_point_centroid":[0.56783,-0.04025,-0.01051],"force_p95":19.11717,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.84841,"mean_force":12.57962,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56625,0.0003,-0.01181]},{"body_a":"world","body_b":"right_finger","contact_count":1550.0,"contact_point_centroid":[0.56356,0.04133,-0.00994],"force_p95":10.49772,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.2362,"mean_force":6.59779,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56116,0.00209,-0.01044]},{"body_a":"world","body_b":"right_finger","contact_count":62.0,"contact_point_centroid":[0.5272,0.05727,-0.00058],"force_p95":3.1142,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.24657,"mean_force":1.03264,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51012,0.03969,0.01392]},{"body_a":"world","body_b":"right_finger","contact_count":1996.0,"contact_point_centroid":[0.53092,0.05844,-0.00115],"force_p95":1.17511,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.24165,"mean_force":0.6713,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51051,0.03898,0.01313]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.55025,0.13851,-0.01156],"force_p95":1.86974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88862,"mean_force":0.63534,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55809,0.14446,0.21086]},{"body_a":"world","body_b":"grasp_target","contact_count":814.0,"contact_point_centroid":[0.53692,-0.02011,-0.00192],"force_p95":0.54866,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37121,"mean_force":0.17849,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.57776,-0.0027,0.0485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.52324,-0.03566,0.00211],"force_p95":0.9372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.34872,"mean_force":0.42789,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53723,0.00119,-0.00747]},{"body_a":"world","body_b":"grasp_target","contact_count":839.0,"contact_point_centroid":[0.51131,0.01246,-0.0044],"force_p95":0.61544,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14742,"mean_force":0.30328,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51055,0.03915,0.0132]},{"body_a":"grasp_target","body_b":"hand","contact_count":450.0,"contact_point_centroid":[0.5412,0.00757,0.01944],"force_p95":0.48135,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.81942,"mean_force":0.23378,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51058,0.03916,0.0133]},{"body_a":"grasp_target","body_b":"hand","contact_count":633.0,"contact_point_centroid":[0.54316,0.01381,0.0695],"force_p95":0.24639,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.66155,"mean_force":0.15559,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50768,0.03814,0.06249]},{"body_a":"grasp_target","body_b":"hand","contact_count":51.0,"contact_point_centroid":[0.5441,-0.01936,0.03467],"force_p95":0.54467,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.59643,"mean_force":0.35299,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52543,0.0094,-0.00223]},{"body_a":"world","body_b":"grasp_target","contact_count":119.0,"contact_point_centroid":[0.52281,0.01373,-0.00258],"force_p95":0.30635,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59228,"mean_force":0.12808,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50854,0.03964,0.01803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1481.0,"contact_point_centroid":[0.49677,0.01553,0.01813],"force_p95":0.29476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57987,"mean_force":0.10354,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51072,0.03948,0.0136]}],"total_contact_groups":27},"final_pose_error":0.09625,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5517,0.14304,0.0072],"final_tcp_position":[0.56231,0.1452,0.19501],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":927.42979,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1444.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52995,-0.01562,0.2012],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.51585,0.01068,0.03372],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.29362,"object_to_goal_dist_start":0.31672,"object_z_max":0.03345,"peak_contact_force":9.53515,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4057.0,"raw_peak_contact_force":927.42979,"subtask_id":"grasp_success","tcp_end":[0.51046,0.03087,0.01046],"tcp_start":[0.52995,-0.01562,0.2012],"tcp_to_object_dist_end":0.03127,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51317,0.0357,0.01828],"object_pos_start":[0.51585,0.01068,0.03372],"object_to_goal_dist_end":0.28652,"object_to_goal_dist_start":0.29362,"object_z_max":0.03639,"peak_contact_force":70.06146,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6463.0,"raw_peak_contact_force":208.12568,"tcp_end":[0.51055,0.03967,0.01307],"tcp_start":[0.51046,0.03087,0.01046],"tcp_to_object_dist_end":0.00706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.51236,0.03163,0.11316],"object_pos_start":[0.51317,0.0357,0.01828],"object_to_goal_dist_end":0.23863,"object_to_goal_dist_start":0.28652,"object_z_max":0.11305,"peak_contact_force":0.11478,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19408.0,"raw_peak_contact_force":51.94908,"subtask_id":"lift_clearance","tcp_end":[0.5091,0.03623,0.11449],"tcp_start":[0.51055,0.03967,0.01307],"tcp_to_object_dist_end":0.00579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52685,0.06582,0.19223],"object_pos_start":[0.51236,0.03163,0.11316],"object_to_goal_dist_end":0.18281,"object_to_goal_dist_start":0.23863,"object_z_max":0.1921,"peak_contact_force":0.07408,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40014.0,"raw_peak_contact_force":0.1355,"subtask_id":"reach_goal","tcp_end":[0.52426,0.07056,0.19834],"tcp_start":[0.5091,0.03623,0.11449],"tcp_to_object_dist_end":0.00816,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56375,0.14069,0.18473],"object_pos_start":[0.52685,0.06582,0.19223],"object_to_goal_dist_end":0.10131,"object_to_goal_dist_start":0.18281,"object_z_max":0.19224,"peak_contact_force":0.07776,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.1097,"subtask_id":"place_accuracy","tcp_end":[0.56231,0.1452,0.19501],"tcp_start":[0.52426,0.07056,0.19834],"tcp_to_object_dist_end":0.01131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5517,0.14304,0.0072],"object_pos_start":[0.56375,0.14069,0.18473],"object_to_goal_dist_end":0.22515,"object_to_goal_dist_start":0.10131,"object_z_max":0.18473,"peak_contact_force":0.19599,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2612.0,"raw_peak_contact_force":1.88862,"tcp_end":[0.55807,0.14445,0.21692],"tcp_start":[0.56231,0.1452,0.19501],"tcp_to_object_dist_end":0.20982,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.16667,"average_mean_iterations":36.48333,"average_solve_count":120.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08001,"descend_1.descend_z_offset":0.03766,"lift_1.lift_guard_threshold":0.15224,"lift_1.lift_height":0.13963,"place_descend_1.place_z_offset":-0.00806,"transport_1.transport_height":0.16772},"optimized_scores":{"best_composite_score":-0.21487,"best_fitness_score":0.23513,"best_task_score":0.17561},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2568.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51861,-0.00068,0.20396]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53198,-0.02345,0.10504]},{"body_a":"world","body_b":"grasp_target","contact_count":1988.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53416,-0.02613,0.12799]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54768,-0.0061,0.19032]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57334,0.05224,0.20393]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58635,0.08613,0.19145]},{"body_a":"left_finger","body_b":"right_finger","contact_count":768.0,"contact_point_centroid":[0.53155,-0.02342,0.10618],"force_p95":0.0132,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01581,"mean_force":0.01073,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53105,-0.02343,0.10378]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4311.0,"contact_point_centroid":[0.5739,0.05214,0.20629],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01035,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57328,0.05213,0.20398]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4389.0,"contact_point_centroid":[0.54834,-0.00596,0.19288],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01019,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54774,-0.00597,0.19053]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2141.0,"contact_point_centroid":[0.53456,-0.02612,0.13026],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01036,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53415,-0.02613,0.12797]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.58958,0.08665,0.18943],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58896,0.08664,0.18734]}],"total_contact_groups":11},"final_pose_error":0.09154,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.5456,-0.02923,0.02602],"final_tcp_position":[0.59031,0.0867,0.1901],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273005.81946,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2568.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53871,-0.0234,0.11423],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"grasp_success","tcp_end":[0.53871,-0.0234,0.11423],"tcp_start":[0.53871,-0.0234,0.11423],"tcp_to_object_dist_end":0.08867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2968.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53105,-0.02343,0.10378],"tcp_start":[0.53105,-0.02343,0.10378],"tcp_to_object_dist_end":0.07932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":497.0,"n_steps_budget":600.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4129.0,"raw_peak_contact_force":0.12263,"subtask_id":"lift_clearance","tcp_end":[0.54044,-0.02868,0.1545],"tcp_start":[0.53105,-0.02343,0.10378],"tcp_to_object_dist_end":0.12859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":273005.81946,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8389.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5586,0.01631,0.22453],"tcp_start":[0.54044,-0.02868,0.1545],"tcp_to_object_dist_end":0.20408,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8311.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.59031,0.0867,0.1901],"tcp_start":[0.5586,0.01631,0.22453],"tcp_to_object_dist_end":0.20582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58485,0.08584,0.21132],"tcp_start":[0.59031,0.0867,0.1901],"tcp_to_object_dist_end":0.22163,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```