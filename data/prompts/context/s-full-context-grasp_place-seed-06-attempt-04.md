## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.4428 | 0.21 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3100 | 0.22 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3044 | 0.23 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1602 | 0.25 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.443) — your mutation base

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

- **Composite score**: -0.443
- **task_score** (E): 0.215
- **fitness_score**: 0.487  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.930

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1265 |
| descend_to_grasp | 1.00 | 1.00 | 0.1285 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 0.00 | 0.33 | 0.1292 |
| approach_goal | 0.00 | 1.00 | 0.1000 |
| descend_to_place | 0.67 | 1.00 | 0.1066 |
| release_object | 1.00 | 1.00 | 0.0217 |
| retract_up | 0.67 | 1.00 | 0.2139 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.033, 0.183) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.033, 0.183)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 16.105 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.024, 0.046) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 45.333 | 0.169 | 0.200 |
| lift_object | lift | 0.00 / step_budget | (0.487, 0.024, 0.046)→(0.515, 0.073, 0.162) | (0.500, 0.024, 0.026)→(0.526, 0.069, 0.115) | 0.272→0.178 | 0.33 / 8.667 | 0.032 | 0.392 |
| approach_goal | approach | 0.00 / step_budget | (0.515, 0.073, 0.162)→(0.522, 0.109, 0.238) | (0.526, 0.069, 0.115)→(0.534, 0.073, 0.016) | 0.178→0.238 | 1.00 / 8.000 | 6499.350 | 1.587 |
| descend_to_place | descend | 0.67 / step_budget | (0.522, 0.109, 0.238)→(0.582, 0.176, 0.202) | (0.534, 0.073, 0.016)→(0.534, 0.073, 0.016) | 0.238→0.238 | 1.00 / 8.333 | 91000.561 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.582, 0.176, 0.202)→(0.577, 0.174, 0.223) | (0.534, 0.073, 0.016)→(0.534, 0.073, 0.016) | 0.238→0.238 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_up | retract | 0.67 / step_budget | (0.577, 0.174, 0.223)→(0.597, 0.195, 0.434) | (0.534, 0.073, 0.016)→(0.534, 0.073, 0.016) | 0.238→0.238 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.311
- phase_score: 0.420
- phase_breakdown.approach_pre_grasp_score: 0.493
- phase_breakdown.reach_goal_score: 0.050
- phase_breakdown.reach_grasp_score: 0.725
- phase_breakdown.place_at_goal_score: 0.819
- phase_breakdown.approach_lift_score: 0.134
- grasp_place_fitness: 0.619

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.619
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.311
- **Median Q (composite search score)**: -0.378
- **K-run variance**: 0.0200
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_to_grasp.descend_offset
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90909,"average_solve_count":462.0,"average_success_count":462.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.14401,"approach_above.arc_height":0.03256,"approach_above.speed":0.03684,"approach_goal.approach_goal_height":0.16454,"approach_goal.arc_height":0.08442,"approach_goal.speed":0.0545,"descend_to_grasp.descend_offset":0.02009,"descend_to_grasp.speed":0.02093,"descend_to_place.place_speed":0.02801,"grasp_close.grasp_duration":0.29303,"lift_object.lift_height":0.2631,"lift_object.speed":0.05189,"release_object.release_duration":0.12422,"retract_up.retract_height":0.1416,"retract_up.speed":0.04047},"optimized_scores":{"best_composite_score":-0.63924,"best_fitness_score":0.29076,"best_task_score":0.15538},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3846.0,"contact_point_centroid":[0.53211,0.04204,-0.00223],"force_p95":0.12511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52894,"mean_force":0.13429,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50479,0.03,0.21887]},{"body_a":"world","body_b":"grasp_target","contact_count":189.0,"contact_point_centroid":[0.50289,-0.01199,-0.00123],"force_p95":0.23025,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40513,"mean_force":0.1237,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48982,-0.01308,0.04771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12889.0,"contact_point_centroid":[0.50185,0.02836,0.09733],"force_p95":0.11485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30044,"mean_force":0.07259,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49825,0.00947,0.09649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14702.0,"contact_point_centroid":[0.50181,-0.00909,0.098],"force_p95":0.10234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.269,"mean_force":0.06607,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49835,0.00965,0.0969]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01558,-0.0021],"force_p95":0.15035,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20463,"mean_force":0.12993,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49206,-0.01459,0.04714]},{"body_a":"world","body_b":"grasp_target","contact_count":1964.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49893,0.01348,0.23552]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4342.0,"contact_point_centroid":[0.49147,0.00468,0.04771],"force_p95":0.07582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12821,"mean_force":0.04974,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49092,-0.01458,0.0459]},{"body_a":"world","body_b":"grasp_target","contact_count":1740.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49796,-0.0106,0.11487]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53213,0.04209,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53142,0.08562,0.25044]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53213,0.04209,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55424,0.13499,0.24723]},{"body_a":"world","body_b":"grasp_target","contact_count":3388.0,"contact_point_centroid":[0.53213,0.04209,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.56844,0.15976,0.36791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5442.0,"contact_point_centroid":[0.49189,-0.03371,0.04833],"force_p95":0.06731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06887,"mean_force":0.04059,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49093,-0.01458,0.04591]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3878.0,"contact_point_centroid":[0.50472,0.02943,0.22392],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01475,"mean_force":0.01045,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50447,0.02942,0.22158]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4260.0,"contact_point_centroid":[0.53177,0.08545,0.25263],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53133,0.08544,0.25046]},{"body_a":"left_finger","body_b":"right_finger","contact_count":228.0,"contact_point_centroid":[0.55693,0.13563,0.24486],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01255,"mean_force":0.00984,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55629,0.13562,0.24268]}],"total_contact_groups":15},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53213,0.04209,0.01602],"final_tcp_position":[0.58563,0.18456,0.4702],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273001.43706,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1964.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.49989,-0.00672,0.17536],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1740.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49888,-0.01465,0.0546],"tcp_start":[0.49989,-0.00672,0.17536],"tcp_to_object_dist_end":0.02902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01484,0.02564],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31197,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14863,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11584.0,"raw_peak_contact_force":0.20463,"tcp_end":[0.49089,-0.01458,0.04587],"tcp_start":[0.49888,-0.01465,0.0546],"tcp_to_object_dist_end":0.02398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52784,0.0346,0.09777],"object_pos_start":[0.50376,-0.01484,0.02564],"object_to_goal_dist_end":0.22238,"object_to_goal_dist_start":0.31197,"object_z_max":0.13538,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27780.0,"raw_peak_contact_force":0.40513,"subtask_id":"approach_lift","tcp_end":[0.51435,0.04268,0.17259],"tcp_start":[0.49089,-0.01458,0.04587],"tcp_to_object_dist_end":0.07645,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53213,0.04209,0.01602],"object_pos_start":[0.52784,0.0346,0.09777],"object_to_goal_dist_end":0.27928,"object_to_goal_dist_start":0.22238,"object_z_max":0.09777,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7724.0,"raw_peak_contact_force":1.52894,"subtask_id":"reach_goal","tcp_end":[0.50412,0.02806,0.26147],"tcp_start":[0.51435,0.04268,0.17259],"tcp_to_object_dist_end":0.24744,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53213,0.04209,0.01602],"object_pos_start":[0.53213,0.04209,0.01602],"object_to_goal_dist_end":0.27928,"object_to_goal_dist_start":0.27928,"object_z_max":0.01602,"peak_contact_force":273001.43706,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8260.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.5574,0.13571,0.24521],"tcp_start":[0.50412,0.02806,0.26147],"tcp_to_object_dist_end":0.24886,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53213,0.04209,0.01602],"object_pos_start":[0.53213,0.04209,0.01602],"object_to_goal_dist_end":0.27928,"object_to_goal_dist_start":0.27928,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55309,0.13463,0.2674],"tcp_start":[0.5574,0.13571,0.24521],"tcp_to_object_dist_end":0.2687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.53213,0.04209,0.01602],"object_pos_start":[0.53213,0.04209,0.01602],"object_to_goal_dist_end":0.27928,"object_to_goal_dist_start":0.27928,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3388.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58563,0.18456,0.4702],"tcp_start":[0.55309,0.13463,0.2674],"tcp_to_object_dist_end":0.479,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99738,"average_solve_count":382.0,"average_success_count":382.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.15357,"approach_above.arc_height":0.06011,"approach_above.speed":0.07307,"approach_goal.approach_goal_height":0.16852,"approach_goal.arc_height":0.03548,"approach_goal.speed":0.12091,"descend_to_grasp.descend_offset":0.02032,"descend_to_grasp.speed":0.02351,"descend_to_place.place_speed":0.04309,"grasp_close.grasp_duration":0.0886,"lift_object.lift_height":0.24216,"lift_object.speed":0.02485,"release_object.release_duration":0.10323,"retract_up.retract_height":0.19716,"retract_up.speed":0.02818},"optimized_scores":{"best_composite_score":-0.311,"best_fitness_score":0.619,"best_task_score":0.31094},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1902.0,"contact_point_centroid":[0.55431,0.07924,-0.0025],"force_p95":0.21395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6787,"mean_force":0.14706,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54519,0.09307,0.21458]},{"body_a":"world","body_b":"grasp_target","contact_count":214.0,"contact_point_centroid":[0.51263,0.04168,-0.00111],"force_p95":0.25579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3987,"mean_force":0.10253,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49902,0.04081,0.04749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15581.0,"contact_point_centroid":[0.51504,0.07641,0.08826],"force_p95":0.10469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25366,"mean_force":0.06421,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51287,0.05739,0.08734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4728.0,"contact_point_centroid":[0.53742,0.09825,0.159],"force_p95":0.14426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24918,"mean_force":0.08591,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53152,0.07953,0.15906]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5462.0,"contact_point_centroid":[0.53771,0.06146,0.16082],"force_p95":0.10495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24336,"mean_force":0.07501,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53175,0.0798,0.16103]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03976,-0.00202],"force_p95":0.22437,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22757,"mean_force":0.16355,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50067,0.03965,0.047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17948.0,"contact_point_centroid":[0.5151,0.03868,0.08872],"force_p95":0.09078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22208,"mean_force":0.0565,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51298,0.05752,0.08765]},{"body_a":"world","body_b":"grasp_target","contact_count":2608.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50124,0.05143,0.25838]},{"body_a":"world","body_b":"grasp_target","contact_count":1812.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50647,0.04443,0.11925]},{"body_a":"world","body_b":"grasp_target","contact_count":3028.0,"contact_point_centroid":[0.55434,0.07926,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58802,0.13686,0.18234]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55434,0.07926,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61527,0.16669,0.14075]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55434,0.07926,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.61726,0.16805,0.27132]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4868.0,"contact_point_centroid":[0.5001,0.05884,0.04908],"force_p95":0.07611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11565,"mean_force":0.05431,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49951,0.03956,0.04572]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5339.0,"contact_point_centroid":[0.50061,0.02039,0.04821],"force_p95":0.07328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10273,"mean_force":0.04902,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49951,0.03956,0.04572]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1792.0,"contact_point_centroid":[0.54645,0.09403,0.21954],"force_p95":0.01166,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01619,"mean_force":0.01057,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54616,0.09401,0.21728]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3197.0,"contact_point_centroid":[0.5882,0.13676,0.18477],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58789,0.13674,0.18251]}],"total_contact_groups":17},"final_pose_error":0.0579,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55434,0.07926,0.01602],"final_tcp_position":[0.62445,0.17096,0.38439],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.86485,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2608.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50823,0.04871,0.18392],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":48.07089,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1812.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50752,0.04025,0.05474],"tcp_start":[0.50823,0.04871,0.18392],"tcp_to_object_dist_end":0.02915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03977,0.02589],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21232,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.2241,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12007.0,"raw_peak_contact_force":0.22757,"tcp_end":[0.49948,0.03955,0.04569],"tcp_start":[0.50752,0.04025,0.05474],"tcp_to_object_dist_end":0.02365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54116,0.07744,0.11115],"object_pos_start":[0.51242,0.03977,0.02589],"object_to_goal_dist_end":0.13287,"object_to_goal_dist_start":0.21232,"object_z_max":0.11105,"peak_contact_force":0.09732,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33743.0,"raw_peak_contact_force":0.3987,"subtask_id":"approach_lift","tcp_end":[0.53274,0.07783,0.13927],"tcp_start":[0.49948,0.03955,0.04569],"tcp_to_object_dist_end":0.02936,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55434,0.07926,0.01602],"object_pos_start":[0.54116,0.07744,0.11115],"object_to_goal_dist_end":0.17522,"object_to_goal_dist_start":0.13287,"object_z_max":0.15099,"peak_contact_force":9748.86485,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13884.0,"raw_peak_contact_force":1.6787,"subtask_id":"reach_goal","tcp_end":[0.55426,0.1019,0.23563],"tcp_start":[0.53274,0.07783,0.13927],"tcp_to_object_dist_end":0.22077,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.55434,0.07926,0.01602],"object_pos_start":[0.55434,0.07926,0.01602],"object_to_goal_dist_end":0.17522,"object_to_goal_dist_start":0.17522,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6225.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.6199,0.168,0.14052],"tcp_start":[0.55426,0.1019,0.23563],"tcp_to_object_dist_end":0.16635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55434,0.07926,0.01602],"object_pos_start":[0.55434,0.07926,0.01602],"object_to_goal_dist_end":0.17522,"object_to_goal_dist_start":0.17522,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61348,0.16612,0.16017],"tcp_start":[0.6199,0.168,0.14052],"tcp_to_object_dist_end":0.17839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55434,0.07926,0.01602],"object_pos_start":[0.55434,0.07926,0.01602],"object_to_goal_dist_end":0.17522,"object_to_goal_dist_start":0.17522,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62445,0.17096,0.38439],"tcp_start":[0.61348,0.16612,0.16017],"tcp_to_object_dist_end":0.38603,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25926,"average_solve_count":324.0,"average_success_count":324.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.15522,"approach_above.arc_height":0.05343,"approach_above.speed":0.08555,"approach_goal.approach_goal_height":0.27589,"approach_goal.arc_height":0.10026,"approach_goal.speed":0.03634,"descend_to_grasp.descend_offset":0.02,"descend_to_grasp.speed":0.03528,"descend_to_place.place_speed":0.04893,"grasp_close.grasp_duration":0.1339,"lift_object.lift_height":0.28396,"lift_object.speed":0.07574,"release_object.release_duration":0.12104,"retract_up.retract_height":0.13598,"retract_up.speed":0.04195},"optimized_scores":{"best_composite_score":-0.37827,"best_fitness_score":0.55173,"best_task_score":0.17757},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3724.0,"contact_point_centroid":[0.5164,0.09867,-0.00225],"force_p95":0.12558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55369,"mean_force":0.13484,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50111,0.15935,0.19261]},{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.48224,0.04957,-0.00115],"force_p95":0.22972,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37156,"mean_force":0.10375,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46959,0.04934,0.04834]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13655.0,"contact_point_centroid":[0.4837,0.08905,0.1004],"force_p95":0.11162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27503,"mean_force":0.07123,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48029,0.07013,0.09976]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15117.0,"contact_point_centroid":[0.48362,0.05167,0.10124],"force_p95":0.09866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25393,"mean_force":0.06497,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48045,0.07042,0.10047]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04867,-0.00204],"force_p95":0.13397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16896,"mean_force":0.12574,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47159,0.04844,0.04779]},{"body_a":"world","body_b":"grasp_target","contact_count":2272.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49235,0.04997,0.26214]},{"body_a":"world","body_b":"grasp_target","contact_count":1880.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4781,0.05323,0.12179]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51642,0.09871,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5413,0.21187,0.21654]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51642,0.09871,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56443,0.22144,0.22174]},{"body_a":"world","body_b":"grasp_target","contact_count":3440.0,"contact_point_centroid":[0.51642,0.09871,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.57103,0.22401,0.34291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4849.0,"contact_point_centroid":[0.46973,0.02909,0.04888],"force_p95":0.06811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08951,"mean_force":0.04492,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47049,0.04833,0.04665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5371.0,"contact_point_centroid":[0.47004,0.06755,0.0485],"force_p95":0.06522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08264,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47049,0.04833,0.04665]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3719.0,"contact_point_centroid":[0.50186,0.16253,0.19623],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01614,"mean_force":0.01052,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50145,0.16251,0.19399]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4331.0,"contact_point_centroid":[0.54185,0.21187,0.2188],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01031,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54122,0.21184,0.21653]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.567,0.22247,0.21983],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01021,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56661,0.22244,0.21776]}],"total_contact_groups":15},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51642,0.09871,0.01602],"final_tcp_position":[0.58109,0.22816,0.44652],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9749.06268,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2272.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.48073,0.05754,0.18947],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1880.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47817,0.04912,0.05471],"tcp_start":[0.48073,0.05754,0.18947],"tcp_to_object_dist_end":0.02905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.0484,0.02585],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29033,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13313,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12020.0,"raw_peak_contact_force":0.16896,"tcp_end":[0.47046,0.04833,0.04662],"tcp_start":[0.47817,0.04912,0.05471],"tcp_to_object_dist_end":0.02407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50879,0.09502,0.13545],"object_pos_start":[0.48262,0.0484,0.02585],"object_to_goal_dist_end":0.17968,"object_to_goal_dist_start":0.29033,"object_z_max":0.14059,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28946.0,"raw_peak_contact_force":0.37156,"subtask_id":"approach_lift","tcp_end":[0.4984,0.09907,0.17421],"tcp_start":[0.47046,0.04833,0.04662],"tcp_to_object_dist_end":0.04034,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51642,0.09871,0.01602],"object_pos_start":[0.50879,0.09502,0.13545],"object_to_goal_dist_end":0.25926,"object_to_goal_dist_start":0.17968,"object_z_max":0.13545,"peak_contact_force":9749.06268,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7443.0,"raw_peak_contact_force":1.55369,"subtask_id":"reach_goal","tcp_end":[0.50745,0.19757,0.21653],"tcp_start":[0.4984,0.09907,0.17421],"tcp_to_object_dist_end":0.22374,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51642,0.09871,0.01602],"object_pos_start":[0.51642,0.09871,0.01602],"object_to_goal_dist_end":0.25926,"object_to_goal_dist_start":0.25926,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8331.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.56771,0.22289,0.22049],"tcp_start":[0.50745,0.19757,0.21653],"tcp_to_object_dist_end":0.24466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51642,0.09871,0.01602],"object_pos_start":[0.51642,0.09871,0.01602],"object_to_goal_dist_end":0.25926,"object_to_goal_dist_start":0.25926,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56321,0.22085,0.24154],"tcp_start":[0.56771,0.22289,0.22049],"tcp_to_object_dist_end":0.2607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.51642,0.09871,0.01602],"object_pos_start":[0.51642,0.09871,0.01602],"object_to_goal_dist_end":0.25926,"object_to_goal_dist_start":0.25926,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3440.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58109,0.22816,0.44652],"tcp_start":[0.56321,0.22085,0.24154],"tcp_to_object_dist_end":0.45418,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```