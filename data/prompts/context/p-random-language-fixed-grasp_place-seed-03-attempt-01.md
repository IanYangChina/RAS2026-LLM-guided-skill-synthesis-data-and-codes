## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1851 | 0.48 | ✅ accepted |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.185) — your mutation base

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
    - 0.15
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
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
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
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
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: add
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
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
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
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (add)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.185
- **task_score** (E): 0.482
- **fitness_score**: 0.715  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1229 |
| descend_1 | 1.00 | 1.00 | 0.1404 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 0.67 | 1.00 | 0.1312 |
| transport_1 | 1.00 | 1.00 | 0.2118 |
| descend_2 | 1.00 | 1.00 | 0.0992 |
| release_1 | 1.00 | 1.00 | 0.0206 |
| retract_1 | 1.00 | 1.00 | 0.0749 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.185) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.002, 0.185)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.038)→(0.501, 0.002, 0.038) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.000 | 0.137 | 0.168 |
| lift_1 | lift | 0.67 / step_budget | (0.501, 0.002, 0.038)→(0.506, 0.002, 0.170) | (0.511, 0.002, 0.026)→(0.514, 0.002, 0.152) | 0.246→0.214 | 1.00 / 39.333 | 0.075 | 0.547 |
| transport_1 | approach | 1.00 / step_budget | (0.506, 0.002, 0.170)→(0.605, 0.153, 0.274) | (0.514, 0.002, 0.152)→(0.607, 0.155, 0.250) | 0.214→0.117 | 1.00 / 36.333 | 55983.970 | 0.283 |
| descend_2 | descend | 1.00 / step_budget | (0.605, 0.153, 0.274)→(0.620, 0.177, 0.179) | (0.607, 0.155, 0.250)→(0.618, 0.178, 0.152) | 0.117→0.018 | 1.00 / 34.667 | 0.093 | 0.294 |
| release_1 | release | 1.00 / step_budget | (0.620, 0.177, 0.179)→(0.614, 0.175, 0.199) | (0.618, 0.178, 0.152)→(0.611, 0.174, 0.024) | 0.018→0.115 | 1.00 / 3.333 | 0.248 | 1.309 |
| retract_1 | retract | 1.00 / step_budget | (0.614, 0.175, 0.199)→(0.623, 0.180, 0.273) | (0.611, 0.174, 0.024)→(0.608, 0.173, 0.026) | 0.115→0.114 | 1.00 / 4.000 | 0.123 | 0.171 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.565
- phase_score: 0.325
- phase_breakdown.release_1_score: 0.361
- phase_breakdown.transport_arc_score: 0.063
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.851
- phase_breakdown.approach_1_score: 0.033
- grasp_place_fitness: 0.757

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.757
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.565
- **Median Q (composite search score)**: 0.220
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.423


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10667,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15261,"descend_1.grasp_z_offset":0.01015,"descend_2.place_z_offset":0.0396,"lift_1.lift_height":0.1475,"release_1.release_duration":0.31802,"retract_1.retract_speed":0.18813,"transport_1.transport_speed":0.33779},"optimized_scores":{"best_composite_score":0.2199,"best_fitness_score":0.7499,"best_task_score":0.55336},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":276.0,"contact_point_centroid":[0.62186,0.20101,-0.00492],"force_p95":0.89499,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19369,"mean_force":0.25197,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61673,0.20081,0.16665]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.45605,-0.02532,-0.00112],"force_p95":0.28554,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49357,"mean_force":0.05754,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44806,-0.02573,0.042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":593.0,"contact_point_centroid":[0.6175,0.22102,0.15114],"force_p95":0.12611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38731,"mean_force":0.08575,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62069,0.20223,0.15307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19611.0,"contact_point_centroid":[0.52177,0.04584,0.22051],"force_p95":0.08338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37761,"mean_force":0.05155,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51981,0.06473,0.2194]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3331.0,"contact_point_centroid":[0.60704,0.20537,0.20625],"force_p95":0.13813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33827,"mean_force":0.09609,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61058,0.18686,0.20772]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18196.0,"contact_point_centroid":[0.5153,0.07952,0.21893],"force_p95":0.08234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33758,"mean_force":0.05461,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51663,0.06052,0.21703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.62531,0.18485,0.14735],"force_p95":0.10315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32724,"mean_force":0.07202,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62068,0.20223,0.15306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15329.0,"contact_point_centroid":[0.44908,-0.04491,0.10246],"force_p95":0.07234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29909,"mean_force":0.04945,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4498,-0.02581,0.10055]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15112.0,"contact_point_centroid":[0.45128,-0.00668,0.10174],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29648,"mean_force":0.05027,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44979,-0.02581,0.10021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3879.0,"contact_point_centroid":[0.61599,0.17001,0.20115],"force_p95":0.13233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26473,"mean_force":0.08723,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61104,0.18747,0.20575]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45857,-0.02637,-0.00205],"force_p95":0.13708,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16494,"mean_force":0.12698,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44972,-0.02578,0.04055]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.62198,0.20108,-0.00197],"force_p95":0.13168,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14718,"mean_force":0.12234,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62015,0.20333,0.21084]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47998,-0.01103,0.24657]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5833.0,"contact_point_centroid":[0.45083,-0.00665,0.04159],"force_p95":0.07283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13083,"mean_force":0.04538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44927,-0.02577,0.04012]},{"body_a":"world","body_b":"grasp_target","contact_count":1876.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45591,-0.02445,0.11771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5436.0,"contact_point_centroid":[0.44804,-0.04494,0.0424],"force_p95":0.07943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09329,"mean_force":0.04848,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44927,-0.02577,0.04012]}],"total_contact_groups":16},"final_pose_error":0.01537,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62199,0.20108,0.02602],"final_tcp_position":[0.62633,0.20669,0.2493],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.19369,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46013,-0.02309,0.19166],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45417,-0.02591,0.04496],"tcp_start":[0.46013,-0.02309,0.19166],"tcp_to_object_dist_end":0.01945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02613,0.02583],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3036,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13668,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13073.0,"raw_peak_contact_force":0.16494,"tcp_end":[0.44925,-0.02577,0.04009],"tcp_start":[0.44925,-0.02577,0.04009],"tcp_to_object_dist_end":0.017,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.46221,-0.02641,0.14297],"object_pos_start":[0.45849,-0.02611,0.02584],"object_to_goal_dist_end":0.28997,"object_to_goal_dist_start":0.30358,"object_z_max":0.14285,"peak_contact_force":0.07135,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30572.0,"raw_peak_contact_force":0.49357,"tcp_end":[0.45434,-0.02596,0.16188],"tcp_start":[0.44925,-0.02577,0.04009],"tcp_to_object_dist_end":0.02049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59966,0.17437,0.22804],"object_pos_start":[0.46221,-0.02641,0.14297],"object_to_goal_dist_end":0.12269,"object_to_goal_dist_start":0.28997,"object_z_max":0.22849,"peak_contact_force":0.10894,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37807.0,"raw_peak_contact_force":0.37761,"subtask_id":"transport_arc","tcp_end":[0.60187,0.17362,0.25605],"tcp_start":[0.45434,-0.02596,0.16188],"tcp_to_object_dist_end":0.02811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.61794,0.20406,0.12503],"object_pos_start":[0.59966,0.17437,0.22804],"object_to_goal_dist_end":0.01688,"object_to_goal_dist_start":0.12269,"object_z_max":0.22804,"peak_contact_force":0.13346,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7210.0,"raw_peak_contact_force":0.33827,"subtask_id":"release_1","tcp_end":[0.62279,0.20278,0.15745],"tcp_start":[0.60187,0.17362,0.25605],"tcp_to_object_dist_end":0.0328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6204,0.20082,0.02639],"object_pos_start":[0.61794,0.20406,0.12503],"object_to_goal_dist_end":0.08858,"object_to_goal_dist_start":0.01688,"object_z_max":0.12503,"peak_contact_force":0.11698,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1613.0,"raw_peak_contact_force":1.19369,"tcp_end":[0.61666,0.20078,0.17693],"tcp_start":[0.62279,0.20278,0.15745],"tcp_to_object_dist_end":0.15059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.62199,0.20108,0.02602],"object_pos_start":[0.6204,0.20082,0.02639],"object_to_goal_dist_end":0.08876,"object_to_goal_dist_start":0.08858,"object_z_max":0.0266,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.14718,"tcp_end":[0.62633,0.20669,0.2493],"tcp_start":[0.61666,0.20078,0.17693],"tcp_to_object_dist_end":0.22339,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12548,"descend_1.grasp_z_offset":0.01,"descend_2.place_z_offset":0.04667,"lift_1.lift_height":0.25804,"release_1.release_duration":0.25042,"retract_1.retract_speed":0.29486,"transport_1.transport_speed":0.36585},"optimized_scores":{"best_composite_score":0.10859,"best_fitness_score":0.63859,"best_task_score":0.32777},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.62374,0.14858,-0.00823],"force_p95":1.48313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64652,"mean_force":0.44092,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63678,0.15187,0.25572]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.54137,0.0009,-0.00113],"force_p95":0.41395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58206,"mean_force":0.08062,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53166,0.00087,0.03917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19176.0,"contact_point_centroid":[0.53282,0.02013,0.11967],"force_p95":0.07559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33984,"mean_force":0.05252,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53284,0.00091,0.11761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4977.0,"contact_point_centroid":[0.62879,0.16078,0.28647],"force_p95":0.07455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33855,"mean_force":0.04935,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63376,0.14225,0.28325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21732.0,"contact_point_centroid":[0.53251,-0.01817,0.11761],"force_p95":0.06932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31099,"mean_force":0.0471,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53276,0.0009,0.11591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1278.0,"contact_point_centroid":[0.63444,0.17121,0.24244],"force_p95":0.06636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26415,"mean_force":0.042,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63982,0.1528,0.23916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22462.0,"contact_point_centroid":[0.57873,0.04259,0.26982],"force_p95":0.06638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26309,"mean_force":0.04511,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57737,0.06169,0.26809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5639.0,"contact_point_centroid":[0.63614,0.12303,0.28471],"force_p95":0.07151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25568,"mean_force":0.04486,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63372,0.14219,0.28346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20005.0,"contact_point_centroid":[0.57514,0.0802,0.27035],"force_p95":0.07061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24317,"mean_force":0.04968,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57697,0.06114,0.26768]},{"body_a":"world","body_b":"grasp_target","contact_count":1958.0,"contact_point_centroid":[0.62308,0.14865,-0.00209],"force_p95":0.16821,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23197,"mean_force":0.12509,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63994,0.15434,0.29359]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1402.0,"contact_point_centroid":[0.64207,0.13352,0.24004],"force_p95":0.0651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2214,"mean_force":0.03901,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63982,0.1528,0.23915]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13002,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14518,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53365,0.00091,0.03804]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51698,0.00047,0.23033]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53619,0.00097,0.10227]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53335,0.0202,0.03942],"force_p95":0.07442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09565,"mean_force":0.0497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53317,0.00091,0.03747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6430.0,"contact_point_centroid":[0.53286,-0.01816,0.03902],"force_p95":0.06278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08786,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53317,0.00091,0.03747]}],"total_contact_groups":16},"final_pose_error":0.01462,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62216,0.14845,0.02602],"final_tcp_position":[0.64485,0.15706,0.32678],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53662,0.00097,0.16169],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5385,0.00101,0.04389],"tcp_start":[0.53662,0.00097,0.16169],"tcp_to_object_dist_end":0.01879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00113,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25025,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12986,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13526.0,"raw_peak_contact_force":0.14518,"tcp_end":[0.53314,0.00091,0.03744],"tcp_start":[0.53314,0.00091,0.03744],"tcp_to_object_dist_end":0.016,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54482,0.00108,0.18041],"object_pos_start":[0.54421,0.00113,0.02589],"object_to_goal_dist_end":0.18797,"object_to_goal_dist_start":0.25025,"object_z_max":0.18022,"peak_contact_force":0.08007,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41054.0,"raw_peak_contact_force":0.58206,"tcp_end":[0.537,0.00099,0.19825],"tcp_start":[0.53314,0.00091,0.03744],"tcp_to_object_dist_end":0.01948,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63086,0.1341,0.2994],"object_pos_start":[0.54482,0.00108,0.18041],"object_to_goal_dist_end":0.11218,"object_to_goal_dist_start":0.18797,"object_z_max":0.29932,"peak_contact_force":167951.73011,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":42467.0,"raw_peak_contact_force":0.26309,"subtask_id":"transport_arc","tcp_end":[0.62802,0.13277,0.32328],"tcp_start":[0.537,0.00099,0.19825],"tcp_to_object_dist_end":0.02408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.64305,0.15469,0.21877],"object_pos_start":[0.63086,0.1341,0.2994],"object_to_goal_dist_end":0.02824,"object_to_goal_dist_start":0.11218,"object_z_max":0.2994,"peak_contact_force":0.06691,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10616.0,"raw_peak_contact_force":0.33855,"subtask_id":"release_1","tcp_end":[0.64141,0.15306,0.24352],"tcp_start":[0.62802,0.13277,0.32328],"tcp_to_object_dist_end":0.02486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63432,0.15101,0.01972],"object_pos_start":[0.64305,0.15469,0.21877],"object_to_goal_dist_end":0.17205,"object_to_goal_dist_start":0.02824,"object_z_max":0.21877,"peak_contact_force":0.49806,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2856.0,"raw_peak_contact_force":1.64652,"tcp_end":[0.63675,0.15187,0.26258],"tcp_start":[0.64141,0.15306,0.24352],"tcp_to_object_dist_end":0.24288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.62216,0.14845,0.02602],"object_pos_start":[0.63432,0.15101,0.01972],"object_to_goal_dist_end":0.16731,"object_to_goal_dist_start":0.17205,"object_z_max":0.02875,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1958.0,"raw_peak_contact_force":0.23197,"tcp_end":[0.64485,0.15706,0.32678],"tcp_start":[0.63675,0.15187,0.26258],"tcp_to_object_dist_end":0.30174,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1648,"descend_1.grasp_z_offset":0.01,"descend_2.place_z_offset":0.02174,"lift_1.lift_height":0.1356,"release_1.release_duration":0.41507,"retract_1.retract_speed":0.38326,"transport_1.transport_speed":0.20241},"optimized_scores":{"best_composite_score":0.22694,"best_fitness_score":0.75694,"best_task_score":0.56531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":307.0,"contact_point_centroid":[0.57914,0.17028,-0.00441],"force_p95":0.7464,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08822,"mean_force":0.2253,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58905,0.17237,0.14577]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52742,0.02936,-0.00118],"force_p95":0.38351,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56453,"mean_force":0.07904,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51847,0.02971,0.03975]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13593.0,"contact_point_centroid":[0.52002,0.04892,0.09562],"force_p95":0.07781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33237,"mean_force":0.05147,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52081,0.0298,0.09362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14026.0,"contact_point_centroid":[0.52184,0.01069,0.09307],"force_p95":0.07532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30517,"mean_force":0.05013,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52064,0.02979,0.09154]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1049.0,"contact_point_centroid":[0.58953,0.19245,0.13488],"force_p95":0.07976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26138,"mean_force":0.04986,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59331,0.1737,0.1325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1239.0,"contact_point_centroid":[0.59792,0.15512,0.1319],"force_p95":0.07127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22566,"mean_force":0.04366,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59332,0.17371,0.13251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21911.0,"contact_point_centroid":[0.55572,0.07076,0.20586],"force_p95":0.06877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20791,"mean_force":0.04585,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55326,0.08973,0.20419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6426.0,"contact_point_centroid":[0.58482,0.18184,0.19216],"force_p95":0.07945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20469,"mean_force":0.05199,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58972,0.16344,0.18844]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53054,0.03078,-0.00211],"force_p95":0.14745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19335,"mean_force":0.13047,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52024,0.02985,0.0385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18956.0,"contact_point_centroid":[0.55034,0.10771,0.20665],"force_p95":0.07711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18844,"mean_force":0.05158,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55279,0.08877,0.2033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7347.0,"contact_point_centroid":[0.5933,0.14424,0.19109],"force_p95":0.07572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15732,"mean_force":0.04714,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58957,0.16314,0.18993]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5926.0,"contact_point_centroid":[0.52092,0.01073,0.03938],"force_p95":0.07278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14584,"mean_force":0.04448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51977,0.02981,0.03795]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51059,0.01319,0.25005]},{"body_a":"world","body_b":"grasp_target","contact_count":2064.0,"contact_point_centroid":[0.57884,0.17026,-0.00198],"force_p95":0.12622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13534,"mean_force":0.1226,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59184,0.17439,0.19804]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.523,0.02855,0.1217]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5333.0,"contact_point_centroid":[0.51921,0.04902,0.04032],"force_p95":0.08151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0837,"mean_force":0.04947,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51977,0.02981,0.03795]}],"total_contact_groups":16},"final_pose_error":0.01557,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57883,0.17026,0.02602],"final_tcp_position":[0.5977,0.17723,0.24306],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.08822,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1404.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52358,0.0271,0.20075],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1900.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52503,0.03016,0.04411],"tcp_start":[0.52358,0.0271,0.20075],"tcp_to_object_dist_end":0.01891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.03031,0.02568],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18392,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14509,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13063.0,"raw_peak_contact_force":0.19335,"tcp_end":[0.51974,0.02981,0.03792],"tcp_start":[0.51974,0.02981,0.03792],"tcp_to_object_dist_end":0.01628,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.53456,0.03054,0.1323],"object_pos_start":[0.53047,0.03035,0.0257],"object_to_goal_dist_end":0.16428,"object_to_goal_dist_start":0.18388,"object_z_max":0.13218,"peak_contact_force":0.07288,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27765.0,"raw_peak_contact_force":0.56453,"tcp_end":[0.52588,0.03006,0.14858],"tcp_start":[0.51974,0.02981,0.03792],"tcp_to_object_dist_end":0.01846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59042,0.15554,0.22197],"object_pos_start":[0.53456,0.03054,0.1323],"object_to_goal_dist_end":0.11672,"object_to_goal_dist_start":0.16428,"object_z_max":0.22194,"peak_contact_force":0.07104,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40867.0,"raw_peak_contact_force":0.20791,"subtask_id":"transport_arc","tcp_end":[0.58609,0.15346,0.24348],"tcp_start":[0.52588,0.03006,0.14858],"tcp_to_object_dist_end":0.02204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.59386,0.17554,0.11249],"object_pos_start":[0.59042,0.15554,0.22197],"object_to_goal_dist_end":0.00935,"object_to_goal_dist_start":0.11672,"object_z_max":0.22197,"peak_contact_force":0.07978,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13773.0,"raw_peak_contact_force":0.20469,"subtask_id":"release_1","tcp_end":[0.59548,0.17422,0.13645],"tcp_start":[0.58609,0.15346,0.24348],"tcp_to_object_dist_end":0.02406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57884,0.17028,0.02648],"object_pos_start":[0.59386,0.17554,0.11249],"object_to_goal_dist_end":0.08511,"object_to_goal_dist_start":0.00935,"object_z_max":0.11249,"peak_contact_force":0.12763,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2595.0,"raw_peak_contact_force":1.08822,"tcp_end":[0.58894,0.17234,0.1571],"tcp_start":[0.59548,0.17422,0.13645],"tcp_to_object_dist_end":0.13103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":600.0,"object_pos_end":[0.57883,0.17026,0.02602],"object_pos_start":[0.57884,0.17028,0.02648],"object_to_goal_dist_end":0.08556,"object_to_goal_dist_start":0.08511,"object_z_max":0.02648,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.13534,"tcp_end":[0.5977,0.17723,0.24306],"tcp_start":[0.58894,0.17234,0.1571],"tcp_to_object_dist_end":0.21797,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```