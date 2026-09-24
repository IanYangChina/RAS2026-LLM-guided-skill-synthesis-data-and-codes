## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0563 | 0.35 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.3280 | 0.21 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.056) — your mutation base

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
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
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
    - 0.1
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
- id: descend_place
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
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
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
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

- **Composite score**: 0.056
- **task_score** (E): 0.349
- **fitness_score**: 0.636  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1659 |
| descend_to_object | 1.00 | 1.00 | 0.0841 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1278 |
| approach_goal | 0.00 | 0.67 | 0.1029 |
| descend_place | 0.33 | 1.00 | 0.0493 |
| release_object | 1.00 | 1.00 | 0.0228 |
| retract_after_place | 1.00 | 1.00 | 0.1265 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.511, 0.018, 0.054) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.506, 0.018, 0.048)→(0.506, 0.018, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 40.333 | 0.143 | 0.175 |
| lift_object | lift | 1.00 / step_budget | (0.506, 0.018, 0.048)→(0.502, 0.018, 0.176) | (0.516, 0.018, 0.026)→(0.508, 0.018, 0.145) | 0.236→0.201 | 1.00 / 24.000 | 55983.980 | 0.398 |
| approach_goal | approach | 0.00 / step_budget | (0.502, 0.018, 0.176)→(0.550, 0.098, 0.209) | (0.508, 0.018, 0.145)→(0.555, 0.086, 0.099) | 0.201→0.148 | 0.67 / 9.333 | 90998.764 | 0.751 |
| descend_place | descend | 0.33 / step_budget | (0.550, 0.098, 0.209)→(0.567, 0.128, 0.179) | (0.555, 0.086, 0.099)→(0.563, 0.103, 0.016) | 0.148→0.178 | 1.00 / 8.333 | 0.123 | 1.053 |
| release_object | release | 1.00 / step_budget | (0.567, 0.128, 0.179)→(0.562, 0.126, 0.202) | (0.563, 0.103, 0.016)→(0.563, 0.103, 0.016) | 0.178→0.178 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.562, 0.126, 0.202)→(0.560, 0.126, 0.328) | (0.563, 0.103, 0.016)→(0.563, 0.103, 0.016) | 0.178→0.178 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.524
- phase_score: 0.208
- phase_breakdown.reach_goal_score: 0.206
- phase_breakdown.reach_object_score: 0.211
- grasp_place_fitness: 0.727

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.727
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.524
- **Median Q (composite search score)**: 0.072
- **K-run variance**: 0.0065
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.233


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.875,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07832,"approach_object.approach_speed":0.10279,"descend_place.place_speed":0.07204,"descend_to_object.descend_speed":0.08016,"lift_object.lift_height":0.15914,"lift_object.lift_speed":0.1084,"retract_after_place.retract_height":0.14937,"retract_after_place.retract_speed":0.1157},"optimized_scores":{"best_composite_score":0.14653,"best_fitness_score":0.72653,"best_task_score":0.52427},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3767.0,"contact_point_centroid":[0.59299,0.14961,-0.00227],"force_p95":0.12559,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63737,"mean_force":0.1365,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57645,0.14405,0.15703]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.52715,0.02947,-0.00126],"force_p95":0.23745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42599,"mean_force":0.06959,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51882,0.02995,0.04813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14528.0,"contact_point_centroid":[0.51842,0.04873,0.11105],"force_p95":0.09689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30386,"mean_force":0.06078,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51646,0.0298,0.1101]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13887.0,"contact_point_centroid":[0.51774,0.01083,0.11065],"force_p95":0.10158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29885,"mean_force":0.06278,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51642,0.02979,0.11012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9756.0,"contact_point_centroid":[0.54666,0.05929,0.18909],"force_p95":0.11943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26124,"mean_force":0.09017,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54103,0.07769,0.19147]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9948.0,"contact_point_centroid":[0.54697,0.0963,0.18935],"force_p95":0.12015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22259,"mean_force":0.08768,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54119,0.07798,0.19149]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53051,0.03066,-0.00208],"force_p95":0.14219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18256,"mean_force":0.1289,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52103,0.0301,0.04716]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51094,0.01386,0.21805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.51983,0.01087,0.04827],"force_p95":0.0784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13431,"mean_force":0.05225,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52052,0.03007,0.04657]},{"body_a":"world","body_b":"grasp_target","contact_count":3296.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52363,0.02948,0.08322]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59304,0.14971,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58003,0.1561,0.13531]},{"body_a":"world","body_b":"grasp_target","contact_count":2964.0,"contact_point_centroid":[0.59304,0.14971,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57524,0.15466,0.21889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5910.0,"contact_point_centroid":[0.52066,0.04913,0.04807],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07953,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52052,0.03007,0.04657]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3770.0,"contact_point_centroid":[0.57738,0.14486,0.15776],"force_p95":0.01115,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5769,0.14484,0.15556]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.58356,0.15702,0.13331],"force_p95":0.01085,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01087,"mean_force":0.0099,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58305,0.157,0.13115]}],"total_contact_groups":15},"final_pose_error":0.0156,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59304,0.14971,0.01602],"final_tcp_position":[0.57587,0.15479,0.28919],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.63737,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52427,0.0282,0.13715],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3296.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52542,0.03039,0.05232],"tcp_start":[0.52427,0.0282,0.13715],"tcp_to_object_dist_end":0.02679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.03015,0.02574],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18404,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.13949,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12669.0,"raw_peak_contact_force":0.18256,"tcp_end":[0.5205,0.03007,0.04654],"tcp_start":[0.5205,0.03007,0.04654],"tcp_to_object_dist_end":0.02305,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":856.0,"n_steps_budget":930.0,"object_pos_end":[0.52673,0.0302,0.16381],"object_pos_start":[0.53042,0.03012,0.02575],"object_to_goal_dist_end":0.17526,"object_to_goal_dist_start":0.18405,"object_z_max":0.16368,"peak_contact_force":0.09773,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28576.0,"raw_peak_contact_force":0.42599,"tcp_end":[0.51692,0.02983,0.19262],"tcp_start":[0.5205,0.03007,0.04654],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57913,0.13166,0.13181],"object_pos_start":[0.52673,0.0302,0.16381],"object_to_goal_dist_end":0.05715,"object_to_goal_dist_start":0.17526,"object_z_max":0.16386,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19704.0,"raw_peak_contact_force":0.26124,"subtask_id":"reach_goal","tcp_end":[0.56886,0.1267,0.19544],"tcp_start":[0.51692,0.02983,0.19262],"tcp_to_object_dist_end":0.06464,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59304,0.14971,0.01602],"object_pos_start":[0.57913,0.13166,0.13181],"object_to_goal_dist_end":0.09686,"object_to_goal_dist_start":0.05715,"object_z_max":0.13181,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7537.0,"raw_peak_contact_force":1.63737,"subtask_id":"reach_goal","tcp_end":[0.58459,0.15739,0.13389],"tcp_start":[0.56886,0.1267,0.19544],"tcp_to_object_dist_end":0.11842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59304,0.14971,0.01602],"object_pos_start":[0.59304,0.14971,0.01602],"object_to_goal_dist_end":0.09686,"object_to_goal_dist_start":0.09686,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57824,0.15556,0.15522],"tcp_start":[0.58459,0.15739,0.13389],"tcp_to_object_dist_end":0.14011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":741.0,"n_steps_budget":810.0,"object_pos_end":[0.59304,0.14971,0.01602],"object_pos_start":[0.59304,0.14971,0.01602],"object_to_goal_dist_end":0.09686,"object_to_goal_dist_start":0.09686,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2964.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57587,0.15479,0.28919],"tcp_start":[0.57824,0.15556,0.15522],"tcp_to_object_dist_end":0.27376,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4978,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07061,"approach_object.approach_speed":0.06342,"descend_place.place_speed":0.04488,"descend_to_object.descend_speed":0.03538,"lift_object.lift_height":0.1513,"lift_object.lift_speed":0.09771,"retract_after_place.retract_height":0.14617,"retract_after_place.retract_speed":0.08163},"optimized_scores":{"best_composite_score":-0.0497,"best_fitness_score":0.5303,"best_task_score":0.14414},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2049.0,"contact_point_centroid":[0.52479,0.02404,-0.00249],"force_p95":0.18718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77971,"mean_force":0.146,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51673,0.04626,0.23264]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.50146,-0.01444,-0.00123],"force_p95":0.24868,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35754,"mean_force":0.05302,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49253,-0.01542,0.05319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9219.0,"contact_point_centroid":[0.49214,0.00317,0.10878],"force_p95":0.13159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34163,"mean_force":0.09076,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49017,-0.01537,0.11146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11145.0,"contact_point_centroid":[0.49128,-0.0338,0.10754],"force_p95":0.12433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32458,"mean_force":0.07615,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49015,-0.01537,0.10955]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3367.0,"contact_point_centroid":[0.50236,0.02179,0.19621],"force_p95":0.12655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22777,"mean_force":0.10521,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4965,0.00349,0.20046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3785.0,"contact_point_centroid":[0.50208,-0.0143,0.1964],"force_p95":0.12114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16988,"mean_force":0.09305,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49661,0.00378,0.20065]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5038,-0.01568,-0.00209],"force_p95":0.14548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15205,"mean_force":0.12949,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49457,-0.01545,0.05179]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.1323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49874,-0.00696,0.21962]},{"body_a":"world","body_b":"grasp_target","contact_count":2188.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49762,-0.01489,0.09446]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52488,0.02405,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53215,0.08324,0.24095]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52488,0.02405,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53708,0.09922,0.2432]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52488,0.02405,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.53386,0.09852,0.32825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4788.0,"contact_point_centroid":[0.49528,0.00359,0.05096],"force_p95":0.09986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10434,"mean_force":0.05684,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4941,-0.01544,0.05127]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5590.0,"contact_point_centroid":[0.49422,-0.03424,0.05116],"force_p95":0.07657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08392,"mean_force":0.04627,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4941,-0.01544,0.05127]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1970.0,"contact_point_centroid":[0.51783,0.04817,0.23629],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01555,"mean_force":0.0105,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51765,0.04817,0.2341]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.53962,0.09968,0.24051],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53916,0.09967,0.23818]}],"total_contact_groups":17},"final_pose_error":0.01401,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52488,0.02405,0.01602],"final_tcp_position":[0.53453,0.0986,0.39587],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":272996.17803,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49964,-0.01428,0.13895],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49885,-0.01551,0.05653],"tcp_start":[0.49964,-0.01428,0.13895],"tcp_to_object_dist_end":0.03091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01532,0.02558],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31235,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14805,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12182.0,"raw_peak_contact_force":0.15205,"tcp_end":[0.49408,-0.01544,0.05125],"tcp_start":[0.49408,-0.01544,0.05125],"tcp_to_object_dist_end":0.02742,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.49653,-0.01522,0.15552],"object_pos_start":[0.50372,-0.01533,0.02554],"object_to_goal_dist_end":0.24045,"object_to_goal_dist_start":0.31238,"object_z_max":0.1554,"peak_contact_force":167951.73011,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20510.0,"raw_peak_contact_force":0.35754,"tcp_end":[0.49052,-0.01537,0.19058],"tcp_start":[0.49408,-0.01544,0.05125],"tcp_to_object_dist_end":0.03557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52488,0.02405,0.01602],"object_pos_start":[0.49653,-0.01522,0.15552],"object_to_goal_dist_end":0.29054,"object_to_goal_dist_start":0.24045,"object_z_max":0.17332,"peak_contact_force":272996.17803,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11171.0,"raw_peak_contact_force":1.77971,"subtask_id":"reach_goal","tcp_end":[0.52574,0.06484,0.24691],"tcp_start":[0.49052,-0.01537,0.19058],"tcp_to_object_dist_end":0.23446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52488,0.02405,0.01602],"object_pos_start":[0.52488,0.02405,0.01602],"object_to_goal_dist_end":0.29054,"object_to_goal_dist_start":0.29054,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8277.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.54032,0.09983,0.24057],"tcp_start":[0.52574,0.06484,0.24691],"tcp_to_object_dist_end":0.2375,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52488,0.02405,0.01602],"object_pos_start":[0.52488,0.02405,0.01602],"object_to_goal_dist_end":0.29054,"object_to_goal_dist_start":0.29054,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5359,0.09895,0.26363],"tcp_start":[0.54032,0.09983,0.24057],"tcp_to_object_dist_end":0.25893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52488,0.02405,0.01602],"object_pos_start":[0.52488,0.02405,0.01602],"object_to_goal_dist_end":0.29054,"object_to_goal_dist_start":0.29054,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53453,0.0986,0.39587],"tcp_start":[0.5359,0.09895,0.26363],"tcp_to_object_dist_end":0.38722,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48066,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.10945,"approach_object.approach_speed":0.09422,"descend_place.place_speed":0.04328,"descend_to_object.descend_speed":0.06188,"lift_object.lift_height":0.10994,"lift_object.lift_speed":0.06085,"retract_after_place.retract_height":0.12563,"retract_after_place.retract_speed":0.07403},"optimized_scores":{"best_composite_score":0.07199,"best_fitness_score":0.65199,"best_task_score":0.37775},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2883.0,"contact_point_centroid":[0.57082,0.13428,-0.00231],"force_p95":0.12646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39954,"mean_force":0.13618,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56906,0.11739,0.16909]},{"body_a":"world","body_b":"grasp_target","contact_count":195.0,"contact_point_centroid":[0.50839,0.0381,-0.0012],"force_p95":0.22126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41037,"mean_force":0.07099,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50096,0.03867,0.04936]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19662.0,"contact_point_centroid":[0.49851,0.0573,0.09595],"force_p95":0.07835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29786,"mean_force":0.05127,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49862,0.03849,0.09536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15965.0,"contact_point_centroid":[0.49752,0.01936,0.09402],"force_p95":0.10752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28699,"mean_force":0.06326,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49862,0.03849,0.0937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1733.0,"contact_point_centroid":[0.56227,0.08641,0.17359],"force_p95":0.15799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24846,"mean_force":0.10579,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55709,0.10473,0.17871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12232.0,"contact_point_centroid":[0.52558,0.08693,0.16025],"force_p95":0.12265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21344,"mean_force":0.07645,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52431,0.06843,0.16237]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51253,0.03958,-0.0021],"force_p95":0.14516,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19188,"mean_force":0.12978,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5033,0.03887,0.0482]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10809.0,"contact_point_centroid":[0.52811,0.05171,0.16049],"force_p95":0.11359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18836,"mean_force":0.08514,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52602,0.07022,0.16362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1959.0,"contact_point_centroid":[0.56223,0.12292,0.17358],"force_p95":0.11395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17776,"mean_force":0.09218,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55722,0.10489,0.17854]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50279,0.01779,0.21864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.50207,0.01963,0.04894],"force_p95":0.07863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13804,"mean_force":0.05228,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5028,0.03883,0.04764]},{"body_a":"world","body_b":"grasp_target","contact_count":2476.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50623,0.03787,0.08788]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57081,0.13431,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57325,0.12477,0.16576]},{"body_a":"world","body_b":"grasp_target","contact_count":3768.0,"contact_point_centroid":[0.57081,0.13431,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.56866,0.12364,0.24127]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5928.0,"contact_point_centroid":[0.50291,0.0579,0.04882],"force_p95":0.07111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07178,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5028,0.03883,0.04764]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2749.0,"contact_point_centroid":[0.57039,0.11822,0.17082],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01575,"mean_force":0.01063,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56988,0.1182,0.1686]}],"total_contact_groups":17},"final_pose_error":0.01265,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57081,0.13431,0.01602],"final_tcp_position":[0.5692,0.12372,0.29905],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.39954,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50772,0.0363,0.13787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2476.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50756,0.03922,0.05302],"tcp_start":[0.50772,0.0363,0.13787],"tcp_to_object_dist_end":0.02745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03898,0.0257],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2129,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14222,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12683.0,"raw_peak_contact_force":0.19188,"tcp_end":[0.50278,0.03883,0.04761],"tcp_start":[0.50278,0.03883,0.04761],"tcp_to_object_dist_end":0.02395,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50055,0.03934,0.11661],"object_pos_start":[0.51244,0.03895,0.02571],"object_to_goal_dist_end":0.18622,"object_to_goal_dist_start":0.21291,"object_z_max":0.1165,"peak_contact_force":0.11361,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35822.0,"raw_peak_contact_force":0.41037,"tcp_end":[0.49874,0.03851,0.14551],"tcp_start":[0.50278,0.03883,0.04761],"tcp_to_object_dist_end":0.02897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56176,0.10184,0.14924],"object_pos_start":[0.50055,0.03934,0.11661],"object_to_goal_dist_end":0.09666,"object_to_goal_dist_start":0.18622,"object_z_max":0.14918,"peak_contact_force":0.1153,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23041.0,"raw_peak_contact_force":0.21344,"subtask_id":"reach_goal","tcp_end":[0.55633,0.10165,0.18595],"tcp_start":[0.49874,0.03851,0.14551],"tcp_to_object_dist_end":0.03711,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57081,0.13431,0.01602],"object_pos_start":[0.56176,0.10184,0.14924],"object_to_goal_dist_end":0.14603,"object_to_goal_dist_start":0.09666,"object_z_max":0.14924,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9324.0,"raw_peak_contact_force":1.39954,"subtask_id":"reach_goal","tcp_end":[0.57745,0.12574,0.164],"tcp_start":[0.55633,0.10165,0.18595],"tcp_to_object_dist_end":0.14838,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57081,0.13431,0.01602],"object_pos_start":[0.57081,0.13431,0.01602],"object_to_goal_dist_end":0.14603,"object_to_goal_dist_start":0.14603,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57162,0.12436,0.18581],"tcp_start":[0.57745,0.12574,0.164],"tcp_to_object_dist_end":0.17009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":942.0,"n_steps_budget":1000.0,"object_pos_end":[0.57081,0.13431,0.01602],"object_pos_start":[0.57081,0.13431,0.01602],"object_to_goal_dist_end":0.14603,"object_to_goal_dist_start":0.14603,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3768.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5692,0.12372,0.29905],"tcp_start":[0.57162,0.12436,0.18581],"tcp_to_object_dist_end":0.28323,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```