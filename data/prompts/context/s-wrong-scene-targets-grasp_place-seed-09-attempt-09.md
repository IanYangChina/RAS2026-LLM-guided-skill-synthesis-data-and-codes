## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.1587 | 0.39 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.1581 | 0.39 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.4703 | 0.17 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0640 | 0.37 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0646 | 0.37 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5370249203970084, -0.021318279091244466, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5370249203970084, -0.021318279091244466, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.159) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: transport_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_above
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: quat
      quat:
      - 0.0
      - 1.0
      - 0.0
      - 0.0
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_grasp
- id: descend_grasp
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
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_grasp
- id: grasp_object
  type: grasp
  generator: linear_cartesian
  control: impedance_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.005
  subtask_id: pre_grasp
- id: lift_clear
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_clear_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
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
  subtask_id: pre_grasp
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.025
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_goal
- id: descend_place
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_height:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_goal
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
      mode: keep_current
  parameters:
    max_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=quat, quat=[0.0, 1.0, 0.0, 0.0], tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.005]
- **lift_clear** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_clear_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.025
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.159
- **task_score** (E): 0.388
- **fitness_score**: 0.666  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.0304 |
| descend_grasp | 1.00 | 1.00 | 0.2307 |
| grasp_object | 1.00 | 1.00 | 0.0167 |
| lift_clear | 0.33 | 1.00 | 0.1014 |
| transport_to_goal | 1.00 | 1.00 | 0.2711 |
| descend_place | 1.00 | 1.00 | 0.0936 |
| release_object | 1.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.011, 0.285) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.124 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.510, -0.011, 0.285)→(0.510, -0.016, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp_object | grasp | 1.00 / condition_met | (0.510, -0.016, 0.054)→(0.503, -0.016, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.135 | 0.176 |
| lift_clear | lift | 0.33 / step_budget | (0.503, -0.016, 0.039)→(0.499, -0.016, 0.141) | (0.515, -0.016, 0.026)→(0.506, -0.016, 0.120) | 0.270→0.239 | 1.00 / 39.000 | 0.077 | 0.502 |
| transport_to_goal | approach | 1.00 / step_budget | (0.499, -0.016, 0.141)→(0.608, 0.169, 0.296) | (0.506, -0.016, 0.120)→(0.615, 0.169, 0.272) | 0.239→0.104 | 1.00 / 29.333 | 0.101 | 0.157 |
| descend_place | descend | 1.00 / step_budget | (0.608, 0.169, 0.296)→(0.613, 0.178, 0.203) | (0.615, 0.169, 0.272)→(0.621, 0.181, 0.105) | 0.104→0.079 | 1.00 / 23.000 | 0.265 | 0.930 |
| release_object | release | 1.00 / step_budget | (0.613, 0.178, 0.203)→(0.608, 0.177, 0.223) | (0.621, 0.181, 0.105)→(0.619, 0.180, 0.022) | 0.079→0.147 | 1.00 / 2.667 | 0.115 | 1.110 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.532
- phase_score: 0.798
- phase_breakdown.pre_grasp_score: 0.680
- phase_breakdown.transport_goal_score: 0.827
- grasp_place_fitness: 0.738

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.738
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.532
- **Median Q (composite search score)**: 0.141
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: transport_to_goal.transport_height
- **Final σ (mean)**: 0.334


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
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46008,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06077,"descend_grasp.speed":0.07335,"descend_place.place_height":0.02425,"descend_place.speed":0.0261,"grasp_object.speed":0.02539,"lift_clear.lift_clear_height":0.17286,"lift_clear.speed":0.06725,"release_object.max_time":1.20712,"transport_to_goal.speed":0.07926,"transport_to_goal.transport_height":0.1},"optimized_scores":{"best_composite_score":0.10402,"best_fitness_score":0.61116,"best_task_score":0.27883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.61947,0.22957,-0.00921],"force_p95":1.63395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.34036,"mean_force":0.99833,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60544,0.22194,0.24114]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61836,0.22984,-0.00317],"force_p95":0.2215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57543,"mean_force":0.12461,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60235,0.22124,0.23828]},{"body_a":"world","body_b":"grasp_target","contact_count":167.0,"contact_point_centroid":[0.53324,-0.02027,-0.00116],"force_p95":0.39899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52183,"mean_force":0.08768,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52257,-0.02063,0.04018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17263.0,"contact_point_centroid":[0.52136,-0.00154,0.09266],"force_p95":0.08638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33318,"mean_force":0.05873,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51997,-0.02057,0.09071]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17846.0,"contact_point_centroid":[0.52136,-0.03956,0.09133],"force_p95":0.08519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30541,"mean_force":0.05737,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51998,-0.02057,0.08963]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":259.0,"contact_point_centroid":[0.60843,0.19597,0.27982],"force_p95":0.21417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2709,"mean_force":0.15327,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60276,0.2138,0.28441]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":429.0,"contact_point_centroid":[0.60857,0.23154,0.27773],"force_p95":0.16388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26087,"mean_force":0.10093,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60277,0.21404,0.28239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8843.0,"contact_point_centroid":[0.56184,0.10673,0.21222],"force_p95":0.10997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21603,"mean_force":0.07587,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55713,0.08815,0.21168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8746.0,"contact_point_centroid":[0.5617,0.06951,0.21248],"force_p95":0.11127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19851,"mean_force":0.07678,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55716,0.08812,0.21171]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53703,-0.02117,-0.00206],"force_p95":0.14035,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18224,"mean_force":0.12749,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52542,-0.02068,0.04033]},{"body_a":"world","body_b":"grasp_target","contact_count":300.0,"contact_point_centroid":[0.53702,-0.02132,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12447,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50886,-0.00551,0.29258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4102.0,"contact_point_centroid":[0.5246,-0.00146,0.04139],"force_p95":0.07765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1305,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52431,-0.02067,0.03859]},{"body_a":"world","body_b":"grasp_target","contact_count":2880.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52442,-0.01647,0.16719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.52471,-0.03976,0.04045],"force_p95":0.07002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08062,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52431,-0.02067,0.0386]},{"body_a":"left_finger","body_b":"right_finger","contact_count":80.0,"contact_point_centroid":[0.60399,0.22192,0.23536],"force_p95":0.01612,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01243,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60373,0.2219,0.23306]}],"total_contact_groups":15},"final_pose_error":0.0098,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61841,0.2299,0.01602],"final_tcp_position":[0.6057,0.22257,0.23859],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.34036,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":76.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02594],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12235,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":300.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.51984,-0.01228,0.28402],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02594],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31677,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2880.0,"raw_peak_contact_force":0.12264,"subtask_id":"pre_grasp","tcp_end":[0.53138,-0.02069,0.05395],"tcp_start":[0.51984,-0.01228,0.28402],"tcp_to_object_dist_end":0.0285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":51.0,"n_steps_budget":720.0,"object_pos_end":[0.53694,-0.02065,0.02578],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31635,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13698,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10819.0,"raw_peak_contact_force":0.18224,"subtask_id":"pre_grasp","tcp_end":[0.52428,-0.02066,0.03856],"tcp_start":[0.53138,-0.02069,0.05395],"tcp_to_object_dist_end":0.01799,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52955,-0.02054,0.12707],"object_pos_start":[0.53694,-0.02065,0.02578],"object_to_goal_dist_end":0.27318,"object_to_goal_dist_start":0.31635,"object_z_max":0.12695,"peak_contact_force":0.09464,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35276.0,"raw_peak_contact_force":0.52183,"subtask_id":"pre_grasp","tcp_end":[0.52017,-0.02056,0.14811],"tcp_start":[0.52428,-0.02066,0.03856],"tcp_to_object_dist_end":0.02304,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.61201,0.21278,0.26284],"object_pos_start":[0.52955,-0.02054,0.12707],"object_to_goal_dist_end":0.05744,"object_to_goal_dist_start":0.27318,"object_z_max":0.26268,"peak_contact_force":0.14601,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17589.0,"raw_peak_contact_force":0.21603,"subtask_id":"transport_goal","tcp_end":[0.60293,0.21246,0.28953],"tcp_start":[0.52017,-0.02056,0.14811],"tcp_to_object_dist_end":0.0282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.61926,0.23089,-0.00668],"object_pos_start":[0.61201,0.21278,0.26284],"object_to_goal_dist_end":0.2143,"object_to_goal_dist_start":0.05744,"object_z_max":0.26294,"peak_contact_force":0.62283,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":748.0,"raw_peak_contact_force":2.34036,"subtask_id":"transport_goal","tcp_end":[0.6057,0.22257,0.23859],"tcp_start":[0.60293,0.21246,0.28953],"tcp_to_object_dist_end":0.24578,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61841,0.2299,0.01602],"object_pos_start":[0.61926,0.23089,-0.00668],"object_to_goal_dist_end":0.19157,"object_to_goal_dist_start":0.2143,"object_z_max":0.0168,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":880.0,"raw_peak_contact_force":0.57543,"tcp_end":[0.60125,0.2207,0.25768],"tcp_start":[0.6057,0.22257,0.23859],"tcp_to_object_dist_end":0.24244,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63284,0.16493,0.17692]},{"name":"goal","value":[0.5456,-0.02923,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83548,"average_solve_count":389.0,"average_success_count":389.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07076,"descend_grasp.speed":0.05456,"descend_place.place_height":0.0179,"descend_place.speed":0.01655,"grasp_object.speed":0.03158,"lift_clear.lift_clear_height":0.15694,"lift_clear.speed":0.05704,"release_object.max_time":1.27799,"transport_to_goal.speed":0.05594,"transport_to_goal.transport_height":0.17859},"optimized_scores":{"best_composite_score":0.1415,"best_fitness_score":0.64864,"best_task_score":0.35382},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":115.0,"contact_point_centroid":[0.62245,0.16098,-0.01112],"force_p95":1.41786,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48295,"mean_force":0.63478,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62325,0.16089,0.21368]},{"body_a":"world","body_b":"grasp_target","contact_count":214.0,"contact_point_centroid":[0.5404,-0.02792,-0.00122],"force_p95":0.3056,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52021,"mean_force":0.09694,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.53075,-0.02831,0.04005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19905.0,"contact_point_centroid":[0.52844,-0.00909,0.08766],"force_p95":0.07647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32454,"mean_force":0.05073,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52838,-0.02822,0.08568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20016.0,"contact_point_centroid":[0.5285,-0.04735,0.08579],"force_p95":0.07518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30411,"mean_force":0.05093,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52839,-0.02822,0.08407]},{"body_a":"world","body_b":"grasp_target","contact_count":1796.0,"contact_point_centroid":[0.54562,-0.02906,-0.00208],"force_p95":0.14472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19838,"mean_force":0.12868,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53389,-0.02841,0.0402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6496.0,"contact_point_centroid":[0.62995,0.17679,0.27121],"force_p95":0.07768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18837,"mean_force":0.05581,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6265,0.15778,0.26949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.63032,0.18115,0.20049],"force_p95":0.07466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18792,"mean_force":0.04797,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62678,0.16204,0.19904]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6216.0,"contact_point_centroid":[0.62916,0.13883,0.27048],"force_p95":0.08043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18303,"mean_force":0.05795,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62651,0.15781,0.26918]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1058.0,"contact_point_centroid":[0.62984,0.14297,0.20065],"force_p95":0.0773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18195,"mean_force":0.04969,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6268,0.16204,0.19908]},{"body_a":"world","body_b":"grasp_target","contact_count":408.0,"contact_point_centroid":[0.5456,-0.02923,-0.00169],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12386,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51317,-0.00906,0.29092]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4096.0,"contact_point_centroid":[0.53311,-0.00917,0.04127],"force_p95":0.07836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1338,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53279,-0.02838,0.03846]},{"body_a":"world","body_b":"grasp_target","contact_count":2980.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53297,-0.02388,0.16626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16697.0,"contact_point_centroid":[0.57493,0.04285,0.23076],"force_p95":0.07024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11375,"mean_force":0.04755,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57484,0.06199,0.22895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16489.0,"contact_point_centroid":[0.57847,0.08582,0.23636],"force_p95":0.07369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10808,"mean_force":0.0479,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57738,0.06665,0.23427]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4935.0,"contact_point_centroid":[0.53321,-0.04748,0.04031],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07826,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53279,-0.02838,0.03846]}],"total_contact_groups":15},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63592,0.16104,0.02115],"final_tcp_position":[0.62863,0.16251,0.20353],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.48295,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12229,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":408.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.5284,-0.01934,0.28164],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2980.0,"raw_peak_contact_force":0.12264,"subtask_id":"pre_grasp","tcp_end":[0.53985,-0.02847,0.05413],"tcp_start":[0.5284,-0.01934,0.28164],"tcp_to_object_dist_end":0.0287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":49.0,"n_steps_budget":600.0,"object_pos_end":[0.54552,-0.02841,0.02573],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26051,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14051,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.19838,"subtask_id":"pre_grasp","tcp_end":[0.53276,-0.02838,0.03842],"tcp_start":[0.53985,-0.02847,0.05413],"tcp_to_object_dist_end":0.018,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5349,-0.0282,0.11048],"object_pos_start":[0.54552,-0.02841,0.02573],"object_to_goal_dist_end":0.22651,"object_to_goal_dist_start":0.26051,"object_z_max":0.11038,"peak_contact_force":0.06819,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40135.0,"raw_peak_contact_force":0.52021,"subtask_id":"pre_grasp","tcp_end":[0.52849,-0.02822,0.13023],"tcp_start":[0.53276,-0.02838,0.03842],"tcp_to_object_dist_end":0.02076,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":798.0,"n_steps_budget":1000.0,"object_pos_end":[0.63016,0.15374,0.31106],"object_pos_start":[0.5349,-0.0282,0.11048],"object_to_goal_dist_end":0.13464,"object_to_goal_dist_start":0.22651,"object_z_max":0.31084,"peak_contact_force":0.07809,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33186.0,"raw_peak_contact_force":0.11375,"subtask_id":"transport_goal","tcp_end":[0.62576,0.15379,0.33436],"tcp_start":[0.52849,-0.02822,0.13023],"tcp_to_object_dist_end":0.02371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.63377,0.1625,0.17802],"object_pos_start":[0.63016,0.15374,0.31106],"object_to_goal_dist_end":0.00282,"object_to_goal_dist_start":0.13464,"object_z_max":0.31122,"peak_contact_force":0.07738,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12712.0,"raw_peak_contact_force":0.18837,"subtask_id":"transport_goal","tcp_end":[0.62863,0.16251,0.20353],"tcp_start":[0.62576,0.15379,0.33436],"tcp_to_object_dist_end":0.02603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63592,0.16104,0.02115],"object_pos_start":[0.63377,0.1625,0.17802],"object_to_goal_dist_end":0.15585,"object_to_goal_dist_start":0.00282,"object_z_max":0.17802,"peak_contact_force":0.07336,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2289.0,"raw_peak_contact_force":1.48295,"tcp_end":[0.62321,0.16088,0.22236],"tcp_start":[0.62863,0.16251,0.20353],"tcp_to_object_dist_end":0.20161,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61015,0.15287,0.12219]},{"name":"goal","value":[0.46286,-7e-05,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92795,"average_solve_count":347.0,"average_success_count":347.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.05373,"descend_grasp.speed":0.06804,"descend_place.place_height":0.03864,"descend_place.speed":0.01442,"grasp_object.speed":0.02694,"lift_clear.lift_clear_height":0.14219,"lift_clear.speed":0.04873,"release_object.max_time":0.81522,"transport_to_goal.speed":0.07107,"transport_to_goal.transport_height":0.16048},"optimized_scores":{"best_composite_score":0.2306,"best_fitness_score":0.73774,"best_task_score":0.53185},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.60104,0.14831,-0.00911],"force_p95":1.21622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27138,"mean_force":0.52326,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59829,0.14846,0.17824]},{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.45939,-0.00026,-0.00115],"force_p95":0.28869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46453,"mean_force":0.07549,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.45149,-0.0002,0.0425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":882.0,"contact_point_centroid":[0.60512,0.13058,0.16393],"force_p95":0.09196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30443,"mean_force":0.06019,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60223,0.14963,0.16412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20704.0,"contact_point_centroid":[0.44908,0.01894,0.09609],"force_p95":0.07174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27993,"mean_force":0.04872,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44904,-0.00021,0.09394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20352.0,"contact_point_centroid":[0.44898,-0.01937,0.09539],"force_p95":0.07171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27666,"mean_force":0.04943,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44904,-0.00021,0.09319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5315.0,"contact_point_centroid":[0.6026,0.16438,0.21899],"force_p95":0.07793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26257,"mean_force":0.05731,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59921,0.14541,0.21764]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1019.0,"contact_point_centroid":[0.60553,0.16852,0.16474],"force_p95":0.08062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25364,"mean_force":0.05323,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60227,0.14964,0.16419]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4869.0,"contact_point_centroid":[0.60176,0.12636,0.21967],"force_p95":0.08499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21479,"mean_force":0.06174,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5991,0.14531,0.21872]},{"body_a":"world","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.46285,-9e-05,-0.00202],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14637,"mean_force":0.1243,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45403,-0.00017,0.04254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13272.0,"contact_point_centroid":[0.5216,0.05157,0.20506],"force_p95":0.06755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14201,"mean_force":0.04491,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52161,0.07072,0.2028]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.46286,-7e-05,-0.00134],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12467,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49156,-5e-05,0.29477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12277.0,"contact_point_centroid":[0.52226,0.08962,0.20506],"force_p95":0.07173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13797,"mean_force":0.04832,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52128,0.07041,0.20253]},{"body_a":"world","body_b":"grasp_target","contact_count":3008.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12703,"mean_force":0.12265,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4694,-8e-05,0.17008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45305,0.01902,0.04283],"force_p95":0.068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08865,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45294,-0.00018,0.04094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4860.0,"contact_point_centroid":[0.45306,-0.01937,0.04284],"force_p95":0.06794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08676,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45294,-0.00018,0.04094]}],"total_contact_groups":15},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60251,0.14872,0.02788],"final_tcp_position":[0.6043,0.15013,0.16827],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.27138,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":51.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02587],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.23316,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12742,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":200.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48113,-7e-05,0.28786],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02587],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23316,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3008.0,"raw_peak_contact_force":0.12703,"subtask_id":"pre_grasp","tcp_end":[0.45979,-0.00011,0.05529],"tcp_start":[0.48113,-7e-05,0.28786],"tcp_to_object_dist_end":0.02943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":60.0,"n_steps_budget":690.0,"object_pos_end":[0.46276,-0.00015,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12802,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11564.0,"raw_peak_contact_force":0.14637,"subtask_id":"pre_grasp","tcp_end":[0.45291,-0.00018,0.04091],"tcp_start":[0.45979,-0.00011,0.05529],"tcp_to_object_dist_end":0.01794,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45402,-0.00031,0.12301],"object_pos_start":[0.46276,-0.00015,0.02592],"object_to_goal_dist_end":0.21873,"object_to_goal_dist_start":0.23325,"object_z_max":0.1229,"peak_contact_force":0.06875,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41209.0,"raw_peak_contact_force":0.46453,"subtask_id":"pre_grasp","tcp_end":[0.4491,-0.0002,0.14355],"tcp_start":[0.45291,-0.00018,0.04091],"tcp_to_object_dist_end":0.02113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.60391,0.14186,0.24199],"object_pos_start":[0.45402,-0.00031,0.12301],"object_to_goal_dist_end":0.12047,"object_to_goal_dist_start":0.21873,"object_z_max":0.24182,"peak_contact_force":0.07998,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25549.0,"raw_peak_contact_force":0.14201,"subtask_id":"transport_goal","tcp_end":[0.59654,0.14165,0.26517],"tcp_start":[0.4491,-0.0002,0.14355],"tcp_to_object_dist_end":0.02432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.61129,0.15,0.14279],"object_pos_start":[0.60391,0.14186,0.24199],"object_to_goal_dist_end":0.02083,"object_to_goal_dist_start":0.12047,"object_z_max":0.2421,"peak_contact_force":0.09613,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10184.0,"raw_peak_contact_force":0.26257,"subtask_id":"transport_goal","tcp_end":[0.6043,0.15013,0.16827],"tcp_start":[0.59654,0.14165,0.26517],"tcp_to_object_dist_end":0.02642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60251,0.14872,0.02788],"object_pos_start":[0.61129,0.15,0.14279],"object_to_goal_dist_end":0.09471,"object_to_goal_dist_start":0.02083,"object_z_max":0.14279,"peak_contact_force":0.14876,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2037.0,"raw_peak_contact_force":1.27138,"tcp_end":[0.59822,0.14845,0.18838],"tcp_start":[0.6043,0.15013,0.16827],"tcp_to_object_dist_end":0.16056,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```