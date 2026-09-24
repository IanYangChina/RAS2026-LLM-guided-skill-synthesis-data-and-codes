## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3783 | 0.40 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → grasp → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 3 | 0.2965 | 0.30 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3246 | 0.29 | ❌ rejected |
| 6 | approach → descend → grasp → lift → grasp → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2798 | 0.26 | ❌ rejected |
| 5 | approach → descend → grasp → lift → grasp → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2860 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.378) — your mutation base

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
  target_entity: object
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
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.04
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
    threshold: 0.01
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
    tolerance: 0.02
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_still_lifted, when=before_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
    - id=object_during_transport, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.01
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=object_still_lifted_before_descend, when=before_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.378
- **task_score** (E): 0.399
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2154 |
| descend_1 | 1.00 | 1.00 | 0.0544 |
| grasp | 1.00 | 1.00 | 0.0118 |
| lift | 1.00 | 1.00 | 0.1720 |
| transport | 1.00 | 0.00 | 0.1932 |
| descend_2 | 0.00 | 0.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.023, 0.089) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.023, 0.089)→(0.494, 0.024, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.494, 0.024, 0.034)→(0.486, 0.023, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 41.667 | 0.151 | 0.229 |
| lift | lift | 1.00 / step_budget | (0.486, 0.023, 0.026)→(0.483, 0.023, 0.198) | (0.500, 0.023, 0.026)→(0.506, 0.023, 0.192) | 0.272→0.204 | 1.00 / 24.000 | 0.113 | 0.705 |
| transport | approach | 1.00 / step_budget | (0.483, 0.023, 0.198)→(0.583, 0.176, 0.244) | (0.506, 0.023, 0.192)→(0.586, 0.188, 0.067) | 0.204→0.144 | 0.00 / 0.000 | 0.000 | 0.321 |
| descend_2 | descend | 0.00 / guard_failure | (0.583, 0.176, 0.244)→(0.583, 0.176, 0.244) | (0.586, 0.188, 0.067)→(0.586, 0.188, 0.067) | 0.144→0.144 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.565
- phase_score: 0.666
- phase_breakdown.touch_object_score: 0.870
- phase_breakdown.place_score: 0.360
- phase_breakdown.lift_object_score: 0.645
- phase_breakdown.reach_object_score: 0.820
- phase_breakdown.pre_place_score: 0.550
- grasp_place_fitness: 0.761

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.761
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.565
- **Median Q (composite search score)**: 0.344
- **K-run variance**: 0.0034
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.183


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86782,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.19107,"lift.lift_tolerance":0.01099,"transport.transport_speed":0.07533},"optimized_scores":{"best_composite_score":0.33025,"best_fitness_score":0.63025,"best_task_score":0.30354},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.50101,-0.01523,-0.00149],"force_p95":0.66182,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69967,"mean_force":0.22734,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48892,-0.01528,0.02668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4419.0,"contact_point_centroid":[0.48994,0.00369,0.09832],"force_p95":0.11517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33775,"mean_force":0.07663,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48694,-0.01524,0.0959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4831.0,"contact_point_centroid":[0.48999,-0.03405,0.09533],"force_p95":0.11316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30849,"mean_force":0.07147,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48696,-0.01524,0.0936]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3586.0,"contact_point_centroid":[0.52469,0.07216,0.21931],"force_p95":0.16453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30798,"mean_force":0.10103,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51956,0.05401,0.22043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3123.0,"contact_point_centroid":[0.52124,0.02819,0.21606],"force_p95":0.18566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27983,"mean_force":0.10768,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51603,0.04664,0.21675]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.0155,-0.00203],"force_p95":0.13392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16578,"mean_force":0.12579,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49138,-0.0153,0.02691]},{"body_a":"world","body_b":"grasp_target","contact_count":2584.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49865,-0.00721,0.1939]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49783,-0.01497,0.06149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4107.0,"contact_point_centroid":[0.4909,0.00391,0.02843],"force_p95":0.07632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11356,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4902,-0.01529,0.02569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4896.0,"contact_point_centroid":[0.49093,-0.03437,0.02751],"force_p95":0.0686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0896,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49021,-0.01529,0.02569]}],"total_contact_groups":10},"final_pose_error":0.02962,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57919,0.18891,0.06945],"final_tcp_position":[0.57552,0.16706,0.2799],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.69967,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2584.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49943,-0.0146,0.08888],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":736.0,"raw_peak_contact_force":0.12263,"subtask_id":"touch_object","tcp_end":[0.49836,-0.01538,0.0343],"tcp_start":[0.49943,-0.0146,0.08888],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01516,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31205,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13119,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10803.0,"raw_peak_contact_force":0.16578,"tcp_end":[0.49017,-0.01529,0.02566],"tcp_start":[0.49836,-0.01538,0.0343],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.50959,-0.01518,0.18215],"object_pos_start":[0.50367,-0.01516,0.02587],"object_to_goal_dist_end":0.22669,"object_to_goal_dist_start":0.31205,"object_z_max":0.18169,"peak_contact_force":0.11441,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9312.0,"raw_peak_contact_force":0.69967,"subtask_id":"lift_object","tcp_end":[0.48726,-0.01522,0.18735],"tcp_start":[0.49017,-0.01529,0.02566],"tcp_to_object_dist_end":0.02293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.57919,0.18891,0.06945],"object_pos_start":[0.50959,-0.01518,0.18215],"object_to_goal_dist_end":0.17883,"object_to_goal_dist_start":0.22669,"object_z_max":0.23391,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6709.0,"raw_peak_contact_force":0.30798,"subtask_id":"pre_place","tcp_end":[0.57552,0.16706,0.2799],"tcp_start":[0.48726,-0.01522,0.18735],"tcp_to_object_dist_end":0.2116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.57919,0.18891,0.06945],"object_pos_start":[0.57919,0.18891,0.06945],"object_to_goal_dist_end":0.17883,"object_to_goal_dist_start":0.17883,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place","tcp_end":[0.57552,0.16706,0.2799],"tcp_start":[0.57552,0.16706,0.2799],"tcp_to_object_dist_end":0.2116,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85235,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.19871,"lift.lift_tolerance":0.05835,"transport.transport_speed":0.09415},"optimized_scores":{"best_composite_score":0.46068,"best_fitness_score":0.76068,"best_task_score":0.56535},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":67.0,"contact_point_centroid":[0.50971,0.03776,-0.00157],"force_p95":0.69027,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72377,"mean_force":0.22681,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49721,0.03795,0.02626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2324.0,"contact_point_centroid":[0.54071,0.06108,0.18827],"force_p95":0.19642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36312,"mean_force":0.1136,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53504,0.07899,0.19013]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4944.0,"contact_point_centroid":[0.49847,0.05662,0.09738],"force_p95":0.11599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33118,"mean_force":0.07372,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49533,0.03777,0.09552]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4654.0,"contact_point_centroid":[0.49865,0.01891,0.10237],"force_p95":0.11509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32909,"mean_force":0.07686,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49532,0.03777,0.10009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1743.0,"contact_point_centroid":[0.53932,0.09581,0.18866],"force_p95":0.22028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26472,"mean_force":0.1291,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53353,0.07743,0.19019]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03935,-0.00215],"force_p95":0.16782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25863,"mean_force":0.13469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4998,0.03818,0.02632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4044.0,"contact_point_centroid":[0.49945,0.01888,0.02782],"force_p95":0.08189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14903,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49861,0.03808,0.02505]},{"body_a":"world","body_b":"grasp_target","contact_count":2672.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50266,0.01826,0.1933]},{"body_a":"world","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50614,0.03776,0.06086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.49939,0.05727,0.02685],"force_p95":0.07443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08715,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49862,0.03808,0.02506]}],"total_contact_groups":10},"final_pose_error":0.02988,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61324,0.13842,0.06789],"final_tcp_position":[0.60657,0.15275,0.18724],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.72377,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2672.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50754,0.03694,0.08814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":728.0,"raw_peak_contact_force":0.12263,"subtask_id":"touch_object","tcp_end":[0.50686,0.03875,0.03398],"tcp_start":[0.50754,0.03694,0.08814],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03807,0.0255],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21361,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15785,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10869.0,"raw_peak_contact_force":0.25863,"tcp_end":[0.49859,0.03807,0.02502],"tcp_start":[0.50686,0.03875,0.03398],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.51847,0.0381,0.18823],"object_pos_start":[0.51239,0.03807,0.0255],"object_to_goal_dist_end":0.17843,"object_to_goal_dist_start":0.21361,"object_z_max":0.18776,"peak_contact_force":0.11265,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9665.0,"raw_peak_contact_force":0.72377,"subtask_id":"lift_object","tcp_end":[0.49568,0.03779,0.19397],"tcp_start":[0.49859,0.03807,0.02502],"tcp_to_object_dist_end":0.02351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.61324,0.13842,0.06789],"object_pos_start":[0.51847,0.0381,0.18823],"object_to_goal_dist_end":0.08555,"object_to_goal_dist_start":0.17843,"object_z_max":0.18925,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4067.0,"raw_peak_contact_force":0.36312,"subtask_id":"pre_place","tcp_end":[0.60657,0.15275,0.18724],"tcp_start":[0.49568,0.03779,0.19397],"tcp_to_object_dist_end":0.12039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.61324,0.13842,0.06789],"object_pos_start":[0.61324,0.13842,0.06789],"object_to_goal_dist_end":0.08555,"object_to_goal_dist_start":0.08555,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place","tcp_end":[0.60657,0.15275,0.18724],"tcp_start":[0.60657,0.15275,0.18724],"tcp_to_object_dist_end":0.12039,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86628,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift.lift_height":0.2148,"lift.lift_tolerance":0.03899,"transport.transport_speed":0.07606},"optimized_scores":{"best_composite_score":0.34398,"best_fitness_score":0.64398,"best_task_score":0.32887},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.47953,0.04627,-0.00163],"force_p95":0.67028,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69134,"mean_force":0.23458,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46853,0.04666,0.02775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5169.0,"contact_point_centroid":[0.46976,0.02753,0.11002],"force_p95":0.11473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32918,"mean_force":0.07419,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46685,0.04645,0.10763]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5577.0,"contact_point_centroid":[0.46951,0.06534,0.10535],"force_p95":0.11497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32587,"mean_force":0.07039,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46684,0.04645,0.10349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2788.0,"contact_point_centroid":[0.50379,0.07881,0.22568],"force_p95":0.17256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29133,"mean_force":0.1041,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49799,0.09716,0.22709]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2726.0,"contact_point_centroid":[0.50806,0.12282,0.22765],"force_p95":0.18619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.291,"mean_force":0.11186,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50257,0.10456,0.22955]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.0483,-0.00218],"force_p95":0.17608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26157,"mean_force":0.1365,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47102,0.04692,0.02769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3630.0,"contact_point_centroid":[0.47121,0.02755,0.02972],"force_p95":0.09073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15621,"mean_force":0.05749,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46989,0.04681,0.02656]},{"body_a":"world","body_b":"grasp_target","contact_count":2632.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.12979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48892,0.02238,0.19368]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47769,0.04634,0.06155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5464.0,"contact_point_centroid":[0.46974,0.06591,0.02917],"force_p95":0.073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08779,"mean_force":0.04146,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46989,0.04681,0.02656]}],"total_contact_groups":10},"final_pose_error":0.02987,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56622,0.23673,0.06459],"final_tcp_position":[0.56728,0.20755,0.26547],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.69134,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":659.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2632.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47974,0.04532,0.08873],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":744.0,"raw_peak_contact_force":0.12263,"subtask_id":"touch_object","tcp_end":[0.47773,0.04758,0.03452],"tcp_start":[0.47974,0.04532,0.08873],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04672,0.02542],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29168,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16296,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10894.0,"raw_peak_contact_force":0.26157,"tcp_end":[0.46986,0.0468,0.02653],"tcp_start":[0.47773,0.04758,0.03452],"tcp_to_object_dist_end":0.01281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.48985,0.04684,0.20477],"object_pos_start":[0.48262,0.04672,0.02542],"object_to_goal_dist_end":0.20557,"object_to_goal_dist_start":0.29168,"object_z_max":0.2043,"peak_contact_force":0.11123,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10810.0,"raw_peak_contact_force":0.69134,"subtask_id":"lift_object","tcp_end":[0.46729,0.04649,0.21186],"tcp_start":[0.46986,0.0468,0.02653],"tcp_to_object_dist_end":0.02365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.56622,0.23673,0.06459],"object_pos_start":[0.48985,0.04684,0.20477],"object_to_goal_dist_end":0.16681,"object_to_goal_dist_start":0.20557,"object_z_max":0.22659,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5514.0,"raw_peak_contact_force":0.29133,"subtask_id":"pre_place","tcp_end":[0.56728,0.20755,0.26547],"tcp_start":[0.46729,0.04649,0.21186],"tcp_to_object_dist_end":0.20298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.56622,0.23673,0.06459],"object_pos_start":[0.56622,0.23673,0.06459],"object_to_goal_dist_end":0.16681,"object_to_goal_dist_start":0.16681,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place","tcp_end":[0.56728,0.20755,0.26547],"tcp_start":[0.56728,0.20755,0.26547],"tcp_to_object_dist_end":0.20298,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```