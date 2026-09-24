## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1459 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2636 | 0.31 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 9 | 0.2855 | 0.73 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1355 | 0.30 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1606 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.146) — your mutation base

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
  weight: 0.2
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.035
  weight: 0.4
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
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
  subtask_id: lift_clearance
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
    - 0.035
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.035], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.146
- **task_score** (E): 0.284
- **fitness_score**: 0.604  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1471 |
| descend_to_grasp | 1.00 | 1.00 | 0.1069 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1411 |
| transport_to_goal | 0.67 | 0.67 | 0.1659 |
| release_object | 1.00 | 1.00 | 0.0221 |
| retract_from_goal | 1.00 | 1.00 | 0.0808 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.032, 0.162) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, 0.032, 0.162)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 16.090 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.025, 0.047) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.000 | 0.173 | 0.208 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.025, 0.047)→(0.483, 0.024, 0.188) | (0.500, 0.024, 0.026)→(0.493, 0.024, 0.163) | 0.272→0.210 | 1.00 / 34.333 | 0.087 | 0.423 |
| transport_to_goal | approach | 0.67 / step_budget | (0.483, 0.024, 0.188)→(0.573, 0.156, 0.221) | (0.493, 0.024, 0.163)→(0.574, 0.169, 0.052) | 0.210→0.162 | 0.67 / 4.000 | 3249.710 | 1.215 |
| release_object | release | 1.00 / step_budget | (0.573, 0.156, 0.221)→(0.568, 0.154, 0.242) | (0.574, 0.169, 0.052)→(0.575, 0.177, 0.016) | 0.162→0.197 | 1.00 / 4.000 | 0.123 | 0.852 |
| retract_from_goal | retract | 1.00 / step_budget | (0.568, 0.154, 0.242)→(0.566, 0.154, 0.323) | (0.575, 0.177, 0.016)→(0.575, 0.177, 0.016) | 0.197→0.197 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.416
- phase_score: 0.697
- phase_breakdown.approach_pre_grasp_score: 0.754
- phase_breakdown.reach_goal_score: 0.652
- phase_breakdown.reach_grasp_score: 0.726
- phase_breakdown.lift_clearance_score: 0.703
- grasp_place_fitness: 0.671

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.671
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.416
- **Median Q (composite search score)**: -0.169
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.356


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24242,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.09388,"approach_above.arc_height":0.04603,"approach_above.speed":0.05194,"descend_to_grasp.descend_offset":0.02138,"descend_to_grasp.speed":0.03058,"grasp_close.grasp_duration":0.13003,"lift_object.lift_distance":0.17608,"lift_object.speed":0.05343,"release_object.release_duration":0.2644,"retract_from_goal.retract_distance":0.09708,"retract_from_goal.speed":0.23092,"transport_to_goal.transport_speed":0.14916},"optimized_scores":{"best_composite_score":-0.18987,"best_fitness_score":0.56013,"best_task_score":0.19762},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":57.0,"contact_point_centroid":[0.56128,0.11947,-0.00806],"force_p95":1.64778,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99986,"mean_force":0.93157,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54327,0.10456,0.24399]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5621,0.11908,-0.00308],"force_p95":0.23001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56157,"mean_force":0.12616,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54058,0.10504,0.24693]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.5012,-0.0139,-0.0015],"force_p95":0.34386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40831,"mean_force":0.1074,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48947,-0.014,0.04832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10813.0,"contact_point_centroid":[0.48764,-0.03302,0.12462],"force_p95":0.08217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27775,"mean_force":0.05444,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48714,-0.01395,0.12353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9706.0,"contact_point_centroid":[0.48774,0.00519,0.12501],"force_p95":0.08366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27061,"mean_force":0.05912,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48714,-0.01395,0.12393]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12235.0,"contact_point_centroid":[0.51317,0.01807,0.21769],"force_p95":0.12039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24822,"mean_force":0.0688,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50934,0.03652,0.21808]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50387,-0.01557,-0.00214],"force_p95":0.16086,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21857,"mean_force":0.13266,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4918,-0.01403,0.04828]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10807.0,"contact_point_centroid":[0.51113,0.05263,0.21577],"force_p95":0.13359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19755,"mean_force":0.07893,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50807,0.03389,0.21713]},{"body_a":"world","body_b":"grasp_target","contact_count":2772.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49873,0.02197,0.20946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4333.0,"contact_point_centroid":[0.49127,0.00518,0.04835],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13148,"mean_force":0.0495,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49066,-0.01401,0.04705]},{"body_a":"world","body_b":"grasp_target","contact_count":984.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49786,-0.01037,0.09046]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.56215,0.11911,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.53763,0.10435,0.30535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5010.0,"contact_point_centroid":[0.4912,-0.0332,0.0484],"force_p95":0.07302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07525,"mean_force":0.04411,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49067,-0.01401,0.04705]},{"body_a":"left_finger","body_b":"right_finger","contact_count":76.0,"contact_point_centroid":[0.54213,0.10538,0.24337],"force_p95":0.01617,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.0121,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54197,0.10538,0.2406]}],"total_contact_groups":14},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56215,0.11911,0.01602],"final_tcp_position":[0.53764,0.10431,0.34454],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.99986,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2772.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.49956,-0.00686,0.12495],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":246.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":984.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49861,-0.01407,0.05573],"tcp_start":[0.49956,-0.00686,0.12495],"tcp_to_object_dist_end":0.03021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50378,-0.01455,0.02551],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31188,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15733,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11143.0,"raw_peak_contact_force":0.21857,"tcp_end":[0.49063,-0.01401,0.04701],"tcp_start":[0.49861,-0.01407,0.05573],"tcp_to_object_dist_end":0.02521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.49506,-0.01428,0.17746],"object_pos_start":[0.50378,-0.01455,0.02551],"object_to_goal_dist_end":0.23265,"object_to_goal_dist_start":0.31188,"object_z_max":0.17718,"peak_contact_force":0.07842,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20607.0,"raw_peak_contact_force":0.40831,"subtask_id":"lift_clearance","tcp_end":[0.48741,-0.01395,0.20347],"tcp_start":[0.49063,-0.01401,0.04701],"tcp_to_object_dist_end":0.02712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56293,0.1196,-0.00395],"object_pos_start":[0.49506,-0.01428,0.17746],"object_to_goal_dist_end":0.26214,"object_to_goal_dist_start":0.23265,"object_z_max":0.20474,"peak_contact_force":0.60594,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23099.0,"raw_peak_contact_force":1.99986,"subtask_id":"reach_goal","tcp_end":[0.54372,0.10554,0.24434],"tcp_start":[0.48741,-0.01395,0.20347],"tcp_to_object_dist_end":0.24944,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56215,0.11911,0.01602],"object_pos_start":[0.56293,0.1196,-0.00395],"object_to_goal_dist_end":0.24321,"object_to_goal_dist_start":0.26214,"object_z_max":0.01671,"peak_contact_force":0.12262,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":876.0,"raw_peak_contact_force":0.56157,"tcp_end":[0.53941,0.10475,0.26732],"tcp_start":[0.54372,0.10554,0.24434],"tcp_to_object_dist_end":0.25274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":263.0,"n_steps_budget":600.0,"object_pos_end":[0.56215,0.11911,0.01602],"object_pos_start":[0.56215,0.11911,0.01602],"object_to_goal_dist_end":0.24321,"object_to_goal_dist_start":0.24321,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53764,0.10431,0.34454],"tcp_start":[0.53941,0.10475,0.26732],"tcp_to_object_dist_end":0.32977,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45503,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.12668,"approach_above.arc_height":0.04601,"approach_above.speed":0.08325,"descend_to_grasp.descend_offset":0.02033,"descend_to_grasp.speed":0.02929,"grasp_close.grasp_duration":0.1554,"lift_object.lift_distance":0.14812,"lift_object.speed":0.09644,"release_object.release_duration":0.09488,"retract_from_goal.retract_distance":0.11737,"retract_from_goal.speed":0.256,"transport_to_goal.transport_speed":0.28059},"optimized_scores":{"best_composite_score":-0.07897,"best_fitness_score":0.67103,"best_task_score":0.41553},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":517.0,"contact_point_centroid":[0.60109,0.17398,-0.00384],"force_p95":0.7536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38359,"mean_force":0.19752,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60508,0.15254,0.17111]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50991,0.03983,-0.00133],"force_p95":0.34385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47313,"mean_force":0.10111,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49814,0.03944,0.04715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8439.0,"contact_point_centroid":[0.54261,0.06595,0.16937],"force_p95":0.13944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34954,"mean_force":0.08781,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53766,0.08446,0.17042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6839.0,"contact_point_centroid":[0.49842,0.05821,0.10331],"force_p95":0.10561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30289,"mean_force":0.06544,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49573,0.03924,0.10115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6534.0,"contact_point_centroid":[0.49823,0.0203,0.10098],"force_p95":0.11119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2782,"mean_force":0.06803,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49578,0.03924,0.09922]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03976,-0.00202],"force_p95":0.22423,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22734,"mean_force":0.16351,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50054,0.03965,0.04715]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8742.0,"contact_point_centroid":[0.54346,0.10389,0.16935],"force_p95":0.1244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19708,"mean_force":0.0848,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53864,0.08544,0.17044]},{"body_a":"world","body_b":"grasp_target","contact_count":2344.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50195,0.04555,0.24101]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60099,0.17465,-0.00199],"force_p95":0.12304,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12358,"mean_force":0.12266,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60842,0.15906,0.17179]},{"body_a":"world","body_b":"grasp_target","contact_count":1484.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50622,0.04365,0.10779]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.60099,0.17465,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.60436,0.15777,0.23968]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4869.0,"contact_point_centroid":[0.50018,0.05884,0.04917],"force_p95":0.07641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11444,"mean_force":0.05435,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49939,0.03956,0.04587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5337.0,"contact_point_centroid":[0.50059,0.02039,0.04832],"force_p95":0.07278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10259,"mean_force":0.04906,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49939,0.03956,0.04586]},{"body_a":"left_finger","body_b":"right_finger","contact_count":253.0,"contact_point_centroid":[0.60928,0.15663,0.1735],"force_p95":0.01419,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01562,"mean_force":0.01143,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60913,0.15661,0.17116]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.61151,0.15997,0.17029],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01024,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61117,0.15995,0.16818]}],"total_contact_groups":15},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60099,0.17465,0.01602],"final_tcp_position":[0.60458,0.15777,0.289],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.52545,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2344.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50786,0.04719,0.16103],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":48.02342,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1484.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50739,0.04025,0.05488],"tcp_start":[0.50786,0.04719,0.16103],"tcp_to_object_dist_end":0.02931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03976,0.02589],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21232,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.22398,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12006.0,"raw_peak_contact_force":0.22734,"tcp_end":[0.49936,0.03955,0.04583],"tcp_start":[0.50739,0.04025,0.05488],"tcp_to_object_dist_end":0.02383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":412.0,"n_steps_budget":960.0,"object_pos_end":[0.51092,0.03943,0.14963],"object_pos_start":[0.51241,0.03976,0.02589],"object_to_goal_dist_end":0.17704,"object_to_goal_dist_start":0.21232,"object_z_max":0.14936,"peak_contact_force":0.10246,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13449.0,"raw_peak_contact_force":0.47313,"subtask_id":"lift_clearance","tcp_end":[0.49582,0.03925,0.17437],"tcp_start":[0.49936,0.03955,0.04583],"tcp_to_object_dist_end":0.02899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60101,0.17465,0.01601],"object_pos_start":[0.51092,0.03943,0.14963],"object_to_goal_dist_end":0.13174,"object_to_goal_dist_start":0.17704,"object_z_max":0.14995,"peak_contact_force":9748.52545,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17951.0,"raw_peak_contact_force":1.38359,"subtask_id":"reach_goal","tcp_end":[0.61253,0.16015,0.17116],"tcp_start":[0.49582,0.03925,0.17437],"tcp_to_object_dist_end":0.15625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60099,0.17465,0.01602],"object_pos_start":[0.60101,0.17465,0.01601],"object_to_goal_dist_end":0.13173,"object_to_goal_dist_start":0.13174,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12358,"tcp_end":[0.60681,0.15854,0.19131],"tcp_start":[0.61253,0.16015,0.17116],"tcp_to_object_dist_end":0.17613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":600.0,"object_pos_end":[0.60099,0.17465,0.01602],"object_pos_start":[0.60099,0.17465,0.01602],"object_to_goal_dist_end":0.13173,"object_to_goal_dist_start":0.13173,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1468.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60458,0.15777,0.289],"tcp_start":[0.60681,0.15854,0.19131],"tcp_to_object_dist_end":0.27353,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16165,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.16434,"approach_above.arc_height":0.08043,"approach_above.speed":0.04219,"descend_to_grasp.descend_offset":0.02017,"descend_to_grasp.speed":0.03708,"grasp_close.grasp_duration":0.17414,"lift_object.lift_distance":0.15756,"lift_object.speed":0.03782,"release_object.release_duration":0.1288,"retract_from_goal.retract_distance":0.08732,"retract_from_goal.speed":0.12075,"transport_to_goal.transport_speed":0.24089},"optimized_scores":{"best_composite_score":-0.16882,"best_fitness_score":0.58118,"best_task_score":0.23741},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":624.0,"contact_point_centroid":[0.56111,0.23781,-0.00384],"force_p95":0.86227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.872,"mean_force":0.20758,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5589,0.20037,0.24897]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47918,0.04794,-0.00147],"force_p95":0.37198,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38718,"mean_force":0.16116,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46916,0.04797,0.04769]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9648.0,"contact_point_centroid":[0.46698,0.06672,0.11541],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26816,"mean_force":0.053,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46679,0.04772,0.11392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14036.0,"contact_point_centroid":[0.50433,0.09444,0.20772],"force_p95":0.1033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26103,"mean_force":0.06633,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50607,0.11346,0.20891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8015.0,"contact_point_centroid":[0.46608,0.02853,0.11606],"force_p95":0.08743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25043,"mean_force":0.06133,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46678,0.04772,0.11452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16319.0,"contact_point_centroid":[0.5063,0.13435,0.20845],"force_p95":0.08596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21496,"mean_force":0.05696,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50741,0.11556,0.2098]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04865,-0.00205],"force_p95":0.13941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17888,"mean_force":0.12688,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47129,0.04818,0.04793]},{"body_a":"world","body_b":"grasp_target","contact_count":2176.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48203,0.04337,0.2637]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.56095,0.23836,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12283,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.55673,0.1994,0.30088]},{"body_a":"world","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47607,0.05187,0.12668]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4355.0,"contact_point_centroid":[0.47029,0.02882,0.04851],"force_p95":0.07461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11805,"mean_force":0.04967,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47019,0.04808,0.04679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5394.0,"contact_point_centroid":[0.46981,0.06721,0.04885],"force_p95":0.06584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08351,"mean_force":0.04075,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47019,0.04808,0.0468]}],"total_contact_groups":12},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56095,0.23836,0.01602],"final_tcp_position":[0.5567,0.19932,0.33537],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.872,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.47701,0.05512,0.19952],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47786,0.04886,0.05484],"tcp_start":[0.47701,0.05512,0.19952],"tcp_to_object_dist_end":0.02922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48263,0.0482,0.02579],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29049,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13848,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11549.0,"raw_peak_contact_force":0.17888,"tcp_end":[0.47016,0.04807,0.04676],"tcp_start":[0.47786,0.04886,0.05484],"tcp_to_object_dist_end":0.0244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.47435,0.04778,0.16088],"object_pos_start":[0.48263,0.0482,0.02579],"object_to_goal_dist_end":0.2218,"object_to_goal_dist_start":0.29049,"object_z_max":0.1606,"peak_contact_force":0.0793,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17749.0,"raw_peak_contact_force":0.38718,"subtask_id":"lift_clearance","tcp_end":[0.46688,0.04773,0.18487],"tcp_start":[0.47016,0.04807,0.04676],"tcp_to_object_dist_end":0.02512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55705,0.21397,0.14438],"object_pos_start":[0.47435,0.04778,0.16088],"object_to_goal_dist_end":0.09084,"object_to_goal_dist_start":0.2218,"object_z_max":0.20519,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30355.0,"raw_peak_contact_force":0.26103,"subtask_id":"reach_goal","tcp_end":[0.56255,0.20166,0.24636],"tcp_start":[0.46688,0.04773,0.18487],"tcp_to_object_dist_end":0.10287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56095,0.23836,0.016],"object_pos_start":[0.55705,0.21397,0.14438],"object_to_goal_dist_end":0.21571,"object_to_goal_dist_start":0.09084,"object_z_max":0.14438,"peak_contact_force":0.12285,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":624.0,"raw_peak_contact_force":1.872,"tcp_end":[0.55841,0.20013,0.26781],"tcp_start":[0.56255,0.20166,0.24636],"tcp_to_object_dist_end":0.25471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":600.0,"object_pos_end":[0.56095,0.23836,0.01602],"object_pos_start":[0.56095,0.23836,0.016],"object_to_goal_dist_end":0.21569,"object_to_goal_dist_start":0.21571,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":996.0,"raw_peak_contact_force":0.12283,"tcp_end":[0.5567,0.19932,0.33537],"tcp_start":[0.55841,0.20013,0.26781],"tcp_to_object_dist_end":0.32175,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```