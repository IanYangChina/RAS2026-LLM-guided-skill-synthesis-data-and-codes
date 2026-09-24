## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0090 | 0.27 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1377 | 0.35 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0229 | 0.33 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.009) — your mutation base

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
  - 0.1
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
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
- id: approach_goal_1
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    goal1_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    goal1_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: approach_goal_2
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
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    goal2_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    goal2_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
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
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_offset_z: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal1_offset_z: status=consumed; consumers=target.offset.z (replace)
    - goal1_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal2_offset_z: status=consumed; consumers=target.offset.z (replace)
    - goal2_speed: status=consumed; consumers=generator.speed (replace)
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

- **Composite score**: -0.009
- **task_score** (E): 0.270
- **fitness_score**: 0.511  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1578 |
| descend | 1.00 | 1.00 | 0.0884 |
| grasp | 1.00 | 1.00 | 0.0118 |
| lift | 0.67 | 0.67 | 0.0882 |
| transport_to_goal | 0.33 | 1.00 | 0.0733 |
| release | 1.00 | 1.00 | 0.0231 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.146) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend | descend | 1.00 / step_budget | (0.510, 0.016, 0.146)→(0.511, 0.018, 0.058) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 39.000 | 0.140 | 0.184 |
| grasp | grasp | 1.00 / step_budget | (0.511, 0.018, 0.058)→(0.503, 0.018, 0.049) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 20.333 | 3249.688 | 0.458 |
| lift | lift | 0.67 / step_budget | (0.504, 0.018, 0.071)→(0.505, 0.024, 0.157) | (0.516, 0.018, 0.026)→(0.512, 0.024, 0.089) | 0.236→0.202 | 0.67 / 10.667 | 0.079 | 0.166 |
| transport_to_goal | approach | 0.33 / step_budget | (0.527, 0.055, 0.150)→(0.562, 0.114, 0.167) | (0.512, 0.024, 0.089)→(0.537, 0.068, 0.089) | 0.202→0.158 | 1.00 / 3.333 | 0.224 | 1.060 |
| release | release | 1.00 / step_budget | (0.562, 0.114, 0.167)→(0.556, 0.113, 0.190) | (0.537, 0.068, 0.089)→(0.540, 0.062, 0.021) | 0.158→0.204 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.347
- phase_score: 0.462
- phase_breakdown.approach_object_score: 0.886
- phase_breakdown.place_at_goal_score: 0.105
- phase_breakdown.grasp_object_score: 0.553
- phase_breakdown.lift_object_score: 0.660
- grasp_place_fitness: 0.640

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.640
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.347
- **Median Q (composite search score)**: 0.020
- **K-run variance**: 0.0142
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.367


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29327,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.15341,"approach_object.approach_speed":0.07045,"descend.descend_offset_z":0.04429,"descend.descend_speed":0.04731,"lift.lift_offset_z":0.14999,"lift.lift_speed":0.03373,"transport_to_goal.transport_offset_z":0.05072,"transport_to_goal.transport_speed":0.07596},"optimized_scores":{"best_composite_score":-0.16728,"best_fitness_score":0.35272,"best_task_score":0.30569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4974.0,"contact_point_centroid":[0.51158,0.04779,-0.00205],"force_p95":0.19264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55764,"mean_force":0.12737,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51544,0.03447,0.12305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4392.0,"contact_point_centroid":[0.51548,0.04812,0.06438],"force_p95":0.10925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29679,"mean_force":0.0787,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51547,0.02966,0.06845]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3867.0,"contact_point_centroid":[0.51467,0.011,0.06379],"force_p95":0.12756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22724,"mean_force":0.08803,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51545,0.02967,0.06798]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.03073,-0.00207],"force_p95":0.14462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1866,"mean_force":0.12792,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51895,0.02998,0.05824]},{"body_a":"world","body_b":"grasp_target","contact_count":1596.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51059,0.01329,0.24461]},{"body_a":"world","body_b":"grasp_target","contact_count":3964.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.5237,0.02919,0.11154]},{"body_a":"world","body_b":"grasp_target","contact_count":6804.0,"contact_point_centroid":[0.51091,0.04952,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55993,0.12586,0.15782]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51091,0.04952,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5917,0.17428,0.1514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2664.0,"contact_point_centroid":[0.51716,0.01108,0.05321],"force_p95":0.09797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10615,"mean_force":0.07662,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51777,0.0299,0.05684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3213.0,"contact_point_centroid":[0.51815,0.0486,0.05337],"force_p95":0.0881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08827,"mean_force":0.06472,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51778,0.0299,0.05685]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4737.0,"contact_point_centroid":[0.51577,0.03504,0.13129],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01049,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51532,0.03504,0.12901]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7211.0,"contact_point_centroid":[0.56037,0.12581,0.16008],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01289,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55988,0.12579,0.15783]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.59515,0.17527,0.14972],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01019,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59458,0.17524,0.14757]}],"total_contact_groups":13},"final_pose_error":0.01044,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.51091,0.04952,0.02602],"final_tcp_position":[0.59604,0.17564,0.15043],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.84353,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3964.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.52376,0.02735,0.18971],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1437,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7677.0,"raw_peak_contact_force":0.1866,"subtask_id":"grasp_object","tcp_end":[0.52561,0.03042,0.06619],"tcp_start":[0.52376,0.02735,0.18971],"tcp_to_object_dist_end":0.04047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03011,0.02574],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18406,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":9748.84353,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":17970.0,"raw_peak_contact_force":0.55764,"subtask_id":"grasp_object","tcp_end":[0.51775,0.0299,0.05681],"tcp_start":[0.52561,0.03042,0.06619],"tcp_to_object_dist_end":0.03356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1605.0,"n_steps_budget":1000.0,"object_pos_end":[0.51091,0.04952,0.02602],"object_pos_start":[0.53044,0.03011,0.02574],"object_to_goal_dist_end":0.17778,"object_to_goal_dist_start":0.18406,"object_z_max":0.04277,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14015.0,"raw_peak_contact_force":0.12263,"subtask_id":"lift_object","tcp_end":[0.5077,0.04807,0.17666],"tcp_start":[0.52099,0.02975,0.12138],"tcp_to_object_dist_end":0.15068,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1701.0,"n_steps_budget":1000.0,"object_pos_end":[0.51091,0.04952,0.02602],"object_pos_start":[0.51091,0.04952,0.02602],"object_to_goal_dist_end":0.17778,"object_to_goal_dist_start":0.17778,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.59604,0.17564,0.15043],"tcp_start":[0.57282,0.14317,0.15607],"tcp_to_object_dist_end":0.19655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51091,0.04952,0.02602],"object_pos_start":[0.51091,0.04952,0.02602],"object_to_goal_dist_end":0.17778,"object_to_goal_dist_start":0.17778,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1596.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.59,0.1737,0.17106],"tcp_start":[0.59604,0.17564,0.15043],"tcp_to_object_dist_end":0.20667,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.07986,"approach_object.approach_speed":0.06242,"descend.descend_offset_z":0.03001,"descend.descend_speed":0.06226,"lift.lift_offset_z":0.1292,"lift.lift_speed":0.06443,"transport_to_goal.transport_offset_z":0.02964,"transport_to_goal.transport_speed":0.0765},"optimized_scores":{"best_composite_score":0.02049,"best_fitness_score":0.54049,"best_task_score":0.15829},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":639.0,"contact_point_centroid":[0.54079,0.04483,-0.00354],"force_p95":0.69302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60497,"mean_force":0.18962,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52728,0.06733,0.19775]},{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.50171,-0.01506,-0.00114],"force_p95":0.23395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37303,"mean_force":0.05669,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48981,-0.01537,0.04929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15040.0,"contact_point_centroid":[0.49443,0.00369,0.09243],"force_p95":0.11674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26899,"mean_force":0.06402,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49273,-0.01534,0.09209]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17057.0,"contact_point_centroid":[0.49439,-0.03419,0.09312],"force_p95":0.08685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25725,"mean_force":0.05559,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49281,-0.01534,0.09278]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8510.0,"contact_point_centroid":[0.5188,0.04569,0.1639],"force_p95":0.13206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24423,"mean_force":0.10045,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51415,0.0274,0.16759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9438.0,"contact_point_centroid":[0.51789,0.00759,0.16355],"force_p95":0.1245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17669,"mean_force":0.09093,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51347,0.02572,0.16658]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01563,-0.00203],"force_p95":0.13249,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15979,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49223,-0.01541,0.04892]},{"body_a":"world","body_b":"grasp_target","contact_count":2340.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49865,-0.00708,0.2092]},{"body_a":"world","body_b":"grasp_target","contact_count":1744.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49767,-0.01499,0.08327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4364.0,"contact_point_centroid":[0.49155,0.00379,0.04908],"force_p95":0.07252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09975,"mean_force":0.04938,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01539,0.04767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.49151,-0.03452,0.04883],"force_p95":0.06839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08655,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01539,0.04767]}],"total_contact_groups":11},"final_pose_error":0.15637,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54058,0.04451,0.01601],"final_tcp_position":[0.53173,0.06787,0.19345],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.60497,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1744.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49953,-0.01443,0.11876],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13184,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11042.0,"raw_peak_contact_force":0.15979,"subtask_id":"grasp_object","tcp_end":[0.49882,-0.0155,0.05615],"tcp_start":[0.49953,-0.01443,0.11876],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01542,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3122,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13243,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":32267.0,"raw_peak_contact_force":0.37303,"subtask_id":"grasp_object","tcp_end":[0.49105,-0.01539,0.04764],"tcp_start":[0.49882,-0.0155,0.05615],"tcp_to_object_dist_end":0.0252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,-0.01595,0.11509],"object_pos_start":[0.50373,-0.01542,0.02586],"object_to_goal_dist_end":0.25585,"object_to_goal_dist_start":0.3122,"object_z_max":0.11503,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17948.0,"raw_peak_contact_force":0.24423,"subtask_id":"lift_object","tcp_end":[0.49919,-0.01535,0.14502],"tcp_start":[0.49105,-0.01539,0.04764],"tcp_to_object_dist_end":0.03092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53594,0.05595,0.11424],"object_pos_start":[0.50695,-0.01595,0.11509],"object_to_goal_dist_end":0.19446,"object_to_goal_dist_start":0.25585,"object_z_max":0.15199,"peak_contact_force":0.1229,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":639.0,"raw_peak_contact_force":1.60497,"subtask_id":"place_at_goal","tcp_end":[0.53173,0.06787,0.19345],"tcp_start":[0.49919,-0.01535,0.14502],"tcp_to_object_dist_end":0.08021,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54058,0.04451,0.01601],"object_pos_start":[0.53594,0.05595,0.11424],"object_to_goal_dist_end":0.2765,"object_to_goal_dist_start":0.19446,"object_z_max":0.11424,"peak_contact_force":0.12262,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2340.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.52653,0.06722,0.21718],"tcp_start":[0.53173,0.06787,0.19345],"tcp_to_object_dist_end":0.20293,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04583,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.09302,"approach_object.approach_speed":0.0156,"descend.descend_offset_z":0.03003,"descend.descend_speed":0.03896,"lift.lift_offset_z":0.13517,"lift.lift_speed":0.07081,"transport_to_goal.transport_offset_z":0.03883,"transport_to_goal.transport_speed":0.03919},"optimized_scores":{"best_composite_score":0.11984,"best_fitness_score":0.63984,"best_task_score":0.34697},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.55108,0.10641,-0.00887],"force_p95":1.36203,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45311,"mean_force":0.60837,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55187,0.09703,0.1691]},{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.51017,0.03804,-0.00119],"force_p95":0.25446,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44352,"mean_force":0.0674,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49845,0.03848,0.04502]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16393.0,"contact_point_centroid":[0.50397,0.05741,0.0947],"force_p95":0.0857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28989,"mean_force":0.05903,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50148,0.03842,0.0926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16121.0,"contact_point_centroid":[0.50366,0.01945,0.09473],"force_p95":0.09221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26138,"mean_force":0.05949,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50146,0.03841,0.09255]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51253,0.03961,-0.00209],"force_p95":0.14815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20672,"mean_force":0.12965,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50102,0.03871,0.04462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":754.0,"contact_point_centroid":[0.56147,0.11635,0.1528],"force_p95":0.11608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15362,"mean_force":0.07312,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55579,0.09783,0.15533]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.49972,0.01937,0.04641],"force_p95":0.06839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14502,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49985,0.03862,0.04332]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50256,0.01782,0.21523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":593.0,"contact_point_centroid":[0.56141,0.07951,0.15249],"force_p95":0.11506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1312,"mean_force":0.0792,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55599,0.09787,0.15562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12643.0,"contact_point_centroid":[0.54028,0.09047,0.15273],"force_p95":0.09659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13108,"mean_force":0.07341,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53427,0.07184,0.15268]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12338.0,"contact_point_centroid":[0.54037,0.05336,0.15265],"force_p95":0.10672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12825,"mean_force":0.07522,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53442,0.07203,0.15269]},{"body_a":"world","body_b":"grasp_target","contact_count":3672.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50646,0.03823,0.07671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5447.0,"contact_point_centroid":[0.49955,0.0579,0.04585],"force_p95":0.06767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07038,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49985,0.03862,0.04332]}],"total_contact_groups":13},"final_pose_error":0.10526,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.56985,0.09345,0.02002],"final_tcp_position":[0.55765,0.09808,0.15838],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.45311,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3672.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50758,0.03639,0.13096],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":918.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14479,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12310.0,"raw_peak_contact_force":0.20672,"subtask_id":"grasp_object","tcp_end":[0.50764,0.03926,0.05202],"tcp_start":[0.50758,0.03639,0.13096],"tcp_to_object_dist_end":0.02646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51245,0.03892,0.02567],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21295,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.08711,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":32699.0,"raw_peak_contact_force":0.44352,"subtask_id":"grasp_object","tcp_end":[0.49982,0.03862,0.04329],"tcp_start":[0.50764,0.03926,0.05202],"tcp_to_object_dist_end":0.02168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":944.0,"n_steps_budget":1000.0,"object_pos_end":[0.51936,0.03871,0.12503],"object_pos_start":[0.51245,0.03892,0.02567],"object_to_goal_dist_end":0.17325,"object_to_goal_dist_start":0.21295,"object_z_max":0.12496,"peak_contact_force":0.11411,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24981.0,"raw_peak_contact_force":0.13108,"subtask_id":"lift_object","tcp_end":[0.50789,0.03859,0.15022],"tcp_start":[0.49982,0.03862,0.04329],"tcp_to_object_dist_end":0.02767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56306,0.09819,0.12553],"object_pos_start":[0.51936,0.03871,0.12503],"object_to_goal_dist_end":0.10033,"object_to_goal_dist_start":0.17325,"object_z_max":0.12553,"peak_contact_force":0.42578,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1461.0,"raw_peak_contact_force":1.45311,"subtask_id":"place_at_goal","tcp_end":[0.55765,0.09808,0.15838],"tcp_start":[0.50789,0.03859,0.15022],"tcp_to_object_dist_end":0.0333,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56985,0.09345,0.02002],"object_pos_start":[0.56306,0.09819,0.12553],"object_to_goal_dist_end":0.15878,"object_to_goal_dist_start":0.10033,"object_z_max":0.12553,"peak_contact_force":0.12262,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.55177,0.09702,0.18113],"tcp_start":[0.55765,0.09808,0.15838],"tcp_to_object_dist_end":0.16216,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```