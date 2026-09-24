## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0063 | 0.35 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2806 | 0.21 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2806 | 0.21 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2807 | 0.21 | ✅ accepted |

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

## Current Skill (Q=-0.006) — your mutation base

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
  weight: 0.2
- id: grasp_target
  anchor: object
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_goal
  weight: 0.2
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_target
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
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
    - -0.01
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
    speed:
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
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: lift_clear
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_goal
- id: place_descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: release_1
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
    tolerance: 0.01

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_z: status=consumed; consumers=target.offset.z (replace)
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.006
- **task_score** (E): 0.347
- **fitness_score**: 0.644  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1712 |
| descend_1 | 1.00 | 1.00 | 0.0859 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 0.33 | 1.00 | 0.1022 |
| transport_1 | 0.00 | 1.00 | 0.0709 |
| place_descend_1 | 0.67 | 1.00 | 0.1004 |
| release_1 | 1.00 | 1.00 | 0.0222 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.025, 0.134) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.025, 0.134)→(0.510, 0.019, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 19.385 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.019, 0.048)→(0.502, 0.019, 0.039) | (0.516, 0.018, 0.026)→(0.516, 0.019, 0.026) | 0.236→0.236 | 1.00 / 41.667 | 0.138 | 0.185 |
| lift_1 | lift | 0.33 / step_budget | (0.502, 0.019, 0.039)→(0.506, 0.019, 0.141) | (0.516, 0.019, 0.026)→(0.515, 0.019, 0.119) | 0.236→0.199 | 1.00 / 29.333 | 0.095 | 0.477 |
| transport_1 | approach | 0.00 / step_budget | (0.506, 0.019, 0.141)→(0.529, 0.060, 0.193) | (0.515, 0.019, 0.119)→(0.535, 0.060, 0.164) | 0.199→0.149 | 1.00 / 22.000 | 0.108 | 0.157 |
| place_descend_1 | descend | 0.67 / step_budget | (0.529, 0.060, 0.193)→(0.579, 0.142, 0.190) | (0.535, 0.060, 0.164)→(0.573, 0.106, 0.016) | 0.149→0.172 | 1.00 / 8.000 | 3249.739 | 1.605 |
| release_1 | release | 1.00 / step_budget | (0.579, 0.142, 0.190)→(0.573, 0.141, 0.212) | (0.573, 0.106, 0.016)→(0.573, 0.106, 0.016) | 0.172→0.172 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.476
- phase_score: 0.454
- phase_breakdown.lift_clear_score: 0.397
- phase_breakdown.transport_goal_score: 0.054
- phase_breakdown.place_goal_score: 0.288
- phase_breakdown.grasp_target_score: 0.710
- phase_breakdown.reach_object_score: 0.819
- grasp_place_fitness: 0.710

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.710
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.476
- **Median Q (composite search score)**: 0.012
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40984,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.12582,"approach_1.speed":0.07828,"descend_1.depth":0.01206,"descend_1.speed":0.05232,"lift_1.lift_height":0.21243,"lift_1.speed":0.06057,"place_descend_1.place_z":0.06555,"place_descend_1.speed":0.08459,"transport_1.speed":0.04678,"transport_1.transport_z":0.22989},"optimized_scores":{"best_composite_score":0.06045,"best_fitness_score":0.71045,"best_task_score":0.47577},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2282.0,"contact_point_centroid":[0.57885,0.12025,-0.00241],"force_p95":0.15409,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5473,"mean_force":0.14493,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57637,0.14141,0.16949]},{"body_a":"world","body_b":"grasp_target","contact_count":189.0,"contact_point_centroid":[0.52689,0.03138,-0.00113],"force_p95":0.29377,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49848,"mean_force":0.07814,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51503,0.03099,0.03819]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16813.0,"contact_point_centroid":[0.51746,0.04991,0.08554],"force_p95":0.08669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30955,"mean_force":0.06002,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51583,0.03086,0.08372]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17992.0,"contact_point_centroid":[0.51741,0.01191,0.08435],"force_p95":0.08388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27498,"mean_force":0.0565,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51577,0.03086,0.08276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2603.0,"contact_point_centroid":[0.55187,0.07203,0.17443],"force_p95":0.17156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26707,"mean_force":0.11647,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54682,0.09027,0.17637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3321.0,"contact_point_centroid":[0.55338,0.10917,0.1746],"force_p95":0.13783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22142,"mean_force":0.09215,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54744,0.09137,0.17619]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5305,0.0309,-0.00204],"force_p95":0.13434,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16241,"mean_force":0.12589,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51784,0.0312,0.03792]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13232.0,"contact_point_centroid":[0.53115,0.03275,0.15904],"force_p95":0.10926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14547,"mean_force":0.07148,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52742,0.05158,0.15831]},{"body_a":"world","body_b":"grasp_target","contact_count":3076.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50956,0.05236,0.22487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14623.0,"contact_point_centroid":[0.53183,0.07088,0.15993],"force_p95":0.09106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13202,"mean_force":0.0645,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52773,0.0522,0.1591]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52376,0.03542,0.08827]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57887,0.12006,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5849,0.16171,0.16827]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.5174,0.05033,0.03922],"force_p95":0.07599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12212,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51663,0.03112,0.03656]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4886.0,"contact_point_centroid":[0.51745,0.01205,0.03844],"force_p95":0.06789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08896,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51663,0.03112,0.03656]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2181.0,"contact_point_centroid":[0.57829,0.14388,0.17147],"force_p95":0.01147,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.017,"mean_force":0.01063,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57782,0.14386,0.16922]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.58781,0.16263,0.16655],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01087,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58764,0.16261,0.16426]}],"total_contact_groups":16},"final_pose_error":0.02113,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57887,0.12006,0.01602],"final_tcp_position":[0.58906,0.16285,0.16705],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.97124,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":770.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52515,0.0392,0.13077],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":29.15245,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1144.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.52497,0.03173,0.04616],"tcp_start":[0.52515,0.0392,0.13077],"tcp_to_object_dist_end":0.0209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.03122,0.02585],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18314,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1324,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10798.0,"raw_peak_contact_force":0.16241,"tcp_end":[0.5166,0.03112,0.03652],"tcp_start":[0.52497,0.03173,0.04616],"tcp_to_object_dist_end":0.01743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52842,0.03088,0.1153],"object_pos_start":[0.53039,0.03122,0.02585],"object_to_goal_dist_end":0.16496,"object_to_goal_dist_start":0.18314,"object_z_max":0.11518,"peak_contact_force":0.09266,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34994.0,"raw_peak_contact_force":0.49848,"subtask_id":"lift_clear","tcp_end":[0.51946,0.03089,0.1352],"tcp_start":[0.5166,0.03112,0.03652],"tcp_to_object_dist_end":0.02182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54445,0.07048,0.1572],"object_pos_start":[0.52842,0.03088,0.1153],"object_to_goal_dist_end":0.13174,"object_to_goal_dist_start":0.16496,"object_z_max":0.15717,"peak_contact_force":0.09581,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27855.0,"raw_peak_contact_force":0.14547,"subtask_id":"transport_goal","tcp_end":[0.53797,0.07051,0.18379],"tcp_start":[0.51946,0.03089,0.1352],"tcp_to_object_dist_end":0.02737,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57887,0.12006,0.01602],"object_pos_start":[0.54445,0.07048,0.1572],"object_to_goal_dist_end":0.11142,"object_to_goal_dist_start":0.13174,"object_z_max":0.1572,"peak_contact_force":9748.97124,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10387.0,"raw_peak_contact_force":1.5473,"subtask_id":"place_goal","tcp_end":[0.58906,0.16285,0.16705],"tcp_start":[0.53797,0.07051,0.18379],"tcp_to_object_dist_end":0.15731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57887,0.12006,0.01602],"object_pos_start":[0.57887,0.12006,0.01602],"object_to_goal_dist_end":0.11142,"object_to_goal_dist_start":0.11142,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5833,0.16119,0.18808],"tcp_start":[0.58906,0.16285,0.16705],"tcp_to_object_dist_end":0.17696,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97266,"average_solve_count":256.0,"average_success_count":256.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.19376,"approach_1.speed":0.04101,"descend_1.depth":0.01012,"descend_1.speed":0.02761,"lift_1.lift_height":0.22869,"lift_1.speed":0.06144,"place_descend_1.place_z":0.02009,"place_descend_1.speed":0.0798,"transport_1.speed":0.05427,"transport_1.transport_z":0.16483},"optimized_scores":{"best_composite_score":-0.09089,"best_fitness_score":0.55911,"best_task_score":0.17093},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2233.0,"contact_point_centroid":[0.54856,0.06544,-0.00248],"force_p95":0.15871,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69677,"mean_force":0.14302,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54109,0.1,0.22154]},{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.50049,-0.01354,-0.0012],"force_p95":0.29812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50941,"mean_force":0.07782,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48904,-0.01431,0.03768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17385.0,"contact_point_centroid":[0.49103,0.00475,0.08673],"force_p95":0.08513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3034,"mean_force":0.05808,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48959,-0.01429,0.08478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18166.0,"contact_point_centroid":[0.4909,-0.03328,0.08495],"force_p95":0.08362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29026,"mean_force":0.05625,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48951,-0.01429,0.08324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2643.0,"contact_point_centroid":[0.52395,0.07081,0.19945],"force_p95":0.1605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24297,"mean_force":0.11718,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.51816,0.05261,0.20119]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01545,-0.00212],"force_p95":0.15685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22283,"mean_force":0.13167,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49176,-0.01434,0.03715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3366.0,"contact_point_centroid":[0.5246,0.0359,0.20001],"force_p95":0.13729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18285,"mean_force":0.09293,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.51864,0.05364,0.2016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11637.0,"contact_point_centroid":[0.5051,0.02971,0.1666],"force_p95":0.11084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16905,"mean_force":0.08139,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50096,0.01083,0.16561]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15093.0,"contact_point_centroid":[0.50508,-0.00724,0.16658],"force_p95":0.09138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1591,"mean_force":0.06294,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50112,0.01121,0.16609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.49117,0.00488,0.03867],"force_p95":0.08013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14604,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49061,-0.01433,0.03592]},{"body_a":"world","body_b":"grasp_target","contact_count":2568.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49875,0.01721,0.21393]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49772,-0.01064,0.08855]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54858,0.06548,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54846,0.12082,0.23351]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4985.0,"contact_point_centroid":[0.4912,-0.03346,0.03777],"force_p95":0.0725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0808,"mean_force":0.04458,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49061,-0.01433,0.03592]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2169.0,"contact_point_centroid":[0.54257,0.10221,0.22471],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.0105,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54219,0.10221,0.22253]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.55135,0.12141,0.23121],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55063,0.12141,0.22877]}],"total_contact_groups":16},"final_pose_error":0.08337,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54858,0.06548,0.01602],"final_tcp_position":[0.55178,0.12152,0.23119],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.69677,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2568.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4996,-0.00708,0.13255],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1276.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.49864,-0.01439,0.04456],"tcp_start":[0.4996,-0.00708,0.13255],"tcp_to_object_dist_end":0.01929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01446,0.0256],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31177,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15035,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10863.0,"raw_peak_contact_force":0.22283,"tcp_end":[0.49058,-0.01433,0.03589],"tcp_start":[0.49864,-0.01439,0.04456],"tcp_to_object_dist_end":0.01671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50221,-0.01432,0.11703],"object_pos_start":[0.50374,-0.01446,0.0256],"object_to_goal_dist_end":0.25508,"object_to_goal_dist_start":0.31177,"object_z_max":0.11692,"peak_contact_force":0.09094,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35736.0,"raw_peak_contact_force":0.50941,"subtask_id":"lift_clear","tcp_end":[0.4928,-0.01432,0.13625],"tcp_start":[0.49058,-0.01433,0.03589],"tcp_to_object_dist_end":0.0214,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51876,0.03452,0.17134],"object_pos_start":[0.50221,-0.01432,0.11703],"object_to_goal_dist_end":0.18419,"object_to_goal_dist_start":0.25508,"object_z_max":0.17128,"peak_contact_force":0.11351,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26730.0,"raw_peak_contact_force":0.16905,"subtask_id":"transport_goal","tcp_end":[0.51212,0.03462,0.19778],"tcp_start":[0.4928,-0.01432,0.13625],"tcp_to_object_dist_end":0.02726,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54858,0.06548,0.01602],"object_pos_start":[0.51876,0.03452,0.17134],"object_to_goal_dist_end":0.26498,"object_to_goal_dist_start":0.18419,"object_z_max":0.17709,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10411.0,"raw_peak_contact_force":1.69677,"subtask_id":"place_goal","tcp_end":[0.55178,0.12152,0.23119],"tcp_start":[0.51212,0.03462,0.19778],"tcp_to_object_dist_end":0.22237,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54858,0.06548,0.01602],"object_pos_start":[0.54858,0.06548,0.01602],"object_to_goal_dist_end":0.26498,"object_to_goal_dist_start":0.26498,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54722,0.12049,0.25379],"tcp_start":[0.55178,0.12152,0.23119],"tcp_to_object_dist_end":0.24405,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0354,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.28552,"approach_1.speed":0.05324,"descend_1.depth":0.01901,"descend_1.speed":0.05439,"lift_1.lift_height":0.15825,"lift_1.speed":0.06586,"place_descend_1.place_z":0.02651,"place_descend_1.speed":0.04069,"transport_1.speed":0.04635,"transport_1.transport_z":0.20075},"optimized_scores":{"best_composite_score":0.01159,"best_fitness_score":0.66159,"best_task_score":0.39375},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.59083,0.13298,-0.00249],"force_p95":0.20014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57101,"mean_force":0.14696,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.58334,0.12884,0.17579]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.51025,0.03914,-0.00112],"force_p95":0.24467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42436,"mean_force":0.06454,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4979,0.03905,0.04611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16860.0,"contact_point_centroid":[0.50222,0.05792,0.09589],"force_p95":0.09314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29136,"mean_force":0.06004,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5002,0.03893,0.09413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17577.0,"contact_point_centroid":[0.50148,0.01997,0.09329],"force_p95":0.10018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25939,"mean_force":0.05809,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49999,0.03892,0.09182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3641.0,"contact_point_centroid":[0.55586,0.07532,0.18308],"force_p95":0.12466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22377,"mean_force":0.10412,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55036,0.09359,0.18735]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03962,-0.00204],"force_p95":0.13453,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1689,"mean_force":0.12623,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50038,0.03928,0.04574]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11238.0,"contact_point_centroid":[0.52422,0.03865,0.17224],"force_p95":0.12327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15713,"mean_force":0.08149,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51924,0.05721,0.17312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11732.0,"contact_point_centroid":[0.52424,0.07585,0.17239],"force_p95":0.11646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15659,"mean_force":0.07816,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51932,0.05733,0.17326]},{"body_a":"world","body_b":"grasp_target","contact_count":2444.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50228,0.0349,0.22407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3915.0,"contact_point_centroid":[0.55623,0.11208,0.18264],"force_p95":0.12176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13676,"mean_force":0.0963,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55071,0.09399,0.18718]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5062,0.04149,0.09539]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59087,0.13307,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59127,0.14055,0.17303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4880.0,"contact_point_centroid":[0.49938,0.02003,0.04779],"force_p95":0.0703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10618,"mean_force":0.04425,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49923,0.03919,0.04446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4793.0,"contact_point_centroid":[0.49983,0.05843,0.04636],"force_p95":0.07009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08899,"mean_force":0.04586,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49923,0.03919,0.04447]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1808.0,"contact_point_centroid":[0.58548,0.1306,0.17749],"force_p95":0.01189,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01067,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.58498,0.13058,0.17525]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.59444,0.14135,0.17108],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01106,"mean_force":0.00996,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59401,0.14133,0.16906]}],"total_contact_groups":16},"final_pose_error":0.04463,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59087,0.13307,0.01602],"final_tcp_position":[0.59541,0.14158,0.17187],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":28.88029,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2444.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50766,0.04326,0.13776],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":28.88029,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.50725,0.03987,0.05347],"tcp_start":[0.50766,0.04326,0.13776],"tcp_to_object_dist_end":0.02795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.0394,0.02583],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21257,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13157,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11473.0,"raw_peak_contact_force":0.1689,"tcp_end":[0.4992,0.03918,0.04443],"tcp_start":[0.50725,0.03987,0.05347],"tcp_to_object_dist_end":0.02283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5146,0.03933,0.12486],"object_pos_start":[0.51242,0.0394,0.02583],"object_to_goal_dist_end":0.17581,"object_to_goal_dist_start":0.21257,"object_z_max":0.12474,"peak_contact_force":0.10273,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34601.0,"raw_peak_contact_force":0.42436,"subtask_id":"lift_clear","tcp_end":[0.50587,0.03904,0.15178],"tcp_start":[0.4992,0.03918,0.04443],"tcp_to_object_dist_end":0.02831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54056,0.07541,0.16353],"object_pos_start":[0.5146,0.03933,0.12486],"object_to_goal_dist_end":0.1317,"object_to_goal_dist_start":0.17581,"object_z_max":0.1635,"peak_contact_force":0.11444,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22970.0,"raw_peak_contact_force":0.15713,"subtask_id":"transport_goal","tcp_end":[0.53568,0.0752,0.19861],"tcp_start":[0.50587,0.03904,0.15178],"tcp_to_object_dist_end":0.03542,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59087,0.13307,0.01602],"object_pos_start":[0.54056,0.07541,0.16353],"object_to_goal_dist_end":0.13981,"object_to_goal_dist_start":0.1317,"object_z_max":0.16353,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11324.0,"raw_peak_contact_force":1.57101,"subtask_id":"place_goal","tcp_end":[0.59541,0.14158,0.17187],"tcp_start":[0.53568,0.0752,0.19861],"tcp_to_object_dist_end":0.15615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59087,0.13307,0.01602],"object_pos_start":[0.59087,0.13307,0.01602],"object_to_goal_dist_end":0.13981,"object_to_goal_dist_start":0.13981,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58968,0.1401,0.19282],"tcp_start":[0.59541,0.14158,0.17187],"tcp_to_object_dist_end":0.17694,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```