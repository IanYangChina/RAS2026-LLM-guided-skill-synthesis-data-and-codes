## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4688 | 0.12 | ❌ rejected |
| 13 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6307 | 0.17 | ❌ rejected |
| 12 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5804 | 0.17 | ❌ rejected |
| 11 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5948 | 0.14 | ❌ rejected |
| 10 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4045 | 0.12 | ❌ rejected |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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

## Current Skill (Q=-0.469) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
- id: release_1
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
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
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
    speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.05
      binds_to:
      - path: generator.speed
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
  parameters:
    grasp_force:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: guards.grasp_check.threshold
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.9
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_1
  type: push
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
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
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
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
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
  parameters:
    release_time:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_force: status=consumed; consumers=guards.grasp_check.threshold (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.9
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.469
- **task_score** (E): 0.124
- **fitness_score**: 0.188  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.800

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1785 |
| descend_1 | 1.00 | 1.00 | 0.0718 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.00 | 1.00 | 0.1131 |
| transport_1 | 0.33 | 1.00 | 0.2267 |
| release_1 | 1.00 | 1.00 | 0.0251 |
| retract_1 | 0.67 | 1.00 | 0.1219 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.420, -0.010, 0.165) | (0.493, -0.015, 0.030)→(0.465, -0.017, 0.019) | 0.279→0.301 | 1.00 / 5.000 | 140.143 | 996.738 |
| descend_1 | descend | 1.00 / force_exceeded | (0.420, -0.010, 0.165)→(0.405, -0.010, 0.095) | (0.465, -0.017, 0.019)→(0.465, -0.017, 0.019) | 0.301→0.302 | 1.00 / 5.000 | 418.487 | 361.007 |
| grasp_1 | grasp | 1.00 / step_budget | (0.384, -0.010, 0.070)→(0.384, -0.010, 0.070) | (0.465, -0.017, 0.019)→(0.460, -0.017, 0.015) | 0.302→0.306 | 1.00 / 10.333 | 56028.655 | 633.325 |
| lift_1 | lift | 0.00 / step_budget | (0.384, -0.010, 0.070)→(0.420, -0.010, 0.160) | (0.460, -0.017, 0.015)→(0.462, -0.019, 0.019) | 0.306→0.304 | 1.00 / 9.333 | 134.475 | 577.840 |
| transport_1 | push | 0.33 / step_budget | (0.420, -0.010, 0.160)→(0.564, 0.112, 0.265) | (0.462, -0.019, 0.019)→(0.446, -0.019, 0.016) | 0.304→0.314 | 1.00 / 9.000 | 94246.058 | 1049.579 |
| release_1 | release | 1.00 / step_budget | (0.564, 0.112, 0.265)→(0.565, 0.116, 0.290) | (0.446, -0.019, 0.016)→(0.446, -0.019, 0.016) | 0.314→0.314 | 1.00 / 4.000 | 0.123 | 154.638 |
| retract_1 | retract | 0.67 / step_budget | (0.565, 0.116, 0.290)→(0.547, 0.092, 0.387) | (0.446, -0.019, 0.016)→(0.446, -0.019, 0.016) | 0.314→0.314 | 1.00 / 5.000 | 31.897 | 246.760 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.146
- phase_score: 0.253
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.121
- phase_breakdown.descend_1_score: 0.249
- phase_breakdown.approach_1_score: 0.004
- phase_breakdown.release_1_score: 0.077
- grasp_place_fitness: 0.197

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.197
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.146
- **Median Q (composite search score)**: -0.468
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.330


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":4.0,"average_failure_rate":0.03883,"average_mean_iterations":15.3301,"average_solve_count":103.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26972,"approach_1.speed":0.31633,"descend_1.contact_force":4.26436,"descend_1.grasp_z_offset":0.01127,"descend_1.speed":0.34277,"grasp_1.grasp_force":0.64924,"lift_1.lift_height":0.08501,"lift_1.lift_speed":0.32735,"release_1.release_time":0.2367,"retract_1.retract_height":0.1344,"retract_1.retract_speed":0.04644,"transport_1.arc_height":0.08663,"transport_1.transport_speed":0.33272},"optimized_scores":{"best_composite_score":-0.47804,"best_fitness_score":0.1791,"best_task_score":0.11459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":731.0,"contact_point_centroid":[0.61698,-0.01077,-0.0005],"force_p95":206.75261,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1460.68892,"mean_force":210.03228,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36586,-0.00904,0.09974]},{"body_a":"world","body_b":"link6","contact_count":511.0,"contact_point_centroid":[0.60019,0.00051,-0.00018],"force_p95":500.39764,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1314.50074,"mean_force":273.87438,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.3666,-0.00902,0.11966]},{"body_a":"world","body_b":"link6","contact_count":956.0,"contact_point_centroid":[0.50651,0.0668,-0.00024],"force_p95":243.96312,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":740.03576,"mean_force":220.96106,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.39718,-0.00777,0.24892]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.60734,-0.01929,-0.00027],"force_p95":528.11952,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":528.11952,"mean_force":528.11952,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.36081,-0.01317,0.09674]},{"body_a":"world","body_b":"link6","contact_count":499.0,"contact_point_centroid":[0.6171,-0.01739,-0.00025],"force_p95":209.08562,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":503.17082,"mean_force":207.19385,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.36912,-0.01854,0.11368]},{"body_a":"link5","body_b":"hand","contact_count":436.0,"contact_point_centroid":[0.39559,0.09045,0.22702],"force_p95":124.50769,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.8068,"mean_force":71.77661,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.39835,-0.01885,0.26155]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60817,-0.01925,-0.00013],"force_p95":86.61042,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.37197,"mean_force":72.38285,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.36146,-0.0132,0.09658]},{"body_a":"world","body_b":"link6","contact_count":68.0,"contact_point_centroid":[0.63843,0.07382,-0.00014],"force_p95":108.21825,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.99103,"mean_force":77.15226,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45323,0.04916,0.21367]},{"body_a":"grasp_target","body_b":"hand","contact_count":148.0,"contact_point_centroid":[0.45103,-0.03789,0.05148],"force_p95":3.22647,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.9424,"mean_force":0.72533,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36815,-0.00632,0.08883]},{"body_a":"grasp_target","body_b":"link7","contact_count":316.0,"contact_point_centroid":[0.46812,-0.03194,0.03212],"force_p95":1.01638,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.91667,"mean_force":0.18964,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36353,-0.00996,0.09389]},{"body_a":"world","body_b":"grasp_target","contact_count":3023.0,"contact_point_centroid":[0.44313,-0.02461,-0.00248],"force_p95":0.33311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01395,"mean_force":0.16729,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38372,-0.00857,0.11448]},{"body_a":"grasp_target","body_b":"link7","contact_count":301.0,"contact_point_centroid":[0.45778,-0.03507,0.0314],"force_p95":0.60021,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.22954,"mean_force":0.40189,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.34867,-0.02159,0.08549]},{"body_a":"world","body_b":"grasp_target","contact_count":2099.0,"contact_point_centroid":[0.42833,-0.02508,-0.00272],"force_p95":0.30316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49153,"mean_force":0.17538,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.36959,-0.00714,0.12418]},{"body_a":"grasp_target","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.465,-0.04127,0.03546],"force_p95":0.0569,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39154,"mean_force":0.03581,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.36146,-0.0132,0.09658]},{"body_a":"grasp_target","body_b":"hand","contact_count":133.0,"contact_point_centroid":[0.44394,-0.02285,0.0308],"force_p95":0.23838,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28879,"mean_force":0.17648,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.3441,-0.02204,0.07431]},{"body_a":"grasp_target","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.46503,-0.04153,0.0351],"force_p95":0.27699,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27699,"mean_force":0.27699,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.36081,-0.01317,0.09674]}],"total_contact_groups":27},"final_pose_error":0.14721,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.4277,-0.02472,0.01602],"final_tcp_position":[0.39623,-0.02645,0.25907],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1460.68892,"phases":[{"contact_detected":true,"contact_event_count":6.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.4329,-0.02695,0.01575],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.32315,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":205.28646,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4235.0,"raw_peak_contact_force":1460.68892,"subtask_id":"approach_1","tcp_end":[0.36081,-0.01317,0.09674],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1093,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43289,-0.02694,0.01576],"object_pos_start":[0.4329,-0.02695,0.01575],"object_to_goal_dist_end":0.32315,"object_to_goal_dist_start":0.32315,"object_z_max":0.01575,"peak_contact_force":619.89743,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":528.11952,"subtask_id":"descend_1","tcp_end":[0.36093,-0.01315,0.09697],"tcp_start":[0.36081,-0.01317,0.09674],"tcp_to_object_dist_end":0.10937,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43213,-0.02673,0.0159],"object_pos_start":[0.43289,-0.02694,0.01576],"object_to_goal_dist_end":0.32342,"object_to_goal_dist_start":0.32315,"object_z_max":0.01593,"peak_contact_force":67.38018,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4047.0,"raw_peak_contact_force":123.37197,"subtask_id":"grasp_1","tcp_end":[0.3616,-0.01325,0.09638],"tcp_start":[0.3616,-0.01324,0.09639],"tcp_to_object_dist_end":0.10785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":499.0,"n_steps_budget":600.0,"object_pos_end":[0.43201,-0.02661,0.01602],"object_pos_start":[0.43202,-0.02671,0.01593],"object_to_goal_dist_end":0.32336,"object_to_goal_dist_start":0.32346,"object_z_max":0.0161,"peak_contact_force":113.19316,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4575.0,"raw_peak_contact_force":503.17082,"tcp_end":[0.3672,-0.02384,0.11531],"tcp_start":[0.3616,-0.01325,0.09638],"tcp_to_object_dist_end":0.1186,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":541.0,"n_steps_budget":690.0,"object_pos_end":[0.4277,-0.02472,0.01602],"object_pos_start":[0.43201,-0.02661,0.01602],"object_to_goal_dist_end":0.32496,"object_to_goal_dist_start":0.32336,"object_z_max":0.01798,"peak_contact_force":0.12265,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5315.0,"raw_peak_contact_force":1314.50074,"subtask_id":"transport_arc","tcp_end":[0.45373,0.04882,0.21541],"tcp_start":[0.3672,-0.02384,0.11531],"tcp_to_object_dist_end":0.21411,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4277,-0.02472,0.01602],"object_pos_start":[0.4277,-0.02472,0.01602],"object_to_goal_dist_end":0.32496,"object_to_goal_dist_start":0.32496,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1091.0,"raw_peak_contact_force":109.99103,"subtask_id":"release_1","tcp_end":[0.45155,0.0478,0.23911],"tcp_start":[0.45373,0.04882,0.21541],"tcp_to_object_dist_end":0.23579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4277,-0.02472,0.01602],"object_pos_start":[0.4277,-0.02472,0.01602],"object_to_goal_dist_end":0.32496,"object_to_goal_dist_start":0.32496,"object_z_max":0.01602,"peak_contact_force":95.44661,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5392.0,"raw_peak_contact_force":740.03576,"tcp_end":[0.39623,-0.02645,0.25907],"tcp_start":[0.45155,0.0478,0.23911],"tcp_to_object_dist_end":0.24509,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.03261,"average_mean_iterations":13.40217,"average_solve_count":92.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23179,"approach_1.speed":0.28949,"descend_1.contact_force":4.61659,"descend_1.grasp_z_offset":-0.00791,"descend_1.speed":0.21532,"grasp_1.grasp_force":0.72332,"lift_1.lift_height":0.10263,"lift_1.lift_speed":0.21762,"release_1.release_time":0.33323,"retract_1.retract_height":0.14319,"retract_1.retract_speed":0.15665,"transport_1.arc_height":0.13984,"transport_1.transport_speed":0.26939},"optimized_scores":{"best_composite_score":-0.46778,"best_fitness_score":0.18936,"best_task_score":0.11126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":662.0,"contact_point_centroid":[0.59329,0.00872,-0.00017],"force_p95":469.15365,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1694.45548,"mean_force":277.90084,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.36394,-0.00614,0.11258]},{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.61796,-0.01276,-0.00046],"force_p95":215.35417,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1529.38611,"mean_force":212.4061,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3683,-0.0094,0.09616]},{"body_a":"world","body_b":"link5","contact_count":49.0,"contact_point_centroid":[0.54784,0.19131,-0.00027],"force_p95":603.31068,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":710.30501,"mean_force":373.69887,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54475,0.07813,0.25681]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61016,-0.02247,-0.00027],"force_p95":554.76532,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":554.76532,"mean_force":554.76532,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.36202,-0.0166,0.0926]},{"body_a":"world","body_b":"link6","contact_count":507.0,"contact_point_centroid":[0.61075,-0.01739,-0.00026],"force_p95":209.13697,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":522.57641,"mean_force":206.01581,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.36168,-0.02265,0.0927]},{"body_a":"world","body_b":"link5","contact_count":52.0,"contact_point_centroid":[0.55374,0.17964,-0.00021],"force_p95":124.9688,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.60664,"mean_force":68.5202,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6011,0.14779,0.2849]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61106,-0.02315,-0.00013],"force_p95":80.92406,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.0854,"mean_force":71.45553,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.36272,-0.01712,0.09232]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43991,-0.02022,0.04304],"force_p95":3.52063,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.94506,"mean_force":1.5723,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37356,-0.00448,0.05501]},{"body_a":"grasp_target","body_b":"hand","contact_count":312.0,"contact_point_centroid":[0.44124,-0.03338,0.0312],"force_p95":0.57243,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.78508,"mean_force":0.38257,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.33902,-0.02478,0.06767]},{"body_a":"world","body_b":"grasp_target","contact_count":3922.0,"contact_point_centroid":[0.42223,-0.0258,-0.00212],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23158,"mean_force":0.1374,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38215,-0.00872,0.10824]},{"body_a":"grasp_target","body_b":"link7","contact_count":259.0,"contact_point_centroid":[0.44065,-0.00848,0.02966],"force_p95":0.52091,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.02424,"mean_force":0.32546,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.33675,-0.02296,0.06589]},{"body_a":"world","body_b":"grasp_target","contact_count":3058.0,"contact_point_centroid":[0.41277,-0.02168,-0.00238],"force_p95":0.33105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81191,"mean_force":0.16267,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.38555,0.00491,0.13231]},{"body_a":"grasp_target","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.46863,-0.00901,0.00968],"force_p95":0.43569,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44364,"mean_force":0.20245,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36261,-0.00454,0.05404]},{"body_a":"grasp_target","body_b":"hand","contact_count":129.0,"contact_point_centroid":[0.44682,-0.02421,0.03386],"force_p95":0.18344,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24189,"mean_force":0.12127,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.35349,-0.02606,0.0782]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.41704,-0.02574,-0.00207],"force_p95":0.16208,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20206,"mean_force":0.12929,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.36168,-0.02265,0.0927]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41709,-0.02573,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.36202,-0.0166,0.0926]}],"total_contact_groups":24},"final_pose_error":0.01597,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41255,-0.01879,0.01602],"final_tcp_position":[0.60173,0.149,0.438],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":272989.14689,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41709,-0.02573,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33127,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":215.00525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4883.0,"raw_peak_contact_force":1529.38611,"subtask_id":"approach_1","tcp_end":[0.36202,-0.0166,0.0926],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09477,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41709,-0.02573,0.01602],"object_pos_start":[0.41709,-0.02573,0.01602],"object_to_goal_dist_end":0.33127,"object_to_goal_dist_start":0.33127,"object_z_max":0.01602,"peak_contact_force":554.76532,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":554.76532,"subtask_id":"descend_1","tcp_end":[0.36215,-0.01663,0.09282],"tcp_start":[0.36202,-0.0166,0.0926],"tcp_to_object_dist_end":0.09487,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41709,-0.02573,0.01602],"object_pos_start":[0.41709,-0.02573,0.01602],"object_to_goal_dist_end":0.33127,"object_to_goal_dist_start":0.33127,"object_z_max":0.01602,"peak_contact_force":66.85494,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3495.0,"raw_peak_contact_force":151.0854,"subtask_id":"grasp_1","tcp_end":[0.36286,-0.01717,0.09212],"tcp_start":[0.36286,-0.01716,0.09212],"tcp_to_object_dist_end":0.09384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":507.0,"n_steps_budget":600.0,"object_pos_end":[0.41687,-0.02627,0.01476],"object_pos_start":[0.41709,-0.02573,0.01602],"object_to_goal_dist_end":0.33217,"object_to_goal_dist_start":0.33127,"object_z_max":0.01602,"peak_contact_force":208.49859,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4776.0,"raw_peak_contact_force":522.57641,"tcp_end":[0.35123,-0.02721,0.07316],"tcp_start":[0.36286,-0.01717,0.09212],"tcp_to_object_dist_end":0.08786,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":789.0,"n_steps_budget":930.0,"object_pos_end":[0.41255,-0.01879,0.01602],"object_pos_start":[0.41687,-0.02627,0.01476],"object_to_goal_dist_end":0.32938,"object_to_goal_dist_start":0.33217,"object_z_max":0.01944,"peak_contact_force":272989.14689,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7659.0,"raw_peak_contact_force":1694.45548,"subtask_id":"transport_arc","tcp_end":[0.59664,0.13629,0.28396],"tcp_start":[0.35123,-0.02721,0.07316],"tcp_to_object_dist_end":0.36019,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41255,-0.01879,0.01602],"object_pos_start":[0.41255,-0.01879,0.01602],"object_to_goal_dist_end":0.32938,"object_to_goal_dist_start":0.32938,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1076.0,"raw_peak_contact_force":260.60664,"subtask_id":"release_1","tcp_end":[0.60115,0.14752,0.31071],"tcp_start":[0.59664,0.13629,0.28396],"tcp_to_object_dist_end":0.38739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.41255,-0.01879,0.01602],"object_pos_start":[0.41255,-0.01879,0.01602],"object_to_goal_dist_end":0.32938,"object_to_goal_dist_start":0.32938,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60173,0.149,0.438],"tcp_start":[0.60115,0.14752,0.31071],"tcp_to_object_dist_end":0.49195,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":4.0,"average_failure_rate":0.04396,"average_mean_iterations":15.52747,"average_solve_count":91.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27059,"approach_1.speed":0.26459,"descend_1.contact_force":2.68792,"descend_1.grasp_z_offset":0.01713,"descend_1.speed":0.36963,"grasp_1.grasp_force":0.64606,"lift_1.lift_height":0.11175,"lift_1.lift_speed":0.17049,"release_1.release_time":0.4675,"retract_1.retract_height":0.16208,"retract_1.retract_speed":0.31746,"transport_1.arc_height":0.0617,"transport_1.transport_speed":0.27957},"optimized_scores":{"best_composite_score":-0.46046,"best_fitness_score":0.19669,"best_task_score":0.14588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":519.0,"contact_point_centroid":[0.54741,-0.00236,-0.00053],"force_p95":126.61183,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1625.51775,"mean_force":131.13163,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4262,-0.00083,0.0222]},{"body_a":"world","body_b":"link6","contact_count":349.0,"contact_point_centroid":[0.59559,0.05233,-0.00017],"force_p95":325.12209,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":707.77325,"mean_force":233.94905,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52181,0.00768,0.2496]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.57372,0.01295,-0.00024],"force_p95":405.01468,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":419.93264,"mean_force":199.56488,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44392,-0.00588,0.03652]},{"body_a":"world","body_b":"link5","contact_count":287.0,"contact_point_centroid":[0.49398,0.1025,-9e-05],"force_p95":323.34281,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.39733,"mean_force":259.51921,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52497,0.0193,0.27926]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56034,0.03891,-8e-05],"force_p95":139.78211,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.78211,"mean_force":139.78211,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.54035,0.02041,0.29132]},{"body_a":"world","body_b":"link6","contact_count":65.0,"contact_point_centroid":[0.61452,0.14788,-0.00014],"force_p95":79.0342,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.31694,"mean_force":42.9491,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64217,0.15194,0.29291]},{"body_a":"grasp_target","body_b":"link7","contact_count":537.0,"contact_point_centroid":[0.54349,-0.00175,0.01507],"force_p95":0.90533,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.03085,"mean_force":0.66982,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.42648,-0.00083,0.02244]},{"body_a":"grasp_target","body_b":"hand","contact_count":539.0,"contact_point_centroid":[0.52683,0.00099,0.02524],"force_p95":1.33551,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.00782,"mean_force":1.13225,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4266,-0.00083,0.02256]},{"body_a":"grasp_target","body_b":"hand","contact_count":87.0,"contact_point_centroid":[0.55359,-0.00657,0.03808],"force_p95":2.29137,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.87443,"mean_force":1.03908,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45922,-0.02959,0.06193]},{"body_a":"world","body_b":"grasp_target","contact_count":2178.0,"contact_point_centroid":[0.54465,0.00067,-0.0067],"force_p95":0.70556,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.81725,"mean_force":0.43992,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.42765,-0.00082,0.02378]},{"body_a":"grasp_target","body_b":"link7","contact_count":88.0,"contact_point_centroid":[0.55625,0.01779,0.04133],"force_p95":1.56598,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.65038,"mean_force":0.81046,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45968,-0.03006,0.06264]},{"body_a":"world","body_b":"grasp_target","contact_count":2520.0,"contact_point_centroid":[0.54022,-0.00089,-0.00263],"force_p95":0.36424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57505,"mean_force":0.17176,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51857,0.01326,0.2526]},{"body_a":"grasp_target","body_b":"link6","contact_count":104.0,"contact_point_centroid":[0.54122,0.01183,0.02434],"force_p95":0.56173,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.11195,"mean_force":0.37105,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.5455,0.02698,0.30251]},{"body_a":"grasp_target","body_b":"link6","contact_count":241.0,"contact_point_centroid":[0.55194,0.01788,0.05834],"force_p95":0.11653,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.73899,"mean_force":0.08762,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53272,0.02235,0.28899]},{"body_a":"world","body_b":"grasp_target","contact_count":1941.0,"contact_point_centroid":[0.50074,-0.01327,-0.00236],"force_p95":0.42767,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53637,"mean_force":0.15317,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.59397,0.08918,0.32777]},{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.54431,0.00113,-0.00088],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.11865,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51316,0.00031,0.30329]}],"total_contact_groups":27},"final_pose_error":0.01841,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.49653,-0.0148,0.01602],"final_tcp_position":[0.64334,0.15367,0.46251],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":29.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.0266],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.24974,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.13762,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":112.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53754,0.00068,0.30538],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":62.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.026],"object_pos_start":[0.54431,0.00113,0.0266],"object_to_goal_dist_end":0.25014,"object_to_goal_dist_start":0.24974,"object_z_max":0.0266,"peak_contact_force":80.79834,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":248.0,"raw_peak_contact_force":0.13728,"subtask_id":"descend_1","tcp_end":[0.49157,-0.00054,0.09533],"tcp_start":[0.53754,0.00068,0.30538],"tcp_to_object_dist_end":0.08713,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5315,0.00107,0.01337],"object_pos_start":[0.54431,0.00113,0.026],"object_to_goal_dist_end":0.26406,"object_to_goal_dist_start":0.25014,"object_z_max":0.02602,"peak_contact_force":167951.73011,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4707.0,"raw_peak_contact_force":1625.51775,"subtask_id":"grasp_1","tcp_end":[0.42646,-0.0009,0.02279],"tcp_start":[0.42645,-0.00089,0.02279],"tcp_to_object_dist_end":0.10549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":720.0,"n_steps_budget":840.0,"object_pos_end":[0.5369,-0.00557,0.02557],"object_pos_start":[0.53147,0.00103,0.01344],"object_to_goal_dist_end":0.25777,"object_to_goal_dist_start":0.26405,"object_z_max":0.03277,"peak_contact_force":81.73389,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6745.0,"raw_peak_contact_force":707.77325,"tcp_end":[0.54035,0.02041,0.29132],"tcp_start":[0.42646,-0.0009,0.02279],"tcp_to_object_dist_end":0.26704,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":547.0,"n_steps_budget":600.0,"object_pos_end":[0.49653,-0.0148,0.01602],"object_pos_start":[0.5369,-0.00557,0.02557],"object_to_goal_dist_end":0.28874,"object_to_goal_dist_start":0.25777,"object_z_max":0.0268,"peak_contact_force":9748.90339,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4378.0,"raw_peak_contact_force":139.78211,"subtask_id":"transport_arc","tcp_end":[0.64251,0.15186,0.2966],"tcp_start":[0.54035,0.02041,0.29132],"tcp_to_object_dist_end":0.35751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49653,-0.0148,0.01602],"object_pos_start":[0.49653,-0.0148,0.01602],"object_to_goal_dist_end":0.28874,"object_to_goal_dist_start":0.28874,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1081.0,"raw_peak_contact_force":93.31694,"subtask_id":"release_1","tcp_end":[0.64229,0.15212,0.31874],"tcp_start":[0.64251,0.15186,0.2966],"tcp_to_object_dist_end":0.37516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49653,-0.0148,0.01602],"object_pos_start":[0.49653,-0.0148,0.01602],"object_to_goal_dist_end":0.28874,"object_to_goal_dist_start":0.28874,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64334,0.15367,0.46251],"tcp_start":[0.64229,0.15212,0.31874],"tcp_to_object_dist_end":0.49929,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```