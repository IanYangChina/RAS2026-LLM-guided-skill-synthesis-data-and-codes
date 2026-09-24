## Search State

- **Seed**: 6
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1602 | 0.25 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

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

## Current Skill (Q=-0.160) — your mutation base

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

- **Composite score**: -0.160
- **task_score** (E): 0.254
- **fitness_score**: 0.590  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1650 |
| descend_to_grasp | 1.00 | 1.00 | 0.0873 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 0.33 | 1.00 | 0.0984 |
| transport_to_goal | 0.00 | 0.67 | 0.1068 |
| release_object | 1.00 | 1.00 | 0.0239 |
| retract_up | 1.00 | 1.00 | 0.2303 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.033, 0.142) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.033, 0.142)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 8.495 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.025, 0.046) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 | 1.00 / 44.333 | 0.138 | 0.172 |
| lift_object | lift | 0.33 / step_budget | (0.487, 0.025, 0.046)→(0.490, 0.025, 0.145) | (0.500, 0.025, 0.026)→(0.495, 0.024, 0.117) | 0.271→0.226 | 1.00 / 33.667 | 0.088 | 0.403 |
| transport_to_goal | approach | 0.00 / step_budget | (0.490, 0.025, 0.145)→(0.543, 0.109, 0.166) | (0.495, 0.024, 0.117)→(0.546, 0.108, 0.127) | 0.226→0.131 | 0.67 / 11.000 | 3253.483 | 0.219 |
| release_object | release | 1.00 / step_budget | (0.543, 0.109, 0.166)→(0.537, 0.108, 0.189) | (0.546, 0.108, 0.127)→(0.546, 0.122, 0.015) | 0.131→0.214 | 1.00 / 4.000 | 0.114 | 1.452 |
| retract_up | retract | 1.00 / step_budget | (0.537, 0.108, 0.189)→(0.595, 0.192, 0.395) | (0.546, 0.122, 0.015)→(0.545, 0.122, 0.016) | 0.214→0.213 | 1.00 / 4.000 | 0.123 | 0.126 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.378
- phase_score: 0.415
- phase_breakdown.approach_pre_grasp_score: 0.516
- phase_breakdown.reach_goal_score: 0.232
- phase_breakdown.reach_grasp_score: 0.725
- phase_breakdown.approach_lift_score: 0.231
- grasp_place_fitness: 0.652

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.652
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.378
- **Median Q (composite search score)**: -0.186
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92239,"average_solve_count":335.0,"average_success_count":335.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.1264,"approach_above.arc_height":0.02568,"approach_above.speed":0.05823,"descend_to_grasp.descend_offset":0.0209,"descend_to_grasp.speed":0.02257,"grasp_close.grasp_duration":0.23778,"lift_object.lift_height":0.16047,"lift_object.speed":0.05642,"release_object.release_duration":0.15662,"retract_up.retract_height":0.10475,"retract_up.speed":0.05071,"transport_to_goal.transport_speed":0.07716},"optimized_scores":{"best_composite_score":-0.19638,"best_fitness_score":0.55362,"best_task_score":0.18333},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":470.0,"contact_point_centroid":[0.53132,0.09886,-0.00401],"force_p95":0.78438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47291,"mean_force":0.20717,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52722,0.0735,0.1884]},{"body_a":"world","body_b":"grasp_target","contact_count":199.0,"contact_point_centroid":[0.50065,-0.01384,-0.0012],"force_p95":0.23306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39349,"mean_force":0.06608,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48936,-0.01456,0.04855]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":26.0,"contact_point_centroid":[0.53186,0.05621,0.17517],"force_p95":0.31667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37517,"mean_force":0.17842,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53231,0.07427,0.18081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18128.0,"contact_point_centroid":[0.49194,0.0045,0.0937],"force_p95":0.08061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26597,"mean_force":0.05589,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49142,-0.01463,0.09288]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19733.0,"contact_point_centroid":[0.49194,-0.03367,0.09284],"force_p95":0.07606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26548,"mean_force":0.05161,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49133,-0.01462,0.09191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12695.0,"contact_point_centroid":[0.51181,0.0085,0.15469],"force_p95":0.13152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22234,"mean_force":0.07521,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51113,0.02714,0.15634]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01559,-0.00209],"force_p95":0.14893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20228,"mean_force":0.12959,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49201,-0.01459,0.04805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.53329,0.09048,0.17538],"force_p95":0.12816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19419,"mean_force":0.04249,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53202,0.0743,0.18034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4341.0,"contact_point_centroid":[0.49142,0.00462,0.04833],"force_p95":0.07479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14301,"mean_force":0.04949,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49087,-0.01457,0.04681]},{"body_a":"world","body_b":"grasp_target","contact_count":1952.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49889,0.00955,0.22892]},{"body_a":"world","body_b":"grasp_target","contact_count":3964.0,"contact_point_centroid":[0.5312,0.09924,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12457,"mean_force":0.12265,"phase_index":6.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.55458,0.12874,0.31929]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49788,-0.01113,0.10812]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12994.0,"contact_point_centroid":[0.51173,0.04662,0.15463],"force_p95":0.10412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12209,"mean_force":0.07102,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51158,0.02812,0.15687]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4950.0,"contact_point_centroid":[0.49136,-0.03373,0.04824],"force_p95":0.0711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07286,"mean_force":0.04439,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49087,-0.01457,0.04682]}],"total_contact_groups":14},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5312,0.09924,0.01602],"final_tcp_position":[0.5841,0.18209,0.43393],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.49979,-0.00778,0.16077],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49882,-0.01465,0.0555],"tcp_start":[0.49979,-0.00778,0.16077],"tcp_to_object_dist_end":0.02992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.0149,0.02566],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.312,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1466,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11091.0,"raw_peak_contact_force":0.20228,"tcp_end":[0.49084,-0.01457,0.04678],"tcp_start":[0.49882,-0.01465,0.0555],"tcp_to_object_dist_end":0.02476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49925,-0.01515,0.11075],"object_pos_start":[0.50376,-0.0149,0.02566],"object_to_goal_dist_end":0.26,"object_to_goal_dist_start":0.312,"object_z_max":0.11066,"peak_contact_force":0.0855,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38060.0,"raw_peak_contact_force":0.39349,"subtask_id":"approach_lift","tcp_end":[0.49583,-0.01473,0.13906],"tcp_start":[0.49084,-0.01457,0.04678],"tcp_to_object_dist_end":0.02852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53377,0.07531,0.14355],"object_pos_start":[0.49925,-0.01515,0.11075],"object_to_goal_dist_end":0.16228,"object_to_goal_dist_start":0.26,"object_z_max":0.14422,"peak_contact_force":9760.30694,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25689.0,"raw_peak_contact_force":0.22234,"subtask_id":"reach_goal","tcp_end":[0.53234,0.07416,0.18093],"tcp_start":[0.49583,-0.01473,0.13906],"tcp_to_object_dist_end":0.03742,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53126,0.09925,0.01606],"object_pos_start":[0.53377,0.07531,0.14355],"object_to_goal_dist_end":0.25441,"object_to_goal_dist_start":0.16228,"object_z_max":0.14355,"peak_contact_force":0.12468,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":684.0,"raw_peak_contact_force":1.47291,"tcp_end":[0.52697,0.07347,0.20467],"tcp_start":[0.53234,0.07416,0.18093],"tcp_to_object_dist_end":0.19041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.5312,0.09924,0.01602],"object_pos_start":[0.53126,0.09925,0.01606],"object_to_goal_dist_end":0.25447,"object_to_goal_dist_start":0.25441,"object_z_max":0.01606,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3964.0,"raw_peak_contact_force":0.12457,"tcp_end":[0.5841,0.18209,0.43393],"tcp_start":[0.52697,0.07347,0.20467],"tcp_to_object_dist_end":0.42931,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67788,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.08811,"approach_above.arc_height":0.07492,"approach_above.speed":0.07593,"descend_to_grasp.descend_offset":0.02068,"descend_to_grasp.speed":0.0445,"grasp_close.grasp_duration":0.14291,"lift_object.lift_height":0.24403,"lift_object.speed":0.0684,"release_object.release_duration":0.09857,"retract_up.retract_height":0.12267,"retract_up.speed":0.07585,"transport_to_goal.transport_speed":0.09297},"optimized_scores":{"best_composite_score":-0.09795,"best_fitness_score":0.65205,"best_task_score":0.37831},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":599.0,"contact_point_centroid":[0.59923,0.11024,-0.00319],"force_p95":0.59989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23445,"mean_force":0.18204,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57028,0.12007,0.14571]},{"body_a":"world","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.50979,0.04065,-0.00118],"force_p95":0.23893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41506,"mean_force":0.06485,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4976,0.04014,0.04739]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15684.0,"contact_point_centroid":[0.50068,0.05892,0.09667],"force_p95":0.10169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29419,"mean_force":0.06464,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49824,0.03992,0.09581]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10485.0,"contact_point_centroid":[0.54443,0.0639,0.14557],"force_p95":0.1157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28518,"mean_force":0.08511,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53877,0.0821,0.14733]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17766.0,"contact_point_centroid":[0.50034,0.02108,0.09652],"force_p95":0.09269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26759,"mean_force":0.05732,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49822,0.03992,0.0955]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9161.0,"contact_point_centroid":[0.54322,0.09901,0.14593],"force_p95":0.13618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23732,"mean_force":0.09714,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53735,0.08056,0.14755]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51252,0.03977,-0.00206],"force_p95":0.13991,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18429,"mean_force":0.12728,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.5003,0.04038,0.04717]},{"body_a":"world","body_b":"grasp_target","contact_count":3488.0,"contact_point_centroid":[0.51251,0.03972,-0.00196],"force_p95":0.12631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50186,0.06313,0.22389]},{"body_a":"world","body_b":"grasp_target","contact_count":3164.0,"contact_point_centroid":[0.60005,0.11039,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.123,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5955,0.14501,0.25666]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50641,0.04474,0.08676]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4550.0,"contact_point_centroid":[0.50024,0.05955,0.04837],"force_p95":0.06985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09958,"mean_force":0.04777,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49915,0.04029,0.04589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5385.0,"contact_point_centroid":[0.5003,0.02114,0.04837],"force_p95":0.06458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08227,"mean_force":0.04087,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49915,0.04029,0.04589]}],"total_contact_groups":12},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60005,0.11039,0.01602],"final_tcp_position":[0.62324,0.16927,0.34859],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.23445,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3488.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50794,0.04852,0.11843],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":884.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50714,0.04101,0.05489],"tcp_start":[0.50794,0.04852,0.11843],"tcp_to_object_dist_end":0.0294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.04016,0.02577],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21212,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13847,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11735.0,"raw_peak_contact_force":0.18429,"tcp_end":[0.49912,0.04029,0.04586],"tcp_start":[0.50714,0.04101,0.05489],"tcp_to_object_dist_end":0.0241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5111,0.03968,0.1291],"object_pos_start":[0.51243,0.04016,0.02577],"object_to_goal_dist_end":0.17738,"object_to_goal_dist_start":0.21212,"object_z_max":0.12901,"peak_contact_force":0.09554,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33621.0,"raw_peak_contact_force":0.41506,"subtask_id":"approach_lift","tcp_end":[0.50213,0.03991,0.15744],"tcp_start":[0.49912,0.04029,0.04586],"tcp_to_object_dist_end":0.02972,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58413,0.11686,0.09784],"object_pos_start":[0.5111,0.03968,0.1291],"object_to_goal_dist_end":0.08492,"object_to_goal_dist_start":0.17738,"object_z_max":0.12912,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19646.0,"raw_peak_contact_force":0.28518,"subtask_id":"reach_goal","tcp_end":[0.57573,0.12121,0.14234],"tcp_start":[0.50213,0.03991,0.15744],"tcp_to_object_dist_end":0.04549,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60005,0.11039,0.01601],"object_pos_start":[0.58413,0.11686,0.09784],"object_to_goal_dist_end":0.14582,"object_to_goal_dist_start":0.08492,"object_z_max":0.09784,"peak_contact_force":0.12302,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":599.0,"raw_peak_contact_force":1.23445,"tcp_end":[0.56954,0.11989,0.16434],"tcp_start":[0.57573,0.12121,0.14234],"tcp_to_object_dist_end":0.15174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.60005,0.11039,0.01602],"object_pos_start":[0.60005,0.11039,0.01601],"object_to_goal_dist_end":0.14581,"object_to_goal_dist_start":0.14582,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3164.0,"raw_peak_contact_force":0.123,"tcp_end":[0.62324,0.16927,0.34859],"tcp_start":[0.56954,0.11989,0.16434],"tcp_to_object_dist_end":0.33853,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26259,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.1139,"approach_above.arc_height":0.06487,"approach_above.speed":0.05997,"descend_to_grasp.descend_offset":0.02011,"descend_to_grasp.speed":0.03299,"grasp_close.grasp_duration":0.22079,"lift_object.lift_height":0.27986,"lift_object.speed":0.05515,"release_object.release_duration":0.11377,"retract_up.retract_height":0.09178,"retract_up.speed":0.05689,"transport_to_goal.transport_speed":0.07854},"optimized_scores":{"best_composite_score":-0.18622,"best_fitness_score":0.56378,"best_task_score":0.20178},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.50305,0.15739,-0.00639],"force_p95":1.38143,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64809,"mean_force":0.39918,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51448,0.13169,0.19219]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.47906,0.04841,-0.00113],"force_p95":0.23356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40062,"mean_force":0.07031,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46884,0.04854,0.04822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":673.0,"contact_point_centroid":[0.51955,0.15161,0.16728],"force_p95":0.18523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30407,"mean_force":0.10689,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51767,0.13258,0.17239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19639.0,"contact_point_centroid":[0.46913,0.06742,0.09396],"force_p95":0.07553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28822,"mean_force":0.05179,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46868,0.04831,0.09275]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19374.0,"contact_point_centroid":[0.46821,0.0292,0.09335],"force_p95":0.0775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25421,"mean_force":0.0526,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46866,0.04831,0.0925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13720.0,"contact_point_centroid":[0.49358,0.10835,0.15293],"force_p95":0.11242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14902,"mean_force":0.06963,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4931,0.08964,0.15421]},{"body_a":"world","body_b":"grasp_target","contact_count":3004.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49111,0.05922,0.241]},{"body_a":"world","body_b":"grasp_target","contact_count":3600.0,"contact_point_centroid":[0.50308,0.1551,-0.00199],"force_p95":0.12318,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13,"mean_force":0.12162,"phase_index":6.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.54559,0.17861,0.30188]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04873,-0.00202],"force_p95":0.12791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12796,"mean_force":0.12432,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4714,0.04881,0.04779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13630.0,"contact_point_centroid":[0.49223,0.06985,0.15231],"force_p95":0.10475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12637,"mean_force":0.0684,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49244,0.08856,0.15368]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4776,0.0536,0.10073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":642.0,"contact_point_centroid":[0.51815,0.11476,0.16897],"force_p95":0.11582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11619,"mean_force":0.06996,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51816,0.13272,0.17292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5110.0,"contact_point_centroid":[0.46948,0.02948,0.04871],"force_p95":0.06522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08164,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47031,0.0487,0.04665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5108.0,"contact_point_centroid":[0.47005,0.06794,0.04906],"force_p95":0.06546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08162,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47031,0.0487,0.04665]}],"total_contact_groups":14},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50308,0.1551,0.01602],"final_tcp_position":[0.57781,0.22361,0.40345],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":25.23994,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.47982,0.05782,0.1468],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":25.23994,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47797,0.04951,0.0547],"tcp_start":[0.47982,0.05782,0.1468],"tcp_to_object_dist_end":0.02908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04871,0.02591],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2901,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12796,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12018.0,"raw_peak_contact_force":0.12796,"tcp_end":[0.47028,0.0487,0.04662],"tcp_start":[0.47797,0.04951,0.0547],"tcp_to_object_dist_end":0.0241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47438,0.04838,0.11026],"object_pos_start":[0.48261,0.04871,0.02591],"object_to_goal_dist_end":0.24203,"object_to_goal_dist_start":0.2901,"object_z_max":0.11019,"peak_contact_force":0.0839,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39185.0,"raw_peak_contact_force":0.40062,"subtask_id":"approach_lift","tcp_end":[0.47092,0.04833,0.1379],"tcp_start":[0.47028,0.0487,0.04662],"tcp_to_object_dist_end":0.02785,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52154,0.13307,0.14058],"object_pos_start":[0.47438,0.04838,0.11026],"object_to_goal_dist_end":0.14456,"object_to_goal_dist_start":0.24203,"object_z_max":0.14057,"peak_contact_force":0.14258,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27350.0,"raw_peak_contact_force":0.14902,"subtask_id":"reach_goal","tcp_end":[0.51977,0.133,0.17551],"tcp_start":[0.47092,0.04833,0.1379],"tcp_to_object_dist_end":0.03497,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50562,0.15552,0.01304],"object_pos_start":[0.52154,0.13307,0.14058],"object_to_goal_dist_end":0.24182,"object_to_goal_dist_start":0.14456,"object_z_max":0.14058,"peak_contact_force":0.09285,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1497.0,"raw_peak_contact_force":1.64809,"tcp_end":[0.51441,0.13168,0.19934],"tcp_start":[0.51977,0.133,0.17551],"tcp_to_object_dist_end":0.18803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.1551,0.01602],"object_pos_start":[0.50562,0.15552,0.01304],"object_to_goal_dist_end":0.24009,"object_to_goal_dist_start":0.24182,"object_z_max":0.0166,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3600.0,"raw_peak_contact_force":0.13,"tcp_end":[0.57781,0.22361,0.40345],"tcp_start":[0.51441,0.13168,0.19934],"tcp_to_object_dist_end":0.40048,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```