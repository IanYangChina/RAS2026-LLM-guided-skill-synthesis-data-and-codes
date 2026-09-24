## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3027 | 0.62 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.3706 | 0.50 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1602 | 0.21 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | contact_lost | pose_tolerance | 9 | 0.0294 | 0.39 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1664 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.62 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.303) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
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
    threshold: 0.02
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
      - 0.08
      - 0.2
      default: 0.14
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_height:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_grasp
    when: during_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_goal
- id: place_object
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: placement_contact
    when: after_phase
    predicate: object_lifted
    threshold: 0.01
    on_failure: abort
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
    - id=grasp_contact, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.02
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_grasp, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=repeat
- **place_object** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=placement_contact, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.01

## Design Metrics

- **Composite score**: 0.303
- **task_score** (E): 0.621
- **fitness_score**: 0.773  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1658 |
| descend_to_object | 1.00 | 1.00 | 0.0842 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 0.67 | 1.00 | 0.0978 |
| approach_goal | 0.67 | 0.67 | 0.1098 |
| place_object | 1.00 | 1.00 | 0.0415 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.511, 0.018, 0.054) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 0.00 / guard_failure | (0.506, 0.018, 0.048)→(0.506, 0.018, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 40.333 | 0.144 | 0.175 |
| lift_object | lift | 0.67 / step_budget | (0.506, 0.018, 0.048)→(0.502, 0.018, 0.146) | (0.516, 0.018, 0.026)→(0.508, 0.018, 0.117) | 0.236→0.203 | 1.00 / 27.667 | 0.109 | 0.398 |
| approach_goal | approach | 0.67 / step_budget | (0.528, 0.074, 0.188)→(0.592, 0.161, 0.206) | (0.508, 0.018, 0.117)→(0.600, 0.157, 0.110) | 0.203→0.082 | 0.67 / 16.667 | 0.075 | 0.170 |
| place_object | descend | 1.00 / step_budget | (0.592, 0.161, 0.206)→(0.598, 0.174, 0.169) | (0.600, 0.158, 0.109)→(0.604, 0.164, 0.071) | 0.083→0.097 | 1.00 / 16.333 | 0.123 | 0.796 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.835
- phase_score: 0.727
- phase_breakdown.reach_goal_score: 0.819
- phase_breakdown.reach_object_score: 0.634
- grasp_place_fitness: 0.882

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.882
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.835
- **Median Q (composite search score)**: 0.403
- **K-run variance**: 0.0221
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41361,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_height":0.05696,"approach_goal.transport_speed":0.07288,"approach_object.approach_speed":0.08525,"descend_to_object.descend_speed":0.06964,"lift_object.lift_height":0.15277,"lift_object.lift_speed":0.05631,"place_object.place_speed":0.0289},"optimized_scores":{"best_composite_score":0.41218,"best_fitness_score":0.88218,"best_task_score":0.83531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":209.0,"contact_point_centroid":[0.5257,0.02944,-0.00122],"force_p95":0.26647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43087,"mean_force":0.0832,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51857,0.02994,0.04811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20274.0,"contact_point_centroid":[0.51637,0.04873,0.09253],"force_p95":0.07388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29943,"mean_force":0.05003,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51623,0.02979,0.09146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16928.0,"contact_point_centroid":[0.51544,0.01062,0.09244],"force_p95":0.08607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29647,"mean_force":0.05905,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51622,0.02979,0.09141]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2097.0,"contact_point_centroid":[0.59151,0.18764,0.13353],"force_p95":0.11002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25167,"mean_force":0.07087,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.5916,0.16902,0.13442]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1791.0,"contact_point_centroid":[0.59174,0.15009,0.13344],"force_p95":0.10769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21313,"mean_force":0.07693,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59149,0.16883,0.13538]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53051,0.03066,-0.00208],"force_p95":0.14214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18247,"mean_force":0.12889,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52104,0.0301,0.04707]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51093,0.01383,0.21821]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4955.0,"contact_point_centroid":[0.51985,0.01087,0.04821],"force_p95":0.07842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13423,"mean_force":0.05224,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52053,0.03007,0.04647]},{"body_a":"world","body_b":"grasp_target","contact_count":3556.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52363,0.02949,0.08259]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7837.0,"contact_point_centroid":[0.54949,0.07767,0.14395],"force_p95":0.09567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12123,"mean_force":0.0612,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5518,0.09678,0.14421]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9122.0,"contact_point_centroid":[0.55043,0.11528,0.1439],"force_p95":0.07769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10938,"mean_force":0.05127,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55163,0.09646,0.14418]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5910.0,"contact_point_centroid":[0.52068,0.04914,0.048],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07957,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52053,0.03007,0.04647]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59642,0.17422,0.08195],"final_tcp_position":[0.59441,0.17368,0.11303],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.43087,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52417,0.02818,0.13719],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":889.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3556.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52543,0.0304,0.05222],"tcp_start":[0.52417,0.02818,0.13719],"tcp_to_object_dist_end":0.02669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.03015,0.02574],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18404,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.13942,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12669.0,"raw_peak_contact_force":0.18247,"tcp_end":[0.52051,0.03007,0.04644],"tcp_start":[0.52051,0.03007,0.04644],"tcp_to_object_dist_end":0.02295,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5188,0.03,0.11096],"object_pos_start":[0.53042,0.03012,0.02575],"object_to_goal_dist_end":0.17009,"object_to_goal_dist_start":0.18405,"object_z_max":0.11087,"peak_contact_force":0.09726,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37411.0,"raw_peak_contact_force":0.43087,"tcp_end":[0.51635,0.0298,0.13787],"tcp_start":[0.52051,0.03007,0.04644],"tcp_to_object_dist_end":0.02703,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.59131,0.16567,0.12504],"object_pos_start":[0.5188,0.03,0.11096],"object_to_goal_dist_end":0.02363,"object_to_goal_dist_start":0.17009,"object_z_max":0.12501,"peak_contact_force":0.09528,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16959.0,"raw_peak_contact_force":0.12123,"subtask_id":"reach_goal","tcp_end":[0.59074,0.16515,0.15489],"tcp_start":[0.51635,0.0298,0.13787],"tcp_to_object_dist_end":0.02986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.59642,0.17422,0.08195],"object_pos_start":[0.59131,0.16567,0.12504],"object_to_goal_dist_end":0.02699,"object_to_goal_dist_start":0.02363,"object_z_max":0.12504,"peak_contact_force":0.11492,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3888.0,"raw_peak_contact_force":0.25167,"subtask_id":"reach_goal","tcp_end":[0.59441,0.17368,0.11303],"tcp_start":[0.59074,0.16515,0.15489],"tcp_to_object_dist_end":0.03116,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46193,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_height":0.05849,"approach_goal.transport_speed":0.08053,"approach_object.approach_speed":0.05088,"descend_to_object.descend_speed":0.09435,"lift_object.lift_height":0.10744,"lift_object.lift_speed":0.09711,"place_object.place_speed":0.04986},"optimized_scores":{"best_composite_score":0.09254,"best_fitness_score":0.56254,"best_task_score":0.20843},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.59084,0.1494,-0.00375],"force_p95":0.79314,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81472,"mean_force":0.19236,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.57448,0.16799,0.25704]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.50148,-0.01465,-0.00124],"force_p95":0.25438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35687,"mean_force":0.05312,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49247,-0.01542,0.05311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7450.0,"contact_point_centroid":[0.49137,0.00328,0.09183],"force_p95":0.12255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34043,"mean_force":0.08403,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49011,-0.01538,0.09432]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9314.0,"contact_point_centroid":[0.49039,-0.03391,0.09204],"force_p95":0.11653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32399,"mean_force":0.06824,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49008,-0.01538,0.09359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5604.0,"contact_point_centroid":[0.52875,0.07938,0.19774],"force_p95":0.1258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2211,"mean_force":0.10254,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52387,0.06115,0.20177]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5807.0,"contact_point_centroid":[0.52953,0.04489,0.19926],"force_p95":0.127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22086,"mean_force":0.09922,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52479,0.06305,0.20323]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50381,-0.01568,-0.00209],"force_p95":0.14635,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15197,"mean_force":0.12976,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49456,-0.01545,0.05169]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4988,-0.00698,0.2195]},{"body_a":"world","body_b":"grasp_target","contact_count":1864.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49782,-0.0149,0.09464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4867.0,"contact_point_centroid":[0.49512,0.00359,0.05097],"force_p95":0.09929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10439,"mean_force":0.05628,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49409,-0.01544,0.05117]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5593.0,"contact_point_centroid":[0.49422,-0.03426,0.05109],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08379,"mean_force":0.0465,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49409,-0.01544,0.05117]},{"body_a":"left_finger","body_b":"right_finger","contact_count":607.0,"contact_point_centroid":[0.57608,0.17081,0.25603],"force_p95":0.01338,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01081,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.57575,0.1708,0.25377]}],"total_contact_groups":12},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59089,0.14945,0.01602],"final_tcp_position":[0.58066,0.18035,0.24514],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.81472,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49971,-0.0143,0.13881],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49884,-0.01551,0.05642],"tcp_start":[0.49971,-0.0143,0.13881],"tcp_to_object_dist_end":0.03081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01533,0.02555],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31237,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14932,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.15197,"tcp_end":[0.49407,-0.01544,0.05115],"tcp_start":[0.49407,-0.01544,0.05115],"tcp_to_object_dist_end":0.02735,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.49692,-0.01568,0.1143],"object_pos_start":[0.50373,-0.01534,0.02551],"object_to_goal_dist_end":0.25936,"object_to_goal_dist_start":0.3124,"object_z_max":0.1142,"peak_contact_force":0.12397,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16919.0,"raw_peak_contact_force":0.35687,"tcp_end":[0.49016,-0.01537,0.14702],"tcp_start":[0.49407,-0.01544,0.05115],"tcp_to_object_dist_end":0.03341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":739.0,"n_steps_budget":1000.0,"object_pos_end":[0.58824,0.14352,0.04729],"object_pos_start":[0.49692,-0.01568,0.1143],"object_to_goal_dist_end":0.20558,"object_to_goal_dist_start":0.25936,"object_z_max":0.21803,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11411.0,"raw_peak_contact_force":0.2211,"subtask_id":"reach_goal","tcp_end":[0.56887,0.15458,0.27375],"tcp_start":[0.56882,0.15441,0.27371],"tcp_to_object_dist_end":0.22756,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.59089,0.14945,0.01602],"object_pos_start":[0.58847,0.14363,0.04361],"object_to_goal_dist_end":0.23522,"object_to_goal_dist_start":0.20915,"object_z_max":0.04361,"peak_contact_force":0.12256,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1335.0,"raw_peak_contact_force":1.81472,"subtask_id":"reach_goal","tcp_end":[0.58066,0.18035,0.24514],"tcp_start":[0.56887,0.15458,0.27375],"tcp_to_object_dist_end":0.23142,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45946,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.place_height":0.05762,"approach_goal.transport_speed":0.06547,"approach_object.approach_speed":0.09517,"descend_to_object.descend_speed":0.07769,"lift_object.lift_height":0.11727,"lift_object.lift_speed":0.09286,"place_object.place_speed":0.02746},"optimized_scores":{"best_composite_score":0.40343,"best_fitness_score":0.87343,"best_task_score":0.82031},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.5102,0.03836,-0.00118],"force_p95":0.25493,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40489,"mean_force":0.0599,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50115,0.03869,0.04931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1202.0,"contact_point_centroid":[0.62193,0.1831,0.16882],"force_p95":0.13553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32308,"mean_force":0.10479,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.6167,0.16484,0.17195]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12916.0,"contact_point_centroid":[0.49906,0.01946,0.09784],"force_p95":0.09067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29912,"mean_force":0.05758,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49865,0.03849,0.0973]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13364.0,"contact_point_centroid":[0.49978,0.05752,0.09753],"force_p95":0.09119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2979,"mean_force":0.05655,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49868,0.0385,0.09658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1217.0,"contact_point_centroid":[0.62187,0.14693,0.167],"force_p95":0.12232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27648,"mean_force":0.09964,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.61685,0.16501,0.1707]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51253,0.03958,-0.0021],"force_p95":0.14509,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19183,"mean_force":0.12976,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50329,0.03887,0.04807]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5951.0,"contact_point_centroid":[0.55633,0.07796,0.16692],"force_p95":0.13288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1685,"mean_force":0.0924,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55213,0.09657,0.16873]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7021.0,"contact_point_centroid":[0.56045,0.11828,0.16944],"force_p95":0.11237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16203,"mean_force":0.07608,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55546,0.10008,0.16986]},{"body_a":"world","body_b":"grasp_target","contact_count":2080.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13223,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50278,0.01777,0.21873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.50206,0.01964,0.04885],"force_p95":0.07866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.138,"mean_force":0.05227,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50279,0.03883,0.04751]},{"body_a":"world","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50623,0.03784,0.08821]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5928.0,"contact_point_centroid":[0.50291,0.0579,0.04873],"force_p95":0.07111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07179,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50279,0.03883,0.04751]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62569,0.16924,0.11555],"final_tcp_position":[0.62017,0.16838,0.15028],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.40489,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50771,0.03626,0.13805],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50756,0.03922,0.0529],"tcp_start":[0.50771,0.03626,0.13805],"tcp_to_object_dist_end":0.02733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03898,0.0257],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2129,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14213,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12683.0,"raw_peak_contact_force":0.19183,"tcp_end":[0.50277,0.03883,0.04748],"tcp_start":[0.50277,0.03883,0.04748],"tcp_to_object_dist_end":0.02383,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.50904,0.03883,0.12573],"object_pos_start":[0.51244,0.03896,0.02572],"object_to_goal_dist_end":0.17971,"object_to_goal_dist_start":0.21291,"object_z_max":0.12562,"peak_contact_force":0.10436,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26437.0,"raw_peak_contact_force":0.40489,"tcp_end":[0.49887,0.03852,0.15319],"tcp_start":[0.50277,0.03883,0.04748],"tcp_to_object_dist_end":0.02928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.62064,0.16329,0.15744],"object_pos_start":[0.50904,0.03883,0.12573],"object_to_goal_dist_end":0.01695,"object_to_goal_dist_start":0.17971,"object_z_max":0.15739,"peak_contact_force":0.13033,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12972.0,"raw_peak_contact_force":0.1685,"subtask_id":"reach_goal","tcp_end":[0.61527,0.16222,0.19073],"tcp_start":[0.49887,0.03852,0.15319],"tcp_to_object_dist_end":0.03374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.62569,0.16924,0.11555],"object_pos_start":[0.62064,0.16329,0.15744],"object_to_goal_dist_end":0.02971,"object_to_goal_dist_start":0.01695,"object_z_max":0.15744,"peak_contact_force":0.13019,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2419.0,"raw_peak_contact_force":0.32308,"subtask_id":"reach_goal","tcp_end":[0.62017,0.16838,0.15028],"tcp_start":[0.61527,0.16222,0.19073],"tcp_to_object_dist_end":0.03518,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```