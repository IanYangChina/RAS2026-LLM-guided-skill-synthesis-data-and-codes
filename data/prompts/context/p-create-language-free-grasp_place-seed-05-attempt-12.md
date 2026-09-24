## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2119 | 0.34 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2533 | 0.43 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1929 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | arc_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 4 | 0.2731 | 0.36 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2054 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
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

## Current Skill (Q=0.212) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: reach_place
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.7
phases:
- id: approach_1
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
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_1
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
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp_1
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
- id: lift_1
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_place
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_depth:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_place
- id: release_1
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
- id: retract_1
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.01
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_depth: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.212
- **task_score** (E): 0.339
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1519 |
| descend_1 | 1.00 | 1.00 | 0.1067 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1040 |
| transport_1 | 0.00 | 1.00 | 0.0890 |
| descend_place | 0.67 | 1.00 | 0.0762 |
| release_1 | 1.00 | 1.00 | 0.0220 |
| retract_1 | 1.00 | 1.00 | 0.0858 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.153) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.016, 0.153)→(0.511, 0.018, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.046)→(0.503, 0.018, 0.037) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 | 1.00 / 43.000 | 0.139 | 0.192 |
| lift_1 | lift | 1.00 / step_budget | (0.503, 0.018, 0.037)→(0.511, 0.018, 0.141) | (0.516, 0.018, 0.026)→(0.525, 0.018, 0.122) | 0.237→0.193 | 1.00 / 23.333 | 0.107 | 0.492 |
| transport_1 | approach | 0.00 / step_budget | (0.511, 0.018, 0.141)→(0.548, 0.087, 0.178) | (0.525, 0.018, 0.122)→(0.554, 0.088, 0.053) | 0.193→0.172 | 1.00 / 12.333 | 3249.658 | 1.132 |
| descend_place | descend | 0.67 / step_budget | (0.548, 0.087, 0.178)→(0.583, 0.146, 0.192) | (0.554, 0.088, 0.053)→(0.560, 0.099, 0.016) | 0.172→0.179 | 1.00 / 8.000 | 6499.152 | 0.560 |
| release_1 | release | 1.00 / step_budget | (0.583, 0.146, 0.192)→(0.578, 0.144, 0.213) | (0.560, 0.099, 0.016)→(0.560, 0.099, 0.016) | 0.179→0.179 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.578, 0.144, 0.213)→(0.576, 0.144, 0.299) | (0.560, 0.099, 0.016)→(0.560, 0.099, 0.016) | 0.179→0.179 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.514
- phase_score: 0.689
- phase_breakdown.reach_grasp_score: 0.822
- phase_breakdown.reach_place_score: 0.632
- grasp_place_fitness: 0.724

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.724
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.514
- **Median Q (composite search score)**: 0.217
- **K-run variance**: 0.0049
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.340


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87075,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1617,"descend_1.descend_depth":0.02867,"descend_place.place_depth":0.06977,"lift_1.lift_height":0.12424,"transport_1.transport_speed":0.07221},"optimized_scores":{"best_composite_score":0.29424,"best_fitness_score":0.72424,"best_task_score":0.51408},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3274.0,"contact_point_centroid":[0.58577,0.14322,-0.00225],"force_p95":0.1303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43379,"mean_force":0.13759,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57989,0.14617,0.16107]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.52907,0.0294,-0.00116],"force_p95":0.27767,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43536,"mean_force":0.05302,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51617,0.02975,0.04414]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9383.0,"contact_point_centroid":[0.52155,0.01078,0.08627],"force_p95":0.10031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28644,"mean_force":0.06516,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51894,0.02962,0.08453]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9513.0,"contact_point_centroid":[0.52103,0.04855,0.08432],"force_p95":0.10358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28387,"mean_force":0.06491,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51872,0.02962,0.08247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":676.0,"contact_point_centroid":[0.5681,0.09485,0.15219],"force_p95":0.19593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24954,"mean_force":0.1239,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56282,0.11311,0.15529]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03063,-0.00208],"force_p95":0.14529,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2009,"mean_force":0.12875,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5186,0.02993,0.04371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.56888,0.13102,0.15234],"force_p95":0.13228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18437,"mean_force":0.08826,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56293,0.11361,0.1551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11846.0,"contact_point_centroid":[0.54983,0.05393,0.14706],"force_p95":0.11098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15971,"mean_force":0.07812,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54381,0.07262,0.14596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12773.0,"contact_point_centroid":[0.55058,0.09255,0.14716],"force_p95":0.0946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14225,"mean_force":0.07248,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54448,0.07395,0.14638]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51068,0.0132,0.24864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.51793,0.01065,0.04512],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13817,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51739,0.02986,0.04232]},{"body_a":"world","body_b":"grasp_target","contact_count":3436.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52341,0.02891,0.11371]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58585,0.14339,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58983,0.16967,0.16888]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.58585,0.14339,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5854,0.16821,0.2292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4937.0,"contact_point_centroid":[0.51794,0.04896,0.04414],"force_p95":0.07122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07704,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5174,0.02986,0.04232]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3186.0,"contact_point_centroid":[0.58138,0.14803,0.16379],"force_p95":0.01133,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01067,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58094,0.14801,0.16157]}],"total_contact_groups":17},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58585,0.14339,0.01602],"final_tcp_position":[0.58566,0.16825,0.27387],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.8577,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52373,0.02716,0.19786],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3436.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52543,0.03039,0.05166],"tcp_start":[0.52373,0.02716,0.19786],"tcp_to_object_dist_end":0.02614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02995,0.02572],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18421,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14114,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10832.0,"raw_peak_contact_force":0.2009,"tcp_end":[0.51736,0.02985,0.04229],"tcp_start":[0.52543,0.03039,0.05166],"tcp_to_object_dist_end":0.0211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53827,0.0298,0.1142],"object_pos_start":[0.53043,0.02995,0.02572],"object_to_goal_dist_end":0.16178,"object_to_goal_dist_start":0.18421,"object_z_max":0.11409,"peak_contact_force":0.0978,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19046.0,"raw_peak_contact_force":0.43536,"tcp_end":[0.52551,0.02967,0.13738],"tcp_start":[0.51736,0.02985,0.04229],"tcp_to_object_dist_end":0.02646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56824,0.1096,0.12692],"object_pos_start":[0.53827,0.0298,0.1142],"object_to_goal_dist_end":0.07887,"object_to_goal_dist_start":0.16178,"object_z_max":0.12691,"peak_contact_force":0.15234,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24619.0,"raw_peak_contact_force":0.15971,"subtask_id":"reach_place","tcp_end":[0.56283,0.10987,0.15784],"tcp_start":[0.52551,0.02967,0.13738],"tcp_to_object_dist_end":0.03139,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58585,0.14339,0.01602],"object_pos_start":[0.56824,0.1096,0.12692],"object_to_goal_dist_end":0.09981,"object_to_goal_dist_start":0.07887,"object_z_max":0.12692,"peak_contact_force":9748.8577,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8144.0,"raw_peak_contact_force":1.43379,"subtask_id":"reach_place","tcp_end":[0.59395,0.17088,0.16781],"tcp_start":[0.56283,0.10987,0.15784],"tcp_to_object_dist_end":0.15448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58585,0.14339,0.01602],"object_pos_start":[0.58585,0.14339,0.01602],"object_to_goal_dist_end":0.09981,"object_to_goal_dist_start":0.09981,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58823,0.16913,0.18858],"tcp_start":[0.59395,0.17088,0.16781],"tcp_to_object_dist_end":0.17449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.58585,0.14339,0.01602],"object_pos_start":[0.58585,0.14339,0.01602],"object_to_goal_dist_end":0.09981,"object_to_goal_dist_start":0.09981,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58566,0.16825,0.27387],"tcp_start":[0.58823,0.16913,0.18858],"tcp_to_object_dist_end":0.25905,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76687,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05408,"descend_1.descend_depth":0.0221,"descend_place.place_depth":0.09266,"lift_1.lift_height":0.1369,"transport_1.transport_speed":0.07579},"optimized_scores":{"best_composite_score":0.12383,"best_fitness_score":0.55383,"best_task_score":0.15933},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.53451,0.04849,-0.00298],"force_p95":0.50973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75838,"mean_force":0.16707,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52429,0.05055,0.20257]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.50207,-0.01521,-0.00109],"force_p95":0.3531,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50565,"mean_force":0.05526,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48986,-0.01544,0.03803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10856.0,"contact_point_centroid":[0.49499,0.00351,0.08821],"force_p95":0.10542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2879,"mean_force":0.06718,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49245,-0.01539,0.08623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11411.0,"contact_point_centroid":[0.49505,-0.03425,0.08716],"force_p95":0.10108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27823,"mean_force":0.06448,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4924,-0.0154,0.08555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6039.0,"contact_point_centroid":[0.51241,-0.00795,0.16649],"force_p95":0.1347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23262,"mean_force":0.09915,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50685,0.01032,0.16816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6239.0,"contact_point_centroid":[0.51261,0.02914,0.1668],"force_p95":0.12756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18724,"mean_force":0.09564,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50708,0.0109,0.16861]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01562,-0.00203],"force_p95":0.13064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15552,"mean_force":0.12504,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49224,-0.01547,0.03751]},{"body_a":"world","body_b":"grasp_target","contact_count":2532.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49867,-0.00719,0.19594]},{"body_a":"world","body_b":"grasp_target","contact_count":2548.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49783,-0.0152,0.06027]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53458,0.04851,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53824,0.08751,0.23318]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53458,0.04851,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54814,0.11443,0.26299]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.53458,0.04851,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54515,0.11367,0.32494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.49095,0.00379,0.03942],"force_p95":0.06552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09187,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49106,-0.01545,0.03626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5364.0,"contact_point_centroid":[0.49082,-0.0347,0.03893],"force_p95":0.06375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08094,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49107,-0.01545,0.03626]},{"body_a":"left_finger","body_b":"right_finger","contact_count":826.0,"contact_point_centroid":[0.52548,0.05253,0.20647],"force_p95":0.01305,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.01074,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52517,0.05253,0.20429]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4290.0,"contact_point_centroid":[0.53861,0.0874,0.23537],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53819,0.08739,0.23306]}],"total_contact_groups":17},"final_pose_error":0.01339,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53458,0.04851,0.01602],"final_tcp_position":[0.54551,0.11371,0.36996],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.69923,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":634.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2532.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49944,-0.01459,0.09283],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2548.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49886,-0.01556,0.04463],"tcp_start":[0.49944,-0.01459,0.09283],"tcp_to_object_dist_end":0.01926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01547,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12987,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12255.0,"raw_peak_contact_force":0.15552,"tcp_end":[0.49104,-0.01545,0.03623],"tcp_start":[0.49886,-0.01556,0.04463],"tcp_to_object_dist_end":0.01636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.51308,-0.01536,0.13179],"object_pos_start":[0.50371,-0.01547,0.02588],"object_to_goal_dist_end":0.24518,"object_to_goal_dist_start":0.31223,"object_z_max":0.13168,"peak_contact_force":0.11005,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22405.0,"raw_peak_contact_force":0.50565,"tcp_end":[0.49914,-0.0154,0.15075],"tcp_start":[0.49104,-0.01545,0.03623],"tcp_to_object_dist_end":0.02353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53458,0.04851,0.01602],"object_pos_start":[0.51308,-0.01536,0.13179],"object_to_goal_dist_end":0.27552,"object_to_goal_dist_start":0.24518,"object_z_max":0.16224,"peak_contact_force":9748.69923,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14112.0,"raw_peak_contact_force":1.75838,"subtask_id":"reach_place","tcp_end":[0.52807,0.05907,0.20996],"tcp_start":[0.49914,-0.0154,0.15075],"tcp_to_object_dist_end":0.19434,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53458,0.04851,0.01602],"object_pos_start":[0.53458,0.04851,0.01602],"object_to_goal_dist_end":0.27552,"object_to_goal_dist_start":0.27552,"object_z_max":0.01602,"peak_contact_force":9748.47467,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8290.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.55107,0.11504,0.26065],"tcp_start":[0.52807,0.05907,0.20996],"tcp_to_object_dist_end":0.25405,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53458,0.04851,0.01602],"object_pos_start":[0.53458,0.04851,0.01602],"object_to_goal_dist_end":0.27552,"object_to_goal_dist_start":0.27552,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54707,0.11414,0.28325],"tcp_start":[0.55107,0.11504,0.26065],"tcp_to_object_dist_end":0.27545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.53458,0.04851,0.01602],"object_pos_start":[0.53458,0.04851,0.01602],"object_to_goal_dist_end":0.27552,"object_to_goal_dist_start":0.27552,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54551,0.11371,0.36996],"tcp_start":[0.54707,0.11414,0.28325],"tcp_to_object_dist_end":0.36006,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78912,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13029,"descend_1.descend_depth":0.01892,"descend_place.place_depth":0.00604,"lift_1.lift_height":0.12177,"transport_1.transport_speed":0.06856},"optimized_scores":{"best_composite_score":0.21748,"best_fitness_score":0.64748,"best_task_score":0.3431},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":773.0,"contact_point_centroid":[0.55884,0.10492,-0.00304],"force_p95":0.77274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47825,"mean_force":0.1885,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5488,0.08821,0.16232]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.51095,0.03788,-0.00117],"force_p95":0.36229,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53602,"mean_force":0.06211,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49836,0.03843,0.03557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10156.0,"contact_point_centroid":[0.50312,0.05719,0.0787],"force_p95":0.10478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29874,"mean_force":0.06427,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50089,0.03825,0.07691]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9989.0,"contact_point_centroid":[0.50368,0.0194,0.08103],"force_p95":0.1,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29654,"mean_force":0.0646,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50113,0.03824,0.07929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7128.0,"contact_point_centroid":[0.5291,0.07859,0.14352],"force_p95":0.13604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23456,"mean_force":0.09103,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5239,0.06029,0.14456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6762.0,"contact_point_centroid":[0.52837,0.04086,0.14327],"force_p95":0.15116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22417,"mean_force":0.09557,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52297,0.05919,0.14392]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03949,-0.0021],"force_p95":0.15249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22003,"mean_force":0.13059,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50076,0.03866,0.03503]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.50005,0.01936,0.03654],"force_p95":0.07976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1435,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49957,0.03856,0.03373]},{"body_a":"world","body_b":"grasp_target","contact_count":1720.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50284,0.01738,0.23386]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55888,0.10629,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12266,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57744,0.12224,0.15263]},{"body_a":"world","body_b":"grasp_target","contact_count":2924.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50624,0.03752,0.09769]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55888,0.10629,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6,0.15007,0.14727]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.55888,0.10629,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59515,0.14868,0.20745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.50006,0.0577,0.03555],"force_p95":0.07235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0823,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49958,0.03856,0.03374]},{"body_a":"left_finger","body_b":"right_finger","contact_count":582.0,"contact_point_centroid":[0.55055,0.08949,0.16524],"force_p95":0.01359,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01102,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54995,0.08947,0.16314]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4248.0,"contact_point_centroid":[0.57792,0.12228,0.15491],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57746,0.12226,0.15262]}],"total_contact_groups":17},"final_pose_error":0.01511,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.55888,0.10629,0.01602],"final_tcp_position":[0.59539,0.1487,0.25211],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.47825,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1720.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50775,0.03569,0.16793],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2924.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.5075,0.03922,0.04244],"tcp_start":[0.50775,0.03569,0.16793],"tcp_to_object_dist_end":0.01718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03862,0.02565],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21317,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14632,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10847.0,"raw_peak_contact_force":0.22003,"tcp_end":[0.49954,0.03856,0.0337],"tcp_start":[0.5075,0.03922,0.04244],"tcp_to_object_dist_end":0.01519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":634.0,"n_steps_budget":720.0,"object_pos_end":[0.52258,0.03842,0.1191],"object_pos_start":[0.51242,0.03862,0.02565],"object_to_goal_dist_end":0.17228,"object_to_goal_dist_start":0.21317,"object_z_max":0.11899,"peak_contact_force":0.11459,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20291.0,"raw_peak_contact_force":0.53602,"tcp_end":[0.50761,0.03829,0.13514],"tcp_start":[0.49954,0.03856,0.0337],"tcp_to_object_dist_end":0.02194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55888,0.10628,0.01602],"object_pos_start":[0.52258,0.03842,0.1191],"object_to_goal_dist_end":0.16046,"object_to_goal_dist_start":0.17228,"object_z_max":0.13058,"peak_contact_force":0.12264,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15245.0,"raw_peak_contact_force":1.47825,"subtask_id":"reach_place","tcp_end":[0.5527,0.09252,0.16512],"tcp_start":[0.50761,0.03829,0.13514],"tcp_to_object_dist_end":0.14986,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55888,0.10629,0.01602],"object_pos_start":[0.55888,0.10628,0.01602],"object_to_goal_dist_end":0.16046,"object_to_goal_dist_start":0.16046,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8248.0,"raw_peak_contact_force":0.12266,"subtask_id":"reach_place","tcp_end":[0.60447,0.15122,0.14636],"tcp_start":[0.5527,0.09252,0.16512],"tcp_to_object_dist_end":0.14521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55888,0.10629,0.01602],"object_pos_start":[0.55888,0.10629,0.01602],"object_to_goal_dist_end":0.16046,"object_to_goal_dist_start":0.16046,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59825,0.14955,0.16692],"tcp_start":[0.60447,0.15122,0.14636],"tcp_to_object_dist_end":0.16184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.55888,0.10629,0.01602],"object_pos_start":[0.55888,0.10629,0.01602],"object_to_goal_dist_end":0.16046,"object_to_goal_dist_start":0.16046,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59539,0.1487,0.25211],"tcp_start":[0.59825,0.14955,0.16692],"tcp_to_object_dist_end":0.24264,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```