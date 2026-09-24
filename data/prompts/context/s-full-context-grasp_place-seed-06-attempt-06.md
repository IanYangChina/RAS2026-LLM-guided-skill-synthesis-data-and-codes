## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1606 | 0.25 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1606 | 0.25 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.4428 | 0.21 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3100 | 0.22 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3044 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=-0.161) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.2
- id: approach_lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: reach_goal
  weight: 0.2
phases:
- id: approach_above
  type: approach
  generator: arc_cartesian
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
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_pre_grasp
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
    - 0.04
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: grasp_close
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: lift_object
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
      - 0.12
      - 0.28
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_lift
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
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
  subtask_id: reach_goal
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
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_up
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
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.04], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_close** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_up** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.161
- **task_score** (E): 0.254
- **fitness_score**: 0.589  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1290 |
| descend_to_grasp | 1.00 | 1.00 | 0.1247 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 0.00 | 1.00 | 0.1018 |
| transport_to_goal | 0.00 | 0.33 | 0.0972 |
| release_object | 1.00 | 1.00 | 0.0240 |
| retract_up | 0.67 | 1.00 | 0.2432 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.033, 0.180) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.033, 0.180)→(0.495, 0.025, 0.056) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.056)→(0.487, 0.024, 0.047) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.000 | 0.137 | 0.168 |
| lift_object | lift | 0.00 / step_budget | (0.487, 0.024, 0.047)→(0.490, 0.024, 0.149) | (0.500, 0.024, 0.026)→(0.497, 0.024, 0.120) | 0.272→0.223 | 1.00 / 26.667 | 0.108 | 0.399 |
| transport_to_goal | approach | 0.00 / step_budget | (0.490, 0.024, 0.149)→(0.539, 0.103, 0.167) | (0.497, 0.024, 0.120)→(0.543, 0.111, 0.088) | 0.223→0.162 | 0.33 / 6.000 | 0.038 | 0.235 |
| release_object | release | 1.00 / step_budget | (0.539, 0.103, 0.167)→(0.533, 0.102, 0.190) | (0.543, 0.111, 0.088)→(0.540, 0.117, 0.019) | 0.162→0.214 | 1.00 / 3.333 | 0.143 | 1.362 |
| retract_up | retract | 0.67 / step_budget | (0.533, 0.102, 0.190)→(0.592, 0.186, 0.410) | (0.540, 0.117, 0.019)→(0.536, 0.118, 0.019) | 0.214→0.215 | 1.00 / 4.000 | 0.123 | 0.162 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.384
- phase_score: 0.474
- phase_breakdown.approach_pre_grasp_score: 0.771
- phase_breakdown.reach_goal_score: 0.199
- phase_breakdown.reach_grasp_score: 0.738
- phase_breakdown.approach_lift_score: 0.184
- grasp_place_fitness: 0.654

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.654
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.384
- **Median Q (composite search score)**: -0.184
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.383


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95616,"average_solve_count":365.0,"average_success_count":365.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.15763,"approach_above.arc_height":0.03867,"approach_above.speed":0.06184,"descend_to_grasp.descend_offset":0.02032,"descend_to_grasp.speed":0.01447,"grasp_close.grasp_duration":0.19572,"lift_object.lift_height":0.20989,"lift_object.speed":0.06273,"release_object.release_duration":0.19643,"retract_up.retract_height":0.10777,"retract_up.speed":0.04676,"transport_to_goal.transport_speed":0.04067},"optimized_scores":{"best_composite_score":-0.20239,"best_fitness_score":0.54761,"best_task_score":0.16984},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.51409,0.06324,-0.00716],"force_p95":1.20851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53462,"mean_force":0.3765,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52106,0.06272,0.1955]},{"body_a":"world","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.50122,-0.01391,-0.00119],"force_p95":0.23298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4176,"mean_force":0.06364,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48948,-0.01461,0.048]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16283.0,"contact_point_centroid":[0.49215,0.0044,0.09358],"force_p95":0.10089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2734,"mean_force":0.06214,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49028,-0.01463,0.09304]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18144.0,"contact_point_centroid":[0.49212,-0.03352,0.09408],"force_p95":0.08974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26678,"mean_force":0.05632,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49031,-0.01463,0.09324]},{"body_a":"world","body_b":"grasp_target","contact_count":3942.0,"contact_point_centroid":[0.50818,0.06435,-0.00201],"force_p95":0.12939,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24036,"mean_force":0.12375,"phase_index":6.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.55151,0.1233,0.32104]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01558,-0.00209],"force_p95":0.14842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20121,"mean_force":0.12933,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49211,-0.01465,0.04752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9693.0,"contact_point_centroid":[0.51361,0.0429,0.1605],"force_p95":0.13037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16884,"mean_force":0.0928,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50857,0.02444,0.16269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10652.0,"contact_point_centroid":[0.51361,0.00661,0.16092],"force_p95":0.11948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16734,"mean_force":0.08459,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50878,0.02491,0.1629]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49911,0.0165,0.24034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":548.0,"contact_point_centroid":[0.53007,0.08169,0.17309],"force_p95":0.12441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12977,"mean_force":0.08873,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52465,0.06324,0.17841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4340.0,"contact_point_centroid":[0.49149,0.00463,0.04799],"force_p95":0.07553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12805,"mean_force":0.04973,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49097,-0.01463,0.04629]},{"body_a":"world","body_b":"grasp_target","contact_count":1864.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49808,-0.01062,0.12053]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":597.0,"contact_point_centroid":[0.52963,0.04496,0.17335],"force_p95":0.11354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12047,"mean_force":0.08065,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52469,0.06324,0.17845]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5431.0,"contact_point_centroid":[0.49222,-0.03376,0.0486],"force_p95":0.067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07097,"mean_force":0.04066,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49098,-0.01463,0.04629]}],"total_contact_groups":14},"final_pose_error":0.02333,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50788,0.06436,0.02602],"final_tcp_position":[0.58309,0.1802,0.43405],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.53462,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50003,-0.00668,0.18633],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49893,-0.01471,0.05499],"tcp_start":[0.50003,-0.00668,0.18633],"tcp_to_object_dist_end":0.0294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01486,0.02567],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31197,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14701,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11571.0,"raw_peak_contact_force":0.20121,"tcp_end":[0.49095,-0.01463,0.04626],"tcp_start":[0.49893,-0.01471,0.05499],"tcp_to_object_dist_end":0.02424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50226,-0.01504,0.12006],"object_pos_start":[0.50375,-0.01486,0.02567],"object_to_goal_dist_end":0.25409,"object_to_goal_dist_start":0.31197,"object_z_max":0.11994,"peak_contact_force":0.10362,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34606.0,"raw_peak_contact_force":0.4176,"subtask_id":"approach_lift","tcp_end":[0.49416,-0.01469,0.14875],"tcp_start":[0.49095,-0.01463,0.04626],"tcp_to_object_dist_end":0.02981,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53136,0.06282,0.14347],"object_pos_start":[0.50226,-0.01504,0.12006],"object_to_goal_dist_end":0.17195,"object_to_goal_dist_start":0.25409,"object_z_max":0.14346,"peak_contact_force":0.11405,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20345.0,"raw_peak_contact_force":0.16884,"subtask_id":"reach_goal","tcp_end":[0.52637,0.06334,0.1811],"tcp_start":[0.49416,-0.01469,0.14875],"tcp_to_object_dist_end":0.03796,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51905,0.06176,0.02589],"object_pos_start":[0.53136,0.06282,0.14347],"object_to_goal_dist_end":0.26417,"object_to_goal_dist_start":0.17195,"object_z_max":0.14347,"peak_contact_force":0.18339,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1330.0,"raw_peak_contact_force":1.53462,"tcp_end":[0.52098,0.06272,0.20503],"tcp_start":[0.52637,0.06334,0.1811],"tcp_to_object_dist_end":0.17915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50788,0.06436,0.02602],"object_pos_start":[0.51905,0.06176,0.02589],"object_to_goal_dist_end":0.26594,"object_to_goal_dist_start":0.26417,"object_z_max":0.02809,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3942.0,"raw_peak_contact_force":0.24036,"tcp_end":[0.58309,0.1802,0.43405],"tcp_start":[0.52098,0.06272,0.20503],"tcp_to_object_dist_end":0.43077,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94099,"average_solve_count":322.0,"average_success_count":322.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.12829,"approach_above.arc_height":0.06504,"approach_above.speed":0.04351,"descend_to_grasp.descend_offset":0.02138,"descend_to_grasp.speed":0.02131,"grasp_close.grasp_duration":0.22256,"lift_object.lift_height":0.20715,"lift_object.speed":0.06078,"release_object.release_duration":0.11183,"retract_up.retract_height":0.12173,"retract_up.speed":0.05758,"transport_to_goal.transport_speed":0.07892},"optimized_scores":{"best_composite_score":-0.09565,"best_fitness_score":0.65435,"best_task_score":0.38408},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":658.0,"contact_point_centroid":[0.57581,0.13685,-0.00318],"force_p95":0.5674,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14984,"mean_force":0.17117,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56546,0.11453,0.14103]},{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.50932,0.03956,-0.00113],"force_p95":0.2332,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39369,"mean_force":0.06564,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49793,0.0396,0.04828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8978.0,"contact_point_centroid":[0.53695,0.05749,0.13695],"force_p95":0.13513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29823,"mean_force":0.09832,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53351,0.07582,0.13981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18474.0,"contact_point_centroid":[0.50027,0.05846,0.09573],"force_p95":0.08222,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28547,"mean_force":0.05515,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49889,0.0394,0.09463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18531.0,"contact_point_centroid":[0.49957,0.02035,0.0954],"force_p95":0.08306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25726,"mean_force":0.05487,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4989,0.0394,0.09471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9744.0,"contact_point_centroid":[0.53907,0.09563,0.13693],"force_p95":0.12381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.196,"mean_force":0.08975,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53505,0.07746,0.13975]},{"body_a":"world","body_b":"grasp_target","contact_count":3152.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5015,0.05554,0.24503]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03972,-0.00202],"force_p95":0.12813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1313,"mean_force":0.12453,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50055,0.03983,0.04797]},{"body_a":"world","body_b":"grasp_target","contact_count":3456.0,"contact_point_centroid":[0.57583,0.13671,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.59306,0.14229,0.25463]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50637,0.04446,0.10712]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4622.0,"contact_point_centroid":[0.49951,0.02059,0.04811],"force_p95":0.06995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08802,"mean_force":0.04687,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4994,0.03974,0.04669]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4620.0,"contact_point_centroid":[0.50015,0.05891,0.04849],"force_p95":0.07003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08785,"mean_force":0.04685,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49939,0.03974,0.04669]}],"total_contact_groups":12},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57583,0.13671,0.01602],"final_tcp_position":[0.62291,0.16901,0.34768],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3152.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50812,0.04856,0.15843],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50742,0.04044,0.05571],"tcp_start":[0.50812,0.04856,0.15843],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03973,0.0259],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21233,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12818,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11042.0,"raw_peak_contact_force":0.1313,"tcp_end":[0.49937,0.03974,0.04665],"tcp_start":[0.50742,0.04044,0.05571],"tcp_to_object_dist_end":0.02451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50841,0.0396,0.11768],"object_pos_start":[0.51242,0.03973,0.0259],"object_to_goal_dist_end":0.18059,"object_to_goal_dist_start":0.21233,"object_z_max":0.11757,"peak_contact_force":0.08774,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37180.0,"raw_peak_contact_force":0.39369,"subtask_id":"approach_lift","tcp_end":[0.50262,0.03941,0.14593],"tcp_start":[0.49937,0.03974,0.04665],"tcp_to_object_dist_end":0.02884,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57427,0.12478,0.08215],"object_pos_start":[0.50841,0.0396,0.11768],"object_to_goal_dist_end":0.09525,"object_to_goal_dist_start":0.18059,"object_z_max":0.11771,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18722.0,"raw_peak_contact_force":0.29823,"subtask_id":"reach_goal","tcp_end":[0.57068,0.11562,0.13814],"tcp_start":[0.50262,0.03941,0.14593],"tcp_to_object_dist_end":0.05684,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57583,0.13671,0.01601],"object_pos_start":[0.57427,0.12478,0.08215],"object_to_goal_dist_end":0.14354,"object_to_goal_dist_start":0.09525,"object_z_max":0.08215,"peak_contact_force":0.12264,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":658.0,"raw_peak_contact_force":1.14984,"tcp_end":[0.56444,0.1143,0.1604],"tcp_start":[0.57068,0.11562,0.13814],"tcp_to_object_dist_end":0.14656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.57583,0.13671,0.01602],"object_pos_start":[0.57583,0.13671,0.01601],"object_to_goal_dist_end":0.14353,"object_to_goal_dist_start":0.14354,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3456.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.62291,0.16901,0.34768],"tcp_start":[0.56444,0.1143,0.1604],"tcp_to_object_dist_end":0.33654,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9027,"average_solve_count":370.0,"average_success_count":370.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.15952,"approach_above.arc_height":0.08177,"approach_above.speed":0.03353,"descend_to_grasp.descend_offset":0.02104,"descend_to_grasp.speed":0.01462,"grasp_close.grasp_duration":0.2627,"lift_object.lift_height":0.187,"lift_object.speed":0.06276,"release_object.release_duration":0.08745,"retract_up.retract_height":0.18253,"retract_up.speed":0.04073,"transport_to_goal.transport_speed":0.06664},"optimized_scores":{"best_composite_score":-0.18373,"best_fitness_score":0.56627,"best_task_score":0.20945},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":773.0,"contact_point_centroid":[0.5247,0.15295,-0.00325],"force_p95":0.6133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40248,"mean_force":0.17311,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5163,0.12933,0.18464]},{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.48037,0.04785,-0.00114],"force_p95":0.23597,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38655,"mean_force":0.06114,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46921,0.04809,0.04941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17685.0,"contact_point_centroid":[0.47194,0.06684,0.09622],"force_p95":0.08703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27833,"mean_force":0.05732,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47035,0.04789,0.09559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17109.0,"contact_point_centroid":[0.47125,0.02888,0.09581],"force_p95":0.1093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2557,"mean_force":0.05992,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47033,0.04789,0.09564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8213.0,"contact_point_centroid":[0.50048,0.07127,0.16067],"force_p95":0.12827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23787,"mean_force":0.10001,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49599,0.08952,0.16434]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04867,-0.00204],"force_p95":0.13525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17244,"mean_force":0.12605,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47163,0.04836,0.04893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8718.0,"contact_point_centroid":[0.49997,0.10702,0.16065],"force_p95":0.12541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17139,"mean_force":0.0949,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49561,0.08882,0.16409]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49227,0.04561,0.26318]},{"body_a":"world","body_b":"grasp_target","contact_count":1992.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47822,0.05281,0.12516]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52464,0.15325,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.54117,0.16993,0.32664]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4843.0,"contact_point_centroid":[0.46972,0.02901,0.04962],"force_p95":0.06808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09822,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47054,0.04825,0.04779]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5381.0,"contact_point_centroid":[0.47004,0.06747,0.04929],"force_p95":0.06539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08055,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47054,0.04825,0.04779]}],"total_contact_groups":12},"final_pose_error":0.06944,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52464,0.15325,0.01602],"final_tcp_position":[0.56901,0.20973,0.44751],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.40248,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.48098,0.05678,0.19501],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1992.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.4782,0.04904,0.05585],"tcp_start":[0.48098,0.05678,0.19501],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04835,0.02583],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29037,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1344,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12024.0,"raw_peak_contact_force":0.17244,"tcp_end":[0.47051,0.04825,0.04776],"tcp_start":[0.4782,0.04904,0.05585],"tcp_to_object_dist_end":0.02505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48161,0.04854,0.12105],"object_pos_start":[0.48262,0.04835,0.02583],"object_to_goal_dist_end":0.23355,"object_to_goal_dist_start":0.29037,"object_z_max":0.12093,"peak_contact_force":0.13216,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34957.0,"raw_peak_contact_force":0.38655,"subtask_id":"approach_lift","tcp_end":[0.47449,0.04793,0.15112],"tcp_start":[0.47051,0.04825,0.04776],"tcp_to_object_dist_end":0.0309,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52289,0.14664,0.03716],"object_pos_start":[0.48161,0.04854,0.12105],"object_to_goal_dist_end":0.2182,"object_to_goal_dist_start":0.23355,"object_z_max":0.13994,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16931.0,"raw_peak_contact_force":0.23787,"subtask_id":"reach_goal","tcp_end":[0.52019,0.13021,0.18134],"tcp_start":[0.47449,0.04793,0.15112],"tcp_to_object_dist_end":0.14514,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52464,0.15325,0.01602],"object_pos_start":[0.52289,0.14664,0.03716],"object_to_goal_dist_end":0.23449,"object_to_goal_dist_start":0.2182,"object_z_max":0.03716,"peak_contact_force":0.12261,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":773.0,"raw_peak_contact_force":1.40248,"tcp_end":[0.51496,0.12897,0.20519],"tcp_start":[0.52019,0.13021,0.18134],"tcp_to_object_dist_end":0.19097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52464,0.15325,0.01602],"object_pos_start":[0.52464,0.15325,0.01602],"object_to_goal_dist_end":0.23449,"object_to_goal_dist_start":0.23449,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56901,0.20973,0.44751],"tcp_start":[0.51496,0.12897,0.20519],"tcp_to_object_dist_end":0.43743,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```