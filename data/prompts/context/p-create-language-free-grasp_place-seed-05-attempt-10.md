## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1929 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | arc_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 4 | 0.2731 | 0.36 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2054 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2586 | 0.44 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1986 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.193) — your mutation base

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

- **Composite score**: 0.193
- **task_score** (E): 0.290
- **fitness_score**: 0.623  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1087 |
| descend_1 | 1.00 | 1.00 | 0.1575 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 0.67 | 1.00 | 0.1232 |
| transport_1 | 0.00 | 1.00 | 0.0922 |
| descend_place | 0.67 | 1.00 | 0.0776 |
| release_1 | 1.00 | 1.00 | 0.0217 |
| retract_1 | 1.00 | 1.00 | 0.0855 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.016, 0.196) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.016, 0.196)→(0.511, 0.018, 0.039) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.039)→(0.502, 0.018, 0.030) | (0.516, 0.018, 0.026)→(0.515, 0.018, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.140 | 0.202 |
| lift_1 | lift | 0.67 / step_budget | (0.502, 0.018, 0.030)→(0.509, 0.018, 0.153) | (0.515, 0.018, 0.026)→(0.524, 0.018, 0.136) | 0.237→0.196 | 1.00 / 22.333 | 0.124 | 0.594 |
| transport_1 | approach | 0.00 / step_budget | (0.509, 0.018, 0.153)→(0.551, 0.089, 0.184) | (0.524, 0.018, 0.136)→(0.537, 0.076, 0.016) | 0.196→0.199 | 1.00 / 8.667 | 91002.173 | 1.489 |
| descend_place | descend | 0.67 / step_budget | (0.551, 0.089, 0.184)→(0.588, 0.151, 0.210) | (0.537, 0.076, 0.016)→(0.537, 0.076, 0.016) | 0.199→0.199 | 1.00 / 8.000 | 3249.684 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.588, 0.151, 0.210)→(0.583, 0.150, 0.231) | (0.537, 0.076, 0.016)→(0.537, 0.076, 0.016) | 0.199→0.199 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.583, 0.150, 0.231)→(0.581, 0.149, 0.316) | (0.537, 0.076, 0.016)→(0.537, 0.076, 0.016) | 0.199→0.199 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.401
- phase_breakdown.reach_grasp_score: 0.699
- phase_breakdown.reach_place_score: 0.273
- grasp_place_fitness: 0.698

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.698
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.446
- **Median Q (composite search score)**: 0.184
- **K-run variance**: 0.0034
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.309


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59195,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11369,"descend_1.descend_depth":0.02,"descend_place.place_depth":0.0752,"lift_1.lift_height":0.12145,"transport_1.transport_speed":0.03171},"optimized_scores":{"best_composite_score":0.2685,"best_fitness_score":0.6985,"best_task_score":0.44564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":606.0,"contact_point_centroid":[0.56698,0.10709,-0.00338],"force_p95":0.82688,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36752,"mean_force":0.19556,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55342,0.09165,0.15029]},{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.52883,0.0292,-0.00117],"force_p95":0.35253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53725,"mean_force":0.06579,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51593,0.02972,0.03532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10012.0,"contact_point_centroid":[0.52101,0.04846,0.07817],"force_p95":0.10455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29767,"mean_force":0.06509,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51856,0.02956,0.07642]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9696.0,"contact_point_centroid":[0.52148,0.01072,0.08002],"force_p95":0.10233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29657,"mean_force":0.06644,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51875,0.02956,0.0783]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7222.0,"contact_point_centroid":[0.54087,0.03824,0.13751],"force_p95":0.14977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2574,"mean_force":0.09596,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53564,0.05654,0.13856]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03059,-0.00209],"force_p95":0.14819,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21494,"mean_force":0.1295,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51842,0.02992,0.03492]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7771.0,"contact_point_centroid":[0.54144,0.07658,0.13764],"force_p95":0.12741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16202,"mean_force":0.08948,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53649,0.05832,0.13908]},{"body_a":"world","body_b":"grasp_target","contact_count":1972.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51089,0.01372,0.22502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4087.0,"contact_point_centroid":[0.51781,0.01064,0.03631],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13769,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5172,0.02984,0.03353]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56722,0.10756,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12312,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57192,0.13131,0.15854]},{"body_a":"world","body_b":"grasp_target","contact_count":3148.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52356,0.02934,0.08498]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56722,0.10756,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58707,0.16468,0.17198]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.56722,0.10756,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58269,0.16328,0.23243]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4948.0,"contact_point_centroid":[0.5178,0.04895,0.03535],"force_p95":0.07149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08187,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51721,0.02984,0.03353]},{"body_a":"left_finger","body_b":"right_finger","contact_count":348.0,"contact_point_centroid":[0.55485,0.0936,0.15307],"force_p95":0.01434,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01528,"mean_force":0.01128,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55442,0.09359,0.15096]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4210.0,"contact_point_centroid":[0.5724,0.13138,0.16076],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01058,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57195,0.13136,0.15856]}],"total_contact_groups":17},"final_pose_error":0.01486,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56722,0.10756,0.01602],"final_tcp_position":[0.58295,0.16331,0.27711],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.36752,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1972.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52418,0.028,0.15086],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":787.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3148.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52535,0.03038,0.04284],"tcp_start":[0.52418,0.028,0.15086],"tcp_to_object_dist_end":0.0176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02985,0.0257],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18431,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14298,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10835.0,"raw_peak_contact_force":0.21494,"tcp_end":[0.51717,0.02984,0.0335],"tcp_start":[0.52535,0.03038,0.04284],"tcp_to_object_dist_end":0.01536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":635.0,"n_steps_budget":720.0,"object_pos_end":[0.54043,0.02967,0.11834],"object_pos_start":[0.5304,0.02985,0.0257],"object_to_goal_dist_end":0.16129,"object_to_goal_dist_start":0.18431,"object_z_max":0.11823,"peak_contact_force":0.09956,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19861.0,"raw_peak_contact_force":0.53725,"tcp_end":[0.52549,0.02958,0.13451],"tcp_start":[0.51717,0.02984,0.0335],"tcp_to_object_dist_end":0.02201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56722,0.10757,0.01601],"object_pos_start":[0.54043,0.02967,0.11834],"object_to_goal_dist_end":0.12124,"object_to_goal_dist_start":0.16129,"object_z_max":0.12089,"peak_contact_force":0.12314,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15947.0,"raw_peak_contact_force":1.36752,"subtask_id":"reach_place","tcp_end":[0.55559,0.09586,0.15175],"tcp_start":[0.52549,0.02958,0.13451],"tcp_to_object_dist_end":0.13675,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56722,0.10756,0.01602],"object_pos_start":[0.56722,0.10757,0.01601],"object_to_goal_dist_end":0.12123,"object_to_goal_dist_start":0.12124,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8210.0,"raw_peak_contact_force":0.12312,"subtask_id":"reach_place","tcp_end":[0.59116,0.16584,0.1708],"tcp_start":[0.55559,0.09586,0.15175],"tcp_to_object_dist_end":0.16711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56722,0.10756,0.01602],"object_pos_start":[0.56722,0.10756,0.01602],"object_to_goal_dist_end":0.12123,"object_to_goal_dist_start":0.12123,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58549,0.16416,0.19173],"tcp_start":[0.59116,0.16584,0.1708],"tcp_to_object_dist_end":0.18551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.56722,0.10756,0.01602],"object_pos_start":[0.56722,0.10756,0.01602],"object_to_goal_dist_end":0.12123,"object_to_goal_dist_start":0.12123,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58295,0.16331,0.27711],"tcp_start":[0.58549,0.16416,0.19173],"tcp_to_object_dist_end":0.26744,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87582,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18093,"descend_1.descend_depth":0.0123,"descend_place.place_depth":0.02862,"lift_1.lift_height":0.12174,"transport_1.transport_speed":0.0745},"optimized_scores":{"best_composite_score":0.12612,"best_fitness_score":0.55612,"best_task_score":0.15582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":949.0,"contact_point_centroid":[0.53022,0.04364,-0.00296],"force_p95":0.50932,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45641,"mean_force":0.16907,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52281,0.04785,0.18977]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.50232,-0.01533,-0.00109],"force_p95":0.39521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56648,"mean_force":0.0578,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48975,-0.0154,0.03254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10144.0,"contact_point_centroid":[0.49474,0.00363,0.07904],"force_p95":0.10562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30708,"mean_force":0.06645,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49238,-0.0153,0.07709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10792.0,"contact_point_centroid":[0.49483,-0.03414,0.07803],"force_p95":0.10088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.283,"mean_force":0.06313,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49233,-0.0153,0.07652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6936.0,"contact_point_centroid":[0.51056,-0.00808,0.15279],"force_p95":0.14738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2619,"mean_force":0.09086,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50643,0.01024,0.15471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7360.0,"contact_point_centroid":[0.51104,0.02927,0.15339],"force_p95":0.12902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19128,"mean_force":0.08564,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50675,0.01105,0.15542]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01554,-0.00203],"force_p95":0.13155,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15531,"mean_force":0.12523,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49211,-0.01543,0.03202]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49932,-0.0062,0.26061]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53026,0.04364,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53858,0.08905,0.21132]},{"body_a":"world","body_b":"grasp_target","contact_count":3772.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49813,-0.01433,0.12388]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53026,0.04364,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55028,0.12078,0.23255]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.53026,0.04364,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54682,0.1199,0.29437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4113.0,"contact_point_centroid":[0.49136,0.00378,0.03354],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11655,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49093,-0.01542,0.03078]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49144,-0.0345,0.03263],"force_p95":0.0682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0899,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49093,-0.01542,0.03078]},{"body_a":"left_finger","body_b":"right_finger","contact_count":739.0,"contact_point_centroid":[0.52402,0.04993,0.19409],"force_p95":0.01308,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01086,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52374,0.04993,0.19174]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4267.0,"contact_point_centroid":[0.53904,0.08916,0.21361],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01291,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53862,0.08915,0.21138]}],"total_contact_groups":17},"final_pose_error":0.01381,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53026,0.04364,0.01602],"final_tcp_position":[0.54712,0.11994,0.33914],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.45641,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50014,-0.01309,0.21985],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":943.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3772.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49891,-0.01552,0.03925],"tcp_start":[0.50014,-0.01309,0.21985],"tcp_to_object_dist_end":0.01411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01528,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31211,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12952,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15531,"tcp_end":[0.4909,-0.01542,0.03075],"tcp_start":[0.49891,-0.01552,0.03925],"tcp_to_object_dist_end":0.01368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.5149,-0.01508,0.12176],"object_pos_start":[0.50369,-0.01528,0.02588],"object_to_goal_dist_end":0.24934,"object_to_goal_dist_start":0.31211,"object_z_max":0.12165,"peak_contact_force":0.10172,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21074.0,"raw_peak_contact_force":0.56648,"tcp_end":[0.49895,-0.01523,0.13564],"tcp_start":[0.4909,-0.01542,0.03075],"tcp_to_object_dist_end":0.02115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53026,0.04364,0.01602],"object_pos_start":[0.5149,-0.01508,0.12176],"object_to_goal_dist_end":0.27885,"object_to_goal_dist_start":0.24934,"object_z_max":0.15237,"peak_contact_force":0.12264,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15984.0,"raw_peak_contact_force":1.45641,"subtask_id":"reach_place","tcp_end":[0.52621,0.05547,0.19696],"tcp_start":[0.49895,-0.01523,0.13564],"tcp_to_object_dist_end":0.18137,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53026,0.04364,0.01602],"object_pos_start":[0.53026,0.04364,0.01602],"object_to_goal_dist_end":0.27885,"object_to_goal_dist_start":0.27885,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8267.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_place","tcp_end":[0.55362,0.12149,0.23027],"tcp_start":[0.52621,0.05547,0.19696],"tcp_to_object_dist_end":0.22915,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53026,0.04364,0.01602],"object_pos_start":[0.53026,0.04364,0.01602],"object_to_goal_dist_end":0.27885,"object_to_goal_dist_start":0.27885,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54904,0.12045,0.2528],"tcp_start":[0.55362,0.12149,0.23027],"tcp_to_object_dist_end":0.24964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.53026,0.04364,0.01602],"object_pos_start":[0.53026,0.04364,0.01602],"object_to_goal_dist_end":0.27885,"object_to_goal_dist_start":0.27885,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54712,0.11994,0.33914],"tcp_start":[0.54904,0.12045,0.2528],"tcp_to_object_dist_end":0.33243,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8875,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18187,"descend_1.descend_depth":0.00998,"descend_place.place_depth":0.09459,"lift_1.lift_height":0.26961,"transport_1.transport_speed":0.09962},"optimized_scores":{"best_composite_score":0.18403,"best_fitness_score":0.61403,"best_task_score":0.26954},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3585.0,"contact_point_centroid":[0.51434,0.0766,-0.00229],"force_p95":0.1249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.642,"mean_force":0.13483,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54408,0.0852,0.19515]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.50984,0.03743,-0.00118],"force_p95":0.48022,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67696,"mean_force":0.0847,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49799,0.03838,0.02775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":292.0,"contact_point_centroid":[0.50894,0.05754,0.183],"force_p95":0.21131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3223,"mean_force":0.10327,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50536,0.04031,0.18854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14334.0,"contact_point_centroid":[0.50183,0.05693,0.09517],"force_p95":0.12936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31579,"mean_force":0.07197,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49888,0.03817,0.0945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13693.0,"contact_point_centroid":[0.50183,0.01942,0.09669],"force_p95":0.12933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3088,"mean_force":0.07391,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49892,0.03817,0.09582]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.50848,0.02156,0.18344],"force_p95":0.21333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29694,"mean_force":0.12812,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50484,0.0394,0.18884]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03942,-0.00211],"force_p95":0.15553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23721,"mean_force":0.1315,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50063,0.03862,0.02723]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4063.0,"contact_point_centroid":[0.49997,0.01932,0.02874],"force_p95":0.0801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14086,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49943,0.03852,0.02594]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50288,0.01635,0.25922]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50625,0.0367,0.11778]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51431,0.07659,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59461,0.14114,0.21209]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51431,0.07659,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61591,0.16515,0.22786]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.51431,0.07659,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61257,0.16397,0.28726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4976.0,"contact_point_centroid":[0.49996,0.05766,0.02776],"force_p95":0.07257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08993,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49944,0.03852,0.02595]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3531.0,"contact_point_centroid":[0.54675,0.08764,0.19793],"force_p95":0.01109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01488,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54631,0.08762,0.19572]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4279.0,"contact_point_centroid":[0.59514,0.14117,0.21439],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59461,0.14114,0.21209]}],"total_contact_groups":17},"final_pose_error":0.01542,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51431,0.07659,0.01602],"final_tcp_position":[0.61296,0.16403,0.3319],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273006.27289,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50765,0.03399,0.21842],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50749,0.03918,0.03467],"tcp_start":[0.50765,0.03399,0.21842],"tcp_to_object_dist_end":0.01001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03847,0.02563],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21329,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.148,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10839.0,"raw_peak_contact_force":0.23721,"tcp_end":[0.4994,0.03851,0.02591],"tcp_start":[0.50749,0.03918,0.03467],"tcp_to_object_dist_end":0.01299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51593,0.03816,0.16726],"object_pos_start":[0.51239,0.03847,0.02563],"object_to_goal_dist_end":0.1761,"object_to_goal_dist_start":0.21329,"object_z_max":0.1671,"peak_contact_force":0.1698,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28171.0,"raw_peak_contact_force":0.67696,"tcp_end":[0.50383,0.03819,0.18894],"tcp_start":[0.4994,0.03851,0.02591],"tcp_to_object_dist_end":0.02483,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51431,0.07659,0.01602],"object_pos_start":[0.51593,0.03816,0.16726],"object_to_goal_dist_end":0.19666,"object_to_goal_dist_start":0.1761,"object_z_max":0.16733,"peak_contact_force":273006.27289,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7564.0,"raw_peak_contact_force":1.642,"subtask_id":"reach_place","tcp_end":[0.57231,0.1157,0.2026],"tcp_start":[0.50383,0.03819,0.18894],"tcp_to_object_dist_end":0.19926,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51431,0.07659,0.01602],"object_pos_start":[0.51431,0.07659,0.01602],"object_to_goal_dist_end":0.19666,"object_to_goal_dist_start":0.19666,"object_z_max":0.01602,"peak_contact_force":9748.80767,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8279.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.61922,0.16616,0.2275],"tcp_start":[0.57231,0.1157,0.2026],"tcp_to_object_dist_end":0.25249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51431,0.07659,0.01602],"object_pos_start":[0.51431,0.07659,0.01602],"object_to_goal_dist_end":0.19666,"object_to_goal_dist_start":0.19666,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61468,0.16471,0.24721],"tcp_start":[0.61922,0.16616,0.2275],"tcp_to_object_dist_end":0.267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.51431,0.07659,0.01602],"object_pos_start":[0.51431,0.07659,0.01602],"object_to_goal_dist_end":0.19666,"object_to_goal_dist_start":0.19666,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61296,0.16403,0.3319],"tcp_start":[0.61468,0.16471,0.24721],"tcp_to_object_dist_end":0.34229,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```