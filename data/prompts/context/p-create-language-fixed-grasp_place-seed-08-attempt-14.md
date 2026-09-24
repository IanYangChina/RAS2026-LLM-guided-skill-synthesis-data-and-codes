## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → contact → lift → grasp → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1413 | 0.19 | ❌ rejected |
| 13 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1549 | 0.19 | ❌ rejected |
| 12 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3310 | 0.26 | ✅ accepted |
| 11 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2594 | 0.22 | ❌ rejected |
| 10 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4248 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.141) — your mutation base

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
    - 0.08
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.08
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
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  end_effector_action: force_grasp
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
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: grasp_1
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
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_to_goal
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
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1
- id: release_grasp
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **release_grasp** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.141
- **task_score** (E): 0.187
- **fitness_score**: 0.546  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0631 |
| descend_1 | 1.00 | 1.00 | 0.2200 |
| contact_1 | 1.00 | 1.00 | 0.0096 |
| lift_1 | 1.00 | 1.00 | 0.1050 |
| grasp_tighten | 1.00 | 1.00 | 0.0112 |
| transport_1 | 0.00 | 1.00 | 0.0842 |
| descend_to_goal | 0.00 | 1.00 | 0.0910 |
| release_grasp | 1.00 | 1.00 | 0.0225 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, -0.001, 0.275) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, -0.001, 0.275)→(0.517, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.055)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 44.333 | 0.140 | 0.184 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.152) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.125) | 0.289→0.243 | 1.00 / 27.667 | 82.715 | 0.444 |
| grasp_tighten | grasp | 1.00 / step_budget | (0.507, -0.001, 0.152)→(0.501, -0.001, 0.143) | (0.518, -0.001, 0.125)→(0.506, -0.001, 0.112) | 0.243→0.252 | 1.00 / 23.333 | 0.114 | 0.182 |
| transport_1 | approach | 0.00 / step_budget | (0.501, -0.001, 0.143)→(0.529, 0.061, 0.190) | (0.506, -0.001, 0.112)→(0.531, 0.058, 0.058) | 0.252→0.233 | 1.00 / 11.000 | 3249.663 | 1.004 |
| descend_to_goal | descend | 0.00 / step_budget | (0.529, 0.061, 0.190)→(0.570, 0.142, 0.190) | (0.531, 0.058, 0.058)→(0.536, 0.058, 0.016) | 0.233→0.253 | 1.00 / 8.333 | 6499.286 | 0.572 |
| release_grasp | release | 1.00 / step_budget | (0.570, 0.142, 0.190)→(0.564, 0.140, 0.212) | (0.536, 0.058, 0.016)→(0.536, 0.058, 0.016) | 0.253→0.253 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.233
- phase_score: 0.308
- phase_breakdown.approach_1_score: 0.005
- phase_breakdown.descend_1_score: 0.874
- phase_breakdown.transport_arc_score: 0.045
- phase_breakdown.release_1_score: 0.305
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.571

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.571
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.233
- **Median Q (composite search score)**: 0.130
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: grasp_tighten.tighten_time
- **Final σ (mean)**: 0.530


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14833,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29281,"contact_1.contact_force":14.2501,"descend_to_goal.descend_speed":0.02024,"grasp_tighten.tighten_time":0.10001,"lift_1.lift_height":0.10051,"transport_1.arc_height":0.02167,"transport_1.transport_speed":0.02852},"optimized_scores":{"best_composite_score":0.13031,"best_fitness_score":0.53531,"best_task_score":0.16779},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1471.0,"contact_point_centroid":[0.48264,0.10284,-0.00262],"force_p95":0.32189,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16653,"mean_force":0.14774,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48632,0.0877,0.17958]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.48031,0.04656,-0.00118],"force_p95":0.25534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39925,"mean_force":0.05647,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47153,0.04734,0.04995]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4382.0,"contact_point_centroid":[0.47181,0.04218,0.14211],"force_p95":0.13673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33729,"mean_force":0.11142,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46848,0.0603,0.14579]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10727.0,"contact_point_centroid":[0.46909,0.02803,0.0929],"force_p95":0.08374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29665,"mean_force":0.05547,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46907,0.04711,0.09233]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11053.0,"contact_point_centroid":[0.46984,0.06619,0.09219],"force_p95":0.08326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2956,"mean_force":0.05476,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46911,0.04712,0.09113]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4894.0,"contact_point_centroid":[0.4729,0.07922,0.14294],"force_p95":0.13019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21245,"mean_force":0.10084,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46906,0.06129,0.14709]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.48273,0.04861,-0.00211],"force_p95":0.15184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20778,"mean_force":0.13104,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47361,0.04755,0.04871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5618.0,"contact_point_centroid":[0.46695,0.06505,0.12926],"force_p95":0.12229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18705,"mean_force":0.07672,"phase_index":4.0,"phase_name":"grasp_tighten","phase_type":"grasp","tcp_position_centroid":[0.46387,0.04664,0.13093]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5298.0,"contact_point_centroid":[0.46632,0.02815,0.12851],"force_p95":0.12718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18338,"mean_force":0.0823,"phase_index":4.0,"phase_name":"grasp_tighten","phase_type":"grasp","tcp_position_centroid":[0.46385,0.04664,0.1309]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4097.0,"contact_point_centroid":[0.47226,0.02829,0.04914],"force_p95":0.0793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14452,"mean_force":0.05204,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47301,0.0475,0.04807]},{"body_a":"world","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48977,0.02235,0.30616]},{"body_a":"world","body_b":"grasp_target","contact_count":3212.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47943,0.04537,0.18336]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4826,0.10299,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.51367,0.13231,0.19488]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4826,0.10299,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_grasp","phase_type":"release","tcp_position_centroid":[0.5299,0.16041,0.20571]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.47311,0.0666,0.04913],"force_p95":0.07237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07331,"mean_force":0.04424,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47302,0.0475,0.04807]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1235.0,"contact_point_centroid":[0.48798,0.08956,0.18389],"force_p95":0.0125,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01089,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48755,0.08954,0.18164]}],"total_contact_groups":18},"final_pose_error":0.08737,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.4826,0.10299,0.01602],"final_tcp_position":[0.53346,0.16146,0.20314],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.78861,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1328.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48229,0.0429,0.31472],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":803.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3212.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47844,0.04801,0.05495],"tcp_start":[0.48229,0.0429,0.31472],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.48265,0.04779,0.02563],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29086,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14888,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10703.0,"raw_peak_contact_force":0.20778,"subtask_id":"grasp_1","tcp_end":[0.47299,0.04749,0.04804],"tcp_start":[0.47844,0.04801,0.05495],"tcp_to_object_dist_end":0.02441,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.47915,0.04766,0.11036],"object_pos_start":[0.48265,0.04779,0.02563],"object_to_goal_dist_end":0.24045,"object_to_goal_dist_start":0.29086,"object_z_max":0.11025,"peak_contact_force":0.0926,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21920.0,"raw_peak_contact_force":0.39925,"tcp_end":[0.46912,0.04712,0.13724],"tcp_start":[0.47299,0.04749,0.04804],"tcp_to_object_dist_end":0.02869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46788,0.04713,0.09747],"object_pos_start":[0.47915,0.04766,0.11036],"object_to_goal_dist_end":0.25241,"object_to_goal_dist_start":0.24045,"object_z_max":0.11039,"peak_contact_force":0.12442,"phase_name":"grasp_tighten","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10916.0,"raw_peak_contact_force":0.18705,"tcp_end":[0.46264,0.04653,0.12945],"tcp_start":[0.46912,0.04712,0.13724],"tcp_to_object_dist_end":0.03241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4826,0.10299,0.01602],"object_pos_start":[0.46788,0.04713,0.09747],"object_to_goal_dist_end":0.26775,"object_to_goal_dist_start":0.25241,"object_z_max":0.12655,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11982.0,"raw_peak_contact_force":1.16653,"subtask_id":"transport_arc","tcp_end":[0.49248,0.09695,0.18954],"tcp_start":[0.46264,0.04653,0.12945],"tcp_to_object_dist_end":0.1739,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4826,0.10299,0.01602],"object_pos_start":[0.4826,0.10299,0.01602],"object_to_goal_dist_end":0.26775,"object_to_goal_dist_start":0.26775,"object_z_max":0.01602,"peak_contact_force":9748.78861,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8260.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.53346,0.16146,0.20314],"tcp_start":[0.49248,0.09695,0.18954],"tcp_to_object_dist_end":0.20253,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.10299,0.01602],"object_pos_start":[0.4826,0.10299,0.01602],"object_to_goal_dist_end":0.26775,"object_to_goal_dist_start":0.26775,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52855,0.15994,0.22612],"tcp_start":[0.53346,0.16146,0.20314],"tcp_to_object_dist_end":0.22248,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.575,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17864,"contact_1.contact_force":10.00267,"descend_to_goal.descend_speed":0.0611,"grasp_tighten.tighten_time":0.35772,"lift_1.lift_height":0.13477,"transport_1.arc_height":0.02078,"transport_1.transport_speed":0.06182},"optimized_scores":{"best_composite_score":0.12732,"best_fitness_score":0.53232,"best_task_score":0.16079},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":741.0,"contact_point_centroid":[0.55295,0.03971,-0.00345],"force_p95":0.71099,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66787,"mean_force":0.18923,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53831,0.04774,0.19854]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53431,-0.02066,-0.00116],"force_p95":0.31535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48047,"mean_force":0.06609,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52442,-0.02087,0.0484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13506.0,"contact_point_centroid":[0.52347,-0.03974,0.10108],"force_p95":0.09521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28879,"mean_force":0.05789,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52187,-0.02081,0.10023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12196.0,"contact_point_centroid":[0.52367,-0.0018,0.1014],"force_p95":0.10201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28217,"mean_force":0.0633,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52187,-0.02081,0.10052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5878.0,"contact_point_centroid":[0.52879,0.02684,0.17154],"force_p95":0.13614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23806,"mean_force":0.10861,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52337,0.00856,0.17483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6949.0,"contact_point_centroid":[0.52841,-0.00944,0.17134],"force_p95":0.12061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18742,"mean_force":0.09305,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52334,0.00855,0.17478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5678.0,"contact_point_centroid":[0.52206,-0.03928,0.16067],"force_p95":0.09463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18128,"mean_force":0.07342,"phase_index":4.0,"phase_name":"grasp_tighten","phase_type":"grasp","tcp_position_centroid":[0.5168,-0.02068,0.16075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5449.0,"contact_point_centroid":[0.52212,-0.00198,0.16049],"force_p95":0.11856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17634,"mean_force":0.07784,"phase_index":4.0,"phase_name":"grasp_tighten","phase_type":"grasp","tcp_position_centroid":[0.51684,-0.02068,0.16081]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.53703,-0.02128,-0.00205],"force_p95":0.13569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16538,"mean_force":0.12661,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52666,-0.02091,0.04746]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51338,-0.00904,0.25662]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4448.0,"contact_point_centroid":[0.5263,-0.00171,0.04773],"force_p95":0.07366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12522,"mean_force":0.04857,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52605,-0.0209,0.04672]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55299,0.04003,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55839,0.10595,0.197]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5292,-0.01976,0.13341]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55299,0.04003,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_grasp","phase_type":"release","tcp_position_centroid":[0.57121,0.14658,0.199]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.52621,-0.04003,0.04821],"force_p95":0.06879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08778,"mean_force":0.04451,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52605,-0.0209,0.04672]},{"body_a":"left_finger","body_b":"right_finger","contact_count":558.0,"contact_point_centroid":[0.5396,0.04973,0.20202],"force_p95":0.01351,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01085,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53908,0.04973,0.19961]}],"total_contact_groups":18},"final_pose_error":0.08824,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55299,0.04003,0.01602],"final_tcp_position":[0.57498,0.14752,0.19738],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.74502,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1268.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52917,-0.01859,0.21401],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53175,-0.02099,0.05427],"tcp_start":[0.52917,-0.01859,0.21401],"tcp_to_object_dist_end":0.02874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02102,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31661,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13513,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10968.0,"raw_peak_contact_force":0.16538,"subtask_id":"grasp_1","tcp_end":[0.52603,-0.0209,0.04669],"tcp_start":[0.53175,-0.02099,0.05427],"tcp_to_object_dist_end":0.02355,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":755.0,"n_steps_budget":840.0,"object_pos_end":[0.53276,-0.02109,0.1412],"object_pos_start":[0.53695,-0.02102,0.02582],"object_to_goal_dist_end":0.26892,"object_to_goal_dist_start":0.31661,"object_z_max":0.14109,"peak_contact_force":0.09455,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25848.0,"raw_peak_contact_force":0.48047,"tcp_end":[0.52219,-0.02081,0.16877],"tcp_start":[0.52603,-0.0209,0.04669],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52155,-0.02098,0.1277],"object_pos_start":[0.53276,-0.02109,0.1412],"object_to_goal_dist_end":0.27586,"object_to_goal_dist_start":0.26892,"object_z_max":0.14124,"peak_contact_force":0.1267,"phase_name":"grasp_tighten","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11127.0,"raw_peak_contact_force":0.18128,"tcp_end":[0.51575,-0.02066,0.1592],"tcp_start":[0.52219,-0.02081,0.16877],"tcp_to_object_dist_end":0.03204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55299,0.04002,0.01602],"object_pos_start":[0.52155,-0.02098,0.1277],"object_to_goal_dist_end":0.27415,"object_to_goal_dist_start":0.27586,"object_z_max":0.15237,"peak_contact_force":9748.74502,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14126.0,"raw_peak_contact_force":1.66787,"subtask_id":"transport_arc","tcp_end":[0.54096,0.05458,0.20214],"tcp_start":[0.51575,-0.02066,0.1592],"tcp_to_object_dist_end":0.18708,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55299,0.04003,0.01602],"object_pos_start":[0.55299,0.04002,0.01602],"object_to_goal_dist_end":0.27415,"object_to_goal_dist_start":0.27415,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8245.0,"raw_peak_contact_force":0.12264,"subtask_id":"release_1","tcp_end":[0.57498,0.14752,0.19738],"tcp_start":[0.54096,0.05458,0.20214],"tcp_to_object_dist_end":0.21197,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55299,0.04003,0.01602],"object_pos_start":[0.55299,0.04003,0.01602],"object_to_goal_dist_end":0.27415,"object_to_goal_dist_start":0.27415,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56978,0.14615,0.21897],"tcp_start":[0.57498,0.14752,0.19738],"tcp_to_object_dist_end":0.22963,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63924,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27144,"contact_1.contact_force":7.40062,"descend_to_goal.descend_speed":0.07521,"grasp_tighten.tighten_time":0.79792,"lift_1.lift_height":0.11603,"transport_1.arc_height":0.02008,"transport_1.transport_speed":0.06653},"optimized_scores":{"best_composite_score":0.1662,"best_fitness_score":0.5712,"best_task_score":0.23327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3350.0,"contact_point_centroid":[0.57189,0.03054,-0.00227],"force_p95":0.12548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47018,"mean_force":0.13413,"phase_index":6.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58276,0.08648,0.17092]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.54317,-0.0284,-0.00116],"force_p95":0.30483,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45358,"mean_force":0.07049,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53283,-0.02869,0.04747]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11329.0,"contact_point_centroid":[0.53158,-0.00952,0.09412],"force_p95":0.09904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28308,"mean_force":0.06011,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53024,-0.02859,0.09257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12882.0,"contact_point_centroid":[0.53159,-0.04758,0.09292],"force_p95":0.09168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26984,"mean_force":0.05386,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53026,-0.02859,0.09148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":680.0,"contact_point_centroid":[0.56152,0.05625,0.17038],"force_p95":0.16723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25265,"mean_force":0.11762,"phase_index":6.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55594,0.03813,0.17599]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5772.0,"contact_point_centroid":[0.52892,-0.00974,0.1401],"force_p95":0.10218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1784,"mean_force":0.07272,"phase_index":4.0,"phase_name":"grasp_tighten","phase_type":"grasp","tcp_position_centroid":[0.52459,-0.02839,0.1407]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.5456,-0.02913,-0.00206],"force_p95":0.13685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17798,"mean_force":0.12712,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53518,-0.02876,0.04661]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10613.0,"contact_point_centroid":[0.54132,-0.01711,0.15594],"force_p95":0.11984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17665,"mean_force":0.08494,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53663,0.0012,0.15833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6285.0,"contact_point_centroid":[0.52861,-0.04699,0.14017],"force_p95":0.09665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17625,"mean_force":0.06757,"phase_index":4.0,"phase_name":"grasp_tighten","phase_type":"grasp","tcp_position_centroid":[0.52466,-0.02839,0.1408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9649.0,"contact_point_centroid":[0.54155,0.01966,0.1559],"force_p95":0.12962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17334,"mean_force":0.09314,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53665,0.00122,0.15834]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.5456,-0.02923,-0.00191],"force_p95":0.13487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51994,-0.01423,0.29582]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":802.0,"contact_point_centroid":[0.56168,0.02125,0.17036],"force_p95":0.12335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13203,"mean_force":0.09547,"phase_index":6.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55629,0.03901,0.17567]},{"body_a":"world","body_b":"grasp_target","contact_count":2816.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5386,-0.02761,0.17349]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57189,0.03053,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_grasp","phase_type":"release","tcp_position_centroid":[0.5961,0.11508,0.17097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4843.0,"contact_point_centroid":[0.53403,-0.00943,0.04785],"force_p95":0.06814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09834,"mean_force":0.04505,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53451,-0.02874,0.04578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5871.0,"contact_point_centroid":[0.53431,-0.04794,0.04764],"force_p95":0.06078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07679,"mean_force":0.03791,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53451,-0.02874,0.04578]}],"total_contact_groups":18},"final_pose_error":0.0593,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.57189,0.03053,0.01602],"final_tcp_position":[0.60032,0.11586,0.16982],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.94652,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53863,-0.02639,0.29491],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":704.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2816.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54054,-0.02891,0.05447],"tcp_start":[0.53863,-0.02639,0.29491],"tcp_to_object_dist_end":0.0289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.54552,-0.02876,0.0258],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26073,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13549,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12362.0,"raw_peak_contact_force":0.17798,"subtask_id":"grasp_1","tcp_end":[0.53448,-0.02874,0.04575],"tcp_start":[0.54054,-0.02891,0.05447],"tcp_to_object_dist_end":0.0228,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.54211,-0.02874,0.12368],"object_pos_start":[0.54552,-0.02876,0.0258],"object_to_goal_dist_end":0.2204,"object_to_goal_dist_start":0.26073,"object_z_max":0.12357,"peak_contact_force":247.95676,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24361.0,"raw_peak_contact_force":0.45358,"tcp_end":[0.53043,-0.02859,0.14915],"tcp_start":[0.53448,-0.02874,0.04575],"tcp_to_object_dist_end":0.02802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52986,-0.02858,0.10993],"object_pos_start":[0.54211,-0.02874,0.12368],"object_to_goal_dist_end":0.22922,"object_to_goal_dist_start":0.2204,"object_z_max":0.12372,"peak_contact_force":0.0914,"phase_name":"grasp_tighten","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12057.0,"raw_peak_contact_force":0.1784,"tcp_end":[0.52366,-0.02836,0.13937],"tcp_start":[0.53043,-0.02859,0.14915],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5588,0.03158,0.14148],"object_pos_start":[0.52986,-0.02858,0.10993],"object_to_goal_dist_end":0.15659,"object_to_goal_dist_start":0.22922,"object_z_max":0.14145,"peak_contact_force":0.12269,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20262.0,"raw_peak_contact_force":0.17665,"subtask_id":"transport_arc","tcp_end":[0.55398,0.03191,0.17949],"tcp_start":[0.52366,-0.02836,0.13937],"tcp_to_object_dist_end":0.03832,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57189,0.03053,0.01602],"object_pos_start":[0.5588,0.03158,0.14148],"object_to_goal_dist_end":0.21833,"object_to_goal_dist_start":0.15659,"object_z_max":0.14148,"peak_contact_force":9748.94652,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8094.0,"raw_peak_contact_force":1.47018,"subtask_id":"release_1","tcp_end":[0.60032,0.11586,0.16982],"tcp_start":[0.55398,0.03191,0.17949],"tcp_to_object_dist_end":0.17817,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57189,0.03053,0.01602],"object_pos_start":[0.57189,0.03053,0.01602],"object_to_goal_dist_end":0.21833,"object_to_goal_dist_start":0.21833,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_grasp","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59447,0.1147,0.19073],"tcp_start":[0.60032,0.11586,0.16982],"tcp_to_object_dist_end":0.19524,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```