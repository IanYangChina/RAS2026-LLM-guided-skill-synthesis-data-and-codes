## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | admittance_control | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0401 | 0.37 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.1661 | 0.30 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | admittance_control | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0038 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0062 | 0.44 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | admittance_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0179 | 0.41 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.040) — your mutation base

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

- **Composite score**: -0.040
- **task_score** (E): 0.370
- **fitness_score**: 0.660  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1470 |
| descend_1 | 1.00 | 1.00 | 0.1181 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 0.00 | 1.00 | 0.0966 |
| transport_1 | 0.33 | 1.00 | 0.1677 |
| place_1 | 0.67 | 1.00 | 0.0265 |
| release_1 | 1.00 | 1.00 | 0.0213 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.013, 0.159) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.491, -0.013, 0.159)→(0.488, -0.015, 0.041) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.041)→(0.480, -0.015, 0.033) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.333 | 0.133 | 0.169 |
| lift_1 | lift | 0.00 / step_budget | (0.480, -0.015, 0.033)→(0.483, -0.015, 0.130) | (0.493, -0.015, 0.026)→(0.491, -0.015, 0.114) | 0.281→0.249 | 1.00 / 39.333 | 0.077 | 0.561 |
| transport_1 | approach | 0.33 / guard_failure | (0.498, 0.007, 0.160)→(0.602, 0.132, 0.196) | (0.491, -0.015, 0.114)→(0.555, 0.063, 0.160) | 0.249→0.143 | 1.00 / 17.000 | 0.055 | 0.381 |
| place_1 | descend | 0.67 / step_budget | (0.602, 0.132, 0.196)→(0.611, 0.146, 0.180) | (0.605, 0.133, 0.168)→(0.630, 0.154, 0.016) | 0.061→0.155 | 1.00 / 8.000 | 3249.689 | 1.646 |
| release_1 | release | 1.00 / step_budget | (0.611, 0.146, 0.180)→(0.606, 0.145, 0.201) | (0.630, 0.154, 0.016)→(0.630, 0.154, 0.016) | 0.155→0.155 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.518
- phase_score: 0.443
- phase_breakdown.transport_arc_score: 0.282
- phase_breakdown.approach_1_score: 0.045
- phase_breakdown.descend_1_score: 0.739
- phase_breakdown.release_1_score: 0.416
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.740

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.740
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.518
- **Median Q (composite search score)**: -0.063
- **K-run variance**: 0.0034
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.253


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98601,"average_solve_count":286.0,"average_success_count":286.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13842,"approach_1.speed":0.04303,"descend_1.grasp_z_offset":0.00633,"descend_1.speed":0.02,"lift_1.lift_height":0.23048,"lift_1.speed":0.04745,"place_1.place_z_offset":0.01346,"place_1.speed":0.02886,"release_1.duration":0.20547,"transport_1.arc_height":0.24372,"transport_1.speed":0.14672},"optimized_scores":{"best_composite_score":-0.06259,"best_fitness_score":0.63741,"best_task_score":0.31321},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2020.0,"contact_point_centroid":[0.6378,0.1615,-0.00248],"force_p95":0.19191,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70193,"mean_force":0.14463,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62389,0.15457,0.19201]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.47274,-0.0196,-0.00115],"force_p95":0.47705,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64179,"mean_force":0.096,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4627,-0.01971,0.0285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8819.0,"contact_point_centroid":[0.5197,0.01932,0.18354],"force_p95":0.14792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37002,"mean_force":0.07937,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51658,0.03811,0.18352]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9712.0,"contact_point_centroid":[0.52482,0.06146,0.18571],"force_p95":0.11171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36578,"mean_force":0.07317,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52108,0.04296,0.18539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.62224,0.166,0.18691],"force_p95":0.12711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36358,"mean_force":0.08631,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61744,0.14845,0.18798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2658.0,"contact_point_centroid":[0.6224,0.12992,0.18589],"force_p95":0.17346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3217,"mean_force":0.12267,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61725,0.14826,0.1879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20404.0,"contact_point_centroid":[0.46269,-0.00048,0.07795],"force_p95":0.07262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28391,"mean_force":0.0498,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46284,-0.01964,0.07608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20584.0,"contact_point_centroid":[0.46268,-0.03879,0.07716],"force_p95":0.07229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28045,"mean_force":0.0496,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46282,-0.01964,0.07547]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02004,-0.00203],"force_p95":0.13351,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17024,"mean_force":0.12567,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46523,-0.01977,0.02804]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48716,-0.00859,0.23938]},{"body_a":"world","body_b":"grasp_target","contact_count":3808.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4719,-0.01886,0.10246]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63786,0.1615,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62323,0.1564,0.19468]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5075.0,"contact_point_centroid":[0.46366,-0.0005,0.03003],"force_p95":0.06606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09013,"mean_force":0.04288,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01975,0.02696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5385.0,"contact_point_centroid":[0.46356,-0.039,0.02943],"force_p95":0.06442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08402,"mean_force":0.04121,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46413,-0.01975,0.02696]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1908.0,"contact_point_centroid":[0.62426,0.15486,0.19446],"force_p95":0.01171,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01552,"mean_force":0.01075,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.6242,0.15485,0.19223]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.626,0.15719,0.19374],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6258,0.15718,0.19126]}],"total_contact_groups":16},"final_pose_error":0.01034,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63786,0.1615,0.01602],"final_tcp_position":[0.62708,0.15752,0.19424],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.70193,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1604.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47548,-0.01784,0.17787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3808.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47164,-0.01993,0.03442],"tcp_start":[0.47548,-0.01784,0.17787],"tcp_to_object_dist_end":0.00955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01976,0.02586],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2883,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13192,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12260.0,"raw_peak_contact_force":0.17024,"subtask_id":"grasp_1","tcp_end":[0.4641,-0.01975,0.02693],"tcp_start":[0.47164,-0.01993,0.03442],"tcp_to_object_dist_end":0.01198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47484,-0.01955,0.11227],"object_pos_start":[0.47603,-0.01976,0.02586],"object_to_goal_dist_end":0.25002,"object_to_goal_dist_start":0.2883,"object_z_max":0.1122,"peak_contact_force":0.06943,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41150.0,"raw_peak_contact_force":0.64179,"tcp_end":[0.4653,-0.01963,0.12175],"tcp_start":[0.4641,-0.01975,0.02693],"tcp_to_object_dist_end":0.01344,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.62109,0.14607,0.16652],"object_pos_start":[0.47484,-0.01955,0.11227],"object_to_goal_dist_end":0.02883,"object_to_goal_dist_start":0.25002,"object_z_max":0.19844,"peak_contact_force":0.16371,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18531.0,"raw_peak_contact_force":0.37002,"subtask_id":"transport_arc","tcp_end":[0.61715,0.14585,0.19298],"tcp_start":[0.4653,-0.01963,0.12175],"tcp_to_object_dist_end":0.02675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.63786,0.1615,0.01602],"object_pos_start":[0.62109,0.14607,0.16652],"object_to_goal_dist_end":0.17413,"object_to_goal_dist_start":0.02883,"object_z_max":0.16652,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10669.0,"raw_peak_contact_force":1.70193,"tcp_end":[0.62708,0.15752,0.19424],"tcp_start":[0.61715,0.14585,0.19298],"tcp_to_object_dist_end":0.17859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63786,0.1615,0.01602],"object_pos_start":[0.63786,0.1615,0.01602],"object_to_goal_dist_end":0.17413,"object_to_goal_dist_start":0.17413,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62175,0.15594,0.21408],"tcp_start":[0.62708,0.15752,0.19424],"tcp_to_object_dist_end":0.19879,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19502,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14578,"approach_1.speed":0.05477,"descend_1.grasp_z_offset":0.00704,"descend_1.speed":0.03066,"lift_1.lift_height":0.16877,"lift_1.speed":0.05149,"place_1.place_z_offset":0.00804,"place_1.speed":0.03325,"release_1.duration":0.30369,"transport_1.arc_height":0.17926,"transport_1.speed":0.191},"optimized_scores":{"best_composite_score":0.03994,"best_fitness_score":0.73994,"best_task_score":0.51755},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1381.0,"contact_point_centroid":[0.64065,0.21248,-0.00254],"force_p95":0.3414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34373,"mean_force":0.15656,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61651,0.19586,0.13618]},{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.45588,-0.0255,-0.00116],"force_p95":0.45898,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62442,"mean_force":0.09284,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44578,-0.02569,0.0302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7798.0,"contact_point_centroid":[0.51167,0.03407,0.19491],"force_p95":0.16692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50051,"mean_force":0.08909,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50839,0.05292,0.19473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9273.0,"contact_point_centroid":[0.51671,0.07776,0.20034],"force_p95":0.11041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41434,"mean_force":0.07185,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51338,0.05942,0.1999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5038.0,"contact_point_centroid":[0.61568,0.1705,0.14866],"force_p95":0.17445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33284,"mean_force":0.11546,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61112,0.18933,0.15091]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20494.0,"contact_point_centroid":[0.44668,-0.04476,0.0807],"force_p95":0.07149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26723,"mean_force":0.04972,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44688,-0.0256,0.07901]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10185.0,"contact_point_centroid":[0.61304,0.2073,0.14995],"force_p95":0.11848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26211,"mean_force":0.05293,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61144,0.18977,0.14972]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20609.0,"contact_point_centroid":[0.44676,-0.00645,0.08175],"force_p95":0.07064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26051,"mean_force":0.04914,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44693,-0.0256,0.07979]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.0262,-0.00205],"force_p95":0.13778,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18847,"mean_force":0.12673,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44812,-0.02578,0.02962]},{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47976,-0.01118,0.24289]},{"body_a":"world","body_b":"grasp_target","contact_count":3796.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45549,-0.02458,0.10695]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64094,0.21276,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6136,0.1962,0.13245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5306.0,"contact_point_centroid":[0.44635,-0.00649,0.03027],"force_p95":0.06488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09576,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44705,-0.02574,0.02861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5400.0,"contact_point_centroid":[0.44636,-0.04502,0.03005],"force_p95":0.06505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08706,"mean_force":0.04122,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44705,-0.02574,0.02861]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1154.0,"contact_point_centroid":[0.61687,0.19626,0.1377],"force_p95":0.01283,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01087,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61685,0.19625,0.13535]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.61667,0.19732,0.13126],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61662,0.19731,0.12894]}],"total_contact_groups":16},"final_pose_error":0.01867,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.64094,0.21276,0.01602],"final_tcp_position":[0.61818,0.19781,0.13203],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.82239,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45995,-0.02323,0.18496],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":949.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3796.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45427,-0.02601,0.03551],"tcp_start":[0.45995,-0.02323,0.18496],"tcp_to_object_dist_end":0.01042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.0258,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30338,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13594,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12506.0,"raw_peak_contact_force":0.18847,"subtask_id":"grasp_1","tcp_end":[0.44703,-0.02574,0.02858],"tcp_start":[0.45427,-0.02601,0.03551],"tcp_to_object_dist_end":0.01175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45898,-0.02555,0.11911],"object_pos_start":[0.45844,-0.0258,0.02582],"object_to_goal_dist_end":0.28976,"object_to_goal_dist_start":0.30338,"object_z_max":0.11902,"peak_contact_force":0.07225,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41261.0,"raw_peak_contact_force":0.62442,"tcp_end":[0.45042,-0.02561,0.12957],"tcp_start":[0.44703,-0.02574,0.02858],"tcp_to_object_dist_end":0.01352,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.45888,-0.02471,0.12147],"object_pos_start":[0.45898,-0.02555,0.11911],"object_to_goal_dist_end":0.28919,"object_to_goal_dist_start":0.28976,"object_z_max":0.21797,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17071.0,"raw_peak_contact_force":0.50051,"subtask_id":"transport_arc","tcp_end":[0.61047,0.18535,0.16984],"tcp_start":[0.45015,-0.02481,0.13196],"tcp_to_object_dist_end":0.26352,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64094,0.21276,0.01602],"object_pos_start":[0.60954,0.18543,0.14544],"object_to_goal_dist_end":0.0988,"object_to_goal_dist_start":0.04386,"object_z_max":0.14544,"peak_contact_force":9748.82239,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17758.0,"raw_peak_contact_force":1.34373,"tcp_end":[0.61818,0.19781,0.13203],"tcp_start":[0.61047,0.18535,0.16984],"tcp_to_object_dist_end":0.11917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64094,0.21276,0.01602],"object_pos_start":[0.64094,0.21276,0.01602],"object_to_goal_dist_end":0.0988,"object_to_goal_dist_start":0.0988,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61179,0.19553,0.1519],"tcp_start":[0.61818,0.19781,0.13203],"tcp_to_object_dist_end":0.14003,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0663,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07824,"approach_1.speed":0.05488,"descend_1.grasp_z_offset":0.0083,"descend_1.speed":0.04092,"lift_1.lift_height":0.20592,"lift_1.speed":0.05854,"place_1.place_z_offset":0.01342,"place_1.speed":0.0237,"release_1.duration":0.32014,"transport_1.arc_height":0.14059,"transport_1.speed":0.18124},"optimized_scores":{"best_composite_score":-0.09755,"best_fitness_score":0.60245,"best_task_score":0.27801},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3641.0,"contact_point_centroid":[0.61178,0.08785,-0.00231],"force_p95":0.12451,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89318,"mean_force":0.13598,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58281,0.07672,0.21659]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.54057,0.0006,-0.00114],"force_p95":0.21922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41661,"mean_force":0.06841,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52747,0.00084,0.04581]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18355.0,"contact_point_centroid":[0.53007,-0.01827,0.09115],"force_p95":0.0841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29012,"mean_force":0.05575,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52891,0.00078,0.08962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.58362,0.08174,0.22109],"force_p95":0.19695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28375,"mean_force":0.05726,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57726,0.0665,0.22586]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18592.0,"contact_point_centroid":[0.53046,0.01981,0.0905],"force_p95":0.0825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27384,"mean_force":0.05513,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52886,0.00078,0.08876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4148.0,"contact_point_centroid":[0.55017,0.00252,0.18339],"force_p95":0.14456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27266,"mean_force":0.08133,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54539,0.02119,0.18371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4417.0,"contact_point_centroid":[0.55145,0.0411,0.18496],"force_p95":0.12075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26755,"mean_force":0.07686,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54633,0.02249,0.18515]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14763,"mean_force":0.12515,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53038,0.0009,0.04565]},{"body_a":"world","body_b":"grasp_target","contact_count":2664.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5173,0.00049,0.20637]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53586,0.00099,0.07309]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61182,0.08784,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58451,0.08316,0.21646]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4122.0,"contact_point_centroid":[0.53032,-0.01832,0.04695],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10387,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52918,0.00088,0.04422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4869.0,"contact_point_centroid":[0.53027,0.01995,0.04608],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09371,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52918,0.00088,0.04422]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.58568,0.05113,0.21972],"force_p95":0.06718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06816,"mean_force":0.05833,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57785,0.06613,0.22658]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3648.0,"contact_point_centroid":[0.58313,0.07716,0.21873],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01054,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58313,0.07715,0.21645]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.58695,0.08359,0.2145],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5869,0.08359,0.2121]}],"total_contact_groups":16},"final_pose_error":0.09575,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61182,0.08784,0.01602],"final_tcp_position":[0.58814,0.08374,0.21471],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.89318,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2664.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53716,0.001,0.11499],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53721,0.00101,0.05383],"tcp_start":[0.53716,0.001,0.11499],"tcp_to_object_dist_end":0.0287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00077,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12985,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.14763,"subtask_id":"grasp_1","tcp_end":[0.52915,0.00088,0.04419],"tcp_start":[0.53721,0.00101,0.05383],"tcp_to_object_dist_end":0.02371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5382,0.00095,0.11171],"object_pos_start":[0.54422,0.00077,0.02588],"object_to_goal_dist_end":0.20729,"object_to_goal_dist_start":0.25048,"object_z_max":0.11161,"peak_contact_force":0.08853,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37163.0,"raw_peak_contact_force":0.41661,"tcp_end":[0.53298,0.00076,0.13817],"tcp_start":[0.52915,0.00088,0.04419],"tcp_to_object_dist_end":0.02697,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.58493,0.06621,0.19336],"object_pos_start":[0.5382,0.00095,0.11171],"object_to_goal_dist_end":0.11125,"object_to_goal_dist_start":0.20729,"object_z_max":0.19379,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8565.0,"raw_peak_contact_force":0.27266,"subtask_id":"transport_arc","tcp_end":[0.57785,0.06613,0.22658],"tcp_start":[0.57773,0.06562,0.22649],"tcp_to_object_dist_end":0.03396,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61182,0.08784,0.01602],"object_pos_start":[0.58564,0.06741,0.19279],"object_to_goal_dist_end":0.19202,"object_to_goal_dist_start":0.10985,"object_z_max":0.19279,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7365.0,"raw_peak_contact_force":1.89318,"tcp_end":[0.58814,0.08374,0.21471],"tcp_start":[0.57785,0.06613,0.22658],"tcp_to_object_dist_end":0.20014,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61182,0.08784,0.01602],"object_pos_start":[0.61182,0.08784,0.01602],"object_to_goal_dist_end":0.19202,"object_to_goal_dist_start":0.19202,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58314,0.08292,0.23649],"tcp_start":[0.58814,0.08374,0.21471],"tcp_to_object_dist_end":0.22238,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```