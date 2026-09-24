## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.5684 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4852 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.5685 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.5685 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4852 | 1.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5370249203970084, -0.021318279091244466, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5370249203970084, -0.021318279091244466, 0.03]
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | approach/contact targets near object start |
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

## Current Skill (Q=0.568) — your mutation base

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
- id: transport_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_above
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: quat
      quat:
      - 0.0
      - 1.0
      - 0.0
      - 0.0
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_grasp
- id: descend_grasp
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_grasp
- id: grasp_object
  type: grasp
  generator: linear_cartesian
  control: impedance_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.005
  subtask_id: pre_grasp
- id: lift_clear
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_clear_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_grasp
- id: transport_to_goal
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
    - 0.2
    tolerance: 0.025
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_goal
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
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
    place_height:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=quat, quat=[0.0, 1.0, 0.0, 0.0], tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.005]
- **lift_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_clear_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.025
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.568
- **task_score** (E): 1.000
- **fitness_score**: 0.972  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.0305 |
| descend_grasp | 1.00 | 1.00 | 0.2306 |
| grasp_object | 1.00 | 1.00 | 0.0168 |
| lift_clear | 1.00 | 1.00 | 0.0986 |
| transport_to_goal | 1.00 | 1.00 | 0.2693 |
| descend_place | 1.00 | 1.00 | 0.0923 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.011, 0.284) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 13.831 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.510, -0.011, 0.284)→(0.510, -0.016, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp_object | grasp | 1.00 / condition_met | (0.510, -0.016, 0.054)→(0.503, -0.016, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.135 | 0.176 |
| lift_clear | lift | 1.00 / step_budget | (0.503, -0.016, 0.039)→(0.499, -0.016, 0.138) | (0.515, -0.016, 0.026)→(0.506, -0.016, 0.118) | 0.270→0.240 | 1.00 / 37.667 | 0.078 | 0.478 |
| transport_to_goal | approach | 1.00 / step_budget | (0.499, -0.016, 0.138)→(0.608, 0.169, 0.288) | (0.506, -0.016, 0.118)→(0.615, 0.169, 0.264) | 0.240→0.096 | 1.00 / 33.667 | 0.089 | 0.119 |
| descend_place | descend | 1.00 / step_budget | (0.608, 0.169, 0.288)→(0.613, 0.179, 0.196) | (0.615, 0.169, 0.264)→(0.619, 0.179, 0.170) | 0.096→0.005 | 1.00 / 27.000 | 0.108 | 0.277 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.636
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.852
- phase_breakdown.pre_grasp_score: 0.705
- phase_breakdown.transport_goal_score: 0.889
- grasp_place_fitness: 0.972

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.972
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.568
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: transport_to_goal.transport_height
- **Final σ (mean)**: 0.317


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8198,"average_solve_count":394.0,"average_success_count":394.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06007,"descend_grasp.speed":0.05632,"descend_place.place_height":0.01655,"descend_place.speed":0.01408,"grasp_object.speed":0.02504,"lift_clear.lift_clear_height":0.11363,"lift_clear.speed":0.05813,"transport_to_goal.speed":0.06039,"transport_to_goal.transport_height":0.16294},"optimized_scores":{"best_composite_score":0.5683,"best_fitness_score":0.97163,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":206.0,"contact_point_centroid":[0.53234,-0.02026,-0.00119],"force_p95":0.28905,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50399,"mean_force":0.08902,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52232,-0.02062,0.04029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19649.0,"contact_point_centroid":[0.52011,-0.00144,0.08888],"force_p95":0.07719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31687,"mean_force":0.05131,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51994,-0.02056,0.0869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19754.0,"contact_point_centroid":[0.52018,-0.03968,0.08704],"force_p95":0.07566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29665,"mean_force":0.05145,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51995,-0.02056,0.08527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4683.0,"contact_point_centroid":[0.61084,0.23813,0.29498],"force_p95":0.09551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25793,"mean_force":0.06938,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60509,0.21925,0.29303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4855.0,"contact_point_centroid":[0.61049,0.20032,0.29801],"force_p95":0.09266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20036,"mean_force":0.06591,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60503,0.219,0.29603]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53704,-0.02117,-0.00206],"force_p95":0.1404,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18232,"mean_force":0.12751,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52541,-0.02068,0.04042]},{"body_a":"world","body_b":"grasp_target","contact_count":300.0,"contact_point_centroid":[0.53702,-0.02132,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12447,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50886,-0.00551,0.29258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4102.0,"contact_point_centroid":[0.52459,-0.00146,0.04149],"force_p95":0.07766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13059,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5243,-0.02066,0.03869]},{"body_a":"world","body_b":"grasp_target","contact_count":3036.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52445,-0.01647,0.16727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17020.0,"contact_point_centroid":[0.55986,0.07291,0.23515],"force_p95":0.07858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11923,"mean_force":0.05128,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5586,0.09193,0.23372]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16028.0,"contact_point_centroid":[0.56288,0.11692,0.24135],"force_p95":0.07738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11582,"mean_force":0.0537,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56079,0.09782,0.23928]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.5247,-0.03975,0.04055],"force_p95":0.07004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07912,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5243,-0.02066,0.03869]}],"total_contact_groups":12},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61458,0.22461,0.2061],"final_tcp_position":[0.60671,0.22472,0.23261],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.50399,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":76.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02594],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12235,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":300.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.51984,-0.01228,0.28402],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02594],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31677,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3036.0,"raw_peak_contact_force":0.12264,"subtask_id":"pre_grasp","tcp_end":[0.53136,-0.02069,0.05398],"tcp_start":[0.51984,-0.01228,0.28402],"tcp_to_object_dist_end":0.02853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":51.0,"n_steps_budget":720.0,"object_pos_end":[0.53694,-0.02065,0.02578],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31635,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13704,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10820.0,"raw_peak_contact_force":0.18232,"subtask_id":"pre_grasp","tcp_end":[0.52427,-0.02066,0.03866],"tcp_start":[0.53136,-0.02069,0.05398],"tcp_to_object_dist_end":0.01807,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52637,-0.02059,0.11194],"object_pos_start":[0.53694,-0.02065,0.02578],"object_to_goal_dist_end":0.27899,"object_to_goal_dist_start":0.31635,"object_z_max":0.11184,"peak_contact_force":0.07643,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39609.0,"raw_peak_contact_force":0.50399,"subtask_id":"pre_grasp","tcp_end":[0.52005,-0.02056,0.13198],"tcp_start":[0.52427,-0.02066,0.03866],"tcp_to_object_dist_end":0.02101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":875.0,"n_steps_budget":1000.0,"object_pos_end":[0.6126,0.21533,0.32598],"object_pos_start":[0.52637,-0.02059,0.11194],"object_to_goal_dist_end":0.11924,"object_to_goal_dist_start":0.27899,"object_z_max":0.32576,"peak_contact_force":0.09716,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33048.0,"raw_peak_contact_force":0.11923,"subtask_id":"transport_goal","tcp_end":[0.60468,0.21489,0.34994],"tcp_start":[0.52005,-0.02056,0.13198],"tcp_to_object_dist_end":0.02524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.61458,0.22461,0.2061],"object_pos_start":[0.6126,0.21533,0.32598],"object_to_goal_dist_end":0.00546,"object_to_goal_dist_start":0.11924,"object_z_max":0.3261,"peak_contact_force":0.09963,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9538.0,"raw_peak_contact_force":0.25793,"subtask_id":"transport_goal","tcp_end":[0.60671,0.22472,0.23261],"tcp_start":[0.60468,0.21489,0.34994],"tcp_to_object_dist_end":0.02766,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63284,0.16493,0.17692]},{"name":"goal","value":[0.5456,-0.02923,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.71111,"average_solve_count":405.0,"average_success_count":405.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.0535,"descend_grasp.speed":0.05194,"descend_place.place_height":0.01976,"descend_place.speed":0.01789,"grasp_object.speed":0.02667,"lift_clear.lift_clear_height":0.12162,"lift_clear.speed":0.06318,"transport_to_goal.speed":0.0356,"transport_to_goal.transport_height":0.14889},"optimized_scores":{"best_composite_score":0.56843,"best_fitness_score":0.97176,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.54177,-0.02802,-0.00121],"force_p95":0.2841,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51539,"mean_force":0.08562,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.5308,-0.02831,0.04001]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17307.0,"contact_point_centroid":[0.52943,-0.00916,0.08992],"force_p95":0.08608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32117,"mean_force":0.05823,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52827,-0.02822,0.08776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18350.0,"contact_point_centroid":[0.52947,-0.04721,0.08878],"force_p95":0.08154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3043,"mean_force":0.05566,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52829,-0.02822,0.08706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2958.0,"contact_point_centroid":[0.63149,0.17483,0.26374],"force_p95":0.15357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25734,"mean_force":0.09385,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6254,0.15625,0.26338]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3408.0,"contact_point_centroid":[0.63148,0.13829,0.26038],"force_p95":0.12051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24936,"mean_force":0.08078,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6255,0.1565,0.26037]},{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.54562,-0.02906,-0.00208],"force_p95":0.14479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19964,"mean_force":0.12866,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53383,-0.02841,0.04014]},{"body_a":"world","body_b":"grasp_target","contact_count":416.0,"contact_point_centroid":[0.5456,-0.02923,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12383,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51309,-0.00905,0.29089]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9605.0,"contact_point_centroid":[0.57769,0.08059,0.2215],"force_p95":0.1049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13679,"mean_force":0.07091,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57455,0.06167,0.22038]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.53305,-0.00917,0.04114],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13375,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53269,-0.02838,0.03833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11253.0,"contact_point_centroid":[0.57808,0.04335,0.2214],"force_p95":0.08654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12817,"mean_force":0.06156,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57475,0.06204,0.22072]},{"body_a":"world","body_b":"grasp_target","contact_count":2984.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53299,-0.0239,0.16617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4936.0,"contact_point_centroid":[0.53314,-0.04748,0.04018],"force_p95":0.0709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07842,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53269,-0.02838,0.03834]}],"total_contact_groups":12},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63334,0.16201,0.17622],"final_tcp_position":[0.62825,0.16198,0.20496],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":41.24276,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":105.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":41.24276,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":416.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52844,-0.01939,0.28158],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2984.0,"raw_peak_contact_force":0.12264,"subtask_id":"pre_grasp","tcp_end":[0.53985,-0.02848,0.05416],"tcp_start":[0.52844,-0.01939,0.28158],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":52.0,"n_steps_budget":690.0,"object_pos_end":[0.54552,-0.02841,0.02573],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26051,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14057,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10839.0,"raw_peak_contact_force":0.19964,"subtask_id":"pre_grasp","tcp_end":[0.53266,-0.02837,0.0383],"tcp_start":[0.53985,-0.02848,0.05416],"tcp_to_object_dist_end":0.01798,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5375,-0.02822,0.11999],"object_pos_start":[0.54552,-0.02841,0.02573],"object_to_goal_dist_end":0.2228,"object_to_goal_dist_start":0.26051,"object_z_max":0.11987,"peak_contact_force":0.09208,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35849.0,"raw_peak_contact_force":0.51539,"subtask_id":"pre_grasp","tcp_end":[0.52839,-0.02822,0.14067],"tcp_start":[0.53266,-0.02837,0.0383],"tcp_to_object_dist_end":0.0226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":717.0,"n_steps_budget":1000.0,"object_pos_end":[0.63208,0.15268,0.28047],"object_pos_start":[0.5375,-0.02822,0.11999],"object_to_goal_dist_end":0.10428,"object_to_goal_dist_start":0.2228,"object_z_max":0.28027,"peak_contact_force":0.09523,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20858.0,"raw_peak_contact_force":0.13679,"subtask_id":"transport_goal","tcp_end":[0.62476,0.15262,0.30587],"tcp_start":[0.52839,-0.02822,0.14067],"tcp_to_object_dist_end":0.02643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.63334,0.16201,0.17622],"object_pos_start":[0.63208,0.15268,0.28047],"object_to_goal_dist_end":0.00304,"object_to_goal_dist_start":0.10428,"object_z_max":0.28061,"peak_contact_force":0.15441,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6366.0,"raw_peak_contact_force":0.25734,"subtask_id":"transport_goal","tcp_end":[0.62825,0.16198,0.20496],"tcp_start":[0.62476,0.15262,0.30587],"tcp_to_object_dist_end":0.02919,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61015,0.15287,0.12219]},{"name":"goal","value":[0.46286,-7e-05,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97281,"average_solve_count":331.0,"average_success_count":331.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04251,"descend_grasp.speed":0.08905,"descend_place.place_height":0.02423,"descend_place.speed":0.01261,"grasp_object.speed":0.02152,"lift_clear.lift_clear_height":0.11833,"lift_clear.speed":0.03045,"transport_to_goal.speed":0.07783,"transport_to_goal.transport_height":0.1},"optimized_scores":{"best_composite_score":0.56861,"best_fitness_score":0.97195,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.45822,-0.00037,-0.00121],"force_p95":0.36248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41322,"mean_force":0.09819,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.45145,-0.0002,0.04224]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3929.0,"contact_point_centroid":[0.59844,0.16318,0.1829],"force_p95":0.07158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31613,"mean_force":0.05143,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5973,0.14399,0.1808]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20104.0,"contact_point_centroid":[0.44921,0.01894,0.09314],"force_p95":0.07205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2446,"mean_force":0.04979,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44903,-0.00021,0.09121]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20110.0,"contact_point_centroid":[0.44922,-0.01935,0.09317],"force_p95":0.07203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24221,"mean_force":0.04973,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44903,-0.00021,0.09122]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4096.0,"contact_point_centroid":[0.59771,0.12495,0.18261],"force_p95":0.06935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18205,"mean_force":0.04858,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59733,0.14402,0.18056]},{"body_a":"world","body_b":"grasp_target","contact_count":1848.0,"contact_point_centroid":[0.46285,-9e-05,-0.00202],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14636,"mean_force":0.12429,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45404,-0.00017,0.04247]},{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.46286,-7e-05,-0.00136],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12472,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49145,-5e-05,0.29469]},{"body_a":"world","body_b":"grasp_target","contact_count":2892.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12666,"mean_force":0.12265,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4693,-8e-05,0.16998]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10354.0,"contact_point_centroid":[0.52036,0.08816,0.17524],"force_p95":0.07072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10184,"mean_force":0.04885,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51963,0.06891,0.17243]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11926.0,"contact_point_centroid":[0.52036,0.05045,0.1754],"force_p95":0.06368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09886,"mean_force":0.04299,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52033,0.06959,0.17276]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45304,0.01902,0.04272],"force_p95":0.068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08867,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45293,-0.00018,0.04083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4860.0,"contact_point_centroid":[0.45305,-0.01937,0.04273],"force_p95":0.06794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08673,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45293,-0.00018,0.04083]}],"total_contact_groups":12},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60808,0.14899,0.12799],"final_tcp_position":[0.60281,0.14904,0.15168],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.41322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02587],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.23316,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12703,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":204.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48083,-7e-05,0.28766],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02587],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23316,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2892.0,"raw_peak_contact_force":0.12666,"subtask_id":"pre_grasp","tcp_end":[0.45984,-0.00011,0.05517],"tcp_start":[0.48083,-7e-05,0.28766],"tcp_to_object_dist_end":0.02931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":62.0,"n_steps_budget":870.0,"object_pos_end":[0.46276,-0.00015,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12802,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11572.0,"raw_peak_contact_force":0.14636,"subtask_id":"pre_grasp","tcp_end":[0.45291,-0.00018,0.0408],"tcp_start":[0.45984,-0.00011,0.05517],"tcp_to_object_dist_end":0.01785,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45402,-0.0002,0.12071],"object_pos_start":[0.46276,-0.00015,0.02592],"object_to_goal_dist_end":0.21865,"object_to_goal_dist_start":0.23325,"object_z_max":0.12063,"peak_contact_force":0.06486,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40378.0,"raw_peak_contact_force":0.41322,"subtask_id":"pre_grasp","tcp_end":[0.44911,-0.0002,0.1408],"tcp_start":[0.45291,-0.00018,0.0408],"tcp_to_object_dist_end":0.02068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.59954,0.14022,0.18561],"object_pos_start":[0.45402,-0.0002,0.12071],"object_to_goal_dist_end":0.06553,"object_to_goal_dist_start":0.21865,"object_z_max":0.18549,"peak_contact_force":0.07448,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22280.0,"raw_peak_contact_force":0.10184,"subtask_id":"transport_goal","tcp_end":[0.59449,0.14004,0.20805],"tcp_start":[0.44911,-0.0002,0.1408],"tcp_to_object_dist_end":0.02301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.60808,0.14899,0.12799],"object_pos_start":[0.59954,0.14022,0.18561],"object_to_goal_dist_end":0.00728,"object_to_goal_dist_start":0.06553,"object_z_max":0.18566,"peak_contact_force":0.07137,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8025.0,"raw_peak_contact_force":0.31613,"subtask_id":"transport_goal","tcp_end":[0.60281,0.14904,0.15168],"tcp_start":[0.59449,0.14004,0.20805],"tcp_to_object_dist_end":0.02427,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```