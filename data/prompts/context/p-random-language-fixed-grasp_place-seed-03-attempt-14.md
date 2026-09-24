## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.2414 | 0.64 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | 0.0283 | 0.47 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0794 | 0.47 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0768 | 0.47 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.3400 | 0.83 | ✅ accepted |

**Proposal policy**: task_score is 0.64 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.241) — your mutation base

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

- **Composite score**: 0.241
- **task_score** (E): 0.635
- **fitness_score**: 0.791  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1728 |
| descend_1 | 1.00 | 1.00 | 0.0890 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 0.67 | 1.00 | 0.1438 |
| transport_1 | 0.67 | 1.00 | 0.1922 |
| descend_2 | 1.00 | 1.00 | 0.0909 |
| final_hold | 1.00 | 1.00 | 0.0164 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.001, 0.133) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.001, 0.133)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.500, 0.002, 0.039)→(0.500, 0.002, 0.039) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.138 | 0.172 |
| lift_1 | lift | 0.67 / step_budget | (0.500, 0.002, 0.039)→(0.506, 0.002, 0.182) | (0.511, 0.002, 0.026)→(0.514, 0.002, 0.164) | 0.246→0.218 | 1.00 / 42.333 | 0.074 | 0.541 |
| transport_1 | approach | 0.67 / step_budget | (0.506, 0.002, 0.182)→(0.607, 0.159, 0.204) | (0.514, 0.002, 0.164)→(0.604, 0.160, 0.178) | 0.218→0.054 | 1.00 / 30.333 | 0.093 | 0.328 |
| descend_2 | descend | 1.00 / step_budget | (0.607, 0.159, 0.204)→(0.620, 0.178, 0.118) | (0.604, 0.160, 0.178)→(0.615, 0.179, 0.089) | 0.054→0.051 | 1.00 / 29.000 | 0.105 | 0.310 |
| final_hold | grasp | 1.00 / step_budget | (0.620, 0.178, 0.118)→(0.612, 0.176, 0.103) | (0.615, 0.179, 0.089)→(0.609, 0.179, 0.071) | 0.051→0.069 | 1.00 / 22.667 | 0.207 | 0.338 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.709
- phase_score: 0.513
- phase_breakdown.release_1_score: 0.823
- phase_breakdown.descend_1_score: 0.855
- phase_breakdown.transport_arc_score: 0.277
- phase_breakdown.approach_1_score: 0.029
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.828

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.828
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.709
- **Median Q (composite search score)**: 0.254
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92701,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05309,"descend_1.grasp_z_offset":0.0103,"descend_2.place_z_offset":-0.0375,"final_hold.hold_duration":0.44379,"lift_1.lift_height":0.13329,"transport_1.approach_z_offset":0.05573,"transport_1.arc_height":0.05032,"transport_1.transport_speed":0.28232},"optimized_scores":{"best_composite_score":0.19215,"best_fitness_score":0.74215,"best_task_score":0.53897},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.45609,-0.02538,-0.00112],"force_p95":0.27525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.487,"mean_force":0.0558,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44766,-0.02559,0.04211]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2863.0,"contact_point_centroid":[0.61161,0.21612,0.06219],"force_p95":0.17388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41041,"mean_force":0.10497,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.6153,0.20064,0.0661]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.60178,0.20152,-0.00452],"force_p95":0.38892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39484,"mean_force":0.29775,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.61414,0.20026,0.06413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18379.0,"contact_point_centroid":[0.51441,0.03754,0.18678],"force_p95":0.08533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37637,"mean_force":0.05511,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5133,0.05667,0.18562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4153.0,"contact_point_centroid":[0.616,0.18665,0.05901],"force_p95":0.11765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37515,"mean_force":0.07021,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.61491,0.20051,0.06544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20533.0,"contact_point_centroid":[0.51271,0.07709,0.1882],"force_p95":0.0708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3473,"mean_force":0.04865,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51446,0.05823,0.18637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5116.0,"contact_point_centroid":[0.60048,0.19836,0.13039],"force_p95":0.13025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31043,"mean_force":0.08847,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6045,0.18004,0.13199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14418.0,"contact_point_centroid":[0.45025,-0.00658,0.09478],"force_p95":0.0702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29872,"mean_force":0.04712,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44955,-0.02573,0.09356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.60914,0.16309,0.12503],"force_p95":0.12743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28629,"mean_force":0.0889,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60516,0.18092,0.12975]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13618.0,"contact_point_centroid":[0.44849,-0.04489,0.09759],"force_p95":0.07582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28523,"mean_force":0.04928,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44972,-0.02573,0.09568]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45858,-0.02637,-0.00207],"force_p95":0.14036,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17644,"mean_force":0.12799,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44928,-0.02563,0.04065]},{"body_a":"world","body_b":"grasp_target","contact_count":2508.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47776,-0.01204,0.19603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5828.0,"contact_point_centroid":[0.4504,-0.00652,0.04169],"force_p95":0.07194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13223,"mean_force":0.04542,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44883,-0.02562,0.04022]},{"body_a":"world","body_b":"grasp_target","contact_count":672.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45439,-0.02507,0.06883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5308.0,"contact_point_centroid":[0.44724,-0.04478,0.04268],"force_p95":0.07971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08534,"mean_force":0.04953,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44883,-0.02562,0.04022]}],"total_contact_groups":15},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60653,0.20647,0.02448],"final_tcp_position":[0.622,0.20262,0.07746],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.487,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2508.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45706,-0.02446,0.09263],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":168.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":672.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45372,-0.02575,0.04504],"tcp_start":[0.45706,-0.02446,0.09263],"tcp_to_object_dist_end":0.01964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02607,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30356,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13923,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12940.0,"raw_peak_contact_force":0.17644,"tcp_end":[0.44881,-0.02562,0.0402],"tcp_start":[0.44881,-0.02562,0.0402],"tcp_to_object_dist_end":0.01737,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.46251,-0.02641,0.12881],"object_pos_start":[0.4585,-0.0261,0.0258],"object_to_goal_dist_end":0.28872,"object_to_goal_dist_start":0.30358,"object_z_max":0.1287,"peak_contact_force":0.06773,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28167.0,"raw_peak_contact_force":0.487,"tcp_end":[0.45415,-0.02594,0.14763],"tcp_start":[0.44881,-0.02562,0.0402],"tcp_to_object_dist_end":0.0206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58584,0.15931,0.1639],"object_pos_start":[0.46251,-0.02641,0.12881],"object_to_goal_dist_end":0.08265,"object_to_goal_dist_start":0.28872,"object_z_max":0.18022,"peak_contact_force":0.10459,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38912.0,"raw_peak_contact_force":0.37637,"subtask_id":"transport_arc","tcp_end":[0.58987,0.15865,0.19063],"tcp_start":[0.45415,-0.02594,0.14763],"tcp_to_object_dist_end":0.02704,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.61381,0.20362,0.04254],"object_pos_start":[0.58584,0.15931,0.1639],"object_to_goal_dist_end":0.07356,"object_to_goal_dist_start":0.08265,"object_z_max":0.1639,"peak_contact_force":0.12814,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10393.0,"raw_peak_contact_force":0.31043,"subtask_id":"release_1","tcp_end":[0.622,0.20262,0.07746],"tcp_start":[0.58987,0.15865,0.19063],"tcp_to_object_dist_end":0.03588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60653,0.20647,0.02448],"object_pos_start":[0.61381,0.20362,0.04254],"object_to_goal_dist_end":0.09271,"object_to_goal_dist_start":0.07356,"object_z_max":0.04254,"peak_contact_force":0.39496,"phase_name":"final_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7808.0,"raw_peak_contact_force":0.41041,"tcp_end":[0.61357,0.20008,0.06318],"tcp_start":[0.622,0.20262,0.07746],"tcp_to_object_dist_end":0.03986,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06399,"descend_1.grasp_z_offset":0.01005,"descend_2.place_z_offset":-0.02311,"final_hold.hold_duration":0.42068,"lift_1.lift_height":0.1892,"transport_1.approach_z_offset":0.04181,"transport_1.arc_height":0.11895,"transport_1.transport_speed":0.22412},"optimized_scores":{"best_composite_score":0.25353,"best_fitness_score":0.80353,"best_task_score":0.65819},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.54111,0.00103,-0.00112],"force_p95":0.41842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5732,"mean_force":0.08572,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53117,0.00086,0.03878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2884.0,"contact_point_centroid":[0.63342,0.16723,0.21225],"force_p95":0.10459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35973,"mean_force":0.07143,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63755,0.14871,0.212]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18724.0,"contact_point_centroid":[0.53412,0.02014,0.11989],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33869,"mean_force":0.05365,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53404,0.00093,0.11772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20484.0,"contact_point_centroid":[0.57881,0.03995,0.26204],"force_p95":0.07701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3372,"mean_force":0.04978,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57725,0.05901,0.26065]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19347.0,"contact_point_centroid":[0.5745,0.07643,0.26272],"force_p95":0.07721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33061,"mean_force":0.05145,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57615,0.05743,0.2606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5861.0,"contact_point_centroid":[0.63241,0.17168,0.16179],"force_p95":0.10439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31284,"mean_force":0.07196,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.63583,0.15305,0.16253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21536.0,"contact_point_centroid":[0.53379,-0.01813,0.11794],"force_p95":0.07006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31232,"mean_force":0.04752,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53394,0.00092,0.1162]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6664.0,"contact_point_centroid":[0.63904,0.1348,0.15937],"force_p95":0.0917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28032,"mean_force":0.06473,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.63578,0.15304,0.16242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3296.0,"contact_point_centroid":[0.64017,0.13013,0.21003],"force_p95":0.09828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26298,"mean_force":0.06458,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63755,0.14871,0.212]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13037,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14549,"mean_force":0.12541,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53303,0.0009,0.03768]},{"body_a":"world","body_b":"grasp_target","contact_count":2616.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51729,0.00048,0.19949]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53628,0.00097,0.0718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53286,0.02018,0.03931],"force_p95":0.07431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09571,"mean_force":0.04969,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53254,0.00089,0.0371]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6429.0,"contact_point_centroid":[0.53235,-0.01817,0.03887],"force_p95":0.06286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08823,"mean_force":0.04105,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53254,0.00089,0.0371]}],"total_contact_groups":14},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63374,0.1542,0.13004],"final_tcp_position":[0.64162,0.15442,0.17505],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.5732,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2616.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53708,0.00098,0.10065],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":744.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53786,0.001,0.04349],"tcp_start":[0.53708,0.00098,0.10065],"tcp_to_object_dist_end":0.01862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00112,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25026,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13022,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13525.0,"raw_peak_contact_force":0.14549,"tcp_end":[0.53251,0.00089,0.03707],"tcp_start":[0.53251,0.00089,0.03707],"tcp_to_object_dist_end":0.01618,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54794,0.00114,0.18089],"object_pos_start":[0.5442,0.00112,0.02589],"object_to_goal_dist_end":0.18621,"object_to_goal_dist_start":0.25026,"object_z_max":0.18071,"peak_contact_force":0.07433,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40403.0,"raw_peak_contact_force":0.5732,"tcp_end":[0.53988,0.00104,0.19834],"tcp_start":[0.53251,0.00089,0.03707],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63171,0.14424,0.22351],"object_pos_start":[0.54794,0.00114,0.18089],"object_to_goal_dist_end":0.03866,"object_to_goal_dist_start":0.18621,"object_z_max":0.26488,"peak_contact_force":0.09251,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39831.0,"raw_peak_contact_force":0.3372,"subtask_id":"transport_arc","tcp_end":[0.63553,0.14384,0.24948],"tcp_start":[0.53988,0.00104,0.19834],"tcp_to_object_dist_end":0.02626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.63822,0.15531,0.14816],"object_pos_start":[0.63171,0.14424,0.22351],"object_to_goal_dist_end":0.04405,"object_to_goal_dist_start":0.03866,"object_z_max":0.22351,"peak_contact_force":0.09359,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6180.0,"raw_peak_contact_force":0.35973,"subtask_id":"release_1","tcp_end":[0.64162,0.15442,0.17505],"tcp_start":[0.63553,0.14384,0.24948],"tcp_to_object_dist_end":0.02712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63374,0.1542,0.13004],"object_pos_start":[0.63822,0.15531,0.14816],"object_to_goal_dist_end":0.06274,"object_to_goal_dist_start":0.04405,"object_z_max":0.14816,"peak_contact_force":0.11395,"phase_name":"final_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12525.0,"raw_peak_contact_force":0.31284,"tcp_end":[0.63468,0.15276,0.16008],"tcp_start":[0.64162,0.15442,0.17505],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02941,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17086,"descend_1.grasp_z_offset":0.01029,"descend_2.place_z_offset":-0.01578,"final_hold.hold_duration":0.31475,"lift_1.lift_height":0.26643,"transport_1.approach_z_offset":0.05686,"transport_1.arc_height":0.06668,"transport_1.transport_speed":0.24202},"optimized_scores":{"best_composite_score":0.27838,"best_fitness_score":0.82838,"best_task_score":0.70887},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.52722,0.02937,-0.00119],"force_p95":0.38701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5615,"mean_force":0.07937,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51827,0.0297,0.04007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18603.0,"contact_point_centroid":[0.51858,0.04888,0.12132],"force_p95":0.07817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33615,"mean_force":0.0538,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51931,0.02972,0.11888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21243.0,"contact_point_centroid":[0.51999,0.01066,0.11859],"force_p95":0.07346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32091,"mean_force":0.0481,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51923,0.02972,0.11714]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6452.0,"contact_point_centroid":[0.58442,0.19289,0.0899],"force_p95":0.09467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29034,"mean_force":0.06596,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.58922,0.17454,0.08902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20615.0,"contact_point_centroid":[0.55971,0.08034,0.22653],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26917,"mean_force":0.04646,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5571,0.0993,0.22501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7822.0,"contact_point_centroid":[0.59247,0.15612,0.08707],"force_p95":0.083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26085,"mean_force":0.05613,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.58914,0.17452,0.08889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3186.0,"contact_point_centroid":[0.59045,0.19355,0.13782],"force_p95":0.09678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26056,"mean_force":0.06596,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59501,0.17508,0.13602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17961.0,"contact_point_centroid":[0.55483,0.11929,0.22824],"force_p95":0.07739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23367,"mean_force":0.05151,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55768,0.10041,0.22513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3785.0,"contact_point_centroid":[0.59911,0.15668,0.13507],"force_p95":0.08684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23211,"mean_force":0.05482,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59501,0.17508,0.13603]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53054,0.03078,-0.00211],"force_p95":0.14743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19329,"mean_force":0.13048,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52027,0.02984,0.03882]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5869.0,"contact_point_centroid":[0.52105,0.01072,0.03975],"force_p95":0.07289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14626,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51979,0.02981,0.03827]},{"body_a":"world","body_b":"grasp_target","contact_count":1340.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51054,0.0131,0.25299]},{"body_a":"world","body_b":"grasp_target","contact_count":1972.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52294,0.02847,0.12485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.51923,0.04902,0.04063],"force_p95":0.08152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08357,"mean_force":0.04948,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51979,0.02981,0.03827]}],"total_contact_groups":14},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58617,0.17544,0.05892],"final_tcp_position":[0.59604,0.17648,0.10032],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.5615,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1340.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52348,0.02695,0.20663],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1972.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52505,0.03015,0.04444],"tcp_start":[0.52348,0.02695,0.20663],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.03029,0.02568],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18394,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14494,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13005.0,"raw_peak_contact_force":0.19329,"tcp_end":[0.51977,0.02981,0.03824],"tcp_start":[0.51977,0.02981,0.03824],"tcp_to_object_dist_end":0.01651,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53086,0.03061,0.18181],"object_pos_start":[0.53047,0.03034,0.0257],"object_to_goal_dist_end":0.17979,"object_to_goal_dist_start":0.18389,"object_z_max":0.18162,"peak_contact_force":0.08036,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39994.0,"raw_peak_contact_force":0.5615,"tcp_end":[0.52329,0.02992,0.20074],"tcp_start":[0.51977,0.02981,0.03824],"tcp_to_object_dist_end":0.0204,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":927.0,"n_steps_budget":1000.0,"object_pos_end":[0.59412,0.17547,0.14755],"object_pos_start":[0.53086,0.03061,0.18181],"object_to_goal_dist_end":0.04027,"object_to_goal_dist_start":0.17979,"object_z_max":0.22153,"peak_contact_force":0.08052,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38576.0,"raw_peak_contact_force":0.26917,"subtask_id":"transport_arc","tcp_end":[0.59609,0.17432,0.1719],"tcp_start":[0.52329,0.02992,0.20074],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.59381,0.17781,0.07497],"object_pos_start":[0.59412,0.17547,0.14755],"object_to_goal_dist_end":0.03402,"object_to_goal_dist_start":0.04027,"object_z_max":0.14755,"peak_contact_force":0.09461,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6971.0,"raw_peak_contact_force":0.26056,"subtask_id":"release_1","tcp_end":[0.59604,0.17648,0.10032],"tcp_start":[0.59609,0.17432,0.1719],"tcp_to_object_dist_end":0.02548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58617,0.17544,0.05892],"object_pos_start":[0.59381,0.17781,0.07497],"object_to_goal_dist_end":0.05161,"object_to_goal_dist_start":0.03402,"object_z_max":0.07497,"peak_contact_force":0.1121,"phase_name":"final_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14274.0,"raw_peak_contact_force":0.29034,"tcp_end":[0.5879,0.17417,0.08687],"tcp_start":[0.59604,0.17648,0.10032],"tcp_to_object_dist_end":0.02803,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```