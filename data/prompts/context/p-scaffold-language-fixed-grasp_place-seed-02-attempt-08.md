## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.1415 | 0.34 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | 0.0156 | 0.50 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0375 | 0.36 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0674 | 0.39 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0002 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.142) — your mutation base

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

- **Composite score**: -0.142
- **task_score** (E): 0.340
- **fitness_score**: 0.558  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1601 |
| descend_1 | 1.00 | 1.00 | 0.1051 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 0.33 | 1.00 | 0.0657 |
| transport_1 | 0.67 | 0.67 | 0.2541 |
| place_1 | 0.33 | 1.00 | 0.0775 |
| release_1 | 1.00 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, -0.014, 0.146) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 8.156 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.489, -0.014, 0.146)→(0.488, -0.015, 0.041) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.041)→(0.480, -0.015, 0.033) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 40.667 | 0.134 | 0.171 |
| lift_1 | lift | 0.33 / step_budget | (0.488, -0.010, 0.085)→(0.489, -0.009, 0.151) | (0.493, -0.015, 0.026)→(0.498, -0.009, 0.082) | 0.281→0.260 | 1.00 / 30.667 | 3249.629 | 0.883 |
| transport_1 | approach | 0.67 / step_budget | (0.489, -0.009, 0.151)→(0.613, 0.149, 0.299) | (0.498, -0.009, 0.082)→(0.588, 0.106, 0.031) | 0.260→0.162 | 0.67 / 5.333 | 3249.713 | 0.870 |
| place_1 | descend | 0.33 / step_budget | (0.613, 0.149, 0.299)→(0.622, 0.162, 0.223) | (0.588, 0.106, 0.031)→(0.588, 0.109, 0.019) | 0.162→0.173 | 1.00 / 8.667 | 182002.949 | 0.731 |
| release_1 | release | 1.00 / step_budget | (0.622, 0.162, 0.223)→(0.617, 0.160, 0.243) | (0.588, 0.109, 0.019)→(0.588, 0.109, 0.019) | 0.173→0.173 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.519
- phase_score: 0.285
- phase_breakdown.transport_arc_score: 0.067
- phase_breakdown.approach_1_score: 0.217
- phase_breakdown.descend_1_score: 0.686
- phase_breakdown.release_1_score: 0.128
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.741

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.741
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.519
- **Median Q (composite search score)**: -0.070
- **K-run variance**: 0.0343
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92395,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09704,"approach_1.speed":0.05216,"descend_1.grasp_z_offset":0.00101,"descend_1.speed":0.0269,"lift_1.lift_height":0.19873,"lift_1.speed":0.05311,"place_1.place_z_offset":0.02473,"place_1.speed":0.02696,"release_1.duration":0.28619,"transport_1.speed":0.3857,"transport_1.transport_z_offset":0.21431},"optimized_scores":{"best_composite_score":-0.07004,"best_fitness_score":0.62996,"best_task_score":0.30107},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1097.0,"contact_point_centroid":[0.5785,0.10469,-0.00322],"force_p95":0.57172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04376,"mean_force":0.18129,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57911,0.10441,0.30927]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.47309,-0.01944,-0.00113],"force_p95":0.56029,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71971,"mean_force":0.10175,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46258,-0.01971,0.02298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9717.0,"contact_point_centroid":[0.49767,0.03449,0.16867],"force_p95":0.1323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3771,"mean_force":0.06523,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49576,0.01584,0.16854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20141.0,"contact_point_centroid":[0.46295,-0.00044,0.07199],"force_p95":0.07463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30102,"mean_force":0.05068,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46303,-0.0196,0.07008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20711.0,"contact_point_centroid":[0.46293,-0.03874,0.0719],"force_p95":0.07276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2851,"mean_force":0.04957,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46305,-0.0196,0.07019]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7768.0,"contact_point_centroid":[0.49657,-0.00415,0.16707],"force_p95":0.1451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2826,"mean_force":0.07568,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49486,0.01482,0.16698]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.01996,-0.00203],"force_p95":0.13329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16954,"mean_force":0.12571,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46508,-0.01978,0.02248]},{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48645,-0.00897,0.21826]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58064,0.10489,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1233,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.6083,0.13694,0.29083]},{"body_a":"world","body_b":"grasp_target","contact_count":2996.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4713,-0.0191,0.07987]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58064,0.10489,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60945,0.14049,0.27368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.46405,-0.00055,0.02421],"force_p95":0.07634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10792,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46397,-0.01975,0.0214]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4901.0,"contact_point_centroid":[0.46421,-0.03884,0.02327],"force_p95":0.06858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0916,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46398,-0.01975,0.0214]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1112.0,"contact_point_centroid":[0.58073,0.10603,0.31412],"force_p95":0.0124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01078,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58064,0.10603,0.31184]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4231.0,"contact_point_centroid":[0.60832,0.13694,0.29314],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01293,"mean_force":0.01053,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.6083,0.13694,0.29084]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.61102,0.14106,0.27232],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01012,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61128,0.14105,0.26998]}],"total_contact_groups":16},"final_pose_error":0.06382,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.58064,0.10489,0.02602],"final_tcp_position":[0.61227,0.14131,0.27294],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.38118,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2124.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47448,-0.01834,0.13668],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2996.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47153,-0.01993,0.02884],"tcp_start":[0.47448,-0.01834,0.13668],"tcp_to_object_dist_end":0.00542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47601,-0.0196,0.02588],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2882,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1303,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10802.0,"raw_peak_contact_force":0.16954,"subtask_id":"grasp_1","tcp_end":[0.46395,-0.01975,0.02137],"tcp_start":[0.47153,-0.01993,0.02884],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47727,-0.01948,0.11101],"object_pos_start":[0.47601,-0.0196,0.02588],"object_to_goal_dist_end":0.24885,"object_to_goal_dist_start":0.2882,"object_z_max":0.11091,"peak_contact_force":0.0723,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41018.0,"raw_peak_contact_force":0.71971,"tcp_end":[0.46579,-0.01956,0.11609],"tcp_start":[0.46395,-0.01975,0.02137],"tcp_to_object_dist_end":0.01256,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58063,0.10489,0.02602],"object_pos_start":[0.47727,-0.01948,0.11101],"object_to_goal_dist_end":0.18007,"object_to_goal_dist_start":0.24885,"object_z_max":0.22468,"peak_contact_force":0.12324,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19694.0,"raw_peak_contact_force":2.04376,"subtask_id":"transport_arc","tcp_end":[0.5996,0.12604,0.34356],"tcp_start":[0.46579,-0.01956,0.11609],"tcp_to_object_dist_end":0.31881,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58064,0.10489,0.02602],"object_pos_start":[0.58063,0.10489,0.02602],"object_to_goal_dist_end":0.18006,"object_to_goal_dist_start":0.18007,"object_z_max":0.02602,"peak_contact_force":273004.38118,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8231.0,"raw_peak_contact_force":0.1233,"tcp_end":[0.61227,0.14131,0.27294],"tcp_start":[0.5996,0.12604,0.34356],"tcp_to_object_dist_end":0.25159,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58064,0.10489,0.02602],"object_pos_start":[0.58064,0.10489,0.02602],"object_to_goal_dist_end":0.18006,"object_to_goal_dist_start":0.18006,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60846,0.14017,0.29326],"tcp_start":[0.61227,0.14131,0.27294],"tcp_to_object_dist_end":0.27099,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25229,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06687,"approach_1.speed":0.06607,"descend_1.grasp_z_offset":0.00344,"descend_1.speed":0.0285,"lift_1.lift_height":0.25896,"lift_1.speed":0.01771,"place_1.place_z_offset":0.01176,"place_1.speed":0.0378,"release_1.duration":0.18031,"transport_1.speed":0.34907,"transport_1.transport_z_offset":0.15621},"optimized_scores":{"best_composite_score":0.04094,"best_fitness_score":0.74094,"best_task_score":0.51934},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3961.0,"contact_point_centroid":[0.62531,0.20472,-0.0023],"force_p95":0.12519,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94644,"mean_force":0.13529,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60637,0.18305,0.20688]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.45423,-0.02537,-0.00119],"force_p95":0.54009,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65951,"mean_force":0.11987,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44553,-0.02565,0.02639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11885.0,"contact_point_centroid":[0.50625,0.03169,0.16909],"force_p95":0.14082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44327,"mean_force":0.07505,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50443,0.05077,0.16852]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20571.0,"contact_point_centroid":[0.44521,-0.04467,0.07799],"force_p95":0.07181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27153,"mean_force":0.04954,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44537,-0.02554,0.07605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19972.0,"contact_point_centroid":[0.44531,-0.00638,0.07871],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26959,"mean_force":0.05054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4454,-0.02554,0.07653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16043.0,"contact_point_centroid":[0.51062,0.07539,0.17259],"force_p95":0.0906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25991,"mean_force":0.05608,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50912,0.05678,0.17206]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02616,-0.00205],"force_p95":0.13792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19025,"mean_force":0.12687,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4479,-0.02574,0.02579]},{"body_a":"world","body_b":"grasp_target","contact_count":2472.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.1306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47803,-0.01198,0.20274]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45427,-0.0251,0.06716]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62531,0.20471,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60584,0.18584,0.19137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4915.0,"contact_point_centroid":[0.44651,-0.00649,0.02726],"force_p95":0.06753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09406,"mean_force":0.04399,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44683,-0.0257,0.02479]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5166.0,"contact_point_centroid":[0.44655,-0.04495,0.02666],"force_p95":0.06688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08297,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44683,-0.0257,0.02479]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4010.0,"contact_point_centroid":[0.60656,0.18333,0.20785],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01526,"mean_force":0.01056,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60653,0.18332,0.20554]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.60829,0.18677,0.19002],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60836,0.18675,0.18773]}],"total_contact_groups":14},"final_pose_error":0.07119,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62531,0.20471,0.01602],"final_tcp_position":[0.60969,0.18717,0.19075],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.94644,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2472.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45772,-0.02433,0.10643],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45411,-0.02598,0.0317],"tcp_start":[0.45772,-0.02433,0.10643],"tcp_to_object_dist_end":0.00723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45843,-0.02571,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30331,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13549,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11881.0,"raw_peak_contact_force":0.19025,"subtask_id":"grasp_1","tcp_end":[0.4468,-0.0257,0.02476],"tcp_start":[0.45411,-0.02598,0.0317],"tcp_to_object_dist_end":0.01168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45711,-0.02548,0.11977],"object_pos_start":[0.45843,-0.02571,0.02582],"object_to_goal_dist_end":0.29083,"object_to_goal_dist_start":0.30331,"object_z_max":0.11968,"peak_contact_force":0.07077,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40703.0,"raw_peak_contact_force":0.65951,"tcp_end":[0.44769,-0.02553,0.12661],"tcp_start":[0.4468,-0.0257,0.02476],"tcp_to_object_dist_end":0.01164,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62264,0.19504,0.05236],"object_pos_start":[0.45711,-0.02548,0.11977],"object_to_goal_dist_end":0.06359,"object_to_goal_dist_start":0.29083,"object_z_max":0.20858,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27928.0,"raw_peak_contact_force":0.44327,"subtask_id":"transport_arc","tcp_end":[0.60325,0.17657,0.24305],"tcp_start":[0.44769,-0.02553,0.12661],"tcp_to_object_dist_end":0.19256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62531,0.20471,0.01602],"object_pos_start":[0.62264,0.19504,0.05236],"object_to_goal_dist_end":0.09828,"object_to_goal_dist_start":0.06359,"object_z_max":0.05236,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7971.0,"raw_peak_contact_force":1.94644,"tcp_end":[0.60969,0.18717,0.19075],"tcp_start":[0.60325,0.17657,0.24305],"tcp_to_object_dist_end":0.1763,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62531,0.20471,0.01602],"object_pos_start":[0.62531,0.20471,0.01602],"object_to_goal_dist_end":0.09828,"object_to_goal_dist_start":0.09828,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60438,0.1853,0.21092],"tcp_start":[0.60969,0.18717,0.19075],"tcp_to_object_dist_end":0.19698,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07358,"average_solve_count":299.0,"average_success_count":299.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1584,"approach_1.speed":0.04448,"descend_1.grasp_z_offset":-0.00746,"descend_1.speed":0.02155,"lift_1.lift_height":0.20192,"lift_1.speed":0.08484,"place_1.place_z_offset":0.02212,"place_1.speed":0.03399,"release_1.duration":0.25906,"transport_1.speed":0.26018,"transport_1.transport_z_offset":0.14023},"optimized_scores":{"best_composite_score":-0.39544,"best_fitness_score":0.30456,"best_task_score":0.20061},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3570.0,"contact_point_centroid":[0.55839,0.01712,-0.00214],"force_p95":0.12763,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26879,"mean_force":0.13009,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54245,0.00703,0.18209]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5847.0,"contact_point_centroid":[0.53257,-0.01744,0.08494],"force_p95":0.14574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36515,"mean_force":0.10384,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52867,0.00079,0.0875]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6707.0,"contact_point_centroid":[0.53269,0.01889,0.08779],"force_p95":0.13507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29228,"mean_force":0.09137,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52888,0.00079,0.09013]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00107,-0.00206],"force_p95":0.13722,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15308,"mean_force":0.1275,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53048,0.0009,0.05343]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51665,0.00047,0.24632]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53548,0.00098,0.11246]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55939,0.01801,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59428,0.08084,0.25741]},{"body_a":"world","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.55939,0.01801,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63967,0.1504,0.24924]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55939,0.01801,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64007,0.15569,0.20568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3647.0,"contact_point_centroid":[0.53185,-0.01797,0.05114],"force_p95":0.10744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11602,"mean_force":0.05948,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52929,0.00088,0.052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4293.0,"contact_point_centroid":[0.5307,0.01968,0.0513],"force_p95":0.08938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09284,"mean_force":0.04931,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5293,0.00088,0.052]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3267.0,"contact_point_centroid":[0.54423,0.00799,0.19462],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01062,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54408,0.00799,0.19235]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2303.0,"contact_point_centroid":[0.6398,0.15041,0.25155],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01041,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63966,0.1504,0.24928]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4283.0,"contact_point_centroid":[0.5946,0.08084,0.25969],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01042,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59428,0.08084,0.2574]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.64271,0.15645,0.20479],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.0102,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64254,0.15644,0.20257]}],"total_contact_groups":15},"final_pose_error":0.00846,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55939,0.01801,0.01602],"final_tcp_position":[0.64381,0.15678,0.20579],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.34378,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":24.22323,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53613,0.00097,0.19402],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53721,0.00101,0.06161],"tcp_start":[0.53613,0.00097,0.19402],"tcp_to_object_dist_end":0.03629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54435,0.00078,0.02567],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25056,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13764,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9740.0,"raw_peak_contact_force":0.15308,"subtask_id":"grasp_1","tcp_end":[0.52926,0.00088,0.05196],"tcp_start":[0.53721,0.00101,0.06161],"tcp_to_object_dist_end":0.03031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1572.0,"n_steps_budget":1000.0,"object_pos_end":[0.55939,0.01801,0.01602],"object_pos_start":[0.54435,0.00078,0.02567],"object_to_goal_dist_end":0.24096,"object_to_goal_dist_start":0.25056,"object_z_max":0.10323,"peak_contact_force":9748.74508,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19391.0,"raw_peak_contact_force":1.26879,"tcp_end":[0.55459,0.01725,0.20921],"tcp_start":[0.55448,0.01678,0.20933],"tcp_to_object_dist_end":0.19325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55939,0.01801,0.01602],"object_pos_start":[0.55939,0.01801,0.01602],"object_to_goal_dist_end":0.24096,"object_to_goal_dist_start":0.24096,"object_z_max":0.01602,"peak_contact_force":9749.01569,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8283.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.63614,0.14296,0.3099],"tcp_start":[0.55459,0.01725,0.20921],"tcp_to_object_dist_end":0.32843,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.55939,0.01801,0.01602],"object_pos_start":[0.55939,0.01801,0.01602],"object_to_goal_dist_end":0.24096,"object_to_goal_dist_start":0.24096,"object_z_max":0.01602,"peak_contact_force":273004.34378,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4455.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64381,0.15678,0.20579],"tcp_start":[0.63614,0.14296,0.3099],"tcp_to_object_dist_end":0.24979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55939,0.01801,0.01602],"object_pos_start":[0.55939,0.01801,0.01602],"object_to_goal_dist_end":0.24096,"object_to_goal_dist_start":0.24096,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63866,0.15525,0.22487],"tcp_start":[0.64381,0.15678,0.20579],"tcp_to_object_dist_end":0.26218,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```