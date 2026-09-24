## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6368 | 1.00 | ✅ accepted |
| 7 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2065 | 0.29 | ✅ accepted |
| 6 | descend → grasp → lift → descend → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2419 | 0.29 | ❌ rejected |
| 5 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2314 | 0.24 | ❌ rejected |
| 4 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1488 | 0.19 | ❌ rejected |

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

## Current Skill (Q=0.637) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.5
phases:
- id: descend_1
  type: descend
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_grasp
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
  - id: bilateral_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_clear
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_retained
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
- id: descend_2
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
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_retained, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.637
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2654 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.0996 |
| transport_1 | 1.00 | 1.00 | 0.2718 |
| descend_2 | 1.00 | 1.00 | 0.0750 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.039) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.511, -0.001, 0.034)→(0.511, -0.001, 0.034) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 45.667 | 0.166 | 0.252 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.034)→(0.507, -0.001, 0.133) | (0.522, -0.001, 0.025)→(0.521, -0.001, 0.119) | 0.290→0.243 | 1.00 / 28.333 | 524.426 | 0.625 |
| transport_1 | approach | 1.00 / step_budget | (0.507, -0.001, 0.133)→(0.599, 0.190, 0.302) | (0.521, -0.001, 0.119)→(0.606, 0.190, 0.277) | 0.243→0.075 | 1.00 / 21.333 | 0.127 | 0.147 |
| descend_2 | descend | 1.00 / step_budget | (0.599, 0.190, 0.302)→(0.604, 0.205, 0.229) | (0.606, 0.190, 0.277)→(0.606, 0.203, 0.199) | 0.075→0.011 | 1.00 / 18.667 | 50723.746 | 0.253 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.020
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.463
- phase_breakdown.pre_grasp_score: 0.132
- phase_breakdown.lift_clear_score: 0.521
- phase_breakdown.place_score: 0.560
- grasp_place_fitness: 0.987

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.987
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.637
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41553,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00984,"descend_2.place_z_offset":0.00119,"lift_1.lift_height":0.10745,"transport_1.approach_height":0.10073,"transport_1.transport_speed":0.03741},"optimized_scores":{"best_composite_score":0.64655,"best_fitness_score":0.98655,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.47917,0.04373,-0.00142],"force_p95":0.57296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79124,"mean_force":0.09879,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47274,0.04534,0.02627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11408.0,"contact_point_centroid":[0.47093,0.06426,0.07113],"force_p95":0.08337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33946,"mean_force":0.0549,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47035,0.04511,0.06906]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11671.0,"contact_point_centroid":[0.47097,0.02604,0.07279],"force_p95":0.08182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30072,"mean_force":0.0528,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47035,0.04511,0.07077]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48283,0.048,-0.00239],"force_p95":0.21189,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2975,"mean_force":0.15103,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47478,0.04556,0.02448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5452.0,"contact_point_centroid":[0.57542,0.23907,0.26621],"force_p95":0.08876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17967,"mean_force":0.06038,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57437,0.22046,0.26762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5667.0,"contact_point_centroid":[0.47452,0.02632,0.02599],"force_p95":0.08089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15861,"mean_force":0.04549,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47435,0.04551,0.02404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4316.0,"contact_point_centroid":[0.57521,0.20125,0.26808],"force_p95":0.09855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1577,"mean_force":0.07415,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57429,0.22031,0.26882]},{"body_a":"world","body_b":"grasp_target","contact_count":3376.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48845,0.0229,0.16286]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15322.0,"contact_point_centroid":[0.52383,0.15143,0.21604],"force_p95":0.09073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12235,"mean_force":0.06402,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52105,0.13256,0.21527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15000.0,"contact_point_centroid":[0.52069,0.10893,0.21031],"force_p95":0.0951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11952,"mean_force":0.06533,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51813,0.12779,0.2099]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6192.0,"contact_point_centroid":[0.4745,0.06495,0.02595],"force_p95":0.08178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0878,"mean_force":0.04532,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47436,0.04551,0.02405]}],"total_contact_groups":11},"final_pose_error":0.00497,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57697,0.22545,0.21182],"final_tcp_position":[0.57778,0.22605,0.23191],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.79124,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3376.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47914,0.04593,0.029],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04567,0.02486],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29274,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19339,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13663.0,"raw_peak_contact_force":0.2975,"tcp_end":[0.47434,0.0455,0.02402],"tcp_start":[0.47434,0.0455,0.02402],"tcp_to_object_dist_end":0.0083,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.48602,0.0454,0.11485],"object_pos_start":[0.48258,0.04565,0.02492],"object_to_goal_dist_end":0.23709,"object_to_goal_dist_start":0.29271,"object_z_max":0.11475,"peak_contact_force":0.09675,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23229.0,"raw_peak_contact_force":0.79124,"subtask_id":"lift_clear","tcp_end":[0.47036,0.04513,0.12006],"tcp_start":[0.47434,0.0455,0.02402],"tcp_to_object_dist_end":0.0165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58134,0.21553,0.29123],"object_pos_start":[0.48602,0.0454,0.11485],"object_to_goal_dist_end":0.06219,"object_to_goal_dist_start":0.23709,"object_z_max":0.29107,"peak_contact_force":0.09615,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30322.0,"raw_peak_contact_force":0.12235,"tcp_end":[0.57232,0.2154,0.30878],"tcp_start":[0.47036,0.04513,0.12006],"tcp_to_object_dist_end":0.01973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.57697,0.22545,0.21182],"object_pos_start":[0.58134,0.21553,0.29123],"object_to_goal_dist_end":0.0196,"object_to_goal_dist_start":0.06219,"object_z_max":0.29129,"peak_contact_force":0.09226,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9768.0,"raw_peak_contact_force":0.17967,"subtask_id":"place","tcp_end":[0.57778,0.22605,0.23191],"tcp_start":[0.57232,0.2154,0.30878],"tcp_to_object_dist_end":0.02012,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36967,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.0126,"descend_2.place_z_offset":0.04384,"lift_1.lift_height":0.11549,"transport_1.approach_height":0.12804,"transport_1.transport_speed":0.0242},"optimized_scores":{"best_composite_score":0.62634,"best_fitness_score":0.96634,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.53458,-0.01973,-0.0012],"force_p95":0.3112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46681,"mean_force":0.07111,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52373,-0.02003,0.04572]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11663.0,"contact_point_centroid":[0.52282,-0.00092,0.09262],"force_p95":0.0945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29939,"mean_force":0.05852,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52118,-0.01997,0.09025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12377.0,"contact_point_centroid":[0.52294,-0.03898,0.09358],"force_p95":0.08536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28424,"mean_force":0.05613,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52119,-0.01997,0.09162]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8285.0,"contact_point_centroid":[0.60729,0.23184,0.26394],"force_p95":0.12682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28381,"mean_force":0.09871,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60237,0.21358,0.26755]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8705.0,"contact_point_centroid":[0.6073,0.19532,0.26438],"force_p95":0.12132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23588,"mean_force":0.09348,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60237,0.21355,0.26765]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53707,-0.02109,-0.00213],"force_p95":0.15251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21574,"mean_force":0.13242,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52586,-0.02008,0.04449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13878.0,"contact_point_centroid":[0.56128,0.06688,0.22148],"force_p95":0.09483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15123,"mean_force":0.06814,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55655,0.08555,0.22101]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12322.0,"contact_point_centroid":[0.56406,0.10994,0.2258],"force_p95":0.09866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14802,"mean_force":0.07609,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55861,0.09122,0.22523]},{"body_a":"world","body_b":"grasp_target","contact_count":3212.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51409,-0.01003,0.17358]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5581.0,"contact_point_centroid":[0.52495,-0.00082,0.04718],"force_p95":0.07171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10674,"mean_force":0.0469,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52539,-0.02006,0.04395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6566.0,"contact_point_centroid":[0.52482,-0.03928,0.04566],"force_p95":0.06701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06919,"mean_force":0.04133,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5254,-0.02006,0.04395]}],"total_contact_groups":11},"final_pose_error":0.00818,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61159,0.22254,0.20297],"final_tcp_position":[0.60695,0.22549,0.24415],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":152170.99322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":804.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3212.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53042,-0.02013,0.04997],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53698,-0.02031,0.0256],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31617,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14614,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13951.0,"raw_peak_contact_force":0.21574,"tcp_end":[0.52537,-0.02006,0.04392],"tcp_start":[0.52537,-0.02006,0.04392],"tcp_to_object_dist_end":0.02169,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53419,-0.02003,0.12347],"object_pos_start":[0.53699,-0.02029,0.02562],"object_to_goal_dist_end":0.27247,"object_to_goal_dist_start":0.31615,"object_z_max":0.12335,"peak_contact_force":0.08905,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24191.0,"raw_peak_contact_force":0.46681,"subtask_id":"lift_clear","tcp_end":[0.52134,-0.01997,0.14703],"tcp_start":[0.52537,-0.02006,0.04392],"tcp_to_object_dist_end":0.02684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60426,0.19841,0.27435],"object_pos_start":[0.53419,-0.02003,0.12347],"object_to_goal_dist_end":0.07334,"object_to_goal_dist_start":0.27247,"object_z_max":0.2742,"peak_contact_force":0.13391,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26200.0,"raw_peak_contact_force":0.15123,"tcp_end":[0.5982,0.19862,0.30546],"tcp_start":[0.52134,-0.01997,0.14703],"tcp_to_object_dist_end":0.0317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.61159,0.22254,0.20297],"object_pos_start":[0.60426,0.19841,0.27435],"object_to_goal_dist_end":0.00697,"object_to_goal_dist_start":0.07334,"object_z_max":0.27439,"peak_contact_force":152170.99322,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16990.0,"raw_peak_contact_force":0.28381,"subtask_id":"place","tcp_end":[0.60695,0.22549,0.24415],"tcp_start":[0.5982,0.19862,0.30546],"tcp_to_object_dist_end":0.04154,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40455,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00223,"descend_2.place_z_offset":0.03279,"lift_1.lift_height":0.11196,"transport_1.approach_height":0.13012,"transport_1.transport_speed":0.02364},"optimized_scores":{"best_composite_score":0.63742,"best_fitness_score":0.97742,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.54265,-0.02685,-0.00126],"force_p95":0.42609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61807,"mean_force":0.08921,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53162,-0.02751,0.03454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11201.0,"contact_point_centroid":[0.5308,-0.04632,0.07789],"force_p95":0.09867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31777,"mean_force":0.05903,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52903,-0.02742,0.07646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10260.0,"contact_point_centroid":[0.53079,-0.00842,0.07979],"force_p95":0.10288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30947,"mean_force":0.0631,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52904,-0.02742,0.07775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1917.0,"contact_point_centroid":[0.63201,0.17708,0.24523],"force_p95":0.1741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29514,"mean_force":0.13671,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62663,0.15912,0.24821]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54568,-0.02894,-0.00219],"force_p95":0.16609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24216,"mean_force":0.13624,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53383,-0.02759,0.0333]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2538.0,"contact_point_centroid":[0.6319,0.1414,0.24534],"force_p95":0.1488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22189,"mean_force":0.10788,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6266,0.15906,0.24879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11359.0,"contact_point_centroid":[0.57729,0.0779,0.20372],"force_p95":0.12633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16713,"mean_force":0.08065,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57306,0.05942,0.20449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11784.0,"contact_point_centroid":[0.57602,0.03858,0.20177],"force_p95":0.12351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15617,"mean_force":0.07862,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57179,0.05702,0.2024]},{"body_a":"world","body_b":"grasp_target","contact_count":3408.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51821,-0.01384,0.16762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6078.0,"contact_point_centroid":[0.53306,-0.00832,0.0356],"force_p95":0.06953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1169,"mean_force":0.04316,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53335,-0.02756,0.03274]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6625.0,"contact_point_centroid":[0.53292,-0.04687,0.03505],"force_p95":0.06969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07783,"mean_force":0.0413,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53336,-0.02757,0.03274]}],"total_contact_groups":11},"final_pose_error":0.00498,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63081,0.16225,0.18116],"final_tcp_position":[0.6286,0.16274,0.2111],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3408.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53853,-0.0277,0.03893],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54553,-0.02784,0.02545],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26024,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15792,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14507.0,"raw_peak_contact_force":0.24216,"tcp_end":[0.53333,-0.02756,0.03271],"tcp_start":[0.53333,-0.02756,0.03271],"tcp_to_object_dist_end":0.0142,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.54427,-0.02753,0.11764],"object_pos_start":[0.54554,-0.02782,0.02549],"object_to_goal_dist_end":0.22,"object_to_goal_dist_start":0.26021,"object_z_max":0.11753,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21613.0,"raw_peak_contact_force":0.61807,"subtask_id":"lift_clear","tcp_end":[0.52914,-0.02742,0.13209],"tcp_start":[0.53333,-0.02756,0.03271],"tcp_to_object_dist_end":0.02091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":982.0,"n_steps_budget":1000.0,"object_pos_end":[0.63152,0.15604,0.26481],"object_pos_start":[0.54427,-0.02753,0.11764],"object_to_goal_dist_end":0.08834,"object_to_goal_dist_start":0.22,"object_z_max":0.26468,"peak_contact_force":0.15128,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23143.0,"raw_peak_contact_force":0.16713,"tcp_end":[0.62616,0.15583,0.29054],"tcp_start":[0.52914,-0.02742,0.13209],"tcp_to_object_dist_end":0.02629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.63081,0.16225,0.18116],"object_pos_start":[0.63152,0.15604,0.26481],"object_to_goal_dist_end":0.00541,"object_to_goal_dist_start":0.08834,"object_z_max":0.26482,"peak_contact_force":0.15208,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4455.0,"raw_peak_contact_force":0.29514,"subtask_id":"place","tcp_end":[0.6286,0.16274,0.2111],"tcp_start":[0.62616,0.15583,0.29054],"tcp_to_object_dist_end":0.03002,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```