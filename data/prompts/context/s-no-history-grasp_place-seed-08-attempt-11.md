## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

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

## Current Skill (Q=0.258) — your mutation base

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

- **Composite score**: 0.258
- **task_score** (E): 1.000
- **fitness_score**: 0.978  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1586 |
| descend_to_grasp | 1.00 | 1.00 | 0.1124 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1125 |
| approach_goal | 1.00 | 1.00 | 0.2394 |
| descend_to_place | 1.00 | 1.00 | 0.0168 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.035)→(0.508, -0.001, 0.026) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.148 | 0.224 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.026)→(0.516, -0.001, 0.138) | (0.522, -0.001, 0.026)→(0.529, -0.001, 0.134) | 0.289→0.236 | 1.00 / 38.000 | 0.080 | 0.600 |
| approach_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.138)→(0.601, 0.196, 0.241) | (0.529, -0.001, 0.134)→(0.614, 0.196, 0.224) | 0.236→0.023 | 1.00 / 23.000 | 25.579 | 0.185 |
| descend_to_place | descend | 1.00 / step_budget | (0.601, 0.196, 0.241)→(0.603, 0.201, 0.225) | (0.614, 0.196, 0.224)→(0.615, 0.201, 0.207) | 0.023→0.010 | 1.00 / 22.000 | 0.142 | 0.223 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.624
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.568
- phase_breakdown.place_goal_score: 0.642
- phase_breakdown.lift_object_score: 0.360
- phase_breakdown.approach_object_score: 0.672
- phase_breakdown.approach_goal_score: 0.671
- phase_breakdown.grasp_object_score: 0.494
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.257
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.323


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00766,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.16333,"approach_goal.approach_goal_tolerance":0.02945,"approach_object.approach_speed":0.10926,"approach_object.approach_tolerance":0.03135,"descend_to_grasp.descend_speed":0.04089,"descend_to_grasp.grasp_offset_z":0.00037,"descend_to_grasp.grasp_tolerance":0.01129,"descend_to_place.descend_place_speed":0.09315,"descend_to_place.place_tolerance":0.01236,"lift.lift_height":0.12305,"lift.lift_speed":0.02194,"lift.lift_tolerance":0.02078},"optimized_scores":{"best_composite_score":0.26004,"best_fitness_score":0.98004,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":116.0,"contact_point_centroid":[0.47965,0.04628,-0.0017],"force_p95":0.44323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51938,"mean_force":0.20954,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46921,0.0466,0.02795]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.0484,-0.00219],"force_p95":0.17565,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26498,"mean_force":0.13701,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47139,0.04683,0.02822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.58025,0.23874,0.25816],"force_p95":0.13347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24913,"mean_force":0.09014,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57498,0.22057,0.25908]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":430.0,"contact_point_centroid":[0.57999,0.20211,0.25756],"force_p95":0.16457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24764,"mean_force":0.11569,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57498,0.22057,0.25907]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7603.0,"contact_point_centroid":[0.47223,0.06565,0.07779],"force_p95":0.07992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24474,"mean_force":0.05259,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47208,0.04644,0.07598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8003.0,"contact_point_centroid":[0.47171,0.0273,0.0769],"force_p95":0.07527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20693,"mean_force":0.04919,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47199,0.04644,0.07526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8450.0,"contact_point_centroid":[0.52188,0.10334,0.18902],"force_p95":0.12464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18285,"mean_force":0.0813,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51843,0.12223,0.1871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10706.0,"contact_point_centroid":[0.52479,0.146,0.19238],"force_p95":0.10496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16711,"mean_force":0.06755,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52137,0.12733,0.19122]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49074,0.02003,0.22559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4992.0,"contact_point_centroid":[0.47009,0.02749,0.03006],"force_p95":0.07198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12689,"mean_force":0.04308,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47027,0.04672,0.02708]},{"body_a":"world","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47865,0.04441,0.09103]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5480.0,"contact_point_centroid":[0.47002,0.0661,0.02944],"force_p95":0.07327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08431,"mean_force":0.04177,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47028,0.04672,0.02709]}],"total_contact_groups":12},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58672,0.22328,0.22912],"final_tcp_position":[0.57617,0.22282,0.25101],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":76.45937,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48206,0.04162,0.14857],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1580.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47815,0.04749,0.03509],"tcp_start":[0.48206,0.04162,0.14857],"tcp_to_object_dist_end":0.01022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04692,0.02536],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2916,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16698,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12272.0,"raw_peak_contact_force":0.26498,"subtask_id":"grasp_object","tcp_end":[0.47024,0.04672,0.02706],"tcp_start":[0.47815,0.04749,0.03509],"tcp_to_object_dist_end":0.01248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.48824,0.04661,0.12543],"object_pos_start":[0.4826,0.04692,0.02536],"object_to_goal_dist_end":0.23026,"object_to_goal_dist_start":0.2916,"object_z_max":0.12516,"peak_contact_force":0.07847,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15722.0,"raw_peak_contact_force":0.51938,"subtask_id":"lift_object","tcp_end":[0.47739,0.04652,0.12925],"tcp_start":[0.47024,0.04672,0.02706],"tcp_to_object_dist_end":0.0115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.58492,0.21901,0.24416],"object_pos_start":[0.48824,0.04661,0.12543],"object_to_goal_dist_end":0.01712,"object_to_goal_dist_start":0.23026,"object_z_max":0.24404,"peak_contact_force":76.45937,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19156.0,"raw_peak_contact_force":0.18285,"subtask_id":"approach_goal","tcp_end":[0.57433,0.21869,0.26511],"tcp_start":[0.47739,0.04652,0.12925],"tcp_to_object_dist_end":0.02348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.58672,0.22328,0.22912],"object_pos_start":[0.58492,0.21901,0.24416],"object_to_goal_dist_end":0.00752,"object_to_goal_dist_start":0.01712,"object_z_max":0.24419,"peak_contact_force":0.16396,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1010.0,"raw_peak_contact_force":0.24913,"subtask_id":"place_goal","tcp_end":[0.57617,0.22282,0.25101],"tcp_start":[0.57433,0.21869,0.26511],"tcp_to_object_dist_end":0.0243,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91667,"average_solve_count":276.0,"average_success_count":276.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.09727,"approach_goal.approach_goal_tolerance":0.02338,"approach_object.approach_speed":0.13967,"approach_object.approach_tolerance":0.02084,"descend_to_grasp.descend_speed":0.02106,"descend_to_grasp.grasp_offset_z":0.0009,"descend_to_grasp.grasp_tolerance":0.03876,"descend_to_place.descend_place_speed":0.07943,"descend_to_place.place_tolerance":0.02282,"lift.lift_height":0.14055,"lift.lift_speed":0.05606,"lift.lift_tolerance":0.03422},"optimized_scores":{"best_composite_score":0.25718,"best_fitness_score":0.97718,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.53453,-0.02031,-0.00139],"force_p95":0.5308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64728,"mean_force":0.15287,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52153,-0.02069,0.02638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8098.0,"contact_point_centroid":[0.5265,-0.00147,0.08901],"force_p95":0.08262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30076,"mean_force":0.05846,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52536,-0.02058,0.08659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8737.0,"contact_point_centroid":[0.52626,-0.03962,0.08622],"force_p95":0.07912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29152,"mean_force":0.05514,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52514,-0.02059,0.08426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11974.0,"contact_point_centroid":[0.56649,0.07247,0.19158],"force_p95":0.09923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25028,"mean_force":0.06898,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56419,0.09143,0.19045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13715.0,"contact_point_centroid":[0.56693,0.11145,0.19153],"force_p95":0.09044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25017,"mean_force":0.06123,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56454,0.09263,0.19092]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":583.0,"contact_point_centroid":[0.60713,0.2356,0.23227],"force_p95":0.17507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.246,"mean_force":0.10594,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60407,0.21762,0.23642]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":454.0,"contact_point_centroid":[0.60792,0.20011,0.23159],"force_p95":0.18315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24404,"mean_force":0.12261,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60416,0.21792,0.23543]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02111,-0.00205],"force_p95":0.13946,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18431,"mean_force":0.12731,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52381,-0.02074,0.02661]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51325,-0.00883,0.22481]},{"body_a":"world","body_b":"grasp_target","contact_count":1596.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5282,-0.01951,0.0906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.52358,-0.00152,0.02792],"force_p95":0.07753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12119,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52257,-0.02072,0.02521]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4918.0,"contact_point_centroid":[0.52354,-0.03981,0.027],"force_p95":0.06948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08819,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52257,-0.02072,0.02521]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61884,0.22094,0.20754],"final_tcp_position":[0.605,0.22072,0.22709],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.64728,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52853,-0.01826,0.14783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1596.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53114,-0.02087,0.03499],"tcp_start":[0.52853,-0.01826,0.14783],"tcp_to_object_dist_end":0.01073,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02061,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31632,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13566,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10810.0,"raw_peak_contact_force":0.18431,"subtask_id":"grasp_object","tcp_end":[0.52254,-0.02071,0.02517],"tcp_start":[0.53114,-0.02087,0.03499],"tcp_to_object_dist_end":0.01436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.54559,-0.02051,0.14232],"object_pos_start":[0.53688,-0.02061,0.02581],"object_to_goal_dist_end":0.26469,"object_to_goal_dist_start":0.31632,"object_z_max":0.14207,"peak_contact_force":0.08239,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16925.0,"raw_peak_contact_force":0.64728,"subtask_id":"lift_object","tcp_end":[0.53165,-0.02054,0.14711],"tcp_start":[0.52254,-0.02071,0.02517],"tcp_to_object_dist_end":0.01475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.61929,0.2155,0.22661],"object_pos_start":[0.54559,-0.02051,0.14232],"object_to_goal_dist_end":0.02448,"object_to_goal_dist_start":0.26469,"object_z_max":0.22657,"peak_contact_force":0.18418,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25689.0,"raw_peak_contact_force":0.25028,"subtask_id":"approach_goal","tcp_end":[0.60375,0.21504,0.2435],"tcp_start":[0.53165,-0.02054,0.14711],"tcp_to_object_dist_end":0.02295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.61884,0.22094,0.20754],"object_pos_start":[0.61929,0.2155,0.22661],"object_to_goal_dist_end":0.01092,"object_to_goal_dist_start":0.02448,"object_z_max":0.22661,"peak_contact_force":0.16378,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1037.0,"raw_peak_contact_force":0.246,"subtask_id":"place_goal","tcp_end":[0.605,0.22072,0.22709],"tcp_start":[0.60375,0.21504,0.2435],"tcp_to_object_dist_end":0.02396,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57368,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.0832,"approach_goal.approach_goal_tolerance":0.0288,"approach_object.approach_speed":0.15412,"approach_object.approach_tolerance":0.02455,"descend_to_grasp.descend_speed":0.07188,"descend_to_grasp.grasp_offset_z":0.00224,"descend_to_grasp.grasp_tolerance":0.03467,"descend_to_place.descend_place_speed":0.02798,"descend_to_place.place_tolerance":0.04906,"lift.lift_height":0.13191,"lift.lift_speed":0.05161,"lift.lift_tolerance":0.0426},"optimized_scores":{"best_composite_score":0.25685,"best_fitness_score":0.97685,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.54153,-0.02807,-0.00143],"force_p95":0.60113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63411,"mean_force":0.19219,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52997,-0.02831,0.02717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7612.0,"contact_point_centroid":[0.53443,-0.00904,0.08427],"force_p95":0.083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29929,"mean_force":0.05871,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53368,-0.02818,0.08166]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8492.0,"contact_point_centroid":[0.53418,-0.04721,0.08184],"force_p95":0.07813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29251,"mean_force":0.05397,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53348,-0.02818,0.07986]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02898,-0.00208],"force_p95":0.14688,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2216,"mean_force":0.12927,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53217,-0.02839,0.02746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":819.0,"contact_point_centroid":[0.62724,0.13714,0.20594],"force_p95":0.09876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17523,"mean_force":0.07408,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62506,0.15602,0.20532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1025.0,"contact_point_centroid":[0.62827,0.17483,0.20604],"force_p95":0.08504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16877,"mean_force":0.06232,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62505,0.15599,0.20543]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51694,-0.01218,0.22428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.53202,-0.00915,0.02873],"force_p95":0.07872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13071,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53092,-0.02835,0.02602]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53635,-0.02684,0.09036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12253.0,"contact_point_centroid":[0.58213,0.04369,0.17512],"force_p95":0.08469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12103,"mean_force":0.05781,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58062,0.0627,0.17342]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12414.0,"contact_point_centroid":[0.58234,0.08223,0.17522],"force_p95":0.08446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10407,"mean_force":0.05687,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58085,0.06325,0.1736]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.53196,-0.04746,0.0278],"force_p95":0.07075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.087,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53093,-0.02835,0.02602]}],"total_contact_groups":12},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63932,0.15864,0.18295],"final_tcp_position":[0.62634,0.15884,0.19605],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.63411,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53612,-0.02518,0.14679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53962,-0.0286,0.03617],"tcp_start":[0.53612,-0.02518,0.14679],"tcp_to_object_dist_end":0.01179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54547,-0.02827,0.02572],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26043,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14151,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10824.0,"raw_peak_contact_force":0.2216,"subtask_id":"grasp_object","tcp_end":[0.53089,-0.02834,0.02598],"tcp_start":[0.53962,-0.0286,0.03617],"tcp_to_object_dist_end":0.01458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.55305,-0.02815,0.13383],"object_pos_start":[0.54547,-0.02827,0.02572],"object_to_goal_dist_end":0.21332,"object_to_goal_dist_start":0.26043,"object_z_max":0.13359,"peak_contact_force":0.08058,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16196.0,"raw_peak_contact_force":0.63411,"subtask_id":"lift_object","tcp_end":[0.54001,-0.02815,0.13841],"tcp_start":[0.53089,-0.02834,0.02598],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.63687,0.15365,0.20076],"object_pos_start":[0.55305,-0.02815,0.13383],"object_to_goal_dist_end":0.02668,"object_to_goal_dist_start":0.21332,"object_z_max":0.20068,"peak_contact_force":0.09405,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24667.0,"raw_peak_contact_force":0.12103,"subtask_id":"approach_goal","tcp_end":[0.62441,0.15343,0.21323],"tcp_start":[0.54001,-0.02815,0.13841],"tcp_to_object_dist_end":0.01763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.63932,0.15864,0.18295],"object_pos_start":[0.63687,0.15365,0.20076],"object_to_goal_dist_end":0.01085,"object_to_goal_dist_start":0.02668,"object_z_max":0.20076,"peak_contact_force":0.09901,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.17523,"subtask_id":"place_goal","tcp_end":[0.62634,0.15884,0.19605],"tcp_start":[0.62441,0.15343,0.21323],"tcp_to_object_dist_end":0.01845,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```