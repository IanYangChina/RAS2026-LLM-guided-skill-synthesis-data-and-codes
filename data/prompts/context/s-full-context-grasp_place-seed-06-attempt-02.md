## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3044 | 0.23 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1602 | 0.25 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.304) — your mutation base

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

- **Composite score**: -0.304
- **task_score** (E): 0.226
- **fitness_score**: 0.576  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1403 |
| descend_to_grasp | 1.00 | 1.00 | 0.1139 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 0.00 | 1.00 | 0.0983 |
| transport_to_goal | 0.00 | 0.67 | 0.1017 |
| descend_to_place | 0.67 | 1.00 | 0.0945 |
| release_object | 1.00 | 1.00 | 0.0222 |
| retract_up | 1.00 | 1.00 | 0.2192 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.033, 0.169) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.033, 0.169)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 24.309 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.025, 0.046) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.000 | 0.169 | 0.203 |
| lift_object | lift | 0.00 / step_budget | (0.487, 0.025, 0.046)→(0.483, 0.024, 0.145) | (0.500, 0.024, 0.026)→(0.488, 0.024, 0.116) | 0.272→0.229 | 1.00 / 34.000 | 0.099 | 0.423 |
| transport_to_goal | approach | 0.00 / step_budget | (0.483, 0.024, 0.145)→(0.524, 0.089, 0.210) | (0.488, 0.024, 0.116)→(0.530, 0.077, 0.093) | 0.229→0.187 | 0.67 / 8.667 | 0.079 | 0.684 |
| descend_to_place | descend | 0.67 / step_budget | (0.524, 0.089, 0.210)→(0.574, 0.163, 0.197) | (0.530, 0.077, 0.093)→(0.541, 0.079, 0.016) | 0.187→0.233 | 1.00 / 9.000 | 90999.300 | 1.188 |
| release_object | release | 1.00 / step_budget | (0.574, 0.163, 0.197)→(0.569, 0.161, 0.219) | (0.541, 0.079, 0.016)→(0.541, 0.079, 0.016) | 0.233→0.233 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_up | retract | 1.00 / step_budget | (0.569, 0.161, 0.219)→(0.597, 0.194, 0.433) | (0.541, 0.079, 0.016)→(0.541, 0.079, 0.016) | 0.233→0.233 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.342
- phase_score: 0.435
- phase_breakdown.approach_goal_score: 0.084
- phase_breakdown.approach_pre_grasp_score: 0.818
- phase_breakdown.reach_grasp_score: 0.722
- phase_breakdown.place_at_goal_score: 0.654
- phase_breakdown.approach_lift_score: 0.064
- grasp_place_fitness: 0.635

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.635
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.342
- **Median Q (composite search score)**: -0.323
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.330


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4708,"average_solve_count":274.0,"average_success_count":274.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.13194,"approach_above.arc_height":0.06306,"approach_above.speed":0.08281,"descend_to_grasp.descend_offset":0.02094,"descend_to_grasp.speed":0.04046,"descend_to_place.place_speed":0.03208,"grasp_close.grasp_duration":0.25348,"lift_object.lift_height":0.3495,"lift_object.speed":0.06323,"release_object.release_duration":0.148,"retract_up.retract_height":0.12643,"retract_up.speed":0.07107,"transport_to_goal.approach_goal_height":0.09658,"transport_to_goal.speed":0.14329},"optimized_scores":{"best_composite_score":-0.34528,"best_fitness_score":0.53472,"best_task_score":0.14555},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1935.0,"contact_point_centroid":[0.52712,0.02578,-0.00248],"force_p95":0.2065,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6356,"mean_force":0.14529,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51676,0.05266,0.20967]},{"body_a":"world","body_b":"grasp_target","contact_count":177.0,"contact_point_centroid":[0.50075,-0.01411,-0.00121],"force_p95":0.23548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41096,"mean_force":0.06853,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48918,-0.01449,0.04859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15747.0,"contact_point_centroid":[0.4886,0.00458,0.09412],"force_p95":0.11856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28003,"mean_force":0.06549,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48671,-0.01444,0.0938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18107.0,"contact_point_centroid":[0.4884,-0.03325,0.09538],"force_p95":0.08756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27947,"mean_force":0.05618,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48671,-0.01444,0.09493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5294.0,"contact_point_centroid":[0.50013,-0.0107,0.16638],"force_p95":0.11961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23554,"mean_force":0.07606,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49428,0.00733,0.16712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3910.0,"contact_point_centroid":[0.49882,0.02464,0.16321],"force_p95":0.14079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22998,"mean_force":0.10072,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49369,0.0061,0.16599]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50385,-0.01559,-0.0021],"force_p95":0.15085,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20832,"mean_force":0.13012,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49201,-0.01452,0.04803]},{"body_a":"world","body_b":"grasp_target","contact_count":2716.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12923,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49898,0.03007,0.22398]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4341.0,"contact_point_centroid":[0.49143,0.00468,0.0483],"force_p95":0.0751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12621,"mean_force":0.04949,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49088,-0.01451,0.0468]},{"body_a":"world","body_b":"grasp_target","contact_count":1420.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49804,-0.01099,0.10662]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52717,0.0258,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54687,0.116,0.22948]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52717,0.0258,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56231,0.15083,0.23654]},{"body_a":"world","body_b":"grasp_target","contact_count":3076.0,"contact_point_centroid":[0.52717,0.0258,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.57226,0.16782,0.3551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.49137,-0.03367,0.04823],"force_p95":0.07145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07316,"mean_force":0.04435,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49088,-0.01451,0.0468]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1836.0,"contact_point_centroid":[0.51824,0.05503,0.21416],"force_p95":0.01157,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51796,0.05503,0.21192]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4275.0,"contact_point_centroid":[0.54729,0.11599,0.23178],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54686,0.11598,0.22948]}],"total_contact_groups":17},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52717,0.0258,0.01602],"final_tcp_position":[0.58559,0.18521,0.45494],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.6356,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2716.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.4999,-0.00755,0.15768],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1420.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49883,-0.01459,0.0555],"tcp_start":[0.4999,-0.00755,0.15768],"tcp_to_object_dist_end":0.02992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01486,0.02563],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.312,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14832,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11096.0,"raw_peak_contact_force":0.20832,"tcp_end":[0.49085,-0.01451,0.04677],"tcp_start":[0.49883,-0.01459,0.0555],"tcp_to_object_dist_end":0.02477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49444,-0.01533,0.12096],"object_pos_start":[0.50376,-0.01486,0.02563],"object_to_goal_dist_end":0.25659,"object_to_goal_dist_start":0.312,"object_z_max":0.12084,"peak_contact_force":0.1354,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34031.0,"raw_peak_contact_force":0.41096,"subtask_id":"approach_lift","tcp_end":[0.4868,-0.01443,0.15097],"tcp_start":[0.49085,-0.01451,0.04677],"tcp_to_object_dist_end":0.03098,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52717,0.0258,0.01602],"object_pos_start":[0.49444,-0.01533,0.12096],"object_to_goal_dist_end":0.28908,"object_to_goal_dist_start":0.25659,"object_z_max":0.14923,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12975.0,"raw_peak_contact_force":1.6356,"subtask_id":"approach_goal","tcp_end":[0.52678,0.07237,0.22842],"tcp_start":[0.4868,-0.01443,0.15097],"tcp_to_object_dist_end":0.21745,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52717,0.0258,0.01602],"object_pos_start":[0.52717,0.0258,0.01602],"object_to_goal_dist_end":0.28908,"object_to_goal_dist_start":0.28908,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8275.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.56557,0.1517,0.23473],"tcp_start":[0.52678,0.07237,0.22842],"tcp_to_object_dist_end":0.25527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52717,0.0258,0.01602],"object_pos_start":[0.52717,0.0258,0.01602],"object_to_goal_dist_end":0.28908,"object_to_goal_dist_start":0.28908,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56111,0.15042,0.25659],"tcp_start":[0.56557,0.1517,0.23473],"tcp_to_object_dist_end":0.27305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":769.0,"n_steps_budget":1000.0,"object_pos_end":[0.52717,0.0258,0.01602],"object_pos_start":[0.52717,0.0258,0.01602],"object_to_goal_dist_end":0.28908,"object_to_goal_dist_start":0.28908,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3076.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58559,0.18521,0.45494],"tcp_start":[0.56111,0.15042,0.25659],"tcp_to_object_dist_end":0.47061,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06534,"average_solve_count":352.0,"average_success_count":352.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.11885,"approach_above.arc_height":0.0926,"approach_above.speed":0.06203,"descend_to_grasp.descend_offset":0.02002,"descend_to_grasp.speed":0.02142,"descend_to_place.place_speed":0.03203,"grasp_close.grasp_duration":0.11156,"lift_object.lift_height":0.29966,"lift_object.speed":0.05979,"release_object.release_duration":0.08901,"retract_up.retract_height":0.14685,"retract_up.speed":0.06373,"transport_to_goal.approach_goal_height":0.14507,"transport_to_goal.speed":0.10352},"optimized_scores":{"best_composite_score":-0.24538,"best_fitness_score":0.63462,"best_task_score":0.34201},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3887.0,"contact_point_centroid":[0.56512,0.09928,-0.00225],"force_p95":0.12583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73339,"mean_force":0.13462,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5829,0.13208,0.16334]},{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.50875,0.03985,-0.00116],"force_p95":0.27201,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45305,"mean_force":0.11718,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49762,0.0397,0.04708]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19122.0,"contact_point_centroid":[0.49601,0.05865,0.09561],"force_p95":0.07655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30766,"mean_force":0.05342,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49517,0.03952,0.0938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19500.0,"contact_point_centroid":[0.49559,0.02043,0.09434],"force_p95":0.07657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26552,"mean_force":0.0525,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49519,0.03952,0.09299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11737.0,"contact_point_centroid":[0.51939,0.04485,0.16377],"force_p95":0.12871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23075,"mean_force":0.07618,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51605,0.06358,0.16493]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03976,-0.00203],"force_p95":0.22496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22662,"mean_force":0.16309,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50051,0.03995,0.04682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12945.0,"contact_point_centroid":[0.52158,0.08356,0.16595],"force_p95":0.10587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19445,"mean_force":0.06844,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51746,0.06501,0.16643]},{"body_a":"world","body_b":"grasp_target","contact_count":3096.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50167,0.05737,0.23994]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50633,0.04459,0.102]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56516,0.09928,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60642,0.15807,0.14505]},{"body_a":"world","body_b":"grasp_target","contact_count":3576.0,"contact_point_centroid":[0.56516,0.09928,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.61354,0.16407,0.26782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4715.0,"contact_point_centroid":[0.49998,0.0591,0.04833],"force_p95":0.07894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1176,"mean_force":0.05576,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49936,0.03985,0.04554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5114.0,"contact_point_centroid":[0.50012,0.02069,0.04773],"force_p95":0.07599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1048,"mean_force":0.05096,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49936,0.03985,0.04554]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3874.0,"contact_point_centroid":[0.58551,0.13421,0.16398],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01626,"mean_force":0.01058,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58501,0.13419,0.16175]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.61014,0.15901,0.14385],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60942,0.15899,0.14142]}],"total_contact_groups":15},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.56516,0.09928,0.01602],"final_tcp_position":[0.62542,0.17126,0.37214],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":48.13221,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":775.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3096.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50809,0.04868,0.14926],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":48.13221,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50736,0.04055,0.05454],"tcp_start":[0.50809,0.04868,0.14926],"tcp_to_object_dist_end":0.02899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03993,0.02588],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21221,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.22349,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11629.0,"raw_peak_contact_force":0.22662,"tcp_end":[0.49933,0.03985,0.0455],"tcp_start":[0.50736,0.04055,0.05454],"tcp_to_object_dist_end":0.02359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49965,0.03964,0.11693],"object_pos_start":[0.51243,0.03993,0.02588],"object_to_goal_dist_end":0.18657,"object_to_goal_dist_start":0.21221,"object_z_max":0.11682,"peak_contact_force":0.07706,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38802.0,"raw_peak_contact_force":0.45305,"subtask_id":"approach_lift","tcp_end":[0.49529,0.03953,0.14343],"tcp_start":[0.49933,0.03985,0.0455],"tcp_to_object_dist_end":0.02686,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5596,0.10296,0.09241],"object_pos_start":[0.49965,0.03964,0.11693],"object_to_goal_dist_end":0.11058,"object_to_goal_dist_start":0.18657,"object_z_max":0.15932,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24682.0,"raw_peak_contact_force":0.23075,"subtask_id":"approach_goal","tcp_end":[0.54569,0.09326,0.19668],"tcp_start":[0.49529,0.03953,0.14343],"tcp_to_object_dist_end":0.10564,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56516,0.09928,0.01602],"object_pos_start":[0.5596,0.10296,0.09241],"object_to_goal_dist_end":0.16094,"object_to_goal_dist_start":0.11058,"object_z_max":0.09241,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7761.0,"raw_peak_contact_force":1.73339,"subtask_id":"place_at_goal","tcp_end":[0.61092,0.15933,0.14438],"tcp_start":[0.54569,0.09326,0.19668],"tcp_to_object_dist_end":0.14892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56516,0.09928,0.01602],"object_pos_start":[0.56516,0.09928,0.01602],"object_to_goal_dist_end":0.16094,"object_to_goal_dist_start":0.16094,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60466,0.15753,0.16461],"tcp_start":[0.61092,0.15933,0.14438],"tcp_to_object_dist_end":0.16441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":894.0,"n_steps_budget":1000.0,"object_pos_end":[0.56516,0.09928,0.01602],"object_pos_start":[0.56516,0.09928,0.01602],"object_to_goal_dist_end":0.16094,"object_to_goal_dist_start":0.16094,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3576.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62542,0.17126,0.37214],"tcp_start":[0.60466,0.15753,0.16461],"tcp_to_object_dist_end":0.36828,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97983,"average_solve_count":347.0,"average_success_count":347.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.16296,"approach_above.arc_height":0.04647,"approach_above.speed":0.09728,"descend_to_grasp.descend_offset":0.02019,"descend_to_grasp.speed":0.02935,"descend_to_place.place_speed":0.04371,"grasp_close.grasp_duration":0.18909,"lift_object.lift_height":0.28417,"lift_object.speed":0.03888,"release_object.release_duration":0.08175,"retract_up.retract_height":0.16171,"retract_up.speed":0.05755,"transport_to_goal.approach_goal_height":0.14438,"transport_to_goal.speed":0.06871},"optimized_scores":{"best_composite_score":-0.32258,"best_fitness_score":0.55742,"best_task_score":0.18938},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2162.0,"contact_point_centroid":[0.53001,0.11231,-0.00246],"force_p95":0.17571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7093,"mean_force":0.14428,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53345,0.15974,0.21013]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.47794,0.0478,-0.00117],"force_p95":0.3296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40616,"mean_force":0.0832,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46901,0.04805,0.04844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21510.0,"contact_point_centroid":[0.4661,0.06692,0.09442],"force_p95":0.07141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28302,"mean_force":0.0481,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46652,0.04782,0.09366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19493.0,"contact_point_centroid":[0.46531,0.02862,0.09445],"force_p95":0.07725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26438,"mean_force":0.05235,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46652,0.04782,0.09353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3123.0,"contact_point_centroid":[0.51235,0.13789,0.19909],"force_p95":0.13013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24926,"mean_force":0.10571,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5072,0.11973,0.20363]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11956.0,"contact_point_centroid":[0.4805,0.09115,0.16509],"force_p95":0.12643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18616,"mean_force":0.07925,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47907,0.07242,0.16701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13409.0,"contact_point_centroid":[0.48007,0.05431,0.1658],"force_p95":0.11425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18306,"mean_force":0.06936,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47932,0.07284,0.16753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3337.0,"contact_point_centroid":[0.51239,0.10236,0.19928],"force_p95":0.12169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18055,"mean_force":0.09797,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50764,0.12046,0.20368]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04866,-0.00204],"force_p95":0.13581,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17395,"mean_force":0.12621,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47164,0.04832,0.04797]},{"body_a":"world","body_b":"grasp_target","contact_count":1988.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.1329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49246,0.04575,0.26482]},{"body_a":"world","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47836,0.05274,0.12639]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52995,0.1122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54154,0.17588,0.21545]},{"body_a":"world","body_b":"grasp_target","contact_count":3916.0,"contact_point_centroid":[0.52995,0.1122,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.55934,0.20092,0.35406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46976,0.02897,0.04894],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09924,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47055,0.04821,0.04683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5384.0,"contact_point_centroid":[0.47007,0.06743,0.04859],"force_p95":0.06557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08213,"mean_force":0.04105,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47055,0.04821,0.04683]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2066.0,"contact_point_centroid":[0.53534,0.1618,0.21283],"force_p95":0.01152,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53481,0.16177,0.2105]}],"total_contact_groups":17},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52995,0.1122,0.01602],"final_tcp_position":[0.5804,0.22627,0.47263],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":272997.65556,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1988.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.48121,0.05669,0.19878],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":24.67071,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47822,0.049,0.05489],"tcp_start":[0.48121,0.05669,0.19878],"tcp_to_object_dist_end":0.02922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04832,0.02582],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2904,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13484,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12024.0,"raw_peak_contact_force":0.17395,"tcp_end":[0.47052,0.04821,0.0468],"tcp_start":[0.47822,0.049,0.05489],"tcp_to_object_dist_end":0.02422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46929,0.04792,0.11156],"object_pos_start":[0.48262,0.04832,0.02582],"object_to_goal_dist_end":0.24404,"object_to_goal_dist_start":0.2904,"object_z_max":0.11147,"peak_contact_force":0.08455,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41168.0,"raw_peak_contact_force":0.40616,"subtask_id":"approach_lift","tcp_end":[0.46658,0.04784,0.13925],"tcp_start":[0.47052,0.04821,0.0468],"tcp_to_object_dist_end":0.02783,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50339,0.1018,0.1698],"object_pos_start":[0.46929,0.04792,0.11156],"object_to_goal_dist_end":0.1612,"object_to_goal_dist_start":0.24404,"object_z_max":0.16973,"peak_contact_force":0.11535,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25365.0,"raw_peak_contact_force":0.18616,"subtask_id":"approach_goal","tcp_end":[0.49813,0.10226,0.20516],"tcp_start":[0.46658,0.04784,0.13925],"tcp_to_object_dist_end":0.03574,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52995,0.1122,0.01602],"object_pos_start":[0.50339,0.1018,0.1698],"object_to_goal_dist_end":0.2496,"object_to_goal_dist_start":0.1612,"object_z_max":0.16981,"peak_contact_force":272997.65556,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10688.0,"raw_peak_contact_force":1.7093,"subtask_id":"place_at_goal","tcp_end":[0.54496,0.17699,0.21325],"tcp_start":[0.49813,0.10226,0.20516],"tcp_to_object_dist_end":0.20814,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52995,0.1122,0.01602],"object_pos_start":[0.52995,0.1122,0.01602],"object_to_goal_dist_end":0.2496,"object_to_goal_dist_start":0.2496,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54025,0.17538,0.23569],"tcp_start":[0.54496,0.17699,0.21325],"tcp_to_object_dist_end":0.22881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":979.0,"n_steps_budget":1000.0,"object_pos_end":[0.52995,0.1122,0.01602],"object_pos_start":[0.52995,0.1122,0.01602],"object_to_goal_dist_end":0.2496,"object_to_goal_dist_start":0.2496,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3916.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5804,0.22627,0.47263],"tcp_start":[0.54025,0.17538,0.23569],"tcp_to_object_dist_end":0.47334,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```