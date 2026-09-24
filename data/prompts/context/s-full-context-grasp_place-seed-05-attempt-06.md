## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.0354 | 0.25 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.0215 | 0.28 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1979 | 0.22 | ✅ accepted |
| 3 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.035) — your mutation base

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
  weight: 0.3
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_goal
  target_entity: object
  weight: 0.3
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
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
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
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
  parameters:
    grasp_timeout:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: grasp_object
- id: lift_object
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
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    move_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
  parameters:
    release_timeout:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_after_place
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
    - 0.1
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - move_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.035
- **task_score** (E): 0.253
- **fitness_score**: 0.495  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1659 |
| descend_to_grasp | 1.00 | 1.00 | 0.0737 |
| grasp_object | 1.00 | 1.00 | 0.0120 |
| lift_object | 1.00 | 1.00 | 0.1055 |
| approach_goal | 0.00 | 1.00 | 0.0001 |
| descend_to_place | 0.50 | 1.00 | 0.1026 |
| release_object | 1.00 | 1.00 | 0.0235 |
| retract_after_place | 1.00 | 1.00 | 0.1168 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.510, 0.018, 0.064) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.064)→(0.502, 0.017, 0.055) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 26.667 | 0.144 | 0.193 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.055)→(0.511, 0.018, 0.160) | (0.516, 0.018, 0.026)→(0.517, 0.025, 0.083) | 0.236→0.207 | 1.00 / 13.667 | 0.114 | 0.615 |
| approach_goal | approach | 0.00 / guard_failure | (0.518, 0.026, 0.158)→(0.518, 0.026, 0.159) | (0.518, 0.007, 0.116)→(0.526, 0.026, 0.115) | 0.209→0.190 | 1.00 / 1.000 | 0.006 | 0.212 |
| descend_to_place | descend | 0.50 / step_budget | (0.518, 0.026, 0.159)→(0.558, 0.113, 0.153) | (0.526, 0.026, 0.114)→(0.542, 0.029, 0.016) | 0.190→0.230 | 1.00 / 8.500 | 141377.958 | 1.370 |
| release_object | release | 1.00 / step_budget | (0.558, 0.113, 0.153)→(0.552, 0.112, 0.175) | (0.542, 0.029, 0.016)→(0.542, 0.029, 0.016) | 0.230→0.230 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.552, 0.112, 0.175)→(0.589, 0.178, 0.264) | (0.542, 0.029, 0.016)→(0.542, 0.029, 0.016) | 0.230→0.230 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.377
- phase_score: 0.583
- phase_breakdown.grasp_object_score: 0.571
- phase_breakdown.reach_goal_score: 0.467
- phase_breakdown.approach_object_score: 0.821
- phase_breakdown.lift_object_score: 0.538
- grasp_place_fitness: 0.641

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.641
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.377
- **Median Q (composite search score)**: -0.017
- **K-run variance**: 0.0162
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54651,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.move_speed":0.0954,"approach_object.approach_speed":0.31683,"descend_to_grasp.descend_speed":0.07859,"descend_to_place.place_speed":0.03056,"grasp_object.grasp_timeout":0.74162,"lift_object.lift_height":0.13626,"release_object.release_timeout":0.21245},"optimized_scores":{"best_composite_score":0.11065,"best_fitness_score":0.64065,"best_task_score":0.37695},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3772.0,"contact_point_centroid":[0.55897,0.07304,-0.00219],"force_p95":0.12473,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3223,"mean_force":0.133,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55964,0.10797,0.12619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5915.0,"contact_point_centroid":[0.52241,0.01108,0.09525],"force_p95":0.13163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31382,"mean_force":0.09744,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51909,0.02943,0.09866]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6078.0,"contact_point_centroid":[0.52229,0.04773,0.09531],"force_p95":0.13134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27275,"mean_force":0.0948,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51914,0.02943,0.09875]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.5293,0.02912,-0.00118],"force_p95":0.21282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26962,"mean_force":0.0432,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51577,0.02943,0.05639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1585.0,"contact_point_centroid":[0.53535,0.02364,0.14552],"force_p95":0.14394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21757,"mean_force":0.111,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52919,0.04193,0.14995]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03071,-0.00209],"force_p95":0.15171,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20476,"mean_force":0.1297,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5181,0.02961,0.05588]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1886.0,"contact_point_centroid":[0.535,0.06014,0.14564],"force_p95":0.12111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14637,"mean_force":0.09172,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52929,0.04217,0.15002]},{"body_a":"world","body_b":"grasp_target","contact_count":1884.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51099,0.01392,0.21769]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52337,0.02904,0.10035]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55912,0.07302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5758,0.1458,0.11311]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.55912,0.07302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58355,0.1601,0.16191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2482.0,"contact_point_centroid":[0.51833,0.01078,0.0518],"force_p95":0.10474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11106,"mean_force":0.08103,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51695,0.02953,0.05453]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2992.0,"contact_point_centroid":[0.51745,0.04818,0.05141],"force_p95":0.09426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09442,"mean_force":0.0692,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51695,0.02953,0.05454]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3685.0,"contact_point_centroid":[0.56188,0.11177,0.12694],"force_p95":0.01112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56162,0.11175,0.1247]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.54195,0.06639,0.14565],"force_p95":0.01359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.01359,"mean_force":0.01359,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53396,0.05341,0.15276]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57931,0.14673,0.11095],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57898,0.14671,0.10876]}],"total_contact_groups":16},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.55912,0.07302,0.01602],"final_tcp_position":[0.59601,0.1751,0.19462],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9749.14396,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5242,0.0282,0.13715],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":928.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52494,0.03005,0.06407],"tcp_start":[0.5242,0.0282,0.13715],"tcp_to_object_dist_end":0.03846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02989,0.02568],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18426,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14802,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7274.0,"raw_peak_contact_force":0.20476,"subtask_id":"grasp_object","tcp_end":[0.51692,0.02953,0.0545],"tcp_start":[0.52494,0.03005,0.06407],"tcp_to_object_dist_end":0.03185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53167,0.02986,0.11319],"object_pos_start":[0.53046,0.02989,0.02568],"object_to_goal_dist_end":0.16439,"object_to_goal_dist_start":0.18426,"object_z_max":0.11307,"peak_contact_force":0.11364,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12145.0,"raw_peak_contact_force":0.31382,"subtask_id":"lift_object","tcp_end":[0.52566,0.02961,0.14941],"tcp_start":[0.51692,0.02953,0.0545],"tcp_to_object_dist_end":0.03672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.54199,0.05682,0.10906],"object_pos_start":[0.53167,0.02986,0.11319],"object_to_goal_dist_end":0.13555,"object_to_goal_dist_start":0.16439,"object_z_max":0.1139,"peak_contact_force":0.01198,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3471.0,"raw_peak_contact_force":0.21757,"subtask_id":"reach_goal","tcp_end":[0.53396,0.05341,0.15276],"tcp_start":[0.53396,0.05336,0.15277],"tcp_to_object_dist_end":0.04456,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55912,0.07302,0.01602],"object_pos_start":[0.54213,0.05701,0.10853],"object_to_goal_dist_end":0.14635,"object_to_goal_dist_start":0.13531,"object_z_max":0.10853,"peak_contact_force":9749.14396,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7458.0,"raw_peak_contact_force":1.3223,"subtask_id":"reach_goal","tcp_end":[0.58061,0.14697,0.1114],"tcp_start":[0.53396,0.05341,0.15276],"tcp_to_object_dist_end":0.12259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55912,0.07302,0.01602],"object_pos_start":[0.55912,0.07302,0.01602],"object_to_goal_dist_end":0.14635,"object_to_goal_dist_start":0.14635,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5739,0.14526,0.13316],"tcp_start":[0.58061,0.14697,0.1114],"tcp_to_object_dist_end":0.13841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.55912,0.07302,0.01602],"object_pos_start":[0.55912,0.07302,0.01602],"object_to_goal_dist_end":0.14635,"object_to_goal_dist_start":0.14635,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59601,0.1751,0.19462],"tcp_start":[0.5739,0.14526,0.13316],"tcp_to_object_dist_end":0.209,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7351,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.move_speed":0.10904,"approach_object.approach_speed":0.33731,"descend_to_grasp.descend_speed":0.08667,"descend_to_place.place_speed":0.04983,"grasp_object.grasp_timeout":0.75336,"lift_object.lift_height":0.14277,"release_object.release_timeout":0.20618},"optimized_scores":{"best_composite_score":-0.01703,"best_fitness_score":0.51297,"best_task_score":0.12335},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3749.0,"contact_point_centroid":[0.52395,-0.01435,-0.0022],"force_p95":0.12744,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4187,"mean_force":0.13404,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51903,0.04488,0.17922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5950.0,"contact_point_centroid":[0.49545,0.00308,0.09702],"force_p95":0.13736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27585,"mean_force":0.10016,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49283,-0.01526,0.10085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6316.0,"contact_point_centroid":[0.4956,-0.0335,0.09767],"force_p95":0.12715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2754,"mean_force":0.09491,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49288,-0.01526,0.10157]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.50251,-0.01516,-0.0011],"force_p95":0.22742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26846,"mean_force":0.04082,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49,-0.01525,0.05762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.5058,0.00908,0.15455],"force_p95":0.15704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20705,"mean_force":0.11252,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49971,-0.00909,0.15949]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01566,-0.00204],"force_p95":0.13362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16564,"mean_force":0.12566,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49222,-0.01528,0.05704]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.50576,-0.02634,0.15512],"force_p95":0.12524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16427,"mean_force":0.09635,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49984,-0.00845,0.15989]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49888,-0.00701,0.21904]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49818,-0.0148,0.10149]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52404,-0.01434,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53112,0.07907,0.19723]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52404,-0.01434,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.55447,0.1301,0.27338]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3058.0,"contact_point_centroid":[0.49103,0.0035,0.0528],"force_p95":0.09072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10163,"mean_force":0.06726,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49111,-0.01526,0.05582]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2944.0,"contact_point_centroid":[0.49137,-0.03408,0.05249],"force_p95":0.09218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09255,"mean_force":0.07041,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49111,-0.01526,0.05582]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.50949,-0.015,0.15726],"force_p95":0.04175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04175,"mean_force":0.04175,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5015,-0.00178,0.16427]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3683.0,"contact_point_centroid":[0.52046,0.04769,0.18273],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52027,0.04769,0.18038]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.53387,0.07952,0.19439],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53361,0.07952,0.19204]}],"total_contact_groups":16},"final_pose_error":0.01779,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52404,-0.01434,0.01602],"final_tcp_position":[0.58167,0.18042,0.33264],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273006.77234,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49966,-0.01428,0.13881],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":956.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.49883,-0.01537,0.06444],"tcp_start":[0.49966,-0.01428,0.13881],"tcp_to_object_dist_end":0.03874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01542,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3122,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13307,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7802.0,"raw_peak_contact_force":0.16564,"subtask_id":"grasp_object","tcp_end":[0.49108,-0.01526,0.05579],"tcp_start":[0.49883,-0.01537,0.06444],"tcp_to_object_dist_end":0.0325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50507,-0.01569,0.11917],"object_pos_start":[0.50375,-0.01542,0.02586],"object_to_goal_dist_end":0.25415,"object_to_goal_dist_start":0.3122,"object_z_max":0.11905,"peak_contact_force":0.11363,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12405.0,"raw_peak_contact_force":0.27585,"subtask_id":"lift_object","tcp_end":[0.49918,-0.01534,0.1566],"tcp_start":[0.49108,-0.01526,0.05579],"tcp_to_object_dist_end":0.03789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.50922,-0.00537,0.12049],"object_pos_start":[0.50507,-0.01569,0.11917],"object_to_goal_dist_end":0.24393,"object_to_goal_dist_start":0.25415,"object_z_max":0.12399,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1888.0,"raw_peak_contact_force":0.20705,"subtask_id":"reach_goal","tcp_end":[0.5015,-0.00178,0.16427],"tcp_start":[0.50143,-0.00186,0.16422],"tcp_to_object_dist_end":0.0446,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52404,-0.01434,0.01602],"object_pos_start":[0.50935,-0.00541,0.12004],"object_to_goal_dist_end":0.31391,"object_to_goal_dist_start":0.24416,"object_z_max":0.12004,"peak_contact_force":273006.77234,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7433.0,"raw_peak_contact_force":1.4187,"subtask_id":"reach_goal","tcp_end":[0.53483,0.07954,0.19418],"tcp_start":[0.5015,-0.00178,0.16427],"tcp_to_object_dist_end":0.20167,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52404,-0.01434,0.01602],"object_pos_start":[0.52404,-0.01434,0.01602],"object_to_goal_dist_end":0.31391,"object_to_goal_dist_start":0.31391,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52968,0.07882,0.21784],"tcp_start":[0.53483,0.07954,0.19418],"tcp_to_object_dist_end":0.22236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52404,-0.01434,0.01602],"object_pos_start":[0.52404,-0.01434,0.01602],"object_to_goal_dist_end":0.31391,"object_to_goal_dist_start":0.31391,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58167,0.18042,0.33264],"tcp_start":[0.52968,0.07882,0.21784],"tcp_to_object_dist_end":0.37617,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17143,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.move_speed":0.1,"approach_object.approach_speed":0.32227,"descend_to_grasp.descend_speed":0.07984,"descend_to_place.place_speed":0.05345,"grasp_object.grasp_timeout":0.64182,"lift_object.lift_height":0.1617,"release_object.release_timeout":0.29102},"optimized_scores":{"best_composite_score":-0.19993,"best_fitness_score":0.33007,"best_task_score":0.25738},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":441.0,"contact_point_centroid":[0.51343,0.05402,-0.00366],"force_p95":0.70391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25616,"mean_force":0.17418,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50441,0.03835,0.13187]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5279.0,"contact_point_centroid":[0.50332,0.05618,0.09597],"force_p95":0.14677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32193,"mean_force":0.10744,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50046,0.03811,0.10023]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5280.0,"contact_point_centroid":[0.50227,0.02001,0.09292],"force_p95":0.15635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27803,"mean_force":0.10673,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5002,0.0381,0.09709]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03968,-0.00211],"force_p95":0.15581,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21008,"mean_force":0.13094,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50062,0.03825,0.05661]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50279,0.01785,0.21836]},{"body_a":"world","body_b":"grasp_target","contact_count":948.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50634,0.03742,0.10089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2869.0,"contact_point_centroid":[0.49971,0.01946,0.05197],"force_p95":0.09263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11049,"mean_force":0.07094,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4995,0.03816,0.05535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2808.0,"contact_point_centroid":[0.50037,0.05697,0.05188],"force_p95":0.09943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10453,"mean_force":0.07375,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49951,0.03816,0.05535]}],"total_contact_groups":8},"final_pose_error":0.01295,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51472,0.06214,0.01647],"final_tcp_position":[0.50817,0.03855,0.1751],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.25616,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50764,0.03626,0.13799],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":948.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.50731,0.03878,0.06429],"tcp_start":[0.50764,0.03626,0.13799],"tcp_to_object_dist_end":0.03863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03888,0.02561],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21299,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15202,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7477.0,"raw_peak_contact_force":0.21008,"subtask_id":"grasp_object","tcp_end":[0.49947,0.03815,0.05531],"tcp_start":[0.50731,0.03878,0.06429],"tcp_to_object_dist_end":0.03244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.51472,0.06214,0.01647],"object_pos_start":[0.51248,0.03888,0.02561],"object_to_goal_dist_end":0.20358,"object_to_goal_dist_start":0.21299,"object_z_max":0.11142,"peak_contact_force":0.11517,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11000.0,"raw_peak_contact_force":1.25616,"subtask_id":"lift_object","tcp_end":[0.50817,0.03855,0.1751],"tcp_start":[0.49947,0.03815,0.05531],"tcp_to_object_dist_end":0.16051,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```