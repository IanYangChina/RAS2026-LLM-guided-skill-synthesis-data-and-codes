## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0884 | 0.39 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.3576 | 0.17 | ✅ accepted |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1650 | 0.13 | ❌ rejected |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1646 | 0.13 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

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

## Current Skill (Q=0.088) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_at_goal
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
    - 0.06
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
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
- id: lift
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
    tolerance: 0.015
    orientation:
      mode: none
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
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.015
    orientation:
      mode: none
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release
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
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    retract_speed:
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
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.06], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.088
- **task_score** (E): 0.386
- **fitness_score**: 0.668  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1352 |
| descend_to_grasp | 1.00 | 1.00 | 0.1317 |
| grasp | 1.00 | 1.00 | 0.0129 |
| lift | 1.00 | 1.00 | 0.1712 |
| transport_to_goal | 0.67 | 1.00 | 0.2060 |
| descend_to_place | 1.00 | 1.00 | 0.1027 |
| release | 1.00 | 1.00 | 0.0209 |
| retract | 0.67 | 1.00 | 0.1192 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.172) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.172)→(0.510, -0.017, 0.040) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.017, 0.040)→(0.501, -0.017, 0.031) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 43.667 | 0.134 | 0.154 |
| lift | lift | 1.00 / step_budget | (0.501, -0.017, 0.031)→(0.511, -0.017, 0.201) | (0.515, -0.017, 0.026)→(0.522, -0.017, 0.190) | 0.270→0.228 | 1.00 / 36.333 | 0.084 | 0.648 |
| transport_to_goal | approach | 0.67 / step_budget | (0.511, -0.017, 0.201)→(0.604, 0.150, 0.265) | (0.522, -0.017, 0.190)→(0.610, 0.152, 0.249) | 0.228→0.094 | 1.00 / 35.000 | 0.080 | 0.144 |
| descend_to_place | descend | 1.00 / step_budget | (0.604, 0.150, 0.265)→(0.613, 0.178, 0.173) | (0.610, 0.152, 0.249)→(0.616, 0.180, 0.154) | 0.094→0.016 | 1.00 / 31.333 | 0.090 | 0.186 |
| release | release | 1.00 / step_budget | (0.613, 0.178, 0.173)→(0.607, 0.176, 0.193) | (0.616, 0.180, 0.154)→(0.605, 0.175, 0.021) | 0.016→0.148 | 1.00 / 3.333 | 0.121 | 1.359 |
| retract | retract | 0.67 / step_budget | (0.607, 0.176, 0.193)→(0.613, 0.180, 0.312) | (0.605, 0.175, 0.021)→(0.602, 0.174, 0.023) | 0.148→0.148 | 1.00 / 4.000 | 7.659 | 0.156 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.520
- phase_score: 0.712
- phase_breakdown.place_at_goal_score: 0.822
- phase_breakdown.lift_object_score: 0.904
- phase_breakdown.reach_object_score: 0.150
- grasp_place_fitness: 0.739

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.739
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.520
- **Median Q (composite search score)**: 0.070
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.448


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48016,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1252,"approach_object.approach_speed":0.09688,"descend_to_grasp.descend_depth":0.00147,"descend_to_place.place_speed":0.05142,"lift.lift_height":0.18641,"lift.lift_speed":0.10246,"retract.retract_speed":0.14869,"transport_to_goal.transport_speed":0.05069},"optimized_scores":{"best_composite_score":0.03614,"best_fitness_score":0.61614,"best_task_score":0.27858},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":187.0,"contact_point_centroid":[0.605,0.21682,-0.00796],"force_p95":1.25503,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54862,"mean_force":0.39602,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59963,0.21824,0.21769]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.53355,-0.02099,-0.00126],"force_p95":0.55518,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76236,"mean_force":0.12276,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52124,-0.02091,0.02672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":615.0,"contact_point_centroid":[0.59867,0.23819,0.19939],"force_p95":0.11745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3424,"mean_force":0.08138,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60298,0.21968,0.20089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15090.0,"contact_point_centroid":[0.52626,-0.04019,0.11385],"force_p95":0.08356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33977,"mean_force":0.06035,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52534,-0.021,0.11125]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17998.0,"contact_point_centroid":[0.52705,-0.00207,0.11209],"force_p95":0.07806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33612,"mean_force":0.05173,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52529,-0.021,0.11051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":790.0,"contact_point_centroid":[0.60895,0.20259,0.19533],"force_p95":0.10379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24715,"mean_force":0.06541,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60295,0.21966,0.20082]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6290.0,"contact_point_centroid":[0.58924,0.20013,0.24023],"force_p95":0.11036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17492,"mean_force":0.07472,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59206,0.18135,0.24097]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6655.0,"contact_point_centroid":[0.59891,0.16631,0.2353],"force_p95":0.10204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15444,"mean_force":0.07233,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59284,0.18385,0.23854]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02134,-0.00203],"force_p95":0.1342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15305,"mean_force":0.12548,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52363,-0.02094,0.02679]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51369,-0.0095,0.23052]},{"body_a":"world","body_b":"grasp_target","contact_count":2888.0,"contact_point_centroid":[0.60648,0.21742,-0.002],"force_p95":0.12343,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12512,"mean_force":0.12098,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60266,0.22186,0.30269]},{"body_a":"world","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52922,-0.02019,0.09805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16726.0,"contact_point_centroid":[0.56268,0.05242,0.24005],"force_p95":0.08957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1068,"mean_force":0.05862,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55865,0.07108,0.23952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5312.0,"contact_point_centroid":[0.52335,-0.00189,0.02758],"force_p95":0.06878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09815,"mean_force":0.04093,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52235,-0.02093,0.02534]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.52329,-0.04022,0.02805],"force_p95":0.08031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0975,"mean_force":0.05198,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52235,-0.02093,0.02535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17589.0,"contact_point_centroid":[0.55774,0.08777,0.23924],"force_p95":0.08374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0919,"mean_force":0.05607,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55792,0.06881,0.23836]}],"total_contact_groups":16},"final_pose_error":0.01796,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60648,0.21742,0.01602],"final_tcp_position":[0.6086,0.22666,0.38956],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.54862,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52995,-0.01939,0.16177],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1536.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53128,-0.02105,0.03553],"tcp_start":[0.52995,-0.01939,0.16177],"tcp_to_object_dist_end":0.01111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02123,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31677,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1342,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11269.0,"raw_peak_contact_force":0.15305,"tcp_end":[0.52232,-0.02092,0.02531],"tcp_start":[0.53128,-0.02105,0.03553],"tcp_to_object_dist_end":0.01457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.54571,-0.02174,0.18949],"object_pos_start":[0.53688,-0.02123,0.02586],"object_to_goal_dist_end":0.25834,"object_to_goal_dist_start":0.31677,"object_z_max":0.18935,"peak_contact_force":0.09197,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33182.0,"raw_peak_contact_force":0.76236,"subtask_id":"lift_object","tcp_end":[0.53273,-0.02114,0.19797],"tcp_start":[0.52232,-0.02092,0.02531],"tcp_to_object_dist_end":0.01552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59277,0.15063,0.2628],"object_pos_start":[0.54571,-0.02174,0.18949],"object_to_goal_dist_end":0.09656,"object_to_goal_dist_start":0.25834,"object_z_max":0.26273,"peak_contact_force":0.0919,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34315.0,"raw_peak_contact_force":0.1068,"subtask_id":"place_at_goal","tcp_end":[0.5829,0.14767,0.2785],"tcp_start":[0.53273,-0.02114,0.19797],"tcp_to_object_dist_end":0.01878,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.61003,0.22362,0.18383],"object_pos_start":[0.59277,0.15063,0.2628],"object_to_goal_dist_end":0.02394,"object_to_goal_dist_start":0.09656,"object_z_max":0.2628,"peak_contact_force":0.1174,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12945.0,"raw_peak_contact_force":0.17492,"subtask_id":"place_at_goal","tcp_end":[0.60468,0.22004,0.20475],"tcp_start":[0.5829,0.14767,0.2785],"tcp_to_object_dist_end":0.02189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60652,0.21772,0.01228],"object_pos_start":[0.61003,0.22362,0.18383],"object_to_goal_dist_end":0.19543,"object_to_goal_dist_start":0.02394,"object_z_max":0.18383,"peak_contact_force":0.06498,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1592.0,"raw_peak_contact_force":1.54862,"tcp_end":[0.59959,0.21823,0.22488],"tcp_start":[0.60468,0.22004,0.20475],"tcp_to_object_dist_end":0.21272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.60648,0.21742,0.01602],"object_pos_start":[0.60652,0.21772,0.01228],"object_to_goal_dist_end":0.19171,"object_to_goal_dist_start":0.19543,"object_z_max":0.01664,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2888.0,"raw_peak_contact_force":0.12512,"tcp_end":[0.6086,0.22666,0.38956],"tcp_start":[0.59959,0.21823,0.22488],"tcp_to_object_dist_end":0.37367,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57205,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14564,"approach_object.approach_speed":0.1129,"descend_to_grasp.descend_depth":0.01557,"descend_to_place.place_speed":0.06084,"lift.lift_height":0.21252,"lift.lift_speed":0.08762,"retract.retract_speed":0.02877,"transport_to_goal.transport_speed":0.09795},"optimized_scores":{"best_composite_score":0.06969,"best_fitness_score":0.64969,"best_task_score":0.36051},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":186.0,"contact_point_centroid":[0.61459,0.15914,-0.00755],"force_p95":1.25076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40319,"mean_force":0.39155,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62265,0.16114,0.1959]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.54258,-0.02858,-0.00126],"force_p95":0.43673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5152,"mean_force":0.09872,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53004,-0.02857,0.04048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16796.0,"contact_point_centroid":[0.53445,-0.04789,0.13395],"force_p95":0.08203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3221,"mean_force":0.05887,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53419,-0.02871,0.13109]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1011.0,"contact_point_centroid":[0.63337,0.14423,0.18065],"force_p95":0.08311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31261,"mean_force":0.05372,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62639,0.16223,0.18107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20207.0,"contact_point_centroid":[0.53562,-0.00975,0.13122],"force_p95":0.0774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31002,"mean_force":0.05055,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53407,-0.02871,0.12952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1051.0,"contact_point_centroid":[0.62462,0.18126,0.18256],"force_p95":0.07924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29068,"mean_force":0.05075,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62642,0.16224,0.18113]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4707.0,"contact_point_centroid":[0.6249,0.17855,0.23745],"force_p95":0.084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23338,"mean_force":0.05866,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62676,0.15959,0.23585]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4480.0,"contact_point_centroid":[0.63371,0.14164,0.23664],"force_p95":0.08472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23168,"mean_force":0.06211,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62676,0.15956,0.23637]},{"body_a":"world","body_b":"grasp_target","contact_count":3962.0,"contact_point_centroid":[0.609,0.15661,-0.002],"force_p95":0.12796,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21004,"mean_force":0.12315,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62138,0.16098,0.22823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17253.0,"contact_point_centroid":[0.58919,0.04994,0.25558],"force_p95":0.08694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19099,"mean_force":0.05712,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58491,0.06858,0.25365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17494.0,"contact_point_centroid":[0.5836,0.08433,0.25422],"force_p95":0.08004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16566,"mean_force":0.05584,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58338,0.0653,0.2525]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02927,-0.00205],"force_p95":0.13843,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16534,"mean_force":0.1267,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53238,-0.02863,0.04055]},{"body_a":"world","body_b":"grasp_target","contact_count":1712.0,"contact_point_centroid":[0.5456,-0.02923,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51763,-0.01296,0.2399]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53749,-0.02757,0.11475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5307.0,"contact_point_centroid":[0.53218,-0.00955,0.04121],"force_p95":0.07074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1122,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53112,-0.0286,0.03906]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4164.0,"contact_point_centroid":[0.5318,-0.04789,0.04187],"force_p95":0.08168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09107,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53112,-0.0286,0.03906]}],"total_contact_groups":16},"final_pose_error":0.12537,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.60881,0.15652,0.02602],"final_tcp_position":[0.62293,0.16153,0.25199],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":22.7314,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53777,-0.02642,0.18098],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5399,-0.02882,0.04955],"tcp_start":[0.53777,-0.02642,0.18098],"tcp_to_object_dist_end":0.02422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02907,0.0258],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26096,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13821,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11271.0,"raw_peak_contact_force":0.16534,"tcp_end":[0.53109,-0.0286,0.03902],"tcp_start":[0.5399,-0.02882,0.04955],"tcp_to_object_dist_end":0.01956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.55058,-0.02961,0.20392],"object_pos_start":[0.54551,-0.02907,0.0258],"object_to_goal_dist_end":0.21293,"object_to_goal_dist_start":0.26096,"object_z_max":0.20376,"peak_contact_force":0.07835,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37107.0,"raw_peak_contact_force":0.5152,"subtask_id":"lift_object","tcp_end":[0.54164,-0.02894,0.22389],"tcp_start":[0.53109,-0.0286,0.03902],"tcp_to_object_dist_end":0.0219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.63464,0.15966,0.26123],"object_pos_start":[0.55058,-0.02961,0.20392],"object_to_goal_dist_end":0.08449,"object_to_goal_dist_start":0.21293,"object_z_max":0.26118,"peak_contact_force":0.07965,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34747.0,"raw_peak_contact_force":0.19099,"subtask_id":"place_at_goal","tcp_end":[0.62689,0.15705,0.28566],"tcp_start":[0.54164,-0.02894,0.22389],"tcp_to_object_dist_end":0.02577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.63266,0.16501,0.15865],"object_pos_start":[0.63464,0.15966,0.26123],"object_to_goal_dist_end":0.01827,"object_to_goal_dist_start":0.08449,"object_z_max":0.26123,"peak_contact_force":0.08314,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9187.0,"raw_peak_contact_force":0.23338,"subtask_id":"place_at_goal","tcp_end":[0.62835,0.16274,0.18548],"tcp_start":[0.62689,0.15705,0.28566],"tcp_to_object_dist_end":0.02726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61717,0.16131,0.02559],"object_pos_start":[0.63266,0.16501,0.15865],"object_to_goal_dist_end":0.15218,"object_to_goal_dist_start":0.01827,"object_z_max":0.15865,"peak_contact_force":0.17484,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2248.0,"raw_peak_contact_force":1.40319,"tcp_end":[0.62259,0.16113,0.20495],"tcp_start":[0.62835,0.16274,0.18548],"tcp_to_object_dist_end":0.17943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60881,0.15652,0.02602],"object_pos_start":[0.61717,0.16131,0.02559],"object_to_goal_dist_end":0.15303,"object_to_goal_dist_start":0.15218,"object_z_max":0.02733,"peak_contact_force":22.7314,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3962.0,"raw_peak_contact_force":0.21004,"tcp_end":[0.62293,0.16153,0.25199],"tcp_start":[0.62259,0.16113,0.20495],"tcp_to_object_dist_end":0.22646,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03804,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1325,"approach_object.approach_speed":0.14954,"descend_to_grasp.descend_depth":0.0005,"descend_to_place.place_speed":0.09979,"lift.lift_height":0.17097,"lift.lift_speed":0.09054,"retract.retract_speed":0.09235,"transport_to_goal.transport_speed":0.14892},"optimized_scores":{"best_composite_score":0.15935,"best_fitness_score":0.73935,"best_task_score":0.51963},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":302.0,"contact_point_centroid":[0.59143,0.14675,-0.00456],"force_p95":0.72255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.12398,"mean_force":0.22912,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59804,0.14921,0.1394]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.46057,-0.00049,-0.00122],"force_p95":0.49499,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66577,"mean_force":0.10954,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44902,-0.00031,0.02891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14594.0,"contact_point_centroid":[0.45307,-0.01951,0.10794],"force_p95":0.07203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29777,"mean_force":0.0501,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45236,-0.00035,0.10565]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14809.0,"contact_point_centroid":[0.45281,0.01881,0.10578],"force_p95":0.07152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29593,"mean_force":0.04953,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45221,-0.00035,0.10368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.60637,0.13146,0.12659],"force_p95":0.07048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16945,"mean_force":0.04338,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60244,0.15037,0.12602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.59861,0.16896,0.1293],"force_p95":0.06883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16893,"mean_force":0.04256,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60247,0.15037,0.12607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5660.0,"contact_point_centroid":[0.59791,0.16692,0.1844],"force_p95":0.06949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14863,"mean_force":0.04925,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60195,0.14838,0.18136]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-0.00015,-0.00202],"force_p95":0.12961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14437,"mean_force":0.12463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4512,-0.00027,0.02849]},{"body_a":"world","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.46286,-7e-05,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48143,-6e-05,0.237]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5660.0,"contact_point_centroid":[0.60588,0.12955,0.18211],"force_p95":0.07121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13695,"mean_force":0.05027,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60195,0.14838,0.18136]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17523.0,"contact_point_centroid":[0.53474,0.05777,0.20807],"force_p95":0.07133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13473,"mean_force":0.04986,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53222,0.07676,0.20664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17476.0,"contact_point_centroid":[0.53033,0.09588,0.20912],"force_p95":0.07085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13331,"mean_force":0.0494,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53244,0.07699,0.2067]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.59127,0.14675,-0.00199],"force_p95":0.12317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13191,"mean_force":0.12259,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60039,0.15006,0.22083]},{"body_a":"world","body_b":"grasp_target","contact_count":1756.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45954,-0.00014,0.10329]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4850.0,"contact_point_centroid":[0.45101,-0.0195,0.02943],"force_p95":0.06672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08777,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45002,-0.00029,0.02737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.45071,0.01892,0.0291],"force_p95":0.06494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08379,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45002,-0.00029,0.02737]}],"total_contact_groups":16},"final_pose_error":0.02677,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59126,0.14675,0.02602],"final_tcp_position":[0.60638,0.15179,0.29571],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.12398,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1444.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46339,-0.00011,0.17245],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1756.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45828,-0.00015,0.03527],"tcp_start":[0.46339,-0.00011,0.17245],"tcp_to_object_dist_end":0.01032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46272,-0.0003,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23338,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12898,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11775.0,"raw_peak_contact_force":0.14437,"tcp_end":[0.44999,-0.00029,0.02734],"tcp_start":[0.45828,-0.00015,0.03527],"tcp_to_object_dist_end":0.01281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.47067,-0.00031,0.17626],"object_pos_start":[0.46272,-0.0003,0.02591],"object_to_goal_dist_end":0.21411,"object_to_goal_dist_start":0.23338,"object_z_max":0.17609,"peak_contact_force":0.08062,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29496.0,"raw_peak_contact_force":0.66577,"subtask_id":"lift_object","tcp_end":[0.45853,-0.00034,0.18254],"tcp_start":[0.44999,-0.00029,0.02734],"tcp_to_object_dist_end":0.01367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.60122,0.14686,0.22191],"object_pos_start":[0.47067,-0.00031,0.17626],"object_to_goal_dist_end":0.1003,"object_to_goal_dist_start":0.21411,"object_z_max":0.22188,"peak_contact_force":0.06969,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34999.0,"raw_peak_contact_force":0.13473,"subtask_id":"place_at_goal","tcp_end":[0.60134,0.14644,0.23204],"tcp_start":[0.45853,-0.00034,0.18254],"tcp_to_object_dist_end":0.01014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.60456,0.15162,0.11867],"object_pos_start":[0.60122,0.14686,0.22191],"object_to_goal_dist_end":0.00672,"object_to_goal_dist_start":0.1003,"object_z_max":0.22191,"peak_contact_force":0.07088,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11320.0,"raw_peak_contact_force":0.14863,"subtask_id":"place_at_goal","tcp_end":[0.60469,0.15092,0.13008],"tcp_start":[0.60134,0.14644,0.23204],"tcp_to_object_dist_end":0.01143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59125,0.14682,0.02645],"object_pos_start":[0.60456,0.15162,0.11867],"object_to_goal_dist_end":0.09777,"object_to_goal_dist_start":0.00672,"object_z_max":0.11867,"peak_contact_force":0.12201,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2754.0,"raw_peak_contact_force":1.12398,"tcp_end":[0.59792,0.14919,0.15056],"tcp_start":[0.60469,0.15092,0.13008],"tcp_to_object_dist_end":0.12431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59126,0.14675,0.02602],"object_pos_start":[0.59125,0.14682,0.02645],"object_to_goal_dist_end":0.0982,"object_to_goal_dist_start":0.09777,"object_z_max":0.02646,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.13191,"tcp_end":[0.60638,0.15179,0.29571],"tcp_start":[0.59792,0.14919,0.15056],"tcp_to_object_dist_end":0.27016,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```