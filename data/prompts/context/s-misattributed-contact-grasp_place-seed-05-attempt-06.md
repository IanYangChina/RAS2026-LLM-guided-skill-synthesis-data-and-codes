## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0229 | 0.33 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.023) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  target_entity: object
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend
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
    - 0.04
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.03
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
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
    - 0.005
  subtask_id: grasp_object
- id: lift
  type: lift
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_offset_z:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
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
  subtask_id: lift_object
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    goal_approach_offset_z:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    goal_approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: descend_to_place
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
    - 0.04
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
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
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.04], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_offset_z: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - goal_approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.04], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.023
- **task_score** (E): 0.328
- **fitness_score**: 0.627  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1857 |
| descend | 1.00 | 1.00 | 0.0632 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 0.67 | 1.00 | 0.1003 |
| approach_goal | 0.00 | 1.00 | 0.0730 |
| descend_to_place | 0.00 | 1.00 | 0.0387 |
| release | 1.00 | 1.00 | 0.0235 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.017, 0.118) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend | descend | 1.00 / step_budget | (0.510, 0.017, 0.118)→(0.511, 0.018, 0.055) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 44.667 | 0.139 | 0.189 |
| grasp | grasp | 1.00 / step_budget | (0.511, 0.018, 0.055)→(0.503, 0.018, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 28.333 | 0.102 | 0.415 |
| lift | lift | 0.67 / step_budget | (0.503, 0.018, 0.046)→(0.507, 0.018, 0.146) | (0.516, 0.018, 0.026)→(0.514, 0.018, 0.118) | 0.236→0.201 | 1.00 / 18.333 | 0.113 | 0.650 |
| approach_goal | approach | 0.00 / step_budget | (0.507, 0.018, 0.146)→(0.532, 0.064, 0.196) | (0.514, 0.018, 0.118)→(0.537, 0.058, 0.108) | 0.201→0.182 | 1.00 / 8.000 | 9748.136 | 0.939 |
| descend_to_place | descend | 0.00 / step_budget | (0.532, 0.064, 0.196)→(0.550, 0.095, 0.193) | (0.537, 0.058, 0.108)→(0.551, 0.093, 0.016) | 0.182→0.185 | 1.00 / 4.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.550, 0.095, 0.193)→(0.545, 0.094, 0.216) | (0.551, 0.093, 0.016)→(0.551, 0.093, 0.016) | 0.185→0.185 | 1.00 / 4.000 | 7.067 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.471
- phase_score: 0.407
- phase_breakdown.approach_object_score: 0.749
- phase_breakdown.place_at_goal_score: 0.099
- phase_breakdown.grasp_object_score: 0.560
- phase_breakdown.lift_object_score: 0.531
- grasp_place_fitness: 0.701

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.701
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.471
- **Median Q (composite search score)**: 0.001
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39286,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_offset_z":0.16771,"approach_goal.goal_approach_speed":0.04134,"approach_object.approach_offset_z":0.0799,"approach_object.approach_speed":0.0792,"descend.descend_offset_z":0.03141,"descend.descend_speed":0.07018,"descend_to_place.place_offset_z":0.04563,"descend_to_place.place_speed":0.04519,"lift.lift_offset_z":0.23722,"lift.lift_speed":0.06478},"optimized_scores":{"best_composite_score":0.05066,"best_fitness_score":0.70066,"best_task_score":0.47119},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1691.0,"contact_point_centroid":[0.56247,0.12621,-0.00255],"force_p95":0.25431,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40819,"mean_force":0.14559,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55673,0.10771,0.17132]},{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.52742,0.0296,-0.00117],"force_p95":0.26169,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45039,"mean_force":0.0734,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51587,0.02974,0.04586]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17231.0,"contact_point_centroid":[0.51823,0.04868,0.09475],"force_p95":0.09227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29348,"mean_force":0.05912,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51635,0.02964,0.09296]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18144.0,"contact_point_centroid":[0.51744,0.01066,0.09328],"force_p95":0.09534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26964,"mean_force":0.05639,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51624,0.02964,0.09163]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4372.0,"contact_point_centroid":[0.55214,0.07241,0.17406],"force_p95":0.12193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24749,"mean_force":0.102,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54715,0.09073,0.17825]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03068,-0.00208],"force_p95":0.14316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19979,"mean_force":0.12855,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51861,0.02993,0.04556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11977.0,"contact_point_centroid":[0.53523,0.03727,0.16565],"force_p95":0.12051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16335,"mean_force":0.07679,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53079,0.05586,0.16663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12081.0,"contact_point_centroid":[0.53574,0.07488,0.16628],"force_p95":0.11885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16205,"mean_force":0.0761,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53105,0.05631,0.16701]},{"body_a":"world","body_b":"grasp_target","contact_count":2428.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51092,0.014,0.20792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4769.0,"contact_point_centroid":[0.55231,0.10907,0.17366],"force_p95":0.1174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13342,"mean_force":0.09314,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54724,0.09093,0.17813]},{"body_a":"world","body_b":"grasp_target","contact_count":3152.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52355,0.02954,0.07638]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56246,0.12627,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55647,0.11347,0.17108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.51765,0.01068,0.04732],"force_p95":0.067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10161,"mean_force":0.04268,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51741,0.02985,0.04417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4938.0,"contact_point_centroid":[0.51795,0.04914,0.04598],"force_p95":0.07115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07504,"mean_force":0.04501,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51741,0.02985,0.04417]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1500.0,"contact_point_centroid":[0.55794,0.1088,0.17306],"force_p95":0.01178,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01065,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55736,0.10878,0.17092]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.55962,0.11411,0.16868],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55918,0.11409,0.1664]}],"total_contact_groups":16},"final_pose_error":0.07769,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56246,0.12627,0.01602],"final_tcp_position":[0.56058,0.11432,0.16887],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.83183,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3152.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.52422,0.02841,0.11719],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":788.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14026,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11803.0,"raw_peak_contact_force":0.19979,"subtask_id":"grasp_object","tcp_end":[0.5254,0.03039,0.05349],"tcp_start":[0.52422,0.02841,0.11719],"tcp_to_object_dist_end":0.02794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.03013,0.02571],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18406,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.10624,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":35551.0,"raw_peak_contact_force":0.45039,"subtask_id":"grasp_object","tcp_end":[0.51738,0.02985,0.04413],"tcp_start":[0.5254,0.03039,0.05349],"tcp_to_object_dist_end":0.02258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52881,0.02993,0.12363],"object_pos_start":[0.53043,0.03013,0.02571],"object_to_goal_dist_end":0.16622,"object_to_goal_dist_start":0.18406,"object_z_max":0.12352,"peak_contact_force":0.11371,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24058.0,"raw_peak_contact_force":0.16335,"subtask_id":"lift_object","tcp_end":[0.51995,0.02973,0.15016],"tcp_start":[0.51738,0.02985,0.04413],"tcp_to_object_dist_end":0.02797,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54969,0.08175,0.1532],"object_pos_start":[0.52881,0.02993,0.12363],"object_to_goal_dist_end":0.11873,"object_to_goal_dist_start":0.16622,"object_z_max":0.15317,"peak_contact_force":9748.83183,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12332.0,"raw_peak_contact_force":1.40819,"subtask_id":"place_at_goal","tcp_end":[0.54494,0.08159,0.18773],"tcp_start":[0.51995,0.02973,0.15016],"tcp_to_object_dist_end":0.03486,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56246,0.12627,0.01602],"object_pos_start":[0.54969,0.08175,0.1532],"object_to_goal_dist_end":0.11287,"object_to_goal_dist_start":0.11873,"object_z_max":0.1532,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.56058,0.11432,0.16887],"tcp_start":[0.54494,0.08159,0.18773],"tcp_to_object_dist_end":0.15333,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56246,0.12627,0.01602],"object_pos_start":[0.56246,0.12627,0.01602],"object_to_goal_dist_end":0.11287,"object_to_goal_dist_start":0.11287,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2428.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.55488,0.1131,0.19135],"tcp_start":[0.56058,0.11432,0.16887],"tcp_to_object_dist_end":0.17599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08936,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_offset_z":0.18708,"approach_goal.goal_approach_speed":0.0345,"approach_object.approach_offset_z":0.08963,"approach_object.approach_speed":0.02369,"descend.descend_offset_z":0.03149,"descend.descend_speed":0.06308,"descend_to_place.place_offset_z":0.06008,"descend_to_place.place_speed":0.02533,"lift.lift_offset_z":0.1583,"lift.lift_speed":0.06248},"optimized_scores":{"best_composite_score":-0.11978,"best_fitness_score":0.53022,"best_task_score":0.14179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1223.0,"contact_point_centroid":[0.52701,0.01872,-0.00286],"force_p95":0.39302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66046,"mean_force":0.16373,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51285,0.02813,0.20585]},{"body_a":"world","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.50124,-0.01521,-0.00113],"force_p95":0.23121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35687,"mean_force":0.05798,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48968,-0.01537,0.05095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15049.0,"contact_point_centroid":[0.49268,0.00358,0.09209],"force_p95":0.12274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26713,"mean_force":0.06693,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49142,-0.01534,0.09257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16761.0,"contact_point_centroid":[0.49272,-0.03411,0.09294],"force_p95":0.11591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25677,"mean_force":0.06017,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49149,-0.01534,0.09323]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.50677,0.0206,0.16633],"force_p95":0.13187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22803,"mean_force":0.10594,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50135,0.00235,0.17016]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5579.0,"contact_point_centroid":[0.50661,-0.01522,0.16692],"force_p95":0.12423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21413,"mean_force":0.09627,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50156,0.00287,0.17086]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01564,-0.00203],"force_p95":0.13252,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15983,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49222,-0.01541,0.05056]},{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49863,-0.00701,0.21439]},{"body_a":"world","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49766,-0.01493,0.09008]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52704,0.01892,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51908,0.04827,0.21806]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52704,0.01892,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5206,0.05868,0.22738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4366.0,"contact_point_centroid":[0.49151,0.00379,0.05018],"force_p95":0.07239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09772,"mean_force":0.04938,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01539,0.04932]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4876.0,"contact_point_centroid":[0.49147,-0.03453,0.04999],"force_p95":0.06832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08603,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01539,0.04932]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1079.0,"contact_point_centroid":[0.51366,0.02937,0.20993],"force_p95":0.01219,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01561,"mean_force":0.01062,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51342,0.02937,0.20759]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4288.0,"contact_point_centroid":[0.51945,0.04827,0.22034],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51908,0.04826,0.21806]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.52334,0.05899,0.22456],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.00993,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52285,0.05898,0.22209]}],"total_contact_groups":16},"final_pose_error":0.16579,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52704,0.01892,0.01602],"final_tcp_position":[0.52402,0.05908,0.22423],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.67071,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49955,-0.01436,0.12854],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13195,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11042.0,"raw_peak_contact_force":0.15983,"subtask_id":"grasp_object","tcp_end":[0.49883,-0.0155,0.05782],"tcp_start":[0.49955,-0.01436,0.12854],"tcp_to_object_dist_end":0.03219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01543,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31221,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12821,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":31989.0,"raw_peak_contact_force":0.35687,"subtask_id":"grasp_object","tcp_end":[0.49105,-0.01539,0.04928],"tcp_start":[0.49883,-0.0155,0.05782],"tcp_to_object_dist_end":0.02664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50277,-0.01583,0.11746],"object_pos_start":[0.50374,-0.01543,0.02586],"object_to_goal_dist_end":0.25588,"object_to_goal_dist_start":0.31221,"object_z_max":0.11735,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12947.0,"raw_peak_contact_force":1.66046,"subtask_id":"lift_object","tcp_end":[0.49703,-0.01535,0.15041],"tcp_start":[0.49105,-0.01539,0.04928],"tcp_to_object_dist_end":0.03346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52704,0.01892,0.01602],"object_pos_start":[0.50277,-0.01583,0.11746],"object_to_goal_dist_end":0.29301,"object_to_goal_dist_start":0.25588,"object_z_max":0.15102,"peak_contact_force":9748.67071,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8288.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.51608,0.03518,0.21571],"tcp_start":[0.49703,-0.01535,0.15041],"tcp_to_object_dist_end":0.20065,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52704,0.01892,0.01602],"object_pos_start":[0.52704,0.01892,0.01602],"object_to_goal_dist_end":0.29301,"object_to_goal_dist_start":0.29301,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.52402,0.05908,0.22423],"tcp_start":[0.51608,0.03518,0.21571],"tcp_to_object_dist_end":0.21207,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52704,0.01892,0.01602],"object_pos_start":[0.52704,0.01892,0.01602],"object_to_goal_dist_end":0.29301,"object_to_goal_dist_start":0.29301,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.51932,0.05851,0.24806],"tcp_start":[0.52402,0.05908,0.22423],"tcp_to_object_dist_end":0.23552,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97797,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.goal_approach_offset_z":0.19179,"approach_goal.goal_approach_speed":0.0472,"approach_object.approach_offset_z":0.06963,"approach_object.approach_speed":0.03621,"descend.descend_offset_z":0.03008,"descend.descend_speed":0.05137,"descend_to_place.place_offset_z":0.06451,"descend_to_place.place_speed":0.06214,"lift.lift_offset_z":0.15677,"lift.lift_speed":0.05749},"optimized_scores":{"best_composite_score":0.00052,"best_fitness_score":0.65052,"best_task_score":0.36953},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":342.0,"contact_point_centroid":[0.56334,0.13276,-0.00502],"force_p95":0.91615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28716,"mean_force":0.2431,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56417,0.10895,0.18618]},{"body_a":"world","body_b":"grasp_target","contact_count":205.0,"contact_point_centroid":[0.50914,0.03804,-0.0012],"force_p95":0.25283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43726,"mean_force":0.07193,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49821,0.03842,0.04548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8786.0,"contact_point_centroid":[0.54532,0.06949,0.17855],"force_p95":0.13336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32981,"mean_force":0.0861,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54427,0.08792,0.18169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19570.0,"contact_point_centroid":[0.50077,0.05747,0.09283],"force_p95":0.07625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28731,"mean_force":0.05185,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50032,0.03834,0.09069]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19679.0,"contact_point_centroid":[0.5002,0.01923,0.09103],"force_p95":0.07567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25676,"mean_force":0.05138,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50015,0.03833,0.08904]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03957,-0.00209],"force_p95":0.14818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20718,"mean_force":0.12987,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50093,0.03867,0.04506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9220.0,"contact_point_centroid":[0.54679,0.1069,0.17818],"force_p95":0.11932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16829,"mean_force":0.08277,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54489,0.08859,0.1818]},{"body_a":"world","body_b":"grasp_target","contact_count":2680.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50252,0.01807,0.20328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18044.0,"contact_point_centroid":[0.51913,0.07595,0.16013],"force_p95":0.08817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1254,"mean_force":0.05359,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51831,0.05693,0.15957]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56315,0.1337,-0.00197],"force_p95":0.12446,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1252,"mean_force":0.12284,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56176,0.10974,0.18865]},{"body_a":"world","body_b":"grasp_target","contact_count":3036.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50625,0.03823,0.07076]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.49917,0.01933,0.04759],"force_p95":0.06774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11653,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49976,0.03858,0.04376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18384.0,"contact_point_centroid":[0.51873,0.03826,0.1603],"force_p95":0.08849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1149,"mean_force":0.05338,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51862,0.05727,0.16005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5448.0,"contact_point_centroid":[0.4995,0.05786,0.04637],"force_p95":0.06777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06965,"mean_force":0.04121,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49977,0.03858,0.04377]},{"body_a":"left_finger","body_b":"right_finger","contact_count":85.0,"contact_point_centroid":[0.56603,0.1102,0.189],"force_p95":0.0162,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01656,"mean_force":0.01299,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56535,0.11018,0.18647]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.56526,0.11035,0.18617],"force_p95":0.0118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01029,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56435,0.11033,0.18407]}],"total_contact_groups":16},"final_pose_error":0.09057,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.56315,0.1337,0.01602],"final_tcp_position":[0.56567,0.11053,0.18655],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9746.90543,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3036.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50751,0.03672,0.10765],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1447,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12311.0,"raw_peak_contact_force":0.20718,"subtask_id":"grasp_object","tcp_end":[0.50755,0.03922,0.05247],"tcp_start":[0.50751,0.03672,0.10765],"tcp_to_object_dist_end":0.02692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51245,0.03885,0.02566],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.213,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.0703,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":39454.0,"raw_peak_contact_force":0.43726,"subtask_id":"grasp_object","tcp_end":[0.49973,0.03857,0.04373],"tcp_start":[0.50755,0.03922,0.05247],"tcp_to_object_dist_end":0.0221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50961,0.03856,0.11211],"object_pos_start":[0.51245,0.03885,0.02566],"object_to_goal_dist_end":0.18151,"object_to_goal_dist_start":0.213,"object_z_max":0.11201,"peak_contact_force":0.10139,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36428.0,"raw_peak_contact_force":0.1254,"subtask_id":"lift_object","tcp_end":[0.50469,0.03844,0.13704],"tcp_start":[0.49973,0.03857,0.04373],"tcp_to_object_dist_end":0.02541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53448,0.0741,0.15376],"object_pos_start":[0.50961,0.03856,0.11211],"object_to_goal_dist_end":0.13575,"object_to_goal_dist_start":0.18151,"object_z_max":0.15373,"peak_contact_force":9746.90543,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18433.0,"raw_peak_contact_force":1.28716,"subtask_id":"place_at_goal","tcp_end":[0.53379,0.07378,0.18408],"tcp_start":[0.50469,0.03844,0.13704],"tcp_to_object_dist_end":0.03033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56318,0.13373,0.01653],"object_pos_start":[0.53448,0.0741,0.15376],"object_to_goal_dist_end":0.14887,"object_to_goal_dist_start":0.13575,"object_z_max":0.15376,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.1252,"subtask_id":"place_at_goal","tcp_end":[0.56567,0.11053,0.18655],"tcp_start":[0.53379,0.07378,0.18408],"tcp_to_object_dist_end":0.17162,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56315,0.1337,0.01602],"object_pos_start":[0.56318,0.13373,0.01653],"object_to_goal_dist_end":0.14933,"object_to_goal_dist_start":0.14887,"object_z_max":0.01653,"peak_contact_force":20.95526,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2680.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.56026,0.10939,0.20884],"tcp_start":[0.56567,0.11053,0.18655],"tcp_to_object_dist_end":0.19437,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```