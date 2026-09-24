## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0493 | 0.47 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2132 | 0.73 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2588 | 0.82 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1245 | 0.45 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0115 | 0.38 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.815, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=-0.049) — your mutation base

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
      - 0.3
      default: 0.15
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
  guards:
  - id: grip_transport
    when: during_phase
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
    - 0.01
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.05
      default: 0.01
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
  guards:
  - id: grip_place
    when: during_phase
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
  subtask_id: place_goal

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
  - guards:
    - id=grip_transport, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.01], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grip_place, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]

## Design Metrics

- **Composite score**: -0.049
- **task_score** (E): 0.470
- **fitness_score**: 0.621  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1704 |
| descend_1 | 1.00 | 1.00 | 0.0857 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 0.33 | 0.67 | 0.0366 |
| transport_1 | 0.00 | 0.33 | 0.0007 |
| place_descend_1 | 0.00 | 0.33 | 0.0190 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.025, 0.135) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.025, 0.135)→(0.510, 0.019, 0.049) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.019, 0.049)→(0.502, 0.019, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.019, 0.026) | 0.236→0.236 | 1.00 / 41.333 | 0.200 | 0.222 |
| lift_1 | lift | 0.33 / guard_failure | (0.506, 0.018, 0.117)→(0.507, 0.018, 0.154) | (0.516, 0.019, 0.026)→(0.522, 0.017, 0.128) | 0.236→0.192 | 0.67 / 17.667 | 0.034 | 0.517 |
| transport_1 | approach | 0.00 / guard_failure | (0.511, 0.024, 0.172)→(0.511, 0.024, 0.173) | (0.521, 0.016, 0.128)→(0.525, 0.022, 0.143) | 0.192→0.186 | 0.33 / 8.333 | 0.000 | 0.172 |
| place_descend_1 | descend | 0.00 / guard_failure | (0.527, 0.055, 0.169)→(0.536, 0.071, 0.167) | (0.525, 0.023, 0.142)→(0.525, 0.023, 0.142) | 0.185→0.185 | 0.33 / 8.000 | 0.037 | 0.097 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.368
- phase_score: 0.359
- phase_breakdown.lift_clear_score: 0.182
- phase_breakdown.transport_goal_score: 0.036
- phase_breakdown.place_goal_score: 0.035
- phase_breakdown.grasp_target_score: 0.719
- phase_breakdown.reach_object_score: 0.822
- grasp_place_fitness: 0.657

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.657
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.842
- **Median Q (composite search score)**: -0.025
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40761,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.26528,"approach_1.speed":0.04465,"descend_1.depth":0.01041,"descend_1.speed":0.07014,"lift_1.lift_height":0.18764,"lift_1.speed":0.14028,"place_descend_1.place_z_offset":0.00421,"place_descend_1.speed":0.03595,"transport_1.arc_height":0.15232,"transport_1.speed":0.19991,"transport_1.transport_z":0.11378},"optimized_scores":{"best_composite_score":-0.02494,"best_fitness_score":0.64506,"best_task_score":0.84235},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.52842,0.03025,-0.00113],"force_p95":0.35066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6156,"mean_force":0.11703,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51516,0.03041,0.03659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6136.0,"contact_point_centroid":[0.51827,0.01131,0.07305],"force_p95":0.10857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3499,"mean_force":0.0703,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51569,0.03022,0.07077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6593.0,"contact_point_centroid":[0.51834,0.04908,0.07116],"force_p95":0.10728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32084,"mean_force":0.0665,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51561,0.03023,0.06937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7313.0,"contact_point_centroid":[0.56031,0.08862,0.11486],"force_p95":0.11551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28953,"mean_force":0.08353,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5566,0.10741,0.11413]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":308.0,"contact_point_centroid":[0.52235,0.04845,0.1247],"force_p95":0.15843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2431,"mean_force":0.10168,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51695,0.02999,0.12288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8719.0,"contact_point_centroid":[0.56162,0.1259,0.11503],"force_p95":0.09629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23442,"mean_force":0.07132,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.55662,0.10747,0.11411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":252.0,"contact_point_centroid":[0.52144,0.01128,0.12475],"force_p95":0.16833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23238,"mean_force":0.11702,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51697,0.02999,0.12284]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53049,0.03067,-0.00203],"force_p95":0.22654,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22822,"mean_force":0.16233,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51778,0.0306,0.03638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.51736,0.01132,0.03778],"force_p95":0.08728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13848,"mean_force":0.06054,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51657,0.03052,0.03501]},{"body_a":"world","body_b":"grasp_target","contact_count":2576.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50998,0.03275,0.22226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4882.0,"contact_point_centroid":[0.5174,0.0496,0.03679],"force_p95":0.0778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1243,"mean_force":0.05393,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51658,0.03052,0.03501]},{"body_a":"world","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52326,0.03318,0.09005]}],"total_contact_groups":12},"final_pose_error":0.01274,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59931,0.17005,0.08391],"final_tcp_position":[0.59256,0.17024,0.10882],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.6156,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":645.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2576.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52429,0.03538,0.13615],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1184.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.52495,0.03112,0.04464],"tcp_start":[0.52429,0.03538,0.13615],"tcp_to_object_dist_end":0.01943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.03041,0.02588],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18378,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.22643,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.22822,"tcp_end":[0.51654,0.03052,0.03498],"tcp_start":[0.52495,0.03112,0.04464],"tcp_to_object_dist_end":0.01655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":416.0,"n_steps_budget":810.0,"object_pos_end":[0.53566,0.03019,0.10185],"object_pos_start":[0.53037,0.03041,0.02588],"object_to_goal_dist_end":0.16248,"object_to_goal_dist_start":0.18378,"object_z_max":0.10462,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12878.0,"raw_peak_contact_force":0.6156,"subtask_id":"lift_clear","tcp_end":[0.5182,0.03009,0.12086],"tcp_start":[0.51861,0.03012,0.12],"tcp_to_object_dist_end":0.02582,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.53354,0.02978,0.1057],"object_pos_start":[0.53456,0.0299,0.1048],"object_to_goal_dist_end":0.16362,"object_to_goal_dist_start":0.1631,"object_z_max":0.10907,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":560.0,"raw_peak_contact_force":0.2431,"subtask_id":"transport_goal","tcp_end":[0.51569,0.02992,0.12591],"tcp_start":[0.51627,0.02994,0.12404],"tcp_to_object_dist_end":0.02696,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.53193,0.02981,0.10944],"object_pos_start":[0.53134,0.02962,0.10938],"object_to_goal_dist_end":0.16425,"object_to_goal_dist_start":0.16468,"object_z_max":0.10973,"peak_contact_force":0.11005,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16032.0,"raw_peak_contact_force":0.28953,"subtask_id":"place_goal","tcp_end":[0.59256,0.17024,0.10882],"tcp_start":[0.56471,0.12108,0.1138],"tcp_to_object_dist_end":0.15296,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52137,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.19267,"approach_1.speed":0.08066,"descend_1.depth":0.0225,"descend_1.speed":0.04197,"lift_1.lift_height":0.19026,"lift_1.speed":0.17154,"place_descend_1.place_z_offset":0.00675,"place_descend_1.speed":0.01813,"transport_1.arc_height":0.18101,"transport_1.speed":0.09685,"transport_1.transport_z":0.16601},"optimized_scores":{"best_composite_score":-0.10981,"best_fitness_score":0.56019,"best_task_score":0.2004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":119.0,"contact_point_centroid":[0.502,-0.01316,-0.0012],"force_p95":0.23301,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3891,"mean_force":0.04543,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4896,-0.01416,0.05024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8404.0,"contact_point_centroid":[0.49526,-0.03289,0.10807],"force_p95":0.11146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34222,"mean_force":0.06786,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49214,-0.01431,0.10787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7298.0,"contact_point_centroid":[0.49462,0.00462,0.10416],"force_p95":0.13946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33027,"mean_force":0.07657,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49185,-0.01429,0.10432]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01559,-0.00213],"force_p95":0.15787,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2146,"mean_force":0.13184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49187,-0.01418,0.04947]},{"body_a":"world","body_b":"grasp_target","contact_count":2368.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49887,0.0173,0.2141]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4336.0,"contact_point_centroid":[0.49126,0.00503,0.04918],"force_p95":0.07534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1326,"mean_force":0.04954,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49073,-0.01416,0.04823]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4979,-0.01063,0.09474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4987.0,"contact_point_centroid":[0.49127,-0.03334,0.04923],"force_p95":0.07188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07484,"mean_force":0.04418,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49073,-0.01416,0.04824]}],"total_contact_groups":8},"final_pose_error":0.22823,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51414,-0.02146,0.15221],"final_tcp_position":[0.4991,-0.01457,0.19513],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.3891,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2368.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49962,-0.00718,0.13259],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.49866,-0.01423,0.05693],"tcp_start":[0.49962,-0.00718,0.13259],"tcp_to_object_dist_end":0.03137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50378,-0.01467,0.02555],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31193,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15486,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11123.0,"raw_peak_contact_force":0.2146,"tcp_end":[0.4907,-0.01416,0.0482],"tcp_start":[0.49866,-0.01423,0.05693],"tcp_to_object_dist_end":0.02616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":557.0,"n_steps_budget":630.0,"object_pos_end":[0.51301,-0.02,0.1565],"object_pos_start":[0.50378,-0.01467,0.02555],"object_to_goal_dist_end":0.23851,"object_to_goal_dist_start":0.31193,"object_z_max":0.15725,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15821.0,"raw_peak_contact_force":0.3891,"subtask_id":"lift_clear","tcp_end":[0.49926,-0.01457,0.19538],"tcp_start":[0.49922,-0.01457,0.1953],"tcp_to_object_dist_end":0.0416,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.51346,-0.02058,0.15526],"object_pos_start":[0.51335,-0.02044,0.15563],"object_to_goal_dist_end":0.23936,"object_to_goal_dist_start":0.23913,"object_z_max":0.15563,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"transport_goal","tcp_end":[0.49924,-0.01457,0.19535],"tcp_start":[0.49927,-0.01457,0.1954],"tcp_to_object_dist_end":0.04296,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51391,-0.02117,0.15338],"object_pos_start":[0.5138,-0.02102,0.15391],"object_to_goal_dist_end":0.24046,"object_to_goal_dist_start":0.24016,"object_z_max":0.15391,"peak_contact_force":0.0,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_goal","tcp_end":[0.4991,-0.01457,0.19513],"tcp_start":[0.49915,-0.01457,0.19521],"tcp_to_object_dist_end":0.04478,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39634,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.16624,"approach_1.speed":0.07714,"descend_1.depth":0.01111,"descend_1.speed":0.03324,"lift_1.lift_height":0.16528,"lift_1.speed":0.06663,"place_descend_1.place_z_offset":0.02773,"place_descend_1.speed":0.03596,"transport_1.arc_height":0.19858,"transport_1.speed":0.18445,"transport_1.transport_z":0.0972},"optimized_scores":{"best_composite_score":-0.01306,"best_fitness_score":0.65694,"best_task_score":0.36771},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.50992,0.03959,-0.00111],"force_p95":0.36441,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54757,"mean_force":0.12117,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49764,0.03947,0.03815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15980.0,"contact_point_centroid":[0.50174,0.05834,0.08849],"force_p95":0.10016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30614,"mean_force":0.06418,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49958,0.03934,0.08688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2132.0,"contact_point_centroid":[0.51258,0.02628,0.16611],"force_p95":0.17327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27407,"mean_force":0.09704,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50745,0.04477,0.16619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17030.0,"contact_point_centroid":[0.50175,0.0205,0.08867],"force_p95":0.09205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2726,"mean_force":0.06036,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49963,0.03935,0.08719]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2409.0,"contact_point_centroid":[0.51359,0.0639,0.16807],"force_p95":0.14542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25249,"mean_force":0.08852,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50806,0.04555,0.16861]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03978,-0.00202],"force_p95":0.21884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22398,"mean_force":0.1612,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50024,0.03971,0.03785]},{"body_a":"world","body_b":"grasp_target","contact_count":2624.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.12998,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50212,0.04677,0.22677]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4135.0,"contact_point_centroid":[0.49969,0.05883,0.03925],"force_p95":0.08619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12495,"mean_force":0.06203,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49907,0.03962,0.03658]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50611,0.04347,0.09012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4856.0,"contact_point_centroid":[0.49978,0.02056,0.03848],"force_p95":0.0768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11982,"mean_force":0.05218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49907,0.03962,0.03658]}],"total_contact_groups":10},"final_pose_error":0.16152,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.52903,0.06049,0.16109],"final_tcp_position":[0.51729,0.0571,0.19742],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.54757,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2624.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50774,0.04675,0.1349],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.50723,0.04033,0.04558],"tcp_start":[0.50774,0.04675,0.1349],"tcp_to_object_dist_end":0.02027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03983,0.0259],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21227,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.21793,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.22398,"tcp_end":[0.49904,0.03961,0.03654],"tcp_start":[0.50723,0.04033,0.04558],"tcp_to_object_dist_end":0.01709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51593,0.0396,0.12484],"object_pos_start":[0.51241,0.03983,0.0259],"object_to_goal_dist_end":0.17475,"object_to_goal_dist_start":0.21227,"object_z_max":0.12473,"peak_contact_force":0.10106,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33172.0,"raw_peak_contact_force":0.54757,"subtask_id":"lift_clear","tcp_end":[0.50484,0.03945,0.14517],"tcp_start":[0.49904,0.03961,0.03654],"tcp_to_object_dist_end":0.02316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.52707,0.05649,0.16848],"object_pos_start":[0.51593,0.0396,0.12484],"object_to_goal_dist_end":0.15529,"object_to_goal_dist_start":0.17475,"object_z_max":0.16874,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4541.0,"raw_peak_contact_force":0.27407,"subtask_id":"transport_goal","tcp_end":[0.51741,0.05699,0.19757],"tcp_start":[0.5175,0.05692,0.19757],"tcp_to_object_dist_end":0.03065,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52882,0.06011,0.16246],"object_pos_start":[0.52872,0.05992,0.16308],"object_to_goal_dist_end":0.15064,"object_to_goal_dist_start":0.15092,"object_z_max":0.16308,"peak_contact_force":0.0,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_goal","tcp_end":[0.51729,0.0571,0.19742],"tcp_start":[0.51734,0.05707,0.19748],"tcp_to_object_dist_end":0.03693,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```