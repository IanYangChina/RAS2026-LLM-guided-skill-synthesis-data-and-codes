## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0222 | 0.51 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1191 | 0.41 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0018 | 0.22 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0976 | 0.24 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0911 | 0.38 | ❌ rejected |

**Proposal policy**: task_score is 0.51 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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

## Current Skill (Q=-0.022) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
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
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.01
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
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
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
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: scale
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.001
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_retained
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: abort
  subtask_id: transport_arc
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.001
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    release_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (scale)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.05]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.001
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_retained, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.001
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (add)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.022
- **task_score** (E): 0.515
- **fitness_score**: 0.478  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0796 |
| descend_1 | 1.00 | 1.00 | 0.1845 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.0186 |
| transport_arc | 0.00 | 1.00 | 0.0901 |
| place_descend | 0.00 | 1.00 | 0.2210 |
| release_1 | 1.00 | 1.00 | 0.0254 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.229) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.016, 0.229)→(0.511, 0.018, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.045)→(0.502, 0.018, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 | 1.00 / 36.333 | 0.144 | 0.214 |
| lift_1 | lift | 1.00 / step_budget | (0.508, 0.017, 0.047)→(0.514, 0.017, 0.064) | (0.516, 0.017, 0.026)→(0.520, 0.017, 0.034) | 0.237→0.231 | 1.00 / 37.667 | 0.124 | 0.448 |
| transport_arc | approach | 0.00 / step_budget | (0.514, 0.017, 0.064)→(0.568, 0.047, 0.129) | (0.524, 0.017, 0.049)→(0.573, 0.049, 0.119) | 0.224→0.163 | 1.00 / 42.667 | 170.654 | 336.166 |
| place_descend | descend | 0.00 / step_budget | (0.568, 0.047, 0.129)→(0.663, 0.124, 0.288) | (0.573, 0.049, 0.119)→(0.596, 0.182, 0.101) | 0.163→0.099 | 1.00 / 19.000 | 284.412 | 1278.977 |
| release_1 | release | 1.00 / step_budget | (0.663, 0.124, 0.288)→(0.662, 0.125, 0.314) | (0.596, 0.182, 0.101)→(0.596, 0.182, 0.108) | 0.099→0.102 | 1.00 / 3.000 | 0.254 | 135.333 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 1.000
- terminal_score: 0.626
- phase_score: 0.292
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.183
- phase_breakdown.transport_arc_score: 0.068
- phase_breakdown.approach_1_score: 0.013
- phase_breakdown.descend_1_score: 0.770
- grasp_place_fitness: 0.517

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.517
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.626
- **Median Q (composite search score)**: -0.007
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.267


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":49.0,"average_failure_rate":0.29518,"average_mean_iterations":61.62048,"average_solve_count":166.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24979,"descend_1.grasp_z_offset":0.00398,"lift_1.lift_distance":0.23571,"place_descend.place_z_offset":-0.01582,"release_1.release_time":1.37678,"transport_arc.arc_height":0.44339,"transport_arc.transport_speed":0.39933},"optimized_scores":{"best_composite_score":-0.00694,"best_fitness_score":0.49306,"best_task_score":0.53027},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":238.0,"contact_point_centroid":[0.72151,0.03675,-0.0006],"force_p95":624.91496,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1408.965,"mean_force":345.33081,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.65855,0.11261,0.25735]},{"body_a":"world","body_b":"hand","contact_count":33.0,"contact_point_centroid":[0.6406,0.22257,-0.00352],"force_p95":1081.85126,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1336.74079,"mean_force":391.85554,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58701,0.24542,0.00193]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.72346,0.03476,-9e-05],"force_p95":73.36355,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.65701,"mean_force":52.80945,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.66595,0.06371,0.28616]},{"body_a":"world","body_b":"left_finger","contact_count":286.0,"contact_point_centroid":[0.57108,0.22506,-0.00597],"force_p95":37.67644,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.90739,"mean_force":10.72814,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58663,0.24023,-0.00659]},{"body_a":"world","body_b":"right_finger","contact_count":314.0,"contact_point_centroid":[0.6045,0.2545,-0.00565],"force_p95":18.02921,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.5609,"mean_force":6.30957,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58663,0.24286,-0.00575]},{"body_a":"world","body_b":"grasp_target","contact_count":1185.0,"contact_point_centroid":[0.58492,0.18215,-0.0039],"force_p95":0.81415,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.57802,"mean_force":0.26142,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.64769,0.13042,0.21775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":181.0,"contact_point_centroid":[0.53963,0.06086,0.08178],"force_p95":0.86486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.13515,"mean_force":0.13318,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53756,0.04213,0.07857]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":719.0,"contact_point_centroid":[0.55384,0.05474,0.06838],"force_p95":0.78869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.83177,"mean_force":0.26737,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.55442,0.07582,0.0695]},{"body_a":"grasp_target","body_b":"hand","contact_count":46.0,"contact_point_centroid":[0.61942,0.18583,0.01892],"force_p95":1.1904,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.30759,"mean_force":0.69488,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58851,0.24868,0.01805]},{"body_a":"world","body_b":"grasp_target","contact_count":340.0,"contact_point_centroid":[0.53025,0.02835,-0.00112],"force_p95":0.32355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49738,"mean_force":0.06938,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51634,0.02944,0.03077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16941.0,"contact_point_centroid":[0.52345,0.04827,0.05588],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25697,"mean_force":0.05234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52299,0.02918,0.05402]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16482.0,"contact_point_centroid":[0.52383,0.01006,0.05732],"force_p95":0.07892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24451,"mean_force":0.05284,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52332,0.02917,0.05516]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03051,-0.0021],"force_p95":0.15391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22715,"mean_force":0.13105,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51811,0.02969,0.0301]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4070.0,"contact_point_centroid":[0.51762,0.01041,0.03151],"force_p95":0.0798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13892,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51689,0.02961,0.02873]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.5305,0.03079,-0.00185],"force_p95":0.13717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51075,0.01288,0.28739]},{"body_a":"world","body_b":"grasp_target","contact_count":2876.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52289,0.02773,0.15647]}],"total_contact_groups":20},"final_pose_error":0.23416,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57962,0.18845,0.01602],"final_tcp_position":[0.66612,0.06391,0.28594],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1408.965,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":872.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52256,0.02541,0.2773],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2876.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52537,0.03017,0.03836],"tcp_start":[0.52256,0.02541,0.2773],"tcp_to_object_dist_end":0.01338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.0296,0.02564],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18454,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14711,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10846.0,"raw_peak_contact_force":0.22715,"subtask_id":"grasp_1","tcp_end":[0.51687,0.02961,0.0287],"tcp_start":[0.52537,0.03017,0.03836],"tcp_to_object_dist_end":0.01386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":869.0,"n_steps_budget":600.0,"object_pos_end":[0.53635,0.02939,0.04543],"object_pos_start":[0.53039,0.0296,0.02564],"object_to_goal_dist_end":0.17445,"object_to_goal_dist_start":0.18454,"object_z_max":0.07058,"peak_contact_force":0.06915,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33763.0,"raw_peak_contact_force":0.49738,"tcp_end":[0.5307,0.02907,0.08164],"tcp_start":[0.52441,0.02928,0.05253],"tcp_to_object_dist_end":0.03665,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.54032,0.0291,0.07062],"object_pos_start":[0.54032,0.0291,0.07062],"object_to_goal_dist_end":0.16582,"object_to_goal_dist_start":0.16582,"peak_contact_force":0.06915,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"transport_arc","tcp_end":[0.5307,0.02907,0.08164],"tcp_start":[0.5307,0.02907,0.08164],"tcp_to_object_dist_end":0.01463,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.57962,0.18846,0.01602],"object_pos_start":[0.54032,0.0291,0.07062],"object_to_goal_dist_end":0.09516,"object_to_goal_dist_start":0.16582,"object_z_max":0.07062,"peak_contact_force":246.01161,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3561.0,"raw_peak_contact_force":1408.965,"tcp_end":[0.66612,0.06391,0.28594],"tcp_start":[0.5307,0.02907,0.08164],"tcp_to_object_dist_end":0.3096,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57962,0.18845,0.01602],"object_pos_start":[0.57962,0.18846,0.01602],"object_to_goal_dist_end":0.09516,"object_to_goal_dist_start":0.09516,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1109.0,"raw_peak_contact_force":135.65701,"subtask_id":"release_1","tcp_end":[0.66623,0.06444,0.31101],"tcp_start":[0.66612,0.06391,0.28594],"tcp_to_object_dist_end":0.33152,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.03521,"average_mean_iterations":10.8169,"average_solve_count":142.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20988,"descend_1.grasp_z_offset":0.02753,"lift_1.lift_distance":0.17963,"place_descend.place_z_offset":-0.00552,"release_1.release_time":1.21622,"transport_arc.arc_height":0.35398,"transport_arc.transport_speed":0.26005},"optimized_scores":{"best_composite_score":0.01728,"best_fitness_score":0.51728,"best_task_score":0.62592},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":988.0,"contact_point_centroid":[0.61215,0.15645,-0.00029],"force_p95":499.10568,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1119.23251,"mean_force":422.57057,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.76998,0.08467,0.20839]},{"body_a":"world","body_b":"hand","contact_count":159.0,"contact_point_centroid":[0.66911,0.03906,-0.00085],"force_p95":592.45646,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1008.49884,"mean_force":220.96331,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59295,0.03367,-0.00188]},{"body_a":"world","body_b":"link6","contact_count":724.0,"contact_point_centroid":[0.53451,0.15089,-0.00032],"force_p95":512.25066,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":585.42464,"mean_force":314.53335,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.6778,0.00978,0.1839]},{"body_a":"world","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.65656,0.07782,-0.00046],"force_p95":346.13001,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":388.93953,"mean_force":216.82532,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.66051,-0.03127,0.10205]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.60957,0.18192,-0.00015],"force_p95":85.63694,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.26306,"mean_force":60.96,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62508,0.16006,0.29298]},{"body_a":"world","body_b":"left_finger","contact_count":1699.0,"contact_point_centroid":[0.60902,0.04099,-0.01176],"force_p95":15.07477,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.23623,"mean_force":9.51019,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59345,0.05848,-0.0115]},{"body_a":"world","body_b":"right_finger","contact_count":1537.0,"contact_point_centroid":[0.57953,0.08134,-0.01023],"force_p95":16.94146,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.50125,"mean_force":11.33001,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5943,0.06189,-0.01309]},{"body_a":"world","body_b":"grasp_target","contact_count":362.0,"contact_point_centroid":[0.54495,0.01878,-0.00753],"force_p95":2.30701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.06545,"mean_force":0.85453,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57223,0.04907,0.00267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16300.0,"contact_point_centroid":[0.67078,-0.00438,0.15814],"force_p95":0.1507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.78739,"mean_force":0.07843,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.67023,0.00642,0.17123]},{"body_a":"grasp_target","body_b":"hand","contact_count":872.0,"contact_point_centroid":[0.65412,0.0339,0.13439],"force_p95":0.60555,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.27007,"mean_force":0.25332,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.66666,0.00744,0.15943]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16486.0,"contact_point_centroid":[0.66748,0.01973,0.17954],"force_p95":0.15236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.87242,"mean_force":0.05564,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.67046,0.00711,0.16824]},{"body_a":"grasp_target","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.63646,0.1644,0.25216],"force_p95":0.6348,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.65005,"mean_force":0.50265,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62511,0.16012,0.29914]},{"body_a":"grasp_target","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.73408,0.10489,0.19147],"force_p95":0.38535,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.416,"mean_force":0.35625,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.76903,0.08457,0.20882]},{"body_a":"world","body_b":"grasp_target","contact_count":652.0,"contact_point_centroid":[0.50452,-0.01545,-0.0035],"force_p95":0.29918,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37311,"mean_force":0.22747,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49484,-0.01524,0.05073]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1793.0,"contact_point_centroid":[0.49504,0.00341,0.04811],"force_p95":0.11209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31598,"mean_force":0.0869,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49484,-0.01524,0.05073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.49487,-0.03381,0.04807],"force_p95":0.10585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31273,"mean_force":0.07809,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49486,-0.01524,0.05069]}],"total_contact_groups":25},"final_pose_error":0.06899,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.6355,0.16218,0.29215],"final_tcp_position":[0.62546,0.15989,0.29275],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1119.23251,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50008,-0.01204,0.24827],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2280.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4992,-0.01535,0.06222],"tcp_start":[0.50008,-0.01204,0.24827],"tcp_to_object_dist_end":0.0365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01533,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31214,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13342,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7415.0,"raw_peak_contact_force":0.16619,"subtask_id":"grasp_1","tcp_end":[0.49127,-0.01525,0.05344],"tcp_start":[0.4992,-0.01535,0.06222],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":163.0,"n_steps_budget":600.0,"object_pos_end":[0.50561,-0.01532,0.02191],"object_pos_start":[0.50374,-0.01533,0.02586],"object_to_goal_dist_end":0.31447,"object_to_goal_dist_start":0.31214,"object_z_max":0.02586,"peak_contact_force":0.23207,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4497.0,"raw_peak_contact_force":0.37311,"tcp_end":[0.49849,-0.01525,0.05186],"tcp_start":[0.49415,-0.01525,0.05001],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.65468,0.07915,0.23537],"object_pos_start":[0.50788,-0.01527,0.02404],"object_to_goal_dist_end":0.12839,"object_to_goal_dist_start":0.31233,"object_z_max":0.2352,"peak_contact_force":511.82132,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38177.0,"raw_peak_contact_force":1008.49884,"subtask_id":"transport_arc","tcp_end":[0.66066,0.07493,0.24837],"tcp_start":[0.49849,-0.01525,0.05186],"tcp_to_object_dist_end":0.01491,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63573,0.16222,0.27146],"object_pos_start":[0.65468,0.07915,0.23537],"object_to_goal_dist_end":0.05971,"object_to_goal_dist_start":0.12839,"object_z_max":0.27145,"peak_contact_force":272.04974,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":41882.0,"raw_peak_contact_force":1119.23251,"tcp_end":[0.62546,0.15989,0.29275],"tcp_start":[0.66066,0.07493,0.24837],"tcp_to_object_dist_end":0.02375,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6355,0.16218,0.29215],"object_pos_start":[0.63573,0.16222,0.27146],"object_to_goal_dist_end":0.07028,"object_to_goal_dist_start":0.05971,"object_z_max":0.2918,"peak_contact_force":0.51688,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2738.0,"raw_peak_contact_force":86.26306,"subtask_id":"release_1","tcp_end":[0.62525,0.16023,0.31898],"tcp_start":[0.62546,0.15989,0.29275],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":56.0,"average_failure_rate":0.34783,"average_mean_iterations":72.6646,"average_solve_count":161.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12455,"descend_1.grasp_z_offset":-0.00063,"lift_1.lift_distance":0.13592,"place_descend.place_z_offset":-0.01418,"release_1.release_time":0.87472,"transport_arc.arc_height":0.27526,"transport_arc.transport_speed":0.33416},"optimized_scores":{"best_composite_score":-0.0769,"best_fitness_score":0.4231,"best_task_score":0.38854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":111.0,"contact_point_centroid":[0.7197,0.07433,-0.00086],"force_p95":1044.62049,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1308.73387,"mean_force":430.96247,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.69323,0.2277,0.21723]},{"body_a":"world","body_b":"hand","contact_count":32.0,"contact_point_centroid":[0.63633,0.24799,-0.00163],"force_p95":1004.04475,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1110.38449,"mean_force":388.90651,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5855,0.28237,0.01557]},{"body_a":"world","body_b":"link6","contact_count":80.0,"contact_point_centroid":[0.72031,0.09449,-0.00016],"force_p95":75.65136,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.07762,"mean_force":55.36152,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.69453,0.14786,0.28631]},{"body_a":"world","body_b":"left_finger","contact_count":243.0,"contact_point_centroid":[0.5524,0.24419,-0.00362],"force_p95":47.39002,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.33661,"mean_force":13.79547,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58034,0.27131,0.00505]},{"body_a":"world","body_b":"right_finger","contact_count":171.0,"contact_point_centroid":[0.62422,0.3046,-0.00226],"force_p95":7.11648,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10.86196,"mean_force":3.2536,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58571,0.28263,0.00622]},{"body_a":"world","body_b":"grasp_target","contact_count":538.0,"contact_point_centroid":[0.57018,0.1736,-0.00592],"force_p95":2.68941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.92689,"mean_force":0.57315,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.65607,0.22129,0.1594]},{"body_a":"grasp_target","body_b":"hand","contact_count":50.0,"contact_point_centroid":[0.56573,0.16761,0.02813],"force_p95":2.25582,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.81127,"mean_force":0.7563,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58331,0.2752,0.01276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":597.0,"contact_point_centroid":[0.5282,0.05219,0.0489],"force_p95":1.20828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.39776,"mean_force":0.35329,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.52903,0.07333,0.04989]},{"body_a":"world","body_b":"grasp_target","contact_count":526.0,"contact_point_centroid":[0.51639,0.03707,-0.00113],"force_p95":0.26344,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47371,"mean_force":0.08054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49979,0.03799,0.02751]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03936,-0.00213],"force_p95":0.1618,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24727,"mean_force":0.13322,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50035,0.03836,0.02615]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13391.0,"contact_point_centroid":[0.50591,0.05673,0.0424],"force_p95":0.0781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22965,"mean_force":0.05246,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50556,0.03765,0.04054]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12685.0,"contact_point_centroid":[0.5063,0.01851,0.04369],"force_p95":0.08137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21244,"mean_force":0.05381,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50588,0.03763,0.04138]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57299,0.19457,-0.00201],"force_p95":0.12575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15719,"mean_force":0.12205,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.69469,0.14842,0.29197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4050.0,"contact_point_centroid":[0.49981,0.01907,0.02768],"force_p95":0.08103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14471,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49916,0.03827,0.02488]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50283,0.01747,0.23098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.51414,0.05961,0.05944],"force_p95":0.05901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12655,"mean_force":0.0167,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.51413,0.04056,0.05763]}],"total_contact_groups":19},"final_pose_error":0.17152,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57299,0.19459,0.01602],"final_tcp_position":[0.69638,0.14938,0.28624],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1308.73387,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50775,0.03583,0.1622],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1604.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50745,0.03894,0.03387],"tcp_start":[0.50775,0.03583,0.1622],"tcp_to_object_dist_end":0.00937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03823,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21348,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1529,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10855.0,"raw_peak_contact_force":0.24727,"subtask_id":"grasp_1","tcp_end":[0.49914,0.03826,0.02485],"tcp_start":[0.50745,0.03894,0.03387],"tcp_to_object_dist_end":0.01327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":679.0,"n_steps_budget":600.0,"object_pos_end":[0.51873,0.03771,0.03601],"object_pos_start":[0.51239,0.03823,0.02556],"object_to_goal_dist_end":0.2047,"object_to_goal_dist_start":0.21348,"object_z_max":0.0523,"peak_contact_force":0.07085,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26602.0,"raw_peak_contact_force":0.47371,"tcp_end":[0.51288,0.03734,0.05835],"tcp_start":[0.50609,0.03783,0.03823],"tcp_to_object_dist_end":0.02309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.52432,0.03738,0.05233],"object_pos_start":[0.52432,0.03738,0.05233],"object_to_goal_dist_end":0.19369,"object_to_goal_dist_start":0.19369,"peak_contact_force":0.07085,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"transport_arc","tcp_end":[0.51288,0.03734,0.05835],"tcp_start":[0.51288,0.03734,0.05835],"tcp_to_object_dist_end":0.01293,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.57332,0.19614,0.01517],"object_pos_start":[0.52432,0.03738,0.05233],"object_to_goal_dist_end":0.1427,"object_to_goal_dist_start":0.19369,"object_z_max":0.05233,"peak_contact_force":335.176,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1908.0,"raw_peak_contact_force":1308.73387,"tcp_end":[0.69638,0.14938,0.28624],"tcp_start":[0.51288,0.03734,0.05835],"tcp_to_object_dist_end":0.30134,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57299,0.19459,0.01602],"object_pos_start":[0.57332,0.19614,0.01517],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.1427,"object_z_max":0.01607,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":978.0,"raw_peak_contact_force":184.07762,"subtask_id":"release_1","tcp_end":[0.69489,0.1492,0.31105],"tcp_start":[0.69638,0.14938,0.28624],"tcp_to_object_dist_end":0.32243,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```