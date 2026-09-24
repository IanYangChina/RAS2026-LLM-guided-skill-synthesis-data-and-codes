## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1952 | 0.76 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3928 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3147 | 0.94 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3802 | 0.95 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4008 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.195) — your mutation base

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
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
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
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
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
    anchor: current_tcp
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_object
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_object** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.195
- **task_score** (E): 0.765
- **fitness_score**: 0.765  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1459 |
| descend_1 | 1.00 | 1.00 | 0.1103 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1308 |
| transport_to_goal | 1.00 | 1.00 | 0.2366 |
| place_object | 1.00 | 1.00 | 0.1086 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.001, 0.160) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.001, 0.160)→(0.506, 0.001, 0.050) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.001, 0.050)→(0.498, 0.001, 0.041) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 31.667 | 0.130 | 0.157 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.001, 0.041)→(0.494, 0.001, 0.172) | (0.511, 0.002, 0.026)→(0.508, 0.002, 0.115) | 0.246→0.224 | 1.00 / 27.333 | 3249.744 | 0.457 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.001, 0.172)→(0.618, 0.172, 0.273) | (0.508, 0.002, 0.115)→(0.602, 0.126, 0.190) | 0.224→0.141 | 1.00 / 29.000 | 0.091 | 0.105 |
| place_object | descend | 1.00 / step_budget | (0.618, 0.172, 0.273)→(0.621, 0.178, 0.165) | (0.602, 0.126, 0.190)→(0.603, 0.130, 0.114) | 0.141→0.070 | 1.00 / 26.333 | 0.093 | 0.150 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.026
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.339
- phase_breakdown.approach_1_score: 0.073
- phase_breakdown.release_1_score: 0.481
- phase_breakdown.descend_1_score: 0.783
- phase_breakdown.transport_arc_score: 0.064
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.407
- **K-run variance**: 0.0909
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.316


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20312,"average_solve_count":320.0,"average_success_count":320.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11155,"approach_1.approach_speed":0.07579,"descend_1.descend_speed":0.03989,"descend_1.grasp_z_offset":0.01,"lift_1.lift_height":0.14786,"lift_1.lift_speed":0.048,"place_object.place_speed":0.06016,"place_object.place_z_offset":0.01725,"transport_to_goal.transport_speed":0.06062},"optimized_scores":{"best_composite_score":0.40942,"best_fitness_score":0.97942,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45525,-0.02544,-0.00141],"force_p95":0.54837,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58317,"mean_force":0.16878,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44584,-0.02562,0.03255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8595.0,"contact_point_centroid":[0.44319,-0.0063,0.0936],"force_p95":0.07351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27717,"mean_force":0.05087,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44355,-0.02551,0.09162]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9023.0,"contact_point_centroid":[0.4431,-0.04468,0.09539],"force_p95":0.07192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27702,"mean_force":0.04914,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44354,-0.02551,0.09384]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02618,-0.00205],"force_p95":0.13959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19105,"mean_force":0.12719,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44799,-0.02569,0.0325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3054.0,"contact_point_centroid":[0.6233,0.2197,0.20321],"force_p95":0.08713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16029,"mean_force":0.06176,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62139,0.20067,0.20267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3002.0,"contact_point_centroid":[0.62307,0.18158,0.20672],"force_p95":0.09237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15364,"mean_force":0.06075,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62129,0.20052,0.20528]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.45856,-0.02632,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48105,-0.01062,0.23195]},{"body_a":"world","body_b":"grasp_target","contact_count":3028.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45635,-0.02404,0.09666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4823.0,"contact_point_centroid":[0.44689,-0.00641,0.03376],"force_p95":0.06809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0984,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.02565,0.03147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21605.0,"contact_point_centroid":[0.53263,0.07028,0.20642],"force_p95":0.06817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09395,"mean_force":0.04574,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53275,0.08934,0.20509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18486.0,"contact_point_centroid":[0.53616,0.11236,0.20871],"force_p95":0.07761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08707,"mean_force":0.05231,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5358,0.09314,0.2067]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5410.0,"contact_point_centroid":[0.44637,-0.04489,0.03319],"force_p95":0.06509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07851,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44691,-0.02565,0.03147]}],"total_contact_groups":12},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63237,0.20421,0.13304],"final_tcp_position":[0.6243,0.20446,0.15005],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.58317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46175,-0.0222,0.16063],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4543,-0.02592,0.03853],"tcp_start":[0.46175,-0.0222,0.16063],"tcp_to_object_dist_end":0.01322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.0257,0.0258],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3033,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1369,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12033.0,"raw_peak_contact_force":0.19105,"subtask_id":"grasp_1","tcp_end":[0.44688,-0.02565,0.03145],"tcp_start":[0.4543,-0.02592,0.03853],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.45416,-0.02532,0.15122],"object_pos_start":[0.45845,-0.0257,0.0258],"object_to_goal_dist_end":0.29475,"object_to_goal_dist_start":0.3033,"object_z_max":0.15093,"peak_contact_force":0.08108,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17698.0,"raw_peak_contact_force":0.58317,"tcp_end":[0.44353,-0.02549,0.15971],"tcp_start":[0.44688,-0.02565,0.03145],"tcp_to_object_dist_end":0.01361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":986.0,"n_steps_budget":1000.0,"object_pos_end":[0.62736,0.19765,0.23557],"object_pos_start":[0.45416,-0.02532,0.15122],"object_to_goal_dist_end":0.12194,"object_to_goal_dist_start":0.29475,"object_z_max":0.2355,"peak_contact_force":0.06739,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40091.0,"raw_peak_contact_force":0.09395,"subtask_id":"transport_arc","tcp_end":[0.6198,0.19755,0.25093],"tcp_start":[0.44353,-0.02549,0.15971],"tcp_to_object_dist_end":0.01712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.63237,0.20421,0.13304],"object_pos_start":[0.62736,0.19765,0.23557],"object_to_goal_dist_end":0.01947,"object_to_goal_dist_start":0.12194,"object_z_max":0.23557,"peak_contact_force":0.08635,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6056.0,"raw_peak_contact_force":0.16029,"subtask_id":"release_1","tcp_end":[0.6243,0.20446,0.15005],"tcp_start":[0.6198,0.19755,0.25093],"tcp_to_object_dist_end":0.01883,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20414,"average_solve_count":338.0,"average_success_count":338.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05046,"approach_1.approach_speed":0.07502,"descend_1.descend_speed":0.0499,"descend_1.grasp_z_offset":0.01593,"lift_1.lift_height":0.16643,"lift_1.lift_speed":0.03803,"place_object.place_speed":0.06842,"place_object.place_z_offset":-0.01042,"transport_to_goal.transport_speed":0.03005},"optimized_scores":{"best_composite_score":0.40732,"best_fitness_score":0.97732,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.53991,0.00054,-0.00145],"force_p95":0.52152,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55858,"mean_force":0.21227,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52919,0.00085,0.03032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10275.0,"contact_point_centroid":[0.52683,-0.01832,0.10262],"force_p95":0.07831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28269,"mean_force":0.05484,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52647,0.00081,0.10012]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10692.0,"contact_point_centroid":[0.52675,0.0199,0.10076],"force_p95":0.07724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27021,"mean_force":0.05325,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52646,0.00081,0.09855]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4346.0,"contact_point_centroid":[0.64208,0.17188,0.26369],"force_p95":0.08217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16781,"mean_force":0.05389,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64159,0.15278,0.26265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4380.0,"contact_point_centroid":[0.64211,0.1336,0.26525],"force_p95":0.08178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1618,"mean_force":0.05352,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64156,0.15272,0.2641]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13191,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15614,"mean_force":0.12535,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53163,0.0009,0.03088]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51651,0.00046,0.20017]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53582,0.00097,0.0608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.5312,-0.01832,0.03214],"force_p95":0.07612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11524,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53038,0.00088,0.02943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19806.0,"contact_point_centroid":[0.58333,0.05814,0.25067],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09802,"mean_force":0.04623,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58326,0.07723,0.24956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53117,0.01996,0.03126],"force_p95":0.06813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09525,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53038,0.00088,0.02943]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17890.0,"contact_point_centroid":[0.58535,0.09866,0.25319],"force_p95":0.07496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09215,"mean_force":0.05053,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58497,0.07946,0.25181]}],"total_contact_groups":12},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64509,0.15527,0.18356],"final_tcp_position":[0.64337,0.15565,0.19992],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.55858,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53565,0.00095,0.09828],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53876,0.00103,0.0392],"tcp_start":[0.53565,0.00095,0.09828],"tcp_to_object_dist_end":0.0143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00075,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12997,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15614,"subtask_id":"grasp_1","tcp_end":[0.53035,0.00088,0.0294],"tcp_start":[0.53876,0.00103,0.0392],"tcp_to_object_dist_end":0.01426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.53803,0.00084,0.16816],"object_pos_start":[0.54417,0.00075,0.02588],"object_to_goal_dist_end":0.19303,"object_to_goal_dist_start":0.25051,"object_z_max":0.1679,"peak_contact_force":0.08136,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21060.0,"raw_peak_contact_force":0.55858,"tcp_end":[0.52672,0.00082,0.17616],"tcp_start":[0.53035,0.00088,0.0294],"tcp_to_object_dist_end":0.01386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":915.0,"n_steps_budget":1000.0,"object_pos_end":[0.64825,0.15033,0.30964],"object_pos_start":[0.53803,0.00084,0.16816],"object_to_goal_dist_end":0.11879,"object_to_goal_dist_start":0.19303,"object_z_max":0.30951,"peak_contact_force":0.08443,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37696.0,"raw_peak_contact_force":0.09802,"subtask_id":"transport_arc","tcp_end":[0.64044,0.1502,0.32428],"tcp_start":[0.52672,0.00082,0.17616],"tcp_to_object_dist_end":0.01659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.64509,0.15527,0.18356],"object_pos_start":[0.64825,0.15033,0.30964],"object_to_goal_dist_end":0.00844,"object_to_goal_dist_start":0.11879,"object_z_max":0.30965,"peak_contact_force":0.0705,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8726.0,"raw_peak_contact_force":0.16781,"subtask_id":"release_1","tcp_end":[0.64337,0.15565,0.19992],"tcp_start":[0.64044,0.1502,0.32428],"tcp_to_object_dist_end":0.01645,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96417,"average_solve_count":307.0,"average_success_count":307.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1765,"approach_1.approach_speed":0.04184,"descend_1.descend_speed":0.0377,"descend_1.grasp_z_offset":0.02294,"lift_1.lift_height":0.13657,"lift_1.lift_speed":0.04759,"place_object.place_speed":0.05649,"place_object.place_z_offset":0.01792,"transport_to_goal.transport_speed":0.05261},"optimized_scores":{"best_composite_score":-0.23126,"best_fitness_score":0.33874,"best_task_score":0.29444},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.53042,0.03079,-0.00199],"force_p95":0.13888,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23025,"mean_force":0.12294,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51281,0.02853,0.12072]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.5305,0.03079,-0.00182],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1233,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50923,0.01101,0.26254]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5214,0.02679,0.13486]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51753,0.02884,0.06477]},{"body_a":"world","body_b":"grasp_target","contact_count":2372.0,"contact_point_centroid":[0.5304,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55232,0.09943,0.21121]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.5304,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59358,0.17058,0.19679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14.0,"contact_point_centroid":[0.52392,0.03256,0.05598],"force_p95":0.1049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10497,"mean_force":0.067,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51616,0.02875,0.06324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10.0,"contact_point_centroid":[0.52394,0.02595,0.05599],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07664,"mean_force":0.05642,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51617,0.02875,0.06324]},{"body_a":"left_finger","body_b":"right_finger","contact_count":331.0,"contact_point_centroid":[0.51664,0.02877,0.06545],"force_p95":0.01431,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01141,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51634,0.02876,0.06334]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1776.0,"contact_point_centroid":[0.51311,0.02854,0.12306],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51281,0.02853,0.1208]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2539.0,"contact_point_centroid":[0.55313,0.1001,0.21385],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01042,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55271,0.10009,0.21153]},{"body_a":"left_finger","body_b":"right_finger","contact_count":800.0,"contact_point_centroid":[0.59402,0.17061,0.19895],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01042,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59358,0.17058,0.19666]}],"total_contact_groups":12},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5304,0.03079,0.02602],"final_tcp_position":[0.596,0.17481,0.14483],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9749.06941,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":724.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52084,0.02363,0.22199],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5241,0.02926,0.0727],"tcp_start":[0.52084,0.02363,0.22199],"tcp_to_object_dist_end":0.04714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2131.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.51634,0.02876,0.06334],"tcp_start":[0.5241,0.02926,0.0727],"tcp_to_object_dist_end":0.03997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.5304,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1834,"object_to_goal_dist_start":0.18336,"object_z_max":0.02603,"peak_contact_force":9749.06941,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3480.0,"raw_peak_contact_force":0.23025,"tcp_end":[0.51286,0.02853,0.18049],"tcp_start":[0.51634,0.02876,0.06334],"tcp_to_object_dist_end":0.15548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.5304,0.03079,0.02602],"object_pos_start":[0.5304,0.03079,0.02602],"object_to_goal_dist_end":0.1834,"object_to_goal_dist_start":0.1834,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4911.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.59248,0.16698,0.24455],"tcp_start":[0.51286,0.02853,0.18049],"tcp_to_object_dist_end":0.26487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.5304,0.03079,0.02602],"object_pos_start":[0.5304,0.03079,0.02602],"object_to_goal_dist_end":0.1834,"object_to_goal_dist_start":0.1834,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1548.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.596,0.17481,0.14483],"tcp_start":[0.59248,0.16698,0.24455],"tcp_to_object_dist_end":0.19789,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```