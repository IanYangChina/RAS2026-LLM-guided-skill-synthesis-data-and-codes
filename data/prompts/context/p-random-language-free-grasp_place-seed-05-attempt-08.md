## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0608 | 0.36 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0416 | 0.32 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0563 | 0.35 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.061) — your mutation base

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
  weight: 0.5
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
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
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_object
- id: descend_to_object
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
    - 0.03
    tolerance: 0.005
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
  subtask_id: reach_object
- id: grasp_object
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
  guards:
  - id: grasp_contact
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
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
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: approach_goal
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_place
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
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: release_object
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
- id: retract_after_place
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
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_contact, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.061
- **task_score** (E): 0.357
- **fitness_score**: 0.641  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1659 |
| descend_to_object | 1.00 | 1.00 | 0.0842 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1184 |
| approach_goal | 0.00 | 1.00 | 0.0990 |
| descend_place | 0.33 | 1.00 | 0.0438 |
| release_object | 1.00 | 1.00 | 0.0230 |
| retract_after_place | 0.67 | 1.00 | 0.0935 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.511, 0.018, 0.054) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.506, 0.018, 0.048)→(0.506, 0.018, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 39.333 | 0.142 | 0.175 |
| lift_object | lift | 1.00 / step_budget | (0.506, 0.018, 0.048)→(0.502, 0.018, 0.167) | (0.516, 0.018, 0.026)→(0.511, 0.018, 0.137) | 0.236→0.202 | 1.00 / 21.333 | 0.109 | 0.399 |
| approach_goal | approach | 0.00 / step_budget | (0.502, 0.018, 0.167)→(0.548, 0.094, 0.202) | (0.511, 0.018, 0.137)→(0.549, 0.095, 0.110) | 0.202→0.150 | 1.00 / 14.333 | 0.123 | 0.619 |
| descend_place | descend | 0.33 / step_budget | (0.548, 0.094, 0.202)→(0.564, 0.120, 0.175) | (0.549, 0.095, 0.110)→(0.556, 0.120, 0.016) | 0.150→0.172 | 1.00 / 8.333 | 91001.923 | 1.044 |
| release_object | release | 1.00 / step_budget | (0.564, 0.120, 0.175)→(0.558, 0.119, 0.197) | (0.556, 0.120, 0.016)→(0.556, 0.120, 0.016) | 0.172→0.172 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 0.67 / step_budget | (0.558, 0.119, 0.197)→(0.556, 0.118, 0.291) | (0.556, 0.120, 0.016)→(0.556, 0.120, 0.016) | 0.172→0.172 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.532
- phase_score: 0.211
- phase_breakdown.reach_goal_score: 0.210
- phase_breakdown.reach_object_score: 0.211
- grasp_place_fitness: 0.730

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.730
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.532
- **Median Q (composite search score)**: 0.074
- **K-run variance**: 0.0063
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.239


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32039,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09227,"approach_object.approach_speed":0.05443,"descend_place.place_speed":0.06062,"descend_to_object.descend_speed":0.08211,"lift_object.lift_height":0.13941,"lift_object.lift_speed":0.08576,"retract_after_place.retract_height":0.14529,"retract_after_place.retract_speed":0.05695},"optimized_scores":{"best_composite_score":0.15045,"best_fitness_score":0.73045,"best_task_score":0.53239},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3470.0,"contact_point_centroid":[0.58477,0.16494,-0.00224],"force_p95":0.12744,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5142,"mean_force":0.13525,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57331,0.13902,0.15501]},{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.5277,0.02964,-0.0012],"force_p95":0.24345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43469,"mean_force":0.06486,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51871,0.02994,0.04828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15612.0,"contact_point_centroid":[0.51728,0.0108,0.1041],"force_p95":0.09961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31226,"mean_force":0.06055,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51625,0.02978,0.10345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16241.0,"contact_point_centroid":[0.518,0.04874,0.10454],"force_p95":0.09472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31046,"mean_force":0.05895,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51628,0.02978,0.10343]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.57214,0.14036,0.17787],"force_p95":0.20263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25105,"mean_force":0.12248,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56569,0.12347,0.18267]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53052,0.03066,-0.00208],"force_p95":0.14223,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18264,"mean_force":0.1289,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52102,0.0301,0.04727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10144.0,"contact_point_centroid":[0.54593,0.05881,0.17706],"force_p95":0.12063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18122,"mean_force":0.08949,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54049,0.07724,0.17913]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":331.0,"contact_point_centroid":[0.57226,0.10469,0.18008],"force_p95":0.16261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17272,"mean_force":0.11852,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56576,0.12286,0.18475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10407.0,"contact_point_centroid":[0.54617,0.09569,0.17722],"force_p95":0.11742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15783,"mean_force":0.08707,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54054,0.07734,0.17915]},{"body_a":"world","body_b":"grasp_target","contact_count":2328.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51083,0.01385,0.21801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.51981,0.01087,0.04834],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1344,"mean_force":0.05225,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52051,0.03006,0.04667]},{"body_a":"world","body_b":"grasp_target","contact_count":3228.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52359,0.02947,0.08364]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58485,0.16495,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57598,0.14939,0.1398]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58485,0.16495,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57095,0.14796,0.20404]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5910.0,"contact_point_centroid":[0.52065,0.04913,0.04814],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07949,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52051,0.03006,0.04667]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3440.0,"contact_point_centroid":[0.57426,0.13977,0.1562],"force_p95":0.01117,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01573,"mean_force":0.01062,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57375,0.13974,0.15394]}],"total_contact_groups":17},"final_pose_error":0.05464,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58485,0.16495,0.01602],"final_tcp_position":[0.57129,0.14802,0.25052],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273005.52353,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2328.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5242,0.02822,0.13703],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3228.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5254,0.03039,0.05242],"tcp_start":[0.5242,0.02822,0.13703],"tcp_to_object_dist_end":0.02689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.03015,0.02574],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18404,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.13955,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12669.0,"raw_peak_contact_force":0.18264,"tcp_end":[0.52048,0.03006,0.04664],"tcp_start":[0.52048,0.03006,0.04664],"tcp_to_object_dist_end":0.02315,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.52625,0.03012,0.14619],"object_pos_start":[0.53042,0.03012,0.02575],"object_to_goal_dist_end":0.17077,"object_to_goal_dist_start":0.18405,"object_z_max":0.14609,"peak_contact_force":0.09885,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32023.0,"raw_peak_contact_force":0.43469,"tcp_end":[0.51668,0.02981,0.17446],"tcp_start":[0.52048,0.03006,0.04664],"tcp_to_object_dist_end":0.02985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57204,0.12173,0.15094],"object_pos_start":[0.52625,0.03012,0.14619],"object_to_goal_dist_end":0.07705,"object_to_goal_dist_start":0.17077,"object_z_max":0.15093,"peak_contact_force":0.1225,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20551.0,"raw_peak_contact_force":0.18122,"subtask_id":"reach_goal","tcp_end":[0.56595,0.12181,0.18818],"tcp_start":[0.51668,0.02981,0.17446],"tcp_to_object_dist_end":0.03774,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58485,0.16495,0.01602],"object_pos_start":[0.57204,0.12173,0.15094],"object_to_goal_dist_end":0.09456,"object_to_goal_dist_start":0.07705,"object_z_max":0.15094,"peak_contact_force":273005.52353,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7773.0,"raw_peak_contact_force":1.5142,"subtask_id":"reach_goal","tcp_end":[0.58051,0.15059,0.1383],"tcp_start":[0.56595,0.12181,0.18818],"tcp_to_object_dist_end":0.12319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58485,0.16495,0.01602],"object_pos_start":[0.58485,0.16495,0.01602],"object_to_goal_dist_end":0.09456,"object_to_goal_dist_start":0.09456,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57422,0.14888,0.15979],"tcp_start":[0.58051,0.15059,0.1383],"tcp_to_object_dist_end":0.14505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58485,0.16495,0.01602],"object_pos_start":[0.58485,0.16495,0.01602],"object_to_goal_dist_end":0.09456,"object_to_goal_dist_start":0.09456,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57129,0.14802,0.25052],"tcp_start":[0.57422,0.14888,0.15979],"tcp_to_object_dist_end":0.2355,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29386,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07255,"approach_object.approach_speed":0.08786,"descend_place.place_speed":0.03046,"descend_to_object.descend_speed":0.02305,"lift_object.lift_height":0.11385,"lift_object.lift_speed":0.10175,"retract_after_place.retract_height":0.13647,"retract_after_place.retract_speed":0.07753},"optimized_scores":{"best_composite_score":-0.04211,"best_fitness_score":0.53789,"best_task_score":0.15998},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1434.0,"contact_point_centroid":[0.51293,0.05988,-0.0027],"force_p95":0.34716,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50106,"mean_force":0.15152,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51549,0.0446,0.20528]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.50165,-0.0151,-0.00123],"force_p95":0.26215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34506,"mean_force":0.05276,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49255,-0.01542,0.05346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7206.0,"contact_point_centroid":[0.49153,0.00319,0.09483],"force_p95":0.12263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34044,"mean_force":0.08638,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49018,-0.01537,0.09747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7666.0,"contact_point_centroid":[0.49102,-0.03385,0.09495],"force_p95":0.12284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33654,"mean_force":0.08132,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49017,-0.01537,0.09777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4746.0,"contact_point_centroid":[0.50216,-0.0109,0.16605],"force_p95":0.13418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25447,"mean_force":0.10506,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49765,0.00729,0.17015]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.50272,0.02625,0.16689],"force_p95":0.12137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20596,"mean_force":0.09901,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49805,0.00814,0.17094]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50377,-0.01565,-0.0021],"force_p95":0.14285,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1521,"mean_force":0.13032,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4946,-0.01545,0.05199]},{"body_a":"world","body_b":"grasp_target","contact_count":1992.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4989,-0.00697,0.21959]},{"body_a":"world","body_b":"grasp_target","contact_count":2336.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49765,-0.0149,0.09443]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51287,0.06008,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52479,0.06959,0.21369]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51287,0.06008,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52677,0.08023,0.21896]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51287,0.06008,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.52306,0.0796,0.30104]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4774.0,"contact_point_centroid":[0.49553,0.00345,0.05109],"force_p95":0.09808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10433,"mean_force":0.05598,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49413,-0.01544,0.05147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4787.0,"contact_point_centroid":[0.49438,-0.03426,0.05058],"force_p95":0.08986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09251,"mean_force":0.05489,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49413,-0.01544,0.05148]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1259.0,"contact_point_centroid":[0.5168,0.04671,0.20953],"force_p95":0.01216,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01065,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51652,0.04671,0.20728]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4303.0,"contact_point_centroid":[0.52524,0.0696,0.21601],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52479,0.06959,0.21369]}],"total_contact_groups":17},"final_pose_error":0.01203,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51287,0.06008,0.01602],"final_tcp_position":[0.52365,0.07967,0.36413],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.50106,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1992.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49976,-0.0143,0.1388],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2336.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49887,-0.0155,0.05673],"tcp_start":[0.49976,-0.0143,0.1388],"tcp_to_object_dist_end":0.03111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01546,0.02551],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31249,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14417,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11365.0,"raw_peak_contact_force":0.1521,"tcp_end":[0.49411,-0.01544,0.05145],"tcp_start":[0.49411,-0.01544,0.05145],"tcp_to_object_dist_end":0.02766,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.49676,-0.01553,0.12007],"object_pos_start":[0.50369,-0.01546,0.02546],"object_to_goal_dist_end":0.25636,"object_to_goal_dist_start":0.31253,"object_z_max":0.11996,"peak_contact_force":0.12426,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15020.0,"raw_peak_contact_force":0.34506,"tcp_end":[0.49026,-0.01537,0.15335],"tcp_start":[0.49411,-0.01544,0.05145],"tcp_to_object_dist_end":0.03391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51287,0.06008,0.01602],"object_pos_start":[0.49676,-0.01553,0.12007],"object_to_goal_dist_end":0.27491,"object_to_goal_dist_start":0.25636,"object_z_max":0.14935,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12435.0,"raw_peak_contact_force":1.50106,"subtask_id":"reach_goal","tcp_end":[0.5211,0.05613,0.21624],"tcp_start":[0.49026,-0.01537,0.15335],"tcp_to_object_dist_end":0.20043,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51287,0.06008,0.01602],"object_pos_start":[0.51287,0.06008,0.01602],"object_to_goal_dist_end":0.27491,"object_to_goal_dist_start":0.27491,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8303.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.53029,0.08078,0.21597],"tcp_start":[0.5211,0.05613,0.21624],"tcp_to_object_dist_end":0.20177,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51287,0.06008,0.01602],"object_pos_start":[0.51287,0.06008,0.01602],"object_to_goal_dist_end":0.27491,"object_to_goal_dist_start":0.27491,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52545,0.08,0.23956],"tcp_start":[0.53029,0.08078,0.21597],"tcp_to_object_dist_end":0.22478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51287,0.06008,0.01602],"object_pos_start":[0.51287,0.06008,0.01602],"object_to_goal_dist_end":0.27491,"object_to_goal_dist_start":0.27491,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52365,0.07967,0.36413],"tcp_start":[0.52545,0.08,0.23956],"tcp_to_object_dist_end":0.34883,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56897,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07568,"approach_object.approach_speed":0.09193,"descend_place.place_speed":0.04974,"descend_to_object.descend_speed":0.04699,"lift_object.lift_height":0.13754,"lift_object.lift_speed":0.10388,"retract_after_place.retract_height":0.07788,"retract_after_place.retract_speed":0.0813},"optimized_scores":{"best_composite_score":0.07412,"best_fitness_score":0.65412,"best_task_score":0.37995},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3067.0,"contact_point_centroid":[0.57169,0.13635,-0.00231],"force_p95":0.12614,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49481,"mean_force":0.1362,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57152,0.11949,0.17914]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.50931,0.03815,-0.0012],"force_p95":0.24832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41778,"mean_force":0.06318,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5013,0.03872,0.04861]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13536.0,"contact_point_centroid":[0.50025,0.05752,0.10449],"force_p95":0.09506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30209,"mean_force":0.05828,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49884,0.03853,0.10353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13028.0,"contact_point_centroid":[0.49956,0.01953,0.10443],"force_p95":0.09889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29448,"mean_force":0.05966,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49881,0.03853,0.10389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1203.0,"contact_point_centroid":[0.56342,0.08738,0.18804],"force_p95":0.16326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24476,"mean_force":0.11429,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55859,0.1056,0.1931]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51253,0.03957,-0.00209],"force_p95":0.14467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19132,"mean_force":0.12967,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50337,0.0389,0.04745]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9816.0,"contact_point_centroid":[0.5328,0.05336,0.18246],"force_p95":0.12593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17431,"mean_force":0.09221,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52802,0.07182,0.1845]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10703.0,"contact_point_centroid":[0.53294,0.08985,0.18266],"force_p95":0.12297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16682,"mean_force":0.08453,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52775,0.07154,0.18436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.56408,0.12356,0.18785],"force_p95":0.12251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15126,"mean_force":0.09678,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55868,0.10571,0.19295]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50278,0.01775,0.2188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4952.0,"contact_point_centroid":[0.50216,0.01966,0.04846],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13744,"mean_force":0.05226,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50287,0.03886,0.04688]},{"body_a":"world","body_b":"grasp_target","contact_count":3212.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50641,0.03807,0.08229]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57168,0.1364,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57705,0.12819,0.17274]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.57168,0.1364,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57246,0.12704,0.22371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5928.0,"contact_point_centroid":[0.503,0.05793,0.04829],"force_p95":0.07109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07179,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50287,0.03886,0.04689]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2956.0,"contact_point_centroid":[0.57276,0.1203,0.18073],"force_p95":0.01115,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01554,"mean_force":0.01065,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57231,0.12028,0.17848]}],"total_contact_groups":17},"final_pose_error":0.01306,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57168,0.1364,0.01602],"final_tcp_position":[0.57256,0.12703,0.2579],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.49481,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50773,0.03626,0.13805],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":803.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3212.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50763,0.03925,0.05226],"tcp_start":[0.50773,0.03626,0.13805],"tcp_to_object_dist_end":0.02669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03899,0.0257],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21289,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14164,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12684.0,"raw_peak_contact_force":0.19132,"tcp_end":[0.50284,0.03886,0.04686],"tcp_start":[0.50284,0.03886,0.04686],"tcp_to_object_dist_end":0.02322,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":758.0,"n_steps_budget":840.0,"object_pos_end":[0.50936,0.03886,0.14421],"object_pos_start":[0.51244,0.03897,0.02572],"object_to_goal_dist_end":0.17844,"object_to_goal_dist_start":0.2129,"object_z_max":0.14409,"peak_contact_force":0.10514,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26710.0,"raw_peak_contact_force":0.41778,"tcp_end":[0.49913,0.03856,0.17202],"tcp_start":[0.50284,0.03886,0.04686],"tcp_to_object_dist_end":0.02963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56273,0.10272,0.16329],"object_pos_start":[0.50936,0.03886,0.14421],"object_to_goal_dist_end":0.097,"object_to_goal_dist_start":0.17844,"object_z_max":0.16327,"peak_contact_force":0.12396,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20519.0,"raw_peak_contact_force":0.17431,"subtask_id":"reach_goal","tcp_end":[0.55784,0.10283,0.2004],"tcp_start":[0.49913,0.03856,0.17202],"tcp_to_object_dist_end":0.03743,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57168,0.1364,0.01602],"object_pos_start":[0.56273,0.10272,0.16329],"object_to_goal_dist_end":0.14516,"object_to_goal_dist_start":0.097,"object_z_max":0.16329,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8618.0,"raw_peak_contact_force":1.49481,"subtask_id":"reach_goal","tcp_end":[0.58118,0.12917,0.17112],"tcp_start":[0.55784,0.10283,0.2004],"tcp_to_object_dist_end":0.15556,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57168,0.1364,0.01602],"object_pos_start":[0.57168,0.1364,0.01602],"object_to_goal_dist_end":0.14516,"object_to_goal_dist_start":0.14516,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57546,0.12777,0.19273],"tcp_start":[0.58118,0.12917,0.17112],"tcp_to_object_dist_end":0.17697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":630.0,"object_pos_end":[0.57168,0.1364,0.01602],"object_pos_start":[0.57168,0.1364,0.01602],"object_to_goal_dist_end":0.14516,"object_to_goal_dist_start":0.14516,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57256,0.12703,0.2579],"tcp_start":[0.57546,0.12777,0.19273],"tcp_to_object_dist_end":0.24206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```