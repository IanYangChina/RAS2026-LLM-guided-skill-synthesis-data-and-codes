## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3059 | 0.72 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0458 | 0.36 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0338 | 0.21 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0520 | 0.39 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2655 | 0.64 | ✅ accepted |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.306) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
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
  subtask_id: approach_1
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
  subtask_id: descend_1
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
  subtask_id: grasp_1
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
      - 0.12
      - 0.3
      default: 0.2
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
      - 0.05
      - 0.2
      default: 0.12
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
  guards:
  - id: transport_retain
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: transport_arc
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
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
  subtask_id: release_1

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
  - guards:
    - id=transport_retain, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.306
- **task_score** (E): 0.724
- **fitness_score**: 0.826  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1489 |
| descend_to_grasp | 1.00 | 1.00 | 0.1032 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift_object | 0.67 | 1.00 | 0.1322 |
| transport_to_goal | 1.00 | 1.00 | 0.1649 |
| descend_to_place | 1.00 | 1.00 | 0.1147 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.157) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 8.230 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.157)→(0.510, -0.017, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.054)→(0.502, -0.017, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.134 | 0.168 |
| lift_object | lift | 0.67 / step_budget | (0.502, -0.017, 0.045)→(0.509, -0.016, 0.177) | (0.515, -0.016, 0.026)→(0.515, -0.016, 0.153) | 0.270→0.232 | 1.00 / 38.333 | 0.078 | 0.395 |
| transport_to_goal | approach | 1.00 / step_budget | (0.555, 0.030, 0.205)→(0.606, 0.160, 0.288) | (0.515, -0.016, 0.153)→(0.609, 0.166, 0.187) | 0.232→0.105 | 1.00 / 19.667 | 0.108 | 0.757 |
| descend_to_place | descend | 1.00 / step_budget | (0.606, 0.160, 0.288)→(0.613, 0.178, 0.176) | (0.610, 0.166, 0.191)→(0.615, 0.182, 0.117) | 0.101→0.053 | 1.00 / 16.333 | 3249.658 | 0.280 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.850
- phase_score: 0.410
- phase_breakdown.descend_1_score: 0.870
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.083
- phase_breakdown.approach_1_score: 0.080
- phase_breakdown.release_1_score: 0.821
- grasp_place_fitness: 0.889

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.889
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.850
- **Median Q (composite search score)**: 0.361
- **K-run variance**: 0.0071
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.409


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76119,"average_solve_count":402.0,"average_success_count":402.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.04855,"descend_to_grasp.speed":0.02695,"descend_to_place.speed":0.02763,"grasp.grip_force":21.27161,"lift_object.lift_height":0.14493,"lift_object.speed":0.04848,"transport_to_goal.arc_height":0.0596,"transport_to_goal.speed":0.05431},"optimized_scores":{"best_composite_score":0.36138,"best_fitness_score":0.88138,"best_task_score":0.83396},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":118.0,"contact_point_centroid":[0.53361,-0.02059,-0.00129],"force_p95":0.38782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41183,"mean_force":0.09418,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52201,-0.0208,0.04552]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13050.0,"contact_point_centroid":[0.52593,-0.00155,0.10073],"force_p95":0.07668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28089,"mean_force":0.05359,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52547,-0.02073,0.09809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14305.0,"contact_point_centroid":[0.5258,-0.03984,0.1006],"force_p95":0.07297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26275,"mean_force":0.04967,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52551,-0.02073,0.09838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3579.0,"contact_point_centroid":[0.60439,0.22233,0.26707],"force_p95":0.13737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25951,"mean_force":0.09783,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59999,0.20363,0.269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4742.0,"contact_point_centroid":[0.60431,0.18581,0.26746],"force_p95":0.10034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22901,"mean_force":0.06834,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60006,0.20388,0.2681]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02121,-0.00205],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1689,"mean_force":0.12664,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52427,-0.02085,0.04563]},{"body_a":"world","body_b":"grasp_target","contact_count":2100.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51366,-0.00953,0.22783]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16013.0,"contact_point_centroid":[0.55565,0.07483,0.25375],"force_p95":0.08937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13495,"mean_force":0.06163,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55375,0.05578,0.25334]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4319.0,"contact_point_centroid":[0.52375,-0.00162,0.04708],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12873,"mean_force":0.04947,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52307,-0.02083,0.04423]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18455.0,"contact_point_centroid":[0.55596,0.03892,0.25542],"force_p95":0.07888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12324,"mean_force":0.05319,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55441,0.05783,0.25499]},{"body_a":"world","body_b":"grasp_target","contact_count":1424.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52923,-0.02016,0.10511]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.5239,-0.03995,0.04603],"force_p95":0.0694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08695,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52307,-0.02083,0.04423]}],"total_contact_groups":12},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61097,0.2198,0.18137],"final_tcp_position":[0.60545,0.22144,0.21326],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.41183,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2100.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53003,-0.01943,0.15664],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1424.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5314,-0.02098,0.05407],"tcp_start":[0.53003,-0.01943,0.15664],"tcp_to_object_dist_end":0.02861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.0208,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13427,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11016.0,"raw_peak_contact_force":0.1689,"subtask_id":"grasp_1","tcp_end":[0.52304,-0.02082,0.04419],"tcp_start":[0.5314,-0.02098,0.05407],"tcp_to_object_dist_end":0.02305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.53972,-0.02067,0.13324],"object_pos_start":[0.53694,-0.0208,0.02581],"object_to_goal_dist_end":0.2687,"object_to_goal_dist_start":0.31645,"object_z_max":0.13309,"peak_contact_force":0.07573,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27473.0,"raw_peak_contact_force":0.41183,"tcp_end":[0.53211,-0.02071,0.15659],"tcp_start":[0.52304,-0.02082,0.04419],"tcp_to_object_dist_end":0.02456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60204,0.1888,0.29225],"object_pos_start":[0.53972,-0.02067,0.13324],"object_to_goal_dist_end":0.09372,"object_to_goal_dist_start":0.2687,"object_z_max":0.2923,"peak_contact_force":0.13495,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34468.0,"raw_peak_contact_force":0.13495,"subtask_id":"transport_arc","tcp_end":[0.59675,0.18904,0.32122],"tcp_start":[0.53211,-0.02071,0.15659],"tcp_to_object_dist_end":0.02945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.61097,0.2198,0.18137],"object_pos_start":[0.60204,0.1888,0.29225],"object_to_goal_dist_end":0.02724,"object_to_goal_dist_start":0.09372,"object_z_max":0.29225,"peak_contact_force":0.13718,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8321.0,"raw_peak_contact_force":0.25951,"subtask_id":"release_1","tcp_end":[0.60545,0.22144,0.21326],"tcp_start":[0.59675,0.18904,0.32122],"tcp_to_object_dist_end":0.0324,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01579,"average_solve_count":380.0,"average_success_count":380.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.03319,"descend_to_grasp.speed":0.06582,"descend_to_place.speed":0.05271,"grasp.grip_force":16.18909,"lift_object.lift_height":0.28163,"lift_object.speed":0.03326,"transport_to_goal.arc_height":0.19037,"transport_to_goal.speed":0.04108},"optimized_scores":{"best_composite_score":0.36947,"best_fitness_score":0.88947,"best_task_score":0.84952},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":3663.0,"contact_point_centroid":[0.62976,0.17266,0.24454],"force_p95":0.13385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45117,"mean_force":0.08634,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62435,0.15395,0.24527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3989.0,"contact_point_centroid":[0.62977,0.13574,0.24296],"force_p95":0.11497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43823,"mean_force":0.07779,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62446,0.1542,0.24333]},{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.54154,-0.02811,-0.00133],"force_p95":0.38496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40686,"mean_force":0.10458,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53019,-0.02846,0.04498]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18661.0,"contact_point_centroid":[0.53283,-0.00924,0.12882],"force_p95":0.0781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27391,"mean_force":0.05455,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53216,-0.02838,0.12663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20136.0,"contact_point_centroid":[0.5329,-0.04746,0.12877],"force_p95":0.07469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26231,"mean_force":0.05121,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53217,-0.02838,0.12673]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14185,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18391,"mean_force":0.1279,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53265,-0.02854,0.04518]},{"body_a":"world","body_b":"grasp_target","contact_count":2236.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51759,-0.01315,0.22723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.53232,-0.00929,0.04646],"force_p95":0.07808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13381,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53143,-0.0285,0.04373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12298.0,"contact_point_centroid":[0.56696,0.0498,0.28152],"force_p95":0.09994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1288,"mean_force":0.06537,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56446,0.03082,0.28157]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14228.0,"contact_point_centroid":[0.56667,0.01231,0.28235],"force_p95":0.08655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12636,"mean_force":0.05687,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56461,0.03113,0.28233]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53759,-0.02771,0.10443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.53232,-0.04759,0.04551],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07749,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53143,-0.0285,0.04373]}],"total_contact_groups":12},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63385,0.16095,0.1528],"final_tcp_position":[0.62793,0.16155,0.18479],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":24.44542,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":24.44542,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53807,-0.02677,0.15578],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53989,-0.02876,0.05393],"tcp_start":[0.53807,-0.02677,0.15578],"tcp_to_object_dist_end":0.02849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02856,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13855,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10819.0,"raw_peak_contact_force":0.18391,"subtask_id":"grasp_1","tcp_end":[0.5314,-0.0285,0.04369],"tcp_start":[0.53989,-0.02876,0.05393],"tcp_to_object_dist_end":0.02283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54265,-0.02844,0.18555],"object_pos_start":[0.54552,-0.02856,0.02576],"object_to_goal_dist_end":0.21354,"object_to_goal_dist_start":0.2606,"object_z_max":0.18539,"peak_contact_force":0.07574,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38917.0,"raw_peak_contact_force":0.40686,"tcp_end":[0.53721,-0.02842,0.2104],"tcp_start":[0.5314,-0.0285,0.04369],"tcp_to_object_dist_end":0.02544,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.62965,0.14736,0.27053],"object_pos_start":[0.54265,-0.02844,0.18555],"object_to_goal_dist_end":0.09529,"object_to_goal_dist_start":0.21354,"object_z_max":0.29209,"peak_contact_force":0.09574,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26526.0,"raw_peak_contact_force":0.1288,"subtask_id":"transport_arc","tcp_end":[0.62301,0.14799,0.29995],"tcp_start":[0.53721,-0.02842,0.2104],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.63385,0.16095,0.1528],"object_pos_start":[0.62965,0.14736,0.27053],"object_to_goal_dist_end":0.02446,"object_to_goal_dist_start":0.09529,"object_z_max":0.27053,"peak_contact_force":0.13671,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7652.0,"raw_peak_contact_force":0.45117,"subtask_id":"release_1","tcp_end":[0.62793,0.16155,0.18479],"tcp_start":[0.62301,0.14799,0.29995],"tcp_to_object_dist_end":0.03253,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19048,"average_solve_count":294.0,"average_success_count":294.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.06744,"descend_to_grasp.speed":0.03406,"descend_to_place.speed":0.04741,"grasp.grip_force":10.94712,"lift_object.lift_height":0.15272,"lift_object.speed":0.03653,"transport_to_goal.arc_height":0.07934,"transport_to_goal.speed":0.14968},"optimized_scores":{"best_composite_score":0.18685,"best_fitness_score":0.70685,"best_task_score":0.48938},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.60125,0.16255,-0.00919],"force_p95":1.55247,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00752,"mean_force":0.51065,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59475,0.13906,0.24937]},{"body_a":"world","body_b":"grasp_target","contact_count":101.0,"contact_point_centroid":[0.45917,-0.00031,-0.00133],"force_p95":0.34463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36697,"mean_force":0.11164,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4503,-0.00021,0.04872]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11984.0,"contact_point_centroid":[0.45316,0.01879,0.10724],"force_p95":0.07546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25238,"mean_force":0.05217,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45313,-0.0002,0.10621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10122.0,"contact_point_centroid":[0.45235,-0.01937,0.10671],"force_p95":0.08564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2412,"mean_force":0.0602,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45308,-0.0002,0.1056]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6522.0,"contact_point_centroid":[0.48959,0.01162,0.22768],"force_p95":0.13159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23444,"mean_force":0.08194,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48658,0.03028,0.22916]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6877.0,"contact_point_centroid":[0.49107,0.04972,0.22852],"force_p95":0.12743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23302,"mean_force":0.07749,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48749,0.03117,0.22967]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-7e-05,-0.00202],"force_p95":0.12941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15222,"mean_force":0.12446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45228,-0.00018,0.04871]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.46286,-7e-05,-0.00192],"force_p95":0.13362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48111,-5e-05,0.23059]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.6003,0.16388,-0.00203],"force_p95":0.12591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12993,"mean_force":0.11801,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5996,0.14592,0.18657]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45953,-0.0001,0.10736]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4870.0,"contact_point_centroid":[0.45113,0.01899,0.04921],"force_p95":0.06688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08169,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45122,-0.00019,0.04767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4786.0,"contact_point_centroid":[0.45034,-0.01938,0.04856],"force_p95":0.06755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0805,"mean_force":0.04558,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45122,-0.00019,0.04767]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1434.0,"contact_point_centroid":[0.60013,0.14596,0.18833],"force_p95":0.01244,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01069,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59961,0.14595,0.18613]}],"total_contact_groups":13},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60029,0.16387,0.01602],"final_tcp_position":[0.60428,0.15037,0.1297],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9748.69919,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46305,-8e-05,0.15999],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1496.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45867,-0.00011,0.05504],"tcp_start":[0.46305,-8e-05,0.15999],"tcp_to_object_dist_end":0.02932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00015,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12953,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11456.0,"raw_peak_contact_force":0.15222,"subtask_id":"grasp_1","tcp_end":[0.45119,-0.00019,0.04764],"tcp_start":[0.45867,-0.00011,0.05504],"tcp_to_object_dist_end":0.02462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.46386,-0.00025,0.13884],"object_pos_start":[0.46277,-0.00015,0.02591],"object_to_goal_dist_end":0.21242,"object_to_goal_dist_start":0.23325,"object_z_max":0.13866,"peak_contact_force":0.08344,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22207.0,"raw_peak_contact_force":0.36697,"tcp_end":[0.45836,-0.00017,0.16448],"tcp_start":[0.45119,-0.00019,0.04764],"tcp_to_object_dist_end":0.02622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.59674,0.16129,-0.00321],"object_pos_start":[0.46386,-0.00025,0.13884],"object_to_goal_dist_end":0.1264,"object_to_goal_dist_start":0.21242,"object_z_max":0.2407,"peak_contact_force":0.09389,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13567.0,"raw_peak_contact_force":2.00752,"subtask_id":"transport_arc","tcp_end":[0.59736,0.14231,0.24432],"tcp_start":[0.59638,0.14038,0.24847],"tcp_to_object_dist_end":0.24826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.60029,0.16387,0.01602],"object_pos_start":[0.59781,0.1626,0.00968],"object_to_goal_dist_end":0.10719,"object_to_goal_dist_start":0.1136,"object_z_max":0.01684,"peak_contact_force":9748.69919,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2798.0,"raw_peak_contact_force":0.12993,"subtask_id":"release_1","tcp_end":[0.60428,0.15037,0.1297],"tcp_start":[0.59736,0.14231,0.24432],"tcp_to_object_dist_end":0.11455,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```