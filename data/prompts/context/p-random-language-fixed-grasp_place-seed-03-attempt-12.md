## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0794 | 0.47 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0768 | 0.47 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.3400 | 0.83 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0779 | 0.47 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.1362 | 0.48 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.079) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
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
    offset:
    - 0.0
    - 0.0
    - 0.03
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
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
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_1
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
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
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
    offset:
    - 0.0
    - 0.0
    - 0.05
  parameters:
    approach_z_offset:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
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
    offset:
    - 0.0
    - 0.0
    - 0.03
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.015
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
- id: final_hold
  type: grasp
  control: impedance_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    hold_duration:
      type: scalar
      range:
      - 0.2
      - 0.6
      default: 0.4
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: hold_check
    when: during_phase
    predicate: object_lifted
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - parameter_bindings:
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **final_hold** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - hold_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=hold_check, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.1
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: 0.079
- **task_score** (E): 0.472
- **fitness_score**: 0.709  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1459 |
| descend_1 | 1.00 | 1.00 | 0.1162 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1603 |
| transport_1 | 0.33 | 1.00 | 0.1650 |
| descend_2 | 1.00 | 0.67 | 0.0805 |
| release_1 | 1.00 | 1.00 | 0.0208 |
| retract_1 | 1.00 | 1.00 | 0.0667 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.161) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.161)→(0.506, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.039)→(0.501, 0.002, 0.039) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.138 | 0.168 |
| lift_1 | lift | 1.00 / step_budget | (0.501, 0.002, 0.039)→(0.506, 0.002, 0.199) | (0.511, 0.002, 0.026)→(0.514, 0.002, 0.180) | 0.246→0.220 | 1.00 / 40.333 | 0.075 | 0.546 |
| transport_1 | approach | 0.33 / step_budget | (0.506, 0.002, 0.199)→(0.589, 0.133, 0.228) | (0.514, 0.002, 0.180)→(0.588, 0.134, 0.202) | 0.220→0.095 | 1.00 / 36.333 | 0.083 | 0.267 |
| descend_2 | descend | 1.00 / step_budget | (0.589, 0.133, 0.228)→(0.620, 0.178, 0.178) | (0.588, 0.134, 0.202)→(0.619, 0.177, 0.142) | 0.095→0.012 | 0.67 / 22.667 | 0.059 | 0.278 |
| release_1 | release | 1.00 / step_budget | (0.620, 0.178, 0.178)→(0.615, 0.176, 0.198) | (0.619, 0.177, 0.142)→(0.616, 0.173, 0.022) | 0.012→0.118 | 1.00 / 4.000 | 0.106 | 1.267 |
| retract_1 | retract | 1.00 / step_budget | (0.615, 0.176, 0.198)→(0.621, 0.180, 0.263) | (0.616, 0.173, 0.022)→(0.616, 0.173, 0.023) | 0.118→0.117 | 1.00 / 4.000 | 0.115 | 0.122 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.566
- phase_score: 0.415
- phase_breakdown.release_1_score: 0.315
- phase_breakdown.descend_1_score: 0.853
- phase_breakdown.transport_arc_score: 0.230
- phase_breakdown.approach_1_score: 0.112
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.757

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.757
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.566
- **Median Q (composite search score)**: 0.101
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.421


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09202,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11847,"descend_1.grasp_z_offset":0.0101,"descend_2.place_z_offset":0.0531,"lift_1.lift_height":0.19087,"release_1.release_duration":0.24615,"retract_1.retract_height":0.19737,"transport_1.approach_z_offset":0.05395,"transport_1.arc_height":0.09254,"transport_1.transport_speed":0.26179},"optimized_scores":{"best_composite_score":0.10139,"best_fitness_score":0.73139,"best_task_score":0.51645},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.6345,0.19487,-0.00347],"force_p95":0.64877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36675,"mean_force":0.18441,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61726,0.20054,0.16699]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.45586,-0.02552,-0.00112],"force_p95":0.2867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49847,"mean_force":0.06196,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44791,-0.02573,0.04194]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18834.0,"contact_point_centroid":[0.51122,0.03186,0.25045],"force_p95":0.09347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37729,"mean_force":0.05378,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50967,0.05073,0.24967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3308.0,"contact_point_centroid":[0.60037,0.19655,0.20044],"force_p95":0.16426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35207,"mean_force":0.10195,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60379,0.17797,0.20307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17090.0,"contact_point_centroid":[0.50735,0.06794,0.24986],"force_p95":0.09527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3359,"mean_force":0.05808,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5083,0.04891,0.24847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20511.0,"contact_point_centroid":[0.44891,-0.04495,0.12174],"force_p95":0.0717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30112,"mean_force":0.04901,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44973,-0.02584,0.11978]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20364.0,"contact_point_centroid":[0.45111,-0.00671,0.12151],"force_p95":0.07279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29782,"mean_force":0.04956,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44976,-0.02584,0.11994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4297.0,"contact_point_centroid":[0.60865,0.16147,0.19651],"force_p95":0.14254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28659,"mean_force":0.08675,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60445,0.17883,0.20174]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45857,-0.02638,-0.00205],"force_p95":0.13717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16515,"mean_force":0.12701,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44961,-0.02578,0.04051]},{"body_a":"world","body_b":"grasp_target","contact_count":1744.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47903,-0.01148,0.22946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5833.0,"contact_point_centroid":[0.45073,-0.00666,0.04155],"force_p95":0.07281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13096,"mean_force":0.04542,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44916,-0.02576,0.04008]},{"body_a":"world","body_b":"grasp_target","contact_count":2892.0,"contact_point_centroid":[0.63462,0.19479,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12283,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62039,0.20317,0.23846]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45517,-0.02477,0.10095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5299.0,"contact_point_centroid":[0.4475,-0.04492,0.04247],"force_p95":0.0795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09334,"mean_force":0.04955,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44917,-0.02576,0.04008]}],"total_contact_groups":14},"final_pose_error":0.01551,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63462,0.19479,0.01602],"final_tcp_position":[0.62713,0.20695,0.29632],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.36675,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1744.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45879,-0.02373,0.15785],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45406,-0.0259,0.04492],"tcp_start":[0.45879,-0.02373,0.15785],"tcp_to_object_dist_end":0.01944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02617,0.02583],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30363,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13646,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12936.0,"raw_peak_contact_force":0.16515,"tcp_end":[0.44914,-0.02576,0.04006],"tcp_start":[0.44914,-0.02576,0.04006],"tcp_to_object_dist_end":0.01703,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46165,-0.02649,0.18163],"object_pos_start":[0.45849,-0.0262,0.02584],"object_to_goal_dist_end":0.29669,"object_to_goal_dist_start":0.30365,"object_z_max":0.18143,"peak_contact_force":0.06983,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41005.0,"raw_peak_contact_force":0.49847,"tcp_end":[0.45449,-0.02604,0.20154],"tcp_start":[0.44914,-0.02576,0.04006],"tcp_to_object_dist_end":0.02117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58328,0.1571,0.21104],"object_pos_start":[0.46165,-0.02649,0.18163],"object_to_goal_dist_end":0.11917,"object_to_goal_dist_start":0.29669,"object_z_max":0.24731,"peak_contact_force":0.10927,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35924.0,"raw_peak_contact_force":0.37729,"subtask_id":"transport_arc","tcp_end":[0.58946,0.15732,0.24119],"tcp_start":[0.45449,-0.02604,0.20154],"tcp_to_object_dist_end":0.03077,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.62104,0.19665,0.1142],"object_pos_start":[0.58328,0.1571,0.21104],"object_to_goal_dist_end":0.01471,"object_to_goal_dist_start":0.11917,"object_z_max":0.21104,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7605.0,"raw_peak_contact_force":0.35207,"subtask_id":"release_1","tcp_end":[0.62243,0.20217,0.16561],"tcp_start":[0.58946,0.15732,0.24119],"tcp_to_object_dist_end":0.05173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63462,0.19479,0.016],"object_pos_start":[0.62104,0.19665,0.1142],"object_to_goal_dist_end":0.09913,"object_to_goal_dist_start":0.01471,"object_z_max":0.1142,"peak_contact_force":0.12285,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":604.0,"raw_peak_contact_force":1.36675,"subtask_id":"release_1","tcp_end":[0.61656,0.20028,0.18537],"tcp_start":[0.62243,0.20217,0.16561],"tcp_to_object_dist_end":0.17041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.63462,0.19479,0.01602],"object_pos_start":[0.63462,0.19479,0.016],"object_to_goal_dist_end":0.09912,"object_to_goal_dist_start":0.09913,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2892.0,"raw_peak_contact_force":0.12283,"tcp_end":[0.62713,0.20695,0.29632],"tcp_start":[0.61656,0.20028,0.18537],"tcp_to_object_dist_end":0.28067,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63924,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14943,"descend_1.grasp_z_offset":0.0103,"descend_2.place_z_offset":0.04128,"lift_1.lift_height":0.21696,"release_1.release_duration":0.23624,"retract_1.retract_height":0.05185,"transport_1.approach_z_offset":0.04393,"transport_1.arc_height":0.05477,"transport_1.transport_speed":0.11331},"optimized_scores":{"best_composite_score":0.01016,"best_fitness_score":0.64016,"best_task_score":0.33193},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.63246,0.15265,-0.00784],"force_p95":1.06989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24085,"mean_force":0.36709,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63788,0.15382,0.23628]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.54158,0.00104,-0.00112],"force_p95":0.39276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57239,"mean_force":0.07802,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53177,0.00088,0.03974]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19689.0,"contact_point_centroid":[0.53351,0.02013,0.11864],"force_p95":0.07486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33765,"mean_force":0.05121,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53359,0.00092,0.11672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21475.0,"contact_point_centroid":[0.53332,-0.01818,0.11678],"force_p95":0.06975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30775,"mean_force":0.04747,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53351,0.00092,0.11506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14170.0,"contact_point_centroid":[0.60928,0.1321,0.24074],"force_p95":0.09838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23528,"mean_force":0.06059,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61262,0.11333,0.2397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16119.0,"contact_point_centroid":[0.61503,0.09475,0.23908],"force_p95":0.09247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22746,"mean_force":0.0548,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61276,0.11351,0.23965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21643.0,"contact_point_centroid":[0.55731,0.01242,0.23738],"force_p95":0.06722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16999,"mean_force":0.04576,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55675,0.03157,0.23552]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":713.0,"contact_point_centroid":[0.63777,0.17348,0.21787],"force_p95":0.10695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16894,"mean_force":0.06993,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64118,0.15479,0.22039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20609.0,"contact_point_centroid":[0.55607,0.051,0.23834],"force_p95":0.07015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16741,"mean_force":0.04781,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55695,0.03185,0.23607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":834.0,"contact_point_centroid":[0.64548,0.13691,0.21554],"force_p95":0.09121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15503,"mean_force":0.06114,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64117,0.15479,0.22038]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.12996,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14523,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53375,0.00092,0.03861]},{"body_a":"world","body_b":"grasp_target","contact_count":1620.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51684,0.00047,0.24194]},{"body_a":"world","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53608,0.00097,0.11415]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.63258,0.15261,-0.00247],"force_p95":0.09488,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.09957,"mean_force":0.07723,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63823,0.15402,0.24358]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53342,0.0202,0.03994],"force_p95":0.07443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09563,"mean_force":0.0497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53327,0.00091,0.03803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6430.0,"contact_point_centroid":[0.53294,-0.01816,0.03955],"force_p95":0.06277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08801,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53327,0.00091,0.03803]}],"total_contact_groups":16},"final_pose_error":0.00955,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63283,0.15247,0.02644],"final_tcp_position":[0.63886,0.15436,0.24225],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.24085,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1620.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53628,0.00096,0.18506],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1696.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53859,0.00102,0.04446],"tcp_start":[0.53628,0.00096,0.18506],"tcp_to_object_dist_end":0.0193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00113,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25025,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1298,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13526.0,"raw_peak_contact_force":0.14523,"tcp_end":[0.53324,0.00091,0.03801],"tcp_start":[0.53324,0.00091,0.03801],"tcp_to_object_dist_end":0.01634,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5462,0.00113,0.17902],"object_pos_start":[0.54421,0.00113,0.02589],"object_to_goal_dist_end":0.18726,"object_to_goal_dist_start":0.25025,"object_z_max":0.17884,"peak_contact_force":0.07888,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41313.0,"raw_peak_contact_force":0.57239,"tcp_end":[0.53843,0.00103,0.19701],"tcp_start":[0.53324,0.00091,0.03801],"tcp_to_object_dist_end":0.01959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58692,0.07071,0.23907],"object_pos_start":[0.5462,0.00113,0.17902],"object_to_goal_dist_end":0.1167,"object_to_goal_dist_start":0.18726,"object_z_max":0.23906,"peak_contact_force":0.07091,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":42252.0,"raw_peak_contact_force":0.16999,"subtask_id":"transport_arc","tcp_end":[0.58353,0.06986,0.26205],"tcp_start":[0.53843,0.00103,0.19701],"tcp_to_object_dist_end":0.02325,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.64004,0.15595,0.19296],"object_pos_start":[0.58692,0.07071,0.23907],"object_to_goal_dist_end":0.00809,"object_to_goal_dist_start":0.1167,"object_z_max":0.23907,"peak_contact_force":0.10753,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30289.0,"raw_peak_contact_force":0.23528,"subtask_id":"release_1","tcp_end":[0.64266,0.15509,0.22419],"tcp_start":[0.58353,0.06986,0.26205],"tcp_to_object_dist_end":0.03135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63333,0.15226,0.02291],"object_pos_start":[0.64004,0.15595,0.19296],"object_to_goal_dist_end":0.1689,"object_to_goal_dist_start":0.00809,"object_z_max":0.19296,"peak_contact_force":0.06697,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1743.0,"raw_peak_contact_force":1.24085,"subtask_id":"release_1","tcp_end":[0.63785,0.15382,0.24376],"tcp_start":[0.64266,0.15509,0.22419],"tcp_to_object_dist_end":0.22089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.63283,0.15247,0.02644],"object_pos_start":[0.63333,0.15226,0.02291],"object_to_goal_dist_end":0.16542,"object_to_goal_dist_start":0.1689,"object_z_max":0.02638,"peak_contact_force":0.09957,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":80.0,"raw_peak_contact_force":0.09957,"tcp_end":[0.63886,0.15436,0.24225],"tcp_start":[0.63785,0.15382,0.24376],"tcp_to_object_dist_end":0.21591,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88462,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10234,"descend_1.grasp_z_offset":0.01065,"descend_2.place_z_offset":0.02834,"lift_1.lift_height":0.18568,"release_1.release_duration":0.31125,"retract_1.retract_height":0.15661,"transport_1.approach_z_offset":0.0681,"transport_1.arc_height":0.12433,"transport_1.transport_speed":0.27348},"optimized_scores":{"best_composite_score":0.12666,"best_fitness_score":0.75666,"best_task_score":0.56629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":297.0,"contact_point_centroid":[0.57936,0.17229,-0.00456],"force_p95":0.8216,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.1944,"mean_force":0.23487,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58954,0.17369,0.15336]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.52764,0.0293,-0.00119],"force_p95":0.38448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56798,"mean_force":0.07593,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51808,0.02967,0.04022]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18018.0,"contact_point_centroid":[0.5201,0.04895,0.11982],"force_p95":0.07885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33655,"mean_force":0.05497,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52074,0.02978,0.11722]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21134.0,"contact_point_centroid":[0.52142,0.01074,0.11764],"force_p95":0.07393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30093,"mean_force":0.04797,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52067,0.02977,0.11618]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21032.0,"contact_point_centroid":[0.56059,0.07914,0.22362],"force_p95":0.06712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25282,"mean_force":0.04527,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55812,0.09814,0.22201]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2161.0,"contact_point_centroid":[0.59003,0.19229,0.16436],"force_p95":0.07931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24634,"mean_force":0.05316,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59489,0.17386,0.16156]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18187.0,"contact_point_centroid":[0.55577,0.11799,0.22516],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23266,"mean_force":0.05059,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55861,0.09912,0.22191]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1061.0,"contact_point_centroid":[0.58983,0.19372,0.14226],"force_p95":0.07924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.231,"mean_force":0.04899,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59375,0.175,0.13982]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1242.0,"contact_point_centroid":[0.59835,0.15638,0.13928],"force_p95":0.07204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2202,"mean_force":0.04328,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59374,0.175,0.1398]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2517.0,"contact_point_centroid":[0.59872,0.15498,0.1629],"force_p95":0.06875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20824,"mean_force":0.04695,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59487,0.1738,0.16232]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53055,0.03082,-0.00211],"force_p95":0.14826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1941,"mean_force":0.13068,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51999,0.02981,0.03896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6371.0,"contact_point_centroid":[0.51998,0.01069,0.03947],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14648,"mean_force":0.04151,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51951,0.02978,0.0384]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.57919,0.17221,-0.00198],"force_p95":0.12694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14374,"mean_force":0.12255,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59219,0.17511,0.20537]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51081,0.01381,0.21933]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52311,0.02905,0.09159]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5335.0,"contact_point_centroid":[0.51902,0.04904,0.04089],"force_p95":0.08213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08303,"mean_force":0.04951,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51952,0.02978,0.03841]}],"total_contact_groups":16},"final_pose_error":0.01484,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57918,0.17221,0.02602],"final_tcp_position":[0.59788,0.17737,0.25038],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.1944,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5241,0.02815,0.13944],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1168.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52476,0.03012,0.04456],"tcp_start":[0.5241,0.02815,0.13944],"tcp_to_object_dist_end":0.01942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.03032,0.02567],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18391,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14675,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13510.0,"raw_peak_contact_force":0.1941,"tcp_end":[0.51949,0.02977,0.03838],"tcp_start":[0.51949,0.02977,0.03838],"tcp_to_object_dist_end":0.0168,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.53426,0.03079,0.17977],"object_pos_start":[0.53047,0.03034,0.02569],"object_to_goal_dist_end":0.1775,"object_to_goal_dist_start":0.18389,"object_z_max":0.17965,"peak_contact_force":0.07763,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39299.0,"raw_peak_contact_force":0.56798,"tcp_end":[0.52652,0.03009,0.19858],"tcp_start":[0.51949,0.02977,0.03838],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":927.0,"n_steps_budget":1000.0,"object_pos_end":[0.59492,0.17384,0.15693],"object_pos_start":[0.53426,0.03079,0.17977],"object_to_goal_dist_end":0.04951,"object_to_goal_dist_start":0.1775,"object_z_max":0.2157,"peak_contact_force":0.06774,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39219.0,"raw_peak_contact_force":0.25282,"subtask_id":"transport_arc","tcp_end":[0.5953,0.17245,0.18098],"tcp_start":[0.52652,0.03009,0.19858],"tcp_to_object_dist_end":0.02409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.59575,0.17726,0.11932],"object_pos_start":[0.59492,0.17384,0.15693],"object_to_goal_dist_end":0.0127,"object_to_goal_dist_start":0.04951,"object_z_max":0.15693,"peak_contact_force":0.06944,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4678.0,"raw_peak_contact_force":0.24634,"subtask_id":"release_1","tcp_end":[0.59585,0.17557,0.14376],"tcp_start":[0.5953,0.17245,0.18098],"tcp_to_object_dist_end":0.0245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57969,0.17215,0.0265],"object_pos_start":[0.59575,0.17726,0.11932],"object_to_goal_dist_end":0.0847,"object_to_goal_dist_start":0.0127,"object_z_max":0.11932,"peak_contact_force":0.1293,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2600.0,"raw_peak_contact_force":1.1944,"subtask_id":"release_1","tcp_end":[0.58944,0.17366,0.16436],"tcp_start":[0.59585,0.17557,0.14376],"tcp_to_object_dist_end":0.13821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.57918,0.17221,0.02602],"object_pos_start":[0.57969,0.17215,0.0265],"object_to_goal_dist_end":0.0853,"object_to_goal_dist_start":0.0847,"object_z_max":0.02653,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.14374,"tcp_end":[0.59788,0.17737,0.25038],"tcp_start":[0.58944,0.17366,0.16436],"tcp_to_object_dist_end":0.22519,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```