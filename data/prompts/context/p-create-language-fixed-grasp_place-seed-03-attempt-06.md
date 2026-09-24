## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2541 | 0.39 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2890 | 0.28 | ❌ rejected |
| 4 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 1 | 0.4518 | 0.39 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3413 | 0.23 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2818 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b

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

## Current Skill (Q=0.254) — your mutation base

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
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_1
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: transport_arc
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.254
- **task_score** (E): 0.394
- **fitness_score**: 0.584  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2556 |
| descend_1 | 1.00 | 1.00 | 0.0043 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_1 | 1.00 | 1.00 | 0.1402 |
| transport_arc | 1.00 | 1.00 | 0.2149 |
| descend_place | 1.00 | 1.00 | 0.0463 |
| release_1 | 1.00 | 1.00 | 0.0211 |
| retract | 1.00 | 1.00 | 0.1302 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.049) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 18.271 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.049)→(0.504, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.504, 0.002, 0.045)→(0.496, 0.002, 0.036) | (0.511, 0.002, 0.026)→(0.511, 0.001, 0.025) | 0.246→0.246 | 1.00 / 38.000 | 0.162 | 0.226 |
| lift_1 | lift | 1.00 / step_budget | (0.496, 0.002, 0.036)→(0.506, 0.001, 0.176) | (0.511, 0.001, 0.025)→(0.522, 0.004, 0.096) | 0.246→0.232 | 1.00 / 17.333 | 0.118 | 0.826 |
| transport_arc | approach | 1.00 / step_budget | (0.490, 0.002, 0.153)→(0.604, 0.179, 0.116) | (0.507, 0.002, 0.136)→(0.603, 0.162, 0.010) | 0.224→0.112 | 1.00 / 6.000 | 0.217 | 1.228 |
| descend_place | descend | 1.00 / step_budget | (0.604, 0.179, 0.116)→(0.610, 0.190, 0.160) | (0.603, 0.162, 0.010)→(0.603, 0.163, 0.016) | 0.112→0.105 | 1.00 / 8.000 | 4874.509 | 0.206 |
| release_1 | release | 1.00 / step_budget | (0.610, 0.190, 0.160)→(0.604, 0.188, 0.181) | (0.603, 0.163, 0.016)→(0.603, 0.163, 0.016) | 0.105→0.105 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.604, 0.188, 0.181)→(0.602, 0.187, 0.311) | (0.603, 0.163, 0.016)→(0.603, 0.163, 0.016) | 0.105→0.105 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.520
- phase_score: 0.684
- phase_breakdown.release_1_score: 0.262
- phase_breakdown.descend_1_score: 0.903
- phase_breakdown.transport_arc_score: 0.674
- phase_breakdown.approach_1_score: 0.677
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.733

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.733
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.520
- **Median Q (composite search score)**: 0.375
- **K-run variance**: 0.0367
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.138


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `952d4e9e12c194d228cf63d10b31c959edc327920598c352d26dcf1284463776`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ab36b663de63a40a5839be0af4fc1d53d37f9e78d4183a3de7f11063534632b8`; realized-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64414,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.descend_offset":0.06477,"lift_1.lift_height":0.17256,"transport_arc.arc_height":0.43129},"optimized_scores":{"best_composite_score":0.40332,"best_fitness_score":0.73332,"best_task_score":0.51985},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.62931,0.20482,-0.00696],"force_p95":1.20856,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25573,"mean_force":0.56917,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.61498,0.1918,0.12506]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.45625,-0.02301,-0.00153],"force_p95":0.45178,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50036,"mean_force":0.10959,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44772,-0.02387,0.04072]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7771.0,"contact_point_centroid":[0.45075,-0.04305,0.1033],"force_p95":0.09951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29092,"mean_force":0.05909,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44949,-0.02402,0.10156]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.63163,0.20624,-0.00242],"force_p95":0.12588,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28996,"mean_force":0.1181,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61921,0.19961,0.13825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7531.0,"contact_point_centroid":[0.52527,0.08349,0.18605],"force_p95":0.13514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28972,"mean_force":0.0865,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51948,0.06517,0.18569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6634.0,"contact_point_centroid":[0.52238,0.04319,0.18674],"force_p95":0.15254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28637,"mean_force":0.09725,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51694,0.06176,0.18602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7307.0,"contact_point_centroid":[0.45073,-0.00494,0.10371],"force_p95":0.10308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27848,"mean_force":0.0614,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4495,-0.02402,0.10146]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45862,-0.0261,-0.00221],"force_p95":0.1799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24682,"mean_force":0.13795,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44988,-0.02393,0.0401]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4778.0,"contact_point_centroid":[0.44899,-0.0047,0.04098],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15138,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4488,-0.0239,0.03906]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.479,-0.01166,0.17559]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63164,0.20618,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6201,0.20323,0.16064]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.63164,0.20618,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61597,0.20159,0.24451]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45695,-0.02396,0.04721]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5099.0,"contact_point_centroid":[0.44898,-0.04324,0.04095],"force_p95":0.07676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08019,"mean_force":0.04427,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44881,-0.0239,0.03906]},{"body_a":"left_finger","body_b":"right_finger","contact_count":651.0,"contact_point_centroid":[0.62075,0.20093,0.14625],"force_p95":0.01353,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01841,"mean_force":0.01107,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62039,0.20091,0.14411]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62354,0.20435,0.15986],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62299,0.20433,0.15766]}],"total_contact_groups":16},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63164,0.20618,0.01602],"final_tcp_position":[0.61657,0.20173,0.31008],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.25573,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45866,-0.02385,0.04937],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.45607,-0.02411,0.04611],"tcp_start":[0.45866,-0.02385,0.04937],"tcp_to_object_dist_end":0.02037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02453,0.02526],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30252,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.17193,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11677.0,"raw_peak_contact_force":0.24682,"subtask_id":"grasp_1","tcp_end":[0.44877,-0.0239,0.03903],"tcp_start":[0.45607,-0.02411,0.04611],"tcp_to_object_dist_end":0.01688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":425.0,"n_steps_budget":990.0,"object_pos_end":[0.47067,-0.02467,0.16054],"object_pos_start":[0.45851,-0.02453,0.02526],"object_to_goal_dist_end":0.28604,"object_to_goal_dist_start":0.30252,"object_z_max":0.16026,"peak_contact_force":0.1059,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15156.0,"raw_peak_contact_force":0.50036,"tcp_end":[0.45433,-0.02432,0.17827],"tcp_start":[0.44877,-0.0239,0.03903],"tcp_to_object_dist_end":0.02412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":769.0,"n_steps_budget":1000.0,"object_pos_end":[0.63205,0.20337,0.00353],"object_pos_start":[0.47067,-0.02467,0.16054],"object_to_goal_dist_end":0.11071,"object_to_goal_dist_start":0.28604,"object_z_max":0.17339,"peak_contact_force":0.3122,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14257.0,"raw_peak_contact_force":1.25573,"subtask_id":"transport_arc","tcp_end":[0.61729,0.19495,0.12102],"tcp_start":[0.45433,-0.02432,0.17827],"tcp_to_object_dist_end":0.11871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.63164,0.20618,0.01602],"object_pos_start":[0.63205,0.20337,0.00353],"object_to_goal_dist_end":0.09813,"object_to_goal_dist_start":0.11071,"object_z_max":0.01652,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1507.0,"raw_peak_contact_force":0.28996,"tcp_end":[0.62415,0.20464,0.16028],"tcp_start":[0.61729,0.19495,0.12102],"tcp_to_object_dist_end":0.14447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63164,0.20618,0.01602],"object_pos_start":[0.63164,0.20618,0.01602],"object_to_goal_dist_end":0.09813,"object_to_goal_dist_start":0.09813,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61844,0.20258,0.17981],"tcp_start":[0.62415,0.20464,0.16028],"tcp_to_object_dist_end":0.16436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":524.0,"n_steps_budget":930.0,"object_pos_end":[0.63164,0.20618,0.01602],"object_pos_start":[0.63164,0.20618,0.01602],"object_to_goal_dist_end":0.09813,"object_to_goal_dist_start":0.09813,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61657,0.20173,0.31008],"tcp_start":[0.61844,0.20258,0.17981],"tcp_to_object_dist_end":0.29448,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55462,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.descend_offset":0.04694,"lift_1.lift_height":0.21575,"transport_arc.arc_height":0.37287},"optimized_scores":{"best_composite_score":-0.01634,"best_fitness_score":0.31366,"best_task_score":0.18987},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":670.0,"contact_point_centroid":[0.55008,0.00848,-0.00326],"force_p95":0.629,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54198,"mean_force":0.17725,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53625,0.00066,0.18114]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4621.0,"contact_point_centroid":[0.53311,-0.01783,0.09228],"force_p95":0.15162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37644,"mean_force":0.09386,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5276,0.00069,0.09114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4546.0,"contact_point_centroid":[0.53298,0.01925,0.09138],"force_p95":0.14979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35838,"mean_force":0.09559,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52754,0.00069,0.09024]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00101,-0.00204],"force_p95":0.13275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15601,"mean_force":0.12586,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52735,0.0008,0.03575]},{"body_a":"world","body_b":"grasp_target","contact_count":1952.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51703,0.00047,0.17474]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53455,0.00093,0.04536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3152.0,"contact_point_centroid":[0.52978,-0.01804,0.03788],"force_p95":0.09883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11619,"mean_force":0.0648,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52611,0.00078,0.03433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3430.0,"contact_point_centroid":[0.53005,0.01949,0.03711],"force_p95":0.09176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0921,"mean_force":0.0612,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52611,0.00078,0.03433]},{"body_a":"left_finger","body_b":"right_finger","contact_count":344.0,"contact_point_centroid":[0.53914,0.00064,0.21286],"force_p95":0.01439,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01586,"mean_force":0.01118,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53872,0.00064,0.21054]}],"total_contact_groups":9},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.5507,0.00959,0.016],"final_tcp_position":[0.53993,0.00064,0.22228],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":54.5679,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":54.5679,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53612,0.00096,0.04797],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.53433,0.00093,0.04395],"tcp_start":[0.53612,0.00096,0.04797],"tcp_to_object_dist_end":0.02052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54426,0.00069,0.02584],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12978,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8382.0,"raw_peak_contact_force":0.15601,"subtask_id":"grasp_1","tcp_end":[0.52608,0.00078,0.03429],"tcp_start":[0.53433,0.00093,0.04395],"tcp_to_object_dist_end":0.02005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":642.0,"n_steps_budget":1000.0,"object_pos_end":[0.5507,0.00959,0.016],"object_pos_start":[0.54426,0.00069,0.02584],"object_to_goal_dist_end":0.24921,"object_to_goal_dist_start":0.25053,"object_z_max":0.1342,"peak_contact_force":0.12298,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10181.0,"raw_peak_contact_force":1.54198,"tcp_end":[0.53993,0.00064,0.22228],"tcp_start":[0.52608,0.00078,0.03429],"tcp_to_object_dist_end":0.20675,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65957,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_place.descend_offset":0.07122,"lift_1.lift_height":0.12133,"transport_arc.arc_height":0.29231},"optimized_scores":{"best_composite_score":0.37529,"best_fitness_score":0.70529,"best_task_score":0.47245},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":615.0,"contact_point_centroid":[0.57412,0.11995,-0.00336],"force_p95":0.62813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19933,"mean_force":0.17825,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57736,0.13754,0.12418]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.52967,0.0266,-0.00155],"force_p95":0.36216,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43683,"mean_force":0.07637,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51288,0.02757,0.03694]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.52195,0.04604,0.07876],"force_p95":0.12177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34143,"mean_force":0.08414,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51725,0.0276,0.07707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3425.0,"contact_point_centroid":[0.52212,0.00884,0.07986],"force_p95":0.13504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32374,"mean_force":0.09412,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51729,0.0276,0.07744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2038.0,"contact_point_centroid":[0.54261,0.03745,0.13005],"force_p95":0.16456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2878,"mean_force":0.10206,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53663,0.05562,0.13216]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53068,0.03041,-0.00228],"force_p95":0.20055,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27502,"mean_force":0.14343,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51506,0.02772,0.0365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1887.0,"contact_point_centroid":[0.54372,0.07662,0.1298],"force_p95":0.16781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24187,"mean_force":0.11113,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53783,0.05828,0.13256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3833.0,"contact_point_centroid":[0.51607,0.00857,0.03835],"force_p95":0.10959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17002,"mean_force":0.05713,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51385,0.02765,0.03514]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5109,0.01362,0.17482]},{"body_a":"world","body_b":"grasp_target","contact_count":900.0,"contact_point_centroid":[0.57416,0.12007,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12269,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59145,0.16874,0.13413]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57416,0.12007,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59179,0.17368,0.16194]},{"body_a":"world","body_b":"grasp_target","contact_count":1972.0,"contact_point_centroid":[0.57416,0.12007,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58761,0.17225,0.24609]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52226,0.02792,0.0457]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4781.0,"contact_point_centroid":[0.51587,0.04677,0.03698],"force_p95":0.09033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09705,"mean_force":0.04839,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51386,0.02765,0.03515]},{"body_a":"left_finger","body_b":"right_finger","contact_count":306.0,"contact_point_centroid":[0.5849,0.15112,0.12035],"force_p95":0.01441,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01586,"mean_force":0.01113,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58427,0.15111,0.11809]},{"body_a":"left_finger","body_b":"right_finger","contact_count":952.0,"contact_point_centroid":[0.59185,0.16877,0.13645],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01053,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59145,0.16875,0.13417]}],"total_contact_groups":17},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57416,0.12007,0.01602],"final_tcp_position":[0.58813,0.17235,0.31175],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.89633,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52366,0.0278,0.04819],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.52191,0.02811,0.04434],"tcp_start":[0.52366,0.0278,0.04819],"tcp_to_object_dist_end":0.02041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53087,0.02812,0.02503],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18582,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18556,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10414.0,"raw_peak_contact_force":0.27502,"subtask_id":"grasp_1","tcp_end":[0.51382,0.02765,0.03511],"tcp_start":[0.52191,0.02811,0.04434],"tcp_to_object_dist_end":0.01981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":318.0,"n_steps_budget":720.0,"object_pos_end":[0.54327,0.02822,0.11055],"object_pos_start":[0.53087,0.02812,0.02503],"object_to_goal_dist_end":0.16127,"object_to_goal_dist_start":0.18582,"object_z_max":0.11031,"peak_contact_force":0.12431,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7617.0,"raw_peak_contact_force":0.43683,"tcp_end":[0.52481,0.0278,0.12731],"tcp_start":[0.51382,0.02765,0.03511],"tcp_to_object_dist_end":0.02493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.57416,0.12007,0.01601],"object_pos_start":[0.54327,0.02822,0.11055],"object_to_goal_dist_end":0.11248,"object_to_goal_dist_start":0.16127,"object_z_max":0.11239,"peak_contact_force":0.12271,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4846.0,"raw_peak_contact_force":1.19933,"subtask_id":"transport_arc","tcp_end":[0.59004,0.16257,0.11086],"tcp_start":[0.52481,0.0278,0.12731],"tcp_to_object_dist_end":0.10515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.57416,0.12007,0.01602],"object_pos_start":[0.57416,0.12007,0.01601],"object_to_goal_dist_end":0.11247,"object_to_goal_dist_start":0.11248,"object_z_max":0.01602,"peak_contact_force":9748.89633,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.12269,"tcp_end":[0.59581,0.17488,0.16057],"tcp_start":[0.59004,0.16257,0.11086],"tcp_to_object_dist_end":0.15611,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57416,0.12007,0.01602],"object_pos_start":[0.57416,0.12007,0.01602],"object_to_goal_dist_end":0.11247,"object_to_goal_dist_start":0.11247,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59013,0.17311,0.18158],"tcp_start":[0.59581,0.17488,0.16057],"tcp_to_object_dist_end":0.17458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":960.0,"object_pos_end":[0.57416,0.12007,0.01602],"object_pos_start":[0.57416,0.12007,0.01602],"object_to_goal_dist_end":0.11247,"object_to_goal_dist_start":0.11247,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1972.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58813,0.17235,0.31175],"tcp_start":[0.59013,0.17311,0.18158],"tcp_to_object_dist_end":0.30064,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```