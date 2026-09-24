## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

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

## Current Skill (Q=0.253) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: place_goal
  target_entity: object
  weight: 0.2
phases:
- id: approach_object
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
  subtask_id: approach_object
- id: descend_to_grasp
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.1
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: grasp_object
- id: grasp
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
  subtask_id: grasp_object
- id: lift
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
- id: descend_to_place
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
    - 0.015
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.005
      - 0.1
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.015], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.253
- **task_score** (E): 1.000
- **fitness_score**: 0.973  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1485 |
| descend_to_grasp | 1.00 | 1.00 | 0.1125 |
| grasp | 1.00 | 1.00 | 0.0132 |
| lift | 1.00 | 1.00 | 0.1319 |
| approach_goal | 1.00 | 1.00 | 0.2158 |
| descend_to_place | 1.00 | 1.00 | 0.0124 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.000, 0.158) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.515, -0.000, 0.158)→(0.516, -0.001, 0.045) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.045)→(0.508, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.289 | 1.00 / 41.667 | 0.160 | 0.238 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.035)→(0.516, -0.001, 0.167) | (0.522, -0.001, 0.025)→(0.531, -0.001, 0.154) | 0.289→0.228 | 1.00 / 33.000 | 0.097 | 0.515 |
| approach_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.167)→(0.597, 0.186, 0.238) | (0.531, -0.001, 0.154)→(0.607, 0.186, 0.219) | 0.228→0.026 | 1.00 / 28.333 | 0.111 | 0.133 |
| descend_to_place | descend | 1.00 / step_budget | (0.597, 0.186, 0.238)→(0.600, 0.193, 0.228) | (0.607, 0.186, 0.219)→(0.610, 0.193, 0.209) | 0.026→0.016 | 1.00 / 26.000 | 0.117 | 0.313 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.201
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.601
- phase_breakdown.place_goal_score: 0.549
- phase_breakdown.lift_object_score: 0.756
- phase_breakdown.approach_object_score: 0.554
- phase_breakdown.approach_goal_score: 0.551
- phase_breakdown.grasp_object_score: 0.597
- grasp_place_fitness: 0.973

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.973
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.253
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.339


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.05556,"approach_goal.approach_goal_tolerance":0.03751,"approach_object.approach_speed":0.14312,"approach_object.approach_tolerance":0.03073,"descend_to_grasp.descend_speed":0.05128,"descend_to_grasp.grasp_offset_z":0.00066,"descend_to_grasp.grasp_tolerance":0.0185,"descend_to_place.descend_place_speed":0.06622,"descend_to_place.place_tolerance":0.02217,"lift.lift_height":0.1976,"lift.lift_speed":0.0489,"lift.lift_tolerance":0.0191},"optimized_scores":{"best_composite_score":0.25323,"best_fitness_score":0.97323,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.48021,0.04607,-0.00175],"force_p95":0.48677,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52458,"mean_force":0.19224,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46984,0.04567,0.03844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6757.0,"contact_point_centroid":[0.47297,0.06496,0.11596],"force_p95":0.08232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30337,"mean_force":0.05298,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47312,0.04575,0.11427]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":586.0,"contact_point_centroid":[0.57101,0.22999,0.26259],"force_p95":0.10444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28209,"mean_force":0.06092,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56993,0.21075,0.26056]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04842,-0.00225],"force_p95":0.19265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26373,"mean_force":0.14106,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47194,0.04589,0.03843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6774.0,"contact_point_centroid":[0.47281,0.02657,0.11489],"force_p95":0.07923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26311,"mean_force":0.05171,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47303,0.04575,0.113]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":598.0,"contact_point_centroid":[0.57124,0.19205,0.26252],"force_p95":0.08308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18292,"mean_force":0.0551,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57008,0.21099,0.26021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4376.0,"contact_point_centroid":[0.47163,0.02659,0.03992],"force_p95":0.07978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15828,"mean_force":0.04876,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47085,0.04579,0.03732]},{"body_a":"world","body_b":"grasp_target","contact_count":796.0,"contact_point_centroid":[0.4827,0.04873,-0.00184],"force_p95":0.13736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49211,0.01859,0.23105]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4804,0.0426,0.10222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7967.0,"contact_point_centroid":[0.52238,0.10678,0.22817],"force_p95":0.0746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1026,"mean_force":0.04971,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52198,0.12577,0.22614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6861.0,"contact_point_centroid":[0.523,0.14595,0.22915],"force_p95":0.07975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09502,"mean_force":0.05675,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52257,0.12679,0.22663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5166.0,"contact_point_centroid":[0.47107,0.06516,0.03917],"force_p95":0.0782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08307,"mean_force":0.04431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47086,0.04579,0.03733]}],"total_contact_groups":12},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58285,0.21483,0.23808],"final_tcp_position":[0.57221,0.21461,0.25506],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.52458,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":796.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48382,0.03896,0.15781],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":904.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47897,0.04653,0.04589],"tcp_start":[0.48382,0.03896,0.15781],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48267,0.04647,0.02514],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29201,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18077,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11342.0,"raw_peak_contact_force":0.26373,"subtask_id":"grasp_object","tcp_end":[0.47082,0.04578,0.03729],"tcp_start":[0.47897,0.04653,0.04589],"tcp_to_object_dist_end":0.01699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.48899,0.04635,0.17885],"object_pos_start":[0.48267,0.04647,0.02514],"object_to_goal_dist_end":0.21119,"object_to_goal_dist_start":0.29201,"object_z_max":0.17838,"peak_contact_force":0.08641,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13609.0,"raw_peak_contact_force":0.52458,"subtask_id":"lift_object","tcp_end":[0.47838,0.04606,0.19306],"tcp_start":[0.47082,0.04578,0.03729],"tcp_to_object_dist_end":0.01773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.57752,0.20818,0.2463],"object_pos_start":[0.48899,0.04635,0.17885],"object_to_goal_dist_end":0.02639,"object_to_goal_dist_start":0.21119,"object_z_max":0.24613,"peak_contact_force":0.07807,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14828.0,"raw_peak_contact_force":0.1026,"subtask_id":"approach_goal","tcp_end":[0.5688,0.20821,0.26348],"tcp_start":[0.47838,0.04606,0.19306],"tcp_to_object_dist_end":0.01927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.58285,0.21483,0.23808],"object_pos_start":[0.57752,0.20818,0.2463],"object_to_goal_dist_end":0.01598,"object_to_goal_dist_start":0.02639,"object_z_max":0.24638,"peak_contact_force":0.07991,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1184.0,"raw_peak_contact_force":0.28209,"subtask_id":"place_goal","tcp_end":[0.57221,0.21461,0.25506],"tcp_start":[0.5688,0.20821,0.26348],"tcp_to_object_dist_end":0.02004,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88919,"average_solve_count":370.0,"average_success_count":370.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.04877,"approach_goal.approach_goal_tolerance":0.0321,"approach_object.approach_speed":0.02413,"approach_object.approach_tolerance":0.03318,"descend_to_grasp.descend_speed":0.05384,"descend_to_grasp.grasp_offset_z":5e-05,"descend_to_grasp.grasp_tolerance":0.01836,"descend_to_place.descend_place_speed":0.05951,"descend_to_place.place_tolerance":0.02709,"lift.lift_height":0.16854,"lift.lift_speed":0.05131,"lift.lift_tolerance":0.01805},"optimized_scores":{"best_composite_score":0.25259,"best_fitness_score":0.97259,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.53489,-0.02018,-0.00159],"force_p95":0.47275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51113,"mean_force":0.17402,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52098,-0.02027,0.03547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4928.0,"contact_point_centroid":[0.52617,-0.00108,0.10065],"force_p95":0.08599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2958,"mean_force":0.06193,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52507,-0.02024,0.09804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5654.0,"contact_point_centroid":[0.52599,-0.03925,0.09844],"force_p95":0.08192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28491,"mean_force":0.05595,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52493,-0.02024,0.09662]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.60498,0.22684,0.23875],"force_p95":0.13646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25201,"mean_force":0.08218,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60171,0.20772,0.2378]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02112,-0.00209],"force_p95":0.15029,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21699,"mean_force":0.12999,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52317,-0.02031,0.03594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":476.0,"contact_point_centroid":[0.60518,0.18917,0.23809],"force_p95":0.09379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18243,"mean_force":0.06634,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60172,0.20774,0.23777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4086.0,"contact_point_centroid":[0.52319,-0.00108,0.03726],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13924,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52197,-0.02029,0.03458]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51199,-0.00781,0.23324]},{"body_a":"world","body_b":"grasp_target","contact_count":888.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52772,-0.01868,0.10143]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9224.0,"contact_point_centroid":[0.56517,0.06847,0.20017],"force_p95":0.08253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11448,"mean_force":0.05433,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56343,0.08734,0.19896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7857.0,"contact_point_centroid":[0.5654,0.10623,0.20076],"force_p95":0.09195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10672,"mean_force":0.06191,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56337,0.08715,0.1989]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4957.0,"contact_point_centroid":[0.52312,-0.03941,0.03635],"force_p95":0.07143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08137,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52197,-0.02029,0.03459]}],"total_contact_groups":12},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61557,0.21226,0.21446],"final_tcp_position":[0.60315,0.21194,0.2321],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.51113,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":896.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52701,-0.01703,0.15762],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":888.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53083,-0.02042,0.04503],"tcp_start":[0.52701,-0.01703,0.15762],"tcp_to_object_dist_end":0.02002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53693,-0.02034,0.02568],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31617,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14495,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10843.0,"raw_peak_contact_force":0.21699,"subtask_id":"grasp_object","tcp_end":[0.52194,-0.02029,0.03454],"tcp_start":[0.53083,-0.02042,0.04503],"tcp_to_object_dist_end":0.01742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.54491,-0.02031,0.15295],"object_pos_start":[0.53693,-0.02034,0.02568],"object_to_goal_dist_end":0.26226,"object_to_goal_dist_start":0.31617,"object_z_max":0.1525,"peak_contact_force":0.08514,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10658.0,"raw_peak_contact_force":0.51113,"subtask_id":"lift_object","tcp_end":[0.53148,-0.02026,0.16485],"tcp_start":[0.52194,-0.02029,0.03454],"tcp_to_object_dist_end":0.01795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.61158,0.20462,0.22336],"object_pos_start":[0.54491,-0.02031,0.15295],"object_to_goal_dist_end":0.02813,"object_to_goal_dist_start":0.26226,"object_z_max":0.22322,"peak_contact_force":0.09018,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17081.0,"raw_peak_contact_force":0.11448,"subtask_id":"approach_goal","tcp_end":[0.60108,0.20467,0.24074],"tcp_start":[0.53148,-0.02026,0.16485],"tcp_to_object_dist_end":0.0203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.61557,0.21226,0.21446],"object_pos_start":[0.61158,0.20462,0.22336],"object_to_goal_dist_end":0.01781,"object_to_goal_dist_start":0.02813,"object_z_max":0.22343,"peak_contact_force":0.10761,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":888.0,"raw_peak_contact_force":0.25201,"subtask_id":"place_goal","tcp_end":[0.60315,0.21194,0.2321],"tcp_start":[0.60108,0.20467,0.24074],"tcp_to_object_dist_end":0.02157,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11307,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.03804,"approach_goal.approach_goal_tolerance":0.03605,"approach_object.approach_speed":0.09723,"approach_object.approach_tolerance":0.02046,"descend_to_grasp.descend_speed":0.07457,"descend_to_grasp.grasp_offset_z":1e-05,"descend_to_grasp.grasp_tolerance":0.04681,"descend_to_place.descend_place_speed":0.0106,"descend_to_place.place_tolerance":0.02733,"lift.lift_height":0.14627,"lift.lift_speed":0.09766,"lift.lift_tolerance":0.03441},"optimized_scores":{"best_composite_score":0.25255,"best_fitness_score":0.97255,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.54353,-0.02733,-0.00155],"force_p95":0.4541,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51025,"mean_force":0.14106,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5291,-0.02773,0.0351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":449.0,"contact_point_centroid":[0.62621,0.16503,0.20208],"force_p95":0.16376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.404,"mean_force":0.121,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62087,0.14683,0.20539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3044.0,"contact_point_centroid":[0.53582,-0.0088,0.08244],"force_p95":0.11812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29278,"mean_force":0.08113,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53239,-0.02771,0.07992]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3364.0,"contact_point_centroid":[0.53599,-0.04649,0.08161],"force_p95":0.11376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29027,"mean_force":0.07635,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5324,-0.02771,0.07992]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":513.0,"contact_point_centroid":[0.62626,0.1292,0.20168],"force_p95":0.13915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28887,"mean_force":0.10488,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62096,0.14702,0.20502]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54566,-0.02899,-0.00213],"force_p95":0.16145,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23474,"mean_force":0.13286,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53143,-0.02781,0.03529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4243.0,"contact_point_centroid":[0.58347,0.07478,0.17424],"force_p95":0.13537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18287,"mean_force":0.09339,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57764,0.05621,0.17318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4771.0,"contact_point_centroid":[0.58247,0.03562,0.173],"force_p95":0.11544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17078,"mean_force":0.08688,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57663,0.05402,0.17235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.53156,-0.00856,0.03657],"force_p95":0.08079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15178,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53021,-0.02777,0.03388]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51627,-0.01115,0.23071]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53549,-0.02567,0.10078]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5001.0,"contact_point_centroid":[0.53146,-0.04692,0.03565],"force_p95":0.07335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08286,"mean_force":0.04455,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53022,-0.02777,0.03389]}],"total_contact_groups":12},"final_pose_error":0.01717,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63294,0.15175,0.17409],"final_tcp_position":[0.62327,0.15175,0.19734],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.51025,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":848.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53417,-0.02342,0.15708],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":856.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.5392,-0.028,0.04469],"tcp_start":[0.53417,-0.02342,0.15708],"tcp_to_object_dist_end":0.01978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02791,0.02555],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26024,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15402,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10874.0,"raw_peak_contact_force":0.23474,"subtask_id":"grasp_object","tcp_end":[0.53018,-0.02777,0.03385],"tcp_start":[0.5392,-0.028,0.04469],"tcp_to_object_dist_end":0.01744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":230.0,"n_steps_budget":900.0,"object_pos_end":[0.5593,-0.02768,0.13025],"object_pos_start":[0.54552,-0.02791,0.02555],"object_to_goal_dist_end":0.21139,"object_to_goal_dist_start":0.26024,"object_z_max":0.1298,"peak_contact_force":0.12088,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6478.0,"raw_peak_contact_force":0.51025,"subtask_id":"lift_object","tcp_end":[0.53932,-0.02776,0.14251],"tcp_start":[0.53018,-0.02777,0.03385],"tcp_to_object_dist_end":0.02344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.63083,0.14427,0.18757],"object_pos_start":[0.5593,-0.02768,0.13025],"object_to_goal_dist_end":0.02333,"object_to_goal_dist_start":0.21139,"object_z_max":0.18742,"peak_contact_force":0.16572,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9014.0,"raw_peak_contact_force":0.18287,"subtask_id":"approach_goal","tcp_end":[0.62044,0.14409,0.20963],"tcp_start":[0.53932,-0.02776,0.14251],"tcp_to_object_dist_end":0.02439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":58.0,"n_steps_budget":1000.0,"object_pos_end":[0.63294,0.15175,0.17409],"object_pos_start":[0.63083,0.14427,0.18757],"object_to_goal_dist_end":0.01348,"object_to_goal_dist_start":0.02333,"object_z_max":0.18765,"peak_contact_force":0.16378,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":962.0,"raw_peak_contact_force":0.404,"subtask_id":"place_goal","tcp_end":[0.62327,0.15175,0.19734],"tcp_start":[0.62044,0.14409,0.20963],"tcp_to_object_dist_end":0.02518,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```