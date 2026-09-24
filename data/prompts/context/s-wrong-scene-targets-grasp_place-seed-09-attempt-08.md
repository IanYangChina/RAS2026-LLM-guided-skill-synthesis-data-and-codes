## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.1581 | 0.39 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.4703 | 0.17 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0640 | 0.37 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0646 | 0.37 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | 0.1125 | 0.28 | ❌ rejected |

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

## Current Skill (Q=0.158) — your mutation base

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

- **Composite score**: 0.158
- **task_score** (E): 0.387
- **fitness_score**: 0.665  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.0304 |
| descend_grasp | 1.00 | 1.00 | 0.2306 |
| grasp_object | 1.00 | 1.00 | 0.0168 |
| lift_clear | 1.00 | 1.00 | 0.0976 |
| transport_to_goal | 1.00 | 1.00 | 0.2710 |
| descend_place | 1.00 | 1.00 | 0.0904 |
| release_object | 1.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.011, 0.285) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 13.003 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.510, -0.011, 0.285)→(0.510, -0.016, 0.054) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 35.932 | 0.124 |
| grasp_object | grasp | 1.00 / condition_met | (0.510, -0.016, 0.054)→(0.503, -0.016, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.135 | 0.175 |
| lift_clear | lift | 1.00 / step_budget | (0.503, -0.016, 0.039)→(0.499, -0.016, 0.137) | (0.515, -0.016, 0.026)→(0.505, -0.016, 0.117) | 0.270→0.241 | 1.00 / 43.667 | 0.069 | 0.494 |
| transport_to_goal | approach | 1.00 / step_budget | (0.499, -0.016, 0.137)→(0.608, 0.169, 0.295) | (0.505, -0.016, 0.117)→(0.615, 0.169, 0.272) | 0.241→0.104 | 1.00 / 33.000 | 0.099 | 0.127 |
| descend_place | descend | 1.00 / step_budget | (0.608, 0.169, 0.295)→(0.613, 0.179, 0.205) | (0.615, 0.169, 0.272)→(0.618, 0.179, 0.179) | 0.104→0.011 | 1.00 / 30.000 | 0.104 | 0.241 |
| release_object | release | 1.00 / step_budget | (0.613, 0.179, 0.205)→(0.608, 0.177, 0.225) | (0.618, 0.179, 0.179)→(0.614, 0.171, 0.022) | 0.011→0.148 | 1.00 / 2.667 | 0.145 | 1.696 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.529
- phase_score: 0.846
- phase_breakdown.pre_grasp_score: 0.679
- phase_breakdown.transport_goal_score: 0.888
- grasp_place_fitness: 0.736

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.736
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.529
- **Median Q (composite search score)**: 0.142
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.207


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17264,"average_solve_count":307.0,"average_success_count":307.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04965,"descend_grasp.speed":0.0642,"descend_place.place_height":0.03311,"descend_place.speed":0.0224,"grasp_object.speed":0.01969,"lift_clear.lift_clear_height":0.13978,"lift_clear.speed":0.05763,"release_object.max_time":1.43349,"transport_to_goal.speed":0.07684,"transport_to_goal.transport_height":0.12756},"optimized_scores":{"best_composite_score":0.1033,"best_fitness_score":0.61045,"best_task_score":0.27784},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":334.0,"contact_point_centroid":[0.61498,0.20498,-0.00585],"force_p95":1.07524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07903,"mean_force":0.27192,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60202,0.22165,0.25533]},{"body_a":"world","body_b":"grasp_target","contact_count":206.0,"contact_point_centroid":[0.53235,-0.02023,-0.00119],"force_p95":0.28798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50331,"mean_force":0.08843,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52217,-0.02061,0.04025]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19412.0,"contact_point_centroid":[0.52004,-0.00143,0.08922],"force_p95":0.07766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31663,"mean_force":0.05191,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.51978,-0.02055,0.08722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":122.0,"contact_point_centroid":[0.61173,0.24137,0.24095],"force_p95":0.21351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30702,"mean_force":0.16285,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60552,0.22334,0.2465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19646.0,"contact_point_centroid":[0.52012,-0.03966,0.08717],"force_p95":0.07589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29662,"mean_force":0.05172,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.5198,-0.02056,0.08539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1590.0,"contact_point_centroid":[0.60972,0.20003,0.2796],"force_p95":0.16318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25862,"mean_force":0.11172,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60427,0.21807,0.28299]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1558.0,"contact_point_centroid":[0.60971,0.23585,0.28193],"force_p95":0.16152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25656,"mean_force":0.11976,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60417,0.21773,0.28555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":223.0,"contact_point_centroid":[0.61124,0.20638,0.24096],"force_p95":0.16096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24307,"mean_force":0.08621,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60526,0.22323,0.24573]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.53704,-0.02117,-0.00206],"force_p95":0.1405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18261,"mean_force":0.12747,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52531,-0.02067,0.04046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14097.0,"contact_point_centroid":[0.55835,0.06784,0.21545],"force_p95":0.08799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17767,"mean_force":0.05535,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55651,0.08686,0.21384]},{"body_a":"world","body_b":"grasp_target","contact_count":300.0,"contact_point_centroid":[0.53702,-0.02132,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12447,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50882,-0.00549,0.2926]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13787.0,"contact_point_centroid":[0.56165,0.11393,0.22197],"force_p95":0.08128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13519,"mean_force":0.05561,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55946,0.09488,0.22023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.5245,-0.00145,0.04144],"force_p95":0.0777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13075,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52415,-0.02065,0.03865]},{"body_a":"world","body_b":"grasp_target","contact_count":2956.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5244,-0.01645,0.16744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4915.0,"contact_point_centroid":[0.5246,-0.03974,0.0405],"force_p95":0.07007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07797,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52415,-0.02065,0.03865]}],"total_contact_groups":15},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6149,0.20513,0.01669],"final_tcp_position":[0.60622,0.22347,0.2485],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":76.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02594],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12235,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":300.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.51981,-0.01226,0.28405],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":739.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02594],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31677,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2956.0,"raw_peak_contact_force":0.12264,"subtask_id":"pre_grasp","tcp_end":[0.53138,-0.02068,0.05417],"tcp_start":[0.51981,-0.01226,0.28405],"tcp_to_object_dist_end":0.02872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":55.0,"n_steps_budget":930.0,"object_pos_end":[0.53694,-0.02064,0.02578],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31635,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1371,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10836.0,"raw_peak_contact_force":0.18261,"subtask_id":"pre_grasp","tcp_end":[0.52412,-0.02065,0.03861],"tcp_start":[0.53138,-0.02068,0.05417],"tcp_to_object_dist_end":0.01814,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52627,-0.02054,0.11216],"object_pos_start":[0.53694,-0.02064,0.02578],"object_to_goal_dist_end":0.2789,"object_to_goal_dist_start":0.31635,"object_z_max":0.11206,"peak_contact_force":0.06842,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39264.0,"raw_peak_contact_force":0.50331,"subtask_id":"pre_grasp","tcp_end":[0.51991,-0.02055,0.13225],"tcp_start":[0.52412,-0.02065,0.03861],"tcp_to_object_dist_end":0.02107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.61622,0.21384,0.29171],"object_pos_start":[0.52627,-0.02054,0.11216],"object_to_goal_dist_end":0.08564,"object_to_goal_dist_start":0.2789,"object_z_max":0.29151,"peak_contact_force":0.14552,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27884.0,"raw_peak_contact_force":0.17767,"subtask_id":"transport_goal","tcp_end":[0.60361,0.21367,0.31544],"tcp_start":[0.51991,-0.02055,0.13225],"tcp_to_object_dist_end":0.02687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.61244,0.2239,0.2204],"object_pos_start":[0.61622,0.21384,0.29171],"object_to_goal_dist_end":0.01372,"object_to_goal_dist_start":0.08564,"object_z_max":0.29185,"peak_contact_force":0.15562,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3148.0,"raw_peak_contact_force":0.25862,"subtask_id":"transport_goal","tcp_end":[0.60622,0.22347,0.2485],"tcp_start":[0.60361,0.21367,0.31544],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6149,0.20513,0.01669],"object_pos_start":[0.61244,0.2239,0.2204],"object_to_goal_dist_end":0.19211,"object_to_goal_dist_start":0.01372,"object_z_max":0.2204,"peak_contact_force":0.1183,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":679.0,"raw_peak_contact_force":2.07903,"tcp_end":[0.60199,0.22163,0.26748],"tcp_start":[0.60622,0.22347,0.2485],"tcp_to_object_dist_end":0.25166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82322,"average_solve_count":379.0,"average_success_count":379.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04548,"descend_grasp.speed":0.07502,"descend_place.place_height":0.02164,"descend_place.speed":0.01772,"grasp_object.speed":0.03165,"lift_clear.lift_clear_height":0.11214,"lift_clear.speed":0.05931,"release_object.max_time":1.04144,"transport_to_goal.speed":0.0484,"transport_to_goal.transport_height":0.14532},"optimized_scores":{"best_composite_score":0.14175,"best_fitness_score":0.6489,"best_task_score":0.35422},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":113.0,"contact_point_centroid":[0.62246,0.16111,-0.0113],"force_p95":1.43386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50838,"mean_force":0.65422,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62291,0.16035,0.21706]},{"body_a":"world","body_b":"grasp_target","contact_count":213.0,"contact_point_centroid":[0.54096,-0.02781,-0.00119],"force_p95":0.28779,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51216,"mean_force":0.08856,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.53078,-0.02832,0.04009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19531.0,"contact_point_centroid":[0.52862,-0.0091,0.09023],"force_p95":0.07779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3185,"mean_force":0.0516,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52843,-0.02823,0.08823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19808.0,"contact_point_centroid":[0.52869,-0.04734,0.08812],"force_p95":0.07549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30271,"mean_force":0.05142,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.52845,-0.02823,0.08639]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1121.0,"contact_point_centroid":[0.62991,0.18062,0.20419],"force_p95":0.07485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20894,"mean_force":0.04791,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62639,0.16148,0.20227]},{"body_a":"world","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.54562,-0.02906,-0.00208],"force_p95":0.14458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19711,"mean_force":0.12865,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53392,-0.02841,0.04016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4935.0,"contact_point_centroid":[0.62908,0.17585,0.25734],"force_p95":0.0777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19365,"mean_force":0.05618,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62564,0.15687,0.25561]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1109.0,"contact_point_centroid":[0.6292,0.14242,0.20401],"force_p95":0.07526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18739,"mean_force":0.04777,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62641,0.16149,0.2023]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4671.0,"contact_point_centroid":[0.62824,0.1379,0.25688],"force_p95":0.08105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18531,"mean_force":0.05901,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62565,0.15687,0.2557]},{"body_a":"world","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.5456,-0.02923,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12382,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51295,-0.00897,0.29094]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4096.0,"contact_point_centroid":[0.53314,-0.00918,0.04126],"force_p95":0.07834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13368,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53283,-0.02838,0.03845]},{"body_a":"world","body_b":"grasp_target","contact_count":2824.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53292,-0.02388,0.16606]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15124.0,"contact_point_centroid":[0.5742,0.04132,0.21602],"force_p95":0.07076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10373,"mean_force":0.04742,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5739,0.06042,0.21435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14378.0,"contact_point_centroid":[0.57834,0.08522,0.22188],"force_p95":0.07532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09969,"mean_force":0.0494,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57698,0.06606,0.21969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4933.0,"contact_point_centroid":[0.53324,-0.04749,0.0403],"force_p95":0.07086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07813,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53283,-0.02838,0.03845]}],"total_contact_groups":15},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63372,0.15941,0.02135],"final_tcp_position":[0.62822,0.16192,0.20673],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":38.76023,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":38.76023,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":420.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52838,-0.01935,0.28159],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2824.0,"raw_peak_contact_force":0.12264,"subtask_id":"pre_grasp","tcp_end":[0.53989,-0.02848,0.05399],"tcp_start":[0.52838,-0.01935,0.28159],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":48.0,"n_steps_budget":600.0,"object_pos_end":[0.54552,-0.02842,0.02573],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26051,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1404,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10821.0,"raw_peak_contact_force":0.19711,"subtask_id":"pre_grasp","tcp_end":[0.5328,-0.02838,0.03841],"tcp_start":[0.53989,-0.02848,0.05399],"tcp_to_object_dist_end":0.01796,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53496,-0.02821,0.11483],"object_pos_start":[0.54552,-0.02842,0.02573],"object_to_goal_dist_end":0.22525,"object_to_goal_dist_start":0.26051,"object_z_max":0.11472,"peak_contact_force":0.07142,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39552.0,"raw_peak_contact_force":0.51216,"subtask_id":"pre_grasp","tcp_end":[0.52857,-0.02823,0.13472],"tcp_start":[0.5328,-0.02838,0.03841],"tcp_to_object_dist_end":0.02089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.62943,0.1527,0.279],"object_pos_start":[0.53496,-0.02821,0.11483],"object_to_goal_dist_end":0.10287,"object_to_goal_dist_start":0.22525,"object_z_max":0.2788,"peak_contact_force":0.07856,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29502.0,"raw_peak_contact_force":0.10373,"subtask_id":"transport_goal","tcp_end":[0.62479,0.15276,0.30229],"tcp_start":[0.52857,-0.02823,0.13472],"tcp_to_object_dist_end":0.02374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.63342,0.16196,0.1817],"object_pos_start":[0.62943,0.1527,0.279],"object_to_goal_dist_end":0.00565,"object_to_goal_dist_start":0.10287,"object_z_max":0.27915,"peak_contact_force":0.07775,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9606.0,"raw_peak_contact_force":0.19365,"subtask_id":"transport_goal","tcp_end":[0.62822,0.16192,0.20673],"tcp_start":[0.62479,0.15276,0.30229],"tcp_to_object_dist_end":0.02557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63372,0.15941,0.02135],"object_pos_start":[0.63342,0.16196,0.1817],"object_to_goal_dist_end":0.15567,"object_to_goal_dist_start":0.00565,"object_z_max":0.1817,"peak_contact_force":0.12174,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2343.0,"raw_peak_contact_force":1.50838,"tcp_end":[0.62288,0.16034,0.2256],"tcp_start":[0.62822,0.16192,0.20673],"tcp_to_object_dist_end":0.20455,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.65877,"average_solve_count":422.0,"average_success_count":422.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06896,"descend_grasp.speed":0.0315,"descend_place.place_height":0.03086,"descend_place.speed":0.01297,"grasp_object.speed":0.01923,"lift_clear.lift_clear_height":0.13296,"lift_clear.speed":0.05138,"release_object.max_time":1.0663,"transport_to_goal.speed":0.05252,"transport_to_goal.transport_height":0.16292},"optimized_scores":{"best_composite_score":0.22925,"best_fitness_score":0.73639,"best_task_score":0.52913},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.59014,0.14899,-0.00651],"force_p95":1.16857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4998,"mean_force":0.34695,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59825,0.14854,0.16924]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.45967,-0.00026,-0.00114],"force_p95":0.34274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46684,"mean_force":0.0783,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.45132,-0.0002,0.04239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20756.0,"contact_point_centroid":[0.44889,0.01895,0.09597],"force_p95":0.07175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28211,"mean_force":0.04871,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44889,-0.00021,0.09381]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20471.0,"contact_point_centroid":[0.44881,-0.01937,0.09539],"force_p95":0.07169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27874,"mean_force":0.04927,"phase_index":3.0,"phase_name":"lift_clear","phase_type":"lift","tcp_position_centroid":[0.44889,-0.00021,0.09319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6691.0,"contact_point_centroid":[0.59973,0.16448,0.21889],"force_p95":0.07475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27194,"mean_force":0.05065,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59914,0.14524,0.21746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1161.0,"contact_point_centroid":[0.60315,0.16903,0.15754],"force_p95":0.07549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24031,"mean_force":0.04667,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60227,0.14972,0.15649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1309.0,"contact_point_centroid":[0.60224,0.13071,0.15759],"force_p95":0.06863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19085,"mean_force":0.04159,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60237,0.14975,0.15669]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7672.0,"contact_point_centroid":[0.59899,0.12638,0.21616],"force_p95":0.06523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16999,"mean_force":0.04396,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59938,0.14548,0.21446]},{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.46285,-9e-05,-0.00201],"force_p95":0.12818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14638,"mean_force":0.12426,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45392,-0.00017,0.04252]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.46286,-7e-05,-0.00134],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12467,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49156,-5e-05,0.29477]},{"body_a":"world","body_b":"grasp_target","contact_count":3128.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12703,"mean_force":0.12265,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46929,-8e-05,0.17006]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14343.0,"contact_point_centroid":[0.52173,0.05182,0.20643],"force_p95":0.06451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09856,"mean_force":0.04321,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52174,0.07093,0.20408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12204.0,"contact_point_centroid":[0.52042,0.08814,0.205],"force_p95":0.07236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09661,"mean_force":0.05007,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5196,0.0689,0.20228]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.4529,0.01902,0.04272],"force_p95":0.068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08868,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45279,-0.00018,0.04083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4860.0,"contact_point_centroid":[0.45291,-0.01937,0.04273],"force_p95":0.06794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08672,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45279,-0.00018,0.04083]}],"total_contact_groups":15},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59412,0.14753,0.02822],"final_tcp_position":[0.60439,0.15024,0.16066],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":26.53252,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":51.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02587],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.23316,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12742,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":200.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48113,-7e-05,0.28786],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02587],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23316,"object_z_max":0.02602,"peak_contact_force":26.53252,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.12703,"subtask_id":"pre_grasp","tcp_end":[0.45975,-0.00011,0.05533],"tcp_start":[0.48113,-7e-05,0.28786],"tcp_to_object_dist_end":0.02947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":65.0,"n_steps_budget":960.0,"object_pos_end":[0.46276,-0.00015,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23325,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12797,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11584.0,"raw_peak_contact_force":0.14638,"subtask_id":"pre_grasp","tcp_end":[0.45276,-0.00018,0.0408],"tcp_start":[0.45975,-0.00011,0.05533],"tcp_to_object_dist_end":0.01793,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45408,-0.00031,0.12304],"object_pos_start":[0.46276,-0.00015,0.02592],"object_to_goal_dist_end":0.21868,"object_to_goal_dist_start":0.23325,"object_z_max":0.12295,"peak_contact_force":0.06765,"phase_name":"lift_clear","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41382.0,"raw_peak_contact_force":0.46684,"subtask_id":"pre_grasp","tcp_end":[0.44898,-0.0002,0.14354],"tcp_start":[0.45276,-0.00018,0.0408],"tcp_to_object_dist_end":0.02112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.60055,0.14167,0.24407],"object_pos_start":[0.45408,-0.00031,0.12304],"object_to_goal_dist_end":0.12277,"object_to_goal_dist_start":0.21868,"object_z_max":0.24389,"peak_contact_force":0.07403,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26547.0,"raw_peak_contact_force":0.09856,"subtask_id":"transport_goal","tcp_end":[0.59673,0.14162,0.26744],"tcp_start":[0.44898,-0.0002,0.14354],"tcp_to_object_dist_end":0.02368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.60771,0.15021,0.13541],"object_pos_start":[0.60055,0.14167,0.24407],"object_to_goal_dist_end":0.01371,"object_to_goal_dist_start":0.12277,"object_z_max":0.24416,"peak_contact_force":0.07962,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14363.0,"raw_peak_contact_force":0.27194,"subtask_id":"transport_goal","tcp_end":[0.60439,0.15024,0.16066],"tcp_start":[0.59673,0.14162,0.26744],"tcp_to_object_dist_end":0.02546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59412,0.14753,0.02822],"object_pos_start":[0.60771,0.15021,0.13541],"object_to_goal_dist_end":0.09548,"object_to_goal_dist_start":0.01371,"object_z_max":0.13541,"peak_contact_force":0.19606,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2674.0,"raw_peak_contact_force":1.4998,"tcp_end":[0.59816,0.14852,0.18079],"tcp_start":[0.60439,0.15024,0.16066],"tcp_to_object_dist_end":0.15263,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```