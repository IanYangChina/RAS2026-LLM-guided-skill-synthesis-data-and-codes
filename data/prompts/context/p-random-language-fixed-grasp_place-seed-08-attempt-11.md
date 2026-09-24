## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4536 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4538 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3538 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4537 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4538 | 1.00 | ❌ rejected |

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

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.454) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
- id: transport_arc
- id: release_1
phases:
- id: approach_1
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
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
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
    - 0.02
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
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
  parameters:
    grasp_retry_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    grasp_retry_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.8
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_1
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
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.06
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_retry_x: status=consumed; consumers=retry.offset.x (replace)
    - grasp_retry_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.8
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.454
- **task_score** (E): 1.000
- **fitness_score**: 0.974  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1261 |
| descend_1 | 1.00 | 1.00 | 0.1379 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 1.00 | 1.00 | 0.1517 |
| transport_1 | 0.33 | 1.00 | 0.1971 |
| descend_2 | 1.00 | 1.00 | 0.1367 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.182) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.182)→(0.516, -0.001, 0.044) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.044)→(0.508, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 42.667 | 0.144 | 0.180 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.035)→(0.517, -0.001, 0.186) | (0.522, -0.001, 0.026)→(0.526, -0.001, 0.170) | 0.290→0.230 | 1.00 / 37.333 | 0.083 | 0.586 |
| transport_1 | approach | 0.33 / step_budget | (0.517, -0.001, 0.186)→(0.570, 0.122, 0.324) | (0.526, -0.001, 0.170)→(0.576, 0.124, 0.299) | 0.230→0.135 | 1.00 / 33.000 | 0.109 | 0.380 |
| descend_2 | descend | 1.00 / step_budget | (0.570, 0.122, 0.324)→(0.603, 0.201, 0.226) | (0.576, 0.124, 0.299)→(0.599, 0.201, 0.195) | 0.135→0.016 | 1.00 / 29.667 | 0.099 | 0.321 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.362
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.329
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.023
- phase_breakdown.approach_1_score: 0.032
- phase_breakdown.descend_1_score: 0.850
- phase_breakdown.release_1_score: 0.533
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.454
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.385


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02174,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13127,"descend_1.grasp_z_offset":0.01079,"descend_2.descend_z_offset":0.02493,"grasp_1.grasp_retry_x":-0.00497,"grasp_1.grasp_retry_y":-0.00351,"lift_1.lift_height":0.15614,"transport_1.arc_height":0.09375,"transport_1.transport_speed":0.22172},"optimized_scores":{"best_composite_score":0.45269,"best_fitness_score":0.97269,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.4802,0.04617,-0.00122],"force_p95":0.3243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53837,"mean_force":0.0734,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46834,0.04681,0.03872]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7263.0,"contact_point_centroid":[0.54657,0.19739,0.29761],"force_p95":0.11733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46796,"mean_force":0.07341,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55096,0.17905,0.29807]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8360.0,"contact_point_centroid":[0.55751,0.16294,0.29398],"force_p95":0.10358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44755,"mean_force":0.06612,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55193,0.18075,0.29624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15209.0,"contact_point_centroid":[0.49554,0.05258,0.26875],"force_p95":0.0973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40364,"mean_force":0.06609,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48939,0.07057,0.26763]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14331.0,"contact_point_centroid":[0.47174,0.06616,0.10507],"force_p95":0.08499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32017,"mean_force":0.0588,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47193,0.04696,0.10237]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17765.0,"contact_point_centroid":[0.47384,0.02804,0.10334],"force_p95":0.07875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29144,"mean_force":0.04883,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47188,0.04695,0.10178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13062.0,"contact_point_centroid":[0.49211,0.09158,0.27147],"force_p95":0.11087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28003,"mean_force":0.07496,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49044,0.07238,0.26947]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04869,-0.00215],"force_p95":0.16359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2202,"mean_force":0.13356,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47077,0.04707,0.03799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5205.0,"contact_point_centroid":[0.47119,0.02794,0.03805],"force_p95":0.07141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19745,"mean_force":0.04168,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46958,0.04695,0.03677]},{"body_a":"world","body_b":"grasp_target","contact_count":1684.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48964,0.02114,0.23499]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47802,0.04557,0.10688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4225.0,"contact_point_centroid":[0.46941,0.06628,0.03921],"force_p95":0.08748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09299,"mean_force":0.05202,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46958,0.04695,0.03678]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5692,0.22148,0.22021],"final_tcp_position":[0.57538,0.22148,0.25393],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.53837,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1684.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48075,0.04364,0.16958],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47786,0.04775,0.04533],"tcp_start":[0.48075,0.04364,0.16958],"tcp_to_object_dist_end":0.01993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.04777,0.02549],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29094,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16062,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11230.0,"raw_peak_contact_force":0.2202,"subtask_id":"grasp_1","tcp_end":[0.46955,0.04695,0.03674],"tcp_start":[0.47786,0.04775,0.04533],"tcp_to_object_dist_end":0.01735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.48787,0.04831,0.15256],"object_pos_start":[0.48273,0.04777,0.02549],"object_to_goal_dist_end":0.21796,"object_to_goal_dist_start":0.29094,"object_z_max":0.15244,"peak_contact_force":0.0809,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32239.0,"raw_peak_contact_force":0.53837,"tcp_end":[0.47846,0.04738,0.16987],"tcp_start":[0.46955,0.04695,0.03674],"tcp_to_object_dist_end":0.01972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53774,0.14196,0.31735],"object_pos_start":[0.48787,0.04831,0.15256],"object_to_goal_dist_end":0.13055,"object_to_goal_dist_start":0.21796,"object_z_max":0.3173,"peak_contact_force":0.15804,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28271.0,"raw_peak_contact_force":0.40364,"subtask_id":"transport_arc","tcp_end":[0.52956,0.13974,0.34419],"tcp_start":[0.47846,0.04738,0.16987],"tcp_to_object_dist_end":0.02815,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.5692,0.22148,0.22021],"object_pos_start":[0.53774,0.14196,0.31735],"object_to_goal_dist_end":0.0179,"object_to_goal_dist_start":0.13055,"object_z_max":0.31735,"peak_contact_force":0.13998,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15623.0,"raw_peak_contact_force":0.46796,"subtask_id":"release_1","tcp_end":[0.57538,0.22148,0.25393],"tcp_start":[0.52956,0.13974,0.34419],"tcp_to_object_dist_end":0.03428,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16646,"descend_1.grasp_z_offset":0.01,"descend_2.descend_z_offset":0.03467,"grasp_1.grasp_retry_x":0.004,"grasp_1.grasp_retry_y":0.00536,"lift_1.lift_height":0.20966,"transport_1.arc_height":0.08523,"transport_1.transport_speed":0.19126},"optimized_scores":{"best_composite_score":0.45416,"best_fitness_score":0.97416,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.53418,-0.02078,-0.00111],"force_p95":0.42411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60609,"mean_force":0.08237,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52124,-0.0209,0.0356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.52525,-0.04017,0.11545],"force_p95":0.08109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33616,"mean_force":0.05879,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52445,-0.02099,0.11272]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20292.0,"contact_point_centroid":[0.52604,-0.00203,0.11336],"force_p95":0.07657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32837,"mean_force":0.05081,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52439,-0.02099,0.11173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15461.0,"contact_point_centroid":[0.54525,0.003,0.27392],"force_p95":0.0867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24514,"mean_force":0.06255,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54193,0.02177,0.27238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12925.0,"contact_point_centroid":[0.58185,0.17687,0.28045],"force_p95":0.08954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23286,"mean_force":0.0595,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58486,0.15811,0.27899]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14362.0,"contact_point_centroid":[0.5902,0.13963,0.2786],"force_p95":0.0823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22182,"mean_force":0.05472,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58474,0.15784,0.27909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15708.0,"contact_point_centroid":[0.54344,0.03941,0.2714],"force_p95":0.08868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16878,"mean_force":0.06184,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54151,0.02046,0.27029]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02136,-0.00203],"force_p95":0.13427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15528,"mean_force":0.1256,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52392,-0.02094,0.03533]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51345,-0.00921,0.25056]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52907,-0.01991,0.12241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5316.0,"contact_point_centroid":[0.52356,-0.00187,0.03606],"force_p95":0.06886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10157,"mean_force":0.04097,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52266,-0.02092,0.03388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.52348,-0.04021,0.03662],"force_p95":0.08044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09489,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52266,-0.02092,0.03388]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59981,0.2205,0.20738],"final_tcp_position":[0.60522,0.22046,0.23762],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.60609,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1404.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52935,-0.01885,0.20211],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1912.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53146,-0.02104,0.04409],"tcp_start":[0.52935,-0.01885,0.20211],"tcp_to_object_dist_end":0.01891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02127,0.02585],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3168,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13426,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.15528,"subtask_id":"grasp_1","tcp_end":[0.52263,-0.02092,0.03385],"tcp_start":[0.53146,-0.02104,0.04409],"tcp_to_object_dist_end":0.01637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54022,-0.0217,0.17825],"object_pos_start":[0.53691,-0.02127,0.02585],"object_to_goal_dist_end":0.26075,"object_to_goal_dist_start":0.3168,"object_z_max":0.17806,"peak_contact_force":0.08246,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37437.0,"raw_peak_contact_force":0.60609,"tcp_end":[0.53077,-0.02114,0.1944],"tcp_start":[0.52263,-0.02092,0.03385],"tcp_to_object_dist_end":0.01872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57126,0.09236,0.3063],"object_pos_start":[0.54022,-0.0217,0.17825],"object_to_goal_dist_end":0.17215,"object_to_goal_dist_start":0.26075,"object_z_max":0.30625,"peak_contact_force":0.08301,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31169.0,"raw_peak_contact_force":0.24514,"subtask_id":"transport_arc","tcp_end":[0.56476,0.09128,0.32929],"tcp_start":[0.53077,-0.02114,0.1944],"tcp_to_object_dist_end":0.02392,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":754.0,"n_steps_budget":1000.0,"object_pos_end":[0.59981,0.2205,0.20738],"object_pos_start":[0.57126,0.09236,0.3063],"object_to_goal_dist_end":0.01276,"object_to_goal_dist_start":0.17215,"object_z_max":0.3063,"peak_contact_force":0.07747,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":27287.0,"raw_peak_contact_force":0.23286,"subtask_id":"release_1","tcp_end":[0.60522,0.22046,0.23762],"tcp_start":[0.56476,0.09128,0.32929],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13669,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13986,"descend_1.grasp_z_offset":0.01008,"descend_2.descend_z_offset":0.00142,"grasp_1.grasp_retry_x":-0.01042,"grasp_1.grasp_retry_y":0.01938,"lift_1.lift_height":0.18146,"transport_1.arc_height":0.147,"transport_1.transport_speed":0.28972},"optimized_scores":{"best_composite_score":0.45399,"best_fitness_score":0.97399,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.54222,-0.02837,-0.00115],"force_p95":0.43112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61319,"mean_force":0.08987,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5296,-0.02857,0.03523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13549.0,"contact_point_centroid":[0.57196,0.01446,0.27962],"force_p95":0.11295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49251,"mean_force":0.0761,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56833,0.03324,0.27832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16918.0,"contact_point_centroid":[0.53446,-0.04787,0.11509],"force_p95":0.08188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33914,"mean_force":0.05878,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53384,-0.02869,0.11229]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20205.0,"contact_point_centroid":[0.53554,-0.00974,0.11284],"force_p95":0.07807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33079,"mean_force":0.05082,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53376,-0.02869,0.11123]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6358.0,"contact_point_centroid":[0.61799,0.16553,0.24427],"force_p95":0.08179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26221,"mean_force":0.05241,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62082,0.14685,0.2429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4992.0,"contact_point_centroid":[0.62618,0.12879,0.24055],"force_p95":0.08822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26005,"mean_force":0.06567,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62099,0.14726,0.241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16458.0,"contact_point_centroid":[0.57152,0.05459,0.28189],"force_p95":0.08969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25975,"mean_force":0.06053,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56963,0.03595,0.28039]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02925,-0.00205],"force_p95":0.13876,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16466,"mean_force":0.12671,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53225,-0.02864,0.03506]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5456,-0.02923,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51756,-0.01303,0.23697]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53743,-0.02762,0.10917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5300.0,"contact_point_centroid":[0.53208,-0.00957,0.03575],"force_p95":0.07058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11763,"mean_force":0.04105,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53098,-0.0286,0.03357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4170.0,"contact_point_centroid":[0.53172,-0.0479,0.03637],"force_p95":0.08162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09328,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53098,-0.0286,0.03357]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62836,0.16228,0.15883],"final_tcp_position":[0.62721,0.16024,0.18512],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.61319,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1804.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53774,-0.02651,0.1753],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53984,-0.02883,0.04406],"tcp_start":[0.53774,-0.02651,0.1753],"tcp_to_object_dist_end":0.01894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02903,0.0258],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26093,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13853,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11270.0,"raw_peak_contact_force":0.16466,"subtask_id":"grasp_1","tcp_end":[0.53095,-0.0286,0.03353],"tcp_start":[0.53984,-0.02883,0.04406],"tcp_to_object_dist_end":0.01648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.55109,-0.02958,0.17833],"object_pos_start":[0.54549,-0.02903,0.0258],"object_to_goal_dist_end":0.21099,"object_to_goal_dist_start":0.26093,"object_z_max":0.17822,"peak_contact_force":0.08598,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37272.0,"raw_peak_contact_force":0.61319,"tcp_end":[0.54133,-0.02889,0.19417],"tcp_start":[0.53095,-0.0286,0.03353],"tcp_to_object_dist_end":0.01861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61992,0.13702,0.27396],"object_pos_start":[0.55109,-0.02958,0.17833],"object_to_goal_dist_end":0.1018,"object_to_goal_dist_start":0.21099,"object_z_max":0.29687,"peak_contact_force":0.08468,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30007.0,"raw_peak_contact_force":0.49251,"subtask_id":"transport_arc","tcp_end":[0.61677,0.13543,0.29853],"tcp_start":[0.54133,-0.02889,0.19417],"tcp_to_object_dist_end":0.02483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.62836,0.16228,0.15883],"object_pos_start":[0.61992,0.13702,0.27396],"object_to_goal_dist_end":0.01883,"object_to_goal_dist_start":0.1018,"object_z_max":0.27396,"peak_contact_force":0.07918,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11350.0,"raw_peak_contact_force":0.26221,"subtask_id":"release_1","tcp_end":[0.62721,0.16024,0.18512],"tcp_start":[0.61677,0.13543,0.29853],"tcp_to_object_dist_end":0.0264,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```