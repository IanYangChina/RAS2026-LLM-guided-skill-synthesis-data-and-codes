## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2603 | 0.18 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1952 | 0.76 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3928 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3147 | 0.94 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3802 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.260) — your mutation base

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

- **Composite score**: -0.260
- **task_score** (E): 0.184
- **fitness_score**: 0.193  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.2060 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| grasp_1 | 1.00 | 1.00 | 0.0007 |
| lift_1 | 1.00 | 1.00 | 0.1271 |
| transport_to_goal | 0.00 | 1.00 | 0.1622 |
| place_object | 0.00 | 1.00 | 0.0012 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.391, -0.003, 0.126) | (0.511, 0.002, 0.030)→(0.474, 0.009, 0.016) | 0.244→0.264 | 1.00 / 5.000 | 196.862 | 1314.699 |
| descend_1 | descend | 1.00 / force_exceeded | (0.391, -0.003, 0.126)→(0.391, -0.003, 0.127) | (0.474, 0.009, 0.016)→(0.474, 0.009, 0.016) | 0.264→0.264 | 1.00 / 5.000 | 634.833 | 326.735 |
| grasp_1 | grasp | 1.00 / step_budget | (0.391, -0.003, 0.127)→(0.391, -0.003, 0.126) | (0.474, 0.009, 0.016)→(0.474, 0.009, 0.016) | 0.264→0.264 | 1.00 / 9.000 | 68.072 | 139.541 |
| lift_1 | lift | 1.00 / step_budget | (0.391, -0.003, 0.126)→(0.390, -0.004, 0.253) | (0.474, 0.009, 0.016)→(0.474, 0.009, 0.016) | 0.264→0.264 | 1.00 / 8.333 | 91001.973 | 91.033 |
| transport_to_goal | approach | 0.00 / step_budget | (0.390, -0.004, 0.253)→(0.505, 0.103, 0.252) | (0.474, 0.009, 0.016)→(0.474, 0.009, 0.016) | 0.264→0.264 | 1.00 / 9.333 | 269.586 | 413.335 |
| place_object | descend | 0.00 / step_budget | (0.505, 0.103, 0.252)→(0.505, 0.104, 0.252) | (0.474, 0.009, 0.016)→(0.474, 0.009, 0.016) | 0.264→0.264 | 1.00 / 9.000 | 254.129 | 277.157 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.279
- phase_score: 0.169
- phase_breakdown.approach_1_score: 0.032
- phase_breakdown.release_1_score: 0.019
- phase_breakdown.descend_1_score: 0.040
- phase_breakdown.transport_arc_score: 0.019
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.225

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.225
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.279
- **Median Q (composite search score)**: -0.267
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.377


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":91.0,"average_failure_rate":0.49457,"average_mean_iterations":101.72283,"average_solve_count":184.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22119,"approach_1.approach_speed":0.07557,"descend_1.descend_speed":0.03818,"descend_1.force_threshold":10.42204,"descend_1.grasp_z_offset":0.02851,"lift_1.lift_height":0.08228,"lift_1.lift_speed":0.05829,"place_object.place_speed":0.08786,"place_object.place_z_offset":-0.03837,"transport_to_goal.transport_speed":0.09011},"optimized_scores":{"best_composite_score":-0.26657,"best_fitness_score":0.18676,"best_task_score":0.11042},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":733.0,"contact_point_centroid":[0.62074,-0.01426,-0.00051],"force_p95":212.38609,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1381.70123,"mean_force":213.5966,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36925,-0.01209,0.09686]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62068,-0.01829,-0.00027],"force_p95":566.32713,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":566.32713,"mean_force":566.32713,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.36601,-0.0179,0.09811]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.61381,-0.02354,-0.00013],"force_p95":83.73299,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.11002,"mean_force":72.69711,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.36666,-0.01796,0.09789]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.61308,-0.02425,-0.0001],"force_p95":84.42725,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.25942,"mean_force":59.1767,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.3668,-0.018,0.0977]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43827,-0.01837,0.04192],"force_p95":3.4748,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.8545,"mean_force":1.61735,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37268,-0.00795,0.05227]},{"body_a":"world","body_b":"grasp_target","contact_count":3312.0,"contact_point_centroid":[0.42336,-0.02517,-0.00215],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29426,"mean_force":0.14069,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38537,-0.01126,0.11101]},{"body_a":"grasp_target","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.46784,-0.01206,0.00991],"force_p95":0.45067,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48607,"mean_force":0.18085,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36164,-0.00795,0.05116]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41743,-0.02497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.36601,-0.0179,0.09811]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.41743,-0.02497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.36666,-0.01796,0.09789]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41743,-0.02497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.3647,-0.01803,0.12792]},{"body_a":"world","body_b":"grasp_target","contact_count":1880.0,"contact_point_centroid":[0.41743,-0.02497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.42603,0.03753,0.17911]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.41743,-0.02497,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.48182,0.10277,0.19377]},{"body_a":"left_finger","body_b":"right_finger","contact_count":329.0,"contact_point_centroid":[0.36901,-0.018,0.09729],"force_p95":0.01423,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01517,"mean_force":0.01147,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.36681,-0.018,0.09767]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1986.0,"contact_point_centroid":[0.42849,0.03787,0.1786],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.42638,0.03788,0.17921]},{"body_a":"left_finger","body_b":"right_finger","contact_count":837.0,"contact_point_centroid":[0.36687,-0.01803,0.12742],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01063,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.3647,-0.01803,0.12799]},{"body_a":"left_finger","body_b":"right_finger","contact_count":9.0,"contact_point_centroid":[0.485,0.10286,0.19388],"force_p95":0.01076,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01076,"mean_force":0.01003,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.48182,0.10277,0.19377]}],"total_contact_groups":17},"final_pose_error":0.21692,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41743,-0.02497,0.01602],"final_tcp_position":[0.48197,0.10267,0.19391],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1381.70123,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.41743,-0.02497,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33051,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":212.28107,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4124.0,"raw_peak_contact_force":1381.70123,"subtask_id":"approach_1","tcp_end":[0.36601,-0.0179,0.09811],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09713,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41743,-0.02497,0.01602],"object_pos_start":[0.41743,-0.02497,0.01602],"object_to_goal_dist_end":0.33051,"object_to_goal_dist_start":0.33051,"object_z_max":0.01602,"peak_contact_force":820.33443,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":566.32713,"subtask_id":"descend_1","tcp_end":[0.36614,-0.01789,0.09834],"tcp_start":[0.36601,-0.0179,0.09811],"tcp_to_object_dist_end":0.09725,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41743,-0.02497,0.01602],"object_pos_start":[0.41743,-0.02497,0.01602],"object_to_goal_dist_end":0.33051,"object_to_goal_dist_start":0.33051,"object_z_max":0.01602,"peak_contact_force":67.41565,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2579.0,"raw_peak_contact_force":118.11002,"subtask_id":"grasp_1","tcp_end":[0.36682,-0.018,0.09766],"tcp_start":[0.36614,-0.01789,0.09834],"tcp_to_object_dist_end":0.09631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":200.0,"n_steps_budget":900.0,"object_pos_end":[0.41743,-0.02497,0.01602],"object_pos_start":[0.41743,-0.02497,0.01602],"object_to_goal_dist_end":0.33051,"object_to_goal_dist_start":0.33051,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1643.0,"raw_peak_contact_force":92.25942,"tcp_end":[0.36432,-0.01804,0.16036],"tcp_start":[0.36682,-0.018,0.09766],"tcp_to_object_dist_end":0.15396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.41743,-0.02497,0.01602],"object_pos_start":[0.41743,-0.02497,0.01602],"object_to_goal_dist_end":0.33051,"object_to_goal_dist_start":0.33051,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3866.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.48179,0.1028,0.19373],"tcp_start":[0.36432,-0.01804,0.16036],"tcp_to_object_dist_end":0.22814,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.41743,-0.02497,0.01602],"object_pos_start":[0.41743,-0.02497,0.01602],"object_to_goal_dist_end":0.33051,"object_to_goal_dist_start":0.33051,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.48197,0.10267,0.19391],"tcp_start":[0.48179,0.1028,0.19373],"tcp_to_object_dist_end":0.22826,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":97.0,"average_failure_rate":0.40756,"average_mean_iterations":84.59244,"average_solve_count":238.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19788,"approach_1.approach_speed":0.02095,"descend_1.descend_speed":0.03137,"descend_1.force_threshold":4.40812,"descend_1.grasp_z_offset":0.01831,"lift_1.lift_height":0.14319,"lift_1.lift_speed":0.06476,"place_object.place_speed":0.06237,"place_object.place_z_offset":0.04371,"transport_to_goal.transport_speed":0.05669},"optimized_scores":{"best_composite_score":-0.28597,"best_fitness_score":0.16736,"best_task_score":0.16378},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53958,0.00432,-0.00314],"force_p95":465.38462,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1205.09356,"mean_force":77.04419,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38546,0.0,0.04926]},{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.64519,0.00028,-0.00046],"force_p95":194.57549,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1169.59187,"mean_force":196.01967,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.402,0.00022,0.11908]},{"body_a":"link5","body_b":"hand","contact_count":96.0,"contact_point_centroid":[0.54852,0.00709,0.26085],"force_p95":511.14059,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":545.47366,"mean_force":362.10814,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51554,0.0814,0.28813]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.54513,0.02051,0.23772],"force_p95":321.29114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.16453,"mean_force":291.64394,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.52449,0.08939,0.29009]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64019,0.00051,-0.00025],"force_p95":196.91907,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.91907,"mean_force":196.91907,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.40902,0.00034,0.14494]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.64072,0.00046,-0.00014],"force_p95":94.52394,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.71774,"mean_force":74.28823,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40934,0.00028,0.14482]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.64093,0.00042,-9e-05],"force_p95":89.52859,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.87292,"mean_force":75.14693,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.40941,0.00025,0.1447]},{"body_a":"grasp_target","body_b":"link7","contact_count":719.0,"contact_point_centroid":[0.53342,0.00437,0.03139],"force_p95":0.85422,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.62602,"mean_force":0.28153,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40087,0.0002,0.11235]},{"body_a":"grasp_target","body_b":"link6","contact_count":102.0,"contact_point_centroid":[0.54701,0.01544,0.02506],"force_p95":0.80599,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.59025,"mean_force":0.43572,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39147,8e-05,0.08116]},{"body_a":"grasp_target","body_b":"hand","contact_count":99.0,"contact_point_centroid":[0.49924,0.01056,0.04264],"force_p95":2.42166,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.94475,"mean_force":0.95703,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39347,7e-05,0.07474]},{"body_a":"world","body_b":"grasp_target","contact_count":3786.0,"contact_point_centroid":[0.51248,0.00572,-0.00257],"force_p95":0.32496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.61289,"mean_force":0.17289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4143,0.00024,0.13077]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50604,0.0066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.40902,0.00034,0.14494]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50604,0.0066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40934,0.00028,0.14482]},{"body_a":"world","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.50604,0.0066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.40777,0.00016,0.20511]},{"body_a":"world","body_b":"grasp_target","contact_count":3296.0,"contact_point_centroid":[0.50604,0.0066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48133,0.05412,0.27301]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50604,0.0066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.52449,0.08939,0.29009]}],"total_contact_groups":20},"final_pose_error":0.15127,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50604,0.0066,0.01602],"final_tcp_position":[0.52494,0.08931,0.2905],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1205.09356,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.0066,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27138,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":187.86177,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5613.0,"raw_peak_contact_force":1205.09356,"subtask_id":"approach_1","tcp_end":[0.40902,0.00034,0.14494],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16147,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.0066,0.01602],"object_pos_start":[0.50604,0.0066,0.01602],"object_to_goal_dist_end":0.27138,"object_to_goal_dist_start":0.27138,"object_z_max":0.01602,"peak_contact_force":582.81175,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":196.91907,"subtask_id":"descend_1","tcp_end":[0.40902,0.00034,0.14497],"tcp_start":[0.40902,0.00034,0.14494],"tcp_to_object_dist_end":0.1615,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50604,0.0066,0.01602],"object_pos_start":[0.50604,0.0066,0.01602],"object_to_goal_dist_end":0.27138,"object_to_goal_dist_start":0.27138,"object_z_max":0.01602,"peak_contact_force":68.55204,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2581.0,"raw_peak_contact_force":145.71774,"subtask_id":"grasp_1","tcp_end":[0.40942,0.00025,0.14465],"tcp_start":[0.40902,0.00034,0.14497],"tcp_to_object_dist_end":0.161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.0066,0.01602],"object_pos_start":[0.50604,0.0066,0.01602],"object_to_goal_dist_end":0.27138,"object_to_goal_dist_start":0.27138,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3228.0,"raw_peak_contact_force":89.87292,"tcp_end":[0.40813,0.00016,0.26795],"tcp_start":[0.40942,0.00025,0.14465],"tcp_to_object_dist_end":0.27036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.0066,0.01602],"object_pos_start":[0.50604,0.0066,0.01602],"object_to_goal_dist_end":0.27138,"object_to_goal_dist_start":0.27138,"object_z_max":0.01602,"peak_contact_force":306.39647,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6924.0,"raw_peak_contact_force":545.47366,"subtask_id":"transport_arc","tcp_end":[0.52426,0.08943,0.28985],"tcp_start":[0.40813,0.00016,0.26795],"tcp_to_object_dist_end":0.28666,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.0066,0.01602],"object_pos_start":[0.50604,0.0066,0.01602],"object_to_goal_dist_end":0.27138,"object_to_goal_dist_start":0.27138,"object_z_max":0.01602,"peak_contact_force":287.91859,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":29.0,"raw_peak_contact_force":323.16453,"subtask_id":"release_1","tcp_end":[0.52494,0.08931,0.2905],"tcp_start":[0.52426,0.08943,0.28985],"tcp_to_object_dist_end":0.2873,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":112.0,"average_failure_rate":0.41948,"average_mean_iterations":86.9176,"average_solve_count":267.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1897,"approach_1.approach_speed":0.01296,"descend_1.descend_speed":0.01159,"descend_1.force_threshold":8.72012,"descend_1.grasp_z_offset":0.01586,"lift_1.lift_height":0.21489,"lift_1.lift_speed":0.06191,"place_object.place_speed":0.05004,"place_object.place_z_offset":-0.03418,"transport_to_goal.transport_speed":0.08402},"optimized_scores":{"best_composite_score":-0.22849,"best_fitness_score":0.22484,"best_task_score":0.27878},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63829,0.00559,-0.00046],"force_p95":195.07355,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1357.30231,"mean_force":199.56182,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39312,0.00549,0.1154]},{"body_a":"link5","body_b":"hand","contact_count":22.0,"contact_point_centroid":[0.54806,0.03652,0.26639],"force_p95":676.08248,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":694.40997,"mean_force":566.05961,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50605,0.11671,0.27291]},{"body_a":"link5","body_b":"hand","contact_count":7.0,"contact_point_centroid":[0.54588,0.03583,0.25705],"force_p95":507.67241,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":508.18391,"mean_force":490.31507,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.50843,0.11799,0.27301]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63378,0.00714,-0.00025],"force_p95":216.958,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.958,"mean_force":216.958,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39737,0.0075,0.13626]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.63434,0.00708,-0.00014],"force_p95":94.87707,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.79457,"mean_force":74.36627,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.3977,0.00743,0.13608]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.63456,0.00704,-9e-05],"force_p95":88.07494,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.96704,"mean_force":68.92148,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.39779,0.0074,0.13594]},{"body_a":"grasp_target","body_b":"link7","contact_count":600.0,"contact_point_centroid":[0.51452,0.01727,0.03322],"force_p95":0.7709,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.89722,"mean_force":0.24817,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39204,0.00486,0.10681]},{"body_a":"grasp_target","body_b":"hand","contact_count":148.0,"contact_point_centroid":[0.4968,0.0419,0.05295],"force_p95":2.11499,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.94972,"mean_force":0.75679,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38766,0.00404,0.08415]},{"body_a":"world","body_b":"grasp_target","contact_count":3569.0,"contact_point_centroid":[0.50424,0.04322,-0.00244],"force_p95":0.44669,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25191,"mean_force":0.17047,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40687,0.00533,0.12868]},{"body_a":"grasp_target","body_b":"link6","contact_count":113.0,"contact_point_centroid":[0.53918,0.03558,0.02658],"force_p95":0.79359,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.84223,"mean_force":0.41699,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38512,0.00401,0.08476]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49811,0.04615,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39737,0.0075,0.13626]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.49811,0.04615,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.3977,0.00743,0.13608]},{"body_a":"world","body_b":"grasp_target","contact_count":2480.0,"contact_point_centroid":[0.49811,0.04615,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.39631,0.0073,0.23234]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.49811,0.04615,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.45541,0.05809,0.30177]},{"body_a":"world","body_b":"grasp_target","contact_count":28.0,"contact_point_centroid":[0.49811,0.04615,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.50843,0.11799,0.27301]},{"body_a":"left_finger","body_b":"right_finger","contact_count":323.0,"contact_point_centroid":[0.39979,0.0074,0.13485],"force_p95":0.01382,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01776,"mean_force":0.01163,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.3978,0.00741,0.1359]}],"total_contact_groups":20},"final_pose_error":0.22625,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49811,0.04615,0.01602],"final_tcp_position":[0.50872,0.11867,0.27135],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273005.6728,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49811,0.04615,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.1916,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":190.44214,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5338.0,"raw_peak_contact_force":1357.30231,"subtask_id":"approach_1","tcp_end":[0.39737,0.0075,0.13626],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16155,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49811,0.04615,0.01602],"object_pos_start":[0.49811,0.04615,0.01602],"object_to_goal_dist_end":0.1916,"object_to_goal_dist_start":0.1916,"object_z_max":0.01602,"peak_contact_force":501.35163,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":216.958,"subtask_id":"descend_1","tcp_end":[0.39736,0.00748,0.13628],"tcp_start":[0.39737,0.0075,0.13626],"tcp_to_object_dist_end":0.16158,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49811,0.04615,0.01602],"object_pos_start":[0.49811,0.04615,0.01602],"object_to_goal_dist_end":0.1916,"object_to_goal_dist_start":0.1916,"object_z_max":0.01602,"peak_contact_force":68.24945,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2573.0,"raw_peak_contact_force":154.79457,"subtask_id":"grasp_1","tcp_end":[0.39781,0.0074,0.13589],"tcp_start":[0.39736,0.00748,0.13628],"tcp_to_object_dist_end":0.16103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":620.0,"n_steps_budget":1000.0,"object_pos_end":[0.49811,0.04615,0.01602],"object_pos_start":[0.49811,0.04615,0.01602],"object_to_goal_dist_end":0.1916,"object_to_goal_dist_start":0.1916,"object_z_max":0.01602,"peak_contact_force":273005.6728,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5089.0,"raw_peak_contact_force":90.96704,"tcp_end":[0.3972,0.00733,0.33103],"tcp_start":[0.39781,0.0074,0.13589],"tcp_to_object_dist_end":0.33305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.49811,0.04615,0.01602],"object_pos_start":[0.49811,0.04615,0.01602],"object_to_goal_dist_end":0.1916,"object_to_goal_dist_start":0.1916,"object_z_max":0.01602,"peak_contact_force":502.23913,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2994.0,"raw_peak_contact_force":694.40997,"subtask_id":"transport_arc","tcp_end":[0.50803,0.11778,0.27336],"tcp_start":[0.3972,0.00733,0.33103],"tcp_to_object_dist_end":0.26731,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.49811,0.04615,0.01602],"object_pos_start":[0.49811,0.04615,0.01602],"object_to_goal_dist_end":0.1916,"object_to_goal_dist_start":0.1916,"object_z_max":0.01602,"peak_contact_force":474.3471,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":66.0,"raw_peak_contact_force":508.18391,"subtask_id":"release_1","tcp_end":[0.50872,0.11867,0.27135],"tcp_start":[0.50803,0.11778,0.27336],"tcp_to_object_dist_end":0.26564,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```