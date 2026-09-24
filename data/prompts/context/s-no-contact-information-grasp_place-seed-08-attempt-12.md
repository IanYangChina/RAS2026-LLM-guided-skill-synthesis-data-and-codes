## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1112 | 0.17 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0565 | 0.15 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4223 | 0.74 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4265 | 0.76 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3284 | 0.56 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.111) — your mutation base

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

- **Composite score**: 0.111
- **task_score** (E): 0.172
- **fitness_score**: 0.538  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.153
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1115 |
| descend_above | 1.00 | 0.1313 |
| contact_approach | 1.00 | 0.0020 |
| grasp_1 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 0.1297 |
| transport_1 | 0.33 | 0.0865 |
| place_1 | 1.00 | 0.1383 |
| release_1 | 1.00 | 0.0208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.001, 0.196) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 |
| descend_above | descend | 1.00 / step_budget | (0.515, -0.001, 0.196)→(0.517, -0.001, 0.065) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| contact_approach | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.065)→(0.516, -0.001, 0.064) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.064)→(0.508, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.054)→(0.504, -0.001, 0.184) | (0.522, -0.001, 0.026)→(0.515, -0.005, 0.125) | 0.289→0.248 |
| transport_1 | approach | 0.33 / guard_failure | (0.504, -0.001, 0.184)→(0.536, 0.049, 0.247) | (0.515, -0.005, 0.125)→(0.510, 0.000, 0.094) | 0.248→0.267 |
| place_1 | descend | 1.00 / step_budget | (0.560, 0.196, 0.338)→(0.576, 0.223, 0.203) | (0.458, 0.064, 0.016)→(0.458, 0.064, 0.016) | 0.298→0.298 |
| release_1 | release | 1.00 / step_budget | (0.576, 0.223, 0.203)→(0.571, 0.221, 0.223) | (0.458, 0.064, 0.016)→(0.458, 0.064, 0.016) | 0.298→0.298 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.221
- phase_score: 0.158
- phase_breakdown.reach_object_score: 0.528
- phase_breakdown.place_at_goal_score: 0.000
- grasp_place_fitness: 0.565

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.565
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.221
- **Median Q (composite search score)**: 0.118
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.398


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65639,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13421,"contact_approach.contact_force_threshold":11.45051,"descend_above.descend_height":0.03045,"lift_1.lift_height":0.11047,"place_1.place_offset_z":-0.03962,"place_1.place_speed":0.09309,"transport_1.arc_height":0.20049,"transport_1.transport_speed":0.04719},"optimized_scores":{"best_composite_score":0.06415,"best_fitness_score":0.51915,"best_task_score":0.13721},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3598.0,"contact_point_centroid":[0.45762,0.06343,-0.00223],"force_p95":0.12397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15924,"mean_force":0.13278,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49265,0.09026,0.28741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.46932,0.02781,0.14389],"force_p95":0.25433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34271,"mean_force":0.1463,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46597,0.04573,0.1492]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.48067,0.04606,-0.00147],"force_p95":0.26364,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2996,"mean_force":0.06555,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46932,0.04654,0.05772]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":266.0,"contact_point_centroid":[0.46935,0.06221,0.14631],"force_p95":0.20271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29878,"mean_force":0.09364,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46525,0.04514,0.15098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3000.0,"contact_point_centroid":[0.46846,0.06468,0.09393],"force_p95":0.14947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29364,"mean_force":0.09953,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46719,0.04632,0.09792]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2852.0,"contact_point_centroid":[0.46765,0.02789,0.09352],"force_p95":0.15008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28579,"mean_force":0.10123,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46718,0.04632,0.09764]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04866,-0.00214],"force_p95":0.16554,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21799,"mean_force":0.13288,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47163,0.04678,0.05741]},{"body_a":"world","body_b":"grasp_target","contact_count":828.0,"contact_point_centroid":[0.4827,0.04873,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49154,0.01873,0.2499]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_above","phase_type":"descend","tcp_position_centroid":[0.47969,0.04325,0.13049]},{"body_a":"world","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.47833,0.0474,0.06479]},{"body_a":"world","body_b":"grasp_target","contact_count":1212.0,"contact_point_centroid":[0.45759,0.06355,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56732,0.20881,0.27072]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45759,0.06355,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57202,0.22145,0.2032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2653.0,"contact_point_centroid":[0.46972,0.02791,0.05259],"force_p95":0.0982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11727,"mean_force":0.07641,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47054,0.04667,0.05626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3039.0,"contact_point_centroid":[0.47045,0.06543,0.0528],"force_p95":0.09506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09546,"mean_force":0.06863,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47055,0.04667,0.05627]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3541.0,"contact_point_centroid":[0.49589,0.09474,0.298],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01054,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49554,0.09472,0.29577]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1302.0,"contact_point_centroid":[0.56789,0.20886,0.27284],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01038,"phase_index":6.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56733,0.20884,0.27062]}],"total_contact_groups":17},"final_pose_error":0.01474,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.45759,0.06355,0.01602],"final_tcp_position":[0.57591,0.223,0.203],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.48326,0.03933,0.19736],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1716,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_above","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.47857,0.0474,0.06521],"tcp_start":[0.48326,0.03933,0.19736],"tcp_to_object_dist_end":0.03943,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":5.0,"n_steps_budget":600.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_object","tcp_end":[0.47802,0.04739,0.06421],"tcp_start":[0.47857,0.0474,0.06521],"tcp_to_object_dist_end":0.0385,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04747,0.0255],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29114,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.47051,0.04667,0.05623],"tcp_start":[0.47802,0.04739,0.06421],"tcp_to_object_dist_end":0.03306,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":283.0,"n_steps_budget":720.0,"object_pos_end":[0.47388,0.04717,0.11117],"object_pos_start":[0.48268,0.04747,0.0255],"object_to_goal_dist_end":0.24271,"object_to_goal_dist_start":0.29114,"object_z_max":0.11089,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.46695,0.0463,0.14732],"tcp_start":[0.47051,0.04667,0.05623],"tcp_to_object_dist_end":0.03682,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45759,0.06355,0.01602],"object_pos_start":[0.47388,0.04717,0.11117],"object_to_goal_dist_end":0.29794,"object_to_goal_dist_start":0.24271,"object_z_max":0.11456,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.56026,0.196,0.33774],"tcp_start":[0.46695,0.0463,0.14732],"tcp_to_object_dist_end":0.36275,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.45759,0.06355,0.01602],"object_pos_start":[0.45759,0.06355,0.01602],"object_to_goal_dist_end":0.29794,"object_to_goal_dist_start":0.29794,"object_z_max":0.01602,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.57591,0.223,0.203],"tcp_start":[0.56026,0.196,0.33774],"tcp_to_object_dist_end":0.27274,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45759,0.06355,0.01602],"object_pos_start":[0.45759,0.06355,0.01602],"object_to_goal_dist_end":0.29794,"object_to_goal_dist_start":0.29794,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.57073,0.22082,0.22302],"tcp_start":[0.57591,0.223,0.203],"tcp_to_object_dist_end":0.28352,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86772,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.01975,"contact_approach.contact_force_threshold":5.32705,"descend_above.descend_height":0.03212,"lift_1.lift_height":0.17253,"place_1.place_offset_z":-0.03472,"place_1.place_speed":0.03575,"transport_1.arc_height":0.16986,"transport_1.transport_speed":0.19554},"optimized_scores":{"best_composite_score":0.1177,"best_fitness_score":0.53104,"best_task_score":0.15884},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":4198.0,"contact_point_centroid":[0.52269,-0.00231,0.11465],"force_p95":0.15663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33109,"mean_force":0.10722,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51887,-0.02059,0.11806]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.53492,-0.02039,-0.00135],"force_p95":0.26866,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28811,"mean_force":0.06186,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52128,-0.02065,0.05605]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4432.0,"contact_point_centroid":[0.52263,-0.03877,0.11785],"force_p95":0.14325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28144,"mean_force":0.10235,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51889,-0.02059,0.12154]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02127,-0.00205],"force_p95":0.13961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18091,"mean_force":0.12685,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52378,-0.0207,0.05612]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.53702,-0.02132,-0.00186],"force_p95":0.13695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51183,-0.00797,0.25075]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_above","phase_type":"descend","tcp_position_centroid":[0.52798,-0.019,0.13039]},{"body_a":"world","body_b":"grasp_target","contact_count":32.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.53112,-0.02083,0.06541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.52364,-0.00192,0.05171],"force_p95":0.09783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10521,"mean_force":0.07624,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52259,-0.02067,0.05471]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2954.0,"contact_point_centroid":[0.52329,-0.03936,0.05152],"force_p95":0.09291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09299,"mean_force":0.06982,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5226,-0.02067,0.05472]}],"total_contact_groups":9},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53143,-0.02733,0.13759],"final_tcp_position":[0.51925,-0.02059,0.2075],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52707,-0.01726,0.19646],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17078,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_above","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.5315,-0.02081,0.06619],"tcp_start":[0.52707,-0.01726,0.19646],"tcp_to_object_dist_end":0.04056,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_object","tcp_end":[0.53074,-0.02083,0.06445],"tcp_start":[0.5315,-0.02081,0.06619],"tcp_to_object_dist_end":0.03894,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02086,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3165,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.52257,-0.02067,0.05468],"tcp_start":[0.53074,-0.02083,0.06445],"tcp_to_object_dist_end":0.03226,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.53143,-0.02733,0.13759],"object_pos_start":[0.53696,-0.02086,0.02581],"object_to_goal_dist_end":0.27598,"object_to_goal_dist_start":0.3165,"object_z_max":0.15819,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51925,-0.02059,0.2075],"tcp_start":[0.52257,-0.02067,0.05468],"tcp_to_object_dist_end":0.07129,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.53143,-0.02733,0.13759],"object_pos_start":[0.53143,-0.02733,0.13759],"object_to_goal_dist_end":0.27598,"object_to_goal_dist_start":0.27598,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.51925,-0.02059,0.2075],"tcp_start":[0.51925,-0.02059,0.2075],"tcp_to_object_dist_end":0.07129,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81818,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15124,"contact_approach.contact_force_threshold":14.36744,"descend_above.descend_height":0.03065,"lift_1.lift_height":0.16479,"place_1.place_offset_z":-0.02118,"place_1.place_speed":0.10458,"transport_1.arc_height":0.15629,"transport_1.transport_speed":0.08764},"optimized_scores":{"best_composite_score":0.15163,"best_fitness_score":0.56496,"best_task_score":0.22139},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":3794.0,"contact_point_centroid":[0.53115,-0.00992,0.10658],"force_p95":0.16416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36669,"mean_force":0.11321,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52693,-0.02817,0.10926]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.54358,-0.02775,-0.00143],"force_p95":0.29119,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32342,"mean_force":0.06614,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52925,-0.02825,0.05336]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4820.0,"contact_point_centroid":[0.5306,-0.04625,0.11072],"force_p95":0.14624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29796,"mean_force":0.09274,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52688,-0.02817,0.113]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02916,-0.00211],"force_p95":0.15102,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18873,"mean_force":0.1308,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53185,-0.02834,0.05328]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51621,-0.01146,0.24859]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_above","phase_type":"descend","tcp_position_centroid":[0.53588,-0.02616,0.12908]},{"body_a":"world","body_b":"grasp_target","contact_count":48.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":2.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.53937,-0.02855,0.06335]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3622.0,"contact_point_centroid":[0.53316,-0.00942,0.0508],"force_p95":0.10619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11687,"mean_force":0.06011,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53065,-0.0283,0.05183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4082.0,"contact_point_centroid":[0.53194,-0.04705,0.05085],"force_p95":0.08994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09485,"mean_force":0.05292,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53065,-0.0283,0.05183]}],"total_contact_groups":9},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54011,-0.03532,0.12739],"final_tcp_position":[0.52717,-0.02817,0.19695],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.53452,-0.02387,0.19556],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16998,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"descend_above","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.5399,-0.02854,0.06459],"tcp_start":[0.53452,-0.02387,0.19556],"tcp_to_object_dist_end":0.039,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_object","tcp_end":[0.53893,-0.02856,0.0619],"tcp_start":[0.5399,-0.02854,0.06459],"tcp_to_object_dist_end":0.0365,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54563,-0.02848,0.02547],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26068,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_object","tcp_end":[0.53062,-0.0283,0.05179],"tcp_start":[0.53893,-0.02856,0.0619],"tcp_to_object_dist_end":0.03031,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.54011,-0.03532,0.12739],"object_pos_start":[0.54563,-0.02848,0.02547],"object_to_goal_dist_end":0.22617,"object_to_goal_dist_start":0.26068,"object_z_max":0.14941,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.52717,-0.02817,0.19695],"tcp_start":[0.53062,-0.0283,0.05179],"tcp_to_object_dist_end":0.07111,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.54011,-0.03532,0.12739],"object_pos_start":[0.54011,-0.03532,0.12739],"object_to_goal_dist_end":0.22617,"object_to_goal_dist_start":0.22617,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.52717,-0.02817,0.19695],"tcp_start":[0.52717,-0.02817,0.19695],"tcp_to_object_dist_end":0.07111,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```