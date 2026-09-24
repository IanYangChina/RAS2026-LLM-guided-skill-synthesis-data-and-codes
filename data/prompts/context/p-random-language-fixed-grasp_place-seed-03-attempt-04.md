## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1155 | 0.43 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.2522 | 0.47 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.1848 | 0.48 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1851 | 0.48 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0374 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.115) — your mutation base

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

- **Composite score**: -0.115
- **task_score** (E): 0.432
- **fitness_score**: 0.440  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1613 |
| descend_1 | 1.00 | 1.00 | 0.1006 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 0.00 | 1.00 | 0.0000 |
| transport_1 | 0.33 | 1.00 | 0.2935 |
| descend_2 | 1.00 | 1.00 | 0.0111 |
| release_1 | 1.00 | 1.00 | 0.0214 |
| retract_1 | 1.00 | 1.00 | 0.0533 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.145) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.002, 0.145)→(0.506, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.500, 0.002, 0.039)→(0.500, 0.002, 0.039) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.000 | 0.138 | 0.168 |
| lift_1 | lift | 0.00 / guard_failure | (0.500, 0.002, 0.039)→(0.500, 0.002, 0.039) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.000 | 0.247 | 0.247 |
| transport_1 | approach | 0.33 / step_budget | (0.500, 0.002, 0.039)→(0.594, 0.137, 0.278) | (0.511, 0.002, 0.026)→(0.600, 0.140, 0.250) | 0.246→0.123 | 1.00 / 27.000 | 0.099 | 0.806 |
| descend_2 | descend | 1.00 / force_exceeded | (0.594, 0.137, 0.278)→(0.595, 0.140, 0.267) | (0.600, 0.140, 0.250)→(0.600, 0.142, 0.239) | 0.123→0.112 | 1.00 / 27.333 | 112060.078 | 0.373 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.140, 0.267)→(0.591, 0.139, 0.288) | (0.600, 0.142, 0.239)→(0.588, 0.153, 0.005) | 0.112→0.143 | 1.00 / 3.333 | 0.401 | 2.021 |
| retract_1 | retract | 1.00 / step_budget | (0.591, 0.139, 0.288)→(0.621, 0.178, 0.279) | (0.588, 0.153, 0.005)→(0.593, 0.151, 0.019) | 0.143→0.130 | 1.00 / 4.000 | 0.123 | 0.484 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.517
- phase_score: 0.275
- phase_breakdown.release_1_score: 0.035
- phase_breakdown.descend_1_score: 0.846
- phase_breakdown.transport_arc_score: 0.053
- phase_breakdown.approach_1_score: 0.129
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.483

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.483
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.517
- **Median Q (composite search score)**: -0.096
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.403


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14563,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14788,"descend_1.grasp_z_offset":0.01119,"descend_2.place_force_threshold":6.15095,"descend_2.place_z_offset":0.02981,"lift_1.lift_height":0.26574,"lift_1.lift_speed":0.26579,"release_1.release_duration":0.48792,"retract_1.retract_speed":0.15776,"transport_1.arc_height":0.11332,"transport_1.transport_speed":0.42831},"optimized_scores":{"best_composite_score":-0.0961,"best_fitness_score":0.4589,"best_task_score":0.4739},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.5752,0.20018,-0.00986],"force_p95":1.57941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.11751,"mean_force":0.69193,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58604,0.15983,0.27976]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.45465,-0.026,-0.00134],"force_p95":0.52945,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74488,"mean_force":0.11468,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.44766,-0.02595,0.04263]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":405.0,"contact_point_centroid":[0.5879,0.17901,0.26639],"force_p95":0.16139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49413,"mean_force":0.11118,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58993,0.1601,0.26874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16432.0,"contact_point_centroid":[0.4838,0.04034,0.17401],"force_p95":0.11154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47666,"mean_force":0.06487,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48268,0.02145,0.17306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16447.0,"contact_point_centroid":[0.48988,0.00862,0.18171],"force_p95":0.10909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44078,"mean_force":0.06596,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48731,0.02733,0.18073]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":671.0,"contact_point_centroid":[0.58426,0.1797,0.2556],"force_p95":0.21555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31755,"mean_force":0.11765,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58847,0.16063,0.25881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":540.0,"contact_point_centroid":[0.59467,0.14264,0.26394],"force_p95":0.1411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31684,"mean_force":0.08504,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58993,0.1601,0.26874]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":779.0,"contact_point_centroid":[0.59325,0.14341,0.25455],"force_p95":0.09307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25808,"mean_force":0.06103,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58879,0.16073,0.25945]},{"body_a":"world","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.57683,0.1992,-0.00223],"force_p95":0.12454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25135,"mean_force":0.11845,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60633,0.1839,0.26671]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.45858,-0.02642,-0.00208],"force_p95":0.23999,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24187,"mean_force":0.22099,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44926,-0.02576,0.04111]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45857,-0.02637,-0.00205],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16514,"mean_force":0.12693,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44973,-0.02578,0.04156]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47986,-0.01108,0.24431]},{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45585,-0.02448,0.11605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5835.0,"contact_point_centroid":[0.45084,-0.00665,0.0426],"force_p95":0.07288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11973,"mean_force":0.04536,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44928,-0.02576,0.04113]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.45079,-0.00665,0.04259],"force_p95":0.09804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09939,"mean_force":0.06325,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44926,-0.02576,0.04111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5452.0,"contact_point_centroid":[0.44809,-0.04493,0.0434],"force_p95":0.07944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09295,"mean_force":0.04834,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44928,-0.02576,0.04113]}],"total_contact_groups":17},"final_pose_error":0.01031,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.57682,0.19918,0.01602],"final_tcp_position":[0.6242,0.20385,0.25689],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46,-0.02315,0.18722],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1808.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45417,-0.0259,0.04597],"tcp_start":[0.46,-0.02315,0.18722],"tcp_to_object_dist_end":0.02044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02612,0.02583],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3036,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1365,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13091.0,"raw_peak_contact_force":0.16514,"tcp_end":[0.44926,-0.02576,0.04111],"tcp_start":[0.44926,-0.02576,0.04111],"tcp_to_object_dist_end":0.01785,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.45848,-0.02611,0.02581],"object_pos_start":[0.45849,-0.02611,0.02584],"object_to_goal_dist_end":0.30359,"object_to_goal_dist_start":0.30358,"object_z_max":0.02584,"peak_contact_force":0.24187,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":44.0,"raw_peak_contact_force":0.24187,"tcp_end":[0.44924,-0.02576,0.04109],"tcp_start":[0.44926,-0.02576,0.04111],"tcp_to_object_dist_end":0.01785,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59058,0.16021,0.24165],"object_pos_start":[0.45848,-0.02611,0.02581],"object_to_goal_dist_end":0.14189,"object_to_goal_dist_start":0.30359,"object_z_max":0.24616,"peak_contact_force":0.1219,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32953.0,"raw_peak_contact_force":0.74488,"subtask_id":"transport_arc","tcp_end":[0.58999,0.15879,0.27413],"tcp_start":[0.44924,-0.02576,0.04109],"tcp_to_object_dist_end":0.03252,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":45.0,"n_steps_budget":1000.0,"object_pos_end":[0.59124,0.16287,0.23024],"object_pos_start":[0.59058,0.16021,0.24165],"object_to_goal_dist_end":0.13059,"object_to_goal_dist_start":0.14189,"object_z_max":0.24165,"peak_contact_force":167951.73011,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":945.0,"raw_peak_contact_force":0.49413,"subtask_id":"release_1","tcp_end":[0.59019,0.16106,0.26304],"tcp_start":[0.58999,0.15879,0.27413],"tcp_to_object_dist_end":0.03287,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57578,0.19671,-0.00047],"object_pos_start":[0.59124,0.16287,0.23024],"object_to_goal_dist_end":0.12735,"object_to_goal_dist_start":0.13059,"object_z_max":0.23024,"peak_contact_force":0.27394,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1556.0,"raw_peak_contact_force":2.11751,"tcp_end":[0.58601,0.15983,0.284],"tcp_start":[0.59019,0.16106,0.26304],"tcp_to_object_dist_end":0.28704,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":448.0,"n_steps_budget":600.0,"object_pos_end":[0.57682,0.19918,0.01602],"object_pos_start":[0.57578,0.19671,-0.00047],"object_to_goal_dist_end":0.11201,"object_to_goal_dist_start":0.12735,"object_z_max":0.01677,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1792.0,"raw_peak_contact_force":0.25135,"tcp_end":[0.6242,0.20385,0.25689],"tcp_start":[0.58601,0.15983,0.284],"tcp_to_object_dist_end":0.24553,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0283,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07916,"descend_1.grasp_z_offset":0.01021,"descend_2.place_force_threshold":14.08738,"descend_2.place_z_offset":0.02096,"lift_1.lift_height":0.09469,"lift_1.lift_speed":0.10091,"release_1.release_duration":0.32955,"retract_1.retract_speed":0.45052,"transport_1.arc_height":0.06915,"transport_1.transport_speed":0.42983},"optimized_scores":{"best_composite_score":-0.17794,"best_fitness_score":0.37706,"best_task_score":0.30542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.60849,0.11487,-0.01396],"force_p95":1.88107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25476,"mean_force":0.92862,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61363,0.12035,0.30853]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.5397,0.00075,-0.00127],"force_p95":0.46615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84614,"mean_force":0.10799,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53099,0.00059,0.03889]},{"body_a":"world","body_b":"grasp_target","contact_count":1595.0,"contact_point_centroid":[0.60194,0.11321,-0.00261],"force_p95":0.34093,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66721,"mean_force":0.14169,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63051,0.14078,0.32072]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14564.0,"contact_point_centroid":[0.55537,0.05222,0.18172],"force_p95":0.10665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50511,"mean_force":0.07002,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55313,0.03319,0.1793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15427.0,"contact_point_centroid":[0.55462,0.01155,0.17228],"force_p95":0.1087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44798,"mean_force":0.06737,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55083,0.03015,0.17059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.61511,0.13759,0.30292],"force_p95":0.09586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31547,"mean_force":0.06484,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61595,0.11862,0.30238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.62175,0.1004,0.30191],"force_p95":0.10532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29109,"mean_force":0.072,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61595,0.11862,0.30238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":894.0,"contact_point_centroid":[0.6216,0.1027,0.28776],"force_p95":0.08835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28424,"mean_force":0.05861,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.616,0.12098,0.28863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":942.0,"contact_point_centroid":[0.61453,0.13992,0.2886],"force_p95":0.08561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28296,"mean_force":0.05601,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61602,0.12099,0.28868]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5443,0.0012,-0.00205],"force_p95":0.24093,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24151,"mean_force":0.22464,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53273,0.0009,0.03737]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13027,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1454,"mean_force":0.1254,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53324,0.00091,0.03797]},{"body_a":"world","body_b":"grasp_target","contact_count":2436.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51721,0.00048,0.20724]},{"body_a":"world","body_b":"grasp_target","contact_count":900.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53626,0.00097,0.0795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18.0,"contact_point_centroid":[0.53301,0.02014,0.0395],"force_p95":0.08715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10008,"mean_force":0.06766,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53273,0.0009,0.03737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53303,0.02019,0.03952],"force_p95":0.07436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09566,"mean_force":0.04969,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53275,0.0009,0.03739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22.0,"contact_point_centroid":[0.5325,-0.01811,0.03906],"force_p95":0.0903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09263,"mean_force":0.05882,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53273,0.0009,0.03737]}],"total_contact_groups":17},"final_pose_error":0.01236,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.6005,0.11141,0.02602],"final_tcp_position":[0.64299,0.15464,0.33017],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":276.77276,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2436.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53699,0.00098,0.11589],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":900.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53807,0.00101,0.0438],"tcp_start":[0.53699,0.00098,0.11589],"tcp_to_object_dist_end":0.01884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00113,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25026,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13012,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13525.0,"raw_peak_contact_force":0.1454,"tcp_end":[0.53273,0.0009,0.03737],"tcp_start":[0.53273,0.0009,0.03737],"tcp_to_object_dist_end":0.01624,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.5442,0.00112,0.02586],"object_pos_start":[0.54421,0.00113,0.02589],"object_to_goal_dist_end":0.25028,"object_to_goal_dist_start":0.25025,"object_z_max":0.02589,"peak_contact_force":0.24151,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":44.0,"raw_peak_contact_force":0.24151,"tcp_end":[0.53271,0.0009,0.03734],"tcp_start":[0.53273,0.0009,0.03737],"tcp_to_object_dist_end":0.01624,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62385,0.11812,0.28644],"object_pos_start":[0.5442,0.00112,0.02586],"object_to_goal_dist_end":0.10607,"object_to_goal_dist_start":0.25028,"object_z_max":0.28632,"peak_contact_force":0.08427,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30082.0,"raw_peak_contact_force":0.84614,"subtask_id":"transport_arc","tcp_end":[0.61511,0.11601,0.31228],"tcp_start":[0.53271,0.0009,0.03734],"tcp_to_object_dist_end":0.02736,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":88.0,"n_steps_budget":1000.0,"object_pos_end":[0.62395,0.12314,0.26531],"object_pos_start":[0.62385,0.11812,0.28644],"object_to_goal_dist_end":0.08537,"object_to_goal_dist_start":0.10607,"object_z_max":0.28645,"peak_contact_force":276.77276,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2640.0,"raw_peak_contact_force":0.31547,"subtask_id":"release_1","tcp_end":[0.61729,0.12115,0.29253],"tcp_start":[0.61511,0.11601,0.31228],"tcp_to_object_dist_end":0.02809,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61368,0.12337,0.00123],"object_pos_start":[0.62395,0.12314,0.26531],"object_to_goal_dist_end":0.19598,"object_to_goal_dist_start":0.08537,"object_z_max":0.26531,"peak_contact_force":0.69716,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1921.0,"raw_peak_contact_force":2.25476,"tcp_end":[0.61361,0.12035,0.31282],"tcp_start":[0.61729,0.12115,0.29253],"tcp_to_object_dist_end":0.31161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":475.0,"n_steps_budget":600.0,"object_pos_end":[0.6005,0.11141,0.02602],"object_pos_start":[0.61368,0.12337,0.00123],"object_to_goal_dist_end":0.17791,"object_to_goal_dist_start":0.19598,"object_z_max":0.03229,"peak_contact_force":0.12267,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1595.0,"raw_peak_contact_force":0.66721,"tcp_end":[0.64299,0.15464,0.33017],"tcp_start":[0.61361,0.12035,0.31282],"tcp_to_object_dist_end":0.31014,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9703,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09509,"descend_1.grasp_z_offset":0.01001,"descend_2.place_force_threshold":7.45817,"descend_2.place_z_offset":0.0157,"lift_1.lift_height":0.14903,"lift_1.lift_speed":0.12722,"release_1.release_duration":0.32297,"retract_1.retract_speed":0.36381,"transport_1.arc_height":0.07536,"transport_1.transport_speed":0.31897},"optimized_scores":{"best_composite_score":-0.07239,"best_fitness_score":0.48261,"best_task_score":0.51712},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.57424,0.13669,-0.01386],"force_p95":1.63825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69127,"mean_force":0.89858,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57194,0.13718,0.26091]},{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.5249,0.02763,-0.00121],"force_p95":0.37184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82624,"mean_force":0.13681,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51723,0.02878,0.03984]},{"body_a":"world","body_b":"grasp_target","contact_count":1378.0,"contact_point_centroid":[0.59689,0.14162,-0.00235],"force_p95":0.20189,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53292,"mean_force":0.13327,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58595,0.15977,0.25532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14293.0,"contact_point_centroid":[0.53016,0.07186,0.15033],"force_p95":0.10608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50485,"mean_force":0.07094,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52863,0.05271,0.14785]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16635.0,"contact_point_centroid":[0.53164,0.03254,0.14538],"force_p95":0.09991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39944,"mean_force":0.06232,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52764,0.05098,0.14415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":888.0,"contact_point_centroid":[0.57389,0.15721,0.24337],"force_p95":0.08894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32665,"mean_force":0.05976,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57487,0.13802,0.2425]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.57551,0.15699,0.24795],"force_p95":0.21556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30821,"mean_force":0.09704,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57644,0.13791,0.24695]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.53062,0.03087,-0.00215],"force_p95":0.25398,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25742,"mean_force":0.22978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51944,0.02976,0.03785]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.58293,0.12021,0.24625],"force_p95":0.14765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24338,"mean_force":0.07266,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57644,0.13791,0.24695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1009.0,"contact_point_centroid":[0.58142,0.12013,0.24165],"force_p95":0.08569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24273,"mean_force":0.05337,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57487,0.13802,0.24249]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53055,0.03081,-0.00211],"force_p95":0.14861,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19461,"mean_force":0.1307,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51994,0.02979,0.03843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6394.0,"contact_point_centroid":[0.5199,0.01067,0.03894],"force_p95":0.06927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14604,"mean_force":0.04135,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51946,0.02976,0.03788]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51083,0.01387,0.2157]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52312,0.02908,0.08771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22.0,"contact_point_centroid":[0.51986,0.01073,0.03894],"force_p95":0.09502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09959,"mean_force":0.05937,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51944,0.02976,0.03785]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18.0,"contact_point_centroid":[0.51902,0.04897,0.0403],"force_p95":0.09001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09491,"mean_force":0.06818,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51944,0.02976,0.03785]}],"total_contact_groups":17},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60063,0.14242,0.01602],"final_tcp_position":[0.59604,0.17423,0.25096],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52412,0.02823,0.13226],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52471,0.0301,0.04403],"tcp_start":[0.52412,0.02823,0.13226],"tcp_to_object_dist_end":0.01893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.0303,0.02567],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18393,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14705,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13533.0,"raw_peak_contact_force":0.19461,"tcp_end":[0.51944,0.02976,0.03785],"tcp_start":[0.51944,0.02976,0.03785],"tcp_to_object_dist_end":0.01644,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.53046,0.03032,0.02566],"object_pos_start":[0.53046,0.03032,0.02569],"object_to_goal_dist_end":0.18393,"object_to_goal_dist_start":0.18391,"object_z_max":0.02569,"peak_contact_force":0.25742,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":44.0,"raw_peak_contact_force":0.25742,"tcp_end":[0.51942,0.02976,0.03782],"tcp_start":[0.51944,0.02976,0.03785],"tcp_to_object_dist_end":0.01644,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58556,0.14052,0.2221],"object_pos_start":[0.53046,0.03032,0.02566],"object_to_goal_dist_end":0.12125,"object_to_goal_dist_start":0.18393,"object_z_max":0.22206,"peak_contact_force":0.09027,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31054.0,"raw_peak_contact_force":0.82624,"subtask_id":"transport_arc","tcp_end":[0.57641,0.13752,0.24729],"tcp_start":[0.51942,0.02976,0.03782],"tcp_to_object_dist_end":0.02697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.58586,0.14134,0.22071],"object_pos_start":[0.58556,0.14052,0.2221],"object_to_goal_dist_end":0.11965,"object_to_goal_dist_start":0.12125,"object_z_max":0.2221,"peak_contact_force":167951.73011,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":240.0,"raw_peak_contact_force":0.30821,"subtask_id":"release_1","tcp_end":[0.57645,0.13828,0.2461],"tcp_start":[0.57641,0.13752,0.24729],"tcp_to_object_dist_end":0.02724,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57584,0.13758,0.01337],"object_pos_start":[0.58586,0.14134,0.22071],"object_to_goal_dist_end":0.10637,"object_to_goal_dist_start":0.11965,"object_z_max":0.22071,"peak_contact_force":0.23231,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1984.0,"raw_peak_contact_force":1.69127,"tcp_end":[0.5719,0.13718,0.26762],"tcp_start":[0.57645,0.13828,0.2461],"tcp_to_object_dist_end":0.25428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":389.0,"n_steps_budget":600.0,"object_pos_end":[0.60063,0.14242,0.01602],"object_pos_start":[0.57584,0.13758,0.01337],"object_to_goal_dist_end":0.09892,"object_to_goal_dist_start":0.10637,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1378.0,"raw_peak_contact_force":0.53292,"tcp_end":[0.59604,0.17423,0.25096],"tcp_start":[0.5719,0.13718,0.26762],"tcp_to_object_dist_end":0.23713,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```