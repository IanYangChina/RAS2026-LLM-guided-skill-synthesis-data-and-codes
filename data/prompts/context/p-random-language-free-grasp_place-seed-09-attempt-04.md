## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1876 | 0.38 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1922 | 0.17 | ✅ accepted |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1650 | 0.13 | ❌ rejected |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1646 | 0.13 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.188) — your mutation base

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
  weight: 0.3
- id: reach_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_above
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
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
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
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
- id: lift_up
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_above_goal
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
- id: release_object
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_up** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_from_goal** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.188
- **task_score** (E): 0.381
- **fitness_score**: 0.668  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1576 |
| descend_to_grasp | 1.00 | 1.00 | 0.1139 |
| grasp_object | 1.00 | 1.00 | 0.0130 |
| lift_up | 1.00 | 1.00 | 0.1357 |
| transport_above_goal | 1.00 | 1.00 | 0.2612 |
| descend_to_place | 1.00 | 1.00 | 0.1157 |
| release_object | 1.00 | 1.00 | 0.0198 |
| retract_from_goal | 1.00 | 1.00 | 0.0930 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.148)→(0.510, -0.017, 0.034) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 7.553 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, -0.017, 0.034)→(0.501, -0.016, 0.025) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.667 | 0.136 | 0.164 |
| lift_up | lift | 1.00 / step_budget | (0.501, -0.016, 0.025)→(0.510, -0.017, 0.160) | (0.515, -0.017, 0.026)→(0.523, -0.017, 0.157) | 0.270→0.226 | 1.00 / 39.333 | 0.077 | 0.563 |
| transport_above_goal | approach | 1.00 / step_budget | (0.510, -0.017, 0.160)→(0.611, 0.172, 0.303) | (0.523, -0.017, 0.157)→(0.619, 0.175, 0.295) | 0.226→0.127 | 1.00 / 38.667 | 0.081 | 0.142 |
| descend_to_place | descend | 1.00 / step_budget | (0.611, 0.172, 0.303)→(0.613, 0.179, 0.188) | (0.619, 0.175, 0.295)→(0.621, 0.182, 0.177) | 0.127→0.009 | 1.00 / 34.667 | 0.089 | 0.156 |
| release_object | release | 1.00 / step_budget | (0.613, 0.179, 0.188)→(0.607, 0.177, 0.207) | (0.621, 0.182, 0.177)→(0.615, 0.178, 0.017) | 0.009→0.153 | 1.00 / 4.000 | 0.090 | 1.691 |
| retract_from_goal | retract | 1.00 / step_budget | (0.607, 0.177, 0.207)→(0.615, 0.181, 0.299) | (0.615, 0.178, 0.017)→(0.615, 0.179, 0.019) | 0.153→0.150 | 1.00 / 4.000 | 0.123 | 0.129 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.522
- phase_score: 0.249
- phase_breakdown.approach_object_score: 0.676
- phase_breakdown.reach_goal_score: 0.066
- grasp_place_fitness: 0.741

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.741
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.522
- **Median Q (composite search score)**: 0.167
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.412


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14596,"average_solve_count":322.0,"average_success_count":322.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.13024,"descend_to_grasp.descend_speed":0.06526,"descend_to_place.descend_place_speed":0.04606,"lift_up.lift_height":0.16129,"lift_up.lift_speed":0.016,"transport_above_goal.transport_speed":0.13297},"optimized_scores":{"best_composite_score":0.13572,"best_fitness_score":0.61572,"best_task_score":0.27903},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":167.0,"contact_point_centroid":[0.61338,0.22622,-0.00849],"force_p95":1.45913,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02507,"mean_force":0.47427,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6018,0.22246,0.23878]},{"body_a":"world","body_b":"grasp_target","contact_count":105.0,"contact_point_centroid":[0.53326,-0.02075,-0.0015],"force_p95":0.48718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54198,"mean_force":0.21769,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52093,-0.02078,0.02447]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12021.0,"contact_point_centroid":[0.52591,-0.00187,0.09451],"force_p95":0.07794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23162,"mean_force":0.05072,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52471,-0.02087,0.09272]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9996.0,"contact_point_centroid":[0.52518,-0.04006,0.09635],"force_p95":0.08152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23154,"mean_force":0.05878,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52478,-0.02087,0.09356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":828.0,"contact_point_centroid":[0.601,0.24242,0.22514],"force_p95":0.09842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22049,"mean_force":0.06322,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6048,0.22378,0.2212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.61202,0.20641,0.21997],"force_p95":0.0816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.181,"mean_force":0.04897,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60483,0.2238,0.22127]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3336.0,"contact_point_centroid":[0.60104,0.23855,0.29542],"force_p95":0.09247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15982,"mean_force":0.06074,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60569,0.22018,0.29257]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.0213,-0.00204],"force_p95":0.13621,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15846,"mean_force":0.12607,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52334,-0.02081,0.02525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4049.0,"contact_point_centroid":[0.61274,0.20288,0.28636],"force_p95":0.0756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1488,"mean_force":0.05289,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60575,0.22049,0.28724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16862.0,"contact_point_centroid":[0.57318,0.08514,0.2572],"force_p95":0.08575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14388,"mean_force":0.05846,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.56884,0.10366,0.2562]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51321,-0.00886,0.22479]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17445.0,"contact_point_centroid":[0.56521,0.11581,0.25321],"force_p95":0.08436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12859,"mean_force":0.05585,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.5667,0.097,0.25122]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.6153,0.22617,-0.00203],"force_p95":0.1242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12647,"mean_force":0.11853,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.60396,0.22414,0.29104]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52822,-0.0196,0.0896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5297.0,"contact_point_centroid":[0.52312,-0.00176,0.02613],"force_p95":0.06803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10165,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,-0.02079,0.0238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4171.0,"contact_point_centroid":[0.52309,-0.0401,0.02648],"force_p95":0.07967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0937,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52205,-0.02079,0.02381]}],"total_contact_groups":16},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6153,0.22617,0.01602],"final_tcp_position":[0.60779,0.22642,0.33777],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.02507,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52861,-0.01834,0.14745],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1468.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53099,-0.0209,0.03397],"tcp_start":[0.52861,-0.01834,0.14745],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02109,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31668,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13601,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11268.0,"raw_peak_contact_force":0.15846,"tcp_end":[0.52202,-0.02079,0.02377],"tcp_start":[0.53099,-0.0209,0.03397],"tcp_to_object_dist_end":0.015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.54541,-0.02147,0.16445],"object_pos_start":[0.53688,-0.02109,0.02584],"object_to_goal_dist_end":0.2611,"object_to_goal_dist_start":0.31668,"object_z_max":0.16421,"peak_contact_force":0.08067,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22122.0,"raw_peak_contact_force":0.54198,"tcp_end":[0.53192,-0.02102,0.16785],"tcp_start":[0.52202,-0.02079,0.02377],"tcp_to_object_dist_end":0.01392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":959.0,"n_steps_budget":1000.0,"object_pos_end":[0.61578,0.22132,0.33099],"object_pos_start":[0.54541,-0.02147,0.16445],"object_to_goal_dist_end":0.12387,"object_to_goal_dist_start":0.2611,"object_z_max":0.33085,"peak_contact_force":0.07849,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34307.0,"raw_peak_contact_force":0.14388,"subtask_id":"reach_goal","tcp_end":[0.60557,0.21714,0.34137],"tcp_start":[0.53192,-0.02102,0.16785],"tcp_to_object_dist_end":0.01515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.61621,0.22931,0.21304],"object_pos_start":[0.61578,0.22132,0.33099],"object_to_goal_dist_end":0.0083,"object_to_goal_dist_start":0.12387,"object_z_max":0.33102,"peak_contact_force":0.09295,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7385.0,"raw_peak_contact_force":0.15982,"tcp_end":[0.60676,0.22451,0.22675],"tcp_start":[0.60557,0.21714,0.34137],"tcp_to_object_dist_end":0.01733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61518,0.22474,0.01025],"object_pos_start":[0.61621,0.22931,0.21304],"object_to_goal_dist_end":0.19724,"object_to_goal_dist_start":0.0083,"object_z_max":0.21304,"peak_contact_force":0.07992,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2174.0,"raw_peak_contact_force":2.02507,"tcp_end":[0.60177,0.22246,0.24529],"tcp_start":[0.60676,0.22451,0.22675],"tcp_to_object_dist_end":0.23543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":720.0,"object_pos_end":[0.6153,0.22617,0.01602],"object_pos_start":[0.61518,0.22474,0.01025],"object_to_goal_dist_end":0.19146,"object_to_goal_dist_start":0.19724,"object_z_max":0.01668,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12647,"tcp_end":[0.60779,0.22642,0.33777],"tcp_start":[0.60177,0.22246,0.24529],"tcp_to_object_dist_end":0.32183,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20063,"average_solve_count":319.0,"average_success_count":319.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.13321,"descend_to_grasp.descend_speed":0.02846,"descend_to_place.descend_place_speed":0.05726,"lift_up.lift_height":0.17438,"lift_up.lift_speed":0.03538,"transport_above_goal.transport_speed":0.18619},"optimized_scores":{"best_composite_score":0.16656,"best_fitness_score":0.64656,"best_task_score":0.34206},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.63162,0.16279,-0.00734],"force_p95":1.31125,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78037,"mean_force":0.3886,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62262,0.16035,0.20655]},{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.54183,-0.02826,-0.00147],"force_p95":0.53,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59309,"mean_force":0.21878,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52931,-0.0284,0.0241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1215.0,"contact_point_centroid":[0.62275,0.17983,0.19191],"force_p95":0.08871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2969,"mean_force":0.05054,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62618,0.16144,0.19007]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10417.0,"contact_point_centroid":[0.53419,-0.04768,0.10364],"force_p95":0.08405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29498,"mean_force":0.06031,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53348,-0.02849,0.10085]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12708.0,"contact_point_centroid":[0.53482,-0.00953,0.10076],"force_p95":0.08142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25355,"mean_force":0.05131,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.53333,-0.02848,0.09912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":934.0,"contact_point_centroid":[0.62974,0.14255,0.18913],"force_p95":0.10492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19912,"mean_force":0.06053,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62615,0.16143,0.19002]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.0292,-0.00206],"force_p95":0.14397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19021,"mean_force":0.12782,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5317,-0.02846,0.02479]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3215.0,"contact_point_centroid":[0.63083,0.13925,0.25728],"force_p95":0.09666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17168,"mean_force":0.06697,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62678,0.15804,0.25781]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4283.0,"contact_point_centroid":[0.62296,0.17635,0.25871],"force_p95":0.07549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17,"mean_force":0.04945,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62681,0.1581,0.25677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11445.0,"contact_point_centroid":[0.58585,0.04553,0.24554],"force_p95":0.09394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16037,"mean_force":0.06486,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.58273,0.06447,0.24434]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13661.0,"contact_point_centroid":[0.5827,0.08486,0.24711],"force_p95":0.08115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15247,"mean_force":0.05282,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.58355,0.06616,0.24559]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51695,-0.01222,0.22425]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.63369,0.16313,-0.00199],"force_p95":0.12409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12484,"mean_force":0.12,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.62519,0.16183,0.26018]},{"body_a":"world","body_b":"grasp_target","contact_count":1548.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53608,-0.02688,0.08929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4863.0,"contact_point_centroid":[0.53218,-0.00951,0.02481],"force_p95":0.07324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1115,"mean_force":0.04409,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5304,-0.02843,0.0233]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4258.0,"contact_point_centroid":[0.53131,-0.04767,0.02589],"force_p95":0.09142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09343,"mean_force":0.0534,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5304,-0.02843,0.0233]}],"total_contact_groups":16},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63369,0.16313,0.01602],"final_tcp_position":[0.62971,0.16379,0.3072],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.78037,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53611,-0.02522,0.14679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1548.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5394,-0.02864,0.03373],"tcp_start":[0.53611,-0.02522,0.14679],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54561,-0.02878,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26073,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14416,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10921.0,"raw_peak_contact_force":0.19021,"tcp_end":[0.53037,-0.02842,0.02326],"tcp_start":[0.5394,-0.02864,0.03373],"tcp_to_object_dist_end":0.01545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.55477,-0.02914,0.1769],"object_pos_start":[0.54561,-0.02878,0.02577],"object_to_goal_dist_end":0.20919,"object_to_goal_dist_start":0.26073,"object_z_max":0.17666,"peak_contact_force":0.08204,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23222.0,"raw_peak_contact_force":0.59309,"tcp_end":[0.54085,-0.02866,0.18077],"tcp_start":[0.53037,-0.02842,0.02326],"tcp_to_object_dist_end":0.01445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.63557,0.15737,0.30138],"object_pos_start":[0.55477,-0.02914,0.1769],"object_to_goal_dist_end":0.12472,"object_to_goal_dist_start":0.20919,"object_z_max":0.30125,"peak_contact_force":0.09587,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25106.0,"raw_peak_contact_force":0.16037,"subtask_id":"reach_goal","tcp_end":[0.62625,0.15481,0.31107],"tcp_start":[0.54085,-0.02866,0.18077],"tcp_to_object_dist_end":0.01368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.63757,0.16499,0.18275],"object_pos_start":[0.63557,0.15737,0.30138],"object_to_goal_dist_end":0.00751,"object_to_goal_dist_start":0.12472,"object_z_max":0.30141,"peak_contact_force":0.10126,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7498.0,"raw_peak_contact_force":0.17168,"tcp_end":[0.62844,0.162,0.19569],"tcp_start":[0.62625,0.15481,0.31107],"tcp_to_object_dist_end":0.01611,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63369,0.16328,0.01319],"object_pos_start":[0.63757,0.16499,0.18275],"object_to_goal_dist_end":0.16374,"object_to_goal_dist_start":0.00751,"object_z_max":0.18275,"peak_contact_force":0.07484,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2343.0,"raw_peak_contact_force":1.78037,"tcp_end":[0.62258,0.16035,0.21403],"tcp_start":[0.62844,0.162,0.19569],"tcp_to_object_dist_end":0.20116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":720.0,"object_pos_end":[0.63369,0.16313,0.01602],"object_pos_start":[0.63369,0.16328,0.01319],"object_to_goal_dist_end":0.16091,"object_to_goal_dist_start":0.16374,"object_z_max":0.01658,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.12484,"tcp_end":[0.62971,0.16379,0.3072],"tcp_start":[0.62258,0.16035,0.21403],"tcp_to_object_dist_end":0.29121,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37786,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.13037,"descend_to_grasp.descend_speed":0.02925,"descend_to_place.descend_place_speed":0.07959,"lift_up.lift_height":0.12442,"lift_up.lift_speed":0.04285,"transport_above_goal.transport_speed":0.18921},"optimized_scores":{"best_composite_score":0.26067,"best_fitness_score":0.74067,"best_task_score":0.52184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.59524,0.14649,-0.00506],"force_p95":0.79364,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26643,"mean_force":0.24928,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59762,0.14857,0.14989]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.45914,-0.00028,-0.00138],"force_p95":0.53627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55458,"mean_force":0.23024,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44929,-0.00031,0.02767]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8001.0,"contact_point_centroid":[0.45213,0.01886,0.07964],"force_p95":0.06934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24317,"mean_force":0.04812,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.45205,-0.00035,0.07799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7994.0,"contact_point_centroid":[0.45217,-0.01957,0.07972],"force_p95":0.06868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24298,"mean_force":0.04808,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.45205,-0.00035,0.07804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.60582,0.13081,0.13606],"force_p95":0.07377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14973,"mean_force":0.04506,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60185,0.14971,0.13559]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.59821,0.16833,0.13895],"force_p95":0.07181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14925,"mean_force":0.04408,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60187,0.14971,0.13563]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00015,-0.00202],"force_p95":0.12959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14449,"mean_force":0.12463,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45129,-0.00027,0.02796]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48241,-5e-05,0.22617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4220.0,"contact_point_centroid":[0.59761,0.16581,0.2041],"force_p95":0.06995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13602,"mean_force":0.04913,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60148,0.14725,0.20099]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.59505,0.14649,-0.00197],"force_p95":0.12936,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13591,"mean_force":0.12229,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.60066,0.14984,0.20613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4220.0,"contact_point_centroid":[0.60545,0.12843,0.20166],"force_p95":0.07088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12677,"mean_force":0.05014,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60148,0.14725,0.20099]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46012,-0.00015,0.09145]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14090.0,"contact_point_centroid":[0.53136,0.05478,0.19527],"force_p95":0.0714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12167,"mean_force":0.04967,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52892,0.07382,0.1939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14297.0,"contact_point_centroid":[0.52631,0.0921,0.19568],"force_p95":0.0706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11263,"mean_force":0.04839,"phase_index":4.0,"phase_name":"transport_above_goal","phase_type":"approach","tcp_position_centroid":[0.52827,0.07317,0.19331]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.45108,-0.0195,0.02889],"force_p95":0.06672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08752,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4501,-0.00029,0.02684]},{"body_a":"grasp_target","body_b":"hand","contact_count":70.0,"contact_point_centroid":[0.47887,0.01968,0.06781],"force_p95":0.04011,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0866,"mean_force":0.02176,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44862,-0.00034,0.03751]}],"total_contact_groups":17},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59504,0.14649,0.02602],"final_tcp_position":[0.60606,0.15165,0.25268],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":22.41272,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46488,-0.00011,0.14947],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":22.41272,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45836,-0.00015,0.03473],"tcp_start":[0.46488,-0.00011,0.14947],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-0.0003,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12896,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.14449,"tcp_end":[0.45007,-0.00029,0.02681],"tcp_start":[0.45836,-0.00015,0.03473],"tcp_to_object_dist_end":0.01267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.46886,-0.00033,0.12852],"object_pos_start":[0.46271,-0.0003,0.02591],"object_to_goal_dist_end":0.2085,"object_to_goal_dist_start":0.23338,"object_z_max":0.12825,"peak_contact_force":0.0684,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16143.0,"raw_peak_contact_force":0.55458,"tcp_end":[0.45745,-0.00036,0.13128],"tcp_start":[0.45007,-0.00029,0.02681],"tcp_to_object_dist_end":0.01174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.6045,0.14576,0.25289],"object_pos_start":[0.46886,-0.00033,0.12852],"object_to_goal_dist_end":0.13101,"object_to_goal_dist_start":0.2085,"object_z_max":0.25276,"peak_contact_force":0.0701,"phase_name":"transport_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28387.0,"raw_peak_contact_force":0.12167,"subtask_id":"reach_goal","tcp_end":[0.59986,0.1446,0.2572],"tcp_start":[0.45745,-0.00036,0.13128],"tcp_to_object_dist_end":0.00644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.61069,0.15202,0.13466],"object_pos_start":[0.6045,0.14576,0.25289],"object_to_goal_dist_end":0.01251,"object_to_goal_dist_start":0.13101,"object_z_max":0.25292,"peak_contact_force":0.0714,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8440.0,"raw_peak_contact_force":0.13602,"tcp_end":[0.60449,0.15033,0.14087],"tcp_start":[0.59986,0.1446,0.2572],"tcp_to_object_dist_end":0.00894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59547,0.14667,0.02639],"object_pos_start":[0.61069,0.15202,0.13466],"object_to_goal_dist_end":0.09712,"object_to_goal_dist_start":0.01251,"object_z_max":0.13466,"peak_contact_force":0.11561,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2732.0,"raw_peak_contact_force":1.26643,"tcp_end":[0.59752,0.14855,0.16031],"tcp_start":[0.60449,0.15033,0.14087],"tcp_to_object_dist_end":0.13395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":357.0,"n_steps_budget":720.0,"object_pos_end":[0.59504,0.14649,0.02602],"object_pos_start":[0.59547,0.14667,0.02639],"object_to_goal_dist_end":0.09756,"object_to_goal_dist_start":0.09712,"object_z_max":0.02653,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1428.0,"raw_peak_contact_force":0.13591,"tcp_end":[0.60606,0.15165,0.25268],"tcp_start":[0.59752,0.14855,0.16031],"tcp_to_object_dist_end":0.22699,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```