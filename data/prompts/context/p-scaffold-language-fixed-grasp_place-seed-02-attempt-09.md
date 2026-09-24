## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | admittance_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0179 | 0.41 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.1415 | 0.34 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | 0.0156 | 0.50 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0375 | 0.36 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0674 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.018) — your mutation base

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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
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
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
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
  guards:
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: grasp_1
- id: lift_1
  type: lift
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
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: close
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=reduce_speed
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.018
- **task_score** (E): 0.405
- **fitness_score**: 0.682  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0697 |
| descend_1 | 1.00 | 1.00 | 0.2177 |
| grasp_1 | 1.00 | 1.00 | 0.0115 |
| lift_1 | 1.00 | 1.00 | 0.1560 |
| transport_1 | 1.00 | 1.00 | 0.2312 |
| place_1 | 1.00 | 1.00 | 0.0120 |
| release_1 | 1.00 | 1.00 | 0.0203 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.013, 0.255) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 32.377 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.493, -0.013, 0.255)→(0.489, -0.015, 0.037) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.489, -0.015, 0.037)→(0.481, -0.015, 0.029) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.333 | 0.135 | 0.172 |
| lift_1 | lift | 1.00 / step_budget | (0.481, -0.015, 0.029)→(0.489, -0.015, 0.185) | (0.493, -0.015, 0.026)→(0.499, -0.015, 0.178) | 0.281→0.238 | 1.00 / 39.000 | 0.078 | 0.566 |
| transport_1 | approach | 1.00 / step_budget | (0.489, -0.015, 0.185)→(0.628, 0.168, 0.175) | (0.499, -0.015, 0.178)→(0.624, 0.167, 0.155) | 0.238→0.023 | 1.00 / 35.333 | 0.093 | 0.261 |
| place_1 | descend | 1.00 / step_budget | (0.628, 0.168, 0.175)→(0.630, 0.172, 0.178) | (0.624, 0.167, 0.155)→(0.626, 0.171, 0.156) | 0.023→0.016 | 1.00 / 37.667 | 0.082 | 0.206 |
| release_1 | release | 1.00 / step_budget | (0.630, 0.172, 0.178)→(0.625, 0.170, 0.198) | (0.626, 0.171, 0.156)→(0.617, 0.174, 0.027) | 0.016→0.140 | 1.00 / 2.667 | 0.127 | 1.418 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.556
- phase_score: 0.560
- phase_breakdown.transport_arc_score: 0.490
- phase_breakdown.approach_1_score: 0.017
- phase_breakdown.descend_1_score: 0.794
- phase_breakdown.release_1_score: 0.399
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.757

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.757
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.556
- **Median Q (composite search score)**: -0.054
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.372


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08746,"average_solve_count":343.0,"average_success_count":343.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17727,"approach_1.speed":0.03198,"descend_1.grasp_z_offset":1e-05,"descend_1.speed":0.02111,"lift_1.lift_height":0.1923,"lift_1.speed":0.02323,"place_1.place_z_offset":0.02512,"place_1.speed":0.04455,"release_1.duration":0.11189,"transport_1.arc_height":0.39998,"transport_1.speed":0.25593},"optimized_scores":{"best_composite_score":-0.05441,"best_fitness_score":0.64559,"best_task_score":0.32943},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":214.0,"contact_point_centroid":[0.6136,0.15666,-0.0072],"force_p95":1.02563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51522,"mean_force":0.33872,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62235,0.15626,0.21691]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.47249,-0.01958,-0.00149],"force_p95":0.53536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55947,"mean_force":0.24227,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46325,-0.01961,0.02805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11465.0,"contact_point_centroid":[0.46622,-0.00038,0.11236],"force_p95":0.07434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25017,"mean_force":0.05252,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46618,-0.01954,0.11013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12032.0,"contact_point_centroid":[0.46631,-0.03866,0.11527],"force_p95":0.07331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24919,"mean_force":0.05056,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46638,-0.01954,0.11327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15283.0,"contact_point_centroid":[0.5431,0.08211,0.21557],"force_p95":0.07462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19464,"mean_force":0.04812,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54328,0.0631,0.21363]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00204],"force_p95":0.13641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18575,"mean_force":0.12647,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4653,-0.01966,0.02827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13422.0,"contact_point_centroid":[0.54451,0.0458,0.21453],"force_p95":0.08132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1839,"mean_force":0.05439,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54506,0.06503,0.21273]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18108.0,"contact_point_centroid":[0.62364,0.17344,0.19808],"force_p95":0.06773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17954,"mean_force":0.04579,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62328,0.15425,0.19574]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48814,-0.00795,0.2592]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17993.0,"contact_point_centroid":[0.62363,0.13504,0.19814],"force_p95":0.06924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13582,"mean_force":0.04558,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62325,0.15422,0.19567]},{"body_a":"world","body_b":"grasp_target","contact_count":2548.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47295,-0.0183,0.12487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.62595,0.17661,0.20382],"force_p95":0.06621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10583,"mean_force":0.03997,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62598,0.1574,0.20178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.46372,-0.00039,0.0301],"force_p95":0.06624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09291,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4642,-0.01963,0.02719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.46362,-0.03889,0.0295],"force_p95":0.06484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08776,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4642,-0.01963,0.0272]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1225.0,"contact_point_centroid":[0.62555,0.13819,0.20398],"force_p95":0.0689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0704,"mean_force":0.04157,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62599,0.1574,0.20179]}],"total_contact_groups":15},"final_pose_error":0.01073,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61492,0.15651,0.0243],"final_tcp_position":[0.62743,0.1578,0.20527],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":15.8647,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":15.8647,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47678,-0.01691,0.21666],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2548.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47186,-0.01981,0.03483],"tcp_start":[0.47678,-0.01691,0.21666],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01966,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13436,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12266.0,"raw_peak_contact_force":0.18575,"subtask_id":"grasp_1","tcp_end":[0.46417,-0.01963,0.02716],"tcp_start":[0.47186,-0.01981,0.03483],"tcp_to_object_dist_end":0.01194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.48212,-0.01934,0.1935],"object_pos_start":[0.47604,-0.01966,0.02583],"object_to_goal_dist_end":0.23276,"object_to_goal_dist_start":0.28825,"object_z_max":0.19322,"peak_contact_force":0.0788,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23588.0,"raw_peak_contact_force":0.55947,"tcp_end":[0.47196,-0.01955,0.19867],"tcp_start":[0.46417,-0.01963,0.02716],"tcp_to_object_dist_end":0.0114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.61587,0.14962,0.17273],"object_pos_start":[0.48212,-0.01934,0.1935],"object_to_goal_dist_end":0.02515,"object_to_goal_dist_start":0.23276,"object_z_max":0.21216,"peak_contact_force":0.07843,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28705.0,"raw_peak_contact_force":0.19464,"subtask_id":"transport_arc","tcp_end":[0.62025,0.14959,0.18846],"tcp_start":[0.47196,-0.01955,0.19867],"tcp_to_object_dist_end":0.01633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.62447,0.15774,0.18588],"object_pos_start":[0.61587,0.14962,0.17273],"object_to_goal_dist_end":0.00822,"object_to_goal_dist_start":0.02515,"object_z_max":0.18588,"peak_contact_force":0.0703,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36101.0,"raw_peak_contact_force":0.17954,"tcp_end":[0.62743,0.1578,0.20527],"tcp_start":[0.62025,0.14959,0.18846],"tcp_to_object_dist_end":0.01961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61492,0.15651,0.0243],"object_pos_start":[0.62447,0.15774,0.18588],"object_to_goal_dist_end":0.16656,"object_to_goal_dist_start":0.00822,"object_z_max":0.18588,"peak_contact_force":0.07023,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2727.0,"raw_peak_contact_force":1.51522,"subtask_id":"release_1","tcp_end":[0.62231,0.15625,0.22503],"tcp_start":[0.62743,0.1578,0.20527],"tcp_to_object_dist_end":0.20087,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87052,"average_solve_count":363.0,"average_success_count":363.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19621,"approach_1.speed":0.02311,"descend_1.grasp_z_offset":0.00405,"descend_1.speed":0.01686,"lift_1.lift_height":0.1798,"lift_1.speed":0.02417,"place_1.place_z_offset":0.01742,"place_1.speed":0.04852,"release_1.duration":0.26795,"transport_1.arc_height":0.15995,"transport_1.speed":0.2599},"optimized_scores":{"best_composite_score":0.05731,"best_fitness_score":0.75731,"best_task_score":0.55568},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.60832,0.2159,-0.00764],"force_p95":1.02569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29623,"mean_force":0.4459,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61835,0.20336,0.14709]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.45494,-0.0256,-0.00152],"force_p95":0.46692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50327,"mean_force":0.21644,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44633,-0.02555,0.03293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15317.0,"contact_point_centroid":[0.53598,0.06451,0.24461],"force_p95":0.1108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41529,"mean_force":0.06911,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53448,0.08364,0.24307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18091.0,"contact_point_centroid":[0.53788,0.10542,0.24539],"force_p95":0.09442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37376,"mean_force":0.05738,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53677,0.08668,0.24426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":366.0,"contact_point_centroid":[0.62383,0.22416,0.14321],"force_p95":0.12056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24487,"mean_force":0.08043,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62481,0.20558,0.1442]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10544.0,"contact_point_centroid":[0.4492,-0.04464,0.10976],"force_p95":0.07487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24468,"mean_force":0.05181,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44909,-0.02549,0.1079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10546.0,"contact_point_centroid":[0.44917,-0.00635,0.10981],"force_p95":0.07422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23515,"mean_force":0.05148,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44909,-0.02549,0.10789]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":841.0,"contact_point_centroid":[0.62209,0.22439,0.13234],"force_p95":0.15293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20864,"mean_force":0.08608,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62233,0.20492,0.13433]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.62093,0.1865,0.13391],"force_p95":0.10274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18711,"mean_force":0.05854,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62273,0.20508,0.135]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02623,-0.00206],"force_p95":0.14121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18655,"mean_force":0.12751,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44831,-0.02562,0.03306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":359.0,"contact_point_centroid":[0.62256,0.18638,0.14267],"force_p95":0.12408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14341,"mean_force":0.08016,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62475,0.20556,0.14385]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.45856,-0.02632,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48163,-0.01016,0.26758]},{"body_a":"world","body_b":"grasp_target","contact_count":2748.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45737,-0.02373,0.13563]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5205.0,"contact_point_centroid":[0.44667,-0.00641,0.0334],"force_p95":0.06654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11382,"mean_force":0.04168,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44726,-0.02558,0.03206]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4940.0,"contact_point_centroid":[0.44733,-0.04486,0.03391],"force_p95":0.07098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0843,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44726,-0.02558,0.03206]}],"total_contact_groups":15},"final_pose_error":0.00978,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60873,0.21616,0.02899],"final_tcp_position":[0.62474,0.20562,0.13929],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":81.14226,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46267,-0.02176,0.23387],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2748.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45465,-0.02585,0.03919],"tcp_start":[0.46267,-0.02176,0.23387],"tcp_to_object_dist_end":0.01374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45846,-0.02571,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30331,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13998,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11945.0,"raw_peak_contact_force":0.18655,"subtask_id":"grasp_1","tcp_end":[0.44723,-0.02558,0.03203],"tcp_start":[0.45465,-0.02585,0.03919],"tcp_to_object_dist_end":0.01285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.4633,-0.02556,0.17706],"object_pos_start":[0.45846,-0.02571,0.02578],"object_to_goal_dist_end":0.29402,"object_to_goal_dist_start":0.30331,"object_z_max":0.17678,"peak_contact_force":0.07432,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21184.0,"raw_peak_contact_force":0.50327,"tcp_end":[0.45431,-0.02554,0.18626],"tcp_start":[0.44723,-0.02558,0.03203],"tcp_to_object_dist_end":0.01286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61565,0.20487,0.12409],"object_pos_start":[0.4633,-0.02556,0.17706],"object_to_goal_dist_end":0.01789,"object_to_goal_dist_start":0.29402,"object_z_max":0.26641,"peak_contact_force":0.12333,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33408.0,"raw_peak_contact_force":0.41529,"subtask_id":"transport_arc","tcp_end":[0.62581,0.206,0.14947],"tcp_start":[0.45431,-0.02554,0.18626],"tcp_to_object_dist_end":0.02737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":27.0,"n_steps_budget":1000.0,"object_pos_end":[0.61538,0.20483,0.11325],"object_pos_start":[0.61565,0.20487,0.12409],"object_to_goal_dist_end":0.01515,"object_to_goal_dist_start":0.01789,"object_z_max":0.12409,"peak_contact_force":0.10877,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":725.0,"raw_peak_contact_force":0.24487,"tcp_end":[0.62474,0.20562,0.13929],"tcp_start":[0.62581,0.206,0.14947],"tcp_to_object_dist_end":0.02768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60873,0.21616,0.02899],"object_pos_start":[0.61538,0.20483,0.11325],"object_to_goal_dist_end":0.08813,"object_to_goal_dist_start":0.01515,"object_z_max":0.11325,"peak_contact_force":0.18035,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1872.0,"raw_peak_contact_force":1.29623,"subtask_id":"release_1","tcp_end":[0.61826,0.20333,0.1582],"tcp_start":[0.62474,0.20562,0.13929],"tcp_to_object_dist_end":0.1302,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98872,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29164,"approach_1.speed":0.0356,"descend_1.grasp_z_offset":0.00283,"descend_1.speed":0.02914,"lift_1.lift_height":0.16237,"lift_1.speed":0.05198,"place_1.place_z_offset":0.0247,"place_1.speed":0.01003,"release_1.duration":0.33266,"transport_1.arc_height":0.35512,"transport_1.speed":0.29758},"optimized_scores":{"best_composite_score":-0.05673,"best_fitness_score":0.64327,"best_task_score":0.32998},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.62299,0.14935,-0.00836],"force_p95":1.35393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44275,"mean_force":0.45288,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63311,0.15001,0.20056]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.54009,0.00074,-0.0014],"force_p95":0.59386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63673,"mean_force":0.19355,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52968,0.00086,0.02854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9847.0,"contact_point_centroid":[0.53341,-0.01835,0.09963],"force_p95":0.07915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31435,"mean_force":0.05584,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53308,0.00076,0.09719]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10172.0,"contact_point_centroid":[0.5332,0.01983,0.09739],"force_p95":0.07815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29467,"mean_force":0.05455,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53292,0.00076,0.09517]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":23410.0,"contact_point_centroid":[0.63709,0.16934,0.18956],"force_p95":0.06247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19484,"mean_force":0.04188,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63725,0.1502,0.18695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13982.0,"contact_point_centroid":[0.58679,0.09219,0.1924],"force_p95":0.07225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17242,"mean_force":0.04831,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58649,0.07322,0.19079]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20423.0,"contact_point_centroid":[0.63673,0.13095,0.1898],"force_p95":0.06798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16665,"mean_force":0.0472,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63726,0.15021,0.18696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11430.0,"contact_point_centroid":[0.58566,0.05262,0.19251],"force_p95":0.08033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16034,"mean_force":0.05779,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58556,0.07182,0.1903]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.001,-0.00203],"force_p95":0.13115,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14418,"mean_force":0.12511,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53186,0.00091,0.02879]},{"body_a":"world","body_b":"grasp_target","contact_count":1872.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5201,0.00055,0.30588]},{"body_a":"world","body_b":"grasp_target","contact_count":3532.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53782,0.00101,0.17376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4118.0,"contact_point_centroid":[0.53127,-0.01831,0.03013],"force_p95":0.07606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09867,"mean_force":0.05169,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53064,0.00089,0.02737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4872.0,"contact_point_centroid":[0.53129,0.01997,0.02925],"force_p95":0.06802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09549,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53064,0.00089,0.02737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1439.0,"contact_point_centroid":[0.63685,0.17037,0.18956],"force_p95":0.06154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07282,"mean_force":0.03611,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63702,0.15115,0.18714]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.63603,0.13183,0.19008],"force_p95":0.06749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06875,"mean_force":0.03993,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.637,0.15114,0.1871]}],"total_contact_groups":15},"final_pose_error":0.02754,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62755,0.14972,0.02622],"final_tcp_position":[0.63852,0.15154,0.19065],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.44275,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53845,0.001,0.31359],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3532.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53918,0.00104,0.03735],"tcp_start":[0.53845,0.001,0.31359],"tcp_to_object_dist_end":0.01244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00075,0.02589],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12927,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10790.0,"raw_peak_contact_force":0.14418,"subtask_id":"grasp_1","tcp_end":[0.53061,0.00089,0.02734],"tcp_start":[0.53918,0.00104,0.03735],"tcp_to_object_dist_end":0.01363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.551,0.00072,0.16237],"object_pos_start":[0.54416,0.00075,0.02589],"object_to_goal_dist_end":0.18688,"object_to_goal_dist_start":0.25051,"object_z_max":0.16212,"peak_contact_force":0.08086,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20109.0,"raw_peak_contact_force":0.63673,"tcp_end":[0.53936,0.0007,0.16888],"tcp_start":[0.53061,0.00089,0.02734],"tcp_to_object_dist_end":0.01334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.64068,0.14796,0.16765],"object_pos_start":[0.551,0.00072,0.16237],"object_to_goal_dist_end":0.02647,"object_to_goal_dist_start":0.18688,"object_z_max":0.18527,"peak_contact_force":0.07818,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25412.0,"raw_peak_contact_force":0.17242,"subtask_id":"transport_arc","tcp_end":[0.63779,0.14795,0.18627],"tcp_start":[0.53936,0.0007,0.16888],"tcp_to_object_dist_end":0.01884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63879,0.15148,0.16888],"object_pos_start":[0.64068,0.14796,0.16765],"object_to_goal_dist_end":0.02481,"object_to_goal_dist_start":0.02647,"object_z_max":0.16888,"peak_contact_force":0.06835,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":43833.0,"raw_peak_contact_force":0.19484,"tcp_end":[0.63852,0.15154,0.19065],"tcp_start":[0.63779,0.14795,0.18627],"tcp_to_object_dist_end":0.02177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62755,0.14972,0.02622],"object_pos_start":[0.63879,0.15148,0.16888],"object_to_goal_dist_end":0.16631,"object_to_goal_dist_start":0.02481,"object_z_max":0.16888,"peak_contact_force":0.12939,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2878.0,"raw_peak_contact_force":1.44275,"subtask_id":"release_1","tcp_end":[0.63306,0.15,0.21004],"tcp_start":[0.63852,0.15154,0.19065],"tcp_to_object_dist_end":0.1839,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```