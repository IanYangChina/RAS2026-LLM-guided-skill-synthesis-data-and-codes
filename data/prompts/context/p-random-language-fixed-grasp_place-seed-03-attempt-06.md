## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → grasp → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.2272 | 0.77 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.1426 | 0.46 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1155 | 0.43 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.2522 | 0.47 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.1848 | 0.48 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.227) — your mutation base

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
- id: secure_grasp
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
    squeeze_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
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
    - 0.024
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
    transport_height_offset:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.024
      binds_to:
      - path: target.offset.z
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.024
  parameters:
    fine_place_offset:
      type: scalar
      range:
      - 0.015
      - 0.035
      default: 0.024
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
- id: hold_final
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
  parameters:
    hold_duration:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.4
      binds_to:
      - path: duration.max_time
        mode: replace

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
- **secure_grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - squeeze_duration: status=consumed; consumers=duration.max_time (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.024]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_height_offset: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.024]
  - parameter_bindings:
    - fine_place_offset: status=consumed; consumers=target.offset.z (replace)
- **hold_final** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - hold_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.227
- **task_score** (E): 0.767
- **fitness_score**: 0.857  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1585 |
| descend_1 | 1.00 | 1.00 | 0.1036 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1622 |
| secure_grasp | 1.00 | 1.00 | 0.0110 |
| transport_1 | 0.67 | 1.00 | 0.1756 |
| descend_2 | 1.00 | 1.00 | 0.0783 |
| hold_final | 1.00 | 1.00 | 0.0158 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.039)→(0.501, 0.002, 0.039) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.138 | 0.172 |
| lift_1 | lift | 1.00 / step_budget | (0.501, 0.002, 0.039)→(0.506, 0.002, 0.201) | (0.511, 0.002, 0.026)→(0.514, 0.002, 0.182) | 0.246→0.221 | 1.00 / 39.667 | 0.078 | 0.551 |
| secure_grasp | grasp | 1.00 / step_budget | (0.506, 0.002, 0.201)→(0.500, 0.002, 0.191) | (0.514, 0.002, 0.182)→(0.505, 0.002, 0.170) | 0.221→0.223 | 1.00 / 40.333 | 0.073 | 0.124 |
| transport_1 | approach | 0.67 / step_budget | (0.500, 0.002, 0.191)→(0.590, 0.137, 0.221) | (0.505, 0.002, 0.170)→(0.586, 0.138, 0.194) | 0.223→0.083 | 1.00 / 30.667 | 0.092 | 0.323 |
| descend_2 | descend | 1.00 / step_budget | (0.590, 0.137, 0.221)→(0.620, 0.177, 0.162) | (0.586, 0.138, 0.194)→(0.601, 0.171, 0.105) | 0.083→0.047 | 1.00 / 23.333 | 0.101 | 0.789 |
| hold_final | grasp | 1.00 / step_budget | (0.620, 0.177, 0.162)→(0.613, 0.175, 0.148) | (0.601, 0.171, 0.105)→(0.598, 0.170, 0.094) | 0.047→0.054 | 1.00 / 18.333 | 0.113 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.009
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.597
- phase_breakdown.release_1_score: 0.546
- phase_breakdown.descend_1_score: 0.853
- phase_breakdown.transport_arc_score: 0.501
- phase_breakdown.approach_1_score: 0.093
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.264
- **K-run variance**: 0.0128
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.415


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90303,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05145,"descend_1.grasp_z_offset":0.01011,"descend_2.fine_place_offset":0.022,"hold_final.hold_duration":0.48106,"lift_1.lift_height":0.19159,"secure_grasp.squeeze_duration":0.3767,"transport_1.arc_height":0.17836,"transport_1.transport_height_offset":0.01457,"transport_1.transport_speed":0.16281},"optimized_scores":{"best_composite_score":0.07429,"best_fitness_score":0.70429,"best_task_score":0.4622},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1670.0,"contact_point_centroid":[0.574,0.18308,-0.00265],"force_p95":0.28443,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69028,"mean_force":0.15127,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60425,0.17926,0.1643]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.4559,-0.02523,-0.00111],"force_p95":0.28184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49774,"mean_force":0.06153,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44756,-0.02558,0.04169]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3918.0,"contact_point_centroid":[0.55746,0.09851,0.24504],"force_p95":0.14855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36042,"mean_force":0.0942,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55586,0.1172,0.24808]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5105.0,"contact_point_centroid":[0.55339,0.13688,0.24348],"force_p95":0.10548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35024,"mean_force":0.0719,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55712,0.11885,0.24577]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18362.0,"contact_point_centroid":[0.48563,0.00616,0.25444],"force_p95":0.0814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30582,"mean_force":0.05393,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48577,0.02534,0.25343]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21535.0,"contact_point_centroid":[0.45034,-0.00656,0.12098],"force_p95":0.07069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30246,"mean_force":0.04728,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44955,-0.02572,0.1197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20855.0,"contact_point_centroid":[0.44855,-0.04487,0.12445],"force_p95":0.07252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28781,"mean_force":0.0484,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44972,-0.02572,0.12262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20046.0,"contact_point_centroid":[0.48572,0.04542,0.25523],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26344,"mean_force":0.04939,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48668,0.02648,0.25407]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45858,-0.02636,-0.00207],"force_p95":0.14042,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17651,"mean_force":0.12799,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44927,-0.02563,0.04022]},{"body_a":"world","body_b":"grasp_target","contact_count":2524.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47777,-0.01203,0.19537]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5828.0,"contact_point_centroid":[0.45039,-0.00652,0.04126],"force_p95":0.07192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13187,"mean_force":0.04542,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44882,-0.02562,0.03978]},{"body_a":"world","body_b":"grasp_target","contact_count":656.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4544,-0.02507,0.06788]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.57393,0.18333,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"hold_final","phase_type":"grasp","tcp_position_centroid":[0.61623,0.20068,0.12108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8447.0,"contact_point_centroid":[0.44873,-0.04493,0.19811],"force_p95":0.07546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11625,"mean_force":0.0515,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.44979,-0.02577,0.19567]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9693.0,"contact_point_centroid":[0.45105,-0.00672,0.19784],"force_p95":0.06729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1154,"mean_force":0.04539,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.44977,-0.02576,0.19564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5308.0,"contact_point_centroid":[0.44723,-0.04478,0.04225],"force_p95":0.07972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08545,"mean_force":0.04954,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44882,-0.02562,0.03979]}],"total_contact_groups":18},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.57393,0.18333,0.01602],"final_tcp_position":[0.62246,0.20255,0.13314],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.69028,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2524.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45705,-0.02446,0.09109],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":656.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45371,-0.02575,0.04461],"tcp_start":[0.45705,-0.02446,0.09109],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02607,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30356,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1393,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12940.0,"raw_peak_contact_force":0.17651,"tcp_end":[0.4488,-0.02561,0.03976],"tcp_start":[0.4488,-0.02561,0.03976],"tcp_to_object_dist_end":0.01702,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4619,-0.02635,0.1822],"object_pos_start":[0.4585,-0.0261,0.0258],"object_to_goal_dist_end":0.29658,"object_to_goal_dist_start":0.30358,"object_z_max":0.182,"peak_contact_force":0.07426,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42522.0,"raw_peak_contact_force":0.49774,"tcp_end":[0.45449,-0.02594,0.20217],"tcp_start":[0.4488,-0.02561,0.03976],"tcp_to_object_dist_end":0.0213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45356,-0.02616,0.17183],"object_pos_start":[0.4619,-0.02635,0.1822],"object_to_goal_dist_end":0.29906,"object_to_goal_dist_start":0.29658,"object_z_max":0.18234,"peak_contact_force":0.08078,"phase_name":"secure_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18140.0,"raw_peak_contact_force":0.11625,"tcp_end":[0.44882,-0.02573,0.19434],"tcp_start":[0.45449,-0.02594,0.20217],"tcp_to_object_dist_end":0.02301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53981,0.09529,0.25599],"object_pos_start":[0.45356,-0.02616,0.17183],"object_to_goal_dist_end":0.20258,"object_to_goal_dist_start":0.29906,"object_z_max":0.25714,"peak_contact_force":0.08944,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38408.0,"raw_peak_contact_force":0.30582,"subtask_id":"transport_arc","tcp_end":[0.54,0.09468,0.28368],"tcp_start":[0.44882,-0.02573,0.19434],"tcp_to_object_dist_end":0.02769,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":877.0,"n_steps_budget":1000.0,"object_pos_end":[0.57393,0.18333,0.01602],"object_pos_start":[0.53981,0.09529,0.25599],"object_to_goal_dist_end":0.11576,"object_to_goal_dist_start":0.20258,"object_z_max":0.25599,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12210.0,"raw_peak_contact_force":1.69028,"subtask_id":"release_1","tcp_end":[0.62246,0.20255,0.13314],"tcp_start":[0.54,0.09468,0.28368],"tcp_to_object_dist_end":0.12823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57393,0.18333,0.01602],"object_pos_start":[0.57393,0.18333,0.01602],"object_to_goal_dist_end":0.11576,"object_to_goal_dist_start":0.11576,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"hold_final","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61512,0.20032,0.11895],"tcp_start":[0.62246,0.20255,0.13314],"tcp_to_object_dist_end":0.11216,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87407,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16845,"descend_1.grasp_z_offset":0.01001,"descend_2.fine_place_offset":0.02517,"hold_final.hold_duration":0.40393,"lift_1.lift_height":0.21059,"secure_grasp.squeeze_duration":0.38723,"transport_1.arc_height":0.15278,"transport_1.transport_height_offset":0.03288,"transport_1.transport_speed":0.2123},"optimized_scores":{"best_composite_score":0.26365,"best_fitness_score":0.89365,"best_task_score":0.83779},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.5406,0.00104,-0.00114],"force_p95":0.42841,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58135,"mean_force":0.08927,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53187,0.00088,0.03921]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1642.0,"contact_point_centroid":[0.6315,0.16433,0.2252],"force_p95":0.09281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41177,"mean_force":0.06819,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63523,0.14569,0.2251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21046.0,"contact_point_centroid":[0.57373,0.03977,0.24288],"force_p95":0.07578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35613,"mean_force":0.04806,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57256,0.05886,0.24149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19974.0,"contact_point_centroid":[0.53381,0.02012,0.1201],"force_p95":0.07463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33854,"mean_force":0.05055,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53388,0.00093,0.11824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19596.0,"contact_point_centroid":[0.56973,0.07614,0.243],"force_p95":0.07549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33053,"mean_force":0.05057,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57125,0.0571,0.24082]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5707.0,"contact_point_centroid":[0.63135,0.16949,0.2016],"force_p95":0.1048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31958,"mean_force":0.07367,"phase_index":7.0,"phase_name":"hold_final","phase_type":"grasp","tcp_position_centroid":[0.63492,0.15088,0.20257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21256.0,"contact_point_centroid":[0.53363,-0.01819,0.11766],"force_p95":0.07116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3089,"mean_force":0.04787,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53376,0.00092,0.11593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1810.0,"contact_point_centroid":[0.63789,0.12702,0.22317],"force_p95":0.08711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29665,"mean_force":0.06319,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63518,0.14563,0.22522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6715.0,"contact_point_centroid":[0.63842,0.13271,0.1994],"force_p95":0.09132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2562,"mean_force":0.06357,"phase_index":7.0,"phase_name":"hold_final","phase_type":"grasp","tcp_position_centroid":[0.63488,0.15087,0.20249]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.12997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14511,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5338,0.00092,0.03814]},{"body_a":"world","body_b":"grasp_target","contact_count":1416.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51662,0.00046,0.25134]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9457.0,"contact_point_centroid":[0.53388,-0.01813,0.19276],"force_p95":0.06796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12785,"mean_force":0.04663,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.53385,0.00096,0.19084]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8632.0,"contact_point_centroid":[0.53391,0.02015,0.19298],"force_p95":0.07297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1247,"mean_force":0.05067,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.53385,0.00096,0.19083]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53595,0.00096,0.12318]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53346,0.0202,0.03945],"force_p95":0.07443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09563,"mean_force":0.0497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53332,0.00091,0.03757]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6430.0,"contact_point_centroid":[0.53298,-0.01816,0.03907],"force_p95":0.06277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08788,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53332,0.00091,0.03757]}],"total_contact_groups":16},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63363,0.15196,0.16939],"final_tcp_position":[0.63989,0.15197,0.21461],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.58135,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1416.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53594,0.00095,0.2038],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1924.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53865,0.00102,0.04399],"tcp_start":[0.53594,0.00095,0.2038],"tcp_to_object_dist_end":0.01884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00113,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25025,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12981,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13526.0,"raw_peak_contact_force":0.14511,"tcp_end":[0.53329,0.00091,0.03754],"tcp_start":[0.53329,0.00091,0.03754],"tcp_to_object_dist_end":0.01597,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54678,0.00112,0.18189],"object_pos_start":[0.54421,0.00113,0.02589],"object_to_goal_dist_end":0.1868,"object_to_goal_dist_start":0.25025,"object_z_max":0.18171,"peak_contact_force":0.08086,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41377.0,"raw_peak_contact_force":0.58135,"tcp_end":[0.5389,0.00103,0.19941],"tcp_start":[0.53329,0.00091,0.03754],"tcp_to_object_dist_end":0.01921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.538,0.00103,0.16909],"object_pos_start":[0.54678,0.00112,0.18189],"object_to_goal_dist_end":0.19278,"object_to_goal_dist_start":0.1868,"object_z_max":0.18203,"peak_contact_force":0.06955,"phase_name":"secure_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18089.0,"raw_peak_contact_force":0.12785,"tcp_end":[0.53288,0.00094,0.18922],"tcp_start":[0.5389,0.00103,0.19941],"tcp_to_object_dist_end":0.02077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62795,0.14019,0.2104],"object_pos_start":[0.538,0.00103,0.16909],"object_to_goal_dist_end":0.03286,"object_to_goal_dist_start":0.19278,"object_z_max":0.23992,"peak_contact_force":0.09181,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40642.0,"raw_peak_contact_force":0.35613,"subtask_id":"transport_arc","tcp_end":[0.63189,0.13973,0.23812],"tcp_start":[0.53288,0.00094,0.18922],"tcp_to_object_dist_end":0.028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.63816,0.15305,0.18699],"object_pos_start":[0.62795,0.14019,0.2104],"object_to_goal_dist_end":0.01148,"object_to_goal_dist_start":0.03286,"object_z_max":0.2104,"peak_contact_force":0.08938,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3452.0,"raw_peak_contact_force":0.41177,"subtask_id":"release_1","tcp_end":[0.63989,0.15197,0.21461],"tcp_start":[0.63189,0.13973,0.23812],"tcp_to_object_dist_end":0.0277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63363,0.15196,0.16939],"object_pos_start":[0.63816,0.15305,0.18699],"object_to_goal_dist_end":0.02655,"object_to_goal_dist_start":0.01148,"object_z_max":0.18699,"peak_contact_force":0.11268,"phase_name":"hold_final","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12422.0,"raw_peak_contact_force":0.31958,"tcp_end":[0.63387,0.15061,0.20006],"tcp_start":[0.63989,0.15197,0.21461],"tcp_to_object_dist_end":0.0307,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74074,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11189,"descend_1.grasp_z_offset":0.01033,"descend_2.fine_place_offset":0.02515,"hold_final.hold_duration":0.43429,"lift_1.lift_height":0.22093,"secure_grasp.squeeze_duration":0.24334,"transport_1.arc_height":0.09988,"transport_1.transport_height_offset":0.02544,"transport_1.transport_speed":0.20922},"optimized_scores":{"best_composite_score":0.34365,"best_fitness_score":0.97365,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52746,0.02942,-0.00119],"force_p95":0.39394,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57275,"mean_force":0.07828,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51811,0.02968,0.04015]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18153.0,"contact_point_centroid":[0.51928,0.04892,0.12064],"force_p95":0.07881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33778,"mean_force":0.05499,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51993,0.02975,0.11804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20378.0,"contact_point_centroid":[0.55812,0.08185,0.21558],"force_p95":0.07648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30689,"mean_force":0.04783,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55558,0.10079,0.2144]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21288.0,"contact_point_centroid":[0.52062,0.01071,0.11846],"force_p95":0.07393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30242,"mean_force":0.04802,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51987,0.02974,0.117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17883.0,"contact_point_centroid":[0.55238,0.11866,0.21698],"force_p95":0.08021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3022,"mean_force":0.05267,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55502,0.09978,0.2143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5541.0,"contact_point_centroid":[0.58597,0.19369,0.12605],"force_p95":0.11062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2931,"mean_force":0.07567,"phase_index":7.0,"phase_name":"hold_final","phase_type":"grasp","tcp_position_centroid":[0.59028,0.17527,0.12677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6344.0,"contact_point_centroid":[0.59384,0.1572,0.12358],"force_p95":0.09836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27797,"mean_force":0.06818,"phase_index":7.0,"phase_name":"hold_final","phase_type":"grasp","tcp_position_centroid":[0.59032,0.17528,0.12684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.59168,0.19541,0.14069],"force_p95":0.13489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2648,"mean_force":0.07571,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59664,0.17711,0.14013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":320.0,"contact_point_centroid":[0.59988,0.15864,0.13783],"force_p95":0.13303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26043,"mean_force":0.06955,"phase_index":6.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59664,0.17711,0.14013]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53055,0.03081,-0.00211],"force_p95":0.1479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19384,"mean_force":0.13059,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52005,0.02982,0.03889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6283.0,"contact_point_centroid":[0.52017,0.0107,0.03947],"force_p95":0.07068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14651,"mean_force":0.04207,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51958,0.02979,0.03834]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13259,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51081,0.01375,0.22403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9414.0,"contact_point_centroid":[0.52082,0.0106,0.19402],"force_p95":0.06911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12797,"mean_force":0.04691,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.51978,0.02969,0.19212]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9004.0,"contact_point_centroid":[0.51899,0.04883,0.19454],"force_p95":0.07499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12536,"mean_force":0.04858,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.51974,0.02969,0.19206]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52311,0.02901,0.09613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5334.0,"contact_point_centroid":[0.51907,0.04904,0.0408],"force_p95":0.08202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08354,"mean_force":0.0495,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51958,0.02979,0.03834]}],"total_contact_groups":16},"final_pose_error":0.00708,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58668,0.17591,0.09522],"final_tcp_position":[0.59643,0.17706,0.13791],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.57275,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52408,0.02806,0.14875],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52483,0.03013,0.0445],"tcp_start":[0.52408,0.02806,0.14875],"tcp_to_object_dist_end":0.01934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.03033,0.02567],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1839,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14636,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13421.0,"raw_peak_contact_force":0.19384,"tcp_end":[0.51956,0.02979,0.03831],"tcp_start":[0.51956,0.02979,0.03832],"tcp_to_object_dist_end":0.0167,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53229,0.03069,0.18149],"object_pos_start":[0.53047,0.03035,0.02569],"object_to_goal_dist_end":0.17904,"object_to_goal_dist_start":0.18388,"object_z_max":0.1813,"peak_contact_force":0.07874,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39587.0,"raw_peak_contact_force":0.57275,"tcp_end":[0.52477,0.03,0.20035],"tcp_start":[0.51956,0.02979,0.03831],"tcp_to_object_dist_end":0.02032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52364,0.02994,0.16922],"object_pos_start":[0.53229,0.03069,0.18149],"object_to_goal_dist_end":0.1786,"object_to_goal_dist_start":0.17904,"object_z_max":0.18163,"peak_contact_force":0.06991,"phase_name":"secure_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18418.0,"raw_peak_contact_force":0.12797,"tcp_end":[0.51883,0.02963,0.19057],"tcp_start":[0.52477,0.03,0.20035],"tcp_to_object_dist_end":0.02189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":944.0,"n_steps_budget":1000.0,"object_pos_end":[0.59031,0.17736,0.11698],"object_pos_start":[0.52364,0.02994,0.16922],"object_to_goal_dist_end":0.01436,"object_to_goal_dist_start":0.1786,"object_z_max":0.21245,"peak_contact_force":0.09495,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38261.0,"raw_peak_contact_force":0.30689,"subtask_id":"transport_arc","tcp_end":[0.59737,0.17734,0.14239],"tcp_start":[0.51883,0.02963,0.19057],"tcp_to_object_dist_end":0.02638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.58947,0.17717,0.11228],"object_pos_start":[0.59031,0.17736,0.11698],"object_to_goal_dist_end":0.01285,"object_to_goal_dist_start":0.01436,"object_z_max":0.11698,"peak_contact_force":0.09014,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":600.0,"raw_peak_contact_force":0.2648,"subtask_id":"release_1","tcp_end":[0.59643,0.17706,0.13791],"tcp_start":[0.59737,0.17734,0.14239],"tcp_to_object_dist_end":0.02655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58668,0.17591,0.09522],"object_pos_start":[0.58947,0.17717,0.11228],"object_to_goal_dist_end":0.01983,"object_to_goal_dist_start":0.01285,"object_z_max":0.11228,"peak_contact_force":0.10279,"phase_name":"hold_final","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11885.0,"raw_peak_contact_force":0.2931,"tcp_end":[0.58908,0.17493,0.12462],"tcp_start":[0.59643,0.17706,0.13791],"tcp_to_object_dist_end":0.02951,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```