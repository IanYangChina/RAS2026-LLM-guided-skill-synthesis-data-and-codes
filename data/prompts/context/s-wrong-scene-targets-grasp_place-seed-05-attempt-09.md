## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1989 | 0.30 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1922 | 0.29 | ✅ accepted |
| 7 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.1719 | 0.22 | ❌ rejected |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.530500292374538, 0.030794078973649372, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.530500292374538, 0.030794078973649372, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.199) — your mutation base

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
  weight: 0.25
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.35
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
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
    entity: grasp_target
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
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.0
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
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: lift
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: approach_goal
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
    - 0.1
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_place
  type: descend
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
    - 0.02
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
    - -0.05
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.199
- **task_score** (E): 0.304
- **fitness_score**: 0.629  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1658 |
| descend_to_grasp | 1.00 | 1.00 | 0.1070 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1062 |
| approach_goal | 0.67 | 1.00 | 0.2001 |
| descend_to_place | 1.00 | 1.00 | 0.0603 |
| release | 1.00 | 1.00 | 0.0212 |
| retract | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.017, 0.138)→(0.510, 0.018, 0.031) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, 0.018, 0.031)→(0.502, 0.017, 0.022) | (0.516, 0.018, 0.026)→(0.515, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.333 | 0.145 | 0.216 |
| lift | lift | 1.00 / step_budget | (0.502, 0.017, 0.022)→(0.498, 0.017, 0.128) | (0.515, 0.017, 0.026)→(0.517, 0.017, 0.119) | 0.237→0.201 | 1.00 / 24.667 | 0.078 | 0.782 |
| approach_goal | approach | 0.67 / step_budget | (0.498, 0.017, 0.128)→(0.589, 0.155, 0.234) | (0.517, 0.017, 0.119)→(0.528, 0.093, 0.016) | 0.201→0.192 | 1.00 / 8.333 | 94252.392 | 1.534 |
| descend_to_place | descend | 1.00 / step_budget | (0.589, 0.155, 0.234)→(0.599, 0.175, 0.189) | (0.528, 0.093, 0.016)→(0.528, 0.093, 0.016) | 0.192→0.192 | 1.00 / 8.333 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.599, 0.175, 0.189)→(0.594, 0.174, 0.210) | (0.528, 0.093, 0.016)→(0.528, 0.093, 0.016) | 0.192→0.192 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.594, 0.174, 0.210)→(0.591, 0.172, 0.169) | (0.528, 0.093, 0.016)→(0.528, 0.093, 0.016) | 0.192→0.192 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.436
- phase_score: 0.418
- phase_breakdown.reach_object_score: 0.138
- phase_breakdown.reach_goal_score: 0.608
- phase_breakdown.lift_object_score: 0.400
- grasp_place_fitness: 0.695

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.695
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.436
- **Median Q (composite search score)**: 0.210
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.222


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
{"anchors":[{"name":"object","value":[0.60153,0.17858,0.10809]},{"name":"goal","value":[0.5305,0.03079,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62755,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09389,"approach_object.approach_speed":0.08239,"descend_to_grasp.descend_speed":0.07611,"descend_to_place.place_speed":0.03442,"lift.lift_height":0.12846},"optimized_scores":{"best_composite_score":0.26499,"best_fitness_score":0.69499,"best_task_score":0.43555},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2203.0,"contact_point_centroid":[0.53837,0.1232,-0.00235],"force_p95":0.171,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46944,"mean_force":0.14468,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56909,0.12976,0.17823]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.52731,0.02871,-0.00118],"force_p95":0.58974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79492,"mean_force":0.10712,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51491,0.02952,0.02368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10696.0,"contact_point_centroid":[0.51518,0.01056,0.0762],"force_p95":0.11087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33145,"mean_force":0.0696,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51225,0.02935,0.07499]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10728.0,"contact_point_centroid":[0.51553,0.04817,0.07387],"force_p95":0.10855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33037,"mean_force":0.07003,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51229,0.02935,0.0725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2481.0,"contact_point_centroid":[0.52646,0.0707,0.14022],"force_p95":0.17963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27622,"mean_force":0.10791,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5235,0.0527,0.14435]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2222.0,"contact_point_centroid":[0.52523,0.03186,0.13953],"force_p95":0.1701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24856,"mean_force":0.10508,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52204,0.05003,0.14332]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03046,-0.0021],"force_p95":0.15438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24211,"mean_force":0.13131,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5178,0.02972,0.02328]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51092,0.01384,0.21815]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4059.0,"contact_point_centroid":[0.51741,0.01044,0.02466],"force_p95":0.07982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13523,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51656,0.02964,0.0219]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52318,0.02935,0.06986]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53815,0.12336,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59438,0.17418,0.15145]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53815,0.12336,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59119,0.17433,0.13497]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.53815,0.12336,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58725,0.17309,0.13558]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4976.0,"contact_point_centroid":[0.51735,0.04878,0.0237],"force_p95":0.07207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0913,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51656,0.02964,0.02191]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2106.0,"contact_point_centroid":[0.57216,0.13412,0.18245],"force_p95":0.01124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01705,"mean_force":0.01062,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57172,0.13411,0.18021]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4209.0,"contact_point_centroid":[0.59484,0.17421,0.1537],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01058,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59437,0.17418,0.15148]}],"total_contact_groups":17},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53815,0.12336,0.01602],"final_tcp_position":[0.58551,0.17252,0.1136],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.46944,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52413,0.02817,0.13724],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52487,0.0302,0.0312],"tcp_start":[0.52413,0.02817,0.13724],"tcp_to_object_dist_end":0.00767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53035,0.02954,0.02565],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1846,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14683,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10835.0,"raw_peak_contact_force":0.24211,"tcp_end":[0.51653,0.02963,0.02187],"tcp_start":[0.52487,0.0302,0.0312],"tcp_to_object_dist_end":0.01433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.53148,0.02947,0.12671],"object_pos_start":[0.53035,0.02954,0.02565],"object_to_goal_dist_end":0.16579,"object_to_goal_dist_start":0.1846,"object_z_max":0.12662,"peak_contact_force":0.12414,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21566.0,"raw_peak_contact_force":0.79492,"subtask_id":"lift_object","tcp_end":[0.51246,0.02937,0.13796],"tcp_start":[0.51653,0.02963,0.02187],"tcp_to_object_dist_end":0.02209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.53815,0.12336,0.01602],"object_pos_start":[0.53148,0.02947,0.12671],"object_to_goal_dist_end":0.12467,"object_to_goal_dist_start":0.16579,"object_z_max":0.12872,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9012.0,"raw_peak_contact_force":1.46944,"subtask_id":"reach_goal","tcp_end":[0.59434,0.17149,0.19712],"tcp_start":[0.51246,0.02937,0.13796],"tcp_to_object_dist_end":0.19563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53815,0.12336,0.01602],"object_pos_start":[0.53815,0.12336,0.01602],"object_to_goal_dist_end":0.12467,"object_to_goal_dist_start":0.12467,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8209.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59577,0.17579,0.13402],"tcp_start":[0.59434,0.17149,0.19712],"tcp_to_object_dist_end":0.1414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53815,0.12336,0.01602],"object_pos_start":[0.53815,0.12336,0.01602],"object_to_goal_dist_end":0.12467,"object_to_goal_dist_start":0.12467,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5894,0.17373,0.15467],"tcp_start":[0.59577,0.17579,0.13402],"tcp_to_object_dist_end":0.15617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":123.0,"n_steps_budget":600.0,"object_pos_end":[0.53815,0.12336,0.01602],"object_pos_start":[0.53815,0.12336,0.01602],"object_to_goal_dist_end":0.12467,"object_to_goal_dist_start":0.12467,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":492.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58551,0.17252,0.1136],"tcp_start":[0.5894,0.17373,0.15467],"tcp_to_object_dist_end":0.11909,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8631,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.1425,"approach_object.approach_speed":0.0889,"descend_to_grasp.descend_speed":0.07797,"descend_to_place.place_speed":0.09349,"lift.lift_height":0.10982},"optimized_scores":{"best_composite_score":0.1215,"best_fitness_score":0.5515,"best_task_score":0.15123},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2659.0,"contact_point_centroid":[0.5084,0.04523,-0.00232],"force_p95":0.13167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58113,"mean_force":0.14098,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53214,0.08278,0.22233]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.50073,-0.01554,-0.00111],"force_p95":0.70578,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86831,"mean_force":0.10768,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4892,-0.01542,0.0195]},{"body_a":"grasp_target","body_b":"hand","contact_count":85.0,"contact_point_centroid":[0.50576,0.00467,0.06118],"force_p95":0.0685,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30495,"mean_force":0.03816,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48803,-0.01541,0.02334]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9115.0,"contact_point_centroid":[0.48923,0.00353,0.06436],"force_p95":0.10672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3047,"mean_force":0.06905,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48655,-0.01538,0.06251]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2849.0,"contact_point_centroid":[0.49748,0.02392,0.13335],"force_p95":0.17922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28544,"mean_force":0.10646,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49397,0.00583,0.13581]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9726.0,"contact_point_centroid":[0.48896,-0.0342,0.0618],"force_p95":0.10926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28115,"mean_force":0.06525,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48659,-0.01538,0.06064]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2573.0,"contact_point_centroid":[0.49632,-0.01498,0.13074],"force_p95":0.1908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27383,"mean_force":0.10432,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49288,0.00338,0.13322]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50378,-0.01549,-0.00204],"force_p95":0.13279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16044,"mean_force":0.12625,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49192,-0.01546,0.01898]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4989,-0.00698,0.21956]},{"body_a":"world","body_b":"grasp_target","contact_count":2980.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49768,-0.01496,0.07418]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50829,0.04521,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56723,0.15474,0.26397]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50829,0.04521,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57823,0.17986,0.26182]},{"body_a":"world","body_b":"grasp_target","contact_count":484.0,"contact_point_centroid":[0.50829,0.04521,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57598,0.17902,0.26286]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49121,0.00375,0.02051],"force_p95":0.07609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09656,"mean_force":0.05161,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01544,0.01775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49126,-0.03452,0.01959],"force_p95":0.06795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09197,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01544,0.01775]},{"body_a":"grasp_target","body_b":"hand","contact_count":300.0,"contact_point_centroid":[0.50826,-0.02249,0.0557],"force_p95":0.01655,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04761,"mean_force":0.00932,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49078,-0.01544,0.01781]}],"total_contact_groups":19},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50829,0.04521,0.01602],"final_tcp_position":[0.57488,0.17861,0.241],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273008.03826,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1984.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49976,-0.01428,0.13902],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2980.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49882,-0.01554,0.02616],"tcp_start":[0.49976,-0.01428,0.13902],"tcp_to_object_dist_end":0.005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50356,-0.01531,0.02583],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3122,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13298,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11096.0,"raw_peak_contact_force":0.16044,"tcp_end":[0.49069,-0.01544,0.01772],"tcp_start":[0.49882,-0.01554,0.02616],"tcp_to_object_dist_end":0.01521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":604.0,"n_steps_budget":690.0,"object_pos_end":[0.50795,-0.01554,0.1105],"object_pos_start":[0.50356,-0.01531,0.02583],"object_to_goal_dist_end":0.25764,"object_to_goal_dist_start":0.3122,"object_z_max":0.1104,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19060.0,"raw_peak_contact_force":0.86831,"subtask_id":"lift_object","tcp_end":[0.48658,-0.01537,0.11569],"tcp_start":[0.49069,-0.01544,0.01772],"tcp_to_object_dist_end":0.02199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50829,0.04521,0.01602],"object_pos_start":[0.50795,-0.01554,0.1105],"object_to_goal_dist_end":0.28334,"object_to_goal_dist_start":0.25764,"object_z_max":0.13274,"peak_contact_force":273008.03826,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10665.0,"raw_peak_contact_force":1.58113,"subtask_id":"reach_goal","tcp_end":[0.5552,0.12802,0.2737],"tcp_start":[0.48658,-0.01537,0.11569],"tcp_to_object_dist_end":0.2747,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50829,0.04521,0.01602],"object_pos_start":[0.50829,0.04521,0.01602],"object_to_goal_dist_end":0.28334,"object_to_goal_dist_start":0.28334,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8262.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.58111,0.18085,0.26066],"tcp_start":[0.5552,0.12802,0.2737],"tcp_to_object_dist_end":0.28905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50829,0.04521,0.01602],"object_pos_start":[0.50829,0.04521,0.01602],"object_to_goal_dist_end":0.28334,"object_to_goal_dist_start":0.28334,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57722,0.17944,0.28158],"tcp_start":[0.58111,0.18085,0.26066],"tcp_to_object_dist_end":0.30543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":121.0,"n_steps_budget":600.0,"object_pos_end":[0.50829,0.04521,0.01602],"object_pos_start":[0.50829,0.04521,0.01602],"object_to_goal_dist_end":0.28334,"object_to_goal_dist_start":0.28334,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":484.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57488,0.17861,0.241],"tcp_start":[0.57722,0.17944,0.28158],"tcp_to_object_dist_end":0.2699,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27103,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.13768,"approach_object.approach_speed":0.06868,"descend_to_grasp.descend_speed":0.04504,"descend_to_place.place_speed":0.02876,"lift.lift_height":0.11629},"optimized_scores":{"best_composite_score":0.2103,"best_fitness_score":0.6403,"best_task_score":0.32375},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2716.0,"contact_point_centroid":[0.53724,0.10906,-0.00237],"force_p95":0.19122,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54998,"mean_force":0.14456,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5774,0.12424,0.19769]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.50943,0.03715,-0.00121],"force_p95":0.50536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6842,"mean_force":0.09356,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49737,0.03805,0.02893]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9923.0,"contact_point_centroid":[0.49757,0.019,0.07584],"force_p95":0.1068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32859,"mean_force":0.06821,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49479,0.03785,0.07409]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10403.0,"contact_point_centroid":[0.49764,0.05671,0.07425],"force_p95":0.10441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32736,"mean_force":0.06607,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49482,0.03785,0.07273]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1576.0,"contact_point_centroid":[0.51132,0.03332,0.13777],"force_p95":0.20477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3122,"mean_force":0.12176,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50611,0.05162,0.13941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2029.0,"contact_point_centroid":[0.51248,0.07117,0.13823],"force_p95":0.18353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30482,"mean_force":0.10728,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50756,0.0532,0.14055]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03939,-0.00214],"force_p95":0.16378,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24551,"mean_force":0.13359,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50018,0.03829,0.02838]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4054.0,"contact_point_centroid":[0.49969,0.01899,0.02987],"force_p95":0.08134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14791,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49898,0.03819,0.02708]},{"body_a":"world","body_b":"grasp_target","contact_count":2184.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50264,0.01776,0.21866]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50593,0.03785,0.07063]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53766,0.11014,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61912,0.16744,0.18814]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53766,0.11014,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61687,0.16786,0.17366]},{"body_a":"world","body_b":"grasp_target","contact_count":472.0,"contact_point_centroid":[0.53766,0.11014,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61342,0.16679,0.17422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5013.0,"contact_point_centroid":[0.49964,0.05737,0.02889],"force_p95":0.07389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08713,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49898,0.03819,0.02709]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2810.0,"contact_point_centroid":[0.57972,0.12614,0.20151],"force_p95":0.01129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01047,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57928,0.12612,0.19925]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4220.0,"contact_point_centroid":[0.61952,0.16746,0.19048],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01055,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61911,0.16743,0.18822]}],"total_contact_groups":17},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.53766,0.11014,0.01602],"final_tcp_position":[0.61181,0.16629,0.15223],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9749.01461,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2184.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50761,0.03628,0.1379],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50695,0.03885,0.03573],"tcp_start":[0.50761,0.03628,0.1379],"tcp_to_object_dist_end":0.01122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5124,0.0382,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2135,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15483,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10867.0,"raw_peak_contact_force":0.24551,"tcp_end":[0.49895,0.03819,0.02705],"tcp_start":[0.50695,0.03885,0.03573],"tcp_to_object_dist_end":0.01354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.51165,0.03795,0.11911],"object_pos_start":[0.5124,0.0382,0.02554],"object_to_goal_dist_end":0.17949,"object_to_goal_dist_start":0.2135,"object_z_max":0.11901,"peak_contact_force":0.10932,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20469.0,"raw_peak_contact_force":0.6842,"subtask_id":"lift_object","tcp_end":[0.49491,0.03787,0.13146],"tcp_start":[0.49895,0.03819,0.02705],"tcp_to_object_dist_end":0.0208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53766,0.11014,0.01602],"object_pos_start":[0.51165,0.03795,0.11911],"object_to_goal_dist_end":0.16917,"object_to_goal_dist_start":0.17949,"object_z_max":0.12825,"peak_contact_force":9749.01461,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9131.0,"raw_peak_contact_force":1.54998,"subtask_id":"reach_goal","tcp_end":[0.61733,0.16414,0.2304],"tcp_start":[0.49491,0.03787,0.13146],"tcp_to_object_dist_end":0.23499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53766,0.11014,0.01602],"object_pos_start":[0.53766,0.11014,0.01602],"object_to_goal_dist_end":0.16917,"object_to_goal_dist_start":0.16917,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8220.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62099,0.16914,0.17337],"tcp_start":[0.61733,0.16414,0.2304],"tcp_to_object_dist_end":0.18758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53766,0.11014,0.01602],"object_pos_start":[0.53766,0.11014,0.01602],"object_to_goal_dist_end":0.16917,"object_to_goal_dist_start":0.16917,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61529,0.16733,0.19302],"tcp_start":[0.62099,0.16914,0.17337],"tcp_to_object_dist_end":0.20156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":118.0,"n_steps_budget":600.0,"object_pos_end":[0.53766,0.11014,0.01602],"object_pos_start":[0.53766,0.11014,0.01602],"object_to_goal_dist_end":0.16917,"object_to_goal_dist_start":0.16917,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":472.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61181,0.16629,0.15223],"tcp_start":[0.61529,0.16733,0.19302],"tcp_to_object_dist_end":0.16494,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```