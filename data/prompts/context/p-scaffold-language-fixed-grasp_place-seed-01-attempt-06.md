## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2287 | 0.35 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2014 | 0.24 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0520 | 0.20 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2735 | 0.38 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3448 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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

## Current Skill (Q=0.229) — your mutation base

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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_arc
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
- id: release_1
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
  subtask_id: release_1
- id: retract_1
  type: retract
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
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_arc_height: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.229
- **task_score** (E): 0.349
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1501 |
| descend_1 | 1.00 | 1.00 | 0.0980 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.0999 |
| transport_arc | 0.00 | 1.00 | 0.0309 |
| descend_2 | 1.00 | 1.00 | 0.0028 |
| release_1 | 1.00 | 1.00 | 0.0235 |
| retract_1 | 1.00 | 1.00 | 0.1320 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.478, -0.002, 0.156) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 9.270 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.478, -0.002, 0.156)→(0.475, -0.000, 0.058) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.475, -0.000, 0.058)→(0.467, -0.000, 0.050) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 36.667 | 0.157 | 0.217 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.000, 0.050)→(0.474, -0.001, 0.149) | (0.479, -0.000, 0.026)→(0.486, -0.000, 0.122) | 0.278→0.245 | 1.00 / 21.333 | 1107.069 | 0.354 |
| transport_arc | approach | 0.00 / guard_failure | (0.533, 0.082, 0.178)→(0.541, 0.107, 0.194) | (0.486, -0.000, 0.122)→(0.501, 0.023, 0.141) | 0.245→0.216 | 1.00 / 4.667 | 0.013 | 0.521 |
| descend_2 | descend | 1.00 / force_exceeded | (0.541, 0.107, 0.194)→(0.542, 0.109, 0.192) | (0.548, 0.106, 0.156)→(0.556, 0.116, 0.108) | 0.119→0.130 | 1.00 / 4.000 | 55992.160 | 0.129 |
| release_1 | release | 1.00 / step_budget | (0.542, 0.109, 0.192)→(0.536, 0.108, 0.215) | (0.556, 0.116, 0.108)→(0.568, 0.124, 0.016) | 0.130→0.167 | 1.00 / 4.000 | 0.124 | 1.571 |
| retract_1 | retract | 1.00 / step_budget | (0.536, 0.108, 0.215)→(0.601, 0.195, 0.285) | (0.568, 0.124, 0.016)→(0.568, 0.124, 0.016) | 0.167→0.167 | 1.00 / 4.000 | 0.123 | 0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.515
- phase_score: 0.394
- phase_breakdown.descend_1_score: 0.877
- phase_breakdown.transport_arc_score: 0.231
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.155
- phase_breakdown.approach_1_score: 0.124
- grasp_place_fitness: 0.719

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.719
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.515
- **Median Q (composite search score)**: 0.213
- **K-run variance**: 0.0042
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.405


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91667,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18495,"descend_1.grasp_z_offset":0.0107,"descend_2.descend_speed":0.04699,"descend_2.place_force_threshold":7.09244,"lift_1.lift_height":0.13101,"transport_arc.arc_speed":0.08911,"transport_arc.transport_arc_height":0.08215},"optimized_scores":{"best_composite_score":0.21338,"best_fitness_score":0.61838,"best_task_score":0.31318},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":465.0,"contact_point_centroid":[0.54686,0.13232,-0.00435],"force_p95":1.15274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69152,"mean_force":0.24307,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51653,0.13044,0.20295]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.4997,0.04212,-0.00151],"force_p95":0.34723,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3932,"mean_force":0.07465,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48802,0.04243,0.0486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5140.0,"contact_point_centroid":[0.49236,0.06156,0.08897],"force_p95":0.1071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28975,"mean_force":0.06444,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49052,0.04254,0.08763]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3185.0,"contact_point_centroid":[0.51033,0.09753,0.16325],"force_p95":0.15534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28625,"mean_force":0.09109,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50435,0.07895,0.16283]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4894.0,"contact_point_centroid":[0.49183,0.02355,0.08875],"force_p95":0.10868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28149,"mean_force":0.06528,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49053,0.04254,0.08782]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.0449,-0.0022],"force_p95":0.17839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23814,"mean_force":0.13722,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49011,0.04264,0.04816]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3254.0,"contact_point_centroid":[0.51075,0.06194,0.16402],"force_p95":0.15397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23078,"mean_force":0.08787,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50477,0.08045,0.16387]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4133.0,"contact_point_centroid":[0.48927,0.02334,0.04853],"force_p95":0.08036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14247,"mean_force":0.05163,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48902,0.04254,0.04698]},{"body_a":"world","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.50118,0.04505,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12344,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49895,0.01582,0.26646]},{"body_a":"world","body_b":"grasp_target","contact_count":1668.0,"contact_point_centroid":[0.54691,0.13119,-0.00199],"force_p95":0.12317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12454,"mean_force":0.12267,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53641,0.18307,0.24942]},{"body_a":"world","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49703,0.03831,0.14389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":23.0,"contact_point_centroid":[0.52876,0.11501,0.18933],"force_p95":0.09008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0935,"mean_force":0.02806,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52143,0.131,0.19576]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5126.0,"contact_point_centroid":[0.48914,0.06175,0.04874],"force_p95":0.07601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08111,"mean_force":0.04353,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48902,0.04254,0.04699]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.52924,0.11402,0.1887],"force_p95":0.04722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04912,"mean_force":0.03015,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52142,0.13155,0.19555]}],"total_contact_groups":14},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54691,0.13119,0.01602],"final_tcp_position":[0.55766,0.23336,0.282],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":27.56537,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":27.56537,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":600.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49859,0.03362,0.23088],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1324.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49719,0.04324,0.05618],"tcp_start":[0.49859,0.03362,0.23088],"tcp_to_object_dist_end":0.03048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04334,0.02528],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24366,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17368,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11059.0,"raw_peak_contact_force":0.23814,"subtask_id":"grasp_1","tcp_end":[0.48899,0.04254,0.04695],"tcp_start":[0.49719,0.04324,0.05618],"tcp_to_object_dist_end":0.02488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":295.0,"n_steps_budget":720.0,"object_pos_end":[0.51054,0.04365,0.11247],"object_pos_start":[0.50118,0.04334,0.02528],"object_to_goal_dist_end":0.21111,"object_to_goal_dist_start":0.24366,"object_z_max":0.11221,"peak_contact_force":0.11052,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10118.0,"raw_peak_contact_force":0.3932,"tcp_end":[0.49587,0.04289,0.13711],"tcp_start":[0.48899,0.04254,0.04695],"tcp_to_object_dist_end":0.02868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.51277,0.05767,0.12203],"object_pos_start":[0.51054,0.04365,0.11247],"object_to_goal_dist_end":0.19576,"object_to_goal_dist_start":0.21111,"object_z_max":0.16241,"peak_contact_force":0.0249,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6439.0,"raw_peak_contact_force":0.28625,"subtask_id":"transport_arc","tcp_end":[0.52141,0.1305,0.19573],"tcp_start":[0.49822,0.05764,0.14794],"tcp_to_object_dist_end":0.10398,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.53227,0.12989,0.15867],"object_pos_start":[0.53119,0.12899,0.16128],"object_to_goal_dist_end":0.11997,"object_to_goal_dist_start":0.12142,"object_z_max":0.16128,"peak_contact_force":8.05272,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23.0,"raw_peak_contact_force":0.0935,"tcp_end":[0.52142,0.13155,0.19555],"tcp_start":[0.52141,0.1305,0.19573],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54688,0.13106,0.01602],"object_pos_start":[0.53227,0.12989,0.15867],"object_to_goal_dist_end":0.17423,"object_to_goal_dist_start":0.11997,"object_z_max":0.15867,"peak_contact_force":0.12473,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":467.0,"raw_peak_contact_force":1.69152,"subtask_id":"release_1","tcp_end":[0.51627,0.13038,0.21917],"tcp_start":[0.52142,0.13155,0.19555],"tcp_to_object_dist_end":0.20544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":417.0,"n_steps_budget":930.0,"object_pos_end":[0.54691,0.13119,0.01602],"object_pos_start":[0.54688,0.13106,0.01602],"object_to_goal_dist_end":0.17414,"object_to_goal_dist_start":0.17423,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.12454,"tcp_end":[0.55766,0.23336,0.282],"tcp_start":[0.51627,0.13038,0.21917],"tcp_to_object_dist_end":0.28513,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85897,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05321,"descend_1.grasp_z_offset":0.01716,"descend_2.descend_speed":0.07438,"descend_2.place_force_threshold":8.02642,"lift_1.lift_height":0.16014,"transport_arc.arc_speed":0.20579,"transport_arc.transport_arc_height":0.12476},"optimized_scores":{"best_composite_score":0.15828,"best_fitness_score":0.56328,"best_task_score":0.219},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":785.0,"contact_point_centroid":[0.53741,0.04565,-0.00339],"force_p95":0.69036,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53446,"mean_force":0.18167,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49625,0.01856,0.21031]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.48998,0.01529,0.18591],"force_p95":0.15091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32087,"mean_force":0.11067,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48428,-0.0028,0.18939]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3795.0,"contact_point_centroid":[0.46782,-0.03744,0.10179],"force_p95":0.13919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29433,"mean_force":0.09488,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46635,-0.01903,0.10511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3674.0,"contact_point_centroid":[0.46828,-0.00057,0.10308],"force_p95":0.13839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29135,"mean_force":0.09725,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46644,-0.01903,0.10631]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.47435,-0.01832,-0.00139],"force_p95":0.25892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28446,"mean_force":0.05883,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46409,-0.01894,0.05575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1317.0,"contact_point_centroid":[0.48852,-0.02239,0.18385],"force_p95":0.16733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21967,"mean_force":0.11186,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48301,-0.0043,0.18733]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.02009,-0.00209],"force_p95":0.15036,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20293,"mean_force":0.12938,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46614,-0.01899,0.05538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":30.0,"contact_point_centroid":[0.50588,0.0298,0.20508],"force_p95":0.1623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19801,"mean_force":0.03779,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.49854,0.01444,0.2115]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48744,-0.00863,0.20238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2656.0,"contact_point_centroid":[0.46574,-0.00017,0.0514],"force_p95":0.10136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1319,"mean_force":0.07616,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46509,-0.01896,0.05432]},{"body_a":"world","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4738,-0.01839,0.08362]},{"body_a":"world","body_b":"grasp_target","contact_count":2628.0,"contact_point_centroid":[0.53795,0.04569,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55828,0.08567,0.27722]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2988.0,"contact_point_centroid":[0.46497,-0.03764,0.05127],"force_p95":0.09428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09461,"mean_force":0.06925,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4651,-0.01896,0.05432]}],"total_contact_groups":13},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53795,0.04569,0.01602],"final_tcp_position":[0.62156,0.14999,0.32551],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":16.69748,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47562,-0.01773,0.10304],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":332.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47287,-0.01913,0.06262],"tcp_start":[0.47562,-0.01773,0.10304],"tcp_to_object_dist_end":0.03676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47611,-0.01936,0.02569],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28811,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14654,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7444.0,"raw_peak_contact_force":0.20293,"subtask_id":"grasp_1","tcp_end":[0.46507,-0.01896,0.05429],"tcp_start":[0.47287,-0.01913,0.06262],"tcp_to_object_dist_end":0.03066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":352.0,"n_steps_budget":840.0,"object_pos_end":[0.48029,-0.01954,0.13295],"object_pos_start":[0.47611,-0.01936,0.02569],"object_to_goal_dist_end":0.24092,"object_to_goal_dist_start":0.28811,"object_z_max":0.13268,"peak_contact_force":0.12768,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7545.0,"raw_peak_contact_force":0.29433,"tcp_end":[0.47149,-0.0192,0.16648],"tcp_start":[0.46507,-0.01896,0.05429],"tcp_to_object_dist_end":0.03467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.01356,0.17324],"object_pos_start":[0.48029,-0.01954,0.13295],"object_to_goal_dist_end":0.19302,"object_to_goal_dist_start":0.24092,"object_z_max":0.17324,"peak_contact_force":0.01519,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2709.0,"raw_peak_contact_force":0.32087,"subtask_id":"transport_arc","tcp_end":[0.4983,0.01395,0.21157],"tcp_start":[0.49788,0.0131,0.21086],"tcp_to_object_dist_end":0.03908,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.5292,0.04268,0.03008],"object_pos_start":[0.50754,0.01591,0.17239],"object_to_goal_dist_end":0.22272,"object_to_goal_dist_start":0.19023,"object_z_max":0.17239,"peak_contact_force":16.69748,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30.0,"raw_peak_contact_force":0.19801,"tcp_end":[0.49989,0.01864,0.20645],"tcp_start":[0.4983,0.01395,0.21157],"tcp_to_object_dist_end":0.1804,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53795,0.04569,0.01602],"object_pos_start":[0.5292,0.04268,0.03008],"object_to_goal_dist_end":0.2278,"object_to_goal_dist_start":0.22272,"object_z_max":0.03008,"peak_contact_force":0.1226,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":785.0,"raw_peak_contact_force":1.53446,"subtask_id":"release_1","tcp_end":[0.49497,0.01849,0.23123],"tcp_start":[0.49989,0.01864,0.20645],"tcp_to_object_dist_end":0.22114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.53795,0.04569,0.01602],"object_pos_start":[0.53795,0.04569,0.01602],"object_to_goal_dist_end":0.2278,"object_to_goal_dist_start":0.2278,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2628.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62156,0.14999,0.32551],"tcp_start":[0.49497,0.01849,0.23123],"tcp_to_object_dist_end":0.33712,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99281,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08525,"descend_1.grasp_z_offset":0.01037,"descend_2.descend_speed":0.02407,"descend_2.place_force_threshold":1.19404,"lift_1.lift_height":0.13851,"transport_arc.arc_speed":0.15172,"transport_arc.transport_arc_height":0.06049},"optimized_scores":{"best_composite_score":0.31438,"best_fitness_score":0.71938,"best_task_score":0.5149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.61903,0.19402,-0.00372],"force_p95":0.79219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48608,"mean_force":0.20646,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59818,0.17581,0.17845]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5936.0,"contact_point_centroid":[0.52097,0.08015,0.16946],"force_p95":0.16602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.95524,"mean_force":0.10231,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51583,0.06165,0.17091]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.45675,-0.02443,-0.0014],"force_p95":0.33212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37531,"mean_force":0.07699,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44726,-0.02501,0.04965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.60493,0.16265,0.16877],"force_p95":0.20432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28706,"mean_force":0.0839,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60327,0.17753,0.1744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5854.0,"contact_point_centroid":[0.45022,-0.04409,0.09541],"force_p95":0.09237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27223,"mean_force":0.05704,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44942,-0.02506,0.09447]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5260.0,"contact_point_centroid":[0.45049,-0.00594,0.0958],"force_p95":0.09868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27123,"mean_force":0.06195,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44946,-0.02506,0.09499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6741.0,"contact_point_centroid":[0.52217,0.0444,0.17033],"force_p95":0.14674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27096,"mean_force":0.08914,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51661,0.06271,0.17143]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02622,-0.00211],"force_p95":0.1528,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20905,"mean_force":0.13055,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44926,-0.02509,0.04916]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.44912,-0.00584,0.04906],"force_p95":0.07984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14812,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44824,-0.02505,0.04817]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.13583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48049,-0.01101,0.21832]},{"body_a":"world","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.61909,0.19524,-0.00199],"force_p95":0.12304,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12364,"mean_force":0.12266,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61033,0.18984,0.2202]},{"body_a":"world","body_b":"grasp_target","contact_count":616.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4578,-0.02398,0.09576]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7.0,"contact_point_centroid":[0.60725,0.16124,0.16986],"force_p95":0.09055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09441,"mean_force":0.04995,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60365,0.17734,0.17516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4969.0,"contact_point_centroid":[0.4483,-0.04414,0.04921],"force_p95":0.07145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07365,"mean_force":0.04411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44824,-0.02505,0.04818]}],"total_contact_groups":14},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61909,0.19524,0.01602],"final_tcp_position":[0.62319,0.20297,0.24624],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46095,-0.02276,0.13429],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":616.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45587,-0.02531,0.05591],"tcp_start":[0.46095,-0.02276,0.13429],"tcp_to_object_dist_end":0.03003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02541,0.02561],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3031,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14974,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10864.0,"raw_peak_contact_force":0.20905,"subtask_id":"grasp_1","tcp_end":[0.44821,-0.02505,0.04815],"tcp_start":[0.45587,-0.02531,0.05591],"tcp_to_object_dist_end":0.02478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":298.0,"n_steps_budget":750.0,"object_pos_end":[0.46824,-0.02557,0.12033],"object_pos_start":[0.45851,-0.02541,0.02561],"object_to_goal_dist_end":0.28444,"object_to_goal_dist_start":0.3031,"object_z_max":0.12005,"peak_contact_force":3320.96995,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11190.0,"raw_peak_contact_force":0.37531,"tcp_end":[0.45377,-0.0252,0.14489],"tcp_start":[0.44821,-0.02505,0.04815],"tcp_to_object_dist_end":0.02851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.48291,-0.00328,0.1283],"object_pos_start":[0.46824,-0.02557,0.12033],"object_to_goal_dist_end":0.25807,"object_to_goal_dist_start":0.28444,"object_z_max":0.15084,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12677.0,"raw_peak_contact_force":0.95524,"subtask_id":"transport_arc","tcp_end":[0.60365,0.17734,0.17516],"tcp_start":[0.60366,0.1765,0.17603],"tcp_to_object_dist_end":0.22225,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.60585,0.17445,0.13468],"object_pos_start":[0.60573,0.1743,0.13508],"object_to_goal_dist_end":0.04639,"object_to_goal_dist_start":0.04675,"object_z_max":0.13508,"peak_contact_force":167951.73011,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7.0,"raw_peak_contact_force":0.09441,"tcp_end":[0.6036,0.17743,0.17502],"tcp_start":[0.60365,0.17734,0.17516],"tcp_to_object_dist_end":0.04052,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61912,0.19524,0.01602],"object_pos_start":[0.60585,0.17445,0.13468],"object_to_goal_dist_end":0.09956,"object_to_goal_dist_start":0.04639,"object_z_max":0.13468,"peak_contact_force":0.12367,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":573.0,"raw_peak_contact_force":1.48608,"subtask_id":"release_1","tcp_end":[0.59785,0.17569,0.19525],"tcp_start":[0.6036,0.17743,0.17502],"tcp_to_object_dist_end":0.18154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":260.0,"n_steps_budget":600.0,"object_pos_end":[0.61909,0.19524,0.01602],"object_pos_start":[0.61912,0.19524,0.01602],"object_to_goal_dist_end":0.09957,"object_to_goal_dist_start":0.09956,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1040.0,"raw_peak_contact_force":0.12364,"tcp_end":[0.62319,0.20297,0.24624],"tcp_start":[0.59785,0.17569,0.19525],"tcp_to_object_dist_end":0.23039,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```