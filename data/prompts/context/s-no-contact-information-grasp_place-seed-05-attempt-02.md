## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1692 | 0.39 | ✅ accepted |
| 1 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.169) — your mutation base

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
  - 0.03
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.06
  weight: 0.3
- id: place_done
  target_entity: object
  metric: goal_progress
  weight: 0.4
phases:
- id: approach_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_1
  type: grasp
  control: impedance_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 20.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_1
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
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: approach_goal
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_goal
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.06
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_goal_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: release_goal
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.03
    orientation:
      mode: keep_current
  subtask_id: place_done
- id: retract_goal
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_goal_height:
      type: scalar
      range:
      - 0.2
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_done

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - grip_force: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.06], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_goal_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_goal** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_goal** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_goal_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.169
- **task_score** (E): 0.392
- **fitness_score**: 0.661  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1051 |
| descend_to_grasp | 1.00 | 0.1462 |
| grasp_1 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 0.1432 |
| approach_goal | 1.00 | 0.2187 |
| descend_to_goal | 1.00 | 0.0459 |
| release_goal | 1.00 | 0.0200 |
| retract_goal | 0.67 | 0.1897 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.015, 0.199) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.015, 0.199)→(0.511, 0.018, 0.053) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.053)→(0.502, 0.017, 0.044) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.044)→(0.499, 0.017, 0.187) | (0.516, 0.018, 0.026)→(0.512, 0.017, 0.164) | 0.237→0.198 |
| approach_goal | approach | 1.00 / step_budget | (0.499, 0.017, 0.187)→(0.597, 0.170, 0.304) | (0.512, 0.017, 0.164)→(0.602, 0.147, 0.097) | 0.198→0.150 |
| descend_to_goal | descend | 1.00 / step_budget | (0.597, 0.170, 0.304)→(0.600, 0.175, 0.259) | (0.602, 0.147, 0.097)→(0.603, 0.148, 0.085) | 0.150→0.138 |
| release_goal | release | 1.00 / step_budget | (0.600, 0.175, 0.259)→(0.596, 0.174, 0.278) | (0.603, 0.148, 0.085)→(0.600, 0.147, 0.015) | 0.138→0.157 |
| retract_goal | retract | 0.67 / step_budget | (0.596, 0.174, 0.278)→(0.606, 0.179, 0.468) | (0.600, 0.147, 0.015)→(0.595, 0.148, 0.019) | 0.157→0.153 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.532
- phase_score: 0.372
- phase_breakdown.reach_object_score: 0.873
- phase_breakdown.reach_goal_score: 0.367
- phase_breakdown.place_done_score: 0.000
- grasp_place_fitness: 0.728

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.728
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.532
- **Median Q (composite search score)**: -0.139
- **K-run variance**: 0.0049
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.374


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81188,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.16506,"approach_goal.approach_goal_speed":0.08079,"approach_object.approach_height":0.15732,"approach_object.approach_speed":0.09548,"descend_to_goal.descend_goal_speed":0.07893,"descend_to_goal.place_z_offset":0.09668,"descend_to_grasp.descend_speed":0.09191,"descend_to_grasp.grasp_offset_z":0.01635,"grasp_1.grip_force":25.17636,"lift_1.lift_height":0.15904,"lift_1.lift_speed":0.09806,"retract_goal.retract_goal_height":0.31372,"retract_goal.retract_speed":0.11518},"optimized_scores":{"best_composite_score":-0.10228,"best_fitness_score":0.72772,"best_task_score":0.53208},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":445.0,"contact_point_centroid":[0.59726,0.15706,-0.00467],"force_p95":0.9424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93295,"mean_force":0.2311,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58527,0.15493,0.25201]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.52849,0.02867,-0.00144],"force_p95":0.40458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47054,"mean_force":0.08678,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51526,0.0291,0.04777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7092.0,"contact_point_centroid":[0.51627,0.04777,0.10694],"force_p95":0.11073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28921,"mean_force":0.07047,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5129,0.02894,0.10555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3874.0,"contact_point_centroid":[0.54067,0.05058,0.20271],"force_p95":0.13762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28392,"mean_force":0.0875,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53451,0.06911,0.2042]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6439.0,"contact_point_centroid":[0.51592,0.01005,0.10883],"force_p95":0.11411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28155,"mean_force":0.07491,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51287,0.02894,0.10786]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03068,-0.00214],"force_p95":0.16082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21912,"mean_force":0.13267,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51778,0.02927,0.04763]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4031.0,"contact_point_centroid":[0.54185,0.08958,0.20372],"force_p95":0.12558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16947,"mean_force":0.08379,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53572,0.07118,0.20532]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.5305,0.03079,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50998,0.01165,0.25318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4334.0,"contact_point_centroid":[0.51715,0.00994,0.04788],"force_p95":0.07747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13804,"mean_force":0.04967,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51661,0.0292,0.04627]},{"body_a":"world","body_b":"grasp_target","contact_count":400.0,"contact_point_centroid":[0.59746,0.15704,-0.00199],"force_p95":0.12463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1249,"mean_force":0.12303,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59394,0.17053,0.2398]},{"body_a":"world","body_b":"grasp_target","contact_count":1372.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52234,0.02705,0.12981]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59746,0.15704,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59204,0.17262,0.21764]},{"body_a":"world","body_b":"grasp_target","contact_count":2484.0,"contact_point_centroid":[0.59746,0.15704,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59439,0.17461,0.31919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5500.0,"contact_point_centroid":[0.5181,0.04836,0.04856],"force_p95":0.06994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07187,"mean_force":0.0404,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51661,0.0292,0.04628]},{"body_a":"left_finger","body_b":"right_finger","contact_count":284.0,"contact_point_centroid":[0.58889,0.16028,0.2572],"force_p95":0.01503,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.01117,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58841,0.16026,0.25502]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.59486,0.17345,0.21571],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59421,0.17342,0.21354]}],"total_contact_groups":17},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59746,0.15704,0.01602],"final_tcp_position":[0.60029,0.17775,0.40196],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52181,0.02452,0.20388],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17818,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52501,0.02973,0.05618],"tcp_start":[0.52181,0.02452,0.20388],"tcp_to_object_dist_end":0.03068,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02963,0.02551],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18455,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51658,0.02919,0.04624],"tcp_start":[0.52501,0.02973,0.05618],"tcp_to_object_dist_end":0.02496,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.52715,0.02956,0.15883],"object_pos_start":[0.53046,0.02963,0.02551],"object_to_goal_dist_end":0.1741,"object_to_goal_dist_start":0.18455,"object_z_max":0.15857,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51306,0.02896,0.18573],"tcp_start":[0.51658,0.02919,0.04624],"tcp_to_object_dist_end":0.03037,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.59745,0.15704,0.01614],"object_pos_start":[0.52715,0.02956,0.15883],"object_to_goal_dist_end":0.09453,"object_to_goal_dist_start":0.1741,"object_z_max":0.19887,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.5928,0.1676,0.25916],"tcp_start":[0.51306,0.02896,0.18573],"tcp_to_object_dist_end":0.2433,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":100.0,"n_steps_budget":1000.0,"object_pos_end":[0.59746,0.15704,0.01602],"object_pos_start":[0.59745,0.15704,0.01614],"object_to_goal_dist_end":0.09464,"object_to_goal_dist_start":0.09453,"object_z_max":0.01614,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.59584,0.17379,0.21763],"tcp_start":[0.5928,0.1676,0.25916],"tcp_to_object_dist_end":0.20231,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59746,0.15704,0.01602],"object_pos_start":[0.59746,0.15704,0.01602],"object_to_goal_dist_end":0.09464,"object_to_goal_dist_start":0.09464,"object_z_max":0.01602,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.59077,0.17214,0.23737],"tcp_start":[0.59584,0.17379,0.21763],"tcp_to_object_dist_end":0.22196,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":621.0,"n_steps_budget":1000.0,"object_pos_end":[0.59746,0.15704,0.01602],"object_pos_start":[0.59746,0.15704,0.01602],"object_to_goal_dist_end":0.09464,"object_to_goal_dist_start":0.09464,"object_z_max":0.01602,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.60029,0.17775,0.40196],"tcp_start":[0.59077,0.17214,0.23737],"tcp_to_object_dist_end":0.38651,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.02426,"average_mean_iterations":7.89488,"average_solve_count":371.0,"average_success_count":362.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.12732,"approach_goal.approach_goal_speed":0.05594,"approach_object.approach_height":0.14895,"approach_object.approach_speed":0.10441,"descend_to_goal.descend_goal_speed":0.02112,"descend_to_goal.place_z_offset":0.03745,"descend_to_grasp.descend_speed":0.04568,"descend_to_grasp.grasp_offset_z":0.01397,"grasp_1.grip_force":13.71553,"lift_1.lift_height":0.15845,"lift_1.lift_speed":0.11255,"retract_goal.retract_goal_height":0.36196,"retract_goal.retract_speed":0.08952},"optimized_scores":{"best_composite_score":-0.26586,"best_fitness_score":0.56414,"best_task_score":0.19931},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":649.0,"contact_point_centroid":[0.58536,0.11911,-0.00418],"force_p95":1.04503,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42066,"mean_force":0.22216,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57331,0.16222,0.34451]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50176,-0.01497,-0.00137],"force_p95":0.4084,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44592,"mean_force":0.10073,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48975,-0.01511,0.04621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7199.0,"contact_point_centroid":[0.49014,0.00397,0.10855],"force_p95":0.10331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29561,"mean_force":0.06522,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48741,-0.01506,0.1061]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7697.0,"contact_point_centroid":[0.49004,-0.03405,0.10804],"force_p95":0.09862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28353,"mean_force":0.06188,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48743,-0.01506,0.10568]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7128.0,"contact_point_centroid":[0.52291,0.06785,0.24063],"force_p95":0.14503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24715,"mean_force":0.08906,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51666,0.04915,0.23935]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8585.0,"contact_point_centroid":[0.52455,0.03434,0.24312],"force_p95":0.10714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24063,"mean_force":0.07588,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51841,0.05272,0.24262]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01562,-0.00205],"force_p95":0.13766,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17621,"mean_force":0.12672,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4921,-0.01514,0.04614]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.50382,-0.01567,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49977,-0.00588,0.25072]},{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.58536,0.11919,-0.00199],"force_p95":0.12289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12313,"mean_force":0.1226,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5819,0.18047,0.33148]},{"body_a":"world","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49851,-0.01377,0.12601]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58536,0.11919,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58094,0.18293,0.29981]},{"body_a":"world","body_b":"grasp_target","contact_count":3344.0,"contact_point_centroid":[0.58536,0.11919,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.5829,0.1843,0.43168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4841.0,"contact_point_centroid":[0.49162,0.00413,0.04755],"force_p95":0.06857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0988,"mean_force":0.04502,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01512,0.04492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5385.0,"contact_point_centroid":[0.4911,-0.03433,0.04756],"force_p95":0.0649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08186,"mean_force":0.04099,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01512,0.04492]},{"body_a":"left_finger","body_b":"right_finger","contact_count":606.0,"contact_point_centroid":[0.57482,0.16435,0.34866],"force_p95":0.0138,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01085,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57438,0.16434,0.34649]},{"body_a":"left_finger","body_b":"right_finger","contact_count":617.0,"contact_point_centroid":[0.58217,0.18048,0.33376],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5819,0.18047,0.33156]}],"total_contact_groups":17},"final_pose_error":0.05983,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58536,0.11919,0.01602],"final_tcp_position":[0.58876,0.18736,0.55028],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50037,-0.01241,0.19828],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17233,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49908,-0.01521,0.05386],"tcp_start":[0.50037,-0.01241,0.19828],"tcp_to_object_dist_end":0.02824,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01527,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31215,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49093,-0.01512,0.04489],"tcp_start":[0.49908,-0.01521,0.05386],"tcp_to_object_dist_end":0.02299,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":435.0,"n_steps_budget":900.0,"object_pos_end":[0.50368,-0.01524,0.16019],"object_pos_start":[0.50374,-0.01527,0.0258],"object_to_goal_dist_end":0.23609,"object_to_goal_dist_start":0.31215,"object_z_max":0.15992,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48756,-0.01505,0.18383],"tcp_start":[0.49093,-0.01512,0.04489],"tcp_to_object_dist_end":0.02861,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.58536,0.11918,0.016],"object_pos_start":[0.50368,-0.01524,0.16019],"object_to_goal_dist_end":0.24195,"object_to_goal_dist_start":0.23609,"object_z_max":0.27544,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.58118,0.17776,0.35896],"tcp_start":[0.48756,-0.01505,0.18383],"tcp_to_object_dist_end":0.34795,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.58536,0.11919,0.01602],"object_pos_start":[0.58536,0.11918,0.016],"object_to_goal_dist_end":0.24193,"object_to_goal_dist_start":0.24195,"object_z_max":0.01602,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.58346,0.18388,0.29951],"tcp_start":[0.58118,0.17776,0.35896],"tcp_to_object_dist_end":0.29078,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58536,0.11919,0.01602],"object_pos_start":[0.58536,0.11919,0.01602],"object_to_goal_dist_end":0.24193,"object_to_goal_dist_start":0.24193,"object_z_max":0.01602,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58021,0.18256,0.31959],"tcp_start":[0.58346,0.18388,0.29951],"tcp_to_object_dist_end":0.31016,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.58536,0.11919,0.01602],"object_pos_start":[0.58536,0.11919,0.01602],"object_to_goal_dist_end":0.24193,"object_to_goal_dist_start":0.24193,"object_z_max":0.01602,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.58876,0.18736,0.55028],"tcp_start":[0.58021,0.18256,0.31959],"tcp_to_object_dist_end":0.5386,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33193,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.16445,"approach_goal.approach_goal_speed":0.12415,"approach_object.approach_height":0.14896,"approach_object.approach_speed":0.10671,"descend_to_goal.descend_goal_speed":0.06063,"descend_to_goal.place_z_offset":0.10121,"descend_to_grasp.descend_speed":0.0523,"descend_to_grasp.grasp_offset_z":0.01028,"grasp_1.grip_force":15.29538,"lift_1.lift_height":0.17075,"lift_1.lift_speed":0.0578,"retract_goal.retract_goal_height":0.32541,"retract_goal.retract_speed":0.12902},"optimized_scores":{"best_composite_score":-0.13942,"best_fitness_score":0.69058,"best_task_score":0.44448},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.608,0.16761,-0.01101],"force_p95":1.59521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74567,"mean_force":0.62079,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61757,0.167,0.27226]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50987,0.0375,-0.00151],"force_p95":0.4054,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47475,"mean_force":0.11961,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49806,0.03767,0.04223]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10123.0,"contact_point_centroid":[0.49622,0.05655,0.11477],"force_p95":0.08202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30654,"mean_force":0.05585,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49565,0.03748,0.11266]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9615.0,"contact_point_centroid":[0.49632,0.01837,0.11875],"force_p95":0.0846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29565,"mean_force":0.05754,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49566,0.03748,0.11625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":734.0,"contact_point_centroid":[0.62384,0.14806,0.27434],"force_p95":0.13942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29038,"mean_force":0.10419,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61958,0.16613,0.27775]},{"body_a":"world","body_b":"grasp_target","contact_count":2509.0,"contact_point_centroid":[0.60356,0.16762,-0.00211],"force_p95":0.15118,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27993,"mean_force":0.12289,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.62172,0.16928,0.3652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":694.0,"contact_point_centroid":[0.62435,0.18429,0.27314],"force_p95":0.14951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2616,"mean_force":0.11437,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61961,0.16616,0.27757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.6246,0.18638,0.24967],"force_p95":0.11304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2606,"mean_force":0.07816,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62013,0.16801,0.25396]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":598.0,"contact_point_centroid":[0.62466,0.14949,0.24948],"force_p95":0.12068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25153,"mean_force":0.08517,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62012,0.168,0.25394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7971.0,"contact_point_centroid":[0.5545,0.07635,0.23742],"force_p95":0.1287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24171,"mean_force":0.07882,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5501,0.09501,0.2366]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03948,-0.00216],"force_p95":0.16857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23134,"mean_force":0.13463,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50041,0.03787,0.04215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8053.0,"contact_point_centroid":[0.55516,0.11436,0.23776],"force_p95":0.1196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21245,"mean_force":0.07839,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55076,0.09568,0.23717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3985.0,"contact_point_centroid":[0.50001,0.01857,0.04364],"force_p95":0.08332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15565,"mean_force":0.05293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49926,0.03778,0.04088]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.51251,0.03972,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5031,0.01526,0.24931]},{"body_a":"world","body_b":"grasp_target","contact_count":1452.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50627,0.0351,0.12311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5002.0,"contact_point_centroid":[0.4999,0.05695,0.04271],"force_p95":0.07551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07975,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49927,0.03778,0.04089]}],"total_contact_groups":16},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60292,0.16768,0.02602],"final_tcp_position":[0.62758,0.17207,0.45055],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.5074,0.03201,0.19619],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17043,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50751,0.03843,0.05014],"tcp_start":[0.5074,0.03201,0.19619],"tcp_to_object_dist_end":0.02467,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03817,0.02545],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21353,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49923,0.03778,0.04085],"tcp_start":[0.50751,0.03843,0.05014],"tcp_to_object_dist_end":0.02031,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.50527,0.03772,0.17207],"object_pos_start":[0.51247,0.03817,0.02545],"object_to_goal_dist_end":0.18401,"object_to_goal_dist_start":0.21353,"object_z_max":0.1718,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49589,0.0375,0.19204],"tcp_start":[0.49923,0.03778,0.04085],"tcp_to_object_dist_end":0.02206,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.62222,0.16391,0.25886],"object_pos_start":[0.50527,0.03772,0.17207],"object_to_goal_dist_end":0.11429,"object_to_goal_dist_start":0.18401,"object_z_max":0.25877,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61798,0.16399,0.29442],"tcp_start":[0.49589,0.0375,0.19204],"tcp_to_object_dist_end":0.03581,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.62737,0.16863,0.22244],"object_pos_start":[0.62222,0.16391,0.25886],"object_to_goal_dist_end":0.07752,"object_to_goal_dist_start":0.11429,"object_z_max":0.25886,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62173,0.16841,0.259],"tcp_start":[0.61798,0.16399,0.29442],"tcp_to_object_dist_end":0.03699,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61616,0.16562,0.01226],"object_pos_start":[0.62737,0.16863,0.22244],"object_to_goal_dist_end":0.13343,"object_to_goal_dist_start":0.07752,"object_z_max":0.22244,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.61756,0.167,0.27759],"tcp_start":[0.62173,0.16841,0.259],"tcp_to_object_dist_end":0.26534,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":647.0,"n_steps_budget":930.0,"object_pos_end":[0.60292,0.16768,0.02602],"object_pos_start":[0.61616,0.16562,0.01226],"object_to_goal_dist_end":0.12163,"object_to_goal_dist_start":0.13343,"object_z_max":0.02862,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.62758,0.17207,0.45055],"tcp_start":[0.61756,0.167,0.27759],"tcp_to_object_dist_end":0.42527,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```