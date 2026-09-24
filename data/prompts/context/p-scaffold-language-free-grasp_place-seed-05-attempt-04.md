## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0686 | 0.39 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0063 | 0.35 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2806 | 0.21 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2806 | 0.21 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2807 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.069) — your mutation base

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
  - 0.05
  weight: 0.2
- id: place_goal
  offset:
  - 0.0
  - 0.0
  - 0.02
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
    - 0.05
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.05
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
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
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.05], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_z: status=consumed; consumers=target.offset.z (replace)
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.069
- **task_score** (E): 0.387
- **fitness_score**: 0.581  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1698 |
| descend_1 | 1.00 | 1.00 | 0.0877 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 0.33 | 1.00 | 0.0943 |
| transport_1 | 0.67 | 1.00 | 0.2031 |
| place_descend_1 | 1.00 | 1.00 | 0.0503 |
| release_1 | 1.00 | 1.00 | 0.0208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.025, 0.135) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.025, 0.135)→(0.510, 0.019, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.019, 0.048)→(0.502, 0.019, 0.038) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 41.000 | 0.200 | 0.225 |
| lift_1 | lift | 0.33 / step_budget | (0.502, 0.019, 0.038)→(0.506, 0.018, 0.133) | (0.516, 0.018, 0.026)→(0.514, 0.018, 0.112) | 0.236→0.203 | 1.00 / 34.667 | 0.084 | 0.470 |
| transport_1 | approach | 0.67 / step_budget | (0.506, 0.018, 0.133)→(0.593, 0.160, 0.240) | (0.514, 0.018, 0.112)→(0.584, 0.140, 0.073) | 0.203→0.154 | 1.00 / 12.000 | 94252.932 | 1.321 |
| place_descend_1 | descend | 1.00 / step_budget | (0.593, 0.160, 0.240)→(0.600, 0.175, 0.197) | (0.584, 0.140, 0.073)→(0.583, 0.141, 0.051) | 0.154→0.133 | 1.00 / 14.667 | 0.126 | 0.168 |
| release_1 | release | 1.00 / step_budget | (0.600, 0.175, 0.197)→(0.594, 0.174, 0.217) | (0.583, 0.141, 0.051)→(0.582, 0.143, 0.019) | 0.133→0.156 | 1.00 / 3.000 | 0.204 | 0.547 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.575
- phase_score: 0.578
- phase_breakdown.lift_clear_score: 0.421
- phase_breakdown.transport_goal_score: 0.323
- phase_breakdown.place_goal_score: 0.623
- phase_breakdown.grasp_target_score: 0.702
- phase_breakdown.reach_object_score: 0.821
- grasp_place_fitness: 0.759

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.759
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.575
- **Median Q (composite search score)**: 0.013
- **K-run variance**: 0.0352
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.419


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14912,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.29225,"approach_1.speed":0.04963,"descend_1.depth":0.01249,"descend_1.speed":0.06843,"lift_1.lift_height":0.13637,"lift_1.speed":0.06169,"place_descend_1.place_z":0.03521,"place_descend_1.speed":0.0924,"transport_1.speed":0.05761,"transport_1.transport_z":0.11817},"optimized_scores":{"best_composite_score":0.10941,"best_fitness_score":0.75941,"best_task_score":0.57494},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":177.0,"contact_point_centroid":[0.58564,0.18491,-0.00642],"force_p95":1.11615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3971,"mean_force":0.37466,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58982,0.17346,0.16094]},{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.52754,0.03014,-0.00114],"force_p95":0.29064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5049,"mean_force":0.12021,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5151,0.03033,0.03878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":773.0,"contact_point_centroid":[0.5985,0.19372,0.14417],"force_p95":0.24515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36592,"mean_force":0.10402,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59358,0.17474,0.14616]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.59766,0.15651,0.14587],"force_p95":0.11926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36108,"mean_force":0.06595,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59383,0.17482,0.1465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16784.0,"contact_point_centroid":[0.51984,0.01113,0.08674],"force_p95":0.08764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29812,"mean_force":0.06035,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51807,0.03013,0.08494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17335.0,"contact_point_centroid":[0.51976,0.0491,0.08474],"force_p95":0.08639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28746,"mean_force":0.05883,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51791,0.03013,0.08338]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1672.0,"contact_point_centroid":[0.60034,0.19116,0.17866],"force_p95":0.17695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25899,"mean_force":0.11711,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.59453,0.17266,0.17957]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5305,0.03067,-0.00203],"force_p95":0.22614,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22702,"mean_force":0.16253,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51778,0.03054,0.03855]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2286.0,"contact_point_centroid":[0.59964,0.15451,0.18074],"force_p95":0.14385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21895,"mean_force":0.0826,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.59446,0.17253,0.18096]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11480.0,"contact_point_centroid":[0.56292,0.12051,0.17485],"force_p95":0.11006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16184,"mean_force":0.08137,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55826,0.10172,0.17392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.51736,0.01126,0.03995],"force_p95":0.08761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14113,"mean_force":0.0607,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51658,0.03046,0.03718]},{"body_a":"world","body_b":"grasp_target","contact_count":2520.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51013,0.03108,0.22186]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52324,0.03285,0.09129]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.51742,0.04954,0.03896],"force_p95":0.07761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11969,"mean_force":0.05399,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51658,0.03046,0.03719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14136.0,"contact_point_centroid":[0.56187,0.08125,0.17351],"force_p95":0.09322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11314,"mean_force":0.06633,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55719,0.09969,0.17274]}],"total_contact_groups":15},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59459,0.18109,0.0254],"final_tcp_position":[0.59612,0.17546,0.15089],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.3971,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":631.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52425,0.0348,0.13647],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1168.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.52491,0.03105,0.04679],"tcp_start":[0.52425,0.0348,0.13647],"tcp_to_object_dist_end":0.02151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53038,0.03037,0.02586],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18382,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.22601,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10798.0,"raw_peak_contact_force":0.22702,"tcp_end":[0.51655,0.03046,0.03715],"tcp_start":[0.52491,0.03105,0.04679],"tcp_to_object_dist_end":0.01786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5329,0.03006,0.11663],"object_pos_start":[0.53038,0.03037,0.02586],"object_to_goal_dist_end":0.16384,"object_to_goal_dist_start":0.18382,"object_z_max":0.11652,"peak_contact_force":0.09289,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34311.0,"raw_peak_contact_force":0.5049,"subtask_id":"lift_clear","tcp_end":[0.52405,0.03011,0.13724],"tcp_start":[0.51655,0.03046,0.03715],"tcp_to_object_dist_end":0.02244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60082,0.17005,0.18572],"object_pos_start":[0.5329,0.03006,0.11663],"object_to_goal_dist_end":0.0781,"object_to_goal_dist_start":0.16384,"object_z_max":0.18565,"peak_contact_force":0.15275,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25616.0,"raw_peak_contact_force":0.16184,"subtask_id":"transport_goal","tcp_end":[0.59428,0.16998,0.21353],"tcp_start":[0.52405,0.03011,0.13724],"tcp_to_object_dist_end":0.02857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":178.0,"n_steps_budget":1000.0,"object_pos_end":[0.5977,0.17393,0.12105],"object_pos_start":[0.60082,0.17005,0.18572],"object_to_goal_dist_end":0.0143,"object_to_goal_dist_start":0.0781,"object_z_max":0.18572,"peak_contact_force":0.13406,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3958.0,"raw_peak_contact_force":0.25899,"subtask_id":"place_goal","tcp_end":[0.59612,0.17546,0.15089],"tcp_start":[0.59428,0.16998,0.21353],"tcp_to_object_dist_end":0.02992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59459,0.18109,0.0254],"object_pos_start":[0.5977,0.17393,0.12105],"object_to_goal_dist_end":0.08302,"object_to_goal_dist_start":0.0143,"object_z_max":0.12105,"peak_contact_force":0.36594,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1958.0,"raw_peak_contact_force":1.3971,"tcp_end":[0.58975,0.17343,0.17095],"tcp_start":[0.59612,0.17546,0.15089],"tcp_to_object_dist_end":0.14584,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46774,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.18586,"approach_1.speed":0.07954,"descend_1.depth":0.01109,"descend_1.speed":0.05967,"lift_1.lift_height":0.18985,"lift_1.speed":0.01567,"place_descend_1.place_z":0.0173,"place_descend_1.speed":0.06337,"transport_1.speed":0.1997,"transport_1.transport_z":0.0961},"optimized_scores":{"best_composite_score":-0.3279,"best_fitness_score":0.3221,"best_task_score":0.19854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1003.0,"contact_point_centroid":[0.56082,0.12227,-0.00321],"force_p95":0.59879,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.13789,"mean_force":0.1719,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55554,0.12529,0.26712]},{"body_a":"world","body_b":"grasp_target","contact_count":209.0,"contact_point_centroid":[0.49918,-0.01372,-0.00125],"force_p95":0.37211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42583,"mean_force":0.09511,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48907,-0.01428,0.03849]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7910.0,"contact_point_centroid":[0.51361,0.01204,0.16197],"force_p95":0.13492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25567,"mean_force":0.07756,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5105,0.03094,0.16079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19719.0,"contact_point_centroid":[0.48984,0.00487,0.07902],"force_p95":0.07598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25124,"mean_force":0.05084,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48971,-0.01427,0.07692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9463.0,"contact_point_centroid":[0.5148,0.05146,0.16366],"force_p95":0.10873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24769,"mean_force":0.06615,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51138,0.03283,0.16291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20132.0,"contact_point_centroid":[0.48977,-0.03338,0.07742],"force_p95":0.07474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24636,"mean_force":0.05043,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48961,-0.01427,0.07559]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01545,-0.00212],"force_p95":0.15733,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22248,"mean_force":0.13181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49187,-0.01431,0.03813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.49123,0.00491,0.03966],"force_p95":0.08033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14694,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49071,-0.0143,0.0369]},{"body_a":"world","body_b":"grasp_target","contact_count":2400.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13069,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49886,0.01815,0.21381]},{"body_a":"world","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49789,-0.01059,0.08885]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.56063,0.12224,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57269,0.16328,0.27167]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56063,0.12224,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57832,0.17996,0.26152]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.49128,-0.03344,0.03875],"force_p95":0.07246,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07859,"mean_force":0.04454,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49071,-0.0143,0.03691]},{"body_a":"left_finger","body_b":"right_finger","contact_count":881.0,"contact_point_centroid":[0.55755,0.12854,0.27293],"force_p95":0.01297,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01559,"mean_force":0.01076,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5571,0.12853,0.27078]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1185.0,"contact_point_centroid":[0.57323,0.16323,0.27406],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01029,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57266,0.16322,0.27172]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.58064,0.18076,0.25979],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58017,0.18074,0.25754]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56063,0.12224,0.01602],"final_tcp_position":[0.58126,0.18088,0.26047],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273009.80043,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2400.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49963,-0.00696,0.13238],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.49874,-0.01436,0.04556],"tcp_start":[0.49963,-0.00696,0.13238],"tcp_to_object_dist_end":0.02023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01445,0.02559],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31177,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15079,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10868.0,"raw_peak_contact_force":0.22248,"tcp_end":[0.49068,-0.0143,0.03687],"tcp_start":[0.49874,-0.01436,0.04556],"tcp_to_object_dist_end":0.01726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49917,-0.01432,0.09569],"object_pos_start":[0.50374,-0.01445,0.02559],"object_to_goal_dist_end":0.26766,"object_to_goal_dist_start":0.31177,"object_z_max":0.09561,"peak_contact_force":0.069,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40060.0,"raw_peak_contact_force":0.42583,"subtask_id":"lift_clear","tcp_end":[0.49246,-0.0143,0.11407],"tcp_start":[0.49068,-0.0143,0.03687],"tcp_to_object_dist_end":0.01957,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56063,0.12224,0.01602],"object_pos_start":[0.49917,-0.01432,0.09569],"object_to_goal_dist_end":0.24251,"object_to_goal_dist_start":0.26766,"object_z_max":0.20061,"peak_contact_force":273009.80043,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19257.0,"raw_peak_contact_force":2.13789,"subtask_id":"transport_goal","tcp_end":[0.56462,0.14416,0.28835],"tcp_start":[0.49246,-0.0143,0.11407],"tcp_to_object_dist_end":0.27324,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.56063,0.12224,0.01602],"object_pos_start":[0.56063,0.12224,0.01602],"object_to_goal_dist_end":0.24251,"object_to_goal_dist_start":0.24251,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2277.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58126,0.18088,0.26047],"tcp_start":[0.56462,0.14416,0.28835],"tcp_to_object_dist_end":0.25223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56063,0.12224,0.01602],"object_pos_start":[0.56063,0.12224,0.01602],"object_to_goal_dist_end":0.24251,"object_to_goal_dist_start":0.24251,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57731,0.17952,0.28129],"tcp_start":[0.58126,0.18088,0.26047],"tcp_to_object_dist_end":0.2719,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53763,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.19403,"approach_1.speed":0.06816,"descend_1.depth":0.01605,"descend_1.speed":0.04862,"lift_1.lift_height":0.25427,"lift_1.speed":0.06386,"place_descend_1.place_z":0.02743,"place_descend_1.speed":0.03839,"transport_1.speed":0.14858,"transport_1.transport_z":0.08535},"optimized_scores":{"best_composite_score":0.01278,"best_fitness_score":0.66278,"best_task_score":0.38897},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1416.0,"contact_point_centroid":[0.59092,0.12689,-0.00265],"force_p95":0.33645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66243,"mean_force":0.15344,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5975,0.14336,0.2048]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.5097,0.03935,-0.00113],"force_p95":0.29383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47843,"mean_force":0.11591,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49769,0.03939,0.0429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4185.0,"contact_point_centroid":[0.53414,0.05217,0.1622],"force_p95":0.16153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34585,"mean_force":0.09606,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5285,0.07081,0.16146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16220.0,"contact_point_centroid":[0.49983,0.02019,0.09185],"force_p95":0.10178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30348,"mean_force":0.06294,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4979,0.03916,0.08995]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16995.0,"contact_point_centroid":[0.50007,0.05805,0.09132],"force_p95":0.09253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28799,"mean_force":0.06002,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49792,0.03916,0.08987]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5248.0,"contact_point_centroid":[0.53617,0.0907,0.16275],"force_p95":0.13148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24209,"mean_force":0.0791,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53001,0.07242,0.16241]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03962,-0.00202],"force_p95":0.22359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22502,"mean_force":0.16183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50033,0.03962,0.04262]},{"body_a":"world","body_b":"grasp_target","contact_count":2516.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50209,0.04274,0.22607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4123.0,"contact_point_centroid":[0.49978,0.02033,0.04415],"force_p95":0.08622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13427,"mean_force":0.06067,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49917,0.03953,0.04134]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50612,0.04297,0.09305]},{"body_a":"world","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.59103,0.12688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.62025,0.16802,0.20005]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59103,0.12688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6175,0.16834,0.17949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4871.0,"contact_point_centroid":[0.49979,0.05861,0.04312],"force_p95":0.07679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11954,"mean_force":0.05385,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49917,0.03953,0.04134]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1265.0,"contact_point_centroid":[0.60188,0.14747,0.20956],"force_p95":0.01211,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01583,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60142,0.14745,0.20727]},{"body_a":"left_finger","body_b":"right_finger","contact_count":495.0,"contact_point_centroid":[0.62059,0.16804,0.20243],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01256,"mean_force":0.01044,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.62024,0.16802,0.20013]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.62053,0.16921,0.17807],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00987,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62007,0.16919,0.1759]}],"total_contact_groups":16},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59103,0.12688,0.01602],"final_tcp_position":[0.62179,0.16964,0.17985],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.84328,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2516.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50767,0.04586,0.13621],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.50723,0.04023,0.05034],"tcp_start":[0.50767,0.04586,0.13621],"tcp_to_object_dist_end":0.0249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03941,0.02589],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21254,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.2235,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10794.0,"raw_peak_contact_force":0.22502,"tcp_end":[0.49914,0.03953,0.04131],"tcp_start":[0.50723,0.04023,0.05034],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51097,0.03899,0.12239],"object_pos_start":[0.51241,0.03941,0.02589],"object_to_goal_dist_end":0.17871,"object_to_goal_dist_start":0.21254,"object_z_max":0.12227,"peak_contact_force":0.09006,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33381.0,"raw_peak_contact_force":0.47843,"subtask_id":"lift_clear","tcp_end":[0.50117,0.03915,0.14649],"tcp_start":[0.49914,0.03953,0.04131],"tcp_to_object_dist_end":0.02601,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":872.0,"n_steps_budget":1000.0,"object_pos_end":[0.59103,0.12688,0.01602],"object_pos_start":[0.51097,0.03899,0.12239],"object_to_goal_dist_end":0.14164,"object_to_goal_dist_start":0.17871,"object_z_max":0.1505,"peak_contact_force":9748.84328,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12114.0,"raw_peak_contact_force":1.66243,"subtask_id":"transport_goal","tcp_end":[0.61989,0.1668,0.21884],"tcp_start":[0.50117,0.03915,0.14649],"tcp_to_object_dist_end":0.20871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.59103,0.12688,0.01602],"object_pos_start":[0.59103,0.12688,0.01602],"object_to_goal_dist_end":0.14164,"object_to_goal_dist_start":0.14164,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":959.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62179,0.16964,0.17985],"tcp_start":[0.61989,0.1668,0.21884],"tcp_to_object_dist_end":0.17209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59103,0.12688,0.01602],"object_pos_start":[0.59103,0.12688,0.01602],"object_to_goal_dist_end":0.14164,"object_to_goal_dist_start":0.14164,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61598,0.16782,0.1989],"tcp_start":[0.62179,0.16964,0.17985],"tcp_to_object_dist_end":0.18906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```