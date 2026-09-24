## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 5 | 0.3416 | 0.23 | ✅ accepted |
| 0 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.342) — your mutation base

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

- **Composite score**: 0.342
- **task_score** (E): 0.227
- **fitness_score**: 0.492  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1179 |
| descend_1 | 1.00 | 1.00 | 0.1875 |
| grasp_1 | 1.00 | 1.00 | 0.0036 |
| lift_1 | 1.00 | 1.00 | 0.1614 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.002, 0.192) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / condition_met | (0.517, 0.002, 0.192)→(0.534, 0.019, 0.011) | (0.522, -0.001, 0.026)→(0.516, 0.009, 0.029) | 0.289→0.282 | 1.00 / 17.667 | 13.374 | 1132.852 |
| grasp_1 | grasp | 1.00 / step_budget | (0.533, 0.019, 0.009)→(0.533, 0.022, 0.010) | (0.516, 0.009, 0.029)→(0.513, 0.027, 0.021) | 0.282→0.276 | 1.00 / 31.333 | 65.357 | 174.569 |
| lift_1 | lift | 1.00 / step_budget | (0.533, 0.022, 0.010)→(0.513, 0.027, 0.168) | (0.513, 0.027, 0.021)→(0.513, 0.027, 0.118) | 0.276→0.225 | 1.00 / 29.333 | 3249.816 | 108.801 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.273
- phase_score: 0.210
- phase_breakdown.reach_goal_score: 0.000
- phase_breakdown.reach_pre_grasp_score: 0.806
- phase_breakdown.lift_clearance_score: 0.664
- phase_breakdown.place_accuracy_score: 0.000
- phase_breakdown.grasp_success_score: 0.627
- grasp_place_fitness: 0.628

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.628
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.273
- **Median Q (composite search score)**: 0.450
- **K-run variance**: 0.0301
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.357


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21622,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12976,"descend_1.descend_z_offset":0.02677,"lift_1.lift_height":0.19178,"place_descend_1.place_z_offset":-0.01103,"transport_1.transport_height":0.17927},"optimized_scores":{"best_composite_score":0.47823,"best_fitness_score":0.62823,"best_task_score":0.27263},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.54432,0.09507,-0.00526],"force_p95":1065.11101,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1224.38033,"mean_force":262.52103,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49765,0.0611,-0.01086]},{"body_a":"world","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.61496,0.05456,-0.00082],"force_p95":407.02261,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":705.30597,"mean_force":301.39042,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49246,0.06255,-0.0017]},{"body_a":"world","body_b":"link7","contact_count":446.0,"contact_point_centroid":[0.60035,0.05833,-0.00018],"force_p95":111.23477,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.35386,"mean_force":81.59656,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.479,0.0694,0.01928]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.6003,0.05829,-0.00013],"force_p95":134.50918,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.34228,"mean_force":91.97326,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47895,0.06935,0.01943]},{"body_a":"world","body_b":"left_finger","contact_count":639.0,"contact_point_centroid":[0.49683,0.01937,-0.00878],"force_p95":14.58415,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.75344,"mean_force":4.31033,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49751,0.06114,-0.00958]},{"body_a":"world","body_b":"right_finger","contact_count":669.0,"contact_point_centroid":[0.50237,0.10261,-0.00925],"force_p95":11.21321,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.20341,"mean_force":4.39935,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49705,0.06116,-0.00913]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.47634,0.02915,0.01563],"force_p95":0.96265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.01164,"mean_force":0.29627,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4823,0.0678,0.01667]},{"body_a":"world","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.47899,0.07374,-0.00255],"force_p95":0.41182,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72226,"mean_force":0.1456,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47726,0.06905,0.02409]},{"body_a":"world","body_b":"grasp_target","contact_count":540.0,"contact_point_centroid":[0.48269,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67877,"mean_force":0.12979,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5072,0.05784,0.06223]},{"body_a":"world","body_b":"grasp_target","contact_count":1781.0,"contact_point_centroid":[0.48242,0.05537,-0.00297],"force_p95":0.48632,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60279,"mean_force":0.22887,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.479,0.0694,0.01928]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5635.0,"contact_point_centroid":[0.47881,0.04284,0.01666],"force_p95":0.13813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36476,"mean_force":0.06615,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47901,0.06939,0.01929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19249.0,"contact_point_centroid":[0.47784,0.04946,0.10179],"force_p95":0.09431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29648,"mean_force":0.05401,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4772,0.06882,0.10178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19412.0,"contact_point_centroid":[0.48031,0.08798,0.10198],"force_p95":0.09259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25018,"mean_force":0.04963,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47718,0.06882,0.10135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2359.0,"contact_point_centroid":[0.482,0.08998,0.02474],"force_p95":0.13992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21581,"mean_force":0.08848,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47897,0.06937,0.01933]},{"body_a":"world","body_b":"grasp_target","contact_count":1752.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49017,0.03009,0.23854]}],"total_contact_groups":15},"final_pose_error":0.03184,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48914,0.06797,0.17116],"final_tcp_position":[0.47964,0.06889,0.18212],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1224.38033,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1752.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.4809,0.0481,0.16938],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.4821,0.04923,0.02653],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28952,"object_to_goal_dist_start":0.28998,"object_z_max":0.02638,"peak_contact_force":9.74874,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1951.0,"raw_peak_contact_force":1224.38033,"subtask_id":"grasp_success","tcp_end":[0.48097,0.06852,0.01773],"tcp_start":[0.4809,0.0481,0.16938],"tcp_to_object_dist_end":0.02123,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48311,0.06921,0.02198],"object_pos_start":[0.4821,0.04923,0.02653],"object_to_goal_dist_end":0.28056,"object_to_goal_dist_start":0.28952,"object_z_max":0.02723,"peak_contact_force":79.11856,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10221.0,"raw_peak_contact_force":233.35386,"tcp_end":[0.47895,0.06937,0.01933],"tcp_start":[0.48097,0.06852,0.01773],"tcp_to_object_dist_end":0.00493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48914,0.06797,0.17116],"object_pos_start":[0.48311,0.06921,0.02198],"object_to_goal_dist_end":0.19495,"object_to_goal_dist_start":0.28056,"object_z_max":0.171,"peak_contact_force":0.08076,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38887.0,"raw_peak_contact_force":140.34228,"subtask_id":"lift_clearance","tcp_end":[0.47964,0.06889,0.18212],"tcp_start":[0.47895,0.06937,0.01933],"tcp_to_object_dist_end":0.01454,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.33333,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1677,"descend_1.descend_z_offset":0.01227,"lift_1.lift_height":0.16752,"place_descend_1.place_z_offset":0.01573,"transport_1.transport_height":0.20237},"optimized_scores":{"best_composite_score":0.44974,"best_fitness_score":0.59974,"best_task_score":0.2336},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":116.0,"contact_point_centroid":[0.62193,0.02407,-0.00209],"force_p95":507.40122,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":922.99815,"mean_force":214.71899,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56247,0.00206,-0.01129]},{"body_a":"world","body_b":"hand","contact_count":422.0,"contact_point_centroid":[0.60645,0.06174,-0.00016],"force_p95":83.90095,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.03613,"mean_force":69.58413,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51139,0.03283,0.00984]},{"body_a":"world","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.60646,0.06235,-0.00012],"force_p95":47.37883,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.64312,"mean_force":36.23667,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51141,0.03341,0.00987]},{"body_a":"world","body_b":"left_finger","contact_count":1412.0,"contact_point_centroid":[0.5675,-0.0408,-0.01043],"force_p95":18.98817,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.31877,"mean_force":12.53486,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56602,-0.00048,-0.01173]},{"body_a":"world","body_b":"right_finger","contact_count":1517.0,"contact_point_centroid":[0.56401,0.04004,-0.01013],"force_p95":10.45193,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.1195,"mean_force":6.62981,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56224,0.00061,-0.01087]},{"body_a":"world","body_b":"right_finger","contact_count":209.0,"contact_point_centroid":[0.52928,0.05215,-0.0012],"force_p95":3.24809,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.0343,"mean_force":1.07752,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51039,0.03357,0.01194]},{"body_a":"world","body_b":"right_finger","contact_count":3473.0,"contact_point_centroid":[0.53397,0.05192,-0.00186],"force_p95":1.48872,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.96839,"mean_force":0.90134,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51142,0.03286,0.00995]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.53699,-0.02039,-0.00191],"force_p95":0.69241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39244,"mean_force":0.18518,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.57729,-0.00329,0.04784]},{"body_a":"world","body_b":"grasp_target","contact_count":1319.0,"contact_point_centroid":[0.51146,0.03643,-0.00277],"force_p95":0.52842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33501,"mean_force":0.20303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51143,0.03301,0.00989]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.51605,-0.03442,0.00283],"force_p95":0.78566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.14662,"mean_force":0.3293,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53338,0.00103,-0.00666]},{"body_a":"grasp_target","body_b":"hand","contact_count":176.0,"contact_point_centroid":[0.54103,0.00703,0.02207],"force_p95":0.73227,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.9466,"mean_force":0.25658,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51146,0.03264,0.0103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2776.0,"contact_point_centroid":[0.49569,0.0094,0.01817],"force_p95":0.15747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.9223,"mean_force":0.07597,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5115,0.03315,0.01009]},{"body_a":"grasp_target","body_b":"hand","contact_count":48.0,"contact_point_centroid":[0.54309,-0.0255,0.03466],"force_p95":0.63638,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67966,"mean_force":0.4348,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52647,0.00686,-0.00317]},{"body_a":"world","body_b":"grasp_target","contact_count":199.0,"contact_point_centroid":[0.50797,0.05243,-0.00122],"force_p95":0.26277,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45021,"mean_force":0.10773,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50983,0.03372,0.01321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1235.0,"contact_point_centroid":[0.52688,0.0573,0.00583],"force_p95":0.14352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3519,"mean_force":0.09076,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51142,0.03308,0.00983]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14832.0,"contact_point_centroid":[0.52187,0.05231,0.09845],"force_p95":0.15842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29683,"mean_force":0.07729,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50701,0.03882,0.10235]}],"total_contact_groups":18},"final_pose_error":0.01307,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50511,0.04377,0.15587],"final_tcp_position":[0.50742,0.04221,0.17015],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":922.99815,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1440.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52995,-0.01562,0.20141],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.51886,0.0068,0.0347],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.29498,"object_to_goal_dist_start":0.31672,"object_z_max":0.03447,"peak_contact_force":11.5133,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4090.0,"raw_peak_contact_force":922.99815,"subtask_id":"grasp_success","tcp_end":[0.51178,0.02559,0.00768],"tcp_start":[0.52995,-0.01562,0.20141],"tcp_to_object_dist_end":0.03367,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51068,0.04247,0.01528],"object_pos_start":[0.51886,0.0068,0.0347],"object_to_goal_dist_end":0.28491,"object_to_goal_dist_start":0.29498,"object_z_max":0.03727,"peak_contact_force":66.79085,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9401.0,"raw_peak_contact_force":204.03613,"tcp_end":[0.51144,0.03341,0.00981],"tcp_start":[0.51178,0.02559,0.00768],"tcp_to_object_dist_end":0.0106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.50511,0.04377,0.15587],"object_pos_start":[0.51068,0.04247,0.01528],"object_to_goal_dist_end":0.21812,"object_to_goal_dist_start":0.28491,"object_z_max":0.15576,"peak_contact_force":0.10243,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30150.0,"raw_peak_contact_force":47.64312,"subtask_id":"lift_clearance","tcp_end":[0.50742,0.04221,0.17015],"tcp_start":[0.51144,0.03341,0.00981],"tcp_to_object_dist_end":0.01455,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48529,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16748,"descend_1.descend_z_offset":0.02285,"lift_1.lift_height":0.16547,"place_descend_1.place_z_offset":-0.00132,"transport_1.transport_height":0.10894},"optimized_scores":{"best_composite_score":0.09693,"best_fitness_score":0.24693,"best_task_score":0.17454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":62.0,"contact_point_centroid":[0.64861,-0.01458,-0.00345],"force_p95":941.17235,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1251.17832,"mean_force":355.19196,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.60893,-0.00956,-0.01475]},{"body_a":"world","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.55482,0.04806,-9e-05],"force_p95":137.60583,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.41892,"mean_force":75.14238,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60709,-0.03704,0.00107]},{"body_a":"world","body_b":"hand","contact_count":530.0,"contact_point_centroid":[0.55917,0.04618,-0.00012],"force_p95":50.15666,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.31769,"mean_force":48.7846,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.60748,-0.03651,0.00093]},{"body_a":"world","body_b":"left_finger","contact_count":739.0,"contact_point_centroid":[0.61877,-0.051,-0.01425],"force_p95":11.74146,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.96216,"mean_force":6.97845,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.60943,-0.01005,-0.01302]},{"body_a":"world","body_b":"right_finger","contact_count":954.0,"contact_point_centroid":[0.59771,0.02485,-0.00896],"force_p95":19.1241,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22.84572,"mean_force":9.41835,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.60884,-0.01443,-0.00888]},{"body_a":"world","body_b":"left_finger","contact_count":6587.0,"contact_point_centroid":[0.64399,-0.05298,-0.00247],"force_p95":2.58445,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":20.59829,"mean_force":1.23169,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.60752,-0.0365,0.00094]},{"body_a":"world","body_b":"right_finger","contact_count":674.0,"contact_point_centroid":[0.57392,-0.01587,-0.00202],"force_p95":2.92564,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.14766,"mean_force":1.20607,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.6041,-0.03722,0.00503]},{"body_a":"world","body_b":"right_finger","contact_count":7665.0,"contact_point_centroid":[0.57595,-0.01283,-0.00307],"force_p95":2.19708,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.51588,"mean_force":1.35473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.60751,-0.0365,0.00098]},{"body_a":"world","body_b":"left_finger","contact_count":489.0,"contact_point_centroid":[0.63719,-0.05596,-0.00164],"force_p95":2.82257,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.0115,"mean_force":1.66541,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60454,-0.03722,0.00448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":105.0,"contact_point_centroid":[0.56362,-0.0226,0.00917],"force_p95":0.2859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50907,"mean_force":0.13612,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60176,-0.03725,0.00789]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":396.0,"contact_point_centroid":[0.56497,-0.02079,0.00489],"force_p95":0.16213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42767,"mean_force":0.03587,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.60765,-0.03633,0.00098]},{"body_a":"world","body_b":"grasp_target","contact_count":3964.0,"contact_point_centroid":[0.54442,-0.03013,-0.00197],"force_p95":0.13173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2641,"mean_force":0.12187,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.57686,-0.03463,0.07478]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.54523,-0.02947,-0.00199],"force_p95":0.13088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20705,"mean_force":0.12345,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.60751,-0.0365,0.00099]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.5456,-0.02923,-0.00191],"force_p95":0.1347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52208,-0.0157,0.25653]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.60901,-0.02433,0.06078]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3224.0,"contact_point_centroid":[0.57122,-0.03215,0.09524],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01032,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.57019,-0.03385,0.09441]}],"total_contact_groups":16},"final_pose_error":0.04028,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54455,-0.02999,0.02602],"final_tcp_position":[0.55229,-0.03149,0.15189],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9749.26417,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53993,-0.02768,0.20532],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":18.86107,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2495.0,"raw_peak_contact_force":1251.17832,"subtask_id":"grasp_success","tcp_end":[0.60803,-0.03623,0.0062],"tcp_start":[0.53993,-0.02768,0.20532],"tcp_to_object_dist_end":0.06587,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.54513,-0.02955,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26132,"object_to_goal_dist_start":0.26092,"object_z_max":0.0262,"peak_contact_force":50.16055,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":17378.0,"raw_peak_contact_force":86.31769,"tcp_end":[0.60712,-0.03704,0.00102],"tcp_start":[0.60714,-0.03697,0.00101],"tcp_to_object_dist_end":0.06726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54455,-0.02999,0.02602],"object_pos_start":[0.54513,-0.02955,0.02602],"object_to_goal_dist_end":0.26184,"object_to_goal_dist_start":0.26132,"object_z_max":0.02738,"peak_contact_force":9749.26417,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8460.0,"raw_peak_contact_force":138.41892,"subtask_id":"lift_clearance","tcp_end":[0.55229,-0.03149,0.15189],"tcp_start":[0.60712,-0.03704,0.00102],"tcp_to_object_dist_end":0.12612,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```