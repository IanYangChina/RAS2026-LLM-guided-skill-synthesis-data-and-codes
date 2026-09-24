## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2130 | 0.35 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1508 | 0.31 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2119 | 0.34 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2533 | 0.43 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1929 | 0.29 | ❌ rejected |

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

## Current Skill (Q=0.213) — your mutation base

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

- **Composite score**: 0.213
- **task_score** (E): 0.349
- **fitness_score**: 0.643  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1261 |
| descend_1 | 1.00 | 1.00 | 0.1319 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.0998 |
| transport_1 | 0.00 | 1.00 | 0.0836 |
| descend_place | 0.67 | 1.00 | 0.0781 |
| release_1 | 1.00 | 1.00 | 0.0221 |
| retract_1 | 1.00 | 1.00 | 0.0859 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.016, 0.179) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.016, 0.179)→(0.511, 0.018, 0.047) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.047)→(0.503, 0.018, 0.038) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.667 | 0.139 | 0.189 |
| lift_1 | lift | 1.00 / step_budget | (0.503, 0.018, 0.038)→(0.511, 0.018, 0.138) | (0.516, 0.018, 0.026)→(0.525, 0.018, 0.117) | 0.236→0.195 | 1.00 / 26.667 | 0.099 | 0.497 |
| transport_1 | approach | 0.00 / step_budget | (0.511, 0.018, 0.138)→(0.545, 0.083, 0.173) | (0.525, 0.018, 0.117)→(0.542, 0.077, 0.090) | 0.195→0.161 | 1.00 / 16.667 | 91002.193 | 0.600 |
| descend_place | descend | 0.67 / step_budget | (0.545, 0.083, 0.173)→(0.582, 0.144, 0.194) | (0.542, 0.077, 0.090)→(0.560, 0.103, 0.016) | 0.161→0.177 | 1.00 / 8.000 | 0.123 | 0.958 |
| release_1 | release | 1.00 / step_budget | (0.582, 0.144, 0.194)→(0.576, 0.142, 0.215) | (0.560, 0.103, 0.016)→(0.560, 0.103, 0.016) | 0.177→0.177 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.576, 0.142, 0.215)→(0.574, 0.141, 0.301) | (0.560, 0.103, 0.016)→(0.560, 0.103, 0.016) | 0.177→0.177 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.528
- phase_score: 0.610
- phase_breakdown.reach_grasp_score: 0.849
- phase_breakdown.reach_place_score: 0.508
- grasp_place_fitness: 0.729

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.729
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.528
- **Median Q (composite search score)**: 0.218
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.235


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77852,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12068,"descend_1.descend_depth":0.03071,"descend_place.place_depth":0.05706,"lift_1.lift_height":0.12602,"transport_1.transport_speed":0.06376},"optimized_scores":{"best_composite_score":0.29899,"best_fitness_score":0.72899,"best_task_score":0.52796},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.5969,0.15246,-0.00233],"force_p95":0.16193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34063,"mean_force":0.141,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58349,0.15254,0.15463]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.52921,0.02966,-0.00117],"force_p95":0.2831,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42647,"mean_force":0.05276,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5162,0.02975,0.04602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9957.0,"contact_point_centroid":[0.52181,0.04869,0.08929],"force_p95":0.09689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28087,"mean_force":0.06274,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51909,0.0297,0.08713]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10092.0,"contact_point_centroid":[0.52108,0.01081,0.08682],"force_p95":0.09731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26119,"mean_force":0.06129,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51878,0.02969,0.08463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3273.0,"contact_point_centroid":[0.56959,0.09887,0.1489],"force_p95":0.13259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22866,"mean_force":0.10205,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56399,0.11712,0.15238]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03068,-0.00207],"force_p95":0.14298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19961,"mean_force":0.12848,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51861,0.02993,0.04561]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51086,0.01365,0.22854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3588.0,"contact_point_centroid":[0.56979,0.13552,0.14888],"force_p95":0.12131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13618,"mean_force":0.09356,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56416,0.11743,0.15238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12164.0,"contact_point_centroid":[0.54893,0.05295,0.14687],"force_p95":0.10657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12559,"mean_force":0.07649,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54324,0.07163,0.14686]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12726.0,"contact_point_centroid":[0.54879,0.08963,0.14691],"force_p95":0.09659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12416,"mean_force":0.07312,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54297,0.07102,0.14672]},{"body_a":"world","body_b":"grasp_target","contact_count":2952.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52362,0.0293,0.09416]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59713,0.15244,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58928,0.16913,0.15733]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.59713,0.15244,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58463,0.16763,0.21777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.5177,0.01069,0.04737],"force_p95":0.06699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10162,"mean_force":0.04268,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51741,0.02985,0.04422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4937.0,"contact_point_centroid":[0.51795,0.04914,0.04604],"force_p95":0.07113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07538,"mean_force":0.04501,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51742,0.02985,0.04423]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2033.0,"contact_point_centroid":[0.58534,0.15495,0.1572],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01055,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58484,0.15492,0.15485]}],"total_contact_groups":17},"final_pose_error":0.01465,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59713,0.15244,0.01602],"final_tcp_position":[0.58489,0.16767,0.26268],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.34063,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52414,0.02789,0.15778],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2952.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52542,0.03039,0.05356],"tcp_start":[0.52414,0.02789,0.15778],"tcp_to_object_dist_end":0.02801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.03013,0.02571],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18406,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14011,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11802.0,"raw_peak_contact_force":0.19961,"tcp_end":[0.51738,0.02985,0.04419],"tcp_start":[0.52542,0.03039,0.05356],"tcp_to_object_dist_end":0.02262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53862,0.02983,0.11471],"object_pos_start":[0.53043,0.03013,0.02571],"object_to_goal_dist_end":0.16165,"object_to_goal_dist_start":0.18406,"object_z_max":0.1146,"peak_contact_force":0.08901,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20198.0,"raw_peak_contact_force":0.42647,"tcp_end":[0.52553,0.02985,0.13916],"tcp_start":[0.51738,0.02985,0.04419],"tcp_to_object_dist_end":0.02773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56556,0.10502,0.12435],"object_pos_start":[0.53862,0.02983,0.11471],"object_to_goal_dist_end":0.08349,"object_to_goal_dist_start":0.16165,"object_z_max":0.12435,"peak_contact_force":0.11469,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24890.0,"raw_peak_contact_force":0.12559,"subtask_id":"reach_place","tcp_end":[0.56016,0.10483,0.15703],"tcp_start":[0.52553,0.02985,0.13916],"tcp_to_object_dist_end":0.03313,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59713,0.15244,0.01602],"object_pos_start":[0.56556,0.10502,0.12435],"object_to_goal_dist_end":0.09581,"object_to_goal_dist_start":0.08349,"object_z_max":0.12435,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11090.0,"raw_peak_contact_force":1.34063,"subtask_id":"reach_place","tcp_end":[0.59356,0.17037,0.15625],"tcp_start":[0.56016,0.10483,0.15703],"tcp_to_object_dist_end":0.14142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59713,0.15244,0.01602],"object_pos_start":[0.59713,0.15244,0.01602],"object_to_goal_dist_end":0.09581,"object_to_goal_dist_start":0.09581,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58761,0.16858,0.17705],"tcp_start":[0.59356,0.17037,0.15625],"tcp_to_object_dist_end":0.16212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.59713,0.15244,0.01602],"object_pos_start":[0.59713,0.15244,0.01602],"object_to_goal_dist_end":0.09581,"object_to_goal_dist_start":0.09581,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58489,0.16767,0.26268],"tcp_start":[0.58761,0.16858,0.17705],"tcp_to_object_dist_end":0.24744,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87898,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12117,"descend_1.descend_depth":0.00782,"descend_place.place_depth":0.07597,"lift_1.lift_height":0.12002,"transport_1.transport_speed":0.07131},"optimized_scores":{"best_composite_score":0.12242,"best_fitness_score":0.55242,"best_task_score":0.14658},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1930.0,"contact_point_centroid":[0.50547,0.03771,-0.00246],"force_p95":0.21258,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52922,"mean_force":0.14804,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51904,0.03939,0.18056]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.50216,-0.01531,-0.00107],"force_p95":0.51312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67714,"mean_force":0.0669,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4896,-0.01544,0.02553]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4660.0,"contact_point_centroid":[0.50682,0.02121,0.14372],"force_p95":0.14587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31529,"mean_force":0.09644,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50339,0.003,0.14659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10694.0,"contact_point_centroid":[0.49495,0.00356,0.07544],"force_p95":0.10375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30405,"mean_force":0.06686,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49238,-0.01533,0.07364]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11171.0,"contact_point_centroid":[0.49463,-0.03419,0.07364],"force_p95":0.10676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28467,"mean_force":0.0646,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49228,-0.01534,0.07242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4635.0,"contact_point_centroid":[0.5064,-0.01655,0.14266],"force_p95":0.1482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23093,"mean_force":0.09347,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50289,0.00168,0.14544]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01553,-0.00202],"force_p95":0.13034,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15631,"mean_force":0.12499,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49199,-0.01548,0.02499]},{"body_a":"world","body_b":"grasp_target","contact_count":1708.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49898,-0.00685,0.23026]},{"body_a":"world","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49784,-0.01485,0.09032]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50538,0.03763,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53638,0.08415,0.21801]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50538,0.03763,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54653,0.11197,0.24749]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.50538,0.03763,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54328,0.11119,0.30952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.49128,0.00374,0.02651],"force_p95":0.07583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10937,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4908,-0.01546,0.02375]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49135,-0.03454,0.02559],"force_p95":0.06788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08968,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49081,-0.01546,0.02375]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1811.0,"contact_point_centroid":[0.5202,0.04127,0.18464],"force_p95":0.01188,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01617,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51988,0.04127,0.18236]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4247.0,"contact_point_centroid":[0.53675,0.08419,0.22024],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5364,0.08419,0.21805]}],"total_contact_groups":17},"final_pose_error":0.01337,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50538,0.03763,0.01602],"final_tcp_position":[0.54361,0.11122,0.35453],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273006.34915,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1708.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49985,-0.0141,0.16004],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2912.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49878,-0.01557,0.03212],"tcp_start":[0.49985,-0.0141,0.16004],"tcp_to_object_dist_end":0.00792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01532,0.0259],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31213,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12891,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10799.0,"raw_peak_contact_force":0.15631,"tcp_end":[0.49077,-0.01546,0.02371],"tcp_start":[0.49878,-0.01557,0.03212],"tcp_to_object_dist_end":0.01308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.51781,-0.01523,0.12432],"object_pos_start":[0.50367,-0.01532,0.0259],"object_to_goal_dist_end":0.24735,"object_to_goal_dist_start":0.31213,"object_z_max":0.12422,"peak_contact_force":0.11273,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22003.0,"raw_peak_contact_force":0.67714,"tcp_end":[0.49894,-0.01526,0.13391],"tcp_start":[0.49077,-0.01546,0.02371],"tcp_to_object_dist_end":0.02117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50538,0.03763,0.01602],"object_pos_start":[0.51781,-0.01523,0.12432],"object_to_goal_dist_end":0.28803,"object_to_goal_dist_start":0.24735,"object_z_max":0.1369,"peak_contact_force":273006.34915,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13036.0,"raw_peak_contact_force":1.52922,"subtask_id":"reach_place","tcp_end":[0.52587,0.05474,0.19516],"tcp_start":[0.49894,-0.01526,0.13391],"tcp_to_object_dist_end":0.18112,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50538,0.03763,0.01602],"object_pos_start":[0.50538,0.03763,0.01602],"object_to_goal_dist_end":0.28803,"object_to_goal_dist_start":0.28803,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8247.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.54966,0.1126,0.24507],"tcp_start":[0.52587,0.05474,0.19516],"tcp_to_object_dist_end":0.24505,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50538,0.03763,0.01602],"object_pos_start":[0.50538,0.03763,0.01602],"object_to_goal_dist_end":0.28803,"object_to_goal_dist_start":0.28803,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54537,0.11167,0.26778],"tcp_start":[0.54966,0.1126,0.24507],"tcp_to_object_dist_end":0.26545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50538,0.03763,0.01602],"object_pos_start":[0.50538,0.03763,0.01602],"object_to_goal_dist_end":0.28803,"object_to_goal_dist_start":0.28803,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54361,0.11122,0.35453],"tcp_start":[0.54537,0.11167,0.26778],"tcp_to_object_dist_end":0.34852,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63924,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18265,"descend_1.descend_depth":0.02899,"descend_place.place_depth":0.05198,"lift_1.lift_height":0.12671,"transport_1.transport_speed":0.04036},"optimized_scores":{"best_composite_score":0.21765,"best_fitness_score":0.64765,"best_task_score":0.3716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3350.0,"contact_point_centroid":[0.57759,0.11844,-0.00223],"force_p95":0.12726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40942,"mean_force":0.13576,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57824,0.1231,0.17129]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.51105,0.03814,-0.00119],"force_p95":0.24885,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38622,"mean_force":0.04872,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49856,0.03835,0.04884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10094.0,"contact_point_centroid":[0.50346,0.0572,0.08809],"force_p95":0.0997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2784,"mean_force":0.06228,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50114,0.0383,0.08726]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9270.0,"contact_point_centroid":[0.50323,0.01937,0.08836],"force_p95":0.10514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26115,"mean_force":0.06599,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50118,0.03831,0.08767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":763.0,"contact_point_centroid":[0.5564,0.07327,0.15893],"force_p95":0.15033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25503,"mean_force":0.10632,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55009,0.09147,0.16327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":851.0,"contact_point_centroid":[0.55669,0.10976,0.15885],"force_p95":0.14025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23589,"mean_force":0.09726,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5502,0.09169,0.16318]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03963,-0.00211],"force_p95":0.15214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20973,"mean_force":0.13051,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5009,0.03857,0.04825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10595.0,"contact_point_centroid":[0.53324,0.08302,0.14946],"force_p95":0.11602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14414,"mean_force":0.08567,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52767,0.06463,0.15123]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10394.0,"contact_point_centroid":[0.53296,0.04615,0.14931],"force_p95":0.11589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13948,"mean_force":0.08739,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52764,0.06459,0.15121]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50289,0.01637,0.25951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4338.0,"contact_point_centroid":[0.49991,0.01929,0.04846],"force_p95":0.0756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12826,"mean_force":0.04947,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49974,0.03848,0.04696]},{"body_a":"world","body_b":"grasp_target","contact_count":3376.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50628,0.03657,0.13236]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57768,0.1185,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59738,0.1466,0.18086]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.57768,0.1185,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5931,0.14536,0.2411]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.50017,0.05765,0.04831],"force_p95":0.07234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07376,"mean_force":0.04432,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49975,0.03848,0.04696]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3253.0,"contact_point_centroid":[0.58071,0.12522,0.17432],"force_p95":0.01114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.01056,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58021,0.1252,0.17201]}],"total_contact_groups":17},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57768,0.1185,0.01602],"final_tcp_position":[0.59338,0.14539,0.28577],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.40942,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1144.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50765,0.03399,0.2191],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":844.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3376.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50761,0.03912,0.0558],"tcp_start":[0.50765,0.03399,0.2191],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03885,0.02561],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21302,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14947,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11106.0,"raw_peak_contact_force":0.20973,"tcp_end":[0.49972,0.03847,0.04692],"tcp_start":[0.50761,0.03912,0.0558],"tcp_to_object_dist_end":0.02483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.51844,0.03893,0.11251],"object_pos_start":[0.51246,0.03885,0.02561],"object_to_goal_dist_end":0.17554,"object_to_goal_dist_start":0.21302,"object_z_max":0.1124,"peak_contact_force":0.09534,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19515.0,"raw_peak_contact_force":0.38622,"tcp_end":[0.50766,0.0385,0.14024],"tcp_start":[0.49972,0.03847,0.04692],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55451,0.08833,0.12857],"object_pos_start":[0.51844,0.03893,0.11251],"object_to_goal_dist_end":0.11268,"object_to_goal_dist_start":0.17554,"object_z_max":0.12856,"peak_contact_force":0.11517,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20989.0,"raw_peak_contact_force":0.14414,"subtask_id":"reach_place","tcp_end":[0.54884,0.08831,0.16542],"tcp_start":[0.50766,0.0385,0.14024],"tcp_to_object_dist_end":0.03728,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57768,0.1185,0.01602],"object_pos_start":[0.55451,0.08833,0.12857],"object_to_goal_dist_end":0.14849,"object_to_goal_dist_start":0.11268,"object_z_max":0.12857,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8217.0,"raw_peak_contact_force":1.40942,"subtask_id":"reach_place","tcp_end":[0.60139,0.14763,0.17985],"tcp_start":[0.54884,0.08831,0.16542],"tcp_to_object_dist_end":0.16808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57768,0.1185,0.01602],"object_pos_start":[0.57768,0.1185,0.01602],"object_to_goal_dist_end":0.14849,"object_to_goal_dist_start":0.14849,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59582,0.14614,0.20053],"tcp_start":[0.60139,0.14763,0.17985],"tcp_to_object_dist_end":0.18745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.57768,0.1185,0.01602],"object_pos_start":[0.57768,0.1185,0.01602],"object_to_goal_dist_end":0.14849,"object_to_goal_dist_start":0.14849,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59338,0.14539,0.28577],"tcp_start":[0.59582,0.14614,0.20053],"tcp_to_object_dist_end":0.27154,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```