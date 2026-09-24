## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → grasp → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2860 | 0.27 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3428 | 0.33 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.1238 | 0.18 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2769 | 0.20 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.2137 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.286) — your mutation base

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
  - 0.05
  weight: 0.3
- id: touch_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: pre_place
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: place
  target_entity: object
  weight: 0.2
phases:
- id: approach_1
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
    - 0.05
    orientation:
      mode: keep_current
  subtask_id: reach_object
- id: descend_1
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
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: touch_object
- id: grasp
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
    orientation:
      mode: keep_current
  guards:
  - id: grasp_ok
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: impedance_control
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
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: object_raised
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: lift_object
- id: transport
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_still_lifted
    when: before_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  - id: object_during_transport
    when: during_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: abort
  subtask_id: pre_place
- id: descend_2
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
    orientation:
      mode: keep_current
  guards:
  - id: object_still_lifted_before_descend
    when: before_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: place
- id: release
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_ok, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_raised, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_still_lifted, when=before_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
    - id=object_during_transport, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=object_still_lifted_before_descend, when=before_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.286
- **task_score** (E): 0.275
- **fitness_score**: 0.616  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2154 |
| descend_1 | 1.00 | 1.00 | 0.0544 |
| grasp | 1.00 | 1.00 | 0.0118 |
| lift | 1.00 | 1.00 | 0.1210 |
| retighten_grasp | 1.00 | 1.00 | 0.0099 |
| transport | 0.00 | 0.00 | 0.0001 |
| descend_2 | 0.00 | 0.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.023, 0.089) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.023, 0.089)→(0.494, 0.024, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.494, 0.024, 0.034)→(0.486, 0.023, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 41.667 | 0.151 | 0.229 |
| lift | lift | 1.00 / step_budget | (0.486, 0.023, 0.026)→(0.483, 0.023, 0.147) | (0.500, 0.023, 0.026)→(0.503, 0.023, 0.144) | 0.272→0.213 | 1.00 / 23.000 | 0.112 | 0.702 |
| retighten_grasp | grasp | 1.00 / step_budget | (0.483, 0.023, 0.147)→(0.477, 0.023, 0.139) | (0.503, 0.023, 0.144)→(0.492, 0.023, 0.125) | 0.213→0.225 | 1.00 / 25.667 | 0.113 | 0.145 |
| transport | approach | 0.00 / guard_failure | (0.506, 0.069, 0.165)→(0.506, 0.069, 0.165) | (0.492, 0.023, 0.125)→(0.513, 0.080, 0.079) | 0.225→0.197 | 0.00 / 0.000 | 0.000 | 0.245 |
| descend_2 | descend | 0.00 / guard_failure | (0.506, 0.069, 0.165)→(0.506, 0.069, 0.165) | (0.513, 0.080, 0.077)→(0.513, 0.080, 0.077) | 0.198→0.198 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.369
- phase_score: 0.487
- phase_breakdown.touch_object_score: 0.870
- phase_breakdown.place_score: 0.054
- phase_breakdown.lift_object_score: 0.468
- phase_breakdown.reach_object_score: 0.820
- phase_breakdown.pre_place_score: 0.047
- grasp_place_fitness: 0.662

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.662
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.369
- **Median Q (composite search score)**: 0.272
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84259,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.15042,"lift.lift_tolerance":0.09876,"transport.transport_speed":0.19724},"optimized_scores":{"best_composite_score":0.25362,"best_fitness_score":0.58362,"best_task_score":0.21029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.50102,-0.01523,-0.00149],"force_p95":0.66069,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69824,"mean_force":0.22399,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48893,-0.01528,0.02668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3510.0,"contact_point_centroid":[0.48931,0.00377,0.08036],"force_p95":0.1117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33715,"mean_force":0.07278,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48692,-0.01524,0.07777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3913.0,"contact_point_centroid":[0.48942,-0.03411,0.0783],"force_p95":0.10719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3079,"mean_force":0.06691,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48693,-0.01524,0.07656]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3722.0,"contact_point_centroid":[0.49303,0.02621,0.14903],"force_p95":0.14762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25825,"mean_force":0.09459,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48957,0.008,0.15222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3643.0,"contact_point_centroid":[0.49227,-0.01186,0.14796],"force_p95":0.15244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24364,"mean_force":0.09235,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48875,0.00637,0.15102]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.0155,-0.00203],"force_p95":0.13392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16578,"mean_force":0.12579,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49138,-0.0153,0.02691]},{"body_a":"world","body_b":"grasp_target","contact_count":2584.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49865,-0.00721,0.1939]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5889.0,"contact_point_centroid":[0.48648,-0.03369,0.14094],"force_p95":0.10527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13367,"mean_force":0.07738,"phase_index":4.0,"phase_name":"retighten_grasp","phase_type":"grasp","tcp_position_centroid":[0.48164,-0.01512,0.13971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5508.0,"contact_point_centroid":[0.48643,0.00355,0.14097],"force_p95":0.1122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13312,"mean_force":0.08234,"phase_index":4.0,"phase_name":"retighten_grasp","phase_type":"grasp","tcp_position_centroid":[0.48167,-0.01512,0.13974]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49783,-0.01497,0.06149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4107.0,"contact_point_centroid":[0.4909,0.00391,0.02843],"force_p95":0.07632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11356,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4902,-0.01529,0.02569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4896.0,"contact_point_centroid":[0.49093,-0.03437,0.02751],"force_p95":0.0686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0896,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49021,-0.01529,0.02569]}],"total_contact_groups":12},"final_pose_error":0.2135,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51011,0.04702,0.07757],"final_tcp_position":[0.50377,0.03571,0.17304],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.69824,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49943,-0.0146,0.08888],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":736.0,"raw_peak_contact_force":0.12263,"subtask_id":"touch_object","tcp_end":[0.49836,-0.01538,0.0343],"tcp_start":[0.49943,-0.0146,0.08888],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01516,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31205,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13119,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10803.0,"raw_peak_contact_force":0.16578,"tcp_end":[0.49017,-0.01529,0.02566],"tcp_start":[0.49836,-0.01538,0.0343],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":238.0,"n_steps_budget":960.0,"object_pos_end":[0.50724,-0.01507,0.14348],"object_pos_start":[0.50367,-0.01516,0.02587],"object_to_goal_dist_end":0.24147,"object_to_goal_dist_start":0.31205,"object_z_max":0.14301,"peak_contact_force":0.11019,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7485.0,"raw_peak_contact_force":0.69824,"subtask_id":"lift_object","tcp_end":[0.48693,-0.01522,0.14633],"tcp_start":[0.49017,-0.01529,0.02566],"tcp_to_object_dist_end":0.02051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49598,-0.01506,0.12504],"object_pos_start":[0.50724,-0.01507,0.14348],"object_to_goal_dist_end":0.25382,"object_to_goal_dist_start":0.24147,"object_z_max":0.14444,"peak_contact_force":0.11013,"phase_name":"retighten_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11397.0,"raw_peak_contact_force":0.13367,"tcp_end":[0.4807,-0.0151,0.1385],"tcp_start":[0.48693,-0.01522,0.14633],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.51012,0.04674,0.07977],"object_pos_start":[0.49598,-0.01506,0.12504],"object_to_goal_dist_end":0.23246,"object_to_goal_dist_start":0.25382,"object_z_max":0.14398,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7365.0,"raw_peak_contact_force":0.25825,"subtask_id":"pre_place","tcp_end":[0.50377,0.03571,0.17304],"tcp_start":[0.5037,0.03563,0.17301],"tcp_to_object_dist_end":0.09414,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.51011,0.04702,0.07757],"object_pos_start":[0.51011,0.04702,0.07757],"object_to_goal_dist_end":0.23389,"object_to_goal_dist_start":0.23389,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place","tcp_end":[0.50377,0.03571,0.17304],"tcp_start":[0.50377,0.03571,0.17304],"tcp_to_object_dist_end":0.09635,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7807,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.1508,"lift.lift_tolerance":0.0736,"transport.transport_speed":0.0832},"optimized_scores":{"best_composite_score":0.33243,"best_fitness_score":0.66243,"best_task_score":0.36884},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":67.0,"contact_point_centroid":[0.50973,0.03776,-0.00158],"force_p95":0.68695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72079,"mean_force":0.22593,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49723,0.03795,0.02624]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3899.0,"contact_point_centroid":[0.49788,0.05666,0.07774],"force_p95":0.11034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32999,"mean_force":0.06866,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49529,0.03777,0.07588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3510.0,"contact_point_centroid":[0.49788,0.0188,0.07994],"force_p95":0.11361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32763,"mean_force":0.07368,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49527,0.03777,0.07734]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03935,-0.00215],"force_p95":0.16782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25863,"mean_force":0.13469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4998,0.03818,0.02632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4339.0,"contact_point_centroid":[0.50626,0.03574,0.13705],"force_p95":0.1508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25151,"mean_force":0.09419,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50303,0.05398,0.1404]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4507.0,"contact_point_centroid":[0.50745,0.07311,0.13731],"force_p95":0.14039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24376,"mean_force":0.09489,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50404,0.05501,0.14073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4044.0,"contact_point_centroid":[0.49945,0.01888,0.02782],"force_p95":0.08189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14903,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49861,0.03808,0.02505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5622.0,"contact_point_centroid":[0.4951,0.05602,0.14085],"force_p95":0.10647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13894,"mean_force":0.08072,"phase_index":4.0,"phase_name":"retighten_grasp","phase_type":"grasp","tcp_position_centroid":[0.48997,0.03736,0.13937]},{"body_a":"world","body_b":"grasp_target","contact_count":2672.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50266,0.01826,0.1933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5573.0,"contact_point_centroid":[0.49487,0.01874,0.14055],"force_p95":0.11343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13286,"mean_force":0.08126,"phase_index":4.0,"phase_name":"retighten_grasp","phase_type":"grasp","tcp_position_centroid":[0.49003,0.03736,0.13945]},{"body_a":"world","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50614,0.03776,0.06086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.49939,0.05727,0.02685],"force_p95":0.07443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08715,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49862,0.03808,0.02506]}],"total_contact_groups":12},"final_pose_error":0.15321,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.5281,0.08329,0.07776],"final_tcp_position":[0.52172,0.07264,0.14714],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.72079,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2672.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50754,0.03694,0.08814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":728.0,"raw_peak_contact_force":0.12263,"subtask_id":"touch_object","tcp_end":[0.50686,0.03875,0.03398],"tcp_start":[0.50754,0.03694,0.08814],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03807,0.0255],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21361,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15785,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10869.0,"raw_peak_contact_force":0.25863,"tcp_end":[0.49859,0.03807,0.02502],"tcp_start":[0.50686,0.03875,0.03398],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":241.0,"n_steps_budget":960.0,"object_pos_end":[0.51588,0.0378,0.14344],"object_pos_start":[0.51239,0.03807,0.0255],"object_to_goal_dist_end":0.175,"object_to_goal_dist_start":0.21361,"object_z_max":0.14297,"peak_contact_force":0.11218,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7476.0,"raw_peak_contact_force":0.72079,"subtask_id":"lift_object","tcp_end":[0.49529,0.03776,0.14625],"tcp_start":[0.49859,0.03807,0.02502],"tcp_to_object_dist_end":0.02078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50418,0.03726,0.12438],"object_pos_start":[0.51588,0.0378,0.14344],"object_to_goal_dist_end":0.18425,"object_to_goal_dist_start":0.175,"object_z_max":0.14436,"peak_contact_force":0.11332,"phase_name":"retighten_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11195.0,"raw_peak_contact_force":0.13894,"tcp_end":[0.48901,0.03728,0.13811],"tcp_start":[0.49529,0.03776,0.14625],"tcp_to_object_dist_end":0.02046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.52806,0.08302,0.07952],"object_pos_start":[0.50418,0.03726,0.12438],"object_to_goal_dist_end":0.14901,"object_to_goal_dist_start":0.18425,"object_z_max":0.12438,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8846.0,"raw_peak_contact_force":0.25151,"subtask_id":"pre_place","tcp_end":[0.52172,0.07264,0.14714],"tcp_start":[0.52171,0.0726,0.14715],"tcp_to_object_dist_end":0.06871,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.5281,0.08329,0.07776],"object_pos_start":[0.5281,0.08329,0.07776],"object_to_goal_dist_end":0.14961,"object_to_goal_dist_start":0.14961,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place","tcp_end":[0.52172,0.07264,0.14714],"tcp_start":[0.52172,0.07264,0.14714],"tcp_to_object_dist_end":0.07049,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55072,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.15049,"lift.lift_tolerance":0.04106,"transport.transport_speed":0.02007},"optimized_scores":{"best_composite_score":0.27198,"best_fitness_score":0.60198,"best_task_score":0.24488},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.48021,0.04632,-0.00159],"force_p95":0.66581,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68726,"mean_force":0.22747,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46856,0.04666,0.0278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3645.0,"contact_point_centroid":[0.4688,0.0274,0.08136],"force_p95":0.11206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32702,"mean_force":0.06935,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46682,0.04646,0.07868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4107.0,"contact_point_centroid":[0.46869,0.06542,0.0799],"force_p95":0.10681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32434,"mean_force":0.06391,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46682,0.04646,0.07796]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.0483,-0.00218],"force_p95":0.17608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26157,"mean_force":0.1365,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47102,0.04692,0.02769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8041.0,"contact_point_centroid":[0.47711,0.0515,0.15247],"force_p95":0.14531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22494,"mean_force":0.08757,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.47354,0.06993,0.15427]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8538.0,"contact_point_centroid":[0.4781,0.08888,0.15319],"force_p95":0.13764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18082,"mean_force":0.08378,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.47395,0.07061,0.15474]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5681.0,"contact_point_centroid":[0.46652,0.06463,0.14277],"force_p95":0.10829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16102,"mean_force":0.07945,"phase_index":4.0,"phase_name":"retighten_grasp","phase_type":"grasp","tcp_position_centroid":[0.46174,0.04597,0.14134]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3630.0,"contact_point_centroid":[0.47121,0.02755,0.02972],"force_p95":0.09073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15621,"mean_force":0.05749,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46989,0.04681,0.02656]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5618.0,"contact_point_centroid":[0.46598,0.02734,0.14243],"force_p95":0.11309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15452,"mean_force":0.08022,"phase_index":4.0,"phase_name":"retighten_grasp","phase_type":"grasp","tcp_position_centroid":[0.46171,0.04597,0.1413]},{"body_a":"world","body_b":"grasp_target","contact_count":2632.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.12979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48892,0.02238,0.19368]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47769,0.04634,0.06155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5464.0,"contact_point_centroid":[0.46974,0.06591,0.02917],"force_p95":0.073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08779,"mean_force":0.04146,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46989,0.04681,0.02656]}],"total_contact_groups":12},"final_pose_error":0.19013,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5002,0.10945,0.07682],"final_tcp_position":[0.49226,0.09829,0.17526],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.68726,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":659.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2632.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47974,0.04532,0.08873],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":744.0,"raw_peak_contact_force":0.12263,"subtask_id":"touch_object","tcp_end":[0.47773,0.04758,0.03452],"tcp_start":[0.47974,0.04532,0.08873],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04672,0.02542],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29168,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16296,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10894.0,"raw_peak_contact_force":0.26157,"tcp_end":[0.46986,0.0468,0.02653],"tcp_start":[0.47773,0.04758,0.03452],"tcp_to_object_dist_end":0.01281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":234.0,"n_steps_budget":960.0,"object_pos_end":[0.48639,0.04646,0.14363],"object_pos_start":[0.48262,0.04672,0.02542],"object_to_goal_dist_end":0.22345,"object_to_goal_dist_start":0.29168,"object_z_max":0.14314,"peak_contact_force":0.11278,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7818.0,"raw_peak_contact_force":0.68726,"subtask_id":"lift_object","tcp_end":[0.46682,0.04644,0.14743],"tcp_start":[0.46986,0.0468,0.02653],"tcp_to_object_dist_end":0.01994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47509,0.04574,0.12671],"object_pos_start":[0.48639,0.04646,0.14363],"object_to_goal_dist_end":0.23601,"object_to_goal_dist_start":0.22345,"object_z_max":0.14459,"peak_contact_force":0.11681,"phase_name":"retighten_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11299.0,"raw_peak_contact_force":0.16102,"tcp_end":[0.46079,0.04588,0.14017],"tcp_start":[0.46682,0.04644,0.14743],"tcp_to_object_dist_end":0.01963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.50012,0.10922,0.07912],"object_pos_start":[0.47509,0.04574,0.12671],"object_to_goal_dist_end":0.20954,"object_to_goal_dist_start":0.23601,"object_z_max":0.14814,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16579.0,"raw_peak_contact_force":0.22494,"subtask_id":"pre_place","tcp_end":[0.49226,0.09829,0.17526],"tcp_start":[0.4922,0.09823,0.17525],"tcp_to_object_dist_end":0.09708,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.5002,0.10945,0.07682],"object_pos_start":[0.5002,0.10945,0.07682],"object_to_goal_dist_end":0.21105,"object_to_goal_dist_start":0.21105,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place","tcp_end":[0.49226,0.09829,0.17526],"tcp_start":[0.49226,0.09829,0.17526],"tcp_to_object_dist_end":0.09939,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```