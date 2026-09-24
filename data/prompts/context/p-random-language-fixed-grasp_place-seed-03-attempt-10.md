## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.3400 | 0.83 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0779 | 0.47 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.1362 | 0.48 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0772 | 0.47 | ❌ rejected |
| 6 | approach → descend → grasp → lift → grasp → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.2272 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.340) — your mutation base

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

- **Composite score**: 0.340
- **task_score** (E): 0.832
- **fitness_score**: 0.890  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1413 |
| descend_1 | 1.00 | 1.00 | 0.1222 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 0.67 | 1.00 | 0.1579 |
| transport_1 | 0.67 | 1.00 | 0.1898 |
| descend_2 | 1.00 | 1.00 | 0.0721 |
| final_hold | 0.33 | 1.00 | 0.0053 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.002, 0.166) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.508, 0.002, 0.166)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.038)→(0.501, 0.002, 0.038) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.000 | 0.138 | 0.171 |
| lift_1 | lift | 0.67 / step_budget | (0.501, 0.002, 0.038)→(0.506, 0.002, 0.196) | (0.511, 0.002, 0.026)→(0.513, 0.002, 0.178) | 0.246→0.220 | 1.00 / 40.667 | 0.075 | 0.551 |
| transport_1 | approach | 0.67 / step_budget | (0.506, 0.002, 0.196)→(0.602, 0.151, 0.237) | (0.513, 0.002, 0.178)→(0.598, 0.152, 0.210) | 0.220→0.084 | 1.00 / 29.667 | 0.095 | 0.347 |
| descend_2 | descend | 1.00 / step_budget | (0.602, 0.151, 0.237)→(0.620, 0.177, 0.172) | (0.598, 0.152, 0.210)→(0.608, 0.178, 0.112) | 0.084→0.045 | 1.00 / 25.000 | 0.099 | 0.815 |
| final_hold | grasp | 0.33 / guard_failure | (0.617, 0.176, 0.167)→(0.615, 0.176, 0.162) | (0.608, 0.178, 0.112)→(0.605, 0.177, 0.104) | 0.045→0.046 | 1.00 / 24.667 | 0.101 | 0.235 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.011
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.403
- phase_breakdown.release_1_score: 0.521
- phase_breakdown.descend_1_score: 0.842
- phase_breakdown.transport_arc_score: 0.153
- phase_breakdown.approach_1_score: 0.130
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.975

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.975
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.424
- **K-run variance**: 0.0143
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.343


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1338,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18944,"descend_1.grasp_z_offset":0.01,"descend_2.place_z_offset":0.03049,"final_hold.hold_duration":0.47365,"lift_1.lift_height":0.17576,"transport_1.approach_z_offset":0.03059,"transport_1.arc_height":0.12267,"transport_1.transport_speed":0.23507},"optimized_scores":{"best_composite_score":0.17113,"best_fitness_score":0.72113,"best_task_score":0.49559},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":947.0,"contact_point_centroid":[0.59236,0.20227,-0.00317],"force_p95":0.59866,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7689,"mean_force":0.17475,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61203,0.1887,0.17196]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.45606,-0.0253,-0.00112],"force_p95":0.28588,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49618,"mean_force":0.06006,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44814,-0.02571,0.04198]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17054.0,"contact_point_centroid":[0.50213,0.02076,0.25376],"force_p95":0.1021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41563,"mean_force":0.05913,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50156,0.03985,0.25284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18963.0,"contact_point_centroid":[0.5018,0.06077,0.25541],"force_p95":0.08736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33574,"mean_force":0.05266,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50311,0.04191,0.25417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2049.0,"contact_point_centroid":[0.58356,0.17403,0.23561],"force_p95":0.1325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33151,"mean_force":0.07873,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58755,0.1562,0.23868]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18482.0,"contact_point_centroid":[0.44925,-0.04488,0.1161],"force_p95":0.07454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30113,"mean_force":0.05054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44992,-0.02577,0.11406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18740.0,"contact_point_centroid":[0.45145,-0.00667,0.11628],"force_p95":0.07362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29809,"mean_force":0.0501,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44996,-0.02577,0.11467]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1449.0,"contact_point_centroid":[0.59037,0.13762,0.23497],"force_p95":0.17674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27855,"mean_force":0.11007,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58728,0.15584,0.23947]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45857,-0.02635,-0.00206],"force_p95":0.13799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17295,"mean_force":0.12728,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44984,-0.02576,0.04051]},{"body_a":"world","body_b":"grasp_target","contact_count":984.0,"contact_point_centroid":[0.45856,-0.02632,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48123,-0.01041,0.26423]},{"body_a":"world","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45709,-0.02391,0.13538]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.59226,0.20264,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.61846,0.20095,0.13751]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5836.0,"contact_point_centroid":[0.45095,-0.0066,0.04155],"force_p95":0.07262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12039,"mean_force":0.04533,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4494,-0.02574,0.04008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5625.0,"contact_point_centroid":[0.44868,-0.04492,0.04225],"force_p95":0.07633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09306,"mean_force":0.04694,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4494,-0.02574,0.04008]},{"body_a":"left_finger","body_b":"right_finger","contact_count":754.0,"contact_point_centroid":[0.6146,0.19198,0.16736],"force_p95":0.0128,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01068,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61477,0.19224,0.16498]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1945.0,"contact_point_centroid":[0.61832,0.20067,0.1399],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01034,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.61847,0.20095,0.13751]}],"total_contact_groups":16},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.59226,0.20264,0.01602],"final_tcp_position":[0.62235,0.20211,0.14542],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.7689,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":984.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46218,-0.02203,0.22736],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4543,-0.02588,0.04493],"tcp_start":[0.46218,-0.02203,0.22736],"tcp_to_object_dist_end":0.01939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02605,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30354,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13727,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13265.0,"raw_peak_contact_force":0.17295,"tcp_end":[0.44938,-0.02574,0.04006],"tcp_start":[0.44938,-0.02574,0.04006],"tcp_to_object_dist_end":0.01692,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.46199,-0.02654,0.17042],"object_pos_start":[0.45849,-0.02606,0.02582],"object_to_goal_dist_end":0.2942,"object_to_goal_dist_start":0.30355,"object_z_max":0.1703,"peak_contact_force":0.07542,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37355.0,"raw_peak_contact_force":0.49618,"tcp_end":[0.45466,-0.02592,0.19012],"tcp_start":[0.44938,-0.02574,0.04006],"tcp_to_object_dist_end":0.02103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57677,0.14737,0.23169],"object_pos_start":[0.46199,-0.02654,0.17042],"object_to_goal_dist_end":0.14273,"object_to_goal_dist_start":0.2942,"object_z_max":0.25861,"peak_contact_force":0.11216,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36017.0,"raw_peak_contact_force":0.41563,"subtask_id":"transport_arc","tcp_end":[0.58215,0.14736,0.26195],"tcp_start":[0.45466,-0.02592,0.19012],"tcp_to_object_dist_end":0.03074,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.59226,0.20264,0.01602],"object_pos_start":[0.57677,0.14737,0.23169],"object_to_goal_dist_end":0.1053,"object_to_goal_dist_start":0.14273,"object_z_max":0.23169,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5199.0,"raw_peak_contact_force":1.7689,"subtask_id":"release_1","tcp_end":[0.62235,0.20211,0.14542],"tcp_start":[0.58215,0.14736,0.26195],"tcp_to_object_dist_end":0.13285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59226,0.20264,0.01602],"object_pos_start":[0.59226,0.20264,0.01602],"object_to_goal_dist_end":0.1053,"object_to_goal_dist_start":0.1053,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"final_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3749.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61804,0.20079,0.13664],"tcp_start":[0.61804,0.20079,0.13664],"tcp_to_object_dist_end":0.12335,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01481,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09521,"descend_1.grasp_z_offset":0.01008,"descend_2.place_z_offset":0.02818,"final_hold.hold_duration":0.41784,"lift_1.lift_height":0.24351,"transport_1.approach_z_offset":0.06119,"transport_1.arc_height":0.08004,"transport_1.transport_speed":0.2061},"optimized_scores":{"best_composite_score":0.42455,"best_fitness_score":0.97455,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.54138,0.0009,-0.00112],"force_p95":0.41126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57864,"mean_force":0.07954,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53147,0.00087,0.03912]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2943.0,"contact_point_centroid":[0.6286,0.15957,0.25088],"force_p95":0.10378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43717,"mean_force":0.06559,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6325,0.14102,0.25005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20781.0,"contact_point_centroid":[0.57228,0.0329,0.27096],"force_p95":0.07623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34487,"mean_force":0.04895,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57083,0.05197,0.26934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18729.0,"contact_point_centroid":[0.53305,0.02012,0.12001],"force_p95":0.0767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33985,"mean_force":0.05366,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53298,0.00091,0.11784]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3882.0,"contact_point_centroid":[0.63212,0.16969,0.21149],"force_p95":0.08705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.332,"mean_force":0.06352,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.63592,0.15109,0.21119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19023.0,"contact_point_centroid":[0.56874,0.06968,0.27092],"force_p95":0.07676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3285,"mean_force":0.05226,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56988,0.05063,0.26848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21567.0,"contact_point_centroid":[0.53274,-0.01815,0.11808],"force_p95":0.07,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31179,"mean_force":0.04746,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5329,0.00091,0.11635]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3423.0,"contact_point_centroid":[0.63543,0.1226,0.24851],"force_p95":0.09461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30034,"mean_force":0.05804,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63262,0.14119,0.24959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4344.0,"contact_point_centroid":[0.6389,0.13253,0.20922],"force_p95":0.08049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26684,"mean_force":0.05817,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.63592,0.15109,0.2112]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13008,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14529,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53345,0.00091,0.03799]},{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51715,0.00048,0.21527]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53629,0.00097,0.08738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53319,0.02019,0.03945],"force_p95":0.07439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09568,"mean_force":0.0497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53297,0.0009,0.03742]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6430.0,"contact_point_centroid":[0.5327,-0.01817,0.03904],"force_p95":0.06279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08784,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53296,0.0009,0.03742]}],"total_contact_groups":14},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.6329,0.15185,0.17947],"final_tcp_position":[0.64039,0.15206,0.22236],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.57864,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53692,0.00098,0.1317],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1076.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53829,0.00101,0.04383],"tcp_start":[0.53692,0.00098,0.1317],"tcp_to_object_dist_end":0.0188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00113,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25026,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12994,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13526.0,"raw_peak_contact_force":0.14529,"tcp_end":[0.53294,0.0009,0.03739],"tcp_start":[0.53294,0.0009,0.03739],"tcp_to_object_dist_end":0.0161,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54535,0.0011,0.18052],"object_pos_start":[0.54421,0.00113,0.02589],"object_to_goal_dist_end":0.18766,"object_to_goal_dist_start":0.25025,"object_z_max":0.18033,"peak_contact_force":0.07228,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40442.0,"raw_peak_contact_force":0.57864,"tcp_end":[0.53742,0.001,0.19841],"tcp_start":[0.53294,0.0009,0.03739],"tcp_to_object_dist_end":0.01957,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62512,0.13219,0.2522],"object_pos_start":[0.54535,0.0011,0.18052],"object_to_goal_dist_end":0.07007,"object_to_goal_dist_start":0.18766,"object_z_max":0.27551,"peak_contact_force":0.09084,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39804.0,"raw_peak_contact_force":0.34487,"subtask_id":"transport_arc","tcp_end":[0.62697,0.13149,0.27869],"tcp_start":[0.53742,0.001,0.19841],"tcp_to_object_dist_end":0.02657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.63947,0.15334,0.19549],"object_pos_start":[0.62512,0.13219,0.2522],"object_to_goal_dist_end":0.0104,"object_to_goal_dist_start":0.07007,"object_z_max":0.2522,"peak_contact_force":0.09156,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6366.0,"raw_peak_contact_force":0.43717,"subtask_id":"release_1","tcp_end":[0.64039,0.15206,0.22236],"tcp_start":[0.62697,0.13149,0.27869],"tcp_to_object_dist_end":0.02692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6329,0.15185,0.17947],"object_pos_start":[0.63947,0.15334,0.19549],"object_to_goal_dist_end":0.01977,"object_to_goal_dist_start":0.0104,"object_z_max":0.19549,"peak_contact_force":0.0872,"phase_name":"final_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8226.0,"raw_peak_contact_force":0.332,"tcp_end":[0.63449,0.15072,0.20767],"tcp_start":[0.64039,0.15206,0.22236],"tcp_to_object_dist_end":0.02827,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85926,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10298,"descend_1.grasp_z_offset":0.01,"descend_2.place_z_offset":0.03318,"final_hold.hold_duration":0.45523,"lift_1.lift_height":0.20583,"transport_1.approach_z_offset":0.05282,"transport_1.arc_height":0.09931,"transport_1.transport_speed":0.18322},"optimized_scores":{"best_composite_score":0.42422,"best_fitness_score":0.97422,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52746,0.02942,-0.00119],"force_p95":0.39427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57914,"mean_force":0.07814,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51806,0.02968,0.03959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17852.0,"contact_point_centroid":[0.51961,0.04893,0.11982],"force_p95":0.07909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33823,"mean_force":0.05583,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5202,0.02975,0.11717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21368.0,"contact_point_centroid":[0.52089,0.01073,0.11802],"force_p95":0.07383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30316,"mean_force":0.04786,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52017,0.02975,0.11657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20576.0,"contact_point_centroid":[0.56157,0.08161,0.22868],"force_p95":0.06797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28073,"mean_force":0.04656,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55888,0.10056,0.22717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7422.0,"contact_point_centroid":[0.58813,0.19376,0.1436],"force_p95":0.08845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24949,"mean_force":0.05867,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.59239,0.17519,0.14173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18165.0,"contact_point_centroid":[0.55661,0.12073,0.23015],"force_p95":0.07598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24177,"mean_force":0.05106,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55956,0.10189,0.22704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1037.0,"contact_point_centroid":[0.59222,0.19447,0.16191],"force_p95":0.08272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23827,"mean_force":0.05882,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5961,0.1758,0.15951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8909.0,"contact_point_centroid":[0.59689,0.15683,0.14093],"force_p95":0.07284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23804,"mean_force":0.04918,"phase_index":6.0,"phase_name":"final_hold","phase_type":"grasp","tcp_position_centroid":[0.59239,0.17519,0.14172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.60076,0.15734,0.15909],"force_p95":0.07495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22158,"mean_force":0.05197,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5961,0.1758,0.15951]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53055,0.03081,-0.00211],"force_p95":0.14827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19421,"mean_force":0.13067,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51999,0.02981,0.03833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6374.0,"contact_point_centroid":[0.51997,0.01069,0.03883],"force_p95":0.06941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14553,"mean_force":0.04148,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51951,0.02978,0.03777]},{"body_a":"world","body_b":"grasp_target","contact_count":2104.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51083,0.01383,0.21954]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52312,0.02906,0.09145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.51902,0.04904,0.04026],"force_p95":0.08212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08303,"mean_force":0.04951,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51951,0.02978,0.03778]}],"total_contact_groups":14},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58984,0.17596,0.11543],"final_tcp_position":[0.59631,0.17631,0.14921],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.57914,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2104.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52412,0.02817,0.13991],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52476,0.03012,0.04393],"tcp_start":[0.52412,0.02817,0.13991],"tcp_to_object_dist_end":0.01882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.03032,0.02567],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18392,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14677,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13514.0,"raw_peak_contact_force":0.19421,"tcp_end":[0.51949,0.02978,0.03775],"tcp_start":[0.51949,0.02978,0.03775],"tcp_to_object_dist_end":0.01633,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53301,0.03061,0.18168],"object_pos_start":[0.53047,0.03033,0.02569],"object_to_goal_dist_end":0.1789,"object_to_goal_dist_start":0.1839,"object_z_max":0.18149,"peak_contact_force":0.07775,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39366.0,"raw_peak_contact_force":0.57914,"tcp_end":[0.52543,0.03002,0.20007],"tcp_start":[0.51949,0.02978,0.03775],"tcp_to_object_dist_end":0.0199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.59287,0.17622,0.14598],"object_pos_start":[0.53301,0.03061,0.18168],"object_to_goal_dist_end":0.03894,"object_to_goal_dist_start":0.1789,"object_z_max":0.22669,"peak_contact_force":0.08095,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38741.0,"raw_peak_contact_force":0.28073,"subtask_id":"transport_arc","tcp_end":[0.59677,0.17559,0.16908],"tcp_start":[0.52543,0.03002,0.20007],"tcp_to_object_dist_end":0.02344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":61.0,"n_steps_budget":1000.0,"object_pos_end":[0.59344,0.17731,0.12587],"object_pos_start":[0.59287,0.17622,0.14598],"object_to_goal_dist_end":0.01957,"object_to_goal_dist_start":0.03894,"object_z_max":0.14598,"peak_contact_force":0.08332,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2257.0,"raw_peak_contact_force":0.23827,"subtask_id":"release_1","tcp_end":[0.59631,0.17631,0.14921],"tcp_start":[0.59677,0.17559,0.16908],"tcp_to_object_dist_end":0.02353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58974,0.17602,0.11571],"object_pos_start":[0.59344,0.17731,0.12587],"object_to_goal_dist_end":0.01427,"object_to_goal_dist_start":0.01957,"object_z_max":0.12587,"peak_contact_force":0.09205,"phase_name":"final_hold","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":16331.0,"raw_peak_contact_force":0.24949,"tcp_end":[0.59197,0.17507,0.14094],"tcp_start":[0.59197,0.17507,0.14095],"tcp_to_object_dist_end":0.02535,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```