## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.3836 | 0.52 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0608 | 0.36 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0416 | 0.32 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0563 | 0.35 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.52 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.384) — your mutation base

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
    threshold: 0.01
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
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - id=grasp_contact, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.384
- **task_score** (E): 0.522
- **fitness_score**: 0.724  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1660 |
| descend_to_object | 1.00 | 1.00 | 0.0844 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1401 |
| approach_goal | 0.33 | 1.00 | 0.1356 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.510, 0.017, 0.138)→(0.511, 0.018, 0.054) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.506, 0.018, 0.048)→(0.506, 0.018, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 40.667 | 0.143 | 0.173 |
| lift_object | lift | 1.00 / step_budget | (0.506, 0.018, 0.048)→(0.502, 0.018, 0.188) | (0.516, 0.018, 0.026)→(0.511, 0.018, 0.157) | 0.236→0.198 | 1.00 / 22.333 | 81.785 | 0.413 |
| approach_goal | approach | 0.33 / step_budget | (0.502, 0.018, 0.188)→(0.569, 0.125, 0.160) | (0.511, 0.018, 0.157)→(0.571, 0.113, 0.069) | 0.198→0.126 | 1.00 / 14.000 | 0.123 | 0.749 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.737
- phase_score: 0.337
- phase_breakdown.reach_goal_score: 0.465
- phase_breakdown.reach_object_score: 0.210
- grasp_place_fitness: 0.833

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.833
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.737
- **Median Q (composite search score)**: 0.458
- **K-run variance**: 0.0170
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.230


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73077,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07121,"approach_object.approach_speed":0.06973,"descend_to_object.descend_speed":0.06997,"lift_object.lift_height":0.14738,"lift_object.lift_speed":0.08964},"optimized_scores":{"best_composite_score":0.49307,"best_fitness_score":0.83307,"best_task_score":0.73707},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.52809,0.0296,-0.00119],"force_p95":0.24784,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42118,"mean_force":0.06422,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51882,0.02995,0.04819]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15475.0,"contact_point_centroid":[0.51743,0.01081,0.10722],"force_p95":0.10007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3037,"mean_force":0.0611,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51632,0.02979,0.10653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16165.0,"contact_point_centroid":[0.51818,0.04874,0.10754],"force_p95":0.09527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29927,"mean_force":0.05926,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51636,0.02979,0.10637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10330.0,"contact_point_centroid":[0.55289,0.0712,0.1435],"force_p95":0.11836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24109,"mean_force":0.0892,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54738,0.08963,0.14558]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10490.0,"contact_point_centroid":[0.55309,0.10806,0.14362],"force_p95":0.11744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21888,"mean_force":0.08761,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54741,0.08969,0.14555]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53051,0.03066,-0.00208],"force_p95":0.14213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18246,"mean_force":0.12889,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52104,0.0301,0.04706]},{"body_a":"world","body_b":"grasp_target","contact_count":2236.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51082,0.01385,0.21806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.51985,0.01087,0.04821],"force_p95":0.07842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13421,"mean_force":0.05224,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52053,0.03007,0.04647]},{"body_a":"world","body_b":"grasp_target","contact_count":3556.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52364,0.0295,0.08254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5910.0,"contact_point_centroid":[0.52068,0.04914,0.048],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07957,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52054,0.03007,0.04647]}],"total_contact_groups":10},"final_pose_error":0.03834,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58619,0.14762,0.07809],"final_tcp_position":[0.58007,0.14762,0.11524],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":245.1423,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52419,0.0282,0.13708],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":889.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3556.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52543,0.0304,0.05222],"tcp_start":[0.52419,0.0282,0.13708],"tcp_to_object_dist_end":0.02669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.03015,0.02574],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18404,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.13942,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12669.0,"raw_peak_contact_force":0.18246,"tcp_end":[0.52051,0.03007,0.04644],"tcp_start":[0.52051,0.03007,0.04644],"tcp_to_object_dist_end":0.02295,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.52648,0.03013,0.15361],"object_pos_start":[0.53042,0.03013,0.02575],"object_to_goal_dist_end":0.17247,"object_to_goal_dist_start":0.18405,"object_z_max":0.15351,"peak_contact_force":245.1423,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31802.0,"raw_peak_contact_force":0.42118,"tcp_end":[0.51678,0.02983,0.1819],"tcp_start":[0.52051,0.03007,0.04644],"tcp_to_object_dist_end":0.0299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58619,0.14762,0.07809],"object_pos_start":[0.52648,0.03013,0.15361],"object_to_goal_dist_end":0.04576,"object_to_goal_dist_start":0.17247,"object_z_max":0.15365,"peak_contact_force":0.12114,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20820.0,"raw_peak_contact_force":0.24109,"subtask_id":"reach_goal","tcp_end":[0.58007,0.14762,0.11524],"tcp_start":[0.51678,0.02983,0.1819],"tcp_to_object_dist_end":0.03764,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25668,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09002,"approach_object.approach_speed":0.03724,"descend_to_object.descend_speed":0.05053,"lift_object.lift_height":0.14989,"lift_object.lift_speed":0.11098},"optimized_scores":{"best_composite_score":0.20033,"best_fitness_score":0.54033,"best_task_score":0.16435},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.53447,0.05789,-0.00249],"force_p95":0.1731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64874,"mean_force":0.14651,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52676,0.0677,0.20691]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.50079,-0.01427,-0.0013],"force_p95":0.23891,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35525,"mean_force":0.0594,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49251,-0.01542,0.0531]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8553.0,"contact_point_centroid":[0.49254,0.00314,0.10925],"force_p95":0.12352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33003,"mean_force":0.08983,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49026,-0.01537,0.1121]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9096.0,"contact_point_centroid":[0.49217,-0.03379,0.10734],"force_p95":0.12526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31476,"mean_force":0.08476,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49027,-0.01537,0.11012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3391.0,"contact_point_centroid":[0.50457,-0.00981,0.18657],"force_p95":0.12649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20947,"mean_force":0.09898,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49884,0.00836,0.19089]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3284.0,"contact_point_centroid":[0.50528,0.02776,0.18681],"force_p95":0.1229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17496,"mean_force":0.10082,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49938,0.00957,0.19118]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5038,-0.01567,-0.00209],"force_p95":0.14481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15204,"mean_force":0.12926,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49459,-0.01545,0.05188]},{"body_a":"world","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49869,-0.00697,0.21955]},{"body_a":"world","body_b":"grasp_target","contact_count":2116.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49768,-0.0149,0.09462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4732.0,"contact_point_centroid":[0.49551,0.00359,0.05097],"force_p95":0.10027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10437,"mean_force":0.05728,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49412,-0.01544,0.05137]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5587.0,"contact_point_centroid":[0.49424,-0.03423,0.05123],"force_p95":0.07655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08386,"mean_force":0.04606,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49412,-0.01544,0.05137]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2052.0,"contact_point_centroid":[0.52848,0.07056,0.20998],"force_p95":0.0116,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01052,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52813,0.07056,0.20772]}],"total_contact_groups":12},"final_pose_error":0.11064,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53453,0.058,0.01602],"final_tcp_position":[0.53916,0.09358,0.2142],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.64874,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":539.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2152.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49961,-0.01429,0.13879],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49887,-0.01551,0.05662],"tcp_start":[0.49961,-0.01429,0.13879],"tcp_to_object_dist_end":0.031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01532,0.0256],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31233,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14722,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12123.0,"raw_peak_contact_force":0.15204,"tcp_end":[0.49409,-0.01544,0.05134],"tcp_start":[0.49409,-0.01544,0.05134],"tcp_to_object_dist_end":0.02748,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":795.0,"n_steps_budget":870.0,"object_pos_end":[0.49714,-0.01536,0.15338],"object_pos_start":[0.50372,-0.01533,0.02557],"object_to_goal_dist_end":0.24117,"object_to_goal_dist_start":0.31236,"object_z_max":0.15325,"peak_contact_force":0.11333,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17805.0,"raw_peak_contact_force":0.35525,"tcp_end":[0.49056,-0.01537,0.18865],"tcp_start":[0.49409,-0.01544,0.05134],"tcp_to_object_dist_end":0.03587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53453,0.058,0.01602],"object_pos_start":[0.49714,-0.01536,0.15338],"object_to_goal_dist_end":0.27087,"object_to_goal_dist_start":0.24117,"object_z_max":0.15738,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10863.0,"raw_peak_contact_force":1.64874,"subtask_id":"reach_goal","tcp_end":[0.53916,0.09358,0.2142],"tcp_start":[0.49056,-0.01537,0.18865],"tcp_to_object_dist_end":0.2014,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56835,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.11877,"approach_object.approach_speed":0.11386,"descend_to_object.descend_speed":0.03516,"lift_object.lift_height":0.15966,"lift_object.lift_speed":0.1014},"optimized_scores":{"best_composite_score":0.4575,"best_fitness_score":0.7975,"best_task_score":0.66563},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.50989,0.03822,-0.00118],"force_p95":0.28725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46334,"mean_force":0.06085,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50136,0.03874,0.04825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10167.0,"contact_point_centroid":[0.5485,0.06891,0.16764],"force_p95":0.1284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35854,"mean_force":0.09098,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54298,0.08734,0.1696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15519.0,"contact_point_centroid":[0.50076,0.0575,0.11299],"force_p95":0.09654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30224,"mean_force":0.05995,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4989,0.03855,0.11191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14909.0,"contact_point_centroid":[0.49999,0.01958,0.11285],"force_p95":0.10049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29442,"mean_force":0.06151,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49886,0.03855,0.11221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10395.0,"contact_point_centroid":[0.54888,0.10587,0.16766],"force_p95":0.12246,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25831,"mean_force":0.08879,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54316,0.08753,0.16952]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51253,0.03957,-0.00209],"force_p95":0.14402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18535,"mean_force":0.12944,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5034,0.03892,0.04705]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50276,0.01777,0.21869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4952.0,"contact_point_centroid":[0.5022,0.01968,0.04821],"force_p95":0.07883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13644,"mean_force":0.05224,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50289,0.03888,0.04649]},{"body_a":"world","body_b":"grasp_target","contact_count":3524.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50648,0.03817,0.08004]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5923.0,"contact_point_centroid":[0.50304,0.05795,0.04802],"force_p95":0.07105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07185,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5029,0.03888,0.04649]}],"total_contact_groups":10},"final_pose_error":0.05713,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59277,0.13301,0.11411],"final_tcp_position":[0.58675,0.13306,0.15144],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.46334,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50767,0.0363,0.13782],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3524.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50766,0.03927,0.05186],"tcp_start":[0.50767,0.0363,0.13782],"tcp_to_object_dist_end":0.02629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.039,0.02571],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21289,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14097,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12679.0,"raw_peak_contact_force":0.18535,"tcp_end":[0.50287,0.03888,0.04646],"tcp_start":[0.50287,0.03888,0.04646],"tcp_to_object_dist_end":0.02284,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":904.0,"n_steps_budget":990.0,"object_pos_end":[0.50923,0.03893,0.16539],"object_pos_start":[0.51243,0.03897,0.02573],"object_to_goal_dist_end":0.17962,"object_to_goal_dist_start":0.21289,"object_z_max":0.16527,"peak_contact_force":0.09806,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30567.0,"raw_peak_contact_force":0.46334,"tcp_end":[0.49934,0.03859,0.19382],"tcp_start":[0.50287,0.03888,0.04646],"tcp_to_object_dist_end":0.03011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59277,0.13301,0.11411],"object_pos_start":[0.50923,0.03893,0.16539],"object_to_goal_dist_end":0.06105,"object_to_goal_dist_start":0.17962,"object_z_max":0.16543,"peak_contact_force":0.12479,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20562.0,"raw_peak_contact_force":0.35854,"subtask_id":"reach_goal","tcp_end":[0.58675,0.13306,0.15144],"tcp_start":[0.49934,0.03859,0.19382],"tcp_to_object_dist_end":0.03782,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```