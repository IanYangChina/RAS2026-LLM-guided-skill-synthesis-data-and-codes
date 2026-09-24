## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.2391 | 0.41 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1884 | 0.39 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | -0.2037 | 0.17 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | joint_interpolation | joint_interpolation | — | joint_interpolation | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | -0.3223 | 0.17 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.2543 | 0.14 | ✅ accepted |

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

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.239) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: descend_to_grasp
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: transport_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.3
- id: final_placement
  target_entity: object
  weight: 0.3
phases:
- id: approach_to_object
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
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
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
    - 0.0
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_lateral_x:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.025
      binds_to:
      - path: target.offset.x
        mode: add
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_to_grasp
- id: grasp_object
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
    orientation:
      mode: none
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: repeat
- id: lift_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
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
    max_attempts: 2
    strategy: repeat
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_to_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - -0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: termination.force_threshold
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
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
    orientation:
      mode: none
  subtask_id: final_placement

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_lateral_x: status=consumed; consumers=target.offset.x (add)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, -0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.239
- **task_score** (E): 0.407
- **fitness_score**: 0.694  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.095
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_to_object | 1.00 | 0.1574 |
| descend_to_grasp | 1.00 | 0.1117 |
| grasp_object | 1.00 | 0.0130 |
| lift_object | 1.00 | 0.1282 |
| transport_to_goal | 0.67 | 0.2629 |
| descend_to_place | 0.67 | 0.1197 |
| release_object | 1.00 | 0.0210 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.148)→(0.528, -0.016, 0.038) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 |
| grasp_object | grasp | 1.00 / step_budget | (0.528, -0.016, 0.038)→(0.519, -0.016, 0.028) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 |
| lift_object | lift | 1.00 / step_budget | (0.519, -0.016, 0.028)→(0.512, -0.016, 0.156) | (0.515, -0.016, 0.026)→(0.507, -0.016, 0.151) | 0.270→0.234 |
| transport_to_goal | approach | 0.67 / step_budget | (0.512, -0.016, 0.156)→(0.605, 0.155, 0.326) | (0.507, -0.016, 0.151)→(0.611, 0.155, 0.312) | 0.234→0.147 |
| descend_to_place | descend | 0.67 / force_exceeded | (0.605, 0.155, 0.326)→(0.606, 0.160, 0.207) | (0.611, 0.155, 0.312)→(0.608, 0.160, 0.189) | 0.147→0.086 |
| release_object | release | 1.00 / step_budget | (0.606, 0.160, 0.207)→(0.601, 0.159, 0.227) | (0.608, 0.160, 0.189)→(0.590, 0.146, 0.045) | 0.086→0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.521
- phase_score: 0.555
- phase_breakdown.final_placement_score: 0.458
- phase_breakdown.transport_to_goal_score: 0.369
- phase_breakdown.approach_object_score: 0.674
- phase_breakdown.lift_object_score: 0.620
- phase_breakdown.descend_to_grasp_score: 0.761
- grasp_place_fitness: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.750
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.521
- **Median Q (composite search score)**: 0.251
- **K-run variance**: 0.0081
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.196


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85635,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.20872,"descend_to_grasp.descend_lateral_x":0.02403,"descend_to_grasp.descend_speed":0.09316,"descend_to_place.contact_force_threshold":1.94523,"descend_to_place.place_speed":0.05805,"lift_object.lift_speed":0.03862,"transport_to_goal.arc_height":0.112,"transport_to_goal.transport_speed":0.12529},"optimized_scores":{"best_composite_score":0.251,"best_fitness_score":0.65814,"best_task_score":0.33605},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.53228,-0.02058,-0.00161],"force_p95":0.64221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68497,"mean_force":0.21737,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54134,-0.02063,0.02823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9580.0,"contact_point_centroid":[0.53625,-0.03974,0.09196],"force_p95":0.07232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29042,"mean_force":0.05157,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53615,-0.02059,0.09008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9580.0,"contact_point_centroid":[0.53623,-0.00144,0.09199],"force_p95":0.07262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28046,"mean_force":0.05128,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53615,-0.02059,0.09008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1614.0,"contact_point_centroid":[0.59337,0.15682,0.36465],"force_p95":0.13812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25477,"mean_force":0.07721,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59242,0.17749,0.36283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.59454,0.19629,0.37037],"force_p95":0.15105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22492,"mean_force":0.0833,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59365,0.17725,0.36858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20380.0,"contact_point_centroid":[0.54908,0.05458,0.29924],"force_p95":0.07325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18892,"mean_force":0.04951,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54896,0.03547,0.2973]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53697,-0.02117,-0.00207],"force_p95":0.14116,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18511,"mean_force":0.12867,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54409,-0.02067,0.02828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.59506,0.15812,0.37132],"force_p95":0.13315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18039,"mean_force":0.06287,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59365,0.17725,0.36858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19305.0,"contact_point_centroid":[0.54787,0.01212,0.29557],"force_p95":0.07776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17454,"mean_force":0.05196,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54761,0.03127,0.29343]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51332,-0.00886,0.22435]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53865,-0.01951,0.09175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1167.0,"contact_point_centroid":[0.59369,0.19659,0.36569],"force_p95":0.08456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11132,"mean_force":0.04626,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5927,0.17765,0.36393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4810.0,"contact_point_centroid":[0.54291,-0.00147,0.02873],"force_p95":0.06993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10811,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54285,-0.02065,0.02681]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.54294,-0.03988,0.02871],"force_p95":0.07024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08764,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.54285,-0.02065,0.02682]}],"total_contact_groups":14},"final_pose_error":0.31475,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.56999,0.13178,0.08123],"final_tcp_position":[0.59346,0.17772,0.3677],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.52862,-0.01828,0.14748],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12179,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.55171,-0.02079,0.03745],"tcp_start":[0.52862,-0.01828,0.14748],"tcp_to_object_dist_end":0.01862,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.02069,0.02571],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31644,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.54282,-0.02065,0.02677],"tcp_start":[0.55171,-0.02079,0.03745],"tcp_to_object_dist_end":0.00605,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.52765,-0.02062,0.15235],"object_pos_start":[0.53687,-0.02069,0.02571],"object_to_goal_dist_end":0.26749,"object_to_goal_dist_start":0.31644,"object_z_max":0.15209,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.5336,-0.0206,0.15623],"tcp_start":[0.54282,-0.02065,0.02677],"tcp_to_object_dist_end":0.0071,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60819,0.17694,0.35935],"object_pos_start":[0.52765,-0.02062,0.15235],"object_to_goal_dist_end":0.16023,"object_to_goal_dist_start":0.26749,"object_z_max":0.36523,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.59383,0.17669,0.36918],"tcp_start":[0.5336,-0.0206,0.15623],"tcp_to_object_dist_end":0.01741,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.60814,0.17812,0.35781],"object_pos_start":[0.60819,0.17694,0.35935],"object_to_goal_dist_end":0.15839,"object_to_goal_dist_start":0.16023,"object_z_max":0.35935,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.59346,0.17772,0.3677],"tcp_start":[0.59383,0.17669,0.36918],"tcp_to_object_dist_end":0.01771,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56999,0.13178,0.08123],"object_pos_start":[0.60814,0.17812,0.35781],"object_to_goal_dist_end":0.16358,"object_to_goal_dist_start":0.15839,"object_z_max":0.35781,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"final_placement","tcp_end":[0.59166,0.1769,0.38776],"tcp_start":[0.59346,0.17772,0.3677],"tcp_to_object_dist_end":0.31059,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51751,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.14243,"descend_to_grasp.descend_lateral_x":0.02371,"descend_to_grasp.descend_speed":0.06325,"descend_to_place.contact_force_threshold":2.13328,"descend_to_place.place_speed":0.03132,"lift_object.lift_speed":0.05219,"transport_to_goal.arc_height":0.15601,"transport_to_goal.transport_speed":0.11747},"optimized_scores":{"best_composite_score":0.12315,"best_fitness_score":0.67315,"best_task_score":0.36389},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":334.0,"contact_point_centroid":[0.61607,0.15733,-0.00403],"force_p95":0.64113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10385,"mean_force":0.20641,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6185,0.15606,0.12634]},{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.54061,-0.02814,-0.00159],"force_p95":0.69048,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76613,"mean_force":0.20683,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54927,-0.0282,0.02814]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9600.0,"contact_point_centroid":[0.54442,-0.04729,0.09194],"force_p95":0.07226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32672,"mean_force":0.05149,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54431,-0.02814,0.09007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9600.0,"contact_point_centroid":[0.5444,-0.00899,0.09199],"force_p95":0.07307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30686,"mean_force":0.05102,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54431,-0.02814,0.09007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.62399,0.17249,0.20898],"force_p95":0.07292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27569,"mean_force":0.04991,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62384,0.15335,0.20719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.62401,0.13421,0.20919],"force_p95":0.07407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23819,"mean_force":0.0497,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62384,0.15335,0.20719]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54554,-0.02903,-0.00211],"force_p95":0.15026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21523,"mean_force":0.13139,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.55203,-0.02828,0.02794]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19640.0,"contact_point_centroid":[0.55848,0.02977,0.29078],"force_p95":0.07337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19157,"mean_force":0.04957,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55837,0.01064,0.28887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19640.0,"contact_point_centroid":[0.5585,-0.00851,0.29074],"force_p95":0.07249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18447,"mean_force":0.04983,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55837,0.01064,0.28887]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51691,-0.01219,0.22407]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54629,-0.02676,0.09153]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4790.0,"contact_point_centroid":[0.55084,-0.00906,0.02834],"force_p95":0.07138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11591,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.55077,-0.02824,0.02642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.62338,0.17665,0.11685],"force_p95":0.0695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10302,"mean_force":0.04157,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62325,0.15744,0.11504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.6234,0.13827,0.11717],"force_p95":0.07039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09773,"mean_force":0.04185,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62328,0.15745,0.11509]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.55086,-0.04749,0.02831],"force_p95":0.07182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08691,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.55078,-0.02824,0.02643]}],"total_contact_groups":15},"final_pose_error":0.09238,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61624,0.1574,0.02639],"final_tcp_position":[0.62522,0.15797,0.11872],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.53612,-0.02513,0.14706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12148,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.55973,-0.02849,0.03736],"tcp_start":[0.53612,-0.02513,0.14706],"tcp_to_object_dist_end":0.01813,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54543,-0.0283,0.02558],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26054,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.55074,-0.02824,0.02638],"tcp_start":[0.55973,-0.02849,0.03736],"tcp_to_object_dist_end":0.00537,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.53687,-0.02818,0.15238],"object_pos_start":[0.54543,-0.0283,0.02558],"object_to_goal_dist_end":0.21703,"object_to_goal_dist_start":0.26054,"object_z_max":0.15212,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.54207,-0.02815,0.15601],"tcp_start":[0.55074,-0.02824,0.02638],"tcp_to_object_dist_end":0.00634,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":982.0,"n_steps_budget":1000.0,"object_pos_end":[0.63062,0.14781,0.3176],"object_pos_start":[0.53687,-0.02818,0.15238],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.21703,"object_z_max":0.34447,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.62371,0.1477,0.33106],"tcp_start":[0.54207,-0.02815,0.15601],"tcp_to_object_dist_end":0.01514,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62284,0.15782,0.1008],"object_pos_start":[0.63062,0.14781,0.3176],"object_to_goal_dist_end":0.07711,"object_to_goal_dist_start":0.14173,"object_z_max":0.3176,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.62522,0.15797,0.11872],"tcp_start":[0.62371,0.1477,0.33106],"tcp_to_object_dist_end":0.01808,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61624,0.1574,0.02639],"object_pos_start":[0.62284,0.15782,0.1008],"object_to_goal_dist_end":0.15163,"object_to_goal_dist_start":0.07711,"object_z_max":0.1008,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"final_placement","tcp_end":[0.61837,0.15602,0.13851],"tcp_start":[0.62522,0.15797,0.11872],"tcp_to_object_dist_end":0.11215,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48684,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.23896,"descend_to_grasp.descend_lateral_x":0.01554,"descend_to_grasp.descend_speed":0.10442,"descend_to_place.contact_force_threshold":2.33661,"descend_to_place.place_speed":0.04382,"lift_object.lift_speed":0.03066,"transport_to_goal.arc_height":0.14982,"transport_to_goal.transport_speed":0.1791},"optimized_scores":{"best_composite_score":0.34306,"best_fitness_score":0.75021,"best_task_score":0.52058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.59058,0.15286,-0.00598],"force_p95":1.03446,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32836,"mean_force":0.34536,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59175,0.14287,0.14245]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.45845,-0.00017,-0.00154],"force_p95":0.50586,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52832,"mean_force":0.21385,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46369,-0.00023,0.03282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11563.0,"contact_point_centroid":[0.59675,0.16107,0.20579],"force_p95":0.08318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3034,"mean_force":0.05786,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59612,0.14199,0.20485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14791.0,"contact_point_centroid":[0.50144,0.02487,0.26419],"force_p95":0.07512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28006,"mean_force":0.05134,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50138,0.04404,0.26225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12376.0,"contact_point_centroid":[0.59611,0.1231,0.20116],"force_p95":0.0803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26608,"mean_force":0.05404,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59623,0.14215,0.19994]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15000.0,"contact_point_centroid":[0.50267,0.06436,0.2645],"force_p95":0.07347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26299,"mean_force":0.05059,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50259,0.04526,0.2626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8380.0,"contact_point_centroid":[0.46059,0.01891,0.09439],"force_p95":0.07253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25786,"mean_force":0.05146,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46052,-0.00024,0.09249]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8380.0,"contact_point_centroid":[0.46061,-0.01938,0.09439],"force_p95":0.07277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25002,"mean_force":0.05132,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46052,-0.00024,0.09249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1238.0,"contact_point_centroid":[0.5976,0.16347,0.13115],"force_p95":0.08784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22425,"mean_force":0.05488,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59593,0.14403,0.13027]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1285.0,"contact_point_centroid":[0.59706,0.1252,0.13212],"force_p95":0.06796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20626,"mean_force":0.04,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59621,0.14411,0.13073]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-0.0001,-0.00202],"force_p95":0.12947,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14296,"mean_force":0.12498,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46594,-0.0002,0.03278]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.46286,-7e-05,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48264,-4e-05,0.22583]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46769,-9e-05,0.09417]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4844.0,"contact_point_centroid":[0.46494,-0.0194,0.03362],"force_p95":0.06796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09954,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46487,-0.00021,0.03171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4874.0,"contact_point_centroid":[0.46492,0.01899,0.03361],"force_p95":0.06803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08555,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46487,-0.00021,0.03172]}],"total_contact_groups":15},"final_pose_error":0.16273,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.58504,0.14763,0.02769],"final_tcp_position":[0.59818,0.1446,0.13427],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"phases":[{"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.4653,-7e-05,0.14954],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12355,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.47257,-0.00012,0.03956],"tcp_start":[0.4653,-7e-05,0.14954],"tcp_to_object_dist_end":0.01666,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46273,-0.0002,0.02588],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23332,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.46484,-0.00021,0.03169],"tcp_start":[0.47257,-0.00012,0.03956],"tcp_to_object_dist_end":0.00618,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.45708,-0.00021,0.14915],"object_pos_start":[0.46273,-0.0002,0.02588],"object_to_goal_dist_end":0.21815,"object_to_goal_dist_start":0.23332,"object_z_max":0.14885,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.45954,-0.00022,0.15634],"tcp_start":[0.46484,-0.00021,0.03169],"tcp_to_object_dist_end":0.0076,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.59421,0.13959,0.25821],"object_pos_start":[0.45708,-0.00021,0.14915],"object_to_goal_dist_end":0.1376,"object_to_goal_dist_start":0.21815,"object_z_max":0.29322,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.59637,0.13999,0.27871],"tcp_start":[0.45954,-0.00022,0.15634],"tcp_to_object_dist_end":0.02061,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.59298,0.14438,0.10919],"object_pos_start":[0.59421,0.13959,0.25821],"object_to_goal_dist_end":0.02315,"object_to_goal_dist_start":0.1376,"object_z_max":0.25821,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.59818,0.1446,0.13427],"tcp_start":[0.59637,0.13999,0.27871],"tcp_to_object_dist_end":0.02561,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58504,0.14763,0.02769],"object_pos_start":[0.59298,0.14438,0.10919],"object_to_goal_dist_end":0.09792,"object_to_goal_dist_start":0.02315,"object_z_max":0.10919,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"final_placement","tcp_end":[0.59162,0.14284,0.15507],"tcp_start":[0.59818,0.1446,0.13427],"tcp_to_object_dist_end":0.12765,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```