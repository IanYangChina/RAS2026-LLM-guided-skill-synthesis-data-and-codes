## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | 0.0283 | 0.47 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0794 | 0.47 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0768 | 0.47 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.3400 | 0.83 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0779 | 0.47 | ❌ rejected |

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

## Current Skill (Q=0.028) — your mutation base

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

- **Composite score**: 0.028
- **task_score** (E): 0.470
- **fitness_score**: 0.708  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1228 |
| descend_1 | 1.00 | 1.00 | 0.1403 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 0.33 | 1.00 | 0.1547 |
| transport_1 | 0.67 | 1.00 | 0.1721 |
| descend_2 | 1.00 | 1.00 | 0.0746 |
| release_1 | 1.00 | 1.00 | 0.0208 |
| retract_1 | 1.00 | 1.00 | 0.0460 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.185) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.185)→(0.506, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.045)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.141 | 0.179 |
| lift_1 | lift | 0.33 / step_budget | (0.497, 0.002, 0.035)→(0.504, 0.002, 0.190) | (0.511, 0.002, 0.026)→(0.513, 0.002, 0.173) | 0.246→0.219 | 1.00 / 37.000 | 0.084 | 0.574 |
| transport_1 | approach | 0.67 / step_budget | (0.504, 0.002, 0.190)→(0.591, 0.137, 0.228) | (0.513, 0.002, 0.173)→(0.592, 0.138, 0.204) | 0.219→0.090 | 1.00 / 42.000 | 0.072 | 0.274 |
| descend_2 | descend | 1.00 / step_budget | (0.591, 0.137, 0.228)→(0.620, 0.177, 0.176) | (0.592, 0.138, 0.204)→(0.618, 0.177, 0.147) | 0.090→0.016 | 1.00 / 32.000 | 0.082 | 0.254 |
| release_1 | release | 1.00 / step_budget | (0.620, 0.177, 0.176)→(0.614, 0.175, 0.196) | (0.618, 0.177, 0.147)→(0.611, 0.172, 0.021) | 0.016→0.118 | 1.00 / 3.333 | 0.154 | 1.491 |
| retract_1 | retract | 1.00 / step_budget | (0.614, 0.175, 0.196)→(0.621, 0.179, 0.237) | (0.611, 0.172, 0.021)→(0.607, 0.171, 0.023) | 0.118→0.117 | 1.00 / 3.333 | 0.154 | 0.171 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.561
- phase_score: 0.435
- phase_breakdown.release_1_score: 0.267
- phase_breakdown.descend_1_score: 0.856
- phase_breakdown.transport_arc_score: 0.284
- phase_breakdown.approach_1_score: 0.064
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.561
- **Median Q (composite search score)**: 0.051
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99387,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12437,"descend_1.grasp_z_offset":0.01003,"descend_2.place_z_offset":0.04042,"grasp_1.grasp_duration":0.36736,"lift_1.lift_height":0.16501,"release_1.release_duration":0.23217,"retract_1.retract_height":0.12344,"transport_1.approach_z_offset":0.07003,"transport_1.arc_height":0.06606,"transport_1.transport_speed":0.19178},"optimized_scores":{"best_composite_score":0.05149,"best_fitness_score":0.73149,"best_task_score":0.51618},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":557.0,"contact_point_centroid":[0.62334,0.19503,-0.00347],"force_p95":0.65752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5479,"mean_force":0.18545,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61814,0.2022,0.15029]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.45614,-0.02529,-0.0011],"force_p95":0.30194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51596,"mean_force":0.06053,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44481,-0.02564,0.03904]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16109.0,"contact_point_centroid":[0.44789,-0.04496,0.11012],"force_p95":0.07912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29034,"mean_force":0.05448,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44812,-0.02578,0.10734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18555.0,"contact_point_centroid":[0.44952,-0.00674,0.10878],"force_p95":0.07306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28965,"mean_force":0.04849,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4481,-0.02577,0.10701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12823.0,"contact_point_centroid":[0.57906,0.16943,0.1947],"force_p95":0.11084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25258,"mean_force":0.06833,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58299,0.15084,0.19397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14898.0,"contact_point_centroid":[0.58721,0.13329,0.19174],"force_p95":0.09945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24622,"mean_force":0.06068,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58361,0.15164,0.19326]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19785.0,"contact_point_centroid":[0.5034,0.0215,0.22578],"force_p95":0.07736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23636,"mean_force":0.05037,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50147,0.04057,0.22371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19616.0,"contact_point_centroid":[0.49756,0.05465,0.22367],"force_p95":0.07215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21325,"mean_force":0.05054,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49774,0.03561,0.2213]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02638,-0.00205],"force_p95":0.13961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17374,"mean_force":0.12673,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44715,-0.02571,0.03826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.62755,0.18913,0.14154],"force_p95":0.10254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15417,"mean_force":0.02631,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62355,0.20403,0.14784]},{"body_a":"world","body_b":"grasp_target","contact_count":1668.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47916,-0.01142,0.23238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.44695,-0.00657,0.0386],"force_p95":0.06843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12721,"mean_force":0.04133,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44599,-0.02567,0.03715]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.62337,0.19517,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12311,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62044,0.20391,0.19351]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4553,-0.02471,0.10403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4407.0,"contact_point_centroid":[0.44539,-0.04494,0.03993],"force_p95":0.07946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08946,"mean_force":0.04917,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44599,-0.02567,0.03715]}],"total_contact_groups":15},"final_pose_error":0.01426,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62337,0.19517,0.01602],"final_tcp_position":[0.62608,0.20669,0.22397],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.5479,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45902,-0.02362,0.16382],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45409,-0.0259,0.04497],"tcp_start":[0.45902,-0.02362,0.16382],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02615,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30363,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13951,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11516.0,"raw_peak_contact_force":0.17374,"subtask_id":"grasp_1","tcp_end":[0.44596,-0.02567,0.03712],"tcp_start":[0.45409,-0.0259,0.04497],"tcp_to_object_dist_end":0.01688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.4636,-0.02666,0.16128],"object_pos_start":[0.45847,-0.02615,0.02581],"object_to_goal_dist_end":0.29176,"object_to_goal_dist_start":0.30363,"object_z_max":0.16117,"peak_contact_force":0.07858,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34794.0,"raw_peak_contact_force":0.51596,"tcp_end":[0.45439,-0.026,0.1793],"tcp_start":[0.44596,-0.02567,0.03712],"tcp_to_object_dist_end":0.02025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55246,0.10513,0.21761],"object_pos_start":[0.4636,-0.02666,0.16128],"object_to_goal_dist_end":0.16544,"object_to_goal_dist_start":0.29176,"object_z_max":0.21895,"peak_contact_force":0.06749,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39401.0,"raw_peak_contact_force":0.23636,"subtask_id":"transport_arc","tcp_end":[0.54914,0.10386,0.24023],"tcp_start":[0.45439,-0.026,0.1793],"tcp_to_object_dist_end":0.02289,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":902.0,"n_steps_budget":1000.0,"object_pos_end":[0.61988,0.20249,0.11228],"object_pos_start":[0.55246,0.10513,0.21761],"object_to_goal_dist_end":0.01188,"object_to_goal_dist_start":0.16544,"object_z_max":0.21761,"peak_contact_force":0.09852,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":27721.0,"raw_peak_contact_force":0.25258,"subtask_id":"release_1","tcp_end":[0.62369,0.204,0.14815],"tcp_start":[0.54914,0.10386,0.24023],"tcp_to_object_dist_end":0.03611,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62338,0.19517,0.016],"object_pos_start":[0.61988,0.20249,0.11228],"object_to_goal_dist_end":0.09921,"object_to_goal_dist_start":0.01188,"object_z_max":0.11228,"peak_contact_force":0.12315,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":632.0,"raw_peak_contact_force":1.5479,"subtask_id":"release_1","tcp_end":[0.61759,0.202,0.16802],"tcp_start":[0.62369,0.204,0.14815],"tcp_to_object_dist_end":0.15228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.62337,0.19517,0.01602],"object_pos_start":[0.62338,0.19517,0.016],"object_to_goal_dist_end":0.09919,"object_to_goal_dist_start":0.09921,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12311,"tcp_end":[0.62608,0.20669,0.22397],"tcp_start":[0.61759,0.202,0.16802],"tcp_to_object_dist_end":0.20828,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61688,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18957,"descend_1.grasp_z_offset":0.01038,"descend_2.place_z_offset":0.03427,"grasp_1.grasp_duration":0.41114,"lift_1.lift_height":0.28367,"release_1.release_duration":0.27372,"retract_1.retract_height":0.0555,"transport_1.approach_z_offset":0.06831,"transport_1.arc_height":0.1446,"transport_1.transport_speed":0.27416},"optimized_scores":{"best_composite_score":-0.04061,"best_fitness_score":0.63939,"best_task_score":0.33105},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.62032,0.14636,-0.00804],"force_p95":1.38584,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71913,"mean_force":0.42684,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63542,0.15092,0.23974]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.54129,0.00113,-0.00113],"force_p95":0.43847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60562,"mean_force":0.08595,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52836,0.0008,0.0358]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17893.0,"contact_point_centroid":[0.53145,0.01996,0.11663],"force_p95":0.08,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3453,"mean_force":0.05643,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53012,0.00084,0.11438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17882.0,"contact_point_centroid":[0.57744,0.04055,0.26586],"force_p95":0.0857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32628,"mean_force":0.05648,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57444,0.05938,0.26494]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19271.0,"contact_point_centroid":[0.53123,-0.01819,0.11282],"force_p95":0.07716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32328,"mean_force":0.05301,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52994,0.00083,0.11083]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17208.0,"contact_point_centroid":[0.57293,0.0764,0.26571],"force_p95":0.08467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29415,"mean_force":0.05758,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57303,0.05744,0.26405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.63347,0.1703,0.22509],"force_p95":0.07056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28865,"mean_force":0.04573,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6387,0.1519,0.22423]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1194.0,"contact_point_centroid":[0.6415,0.13292,0.22302],"force_p95":0.07146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2598,"mean_force":0.04544,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63868,0.15189,0.22419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3342.0,"contact_point_centroid":[0.62876,0.16179,0.25188],"force_p95":0.07905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25601,"mean_force":0.05201,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63395,0.14344,0.25067]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3340.0,"contact_point_centroid":[0.63647,0.12447,0.25014],"force_p95":0.08243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22186,"mean_force":0.05313,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63395,0.14343,0.25069]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.63613,0.14787,-0.00362],"force_p95":0.21818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21892,"mean_force":0.16269,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63731,0.15224,0.24534]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00115,-0.00203],"force_p95":0.13138,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15363,"mean_force":0.12534,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53111,0.00086,0.03561]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51657,0.00046,0.26127]},{"body_a":"world","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53575,0.00096,0.13338]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53103,0.02013,0.03669],"force_p95":0.07644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0966,"mean_force":0.05218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52984,0.00083,0.03413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.53035,-0.0182,0.03674],"force_p95":0.06271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08748,"mean_force":0.04072,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52984,0.00083,0.03413]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62312,0.14678,0.02749],"final_tcp_position":[0.63971,0.154,0.24209],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.71913,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53542,0.00094,0.22384],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2152.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53869,0.00102,0.04456],"tcp_start":[0.53542,0.00094,0.22384],"tcp_to_object_dist_end":0.01938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.0011,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2503,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1311,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.15363,"subtask_id":"grasp_1","tcp_end":[0.52981,0.00083,0.03409],"tcp_start":[0.53869,0.00102,0.04456],"tcp_to_object_dist_end":0.01656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5442,0.00093,0.17798],"object_pos_start":[0.54419,0.0011,0.02587],"object_to_goal_dist_end":0.18859,"object_to_goal_dist_start":0.2503,"object_z_max":0.17779,"peak_contact_force":0.08241,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37308.0,"raw_peak_contact_force":0.60562,"tcp_end":[0.53484,0.00093,0.19456],"tcp_start":[0.52981,0.00083,0.03409],"tcp_to_object_dist_end":0.01904,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62692,0.13632,0.24771],"object_pos_start":[0.5442,0.00093,0.17798],"object_to_goal_dist_end":0.06409,"object_to_goal_dist_start":0.18859,"object_z_max":0.27053,"peak_contact_force":0.07289,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35090.0,"raw_peak_contact_force":0.32628,"subtask_id":"transport_arc","tcp_end":[0.62936,0.13586,0.27437],"tcp_start":[0.53484,0.00093,0.19456],"tcp_to_object_dist_end":0.02677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.63795,0.15299,0.20105],"object_pos_start":[0.62692,0.13632,0.24771],"object_to_goal_dist_end":0.01477,"object_to_goal_dist_start":0.06409,"object_z_max":0.24771,"peak_contact_force":0.07417,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6682.0,"raw_peak_contact_force":0.25601,"subtask_id":"release_1","tcp_end":[0.64029,0.15212,0.22833],"tcp_start":[0.62936,0.13586,0.27437],"tcp_to_object_dist_end":0.0274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63043,0.14996,0.02213],"object_pos_start":[0.63795,0.15299,0.20105],"object_to_goal_dist_end":0.17004,"object_to_goal_dist_start":0.01477,"object_z_max":0.20105,"peak_contact_force":0.18724,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2546.0,"raw_peak_contact_force":1.71913,"subtask_id":"release_1","tcp_end":[0.63539,0.15091,0.2476],"tcp_start":[0.64029,0.15212,0.22833],"tcp_to_object_dist_end":0.22553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":51.0,"n_steps_budget":600.0,"object_pos_end":[0.62312,0.14678,0.02749],"object_pos_start":[0.63043,0.14996,0.02213],"object_to_goal_dist_end":0.16582,"object_to_goal_dist_start":0.17004,"object_z_max":0.02942,"peak_contact_force":0.2178,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":102.0,"raw_peak_contact_force":0.21892,"tcp_end":[0.63971,0.154,0.24209],"tcp_start":[0.63539,0.15091,0.2476],"tcp_to_object_dist_end":0.21536,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83333,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13047,"descend_1.grasp_z_offset":0.0104,"descend_2.place_z_offset":0.03725,"grasp_1.grasp_duration":0.30186,"lift_1.lift_height":0.23065,"release_1.release_duration":0.31547,"retract_1.retract_height":0.15175,"transport_1.approach_z_offset":0.05875,"transport_1.arc_height":0.05047,"transport_1.transport_speed":0.2658},"optimized_scores":{"best_composite_score":0.07409,"best_fitness_score":0.75409,"best_task_score":0.56128},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":241.0,"contact_point_centroid":[0.57889,0.17021,-0.0054],"force_p95":1.09085,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.20537,"mean_force":0.2904,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58928,0.17286,0.16171]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.52758,0.02918,-0.00119],"force_p95":0.41239,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60081,"mean_force":0.08278,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51477,0.02946,0.03641]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16996.0,"contact_point_centroid":[0.51815,0.04872,0.11641],"force_p95":0.08251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34117,"mean_force":0.05895,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5175,0.02952,0.11368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20394.0,"contact_point_centroid":[0.51932,0.01059,0.11404],"force_p95":0.07777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31501,"mean_force":0.05051,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51743,0.02952,0.11244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19372.0,"contact_point_centroid":[0.5617,0.08283,0.21224],"force_p95":0.07521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25912,"mean_force":0.04845,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5581,0.1014,0.21135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1111.0,"contact_point_centroid":[0.5898,0.19288,0.15202],"force_p95":0.07737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25418,"mean_force":0.04771,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59339,0.17415,0.14819]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1202.0,"contact_point_centroid":[0.59129,0.19199,0.16557],"force_p95":0.07626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2523,"mean_force":0.05236,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59473,0.17326,0.16157]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1351.0,"contact_point_centroid":[0.59835,0.15555,0.1487],"force_p95":0.07454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24168,"mean_force":0.04095,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59339,0.17415,0.14819]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1394.0,"contact_point_centroid":[0.59972,0.15465,0.16256],"force_p95":0.07343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22257,"mean_force":0.04698,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59473,0.17325,0.16163]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15661.0,"contact_point_centroid":[0.55664,0.12046,0.21353],"force_p95":0.09166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2177,"mean_force":0.0614,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5581,0.10139,0.21081]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.0021],"force_p95":0.15271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21051,"mean_force":0.13055,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51746,0.02966,0.03601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.51735,0.01054,0.03656],"force_p95":0.06752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16967,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51621,0.02957,0.03459]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.57528,0.16967,-0.00198],"force_p95":0.14854,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1696,"mean_force":0.12259,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59207,0.17468,0.20728]},{"body_a":"world","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51073,0.01355,0.23337]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52308,0.02886,0.10548]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4214.0,"contact_point_centroid":[0.5168,0.04889,0.03739],"force_p95":0.08164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08427,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51622,0.02957,0.0346]}],"total_contact_groups":16},"final_pose_error":0.01463,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57527,0.16966,0.02602],"final_tcp_position":[0.59772,0.17727,0.24577],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.20537,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1788.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52395,0.02775,0.16729],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1504.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52493,0.03014,0.04459],"tcp_start":[0.52395,0.02775,0.16729],"tcp_to_object_dist_end":0.0194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03016,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18408,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15093,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11291.0,"raw_peak_contact_force":0.21051,"subtask_id":"grasp_1","tcp_end":[0.51618,0.02957,0.03456],"tcp_start":[0.52493,0.03014,0.04459],"tcp_to_object_dist_end":0.01684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53257,0.0305,0.17842],"object_pos_start":[0.53044,0.03016,0.02563],"object_to_goal_dist_end":0.17785,"object_to_goal_dist_start":0.18408,"object_z_max":0.17824,"peak_contact_force":0.09049,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37537.0,"raw_peak_contact_force":0.60081,"tcp_end":[0.52329,0.02977,0.19552],"tcp_start":[0.51618,0.02957,0.03456],"tcp_to_object_dist_end":0.01947,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.59578,0.17351,0.1475],"object_pos_start":[0.53257,0.0305,0.17842],"object_to_goal_dist_end":0.04015,"object_to_goal_dist_start":0.17785,"object_z_max":0.2053,"peak_contact_force":0.07702,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35033.0,"raw_peak_contact_force":0.25912,"subtask_id":"transport_arc","tcp_end":[0.59491,0.17215,0.17042],"tcp_start":[0.52329,0.02977,0.19552],"tcp_to_object_dist_end":0.02298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":61.0,"n_steps_budget":1000.0,"object_pos_end":[0.59699,0.17638,0.12894],"object_pos_start":[0.59578,0.17351,0.1475],"object_to_goal_dist_end":0.02146,"object_to_goal_dist_start":0.04015,"object_z_max":0.1475,"peak_contact_force":0.07388,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2596.0,"raw_peak_contact_force":0.2523,"subtask_id":"release_1","tcp_end":[0.59543,0.17467,0.1521],"tcp_start":[0.59491,0.17215,0.17042],"tcp_to_object_dist_end":0.02328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57864,0.17041,0.02628],"object_pos_start":[0.59699,0.17638,0.12894],"object_to_goal_dist_end":0.08534,"object_to_goal_dist_start":0.02146,"object_z_max":0.12894,"peak_contact_force":0.15278,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2703.0,"raw_peak_contact_force":1.20537,"subtask_id":"release_1","tcp_end":[0.58919,0.17284,0.17274],"tcp_start":[0.59543,0.17467,0.1521],"tcp_to_object_dist_end":0.14686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.57527,0.16966,0.02602],"object_pos_start":[0.57864,0.17041,0.02628],"object_to_goal_dist_end":0.08663,"object_to_goal_dist_start":0.08534,"object_z_max":0.02648,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.1696,"tcp_end":[0.59772,0.17727,0.24577],"tcp_start":[0.58919,0.17284,0.17274],"tcp_to_object_dist_end":0.22103,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```