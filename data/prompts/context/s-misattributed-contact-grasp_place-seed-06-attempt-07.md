## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2166 | 0.28 | ✅ accepted |
| 6 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ❌ rejected |
| 5 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |
| 4 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ❌ rejected |
| 3 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1415 | 0.25 | ✅ accepted |

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

## Current Skill (Q=0.217) — your mutation base

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
  metric: goal_progress
  weight: 0.3
- id: reach_goal
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
    - 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    - 0.02
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: grasp_object
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_object
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
    - 0.2
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
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: lift_object
- id: transport_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **transport_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.217
- **task_score** (E): 0.279
- **fitness_score**: 0.617  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1464 |
| descend_to_grasp | 1.00 | 1.00 | 0.1217 |
| grasp_object | 1.00 | 1.00 | 0.0125 |
| lift_object | 0.33 | 1.00 | 0.1624 |
| transport_to_goal | 0.33 | 1.00 | 0.1568 |
| release_object | 1.00 | 1.00 | 0.0228 |
| retract | 0.33 | 1.00 | 0.1393 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.159) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.022, 0.159)→(0.494, 0.024, 0.037) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 42.333 | 0.153 | 0.209 |
| grasp_object | grasp | 1.00 / step_budget | (0.494, 0.024, 0.037)→(0.486, 0.023, 0.028) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 34.000 | 0.109 | 0.718 |
| lift_object | lift | 0.33 / step_budget | (0.486, 0.023, 0.028)→(0.482, 0.023, 0.190) | (0.500, 0.023, 0.026)→(0.494, 0.023, 0.177) | 0.272→0.211 | 1.00 / 34.333 | 0.097 | 0.150 |
| transport_to_goal | push | 0.33 / step_budget | (0.482, 0.023, 0.190)→(0.560, 0.137, 0.258) | (0.494, 0.023, 0.177)→(0.565, 0.139, 0.238) | 0.211→0.081 | 1.00 / 4.000 | 0.421 | 1.974 |
| release_object | release | 1.00 / step_budget | (0.560, 0.137, 0.258)→(0.556, 0.136, 0.280) | (0.565, 0.139, 0.238)→(0.550, 0.152, 0.006) | 0.081→0.214 | 1.00 / 4.000 | 27.129 | 0.411 |
| retract | retract | 0.33 / step_budget | (0.556, 0.136, 0.280)→(0.555, 0.136, 0.419) | (0.550, 0.152, 0.006)→(0.549, 0.155, 0.019) | 0.214→0.201 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.425
- phase_score: 0.176
- phase_breakdown.reach_goal_score: 0.166
- phase_breakdown.lift_object_score: 0.136
- phase_breakdown.reach_object_score: 0.265
- grasp_place_fitness: 0.688

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.688
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.425
- **Median Q (composite search score)**: 0.188
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.483


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90446,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14403,"descend_to_grasp.descend_offset":0.00023,"lift_object.lift_height":0.22412,"retract.retract_height":0.10938,"transport_to_goal.transport_speed":0.09964},"optimized_scores":{"best_composite_score":0.17427,"best_fitness_score":0.57427,"best_task_score":0.19231},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.55016,0.10943,-0.01057],"force_p95":1.74156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.23989,"mean_force":0.7313,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54077,0.1063,0.29715]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.50017,-0.01516,-0.0011],"force_p95":0.51662,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76362,"mean_force":0.1065,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48844,-0.01541,0.02719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17592.0,"contact_point_centroid":[0.48681,-0.03455,0.10793],"force_p95":0.08133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33728,"mean_force":0.05753,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48583,-0.01537,0.10545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20246.0,"contact_point_centroid":[0.48754,0.00362,0.10548],"force_p95":0.0765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33304,"mean_force":0.05131,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48584,-0.01537,0.10383]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.55274,0.10925,-0.00215],"force_p95":0.12408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20427,"mean_force":0.11918,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.53899,0.10594,0.34824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":828.0,"contact_point_centroid":[0.54237,0.12625,0.27815],"force_p95":0.09438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18129,"mean_force":0.06228,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54336,0.10697,0.27594]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01575,-0.00203],"force_p95":0.13274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15808,"mean_force":0.12509,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4912,-0.01543,0.02675]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.54832,0.08879,0.27582],"force_p95":0.07245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14804,"mean_force":0.04466,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54339,0.10698,0.27601]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49895,-0.00668,0.24185]},{"body_a":"world","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49789,-0.01464,0.10803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15460.0,"contact_point_centroid":[0.51351,0.06286,0.23122],"force_p95":0.09051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11882,"mean_force":0.06317,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.51278,0.04385,0.22988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16758.0,"contact_point_centroid":[0.51808,0.02871,0.23327],"force_p95":0.08587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11273,"mean_force":0.05893,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.51452,0.04731,0.23255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4148.0,"contact_point_centroid":[0.48946,-0.03469,0.02807],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09441,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48996,-0.01541,0.02546]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5325.0,"contact_point_centroid":[0.49075,0.00364,0.02741],"force_p95":0.06667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09377,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48996,-0.01541,0.02546]}],"total_contact_groups":14},"final_pose_error":0.0133,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55273,0.10924,0.01602],"final_tcp_position":[0.53931,0.10599,0.39783],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.23989,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1840.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49983,-0.01384,0.18291],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13287,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.15808,"tcp_end":[0.49861,-0.01548,0.03459],"tcp_start":[0.49983,-0.01384,0.18291],"tcp_to_object_dist_end":0.01003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50366,-0.01576,0.02589],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31242,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.09317,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":37969.0,"raw_peak_contact_force":0.76362,"tcp_end":[0.48993,-0.01541,0.02542],"tcp_start":[0.49861,-0.01548,0.03459],"tcp_to_object_dist_end":0.01374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49802,-0.01578,0.1784],"object_pos_start":[0.50366,-0.01576,0.02589],"object_to_goal_dist_end":0.23252,"object_to_goal_dist_start":0.31242,"object_z_max":0.17821,"peak_contact_force":0.09334,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32218.0,"raw_peak_contact_force":0.11882,"subtask_id":"lift_object","tcp_end":[0.48628,-0.01536,0.18889],"tcp_start":[0.48993,-0.01541,0.02542],"tcp_to_object_dist_end":0.01575,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55313,0.10923,0.26171],"object_pos_start":[0.49802,-0.01578,0.1784],"object_to_goal_dist_end":0.08627,"object_to_goal_dist_start":0.23252,"object_z_max":0.2616,"peak_contact_force":0.22536,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2115.0,"raw_peak_contact_force":2.23989,"subtask_id":"reach_goal","tcp_end":[0.54452,0.10694,0.27857],"tcp_start":[0.48628,-0.01536,0.18889],"tcp_to_object_dist_end":0.01907,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55168,0.1071,0.00012],"object_pos_start":[0.55313,0.10923,0.26171],"object_to_goal_dist_end":0.26305,"object_to_goal_dist_start":0.08627,"object_z_max":0.26174,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.20427,"tcp_end":[0.54073,0.1063,0.30167],"tcp_start":[0.54452,0.10694,0.27857],"tcp_to_object_dist_end":0.30174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.55273,0.10924,0.01602],"object_pos_start":[0.55168,0.1071,0.00012],"object_to_goal_dist_end":0.24729,"object_to_goal_dist_start":0.26305,"object_z_max":0.01679,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53931,0.10599,0.39783],"tcp_start":[0.54073,0.1063,0.30167],"tcp_to_object_dist_end":0.38206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91176,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.15898,"descend_to_grasp.descend_offset":0.00766,"lift_object.lift_height":0.29517,"retract.retract_height":0.22739,"transport_to_goal.transport_speed":0.09852},"optimized_scores":{"best_composite_score":0.28787,"best_fitness_score":0.68787,"best_task_score":0.42504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.58739,0.14625,-0.00813],"force_p95":1.16323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58738,"mean_force":0.39918,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59968,0.15013,0.24299]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.50927,0.03747,-0.00122],"force_p95":0.36828,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64139,"mean_force":0.09268,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49705,0.03808,0.0346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16861.0,"contact_point_centroid":[0.49538,0.05711,0.11271],"force_p95":0.11088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34517,"mean_force":0.0625,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49458,0.03789,0.11059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20474.0,"contact_point_centroid":[0.49677,0.01925,0.11225],"force_p95":0.08499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32087,"mean_force":0.04988,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49459,0.03789,0.11075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1270.0,"contact_point_centroid":[0.59782,0.16959,0.2288],"force_p95":0.07495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24695,"mean_force":0.04214,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60298,0.15114,0.2261]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03968,-0.00213],"force_p95":0.1601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21974,"mean_force":0.13242,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49992,0.03832,0.03404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1339.0,"contact_point_centroid":[0.60646,0.1321,0.22674],"force_p95":0.07355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20823,"mean_force":0.04025,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60297,0.15114,0.22608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5027.0,"contact_point_centroid":[0.50034,0.01922,0.03418],"force_p95":0.07368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17783,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49868,0.03822,0.03269]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17376.0,"contact_point_centroid":[0.55096,0.11841,0.21353],"force_p95":0.10198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1776,"mean_force":0.05814,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.553,0.09946,0.21088]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21269.0,"contact_point_centroid":[0.5525,0.0772,0.21113],"force_p95":0.08295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16256,"mean_force":0.04763,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.54952,0.09592,0.20966]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58735,0.14626,-0.00199],"force_p95":0.12411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14348,"mean_force":0.12138,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59772,0.14958,0.3279]},{"body_a":"world","body_b":"grasp_target","contact_count":1400.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50276,0.0169,0.248]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50617,0.03679,0.11851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4223.0,"contact_point_centroid":[0.49895,0.05753,0.03543],"force_p95":0.08345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09085,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49869,0.03822,0.0327]}],"total_contact_groups":14},"final_pose_error":0.06755,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.58735,0.14626,0.02602],"final_tcp_position":[0.59849,0.14974,0.41007],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50766,0.03489,0.19612],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15755,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11050.0,"raw_peak_contact_force":0.21974,"tcp_end":[0.50729,0.03891,0.04215],"tcp_start":[0.50766,0.03489,0.19612],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.03885,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21304,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.11697,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":37480.0,"raw_peak_contact_force":0.64139,"tcp_end":[0.49866,0.03822,0.03266],"tcp_start":[0.50729,0.03891,0.04215],"tcp_to_object_dist_end":0.01557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50551,0.03849,0.17711],"object_pos_start":[0.51249,0.03885,0.02554],"object_to_goal_dist_end":0.1841,"object_to_goal_dist_start":0.21304,"object_z_max":0.17692,"peak_contact_force":0.07603,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38645.0,"raw_peak_contact_force":0.1776,"subtask_id":"lift_object","tcp_end":[0.49505,0.03793,0.19388],"tcp_start":[0.49866,0.03822,0.03266],"tcp_to_object_dist_end":0.01978,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60145,0.15159,0.20635],"object_pos_start":[0.50551,0.03849,0.17711],"object_to_goal_dist_end":0.06986,"object_to_goal_dist_start":0.1841,"object_z_max":0.20631,"peak_contact_force":0.0987,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2797.0,"raw_peak_contact_force":1.58738,"subtask_id":"reach_goal","tcp_end":[0.60432,0.15126,0.22926],"tcp_start":[0.49505,0.03793,0.19388],"tcp_to_object_dist_end":0.02309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59125,0.14766,0.02175],"object_pos_start":[0.60145,0.15159,0.20635],"object_to_goal_dist_end":0.1309,"object_to_goal_dist_start":0.06986,"object_z_max":0.20635,"peak_contact_force":81.14225,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.14348,"tcp_end":[0.59964,0.15013,0.25021],"tcp_start":[0.60432,0.15126,0.22926],"tcp_to_object_dist_end":0.22863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58735,0.14626,0.02602],"object_pos_start":[0.59125,0.14766,0.02175],"object_to_goal_dist_end":0.12833,"object_to_goal_dist_start":0.1309,"object_z_max":0.02677,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1400.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.59849,0.14974,0.41007],"tcp_start":[0.59964,0.15013,0.25021],"tcp_to_object_dist_end":0.38422,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90909,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.05831,"descend_to_grasp.descend_offset":1e-05,"lift_object.lift_height":0.20727,"retract.retract_height":0.23835,"transport_to_goal.transport_speed":0.09078},"optimized_scores":{"best_composite_score":0.18761,"best_fitness_score":0.58761,"best_task_score":0.2192},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":53.0,"contact_point_centroid":[0.51721,0.20434,-0.0103],"force_p95":1.97419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09567,"mean_force":1.16613,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52691,0.15152,0.2853]},{"body_a":"world","body_b":"grasp_target","contact_count":3993.0,"contact_point_centroid":[0.50767,0.2108,-0.00218],"force_p95":0.1239,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88668,"mean_force":0.12522,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52529,0.15103,0.36759]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.47919,0.04539,-0.00126],"force_p95":0.48579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74825,"mean_force":0.10595,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46738,0.04662,0.02791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17008.0,"contact_point_centroid":[0.46544,0.06564,0.10644],"force_p95":0.11064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33776,"mean_force":0.06143,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46491,0.04639,0.10447]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20578.0,"contact_point_centroid":[0.46748,0.02781,0.10609],"force_p95":0.0863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31371,"mean_force":0.0499,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46492,0.04639,0.1047]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48281,0.04856,-0.00218],"force_p95":0.1734,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24972,"mean_force":0.1361,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47016,0.0469,0.0271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":933.0,"contact_point_centroid":[0.52826,0.17278,0.26031],"force_p95":0.19768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24296,"mean_force":0.09446,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52916,0.15228,0.26165]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4980.0,"contact_point_centroid":[0.471,0.02782,0.02717],"force_p95":0.07944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19704,"mean_force":0.04318,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46895,0.04679,0.02589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":859.0,"contact_point_centroid":[0.53744,0.13562,0.26189],"force_p95":0.10338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18687,"mean_force":0.05521,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52967,0.15246,0.26243]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12361.0,"contact_point_centroid":[0.49628,0.1178,0.2246],"force_p95":0.1201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15248,"mean_force":0.08063,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.49591,0.09845,0.22365]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17557.0,"contact_point_centroid":[0.50042,0.07986,0.22334],"force_p95":0.09378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14762,"mean_force":0.05512,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"push","tcp_position_centroid":[0.49538,0.09763,0.22302]},{"body_a":"world","body_b":"grasp_target","contact_count":2532.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48882,0.02221,0.19816]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47731,0.04625,0.06554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4265.0,"contact_point_centroid":[0.46905,0.06615,0.02844],"force_p95":0.08544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09985,"mean_force":0.05203,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46895,0.04679,0.0259]}],"total_contact_groups":14},"final_pose_error":0.07643,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50764,0.21081,0.01602],"final_tcp_position":[0.52601,0.15121,0.45006],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.09567,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":634.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":824.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47959,0.04514,0.09704],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16907,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11045.0,"raw_peak_contact_force":0.24972,"tcp_end":[0.47737,0.04759,0.03441],"tcp_start":[0.47959,0.04514,0.09704],"tcp_to_object_dist_end":0.01001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04734,0.02539],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29128,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.11775,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":37726.0,"raw_peak_contact_force":0.74825,"tcp_end":[0.46892,0.04678,0.02586],"tcp_start":[0.47737,0.04759,0.03441],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47742,0.04726,0.17633],"object_pos_start":[0.48271,0.04734,0.02539],"object_to_goal_dist_end":0.21638,"object_to_goal_dist_start":0.29128,"object_z_max":0.17614,"peak_contact_force":0.1208,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29918.0,"raw_peak_contact_force":0.15248,"subtask_id":"lift_object","tcp_end":[0.46533,0.04643,0.18812],"tcp_start":[0.46892,0.04678,0.02586],"tcp_to_object_dist_end":0.0169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54062,0.15509,0.24633],"object_pos_start":[0.47742,0.04726,0.17633],"object_to_goal_dist_end":0.08599,"object_to_goal_dist_start":0.21638,"object_z_max":0.24625,"peak_contact_force":0.9379,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1845.0,"raw_peak_contact_force":2.09567,"subtask_id":"reach_goal","tcp_end":[0.53083,0.15257,0.2649],"tcp_start":[0.46533,0.04643,0.18812],"tcp_to_object_dist_end":0.02114,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5078,0.20253,-0.00536],"object_pos_start":[0.54062,0.15509,0.24633],"object_to_goal_dist_end":0.2486,"object_to_goal_dist_start":0.08599,"object_z_max":0.24634,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3993.0,"raw_peak_contact_force":0.88668,"tcp_end":[0.52689,0.15152,0.28813],"tcp_start":[0.53083,0.15257,0.2649],"tcp_to_object_dist_end":0.29851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50764,0.21081,0.01602],"object_pos_start":[0.5078,0.20253,-0.00536],"object_to_goal_dist_end":0.22767,"object_to_goal_dist_start":0.2486,"object_z_max":0.01712,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2532.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52601,0.15121,0.45006],"tcp_start":[0.52689,0.15152,0.28813],"tcp_to_object_dist_end":0.4385,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```