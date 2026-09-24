## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2014 | 0.24 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0520 | 0.20 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2735 | 0.38 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3448 | 0.34 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3429 | 0.34 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.201) — your mutation base

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

- **Composite score**: 0.201
- **task_score** (E): 0.239
- **fitness_score**: 0.581  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0815 |
| descend_1 | 1.00 | 1.00 | 0.1715 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1060 |
| transport_arc | 1.00 | 1.00 | 0.2581 |
| descend_2 | 1.00 | 1.00 | 0.0903 |
| release_1 | 1.00 | 1.00 | 0.0199 |
| retract_1 | 1.00 | 1.00 | 0.0841 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.484, 0.002, 0.227) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.484, 0.002, 0.227)→(0.476, -0.000, 0.056) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.476, -0.000, 0.056)→(0.468, -0.000, 0.048) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 41.000 | 0.155 | 0.213 |
| lift_1 | lift | 1.00 / step_budget | (0.468, -0.000, 0.048)→(0.474, -0.000, 0.153) | (0.479, -0.000, 0.026)→(0.488, -0.001, 0.129) | 0.278→0.243 | 1.00 / 25.333 | 0.271 | 0.388 |
| transport_arc | approach | 1.00 / step_budget | (0.474, -0.000, 0.153)→(0.598, 0.190, 0.268) | (0.488, -0.001, 0.129)→(0.530, 0.061, 0.016) | 0.243→0.216 | 1.00 / 8.333 | 94255.813 | 1.841 |
| descend_2 | descend | 1.00 / step_budget | (0.598, 0.190, 0.268)→(0.603, 0.199, 0.178) | (0.530, 0.061, 0.016)→(0.530, 0.061, 0.016) | 0.216→0.216 | 1.00 / 8.333 | 3249.689 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.603, 0.199, 0.178)→(0.597, 0.197, 0.197) | (0.530, 0.061, 0.016)→(0.530, 0.061, 0.016) | 0.216→0.216 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.597, 0.197, 0.197)→(0.605, 0.202, 0.281) | (0.530, 0.061, 0.016)→(0.530, 0.061, 0.016) | 0.216→0.216 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.277
- phase_score: 0.368
- phase_breakdown.descend_1_score: 0.862
- phase_breakdown.transport_arc_score: 0.136
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.366
- phase_breakdown.approach_1_score: 0.052
- grasp_place_fitness: 0.600

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.600
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.277
- **Median Q (composite search score)**: 0.196
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9162,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12922,"descend_1.grasp_z_offset":0.01045,"lift_1.lift_height":0.14616,"transport_arc.transport_arc_height":0.10746},"optimized_scores":{"best_composite_score":0.22034,"best_fitness_score":0.60034,"best_task_score":0.27654},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1551.0,"contact_point_centroid":[0.53214,0.10678,-0.00269],"force_p95":0.29927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74024,"mean_force":0.15472,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53615,0.16879,0.22982]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.4994,0.04231,-0.0015],"force_p95":0.36397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40433,"mean_force":0.07669,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48782,0.04252,0.0483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.50674,0.08173,0.1695],"force_p95":0.15405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31305,"mean_force":0.09242,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50057,0.06308,0.16888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5737.0,"contact_point_centroid":[0.49257,0.0616,0.09465],"force_p95":0.10908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29285,"mean_force":0.06669,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49037,0.04264,0.09335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5423.0,"contact_point_centroid":[0.49201,0.0237,0.09408],"force_p95":0.11083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26718,"mean_force":0.06782,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49034,0.04263,0.09314]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2345.0,"contact_point_centroid":[0.50732,0.04744,0.17135],"force_p95":0.13284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25169,"mean_force":0.08262,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50137,0.06586,0.17118]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.0449,-0.00219],"force_p95":0.17576,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23299,"mean_force":0.13651,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48995,0.04274,0.04788]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4204.0,"contact_point_centroid":[0.48902,0.02347,0.04825],"force_p95":0.07998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1574,"mean_force":0.05072,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48885,0.04264,0.0467]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.50118,0.04505,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49858,0.01788,0.23964]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49674,0.0402,0.11705]},{"body_a":"world","body_b":"grasp_target","contact_count":520.0,"contact_point_centroid":[0.53218,0.10688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55786,0.23375,0.21164]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53218,0.10688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55514,0.23711,0.17515]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.53218,0.10688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55637,0.2392,0.23591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.48943,0.06187,0.04821],"force_p95":0.07904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08075,"mean_force":0.04559,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48886,0.04264,0.04671]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1437.0,"contact_point_centroid":[0.5391,0.17644,0.23516],"force_p95":0.01201,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0161,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53881,0.17642,0.23287]},{"body_a":"left_finger","body_b":"right_finger","contact_count":559.0,"contact_point_centroid":[0.55815,0.23377,0.21388],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01038,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55786,0.23375,0.21163]}],"total_contact_groups":17},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.53218,0.10688,0.01602],"final_tcp_position":[0.5609,0.24271,0.27742],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273018.37974,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49816,0.03728,0.17723],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":928.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49702,0.04334,0.05589],"tcp_start":[0.49816,0.03728,0.17723],"tcp_to_object_dist_end":0.03021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50117,0.04346,0.02532],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24355,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17035,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10882.0,"raw_peak_contact_force":0.23299,"subtask_id":"grasp_1","tcp_end":[0.48883,0.04263,0.04667],"tcp_start":[0.49702,0.04334,0.05589],"tcp_to_object_dist_end":0.02468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":344.0,"n_steps_budget":810.0,"object_pos_end":[0.51087,0.04364,0.12717],"object_pos_start":[0.50117,0.04346,0.02532],"object_to_goal_dist_end":0.20915,"object_to_goal_dist_start":0.24355,"object_z_max":0.1269,"peak_contact_force":0.11043,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11243.0,"raw_peak_contact_force":0.40433,"tcp_end":[0.49613,0.04302,0.15217],"tcp_start":[0.48883,0.04263,0.04667],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.53218,0.10688,0.01602],"object_pos_start":[0.51087,0.04364,0.12717],"object_to_goal_dist_end":0.19281,"object_to_goal_dist_start":0.20915,"object_z_max":0.16021,"peak_contact_force":273018.37974,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7389.0,"raw_peak_contact_force":1.74024,"subtask_id":"transport_arc","tcp_end":[0.55688,0.22892,0.24508],"tcp_start":[0.49613,0.04302,0.15217],"tcp_to_object_dist_end":0.26072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":130.0,"n_steps_budget":1000.0,"object_pos_end":[0.53218,0.10688,0.01602],"object_pos_start":[0.53218,0.10688,0.01602],"object_to_goal_dist_end":0.19281,"object_to_goal_dist_start":0.19281,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1079.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55948,0.23897,0.17503],"tcp_start":[0.55688,0.22892,0.24508],"tcp_to_object_dist_end":0.20851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53218,0.10688,0.01602],"object_pos_start":[0.53218,0.10688,0.01602],"object_to_goal_dist_end":0.19281,"object_to_goal_dist_start":0.19281,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55372,0.2364,0.19519],"tcp_start":[0.55948,0.23897,0.17503],"tcp_to_object_dist_end":0.22213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":660.0,"object_pos_end":[0.53218,0.10688,0.01602],"object_pos_start":[0.53218,0.10688,0.01602],"object_to_goal_dist_end":0.19281,"object_to_goal_dist_start":0.19281,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5609,0.24271,0.27742],"tcp_start":[0.55372,0.2364,0.19519],"tcp_to_object_dist_end":0.29598,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86559,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18825,"descend_1.grasp_z_offset":0.01,"lift_1.lift_height":0.15425,"transport_arc.transport_arc_height":0.0818},"optimized_scores":{"best_composite_score":0.18793,"best_fitness_score":0.56793,"best_task_score":0.2098},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1927.0,"contact_point_centroid":[0.53587,0.03487,-0.00254],"force_p95":0.21744,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86511,"mean_force":0.14812,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56711,0.09015,0.24484]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47423,-0.01879,-0.00141],"force_p95":0.34622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38896,"mean_force":0.08097,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46431,-0.01916,0.04852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5856.0,"contact_point_centroid":[0.46799,-0.00012,0.09997],"force_p95":0.10562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27928,"mean_force":0.06504,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46645,-0.01918,0.09886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6506.0,"contact_point_centroid":[0.46776,-0.03816,0.0998],"force_p95":0.09913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27375,"mean_force":0.05975,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46644,-0.01918,0.09864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2483.0,"contact_point_centroid":[0.49186,-0.01889,0.18078],"force_p95":0.13989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2661,"mean_force":0.0837,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48586,-0.00049,0.18036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2116.0,"contact_point_centroid":[0.49061,0.0166,0.17957],"force_p95":0.15963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24059,"mean_force":0.0928,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48453,-0.00206,0.17871]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02006,-0.00208],"force_p95":0.14641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19503,"mean_force":0.12888,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46637,-0.01921,0.04822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.46623,3e-05,0.04846],"force_p95":0.07928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14111,"mean_force":0.05213,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46532,-0.01918,0.04716]},{"body_a":"world","body_b":"grasp_target","contact_count":512.0,"contact_point_centroid":[0.47616,-0.02015,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12358,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49071,-0.00668,0.26981]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47628,-0.01681,0.14644]},{"body_a":"world","body_b":"grasp_target","contact_count":348.0,"contact_point_centroid":[0.53584,0.03486,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62118,0.15026,0.24172]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53584,0.03486,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62026,0.15276,0.21649]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.53584,0.03486,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62284,0.15492,0.27787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4933.0,"contact_point_centroid":[0.4654,-0.03827,0.04851],"force_p95":0.07036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07247,"mean_force":0.04433,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46532,-0.01918,0.04716]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1839.0,"contact_point_centroid":[0.57225,0.09572,0.24991],"force_p95":0.01126,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57216,0.09571,0.24768]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.62279,0.15351,0.21508],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01256,"mean_force":0.00987,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62248,0.15349,0.21262]}],"total_contact_groups":17},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53584,0.03486,0.01602],"final_tcp_position":[0.62831,0.15782,0.32045],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.82189,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.1226,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":512.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48092,-0.01439,0.23669],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1384.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.4732,-0.01935,0.05547],"tcp_start":[0.48092,-0.01439,0.23669],"tcp_to_object_dist_end":0.02961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01942,0.0257],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28815,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14391,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10833.0,"raw_peak_contact_force":0.19503,"subtask_id":"grasp_1","tcp_end":[0.46529,-0.01918,0.04713],"tcp_start":[0.4732,-0.01935,0.05547],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":354.0,"n_steps_budget":840.0,"object_pos_end":[0.48639,-0.01958,0.13628],"object_pos_start":[0.4761,-0.01942,0.0257],"object_to_goal_dist_end":0.23639,"object_to_goal_dist_start":0.28815,"object_z_max":0.13601,"peak_contact_force":0.10563,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12436.0,"raw_peak_contact_force":0.38896,"tcp_end":[0.47147,-0.01928,0.16061],"tcp_start":[0.46529,-0.01918,0.04713],"tcp_to_object_dist_end":0.02854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.53584,0.03486,0.01602],"object_pos_start":[0.48639,-0.01958,0.13628],"object_to_goal_dist_end":0.23424,"object_to_goal_dist_start":0.23639,"object_z_max":0.17097,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8365.0,"raw_peak_contact_force":1.86511,"subtask_id":"transport_arc","tcp_end":[0.61879,0.14696,0.26252],"tcp_start":[0.47147,-0.01928,0.16061],"tcp_to_object_dist_end":0.28321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":87.0,"n_steps_budget":1000.0,"object_pos_end":[0.53584,0.03486,0.01602],"object_pos_start":[0.53584,0.03486,0.01602],"object_to_goal_dist_end":0.23424,"object_to_goal_dist_start":0.23424,"object_z_max":0.01602,"peak_contact_force":9748.82189,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":721.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62428,0.1538,0.21756],"tcp_start":[0.61879,0.14696,0.26252],"tcp_to_object_dist_end":0.25017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53584,0.03486,0.01602],"object_pos_start":[0.53584,0.03486,0.01602],"object_to_goal_dist_end":0.23424,"object_to_goal_dist_start":0.23424,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61897,0.15233,0.23601],"tcp_start":[0.62428,0.1538,0.21756],"tcp_to_object_dist_end":0.26288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":660.0,"object_pos_end":[0.53584,0.03486,0.01602],"object_pos_start":[0.53584,0.03486,0.01602],"object_to_goal_dist_end":0.23424,"object_to_goal_dist_start":0.23424,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62831,0.15782,0.32045],"tcp_start":[0.61897,0.15233,0.23601],"tcp_to_object_dist_end":0.3411,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92694,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22605,"descend_1.grasp_z_offset":0.01091,"lift_1.lift_height":0.14113,"transport_arc.transport_arc_height":0.19266},"optimized_scores":{"best_composite_score":0.19601,"best_fitness_score":0.57601,"best_task_score":0.22944},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2481.0,"contact_point_centroid":[0.52176,0.04275,-0.00241],"force_p95":0.13051,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91879,"mean_force":0.14193,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55991,0.11812,0.26806]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.45646,-0.02469,-0.00143],"force_p95":0.32887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37061,"mean_force":0.07663,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44787,-0.0249,0.05036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6052.0,"contact_point_centroid":[0.45044,-0.04402,0.09768],"force_p95":0.08977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27265,"mean_force":0.05625,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44984,-0.02498,0.0969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5421.0,"contact_point_centroid":[0.45078,-0.00585,0.09833],"force_p95":0.09594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27023,"mean_force":0.06135,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4499,-0.02498,0.09774]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3476.0,"contact_point_centroid":[0.47639,-0.01757,0.17795],"force_p95":0.12884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24736,"mean_force":0.08167,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47087,0.00088,0.17796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2982.0,"contact_point_centroid":[0.47565,0.01827,0.17667],"force_p95":0.14108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23106,"mean_force":0.09099,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46989,-0.00042,0.1765]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02623,-0.00212],"force_p95":0.15535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21078,"mean_force":0.13121,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44988,-0.02498,0.04989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.44973,-0.00573,0.04948],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14899,"mean_force":0.05218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44886,-0.02494,0.0489]},{"body_a":"world","body_b":"grasp_target","contact_count":372.0,"contact_point_centroid":[0.45856,-0.02632,-0.00166],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12402,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48648,-0.0078,0.2847]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46331,-0.02108,0.16226]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.52172,0.04273,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62149,0.19969,0.22138]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52172,0.04273,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61969,0.20297,0.14121]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.52172,0.04273,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62097,0.20404,0.20237]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4978.0,"contact_point_centroid":[0.44892,-0.04404,0.04974],"force_p95":0.07154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07386,"mean_force":0.04403,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44886,-0.02494,0.04891]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2417.0,"contact_point_centroid":[0.56461,0.124,0.27367],"force_p95":0.01122,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56442,0.124,0.2714]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1122.0,"contact_point_centroid":[0.62183,0.19971,0.22361],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6215,0.1997,0.22115]}],"total_contact_groups":17},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.52172,0.04273,0.01602],"final_tcp_position":[0.62614,0.20649,0.24462],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.93776,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.026],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12214,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":372.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47149,-0.0171,0.26759],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.026],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.45651,-0.02519,0.05669],"tcp_start":[0.47149,-0.0171,0.26759],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02536,0.02558],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30307,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15219,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10873.0,"raw_peak_contact_force":0.21078,"subtask_id":"grasp_1","tcp_end":[0.44883,-0.02494,0.04887],"tcp_start":[0.45651,-0.02519,0.05669],"tcp_to_object_dist_end":0.02523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":303.0,"n_steps_budget":750.0,"object_pos_end":[0.46777,-0.02558,0.12213],"object_pos_start":[0.45851,-0.02536,0.02558],"object_to_goal_dist_end":0.28475,"object_to_goal_dist_start":0.30307,"object_z_max":0.12185,"peak_contact_force":0.59819,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11548.0,"raw_peak_contact_force":0.37061,"tcp_end":[0.45388,-0.02514,0.14745],"tcp_start":[0.44883,-0.02494,0.04887],"tcp_to_object_dist_end":0.02889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.52172,0.04273,0.01602],"object_pos_start":[0.46777,-0.02558,0.12213],"object_to_goal_dist_end":0.22081,"object_to_goal_dist_start":0.28475,"object_z_max":0.1771,"peak_contact_force":9748.93776,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11356.0,"raw_peak_contact_force":1.91879,"subtask_id":"transport_arc","tcp_end":[0.61917,0.19522,0.29667],"tcp_start":[0.45388,-0.02514,0.14745],"tcp_to_object_dist_end":0.33394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.52172,0.04273,0.01602],"object_pos_start":[0.52172,0.04273,0.01602],"object_to_goal_dist_end":0.22081,"object_to_goal_dist_start":0.22081,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2170.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62482,0.20476,0.14283],"tcp_start":[0.61917,0.19522,0.29667],"tcp_to_object_dist_end":0.23014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52172,0.04273,0.01602],"object_pos_start":[0.52172,0.04273,0.01602],"object_to_goal_dist_end":0.22081,"object_to_goal_dist_start":0.22081,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61798,0.2023,0.16063],"tcp_start":[0.62482,0.20476,0.14283],"tcp_to_object_dist_end":0.23588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":660.0,"object_pos_end":[0.52172,0.04273,0.01602],"object_pos_start":[0.52172,0.04273,0.01602],"object_to_goal_dist_end":0.22081,"object_to_goal_dist_start":0.22081,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62614,0.20649,0.24462],"tcp_start":[0.61798,0.2023,0.16063],"tcp_to_object_dist_end":0.29997,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```