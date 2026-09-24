## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0794 | 0.37 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0206 | 0.39 | ✅ accepted |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1650 | 0.13 | ❌ rejected |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1646 | 0.13 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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

## Current Skill (Q=-0.079) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_to_object
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
    - 0.12
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_grasp
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp
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
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 20.0
      binds_to:
      - path: guards.grasp_check.threshold
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_place
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
- id: release_object
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
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_from_goal
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grip_force: status=consumed; consumers=guards.grasp_check.threshold (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_from_goal** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.079
- **task_score** (E): 0.374
- **fitness_score**: 0.651  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1489 |
| descend_to_grasp | 1.00 | 1.00 | 0.1031 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1368 |
| transport_to_goal | 1.00 | 1.00 | 0.2352 |
| descend_to_place | 1.00 | 1.00 | 0.0764 |
| release_object | 1.00 | 1.00 | 0.0200 |
| retract_from_goal | 1.00 | 1.00 | 0.0254 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.157) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.157)→(0.510, -0.017, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.054)→(0.502, -0.017, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.667 | 0.134 | 0.168 |
| lift_object | lift | 1.00 / step_budget | (0.502, -0.017, 0.045)→(0.511, -0.016, 0.182) | (0.515, -0.017, 0.026)→(0.517, -0.016, 0.157) | 0.270→0.229 | 1.00 / 38.333 | 0.075 | 0.391 |
| transport_to_goal | approach | 1.00 / step_budget | (0.511, -0.016, 0.182)→(0.608, 0.167, 0.281) | (0.517, -0.016, 0.157)→(0.607, 0.148, 0.161) | 0.229→0.125 | 1.00 / 20.333 | 0.116 | 0.777 |
| descend_to_place | descend | 1.00 / step_budget | (0.608, 0.167, 0.281)→(0.613, 0.178, 0.206) | (0.607, 0.148, 0.161)→(0.611, 0.155, 0.110) | 0.125→0.077 | 1.00 / 17.667 | 0.123 | 0.233 |
| release_object | release | 1.00 / step_budget | (0.613, 0.178, 0.206)→(0.607, 0.176, 0.225) | (0.611, 0.155, 0.110)→(0.604, 0.154, 0.017) | 0.077→0.158 | 1.00 / 3.333 | 0.239 | 1.114 |
| retract_from_goal | retract | 1.00 / step_budget | (0.607, 0.176, 0.225)→(0.613, 0.180, 0.250) | (0.604, 0.154, 0.017)→(0.605, 0.152, 0.021) | 0.158→0.154 | 1.00 / 3.333 | 0.168 | 0.242 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.516
- phase_score: 0.000
- phase_breakdown.descend_1_score: 0.000
- phase_breakdown.grasp_1_score: 0.000
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.approach_1_score: 0.000
- phase_breakdown.release_1_score: 0.000
- grasp_place_fitness: 0.720

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.720
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.516
- **Median Q (composite search score)**: -0.090
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.388


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34219,"average_solve_count":301.0,"average_success_count":301.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.06438,"descend_to_grasp.speed":0.03312,"descend_to_place.place_z_offset":0.02689,"descend_to_place.speed":0.07145,"grasp.grip_force":24.88944,"lift_object.lift_height":0.2043,"lift_object.speed":0.03826,"release_object.release_duration":0.84382,"retract_from_goal.speed":0.07419,"transport_to_goal.arc_height":0.03145,"transport_to_goal.speed":0.14993},"optimized_scores":{"best_composite_score":-0.13866,"best_fitness_score":0.59134,"best_task_score":0.25411},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":797.0,"contact_point_centroid":[0.59491,0.15458,-0.00379],"force_p95":0.8183,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05564,"mean_force":0.19524,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59222,0.17427,0.31505]},{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.53324,-0.02064,-0.00134],"force_p95":0.3743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40301,"mean_force":0.10883,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52188,-0.0208,0.04544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6071.0,"contact_point_centroid":[0.55045,0.04996,0.25186],"force_p95":0.10652,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28683,"mean_force":0.0712,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54657,0.03119,0.25171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19325.0,"contact_point_centroid":[0.526,-0.00164,0.12862],"force_p95":0.07561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25309,"mean_force":0.05288,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52566,-0.02077,0.12653]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6002.0,"contact_point_centroid":[0.54984,0.01013,0.25077],"force_p95":0.1197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25287,"mean_force":0.07059,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54585,0.02891,0.25039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20019.0,"contact_point_centroid":[0.52604,-0.03989,0.127],"force_p95":0.07451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25035,"mean_force":0.05128,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52553,-0.02077,0.12479]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02125,-0.00205],"force_p95":0.13543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16893,"mean_force":0.12664,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52427,-0.02085,0.04572]},{"body_a":"world","body_b":"grasp_target","contact_count":2032.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51367,-0.00952,0.2279]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5008.0,"contact_point_centroid":[0.52346,-0.00165,0.04745],"force_p95":0.06572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12271,"mean_force":0.04313,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52307,-0.02082,0.04432]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52927,-0.02016,0.10512]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.5948,0.15455,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60462,0.21685,0.28082]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5948,0.15455,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60321,0.22203,0.24164]},{"body_a":"world","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.5948,0.15455,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.604,0.22333,0.27376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.52391,-0.04008,0.04612],"force_p95":0.06942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08698,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52307,-0.02082,0.04432]},{"body_a":"left_finger","body_b":"right_finger","contact_count":720.0,"contact_point_centroid":[0.59421,0.17928,0.31831],"force_p95":0.01325,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01093,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59384,0.17927,0.31596]},{"body_a":"left_finger","body_b":"right_finger","contact_count":903.0,"contact_point_centroid":[0.60519,0.21688,0.28306],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60463,0.21686,0.28076]}],"total_contact_groups":17},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5948,0.15455,0.01602],"final_tcp_position":[0.60647,0.22535,0.288],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.05564,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2032.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53005,-0.01944,0.15661],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1384.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53142,-0.02098,0.05419],"tcp_start":[0.53005,-0.01944,0.15661],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02089,0.0258],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31653,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13419,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11705.0,"raw_peak_contact_force":0.16893,"tcp_end":[0.52304,-0.02083,0.04429],"tcp_start":[0.53142,-0.02098,0.05419],"tcp_to_object_dist_end":0.02313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53783,-0.02092,0.1865],"object_pos_start":[0.53694,-0.02089,0.0258],"object_to_goal_dist_end":0.25987,"object_to_goal_dist_start":0.31653,"object_z_max":0.18635,"peak_contact_force":0.07361,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39464.0,"raw_peak_contact_force":0.40301,"tcp_end":[0.5326,-0.02082,0.21167],"tcp_start":[0.52304,-0.02083,0.04429],"tcp_to_object_dist_end":0.0257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":756.0,"n_steps_budget":1000.0,"object_pos_end":[0.5948,0.15455,0.01602],"object_pos_start":[0.53783,-0.02092,0.1865],"object_to_goal_dist_end":0.2055,"object_to_goal_dist_start":0.25987,"object_z_max":0.26495,"peak_contact_force":0.12261,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13590.0,"raw_peak_contact_force":2.05564,"tcp_end":[0.60392,0.21117,0.31884],"tcp_start":[0.5326,-0.02082,0.21167],"tcp_to_object_dist_end":0.3082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.5948,0.15455,0.01602],"object_pos_start":[0.5948,0.15455,0.01602],"object_to_goal_dist_end":0.2055,"object_to_goal_dist_start":0.2055,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1747.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60648,0.22336,0.24211],"tcp_start":[0.60392,0.21117,0.31884],"tcp_to_object_dist_end":0.23661,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5948,0.15455,0.01602],"object_pos_start":[0.5948,0.15455,0.01602],"object_to_goal_dist_end":0.2055,"object_to_goal_dist_start":0.2055,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60215,0.22149,0.26101],"tcp_start":[0.60648,0.22336,0.24211],"tcp_to_object_dist_end":0.25408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.5948,0.15455,0.01602],"object_pos_start":[0.5948,0.15455,0.01602],"object_to_goal_dist_end":0.2055,"object_to_goal_dist_start":0.2055,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":524.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60647,0.22535,0.288],"tcp_start":[0.60215,0.22149,0.26101],"tcp_to_object_dist_end":0.28129,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97329,"average_solve_count":337.0,"average_success_count":337.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.05356,"descend_to_grasp.speed":0.04864,"descend_to_place.place_z_offset":0.04005,"descend_to_place.speed":0.06226,"grasp.grip_force":22.1906,"lift_object.lift_height":0.15187,"lift_object.speed":0.04021,"release_object.release_duration":0.5403,"retract_from_goal.speed":0.07095,"transport_to_goal.arc_height":0.03429,"transport_to_goal.speed":0.0441},"optimized_scores":{"best_composite_score":-0.08957,"best_fitness_score":0.64043,"best_task_score":0.35156},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.61923,0.16733,-0.0106],"force_p95":1.83238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90331,"mean_force":0.896,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62294,0.15919,0.23602]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.63525,0.15853,-0.00449],"force_p95":0.31015,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43131,"mean_force":0.21141,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.62488,0.16061,0.24969]},{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.54207,-0.02814,-0.00133],"force_p95":0.35847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38758,"mean_force":0.0971,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53026,-0.02846,0.045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1017.0,"contact_point_centroid":[0.62724,0.17925,0.21794],"force_p95":0.13559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29984,"mean_force":0.07114,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62589,0.16021,0.21933]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13968.0,"contact_point_centroid":[0.53485,-0.00924,0.10652],"force_p95":0.07873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25931,"mean_force":0.05445,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53423,-0.02839,0.10416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14938.0,"contact_point_centroid":[0.53489,-0.04747,0.10577],"force_p95":0.07564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2498,"mean_force":0.05158,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53416,-0.02839,0.1035]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1123.0,"contact_point_centroid":[0.627,0.14156,0.21883],"force_p95":0.12036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23927,"mean_force":0.05907,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62601,0.16025,0.21959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2430.0,"contact_point_centroid":[0.62759,0.17391,0.25535],"force_p95":0.11356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22411,"mean_force":0.07775,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62523,0.15499,0.2566]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3085.0,"contact_point_centroid":[0.62712,0.13638,0.25502],"force_p95":0.10478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21148,"mean_force":0.0611,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62529,0.15514,0.25556]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18406,"mean_force":0.12792,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53262,-0.02854,0.0452]},{"body_a":"world","body_b":"grasp_target","contact_count":2204.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51765,-0.01316,0.22721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.5323,-0.00929,0.04648],"force_p95":0.0781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13396,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5314,-0.0285,0.04375]},{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53748,-0.02768,0.10456]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14462.0,"contact_point_centroid":[0.57489,0.06465,0.23683],"force_p95":0.08554,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11508,"mean_force":0.05728,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57343,0.04556,0.23604]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16583.0,"contact_point_centroid":[0.57507,0.02769,0.23733],"force_p95":0.07602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1128,"mean_force":0.05044,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57397,0.04666,0.23663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.5323,-0.04759,0.04553],"force_p95":0.07027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07751,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5314,-0.0285,0.04375]}],"total_contact_groups":16},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63342,0.15439,0.02047],"final_tcp_position":[0.6274,0.16228,0.25795],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.90331,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2204.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53801,-0.02674,0.15594],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53984,-0.02875,0.05393],"tcp_start":[0.53801,-0.02674,0.15594],"tcp_to_object_dist_end":0.0285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02855,0.02575],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13861,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10818.0,"raw_peak_contact_force":0.18406,"tcp_end":[0.53137,-0.0285,0.04371],"tcp_start":[0.53984,-0.02875,0.05393],"tcp_to_object_dist_end":0.02286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.54795,-0.02845,0.13988],"object_pos_start":[0.54552,-0.02855,0.02575],"object_to_goal_dist_end":0.21442,"object_to_goal_dist_start":0.2606,"object_z_max":0.13974,"peak_contact_force":0.07624,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29032.0,"raw_peak_contact_force":0.38758,"tcp_end":[0.54077,-0.02842,0.16341],"tcp_start":[0.53137,-0.0285,0.04371],"tcp_to_object_dist_end":0.0246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.62828,0.14994,0.25905],"object_pos_start":[0.54795,-0.02845,0.13988],"object_to_goal_dist_end":0.08361,"object_to_goal_dist_start":0.21442,"object_z_max":0.25904,"peak_contact_force":0.08955,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31045.0,"raw_peak_contact_force":0.11508,"tcp_end":[0.6241,0.15024,0.28692],"tcp_start":[0.54077,-0.02842,0.16341],"tcp_to_object_dist_end":0.02818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.63001,0.16019,0.19536],"object_pos_start":[0.62828,0.14994,0.25905],"object_to_goal_dist_end":0.01925,"object_to_goal_dist_start":0.08361,"object_z_max":0.25905,"peak_contact_force":0.10645,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5515.0,"raw_peak_contact_force":0.22411,"tcp_end":[0.62786,0.16063,0.22435],"tcp_start":[0.6241,0.15024,0.28692],"tcp_to_object_dist_end":0.02907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62877,0.16153,0.00744],"object_pos_start":[0.63001,0.16019,0.19536],"object_to_goal_dist_end":0.16956,"object_to_goal_dist_start":0.01925,"object_z_max":0.19536,"peak_contact_force":0.45865,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2224.0,"raw_peak_contact_force":1.90331,"tcp_end":[0.62292,0.15919,0.24309],"tcp_start":[0.62786,0.16063,0.22435],"tcp_to_object_dist_end":0.23574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":82.0,"n_steps_budget":600.0,"object_pos_end":[0.63342,0.15439,0.02047],"object_pos_start":[0.62877,0.16153,0.00744],"object_to_goal_dist_end":0.15681,"object_to_goal_dist_start":0.16956,"object_z_max":0.02231,"peak_contact_force":0.2565,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":164.0,"raw_peak_contact_force":0.43131,"tcp_end":[0.6274,0.16228,0.25795],"tcp_start":[0.62292,0.15919,0.24309],"tcp_to_object_dist_end":0.23769,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03716,"average_solve_count":296.0,"average_success_count":296.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.06483,"descend_to_grasp.speed":0.05713,"descend_to_place.place_z_offset":0.02203,"descend_to_place.speed":0.03946,"grasp.grip_force":21.38878,"lift_object.lift_height":0.15845,"lift_object.speed":0.05408,"release_object.release_duration":0.38007,"retract_from_goal.speed":0.10306,"transport_to_goal.arc_height":0.03658,"transport_to_goal.speed":0.05509},"optimized_scores":{"best_composite_score":-0.00984,"best_fitness_score":0.72016,"best_task_score":0.51576},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.58894,0.14858,-0.00494],"force_p95":1.01221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31572,"mean_force":0.27827,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59743,0.14798,0.16059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":481.0,"contact_point_centroid":[0.60558,0.13083,0.14416],"force_p95":0.13881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42712,"mean_force":0.1032,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60145,0.14916,0.14684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":602.0,"contact_point_centroid":[0.60589,0.16721,0.14299],"force_p95":0.12035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38207,"mean_force":0.08463,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60148,0.14916,0.14688]},{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.46063,-0.00027,-0.00127],"force_p95":0.33534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38178,"mean_force":0.06659,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45029,-0.00021,0.04887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2354.0,"contact_point_centroid":[0.60153,0.16238,0.19358],"force_p95":0.13814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35204,"mean_force":0.10536,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59811,0.14413,0.1974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2632.0,"contact_point_centroid":[0.60073,0.12615,0.19288],"force_p95":0.13435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27368,"mean_force":0.09444,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59821,0.14423,0.19648]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11956.0,"contact_point_centroid":[0.45332,0.01892,0.10959],"force_p95":0.07831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26275,"mean_force":0.05415,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4531,-0.0002,0.10828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11962.0,"contact_point_centroid":[0.45241,-0.01932,0.10956],"force_p95":0.07996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2507,"mean_force":0.05419,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45315,-0.0002,0.10884]},{"body_a":"world","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.58608,0.14661,-0.00193],"force_p95":0.16424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17328,"mean_force":0.12227,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.6002,0.1493,0.1866]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11181.0,"contact_point_centroid":[0.51234,0.07427,0.21719],"force_p95":0.10593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1615,"mean_force":0.06195,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51117,0.05537,0.21746]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-7e-05,-0.00202],"force_p95":0.12944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15221,"mean_force":0.12445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45231,-0.00018,0.04863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11770.0,"contact_point_centroid":[0.51304,0.03816,0.21786],"force_p95":0.09448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14494,"mean_force":0.05976,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51283,0.05702,0.21857]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.46286,-7e-05,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48109,-5e-05,0.2305]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4595,-0.0001,0.10712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4870.0,"contact_point_centroid":[0.45116,0.019,0.04914],"force_p95":0.06696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0817,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45125,-0.00019,0.04759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4857.0,"contact_point_centroid":[0.45025,-0.01939,0.04847],"force_p95":0.06666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08049,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45125,-0.00019,0.04759]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.58615,0.14663,0.02602],"final_tcp_position":[0.60421,0.15089,0.20324],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.31572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1764.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46293,-8e-05,0.15981],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4587,-0.00011,0.05495],"tcp_start":[0.46293,-8e-05,0.15981],"tcp_to_object_dist_end":0.02923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00015,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12957,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11527.0,"raw_peak_contact_force":0.15221,"tcp_end":[0.45122,-0.00019,0.04756],"tcp_start":[0.4587,-0.00011,0.05495],"tcp_to_object_dist_end":0.02454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.46443,-1e-05,0.14383],"object_pos_start":[0.46277,-0.00015,0.02591],"object_to_goal_dist_end":0.21231,"object_to_goal_dist_start":0.23325,"object_z_max":0.14366,"peak_contact_force":0.07442,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24017.0,"raw_peak_contact_force":0.38178,"tcp_end":[0.45844,-0.00017,0.17013],"tcp_start":[0.45122,-0.00019,0.04756],"tcp_to_object_dist_end":0.02697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":709.0,"n_steps_budget":1000.0,"object_pos_end":[0.59909,0.14034,0.2068],"object_pos_start":[0.46443,-1e-05,0.14383],"object_to_goal_dist_end":0.08625,"object_to_goal_dist_start":0.21231,"object_z_max":0.21283,"peak_contact_force":0.13537,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22951.0,"raw_peak_contact_force":0.1615,"tcp_end":[0.5955,0.14002,0.23822],"tcp_start":[0.45844,-0.00017,0.17013],"tcp_to_object_dist_end":0.03163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.60818,0.14934,0.11723],"object_pos_start":[0.59909,0.14034,0.2068],"object_to_goal_dist_end":0.0064,"object_to_goal_dist_start":0.08625,"object_z_max":0.2068,"peak_contact_force":0.1401,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4986.0,"raw_peak_contact_force":0.35204,"tcp_end":[0.60378,0.1497,0.15125],"tcp_start":[0.5955,0.14002,0.23822],"tcp_to_object_dist_end":0.03431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58923,0.14713,0.02636],"object_pos_start":[0.60818,0.14934,0.11723],"object_to_goal_dist_end":0.09826,"object_to_goal_dist_start":0.0064,"object_z_max":0.11723,"peak_contact_force":0.13464,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1331.0,"raw_peak_contact_force":1.31572,"tcp_end":[0.59735,0.14796,0.17132],"tcp_start":[0.60378,0.1497,0.15125],"tcp_to_object_dist_end":0.1452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":150.0,"n_steps_budget":600.0,"object_pos_end":[0.58615,0.14663,0.02602],"object_pos_start":[0.58923,0.14713,0.02636],"object_to_goal_dist_end":0.09932,"object_to_goal_dist_start":0.09826,"object_z_max":0.02654,"peak_contact_force":0.12474,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":600.0,"raw_peak_contact_force":0.17328,"tcp_end":[0.60421,0.15089,0.20324],"tcp_start":[0.59735,0.14796,0.17132],"tcp_to_object_dist_end":0.17819,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```