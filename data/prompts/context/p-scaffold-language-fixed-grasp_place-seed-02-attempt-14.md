## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0450 | 0.36 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | admittance_control | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0401 | 0.37 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.1661 | 0.30 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | admittance_control | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0038 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0062 | 0.44 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.045) — your mutation base

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

- **Composite score**: -0.045
- **task_score** (E): 0.361
- **fitness_score**: 0.655  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1465 |
| descend_1 | 1.00 | 1.00 | 0.1173 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 0.00 | 1.00 | 0.0996 |
| transport_1 | 0.67 | 1.00 | 0.2156 |
| place_1 | 1.00 | 1.00 | 0.0007 |
| release_1 | 1.00 | 1.00 | 0.0203 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.013, 0.160) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 27.129 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.491, -0.013, 0.160)→(0.488, -0.015, 0.042) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.042)→(0.480, -0.015, 0.034) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.133 | 0.171 |
| lift_1 | lift | 0.00 / step_budget | (0.480, -0.015, 0.034)→(0.483, -0.015, 0.134) | (0.493, -0.015, 0.026)→(0.491, -0.015, 0.117) | 0.281→0.247 | 1.00 / 34.000 | 0.061 | 0.495 |
| transport_1 | approach | 0.67 / step_budget | (0.483, -0.015, 0.134)→(0.611, 0.146, 0.191) | (0.491, -0.015, 0.117)→(0.596, 0.124, 0.055) | 0.247→0.144 | 1.00 / 16.333 | 0.117 | 1.407 |
| place_1 | descend | 1.00 / step_budget | (0.632, 0.173, 0.189)→(0.632, 0.174, 0.189) | (0.596, 0.124, 0.055)→(0.598, 0.127, 0.051) | 0.144→0.140 | 1.00 / 10.333 | 91001.472 | 0.163 |
| release_1 | release | 1.00 / step_budget | (0.632, 0.174, 0.189)→(0.627, 0.172, 0.209) | (0.603, 0.130, 0.049)→(0.596, 0.129, 0.019) | 0.134→0.163 | 1.00 / 4.000 | 0.126 | 0.522 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.550
- phase_score: 0.476
- phase_breakdown.transport_arc_score: 0.375
- phase_breakdown.approach_1_score: 0.053
- phase_breakdown.descend_1_score: 0.706
- phase_breakdown.release_1_score: 0.311
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.550
- **Median Q (composite search score)**: -0.073
- **K-run variance**: 0.0055
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88095,"average_solve_count":294.0,"average_success_count":294.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15339,"approach_1.speed":0.05125,"descend_1.grasp_z_offset":0.01735,"descend_1.speed":0.02954,"lift_1.lift_height":0.20587,"lift_1.speed":0.01517,"place_1.place_z_offset":0.02254,"place_1.speed":0.03091,"release_1.duration":0.32351,"transport_1.arc_height":0.1954,"transport_1.speed":0.39962},"optimized_scores":{"best_composite_score":-0.07278,"best_fitness_score":0.62722,"best_task_score":0.30783},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":365.0,"contact_point_centroid":[0.60764,0.1395,-0.00535],"force_p95":0.9851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.23113,"mean_force":0.2562,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60013,0.12788,0.21622]},{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.47174,-0.01955,-0.00119],"force_p95":0.39616,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44398,"mean_force":0.09608,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46294,-0.0197,0.0395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9462.0,"contact_point_centroid":[0.49917,-0.00313,0.18699],"force_p95":0.16134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39807,"mean_force":0.08188,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49603,0.01566,0.1864]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11179.0,"contact_point_centroid":[0.50828,0.04316,0.19563],"force_p95":0.10626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35283,"mean_force":0.0697,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50445,0.02476,0.1946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19695.0,"contact_point_centroid":[0.46319,-0.00046,0.08576],"force_p95":0.07396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24699,"mean_force":0.05099,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46334,-0.01964,0.0836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20941.0,"contact_point_centroid":[0.46312,-0.03875,0.08599],"force_p95":0.07048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24628,"mean_force":0.0485,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46336,-0.01964,0.08411]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02008,-0.00204],"force_p95":0.13414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17136,"mean_force":0.1258,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46539,-0.01976,0.03914]},{"body_a":"world","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48751,-0.00839,0.24705]},{"body_a":"world","body_b":"grasp_target","contact_count":9256.0,"contact_point_centroid":[0.60746,0.13956,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12522,"mean_force":0.12265,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62071,0.15178,0.20359]},{"body_a":"world","body_b":"grasp_target","contact_count":3772.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4722,-0.0187,0.11567]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60746,0.13956,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62394,0.15697,0.20838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5083.0,"contact_point_centroid":[0.46379,-0.00048,0.04073],"force_p95":0.06565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09576,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4643,-0.01973,0.03804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5380.0,"contact_point_centroid":[0.46369,-0.03898,0.04018],"force_p95":0.06456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0839,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4643,-0.01973,0.03805]},{"body_a":"left_finger","body_b":"right_finger","contact_count":177.0,"contact_point_centroid":[0.60476,0.13228,0.21497],"force_p95":0.01424,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01518,"mean_force":0.01199,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60427,0.13228,0.21276]},{"body_a":"left_finger","body_b":"right_finger","contact_count":9817.0,"contact_point_centroid":[0.62083,0.15183,0.20588],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.0105,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62075,0.15182,0.20361]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62635,0.15773,0.20725],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01011,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62638,0.15772,0.205]}],"total_contact_groups":16},"final_pose_error":0.00607,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60746,0.13956,0.01602],"final_tcp_position":[0.6276,0.15806,0.20798],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.24828,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1408.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4759,-0.01753,0.19297],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":943.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3772.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47172,-0.01991,0.04555],"tcp_start":[0.4759,-0.01753,0.19297],"tcp_to_object_dist_end":0.02003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01979,0.02585],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28831,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13273,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12263.0,"raw_peak_contact_force":0.17136,"subtask_id":"grasp_1","tcp_end":[0.46427,-0.01973,0.03802],"tcp_start":[0.47172,-0.01991,0.04555],"tcp_to_object_dist_end":0.01694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47213,-0.01952,0.11109],"object_pos_start":[0.47606,-0.01979,0.02585],"object_to_goal_dist_end":0.25207,"object_to_goal_dist_start":0.28831,"object_z_max":0.11102,"peak_contact_force":0.07532,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40805.0,"raw_peak_contact_force":0.44398,"tcp_end":[0.4662,-0.01964,0.12966],"tcp_start":[0.46427,-0.01973,0.03802],"tcp_to_object_dist_end":0.01949,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60745,0.13957,0.01651],"object_pos_start":[0.47213,-0.01952,0.11109],"object_to_goal_dist_end":0.17624,"object_to_goal_dist_start":0.25207,"object_z_max":0.20674,"peak_contact_force":0.12231,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21183.0,"raw_peak_contact_force":2.23113,"subtask_id":"transport_arc","tcp_end":[0.60695,0.13558,0.20976],"tcp_start":[0.4662,-0.01964,0.12966],"tcp_to_object_dist_end":0.19329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2314.0,"n_steps_budget":1000.0,"object_pos_end":[0.60746,0.13956,0.01602],"object_pos_start":[0.60745,0.13957,0.01651],"object_to_goal_dist_end":0.17673,"object_to_goal_dist_start":0.17624,"object_z_max":0.01651,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19073.0,"raw_peak_contact_force":0.12522,"tcp_end":[0.6276,0.15806,0.20798],"tcp_start":[0.62728,0.15776,0.20765],"tcp_to_object_dist_end":0.1939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60746,0.13956,0.01602],"object_pos_start":[0.60746,0.13956,0.01602],"object_to_goal_dist_end":0.17673,"object_to_goal_dist_start":0.17673,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62254,0.15653,0.22777],"tcp_start":[0.6276,0.15806,0.20798],"tcp_to_object_dist_end":0.21296,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.79772,"average_solve_count":351.0,"average_success_count":351.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13752,"approach_1.speed":0.02167,"descend_1.grasp_z_offset":0.00471,"descend_1.speed":0.03914,"lift_1.lift_height":0.17853,"lift_1.speed":0.02048,"place_1.place_z_offset":0.04276,"place_1.speed":0.01288,"release_1.duration":0.26844,"transport_1.arc_height":0.10705,"transport_1.speed":0.32987},"optimized_scores":{"best_composite_score":0.05644,"best_fitness_score":0.75644,"best_task_score":0.54981},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":247.0,"contact_point_centroid":[0.6115,0.20297,-0.00497],"force_p95":1.01108,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31934,"mean_force":0.27749,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61967,0.2043,0.16069]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.45408,-0.0254,-0.00121],"force_p95":0.48611,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56479,"mean_force":0.12006,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44565,-0.02569,0.02767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14057.0,"contact_point_centroid":[0.51672,0.04218,0.1838],"force_p95":0.11724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44727,"mean_force":0.07533,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51401,0.06115,0.18347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16176.0,"contact_point_centroid":[0.52737,0.09375,0.18747],"force_p95":0.09347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32945,"mean_force":0.06184,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52483,0.07516,0.1864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":33284.0,"contact_point_centroid":[0.61945,0.1782,0.14686],"force_p95":0.11642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24133,"mean_force":0.06758,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.6167,0.19718,0.14684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19091.0,"contact_point_centroid":[0.44645,-0.00639,0.07774],"force_p95":0.07488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23921,"mean_force":0.05246,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44646,-0.02558,0.07529]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21069.0,"contact_point_centroid":[0.4463,-0.04466,0.07851],"force_p95":0.07054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23717,"mean_force":0.04831,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44652,-0.02558,0.07647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":40817.0,"contact_point_centroid":[0.61767,0.21539,0.14675],"force_p95":0.10392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22146,"mean_force":0.0561,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61624,0.1966,0.14679]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02616,-0.00205],"force_p95":0.13769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18871,"mean_force":0.12673,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44803,-0.02578,0.02723]},{"body_a":"world","body_b":"grasp_target","contact_count":1712.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47955,-0.01121,0.2391]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":490.0,"contact_point_centroid":[0.62869,0.22399,0.14261],"force_p95":0.13791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13842,"mean_force":0.09797,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6237,0.20586,0.14793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":491.0,"contact_point_centroid":[0.62778,0.18772,0.14397],"force_p95":0.13528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13822,"mean_force":0.095,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6237,0.20586,0.14793]},{"body_a":"world","body_b":"grasp_target","contact_count":3644.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45534,-0.02464,0.10183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4822.0,"contact_point_centroid":[0.44678,-0.0065,0.02852],"force_p95":0.06789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09494,"mean_force":0.04491,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44696,-0.02574,0.02622]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5404.0,"contact_point_centroid":[0.44629,-0.04497,0.02782],"force_p95":0.06481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08424,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44696,-0.02574,0.02622]}],"total_contact_groups":15},"final_pose_error":0.00686,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61175,0.2045,0.02637],"final_tcp_position":[0.62562,0.20654,0.15199],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":81.14225,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45963,-0.02335,0.17699],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45424,-0.02601,0.03315],"tcp_start":[0.45963,-0.02335,0.17699],"tcp_to_object_dist_end":0.00835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02574,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30333,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13494,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12026.0,"raw_peak_contact_force":0.18871,"subtask_id":"grasp_1","tcp_end":[0.44693,-0.02574,0.02619],"tcp_start":[0.45424,-0.02601,0.03315],"tcp_to_object_dist_end":0.01151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45845,-0.02546,0.11681],"object_pos_start":[0.45844,-0.02574,0.02582],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.30333,"object_z_max":0.11673,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40326.0,"raw_peak_contact_force":0.56479,"tcp_end":[0.44969,-0.02557,0.12465],"tcp_start":[0.44693,-0.02574,0.02619],"tcp_to_object_dist_end":0.01176,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61096,0.18778,0.1324],"object_pos_start":[0.45845,-0.02546,0.11681],"object_to_goal_dist_end":0.03345,"object_to_goal_dist_start":0.28998,"object_z_max":0.20276,"peak_contact_force":0.10645,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30233.0,"raw_peak_contact_force":0.44727,"subtask_id":"transport_arc","tcp_end":[0.61105,0.18719,0.15419],"tcp_start":[0.44969,-0.02557,0.12465],"tcp_to_object_dist_end":0.0218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":2412.0,"n_steps_budget":1000.0,"object_pos_end":[0.61682,0.19629,0.12073],"object_pos_start":[0.61096,0.18778,0.1324],"object_to_goal_dist_end":0.01906,"object_to_goal_dist_start":0.03345,"object_z_max":0.1324,"peak_contact_force":0.13625,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":74101.0,"raw_peak_contact_force":0.24133,"tcp_end":[0.62562,0.20654,0.15199],"tcp_start":[0.62522,0.20603,0.15198],"tcp_to_object_dist_end":0.03405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61175,0.2045,0.02637],"object_pos_start":[0.63019,0.20681,0.11546],"object_to_goal_dist_end":0.08973,"object_to_goal_dist_start":0.00194,"object_z_max":0.11546,"peak_contact_force":0.13199,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1228.0,"raw_peak_contact_force":1.31934,"subtask_id":"release_1","tcp_end":[0.6196,0.20428,0.1714],"tcp_start":[0.62562,0.20654,0.15199],"tcp_to_object_dist_end":0.14524,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24528,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07214,"approach_1.speed":0.06413,"descend_1.grasp_z_offset":-0.00227,"descend_1.speed":0.04062,"lift_1.lift_height":0.21231,"lift_1.speed":0.06745,"place_1.place_z_offset":0.02201,"place_1.speed":0.02963,"release_1.duration":0.11503,"transport_1.arc_height":0.19824,"transport_1.speed":0.17621},"optimized_scores":{"best_composite_score":-0.11863,"best_fitness_score":0.58137,"best_task_score":0.22601},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2604.0,"contact_point_centroid":[0.56994,0.04368,-0.00237],"force_p95":0.1257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54262,"mean_force":0.13888,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58301,0.07316,0.20736]},{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.54122,0.00056,-0.00114],"force_p95":0.36472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4764,"mean_force":0.0724,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52716,0.00083,0.04046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14576.0,"contact_point_centroid":[0.53195,-0.01796,0.09041],"force_p95":0.10541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3076,"mean_force":0.06881,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52872,0.00077,0.08895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14391.0,"contact_point_centroid":[0.53205,0.01948,0.08871],"force_p95":0.10613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2892,"mean_force":0.06974,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52862,0.00077,0.08737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2294.0,"contact_point_centroid":[0.54444,0.03018,0.16181],"force_p95":0.15081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27326,"mean_force":0.10562,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53875,0.01198,0.16453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2381.0,"contact_point_centroid":[0.5442,-0.00652,0.16122],"force_p95":0.14591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26189,"mean_force":0.10224,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53852,0.01161,0.16398]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13209,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15326,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52998,0.00089,0.04048]},{"body_a":"world","body_b":"grasp_target","contact_count":2664.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51727,0.00049,0.20341]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53563,0.00098,0.0676]},{"body_a":"world","body_b":"grasp_target","contact_count":9844.0,"contact_point_centroid":[0.57001,0.04369,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63068,0.14112,0.20289]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57001,0.04369,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6401,0.15585,0.20809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.53006,-0.01834,0.04178],"force_p95":0.07627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12135,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52877,0.00087,0.03906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.52999,0.01994,0.04091],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09428,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52877,0.00087,0.03906]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2511.0,"contact_point_centroid":[0.5862,0.07724,0.21125],"force_p95":0.01131,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.586,0.07724,0.20896]},{"body_a":"left_finger","body_b":"right_finger","contact_count":10412.0,"contact_point_centroid":[0.63075,0.14119,0.2052],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01053,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63073,0.14118,0.20291]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.64266,0.15661,0.20735],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64257,0.15659,0.20506]}],"total_contact_groups":16},"final_pose_error":0.0064,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57001,0.04369,0.01602],"final_tcp_position":[0.64377,0.15692,0.20814],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.949,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2664.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53721,0.001,0.10898],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53687,0.001,0.04865],"tcp_start":[0.53721,0.001,0.10898],"tcp_to_object_dist_end":0.02382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00076,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13036,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.15326,"subtask_id":"grasp_1","tcp_end":[0.52874,0.00087,0.03902],"tcp_start":[0.53687,0.001,0.04865],"tcp_to_object_dist_end":0.0203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54358,0.00071,0.12409],"object_pos_start":[0.5442,0.00076,0.02588],"object_to_goal_dist_end":0.20021,"object_to_goal_dist_start":0.25049,"object_z_max":0.12401,"peak_contact_force":0.10753,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29147.0,"raw_peak_contact_force":0.4764,"tcp_end":[0.53354,0.00075,0.14761],"tcp_start":[0.52874,0.00087,0.03902],"tcp_to_object_dist_end":0.02557,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57001,0.04369,0.01602],"object_pos_start":[0.54358,0.00071,0.12409],"object_to_goal_dist_end":0.22308,"object_to_goal_dist_start":0.20021,"object_z_max":0.15416,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9790.0,"raw_peak_contact_force":1.54262,"subtask_id":"transport_arc","tcp_end":[0.6145,0.11634,0.20896],"tcp_start":[0.53354,0.00075,0.14761],"tcp_to_object_dist_end":0.21091,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2461.0,"n_steps_budget":1000.0,"object_pos_end":[0.57001,0.04369,0.01602],"object_pos_start":[0.57001,0.04369,0.01602],"object_to_goal_dist_end":0.22308,"object_to_goal_dist_start":0.22308,"object_z_max":0.01602,"peak_contact_force":273004.15817,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20256.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64377,0.15692,0.20814],"tcp_start":[0.64319,0.1561,0.20824],"tcp_to_object_dist_end":0.23488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57001,0.04369,0.01602],"object_pos_start":[0.57001,0.04369,0.01602],"object_to_goal_dist_end":0.22308,"object_to_goal_dist_start":0.22308,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.6387,0.15541,0.22727],"tcp_start":[0.64377,0.15692,0.20814],"tcp_to_object_dist_end":0.24864,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```