## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5532 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5572 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1876 | 0.38 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1922 | 0.17 | ✅ accepted |

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
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=0.557) — your mutation base

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
  weight: 0.3
- id: reach_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_above
  type: approach
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp_object
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
- id: lift_up
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_above_goal
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_up** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.557
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1575 |
| descend_to_grasp | 1.00 | 1.00 | 0.1138 |
| grasp_object | 1.00 | 1.00 | 0.0130 |
| lift_up | 1.00 | 1.00 | 0.1528 |
| transport_above_goal | 1.00 | 1.00 | 0.2530 |
| descend_to_place | 1.00 | 1.00 | 0.1262 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.148)→(0.510, -0.017, 0.034) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, -0.017, 0.034)→(0.501, -0.017, 0.025) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.667 | 0.136 | 0.164 |
| lift_up | lift | 1.00 / step_budget | (0.501, -0.017, 0.025)→(0.510, -0.017, 0.177) | (0.515, -0.017, 0.026)→(0.525, -0.017, 0.172) | 0.270→0.230 | 1.00 / 35.000 | 11.615 | 0.603 |
| transport_above_goal | approach | 1.00 / step_budget | (0.510, -0.017, 0.177)→(0.610, 0.171, 0.303) | (0.525, -0.017, 0.172)→(0.618, 0.173, 0.293) | 0.230→0.125 | 1.00 / 37.333 | 0.084 | 0.155 |
| descend_to_place | descend | 1.00 / step_budget | (0.610, 0.171, 0.303)→(0.613, 0.179, 0.177) | (0.618, 0.173, 0.293)→(0.619, 0.182, 0.164) | 0.125→0.007 | 1.00 / 35.000 | 0.089 | 0.197 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.724
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.776
- phase_breakdown.approach_object_score: 0.674
- phase_breakdown.reach_goal_score: 0.820
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.556
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.430


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
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42857,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.08122,"descend_to_grasp.descend_speed":0.09094,"descend_to_place.descend_place_speed":0.04534,"lift_up.lift_height":0.13902,"lift_up.lift_speed":0.03867,"transport_above_goal.transport_speed":0.13359},"optimized_scores":{"best_composite_score":0.55627,"best_fitness_score":0.97627,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.53321,-0.02091,-0.00141],"force_p95":0.55998,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60108,"mean_force":0.21668,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52109,-0.02078,0.02462]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8246.0,"contact_point_centroid":[0.52507,-0.04007,0.08591],"force_p95":0.08158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25712,"mean_force":0.05904,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52477,-0.02088,0.08311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9966.0,"contact_point_centroid":[0.52582,-0.00187,0.08427],"force_p95":0.07802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25666,"mean_force":0.05062,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52471,-0.02087,0.08242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.60025,0.23694,0.28645],"force_p95":0.09333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2154,"mean_force":0.06532,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60475,0.21854,0.28323]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6660.0,"contact_point_centroid":[0.6118,0.20139,0.27775],"force_p95":0.07545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17097,"mean_force":0.05301,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60482,0.21891,0.27861]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.0213,-0.00204],"force_p95":0.13619,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15831,"mean_force":0.12605,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52339,-0.02081,0.02521]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51301,-0.00884,0.22494]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17620.0,"contact_point_centroid":[0.57225,0.08352,0.24511],"force_p95":0.08503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13696,"mean_force":0.05827,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56801,0.10209,0.24396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18500.0,"contact_point_centroid":[0.56443,0.11466,0.24077],"force_p95":0.08287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12401,"mean_force":0.05501,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56599,0.09585,0.23873]},{"body_a":"world","body_b":"grasp_target","contact_count":1400.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52825,-0.01961,0.0896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5297.0,"contact_point_centroid":[0.52316,-0.00176,0.02608],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10163,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5221,-0.02079,0.02377]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4169.0,"contact_point_centroid":[0.52312,-0.0401,0.02645],"force_p95":0.07977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09366,"mean_force":0.05202,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5221,-0.02079,0.02377]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61519,0.22937,0.20181],"final_tcp_position":[0.60646,0.22476,0.21606],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.60108,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52844,-0.01835,0.14731],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1400.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53105,-0.02091,0.03394],"tcp_start":[0.52844,-0.01835,0.14731],"tcp_to_object_dist_end":0.00993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.0211,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31668,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.136,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11266.0,"raw_peak_contact_force":0.15831,"tcp_end":[0.52207,-0.02079,0.02373],"tcp_start":[0.53105,-0.02091,0.03394],"tcp_to_object_dist_end":0.01496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.54523,-0.02143,0.14353],"object_pos_start":[0.53688,-0.0211,0.02584],"object_to_goal_dist_end":0.26535,"object_to_goal_dist_start":0.31668,"object_z_max":0.14329,"peak_contact_force":0.07996,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18306.0,"raw_peak_contact_force":0.60108,"tcp_end":[0.53155,-0.02101,0.14584],"tcp_start":[0.52207,-0.02079,0.02373],"tcp_to_object_dist_end":0.01388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61625,0.21864,0.32868],"object_pos_start":[0.54523,-0.02143,0.14353],"object_to_goal_dist_end":0.12176,"object_to_goal_dist_start":0.26535,"object_z_max":0.32849,"peak_contact_force":0.08663,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36120.0,"raw_peak_contact_force":0.13696,"subtask_id":"reach_goal","tcp_end":[0.60462,0.21414,0.33801],"tcp_start":[0.53155,-0.02101,0.14584],"tcp_to_object_dist_end":0.01557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.61519,0.22937,0.20181],"object_pos_start":[0.61625,0.21864,0.32868],"object_to_goal_dist_end":0.0076,"object_to_goal_dist_start":0.12176,"object_z_max":0.32875,"peak_contact_force":0.09328,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11723.0,"raw_peak_contact_force":0.2154,"subtask_id":"reach_goal","tcp_end":[0.60646,0.22476,0.21606],"tcp_start":[0.60462,0.21414,0.33801],"tcp_to_object_dist_end":0.01733,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46457,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.12147,"descend_to_grasp.descend_speed":0.04952,"descend_to_place.descend_place_speed":0.07735,"lift_up.lift_height":0.18066,"lift_up.lift_speed":0.03638,"transport_above_goal.transport_speed":0.15554},"optimized_scores":{"best_composite_score":0.55553,"best_fitness_score":0.97553,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.54161,-0.02805,-0.00147],"force_p95":0.53576,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60241,"mean_force":0.21616,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52931,-0.02839,0.02425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10842.0,"contact_point_centroid":[0.53428,-0.04768,0.10706],"force_p95":0.08399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30103,"mean_force":0.06026,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53353,-0.02849,0.10428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13196.0,"contact_point_centroid":[0.53491,-0.00953,0.10413],"force_p95":0.08128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25625,"mean_force":0.05136,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53339,-0.02848,0.1025]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.0292,-0.00206],"force_p95":0.14417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19032,"mean_force":0.12785,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53169,-0.02845,0.02488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5049.0,"contact_point_centroid":[0.6303,0.13925,0.25105],"force_p95":0.09817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17676,"mean_force":0.06741,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62641,0.15807,0.25155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6809.0,"contact_point_centroid":[0.62277,0.17644,0.25207],"force_p95":0.07439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17612,"mean_force":0.04927,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62645,0.15817,0.25]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11312.0,"contact_point_centroid":[0.58583,0.04491,0.24831],"force_p95":0.09343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15412,"mean_force":0.0653,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.58249,0.06379,0.24717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13492.0,"contact_point_centroid":[0.58259,0.08399,0.24957],"force_p95":0.08471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14303,"mean_force":0.05415,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.58319,0.06524,0.2482]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51685,-0.01219,0.22445]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53613,-0.02687,0.08928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4808.0,"contact_point_centroid":[0.53225,-0.00952,0.02479],"force_p95":0.07329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11157,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53039,-0.02842,0.02339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4247.0,"contact_point_centroid":[0.53132,-0.04766,0.02601],"force_p95":0.09138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09345,"mean_force":0.05349,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53039,-0.02842,0.0234]}],"total_contact_groups":12},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63554,0.16519,0.17084],"final_tcp_position":[0.62841,0.16261,0.1854],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.60241,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53611,-0.0252,0.14695],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1504.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53939,-0.02863,0.03383],"tcp_start":[0.53611,-0.0252,0.14695],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54561,-0.02878,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26073,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14434,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10855.0,"raw_peak_contact_force":0.19032,"tcp_end":[0.53035,-0.02842,0.02336],"tcp_start":[0.53939,-0.02863,0.03383],"tcp_to_object_dist_end":0.01545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.55481,-0.02916,0.18279],"object_pos_start":[0.54561,-0.02878,0.02577],"object_to_goal_dist_end":0.20927,"object_to_goal_dist_start":0.26073,"object_z_max":0.18256,"peak_contact_force":0.08172,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24134.0,"raw_peak_contact_force":0.60241,"tcp_end":[0.54096,-0.02866,0.18718],"tcp_start":[0.53035,-0.02842,0.02336],"tcp_to_object_dist_end":0.01453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.63534,0.15696,0.30073],"object_pos_start":[0.55481,-0.02916,0.18279],"object_to_goal_dist_end":0.12409,"object_to_goal_dist_start":0.20927,"object_z_max":0.3006,"peak_contact_force":0.09405,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24804.0,"raw_peak_contact_force":0.15412,"subtask_id":"reach_goal","tcp_end":[0.62616,0.15454,0.3112],"tcp_start":[0.54096,-0.02866,0.18718],"tcp_to_object_dist_end":0.01414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.63554,0.16519,0.17084],"object_pos_start":[0.63534,0.15696,0.30073],"object_to_goal_dist_end":0.00666,"object_to_goal_dist_start":0.12409,"object_z_max":0.30075,"peak_contact_force":0.10222,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11858.0,"raw_peak_contact_force":0.17676,"subtask_id":"reach_goal","tcp_end":[0.62841,0.16261,0.1854],"tcp_start":[0.62616,0.15454,0.3112],"tcp_to_object_dist_end":0.01641,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94152,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.19964,"descend_to_grasp.descend_speed":0.09338,"descend_to_place.descend_place_speed":0.09821,"lift_up.lift_height":0.19204,"lift_up.lift_speed":0.06591,"transport_above_goal.transport_speed":0.14447},"optimized_scores":{"best_composite_score":0.5599,"best_fitness_score":0.9799,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.45986,-0.00028,-0.00133],"force_p95":0.54391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60443,"mean_force":0.17378,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44924,-0.00031,0.02815]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11025.0,"contact_point_centroid":[0.45369,-0.01948,0.11099],"force_p95":0.08036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2665,"mean_force":0.05371,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.45216,-0.00035,0.10889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11290.0,"contact_point_centroid":[0.45331,0.01877,0.1094],"force_p95":0.08227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2662,"mean_force":0.05274,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.45205,-0.00035,0.10745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7160.0,"contact_point_centroid":[0.5967,0.16507,0.19831],"force_p95":0.0715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20008,"mean_force":0.04906,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60034,0.14648,0.19508]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12015.0,"contact_point_centroid":[0.53373,0.05601,0.22984],"force_p95":0.08457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17338,"mean_force":0.05232,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.53078,0.07482,0.22869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7160.0,"contact_point_centroid":[0.6043,0.12765,0.19564],"force_p95":0.07278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16651,"mean_force":0.05029,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60034,0.14648,0.19508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11308.0,"contact_point_centroid":[0.53026,0.09448,0.23182],"force_p95":0.09901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14512,"mean_force":0.05733,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.53155,0.07557,0.22907]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00015,-0.00202],"force_p95":0.12961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14453,"mean_force":0.12464,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4514,-0.00027,0.0281]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48252,-5e-05,0.22616]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46038,-0.00015,0.09151]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.45117,-0.0195,0.02903],"force_p95":0.0667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08758,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45021,-0.00029,0.02698]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.45087,0.01892,0.0287],"force_p95":0.06492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08389,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45021,-0.00029,0.02698]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60595,0.15174,0.11877],"final_tcp_position":[0.60455,0.15067,0.13008],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":34.68372,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46496,-0.00011,0.14961],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45849,-0.00015,0.0349],"tcp_start":[0.46496,-0.00011,0.14961],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-0.0003,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12898,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.14453,"tcp_end":[0.45018,-0.00029,0.02695],"tcp_start":[0.45849,-0.00015,0.0349],"tcp_to_object_dist_end":0.01258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.47417,-0.00014,0.19047],"object_pos_start":[0.46271,-0.0003,0.02591],"object_to_goal_dist_end":0.21579,"object_to_goal_dist_start":0.23338,"object_z_max":0.19021,"peak_contact_force":34.68372,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22391.0,"raw_peak_contact_force":0.60443,"tcp_end":[0.4585,-0.00036,0.19844],"tcp_start":[0.45018,-0.00029,0.02695],"tcp_to_object_dist_end":0.01758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.60135,0.144,0.25045],"object_pos_start":[0.47417,-0.00014,0.19047],"object_to_goal_dist_end":0.12887,"object_to_goal_dist_start":0.21579,"object_z_max":0.25037,"peak_contact_force":0.07265,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23323.0,"raw_peak_contact_force":0.17338,"subtask_id":"reach_goal","tcp_end":[0.59837,0.14298,0.25972],"tcp_start":[0.4585,-0.00036,0.19844],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.60595,0.15174,0.11877],"object_pos_start":[0.60135,0.144,0.25045],"object_to_goal_dist_end":0.00553,"object_to_goal_dist_start":0.12887,"object_z_max":0.25045,"peak_contact_force":0.07294,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14320.0,"raw_peak_contact_force":0.20008,"subtask_id":"reach_goal","tcp_end":[0.60455,0.15067,0.13008],"tcp_start":[0.59837,0.14298,0.25972],"tcp_to_object_dist_end":0.01145,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```